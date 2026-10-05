from pathlib import Path
import random

import pandas as pd


RUNS_DIR = Path(
    "results/raw/runs"
)

OUTPUT_DIR = Path(
    "results/raw/aggregated"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "bootstrap_confidence_intervals.csv"
)


BOOTSTRAP_SAMPLES = 10_000
RANDOM_SEED = 20261005


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
            f"No files found for "
            f"{filename}"
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


def percentile(
    values,
    probability,
):
    values = sorted(values)

    if not values:
        raise ValueError(
            "Cannot compute percentile "
            "of empty data."
        )

    position = (
        probability
        * (len(values) - 1)
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1,
    )

    fraction = (
        position - lower
    )

    return (
        values[lower]
        * (1 - fraction)
        + values[upper]
        * fraction
    )


def confidence_interval(
    bootstrap_values,
):
    return (
        percentile(
            bootstrap_values,
            0.025,
        ),
        percentile(
            bootstrap_values,
            0.975,
        ),
    )


def mean(values):
    return (
        sum(values)
        / len(values)
    )


def create_key_establishment_runs():

    mlkem = load_runs(
        "ml_kem_benchmark.csv"
    )

    x25519 = load_runs(
        "x25519_benchmark.csv"
    )

    rows = []

    run_ids = sorted(
        set(
            mlkem["run_id"]
        )
        &
        set(
            x25519["run_id"]
        )
    )

    for run_id in run_ids:

        x_run = x25519[
            x25519["run_id"]
            == run_id
        ]

        m_run = mlkem[
            (
                mlkem["run_id"]
                == run_id
            )
            &
            (
                mlkem["algorithm"]
                == "ML-KEM-768"
            )
        ]

        def x_value(operation):
            values = x_run[
                x_run["operation"]
                == operation
            ]["mean_ms"]

            if len(values) != 1:
                raise RuntimeError(
                    "Expected one X25519 "
                    f"{operation} result "
                    f"for run {run_id}."
                )

            return float(
                values.iloc[0]
            )

        def m_value(operation):
            values = m_run[
                m_run["operation"]
                == operation
            ]["mean_ms"]

            if len(values) != 1:
                raise RuntimeError(
                    "Expected one ML-KEM-768 "
                    f"{operation} result "
                    f"for run {run_id}."
                )

            return float(
                values.iloc[0]
            )

        x_keygen = x_value(
            "keygen"
        )

        x_exchange = x_value(
            "exchange"
        )

        m_keygen = m_value(
            "keygen"
        )

        m_encaps = m_value(
            "encaps"
        )

        m_decaps = m_value(
            "decaps"
        )

        classical_total = (
            2 * x_keygen
            + 2 * x_exchange
        )

        pq_total = (
            m_keygen
            + m_encaps
            + m_decaps
        )

        hybrid_total = (
            classical_total
            + pq_total
        )

        classical_server = (
            x_keygen
            + x_exchange
        )

        pq_server = (
            m_encaps
        )

        hybrid_server = (
            classical_server
            + m_encaps
        )

        rows.append(
            {
                "run_id":
                    run_id,

                "x25519_total_ms":
                    classical_total,

                "mlkem768_total_ms":
                    pq_total,

                "hybrid_total_ms":
                    hybrid_total,

                "x25519_server_ms":
                    classical_server,

                "mlkem768_server_ms":
                    pq_server,

                "hybrid_server_ms":
                    hybrid_server,
            }
        )

    return pd.DataFrame(
        rows
    )


def create_signature_runs():

    ecdsa = load_runs(
        "ecdsa_benchmark.csv"
    )

    mldsa = load_runs(
        "ml_dsa_benchmark.csv"
    )

    run_ids = sorted(
        set(
            ecdsa["run_id"]
        )
        &
        set(
            mldsa["run_id"]
        )
    )

    rows = []

    for run_id in run_ids:

        e_run = ecdsa[
            ecdsa["run_id"]
            == run_id
        ]

        m_run = mldsa[
            (
                mldsa["run_id"]
                == run_id
            )
            &
            (
                mldsa["algorithm"]
                == "ML-DSA-44"
            )
        ]

        def value(
            dataframe,
            operation,
        ):
            values = dataframe[
                dataframe["operation"]
                == operation
            ]["mean_ms"]

            if len(values) != 1:
                raise RuntimeError(
                    "Expected one "
                    f"{operation} result "
                    f"for run {run_id}."
                )

            return float(
                values.iloc[0]
            )

        rows.append(
            {
                "run_id":
                    run_id,

                "ecdsa_sign_ms":
                    value(
                        e_run,
                        "sign",
                    ),

                "ecdsa_verify_ms":
                    value(
                        e_run,
                        "verify",
                    ),

                "mldsa44_sign_ms":
                    value(
                        m_run,
                        "sign",
                    ),

                "mldsa44_verify_ms":
                    value(
                        m_run,
                        "verify",
                    ),
            }
        )

    return pd.DataFrame(
        rows
    )


