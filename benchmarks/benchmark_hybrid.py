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
        "median_ms": samples_ms.median(),
        "p95_ms": samples_ms.quantile(0.95),
        "p99_ms": samples_ms.quantile(0.99),
        "std_ms": samples_ms.std(ddof=0),
        "min_ms": samples_ms.min(),
        "max_ms": samples_ms.max(),
        "ops_per_second": 1000 / mean_ms,
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

    print("=" * 70)
    print(
        " X25519MLKEM768 FULL-ESTABLISHMENT "
        "DIAGNOSTIC BENCHMARK"
    )
    print(f" Run ID: {args.run_id}")
    print("=" * 70)

    hybrid = X25519MLKEM768()

    # ========================================================
    # WARM-UP
    # ========================================================

    print(
        f"\nWarm-up: "
        f"{WARMUP_ITERATIONS} iterations"
    )

    for _ in range(
        WARMUP_ITERATIONS
    ):
        result = hybrid.establish()

        assert (
            result["client_secret"]
            == result["server_secret"]
        )

        assert (
            result["hybrid_secret_bytes"]
            == 64
        )

    # ========================================================
    # FULL ESTABLISHMENT DIAGNOSTIC
    # ========================================================
    #
    # This deliberately measures the complete Python
    # implementation:
    #
    # - object creation,
    # - both X25519 key generations,
    # - both X25519 exchanges,
    # - ML-KEM key generation,
    # - ML-KEM encapsulation,
    # - ML-KEM decapsulation,
    # - Python wrapper overhead.
    #
    # Therefore it is NOT used as the canonical TLS
    # performance figure.
    #
    # The component-based RFC 10024 model built from primitive
    # benchmarks is the canonical comparison.
    # ========================================================

    times = []

    for _ in range(
        BENCHMARK_ITERATIONS
    ):
        start = perf_counter_ns()

        result = hybrid.establish()

        end = perf_counter_ns()

        assert (
            result["client_secret"]
            == result["server_secret"]
        )

        times.append(
            end - start
        )

    stats = summarize(times)

    # ========================================================
    # RFC 10024 CRYPTOGRAPHIC MATERIAL
    # ========================================================

    client_share_bytes = (
        result["client_share_bytes"]
    )

    server_share_bytes = (
        result["server_share_bytes"]
    )

    transmitted_bytes = (
        client_share_bytes
        + server_share_bytes
    )

    row = {
        "algorithm":
            "X25519MLKEM768",

        "operation":
            "full_establishment_diagnostic",

        "benchmark_scope":
            "diagnostic_only",

        "iterations":
            BENCHMARK_ITERATIONS,

        **stats,

        "client_share_bytes":
            client_share_bytes,

        "server_share_bytes":
            server_share_bytes,

        "transmitted_bytes":
            transmitted_bytes,

        "shared_secret_bytes":
            result["hybrid_secret_bytes"],
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

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RESULTS — DIAGNOSTIC ONLY")
    print("=" * 70)

    print(
        df[
            [
                "algorithm",
                "mean_ms",
                "median_ms",
                "p95_ms",
                "p99_ms",
                "ops_per_second",
                "client_share_bytes",
                "server_share_bytes",
                "transmitted_bytes",
                "shared_secret_bytes",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print()
    print(
        "NOTE:"
    )
    print(
        "- This is an end-to-end Python diagnostic benchmark."
    )
    print(
        "- It is NOT the canonical performance comparison."
    )
    print(
        "- The canonical model is derived from primitive "
        "benchmarks using RFC 10024 client/server roles."
    )

    print(
        f"\nBenchmark saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()