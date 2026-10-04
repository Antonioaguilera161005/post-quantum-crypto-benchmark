import argparse
import json
import platform
import sys

from pathlib import Path
from time import perf_counter_ns

import oqs
import pandas as pd


ALGORITHMS = [
    "ML-KEM-512",
    "ML-KEM-768",
    "ML-KEM-1024",
]

WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000


def summarize(samples_ns):
    """
    Convert nanosecond measurements into useful benchmark statistics.
    """

    samples_ms = (
        pd.Series(samples_ns, dtype="float64")
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


def benchmark_algorithm(algorithm):

    print(f"\n{'=' * 60}")
    print(f"Benchmarking {algorithm}")
    print("=" * 60)

    rows = []

    # Keep liboqs objects alive while measuring operations.
    with oqs.KeyEncapsulation(algorithm) as receiver:

        with oqs.KeyEncapsulation(algorithm) as sender:

            details = receiver.details

            # ========================================================
            # WARM-UP
            # ========================================================

            print(
                f"Warm-up: {WARMUP_ITERATIONS} iterations"
            )

            for _ in range(WARMUP_ITERATIONS):

                public_key = receiver.generate_keypair()

                ciphertext, secret_a = (
                    sender.encap_secret(public_key)
                )

                secret_b = receiver.decap_secret(
                    ciphertext
                )

                assert secret_a == secret_b

            # ========================================================
            # KEY GENERATION
            # ========================================================

            keygen_times = []

            for _ in range(BENCHMARK_ITERATIONS):

                start = perf_counter_ns()

                public_key = receiver.generate_keypair()

                end = perf_counter_ns()

                keygen_times.append(
                    end - start
                )

            rows.append(
                {
                    "algorithm": algorithm,
                    "operation": "keygen",
                    "iterations":
                        BENCHMARK_ITERATIONS,
                    **summarize(keygen_times),
                }
            )

            # Generate one fixed public key for encapsulation tests.
            public_key = receiver.generate_keypair()

            # ========================================================
            # ENCAPSULATION
            # ========================================================

            encaps_times = []

            for _ in range(BENCHMARK_ITERATIONS):

                start = perf_counter_ns()

                ciphertext, shared_secret = (
                    sender.encap_secret(
                        public_key
                    )
                )

                end = perf_counter_ns()

                encaps_times.append(
                    end - start
                )

            rows.append(
                {
                    "algorithm": algorithm,
                    "operation": "encaps",
                    "iterations":
                        BENCHMARK_ITERATIONS,
                    **summarize(encaps_times),
                }
            )

            # ========================================================
            # DECAPSULATION
            # ========================================================

            decaps_times = []

            for _ in range(BENCHMARK_ITERATIONS):

                # Generate ciphertext outside measured section.
                ciphertext, sender_secret = (
                    sender.encap_secret(
                        public_key
                    )
                )

                start = perf_counter_ns()

                receiver_secret = (
                    receiver.decap_secret(
                        ciphertext
                    )
                )

                end = perf_counter_ns()

                assert (
                    sender_secret
                    == receiver_secret
                )

                decaps_times.append(
                    end - start
                )

            rows.append(
                {
                    "algorithm": algorithm,
                    "operation": "decaps",
                    "iterations":
                        BENCHMARK_ITERATIONS,
                    **summarize(decaps_times),
                }
            )

            # ========================================================
            # METADATA
            # ========================================================

            metadata = {
                "public_key_bytes":
                    details["length_public_key"],

                "secret_key_bytes":
                    details["length_secret_key"],

                "ciphertext_bytes":
                    details["length_ciphertext"],

                "shared_secret_bytes":
                    details["length_shared_secret"],

                "nist_level":
                    details["claimed_nist_level"],
            }

            for row in rows:
                row.update(metadata)

    return rows


def save_environment(run_dir, run_id):

    environment = {
        "run_id": run_id,
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "liboqs_version": oqs.oqs_version(),
        "liboqs_python_version":
            oqs.oqs_python_version(),
        "warmup_iterations":
            WARMUP_ITERATIONS,
        "benchmark_iterations":
            BENCHMARK_ITERATIONS,
    }

    output_path = (
        run_dir / "environment.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            environment,
            file,
            indent=4,
        )

    print(
        f"\nEnvironment saved to: "
        f"{output_path}"
    )


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
    print(" ML-KEM BENCHMARK")
    print(f" Run ID: {args.run_id}")
    print("=" * 60)

    all_results = []

    for algorithm in ALGORITHMS:

        results = benchmark_algorithm(
            algorithm
        )

        all_results.extend(
            results
        )

    df = pd.DataFrame(
        all_results
    )

    output_path = (
        run_dir / "ml_kem_benchmark.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    save_environment(
        run_dir,
        args.run_id,
    )

    print("\n")
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    display_columns = [
        "algorithm",
        "operation",
        "mean_ms",
        "median_ms",
        "p95_ms",
        "ops_per_second",
    ]

    print(
        df[
            display_columns
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