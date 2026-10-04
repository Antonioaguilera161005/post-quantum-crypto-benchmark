from pathlib import Path

import pandas as pd


RUNS_DIR = Path("results/raw/runs")

OUTPUT_DIR = Path(
    "results/raw/aggregated"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def load_runs(filename):

    frames = []

    for run_dir in sorted(
        RUNS_DIR.glob("run_*")
    ):

        file_path = (
            run_dir / filename
        )

        if not file_path.exists():
            continue

        df = pd.read_csv(
            file_path
        )

        run_id = int(
            run_dir.name.split("_")[1]
        )

        df["run_id"] = run_id

        frames.append(df)

    if not frames:
        raise RuntimeError(
            f"No files found for {filename}"
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


def aggregate_operations(
    df,
    group_columns,
):

    result = (
        df.groupby(
            group_columns
        )
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
        result[
            "run_mean_std_ms"
        ]
        / result["mean_ms"]
        * 100
    )

    return result


def aggregate_ecdsa():

    raw = load_runs(
        "ecdsa_benchmark.csv"
    )

    aggregated = (
        aggregate_operations(
            raw,
            [
                "algorithm",
                "operation",
            ],
        )
    )

    metadata = (
        raw.groupby(
            [
                "algorithm",
                "operation",
            ]
        )
        .agg(
            public_key_bytes=(
                "public_key_bytes",
                "first",
            ),

            signature_mean_bytes=(
                "signature_mean_bytes",
                "mean",
            ),

            signature_min_bytes=(
                "signature_min_bytes",
                "min",
            ),

            signature_max_bytes=(
                "signature_max_bytes",
                "max",
            ),
        )
        .reset_index()
    )

    aggregated = (
        aggregated.merge(
            metadata,
            on=[
                "algorithm",
                "operation",
            ],
        )
    )

    aggregated.to_csv(
        OUTPUT_DIR / "ecdsa.csv",
        index=False,
    )

    return aggregated


def aggregate_mldsa():

    raw = load_runs(
        "ml_dsa_benchmark.csv"
    )

    aggregated = (
        aggregate_operations(
            raw,
            [
                "algorithm",
                "operation",
            ],
        )
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
                "signature_bytes",
            ]
        ]
        .first()
        .reset_index()
    )

    aggregated = (
        aggregated.merge(
            metadata,
            on=[
                "algorithm",
                "operation",
            ],
        )
    )

    aggregated.to_csv(
        OUTPUT_DIR / "ml_dsa.csv",
        index=False,
    )

    return aggregated


def get_operation(
    df,
    algorithm,
    operation,
):

    return df[
        (df["algorithm"] == algorithm)
        & (df["operation"] == operation)
    ].iloc[0]


