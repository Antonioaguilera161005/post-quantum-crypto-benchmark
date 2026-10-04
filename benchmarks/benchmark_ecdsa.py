import argparse

from pathlib import Path
from time import perf_counter_ns

import pandas as pd

from algorithms.classical.ecdsa_p256 import ECDSAP256


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


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run-id",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    run_dir = Path(
        f"results/raw/runs/run_{args.run_id:02d}"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print(" ECDSA P-256 BENCHMARK")
    print(f" Run ID: {args.run_id}")
    print("=" * 60)

    algorithm = ECDSAP256()

    # ============================================================
    # WARM-UP
    # ============================================================

    print(
        f"\nWarm-up: {WARMUP_ITERATIONS} iterations"
    )

    for _ in range(WARMUP_ITERATIONS):

        private_key, public_key = algorithm.keygen()

        signature = algorithm.sign(
            private_key,
            MESSAGE,
        )

        assert algorithm.verify(
            public_key,
            signature,
            MESSAGE,
        )

    # ============================================================
    # KEYGEN
    # ============================================================

    keygen_times = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        private_key, public_key = algorithm.keygen()

        end = perf_counter_ns()

        keygen_times.append(
            end - start
        )

    # Fixed pair for sign / verify
    private_key, public_key = algorithm.keygen()

    # ============================================================
    # SIGN
    # ============================================================

    sign_times = []
    signature_sizes = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        signature = algorithm.sign(
            private_key,
            MESSAGE,
        )

        end = perf_counter_ns()

        sign_times.append(
            end - start
        )

        signature_sizes.append(
            len(signature)
        )

    # ============================================================
    # VERIFY
    # ============================================================

    signature = algorithm.sign(
        private_key,
        MESSAGE,
    )

    verify_times = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        valid = algorithm.verify(
            public_key,
            signature,
            MESSAGE,
        )

        end = perf_counter_ns()

        assert valid

        verify_times.append(
            end - start
        )

    public_key_size = len(
        algorithm.public_key_bytes(
            public_key
        )
    )

    rows = []

    for operation, times in [
        ("keygen", keygen_times),
        ("sign", sign_times),
        ("verify", verify_times),
    ]:

        row = {
            "algorithm": "ECDSA-P256",
            "operation": operation,
            "iterations":
                BENCHMARK_ITERATIONS,
            **summarize(times),
            "public_key_bytes":
                public_key_size,

            "signature_mean_bytes":
                sum(signature_sizes)
                / len(signature_sizes),

            "signature_min_bytes":
                min(signature_sizes),

            "signature_max_bytes":
                max(signature_sizes),
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    output_path = (
        run_dir
        / "ecdsa_benchmark.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print("\nRESULTS\n")

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
        f"\nPublic key: "
        f"{public_key_size} bytes"
    )

    print(
        "Signature size: "
        f"{min(signature_sizes)}-"
        f"{max(signature_sizes)} bytes"
    )

    print(
        f"\nSaved to: {output_path}"
    )


if __name__ == "__main__":
    main()