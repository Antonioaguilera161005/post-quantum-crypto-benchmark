from pathlib import Path

import pandas as pd

from analysis.tls_key_establishment_model import (
    main as build_tls_key_establishment_model,
)


RUNS_DIR = Path("results/raw/runs")
OUTPUT_DIR = Path("results/raw/aggregated")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
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
        ignore_index=True,
    )


def aggregate(df, group_columns):
    result = (
        df.groupby(group_columns)
        .agg(
            runs=(
                "run_id",
                "count",
            ),

            mean_ms=(
                "mean_ms",
                "mean",
            ),

            run_mean_std_ms=(
                "mean_ms",
                "std",
            ),

            median_ms=(
                "median_ms",
                "mean",
            ),

            p95_ms=(
                "p95_ms",
                "mean",
            ),

            p99_ms=(
                "p99_ms",
                "mean",
            ),

            ops_per_second=(
                "ops_per_second",
                "mean",
            ),

            min_run_mean_ms=(
                "mean_ms",
                "min",
            ),

            max_run_mean_ms=(
                "mean_ms",
                "max",
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
        )[
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
        )[
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
    """
    Aggregate the full Python X25519MLKEM768 benchmark.

    This result is diagnostic only.

    The canonical key-establishment comparison is generated
    separately by tls_key_establishment_model.py from the
    primitive X25519 and ML-KEM measurements.
    """

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

    metadata_columns = [
        "client_share_bytes",
        "server_share_bytes",
        "transmitted_bytes",
        "shared_secret_bytes",
        "benchmark_scope",
    ]

    # Be tolerant of older raw files while the user is
    # regenerating the benchmark suite.
    available_metadata = [
        column
        for column in metadata_columns
        if column in raw.columns
    ]

    if available_metadata:
        metadata = (
            raw.groupby(
                [
                    "algorithm",
                    "operation",
                ]
            )[
                available_metadata
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
        OUTPUT_DIR
        / "hybrid_end_to_end.csv",
        index=False,
    )

    return aggregated


def aggregate_hkdf():
    """
    HKDF remains independently benchmarked because it is
    relevant to TLS and other cryptographic protocols.

    It is NOT added as a hybrid-specific cost in the
    X25519MLKEM768 comparison.
    """

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


def remove_legacy_component_model():
    """
    Remove the obsolete pre-RFC component model if it exists.

    That model incorrectly added two HKDF operations as a
    hybrid-specific cost.
    """

    legacy_file = (
        OUTPUT_DIR
        / "key_establishment_component_model.csv"
    )

    if legacy_file.exists():
        legacy_file.unlink()

        print(
            f"Removed obsolete result: "
            f"{legacy_file}"
        )


def main():
    mlkem = aggregate_mlkem()
    x25519 = aggregate_x25519()
    hybrid_end_to_end = (
        aggregate_hybrid()
    )
    hkdf = aggregate_hkdf()

    remove_legacy_component_model()

    print("=" * 100)
    print(
        " AGGREGATED PRIMITIVE BENCHMARK RESULTS"
    )
    print("=" * 100)

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

    print("\nHKDF-SHA256 — independent benchmark\n")

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
        "\nX25519MLKEM768 full-establishment "
        "diagnostic\n"
    )

    print(
        hybrid_end_to_end[
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

    print()
    print(
        "NOTE: The end-to-end hybrid measurement above is "
        "diagnostic only."
    )
    print(
        "It includes Python wrapper/object-creation overhead "
        "and is not used as the canonical TLS performance "
        "comparison."
    )

    print()
    print("=" * 100)
    print(
        " BUILDING CANONICAL TLS KEY-ESTABLISHMENT MODEL"
    )
    print("=" * 100)
    print()

    # The canonical model is generated by the dedicated
    # RFC 10024 analysis module.
    build_tls_key_establishment_model()

    print()
    print("=" * 100)
    print(" AGGREGATION COMPLETE")
    print("=" * 100)

    print(
        "\nCanonical key-establishment result:"
        "\nresults/raw/aggregated/"
        "tls_key_establishment_model.csv"
    )

    print(
        "\nDiagnostic hybrid result:"
        "\nresults/raw/aggregated/"
        "hybrid_end_to_end.csv"
    )

    print(
        "\nPrimitive results:"
        "\nresults/raw/aggregated/"
    )


if __name__ == "__main__":
    main()