def bootstrap_metric(
    dataframe,
    metric_function,
):

    rng = random.Random(
        RANDOM_SEED
    )

    records = (
        dataframe.to_dict(
            orient="records"
        )
    )

    n = len(records)

    bootstrap_values = []

    for _ in range(
        BOOTSTRAP_SAMPLES
    ):

        sample = [
            records[
                rng.randrange(n)
            ]
            for _ in range(n)
        ]

        bootstrap_values.append(
            metric_function(
                sample
            )
        )

    point_estimate = (
        metric_function(
            records
        )
    )

    ci_low, ci_high = (
        confidence_interval(
            bootstrap_values
        )
    )

    return (
        point_estimate,
        ci_low,
        ci_high,
    )


def average_column(
    sample,
    column,
):
    return mean(
        [
            row[column]
            for row in sample
        ]
    )


def ratio_of_means(
    sample,
    numerator,
    denominator,
):

    numerator_mean = (
        average_column(
            sample,
            numerator,
        )
    )

    denominator_mean = (
        average_column(
            sample,
            denominator,
        )
    )

    return (
        numerator_mean
        / denominator_mean
    )


def main():

    key_runs = (
        create_key_establishment_runs()
    )

    signature_runs = (
        create_signature_runs()
    )

    print("=" * 100)
    print(
        " BOOTSTRAP 95% CONFIDENCE INTERVALS"
    )
    print("=" * 100)

    print(
        f"Independent runs: "
        f"{len(key_runs)}"
    )

    print(
        f"Bootstrap samples: "
        f"{BOOTSTRAP_SAMPLES:,}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )

    print()
    print(
        "Bootstrap unit: independent run "
        "(not individual timing iteration)"
    )

    results = []

    metrics = [
        (
            "ML-KEM-768 / X25519",
            "total_compute_ratio",
            key_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "mlkem768_total_ms",
                    "x25519_total_ms",
                ),
        ),

        (
            "X25519MLKEM768 / X25519",
            "total_compute_ratio",
            key_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "hybrid_total_ms",
                    "x25519_total_ms",
                ),
        ),

        (
            "ML-KEM-768 / X25519",
            "server_compute_ratio",
            key_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "mlkem768_server_ms",
                    "x25519_server_ms",
                ),
        ),

        (
            "X25519MLKEM768 / X25519",
            "server_compute_ratio",
            key_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "hybrid_server_ms",
                    "x25519_server_ms",
                ),
        ),

        (
            "ML-DSA-44 / ECDSA-P256",
            "sign_ratio",
            signature_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "mldsa44_sign_ms",
                    "ecdsa_sign_ms",
                ),
        ),

        (
            "ML-DSA-44 / ECDSA-P256",
            "verify_ratio",
            signature_runs,
            lambda sample:
                ratio_of_means(
                    sample,
                    "mldsa44_verify_ms",
                    "ecdsa_verify_ms",
                ),
        ),
    ]

    for (
        comparison,
        metric,
        dataframe,
        function,
    ) in metrics:

        (
            estimate,
            ci_low,
            ci_high,
        ) = bootstrap_metric(
            dataframe,
            function,
        )

        results.append(
            {
                "comparison":
                    comparison,

                "metric":
                    metric,

                "point_estimate":
                    estimate,

                "ci_95_low":
                    ci_low,

                "ci_95_high":
                    ci_high,

                "independent_runs":
                    len(dataframe),

                "bootstrap_samples":
                    BOOTSTRAP_SAMPLES,

                "random_seed":
                    RANDOM_SEED,

                "bootstrap_unit":
                    "independent_run",
            }
        )

    result = pd.DataFrame(
        results
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
    OUTPUT_FILE,
    index=False,
    float_format="%.6f",
)

    print()
    print(
        result[
            [
                "comparison",
                "metric",
                "point_estimate",
                "ci_95_low",
                "ci_95_high",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print()
    print(
        f"Saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()