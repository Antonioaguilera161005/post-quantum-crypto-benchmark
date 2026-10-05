import subprocess
import sys
import time

from pathlib import Path

from benchmarks.environment import (
    get_campaign_metadata,
    run_native_crosscheck,
    save_run_environment,
)


RUNS = 10

WARMUP_ITERATIONS = 100
BENCHMARK_ITERATIONS = 2000


BENCHMARKS = [
    "benchmarks.benchmark_ml_kem",
    "benchmarks.benchmark_x25519",
    "benchmarks.benchmark_hybrid",
    "benchmarks.benchmark_hkdf",
]


def main():

    campaign_metadata = (
        get_campaign_metadata()
    )

    print("=" * 80)
    print(
        " PQC KEY-ESTABLISHMENT BENCHMARK SUITE"
    )
    print(
        f" {RUNS} independent runs"
    )
    print("=" * 80)

    native_crosscheck = (
        run_native_crosscheck(
            "kem"
        )
    )

    for run_id in range(
        1,
        RUNS + 1,
    ):

        print("\n")
        print("#" * 80)
        print(
            f" RUN {run_id}/{RUNS}"
        )
        print("#" * 80)

        for module in BENCHMARKS:

            print(
                f"\nRunning "
                f"{module}..."
            )

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

        run_dir = (
            Path(
                "results/raw/runs"
            )
            / f"run_{run_id:02d}"
        )

        save_run_environment(
            run_dir=run_dir,
            run_id=run_id,
            suite_name=(
                "key_establishment"
            ),
            native_crosscheck=(
                native_crosscheck
            ),
            campaign_metadata=(
                campaign_metadata
            ),
            warmup_iterations=(
                WARMUP_ITERATIONS
            ),
            benchmark_iterations=(
                BENCHMARK_ITERATIONS
            ),
        )

        if run_id < RUNS:

            print(
                "\nCooling down for "
                "3 seconds..."
            )

            time.sleep(3)

    print(
        "\n"
        + "=" * 80
    )

    print(
        " ALL KEY-ESTABLISHMENT "
        "BENCHMARK RUNS COMPLETED"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()