import argparse

from pathlib import Path
from time import perf_counter_ns

import oqs
import pandas as pd


ALGORITHMS = [
    "ML-DSA-44",
    "ML-DSA-65",
    "ML-DSA-87",
]

WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000

MESSAGE = b"Post-Quantum Cryptography Benchmark"


def summarize(samples_ns):

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

    print("\n" + "=" * 60)
    print(f"Benchmarking {algorithm}")
    print("=" * 60)

    rows = []

    with oqs.Signature(
        algorithm
    ) as signer:

        public_key = (
            signer.generate_keypair()
        )

        details = signer.details

        with oqs.Signature(
            algorithm
        ) as verifier:

            # =====================================================
            # WARM-UP
            # =====================================================

            for _ in range(WARMUP_ITERATIONS):

                public_key = (
                    signer.generate_keypair()
                )

                signature = signer.sign(
                    MESSAGE
                )

                assert verifier.verify(
                    MESSAGE,
                    signature,
                    public_key,
                )

            # =====================================================
            # KEYGEN
            # =====================================================

            keygen_times = []

            for _ in range(
                BENCHMARK_ITERATIONS
            ):

                start = perf_counter_ns()

                public_key = (
                    signer.generate_keypair()
                )

                end = perf_counter_ns()

                keygen_times.append(
                    end - start
                )

            public_key = (
                signer.generate_keypair()
            )

            # =====================================================
            # SIGN
            # =====================================================

            sign_times = []
            signature_sizes = []

            for _ in range(
                BENCHMARK_ITERATIONS
            ):

                start = perf_counter_ns()

                signature = signer.sign(
                    MESSAGE
                )

                end = perf_counter_ns()

                sign_times.append(
                    end - start
                )

                signature_sizes.append(
                    len(signature)
                )

            # =====================================================
            # VERIFY
            # =====================================================

            signature = signer.sign(
                MESSAGE
            )

            verify_times = []

            for _ in range(
                BENCHMARK_ITERATIONS
            ):

                start = perf_counter_ns()

                valid = verifier.verify(
                    MESSAGE,
                    signature,
                    public_key,
                )

                end = perf_counter_ns()

                assert valid

                verify_times.append(
                    end - start
                )

            metadata = {
                "public_key_bytes":
                    details["length_public_key"],

                "secret_key_bytes":
                    details["length_secret_key"],

                "signature_bytes":
                    details["length_signature"],
            }

            for operation, times in [
                ("keygen", keygen_times),
                ("sign", sign_times),
                ("verify", verify_times),
            ]:

                rows.append(
                    {
                        "algorithm":
                            algorithm,

                        "operation":
                            operation,

                        "iterations":
                            BENCHMARK_ITERATIONS,

                        **summarize(times),

                        **metadata,
                    }
                )

    return rows


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
    print(" ML-DSA BENCHMARK")
    print(f" Run ID: {args.run_id}")
    print("=" * 60)

    results = []

    for algorithm in ALGORITHMS:

        results.extend(
            benchmark_algorithm(
                algorithm
            )
        )

    df = pd.DataFrame(results)

    output_path = (
        run_dir
        / "ml_dsa_benchmark.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print("\n")
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(
        df[
            [
                "algorithm",
                "operation",
                "mean_ms",
                "median_ms",
                "p95_ms",
                "ops_per_second",
            ]
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.6f}",
        )
    )

    print(
        f"\nSaved to: {output_path}"
    )


if __name__ == "__main__":
    main()