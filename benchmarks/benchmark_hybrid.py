import argparse

from pathlib import Path
from time import perf_counter_ns

import pandas as pd

from algorithms.hybrid.x25519_mlkem768 import (
    X25519MLKEM768,
)


WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000


def summarize(samples_ns):

    samples_ms = (
        pd.Series(
            samples_ns,
            dtype="float64",
        )
        / 1_000_000
    )

    mean_ms = samples_ms.mean()

    return {
        "mean_ms": mean_ms,
        "median_ms":
            samples_ms.median(),
        "p95_ms":
            samples_ms.quantile(0.95),
        "p99_ms":
            samples_ms.quantile(0.99),
        "std_ms":
            samples_ms.std(ddof=0),
        "min_ms":
            samples_ms.min(),
        "max_ms":
            samples_ms.max(),
        "ops_per_second":
            1000 / mean_ms,
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run-id",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    run_dir = Path(
        f"results/raw/runs/"
        f"run_{args.run_id:02d}"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print(
        " HYBRID X25519 + "
        "ML-KEM-768 BENCHMARK"
    )
    print(
        f" Run ID: {args.run_id}"
    )
    print("=" * 60)

    hybrid = X25519MLKEM768()

    # ============================================================
    # WARM-UP
    # ============================================================

    print(
        f"\nWarm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for _ in range(
        WARMUP_ITERATIONS
    ):

        result = (
            hybrid.establish()
        )

        assert (
            result["alice_secret"]
            == result["bob_secret"]
        )

    # ============================================================
    # FULL HYBRID ESTABLISHMENT
    # ============================================================

    times = []

    for _ in range(
        BENCHMARK_ITERATIONS
    ):

        start = perf_counter_ns()

        result = (
            hybrid.establish()
        )

        end = perf_counter_ns()

        assert (
            result["alice_secret"]
            == result["bob_secret"]
        )

        times.append(
            end - start
        )

    stats = summarize(
        times
    )

    # ============================================================
    # TRANSMITTED MATERIAL
    # ============================================================

    transmitted_bytes = (
        2
        * result[
            "x25519_public_key_bytes"
        ]
        + result[
            "mlkem_public_key_bytes"
        ]
        + result[
            "mlkem_ciphertext_bytes"
        ]
    )

    row = {
        "algorithm":
            "X25519+ML-KEM-768",

        "operation":
            "full_hybrid_establishment",

        "iterations":
            BENCHMARK_ITERATIONS,

        **stats,

        "transmitted_bytes":
            transmitted_bytes,

        "shared_secret_bytes":
            len(
                result["alice_secret"]
            ),
    }

    df = pd.DataFrame(
        [row]
    )

    output_path = (
        run_dir
        / "hybrid_benchmark.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    # ============================================================
    # DISPLAY
    # ============================================================

    print("\n")
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(
        df[
            [
                "algorithm",
                "mean_ms",
                "median_ms",
                "p95_ms",
                "p99_ms",
                "ops_per_second",
                "transmitted_bytes",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print(
        f"\nBenchmark saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()