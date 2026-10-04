from pathlib import Path

import pandas as pd


RUNS_DIR = Path("results/raw/runs")
OUTPUT_DIR = Path("results/raw/aggregated")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_runs(filename):

    frames = []

    run_dirs = sorted(
        RUNS_DIR.glob("run_*")
    )

    for run_dir in run_dirs:

        file_path = run_dir / filename

        if not file_path.exists():
            continue

        df = pd.read_csv(file_path)

        run_id = int(
            run_dir.name.split("_")[1]
        )

        df["run_id"] = run_id

        frames.append(df)

    if not frames:
        raise RuntimeError(
            f"No benchmark files found for {filename}"
        )

    return pd.concat(
        frames,
        ignore_index=True
    )


def aggregate(df, group_columns):

    result = (
        df.groupby(group_columns)
        .agg(
            runs=("run_id", "count"),

            mean_ms=(
                "mean_ms",
                "mean"
            ),

            run_mean_std_ms=(
                "mean_ms",
                "std"
            ),

            median_ms=(
                "median_ms",
                "mean"
            ),

            p95_ms=(
                "p95_ms",
                "mean"
            ),

            p99_ms=(
                "p99_ms",
                "mean"
            ),

            ops_per_second=(
                "ops_per_second",
                "mean"
            ),

            min_run_mean_ms=(
                "mean_ms",
                "min"
            ),

            max_run_mean_ms=(
                "mean_ms",
                "max"
            ),
        )
        .reset_index()
    )

    result[
        "coefficient_of_variation_pct"
    ] = (
        result["run_mean_std_ms"]
        / result["mean_ms"]
        * 100
    )

    return result


def aggregate_mlkem():

    raw = load_runs(
        "ml_kem_benchmark.csv"
    )

    aggregated = aggregate(
        raw,
        [
            "algorithm",
            "operation",
        ],
    )

    metadata = (
        raw.groupby(
            [
                "algorithm",
                "operation",
            ]
        )
        [
            [
                "public_key_bytes",
                "secret_key_bytes",
                "ciphertext_bytes",
                "shared_secret_bytes",
                "nist_level",
            ]
        ]
        .first()
        .reset_index()
    )

    aggregated = aggregated.merge(
        metadata,
        on=[
            "algorithm",
            "operation",
        ],
    )

    aggregated.to_csv(
        OUTPUT_DIR / "ml_kem.csv",
        index=False,
    )

    return aggregated


def aggregate_x25519():

    raw = load_runs(
        "x25519_benchmark.csv"
    )

    aggregated = aggregate(
        raw,
        [
            "algorithm",
            "operation",
        ],
    )

    metadata = (
        raw.groupby(
            [
                "algorithm",
                "operation",
            ]
        )
        [
            [
                "public_key_bytes",
                "secret_key_bytes",
                "shared_secret_bytes",
            ]
        ]
        .first()
        .reset_index()
    )

    aggregated = aggregated.merge(
        metadata,
        on=[
            "algorithm",
            "operation",
        ],
    )

    aggregated.to_csv(
        OUTPUT_DIR / "x25519.csv",
        index=False,
    )

    return aggregated


def aggregate_hybrid():

    raw = load_runs(
        "hybrid_benchmark.csv"
    )

    aggregated = aggregate(
        raw,
        [
            "algorithm",
            "operation",
        ],
    )

    metadata = (
        raw.groupby(
            [
                "algorithm",
                "operation",
            ]
        )
        [
            [
                "transmitted_bytes",
                "shared_secret_bytes",
            ]
        ]
        .first()
        .reset_index()
    )

    aggregated = aggregated.merge(
        metadata,
        on=[
            "algorithm",
            "operation",
        ],
    )

    aggregated.to_csv(
        OUTPUT_DIR / "hybrid_end_to_end.csv",
        index=False,
    )

    return aggregated


def aggregate_hkdf():

    raw = load_runs(
        "hkdf_benchmark.csv"
    )

    aggregated = aggregate(
        raw,
        [
            "algorithm",
            "operation",
        ],
    )

    aggregated.to_csv(
        OUTPUT_DIR / "hkdf.csv",
        index=False,
    )

    return aggregated