def build_comparison(
    ecdsa,
    mldsa,
):

    rows = []

    # ============================================================
    # ECDSA
    # ============================================================

    ecdsa_keygen = get_operation(
        ecdsa,
        "ECDSA-P256",
        "keygen",
    )

    ecdsa_sign = get_operation(
        ecdsa,
        "ECDSA-P256",
        "sign",
    )

    ecdsa_verify = get_operation(
        ecdsa,
        "ECDSA-P256",
        "verify",
    )

    rows.append(
        {
            "algorithm":
                "ECDSA-P256",

            "type":
                "Classical",

            "keygen_ms":
                ecdsa_keygen[
                    "mean_ms"
                ],

            "sign_ms":
                ecdsa_sign[
                    "mean_ms"
                ],

            "verify_ms":
                ecdsa_verify[
                    "mean_ms"
                ],

            "public_key_bytes":
                ecdsa_keygen[
                    "public_key_bytes"
                ],

            "signature_bytes":
                ecdsa_sign[
                    "signature_mean_bytes"
                ],

            "signature_min_bytes":
                ecdsa_sign[
                    "signature_min_bytes"
                ],

            "signature_max_bytes":
                ecdsa_sign[
                    "signature_max_bytes"
                ],

            "keygen_cv_pct":
                ecdsa_keygen[
                    "coefficient_of_variation_pct"
                ],

            "sign_cv_pct":
                ecdsa_sign[
                    "coefficient_of_variation_pct"
                ],

            "verify_cv_pct":
                ecdsa_verify[
                    "coefficient_of_variation_pct"
                ],
        }
    )

    # ============================================================
    # ML-DSA
    # ============================================================

    algorithms = [
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]

    for algorithm in algorithms:

        keygen = get_operation(
            mldsa,
            algorithm,
            "keygen",
        )

        sign = get_operation(
            mldsa,
            algorithm,
            "sign",
        )

        verify = get_operation(
            mldsa,
            algorithm,
            "verify",
        )

        rows.append(
            {
                "algorithm":
                    algorithm,

                "type":
                    "Post-Quantum",

                "keygen_ms":
                    keygen["mean_ms"],

                "sign_ms":
                    sign["mean_ms"],

                "verify_ms":
                    verify["mean_ms"],

                "public_key_bytes":
                    keygen[
                        "public_key_bytes"
                    ],

                "signature_bytes":
                    sign[
                        "signature_bytes"
                    ],

                "signature_min_bytes":
                    sign[
                        "signature_bytes"
                    ],

                "signature_max_bytes":
                    sign[
                        "signature_bytes"
                    ],

                "keygen_cv_pct":
                    keygen[
                        "coefficient_of_variation_pct"
                    ],

                "sign_cv_pct":
                    sign[
                        "coefficient_of_variation_pct"
                    ],

                "verify_cv_pct":
                    verify[
                        "coefficient_of_variation_pct"
                    ],
            }
        )

    comparison = pd.DataFrame(
        rows
    )

    # ============================================================
    # RATIOS VS ECDSA
    # ============================================================

    baseline = comparison[
        comparison["algorithm"]
        == "ECDSA-P256"
    ].iloc[0]

    comparison[
        "keygen_ratio_vs_ecdsa"
    ] = (
        comparison["keygen_ms"]
        / baseline["keygen_ms"]
    )

    comparison[
        "sign_ratio_vs_ecdsa"
    ] = (
        comparison["sign_ms"]
        / baseline["sign_ms"]
    )

    comparison[
        "verify_ratio_vs_ecdsa"
    ] = (
        comparison["verify_ms"]
        / baseline["verify_ms"]
    )

    comparison[
        "public_key_ratio_vs_ecdsa"
    ] = (
        comparison[
            "public_key_bytes"
        ]
        / baseline[
            "public_key_bytes"
        ]
    )

    comparison[
        "signature_ratio_vs_ecdsa"
    ] = (
        comparison[
            "signature_bytes"
        ]
        / baseline[
            "signature_bytes"
        ]
    )

    comparison.to_csv(
        OUTPUT_DIR
        / "signature_comparison.csv",
        index=False,
    )

    return comparison


def main():

    ecdsa = aggregate_ecdsa()
    mldsa = aggregate_mldsa()

    comparison = build_comparison(
        ecdsa,
        mldsa,
    )

    print("=" * 100)
    print(
        " DIGITAL SIGNATURE BENCHMARK "
        "— AGGREGATED RESULTS"
    )
    print("=" * 100)

    print("\nECDSA\n")

    print(
        ecdsa[
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

    print("\nML-DSA\n")

    print(
        mldsa[
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

    print("\n")
    print("=" * 100)
    print(
        " CLASSICAL VS POST-QUANTUM "
        "SIGNATURE COMPARISON"
    )
    print("=" * 100)

    columns = [
        "algorithm",
        "keygen_ms",
        "sign_ms",
        "verify_ms",
        "public_key_bytes",
        "signature_bytes",
        "sign_ratio_vs_ecdsa",
        "verify_ratio_vs_ecdsa",
        "public_key_ratio_vs_ecdsa",
        "signature_ratio_vs_ecdsa",
    ]

    print(
        comparison[
            columns
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.3f}",
        )
    )

    print(
        "\nResults saved to:"
        "\nresults/raw/aggregated/"
    )


if __name__ == "__main__":
    main()