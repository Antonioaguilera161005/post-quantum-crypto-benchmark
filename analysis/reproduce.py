import argparse
import subprocess
import sys

from pathlib import Path


PIPELINE = [
    "analysis.aggregate_benchmarks",
    "analysis.aggregate_signatures",
    "analysis.bootstrap_confidence_intervals",

    "cost_model.operational_impact",
    "cost_model.cloud_network_cost",
    "cost_model.provider_compute_cost",
    "cost_model.total_operational_cost",

    "cost_model.signature_operational_impact",
    "cost_model.signature_cloud_cost",

    "cost_model.migration_cost",
    "cost_model.migration_sensitivity",
]


EXPECTED_OUTPUTS = [
    Path(
        "results/raw/aggregated/"
        "ml_kem.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "x25519.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "hybrid_end_to_end.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "tls_key_establishment_model.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "ecdsa.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "ml_dsa.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "signature_comparison.csv"
    ),

    Path(
        "results/raw/aggregated/"
        "bootstrap_confidence_intervals.csv"
    ),

    Path(
        "results/economic/"
        "operational_impact.csv"
    ),

    Path(
        "results/economic/"
        "cloud_network_cost.csv"
    ),

    Path(
        "results/economic/"
        "provider_compute_cost.csv"
    ),

    Path(
        "results/economic/"
        "total_operational_cost.csv"
    ),

    Path(
        "results/economic/"
        "signature_operational_impact.csv"
    ),

    Path(
        "results/economic/"
        "signature_cloud_cost.csv"
    ),

    Path(
        "results/economic/"
        "migration_cost.csv"
    ),

    Path(
        "results/economic/"
        "migration_sensitivity.csv"
    ),
]


def run_module(module):

    print()
    print("=" * 80)
    print(
        f" RUNNING: {module}"
    )
    print("=" * 80)
    print()

    subprocess.run(
        [
            sys.executable,
            "-m",
            module,
        ],
        check=True,
    )


def verify_outputs():

    missing = [
        path
        for path in EXPECTED_OUTPUTS
        if not path.exists()
    ]

    if missing:

        print()
        print(
            "ERROR: expected outputs "
            "were not generated:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

        raise RuntimeError(
            "Reproduction pipeline "
            "did not generate all "
            "expected outputs."
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Regenerate deterministic "
            "derived results from committed "
            "raw benchmark data."
        )
    )

    parser.add_argument(
        "--figures",
        action="store_true",
        help=(
            "Also regenerate figures "
            "after CSV outputs."
        ),
    )

    args = parser.parse_args()

    print("=" * 80)
    print(
        " PQC BENCHMARK REPRODUCTION PIPELINE"
    )
    print("=" * 80)

    print()
    print(
        "Raw benchmark measurements "
        "are treated as experimental inputs."
    )

    print(
        "This command regenerates "
        "deterministic derived outputs."
    )

    for module in PIPELINE:
        run_module(
            module
        )

    verify_outputs()

    if args.figures:

        run_module(
            "analysis.generate_figures"
        )

    print()
    print("=" * 80)
    print(
        " REPRODUCTION COMPLETE"
    )
    print("=" * 80)

    print()
    print(
        "All expected derived "
        "CSV outputs exist."
    )

    if args.figures:
        print(
            "Figures were also regenerated."
        )


if __name__ == "__main__":
    main()