def build_component_model(
    mlkem,
    x25519,
    hkdf,
):

    x_keygen = x25519[
        x25519["operation"] == "keygen"
    ].iloc[0]["mean_ms"]

    x_exchange = x25519[
        x25519["operation"] == "exchange"
    ].iloc[0]["mean_ms"]

    x25519_total = (
        2 * x_keygen
        + 2 * x_exchange
    )

    mlkem_768 = mlkem[
        mlkem["algorithm"] == "ML-KEM-768"
    ]

    mlkem_keygen = mlkem_768[
        mlkem_768["operation"] == "keygen"
    ].iloc[0]["mean_ms"]

    mlkem_encaps = mlkem_768[
        mlkem_768["operation"] == "encaps"
    ].iloc[0]["mean_ms"]

    mlkem_decaps = mlkem_768[
        mlkem_768["operation"] == "decaps"
    ].iloc[0]["mean_ms"]

    mlkem_total = (
        mlkem_keygen
        + mlkem_encaps
        + mlkem_decaps
    )

    hkdf_mean = hkdf.iloc[0]["mean_ms"]

    hybrid_component_model = (
        x25519_total
        + mlkem_total
        + 2 * hkdf_mean
    )

    rows = [
        {
            "scenario": "Classical",
            "algorithm": "X25519",
            "crypto_work_ms":
                x25519_total,
            "transmitted_bytes":
                64,
        },

        {
            "scenario": "Post-Quantum",
            "algorithm": "ML-KEM-768",
            "crypto_work_ms":
                mlkem_total,
            "transmitted_bytes":
                2272,
        },

        {
            "scenario": "Hybrid",
            "algorithm":
                "X25519+ML-KEM-768",
            "crypto_work_ms":
                hybrid_component_model,
            "transmitted_bytes":
                2336,
        },
    ]

    model = pd.DataFrame(rows)

    baseline_ms = model.iloc[0][
        "crypto_work_ms"
    ]

    baseline_bytes = model.iloc[0][
        "transmitted_bytes"
    ]

    model[
        "compute_ratio_vs_x25519"
    ] = (
        model["crypto_work_ms"]
        / baseline_ms
    )

    model[
        "traffic_ratio_vs_x25519"
    ] = (
        model["transmitted_bytes"]
        / baseline_bytes
    )

    model.to_csv(
        OUTPUT_DIR
        / "key_establishment_component_model.csv",
        index=False,
    )

    return model


def main():

    mlkem = aggregate_mlkem()
    x25519 = aggregate_x25519()
    hybrid_end_to_end = (
        aggregate_hybrid()
    )
    hkdf = aggregate_hkdf()

    component_model = (
        build_component_model(
            mlkem,
            x25519,
            hkdf,
        )
    )

    print("=" * 90)
    print(
        " AGGREGATED BENCHMARK RESULTS"
    )
    print("=" * 90)

    print("\nML-KEM\n")

    print(
        mlkem[
            [
                "algorithm",
                "operation",
                "runs",
                "mean_ms",
                "run_mean_std_ms",
                "coefficient_of_variation_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print("\nX25519\n")

    print(
        x25519[
            [
                "algorithm",
                "operation",
                "runs",
                "mean_ms",
                "run_mean_std_ms",
                "coefficient_of_variation_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print("\nHKDF\n")

    print(
        hkdf[
            [
                "algorithm",
                "operation",
                "runs",
                "mean_ms",
                "run_mean_std_ms",
                "coefficient_of_variation_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print(
        "\nHybrid end-to-end diagnostic\n"
    )

    print(
        hybrid_end_to_end[
            [
                "algorithm",
                "runs",
                "mean_ms",
                "run_mean_std_ms",
                "coefficient_of_variation_pct",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print(
        "\nComponent-based comparison\n"
    )

    print(
        component_model.to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print(
        "\nAggregated results saved to:"
        "\nresults/raw/aggregated/"
    )


if __name__ == "__main__":
    main()