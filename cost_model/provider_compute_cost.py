from pathlib import Path

import pandas as pd

from cost_model.pricing import (
    get_service_pricing,
)


INPUT_FILE = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_FILE = Path(
    "results/economic/provider_compute_cost.csv"
)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing operational impact file: "
            f"{INPUT_FILE}"
        )

    impact = pd.read_csv(
        INPUT_FILE
    )

    required_columns = {
        "handshakes_per_month",
        "scenario",
        "algorithm",
        "server_cpu_hours_month",
    }

    missing = (
        required_columns
        - set(impact.columns)
    )

    if missing:
        raise RuntimeError(
            f"Missing required columns: "
            f"{sorted(missing)}"
        )

    pricing_table = (
        get_service_pricing(
            "compute"
        )
    )

    rows = []

    for _, pricing in (
        pricing_table.iterrows()
    ):

        provider = (
            pricing["provider"]
        )

        vm_price_per_hour = float(
            pricing["price"]
        )

        vcpus = int(
            pricing["vcpus"]
        )

        price_per_vcpu_hour = (
            vm_price_per_hour
            / vcpus
        )

        for _, row in (
            impact.iterrows()
        ):

            cpu_hours = (
                row[
                    "server_cpu_hours_month"
                ]
            )

            compute_cost = (
                cpu_hours
                * price_per_vcpu_hour
            )

            rows.append(
                {
                    "handshakes_per_month":
                        row[
                            "handshakes_per_month"
                        ],

                    "provider":
                        provider,

                    "region":
                        pricing["region"],

                    "instance":
                        pricing["product"],

                    "scenario":
                        row["scenario"],

                    "algorithm":
                        row["algorithm"],

                    "server_cpu_hours_month":
                        cpu_hours,

                    "vm_price_per_hour":
                        vm_price_per_hour,

                    "vcpus":
                        vcpus,

                    "price_per_vcpu_hour":
                        price_per_vcpu_hour,

                    "compute_cost_month":
                        compute_cost,

                    "currency":
                        pricing["currency"],

                    "pricing_source":
                        pricing["source_name"],

                    "pricing_source_type":
                        pricing["source_type"],

                    "pricing_checked_date":
                        pricing["checked_date"],
                }
            )

    result = pd.DataFrame(
        rows
    )

    # ========================================================
    # DIFFERENCE VS CLASSICAL
    # ========================================================

    frames = []

    for (
        handshakes,
        provider,
    ), group in result.groupby(
        [
            "handshakes_per_month",
            "provider",
        ]
    ):

        group = group.copy()

        classical = group[
            group["scenario"]
            == "Classical"
        ]

        if len(classical) != 1:
            raise RuntimeError(
                "Expected exactly one "
                "Classical baseline for "
                f"{provider}, "
                f"{handshakes:,} handshakes."
            )

        baseline = (
            classical.iloc[0]
        )

        group[
            "extra_compute_cost_vs_classical"
        ] = (
            group[
                "compute_cost_month"
            ]
            - baseline[
                "compute_cost_month"
            ]
        )

        frames.append(
            group
        )

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    focus = result[
        result[
            "handshakes_per_month"
        ]
        == 100_000_000
    ].copy()

    display_columns = [
        "provider",
        "scenario",
        "algorithm",
        "server_cpu_hours_month",
        "price_per_vcpu_hour",
        "compute_cost_month",
        "extra_compute_cost_vs_classical",
        "pricing_checked_date",
    ]

    print("=" * 135)
    print(
        " PROVIDER COMPUTE COST - "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 135)

    print(
        focus[
            display_columns
        ]
        .round(4)
        .to_string(
            index=False
        )
    )

    print()
    print("MODEL:")
    print(
        "- Only server-side cryptographic "
        "CPU is charged."
    )
    print(
        "- CPU-hours are converted using "
        "reference USD/vCPU-hour rates."
    )
    print(
        "- This is a simplified resource "
        "cost model, not complete VM billing."
    )
    print(
        "- Pricing assumptions are loaded "
        "from cloud_pricing.csv."
    )

    print()
    print(
        f"Results saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()