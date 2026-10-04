import argparse
import os

from pathlib import Path
from time import perf_counter_ns

import pandas as pd

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000


def derive_hybrid_key(secret_a, secret_b):

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"pqc-benchmark-hybrid-x25519-mlkem768",
    )

    return hkdf.derive(
        secret_a + secret_b
    )


def summarize(samples_ns):

    samples_ms = (
        pd.Series(
            samples_ns,
            dtype="float64"
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
        required=True
    )

    args = parser.parse_args()

    run_dir = Path(
        f"results/raw/runs/run_{args.run_id:02d}"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    secret_a = os.urandom(32)
    secret_b = os.urandom(32)

    print("=" * 60)
    print(" HKDF-SHA256 BENCHMARK")
    print(f" Run ID: {args.run_id}")
    print("=" * 60)

    print(
        f"\nWarm-up: {WARMUP_ITERATIONS} iterations"
    )

    for _ in range(WARMUP_ITERATIONS):

        derive_hybrid_key(
            secret_a,
            secret_b
        )

    times = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        derive_hybrid_key(
            secret_a,
            secret_b
        )

        end = perf_counter_ns()

        times.append(
            end - start
        )

    row = {
        "algorithm": "HKDF-SHA256",
        "operation": "derive",
        "iterations": BENCHMARK_ITERATIONS,
        **summarize(times),
    }

    df = pd.DataFrame([row])

    output_path = (
        run_dir / "hkdf_benchmark.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print("\nRESULTS\n")

    print(
        df[
            [
                "algorithm",
                "mean_ms",
                "median_ms",
                "p95_ms",
                "ops_per_second",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}"
        )
    )


if __name__ == "__main__":
    main()