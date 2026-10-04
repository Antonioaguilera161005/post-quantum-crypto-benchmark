import subprocess
import sys
import time


RUNS = 10

BENCHMARKS = [
    "benchmarks.benchmark_ml_kem",
    "benchmarks.benchmark_x25519",
    "benchmarks.benchmark_hybrid",
]


def main():

    print("=" * 80)
    print(" PQC BENCHMARK SUITE")
    print(f" {RUNS} independent runs")
    print("=" * 80)

    for run_id in range(1, RUNS + 1):

        print("\n")
        print("#" * 80)
        print(f" RUN {run_id}/{RUNS}")
        print("#" * 80)

        for module in BENCHMARKS:

            print(f"\nRunning {module}...")

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    module,
                    "--run-id",
                    str(run_id),
                ],
                check=True,
            )

        if run_id < RUNS:
            print("\nCooling down for 3 seconds...")
            time.sleep(3)

    print("\n" + "=" * 80)
    print(" ALL BENCHMARK RUNS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()