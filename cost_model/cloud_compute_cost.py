import argparse
from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_PATH = Path(
    "results/economic/cloud_compute_cost.csv"
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Estimate compute cost of cryptographic "
            "key establishment from measured server CPU-hours."
        )
    )

    parser.add_argument(
        "--price-per-vcpu-hour",
        type=float,
        required=True,
        help=(
            "Marginal compute price in USD/EUR "
            "per vCPU-hour."
        ),
    )

    parser.add_argument(
        "--currency",
        type=str,
        default="USD",
    )

    args = parser.parse_args()

    df = pd.read_csv(
        INPUT_PATH
    )

    # ------------------------------------------------------------
    # Compute cost
    # ------------------------------------------------------------

    df["compute_cost_month"] = (
        df["server_cpu_hours_month"]
        * args.price_per_vcpu_hour
    )

    df["extra_compute_cost_vs_classical"] = (
        df["extra_server_cpu_hours_vs_classical"]
        * args.price_per_vcpu_hour
    )

    df["price_per_vcpu_hour"] = (
        args.price_per_vcpu_hour
    )

    df["currency"] = args.currency

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ------------------------------------------------------------
    # Display 100M scenario
    # ------------------------------------------------------------

    display = df[
        df["handshakes_per_month"]
        == 100_000_000
    ]

    print("=" * 105)

    print(
        " COMPUTE COST — "
        "100 MILLION HANDSHAKES / MONTH"
    )

    print("=" * 105)

    print(
        f"\nPrice per vCPU-hour: "
        f"{args.price_per_vcpu_hour:.4f} "
        f"{args.currency}\n"
    )

    columns = [
        "scenario",
        "algorithm",
        "server_cpu_hours_month",
        "compute_cost_month",
        "extra_compute_cost_vs_classical",
    ]

    print(
        display[
            columns
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.4f}",
        )
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nIMPORTANT:"
        "\nThis is a marginal CPU-equivalent cost model."
        "\nIt is NOT the full price of a cloud VM."
        "\nReal VM billing also depends on memory, instance size,"
        " utilization, reserved capacity, discounts and other factors."
    )


if __name__ == "__main__":
    main()