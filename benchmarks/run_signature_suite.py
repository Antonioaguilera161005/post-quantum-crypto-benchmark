import subprocess
import sys
import time


RUNS = 10

BENCHMARKS = [
    "benchmarks.benchmark_ecdsa",
    "benchmarks.benchmark_ml_dsa",
]


def main():

    print("=" * 70)
    print(" DIGITAL SIGNATURE BENCHMARK SUITE")
    print(f" {RUNS} independent runs")
    print("=" * 70)

    for run_id in range(1, RUNS + 1):

        print("\n" + "#" * 70)
        print(f" RUN {run_id}/{RUNS}")
        print("#" * 70)

        for module in BENCHMARKS:

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
            time.sleep(3)

    print("\n" + "=" * 70)
    print(" SIGNATURE BENCHMARKS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()