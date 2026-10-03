from pathlib import Path
from time import perf_counter_ns

import pandas as pd

from algorithms.classical.x25519 import X25519


WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000


def summarize(samples_ns):
    samples_ms = pd.Series(
        samples_ns,
        dtype="float64"
    ) / 1_000_000

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

    print("=" * 60)
    print(" X25519 BENCHMARK")
    print("=" * 60)

    algorithm = X25519()

    # Warm-up
    print(f"\nWarm-up: {WARMUP_ITERATIONS} iterations")

    for _ in range(WARMUP_ITERATIONS):
        alice_private, alice_public = algorithm.keygen()
        bob_private, bob_public = algorithm.keygen()

        alice_secret = algorithm.exchange(
            alice_private,
            bob_public
        )

        bob_secret = algorithm.exchange(
            bob_private,
            alice_public
        )

        assert alice_secret == bob_secret

    # ------------------------------------------------
    # KEYGEN
    # ------------------------------------------------

    keygen_times = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        private_key, public_key = algorithm.keygen()

        end = perf_counter_ns()

        keygen_times.append(end - start)

    # ------------------------------------------------
    # EXCHANGE
    # ------------------------------------------------

    alice_private, alice_public = algorithm.keygen()
    bob_private, bob_public = algorithm.keygen()

    exchange_times = []

    for _ in range(BENCHMARK_ITERATIONS):

        start = perf_counter_ns()

        shared_secret = algorithm.exchange(
            alice_private,
            bob_public
        )

        end = perf_counter_ns()

        exchange_times.append(end - start)

    public_key_size = len(
        algorithm.public_key_bytes(alice_public)
    )

    private_key_size = len(
        algorithm.private_key_bytes(alice_private)
    )

    rows = [
        {
            "algorithm": "X25519",
            "operation": "keygen",
            "iterations": BENCHMARK_ITERATIONS,
            **summarize(keygen_times),
            "public_key_bytes": public_key_size,
            "secret_key_bytes": private_key_size,
            "shared_secret_bytes": 32,
        },
        {
            "algorithm": "X25519",
            "operation": "exchange",
            "iterations": BENCHMARK_ITERATIONS,
            **summarize(exchange_times),
            "public_key_bytes": public_key_size,
            "secret_key_bytes": private_key_size,
            "shared_secret_bytes": 32,
        }
    ]

    df = pd.DataFrame(rows)

    output_path = Path(
        "results/raw/x25519_benchmark.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print("\n")
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    columns = [
        "algorithm",
        "operation",
        "mean_ms",
        "median_ms",
        "p95_ms",
        "ops_per_second",
    ]

    print(
        df[columns].to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}"
        )
    )

    print(
        f"\nPublic key: {public_key_size} bytes"
    )

    print(
        f"Private key: {private_key_size} bytes"
    )

    print(
        f"\nBenchmark saved to: {output_path}"
    )


if __name__ == "__main__":
    main()