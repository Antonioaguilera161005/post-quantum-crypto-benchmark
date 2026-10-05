import os
import subprocess
import sys

from benchmarks.environment import (
    get_campaign_metadata,
)


SUITES = [
    "benchmarks.run_benchmark_suite",
    "benchmarks.run_signature_suite",
]


def main():

    campaign = (
        get_campaign_metadata()
    )

    print("=" * 80)
    print(
        " FULL PQC BENCHMARK CAMPAIGN"
    )
    print("=" * 80)

    print(
        f"Git commit: "
        f"{campaign['commit']}"
    )

    print(
        "Repository dirty at start: "
        f"{campaign['dirty']}"
    )

    print(
        "Campaign started at: "
        f"{campaign['started_at_utc']}"
    )

    environment = os.environ.copy()

    environment[
        "PQC_CAMPAIGN_STARTED_AT_UTC"
    ] = campaign[
        "started_at_utc"
    ]

    environment[
        "PQC_CAMPAIGN_GIT_COMMIT"
    ] = (
        campaign["commit"]
        or ""
    )

    environment[
        "PQC_CAMPAIGN_GIT_DIRTY"
    ] = str(
        campaign["dirty"]
    ).lower()

    for suite in SUITES:

        print()
        print("=" * 80)
        print(
            f" RUNNING {suite}"
        )
        print("=" * 80)

        subprocess.run(
            [
                sys.executable,
                "-m",
                suite,
            ],
            check=True,
            env=environment,
        )

    print()
    print("=" * 80)
    print(
        " FULL BENCHMARK CAMPAIGN COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()