from pathlib import Path

import pandas as pd

from cost_model.pricing import (
    convert_network_units,
    get_service_pricing,
)


INPUT_FILE = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_FILE = Path(
    "results/economic/cloud_network_cost.csv"
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
        "server_egress_gb_month",
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
            "network"
        )
    )

    rows = []

    for _, pricing in (
        pricing_table.iterrows()
    ):

        provider = (
            pricing["provider"]
        )

        billing_unit = (
            pricing["billing_unit"]
        )

        price_per_unit = float(
            pricing["price"]
        )

        free_units = float(
            pricing["free_units_month"]
        )

        for _, row in (
            impact.iterrows()
        ):

            network_units = (
                convert_network_units(
                    row[
                        "server_egress_gb_month"
                    ],
                    billing_unit,
                )
            )

            # ================================================
            # STANDALONE
            # ================================================

            standalone_billable = max(
                0.0,
                network_units
                - free_units,
            )

            standalone_cost = (
                standalone_billable
                * price_per_unit
            )

            # ================================================
            # MARGINAL
            #
            # Existing business traffic is assumed to have
            # consumed the free allowance already.
            # ================================================

            marginal_billable = (
                network_units
            )

            marginal_cost = (
                marginal_billable
                * price_per_unit
            )

            rows.append(
                {
                    "handshakes_per_month":
                        row[
                            "handshakes_per_month"
                        ],

                    "provider":
                        provider,

                    "scenario":
                        row["scenario"],

                    "algorithm":
                        row["algorithm"],

                    "server_egress_gb_month":
                        row[
                            "server_egress_gb_month"
                        ],

                    "region":
                        pricing["region"],

                    "pricing_product":
                        pricing["product"],

                    "network_unit":
                        billing_unit,

                    "network_units_month":
                        network_units,

                    "free_units_month":
                        free_units,

                    "price_per_unit":
                        price_per_unit,

                    "standalone_billable_units":
                        standalone_billable,

                    "standalone_network_cost_month":
                        standalone_cost,

                    "marginal_billable_units":
                        marginal_billable,

                    "marginal_network_cost_month":
                        marginal_cost,

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
            "extra_standalone_network_cost_vs_classical"
        ] = (
            group[
                "standalone_network_cost_month"
            ]
            - baseline[
                "standalone_network_cost_month"
            ]
        )

        group[
            "extra_marginal_network_cost_vs_classical"
        ] = (
            group[
                "marginal_network_cost_month"
            ]
            - baseline[
                "marginal_network_cost_month"
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
        "server_egress_gb_month",
        "network_units_month",
        "standalone_network_cost_month",
        "marginal_network_cost_month",
        "extra_marginal_network_cost_vs_classical",
        "pricing_checked_date",
    ]

    print("=" * 145)
    print(
        " CLOUD NETWORK COST - "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 145)

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
        "- Only server egress is charged."
    )
    print(
        "- Standalone applies configured "
        "provider free allowances."
    )
    print(
        "- Marginal assumes free allowances "
        "are already consumed."
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