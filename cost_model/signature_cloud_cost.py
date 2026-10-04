from pathlib import Path

import pandas as pd

from cost_model.pricing import (
    convert_network_units,
    get_provider_pricing,
    get_service_pricing,
)


INPUT_FILE = Path(
    "results/economic/"
    "signature_operational_impact.csv"
)

OUTPUT_FILE = Path(
    "results/economic/"
    "signature_cloud_cost.csv"
)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing signature impact file: "
            f"{INPUT_FILE}"
        )

    impact = pd.read_csv(
        INPUT_FILE
    )

    # Only providers for which both network and compute
    # assumptions exist are eligible for this combined model.

    network_pricing = (
        get_service_pricing(
            "network"
        )
    )

    providers = list(
        network_pricing[
            "provider"
        ].unique()
    )

    rows = []

    for provider in providers:

        compute = (
            get_provider_pricing(
                provider,
                "compute",
            )
        )

        network = (
            get_provider_pricing(
                provider,
                "network",
            )
        )

        price_per_vcpu_hour = (
            float(compute["price"])
            / int(compute["vcpus"])
        )

        network_price = float(
            network["price"]
        )

        network_unit = (
            network["billing_unit"]
        )

        for _, row in (
            impact.iterrows()
        ):

            # ================================================
            # COMPUTE
            # ================================================

            signer_compute_cost = (
                row[
                    "signer_cpu_hours_month"
                ]
                * price_per_vcpu_hour
            )

            # ================================================
            # NETWORK
            #
            # Signature model uses a marginal interpretation:
            # existing traffic is assumed to have already
            # consumed any free provider allowance.
            # ================================================

            network_units = (
                convert_network_units(
                    row[
                        "signature_traffic_gb_month"
                    ],
                    network_unit,
                )
            )

            network_cost = (
                network_units
                * network_price
            )

            total_cost = (
                signer_compute_cost
                + network_cost
            )

            rows.append(
                {
                    "provider":
                        provider,

                    "algorithm":
                        row["algorithm"],

                    "signed_operations_per_month":
                        row[
                            "signed_operations_per_month"
                        ],

                    "signer_cpu_hours_month":
                        row[
                            "signer_cpu_hours_month"
                        ],

                    "signature_traffic_gb_month":
                        row[
                            "signature_traffic_gb_month"
                        ],

                    "compute_cost_month":
                        signer_compute_cost,

                    "network_cost_month":
                        network_cost,

                    "total_signature_cost_month":
                        total_cost,

                    "currency":
                        compute["currency"],

                    "compute_region":
                        compute["region"],

                    "compute_product":
                        compute["product"],

                    "compute_pricing_source":
                        compute["source_name"],

                    "network_region":
                        network["region"],

                    "network_product":
                        network["product"],

                    "network_unit":
                        network_unit,

                    "network_pricing_source":
                        network["source_name"],

                    "pricing_checked_date":
                        network["checked_date"],
                }
            )

    result = pd.DataFrame(
        rows
    )

    # ========================================================
    # EXTRA COST VS ECDSA
    # ========================================================

    result[
        "extra_cost_vs_ecdsa_month"
    ] = 0.0

    for (
        provider,
        operations,
    ), group in result.groupby(
        [
            "provider",
            "signed_operations_per_month",
        ]
    ):

        baseline_rows = group[
            group["algorithm"]
            == "ECDSA-P256"
        ]

        if len(baseline_rows) != 1:
            raise RuntimeError(
                "Expected exactly one ECDSA "
                f"baseline for {provider}, "
                f"{operations:,} operations."
            )

        baseline = (
            baseline_rows.iloc[0][
                "total_signature_cost_month"
            ]
        )

        result.loc[
            group.index,
            "extra_cost_vs_ecdsa_month",
        ] = (
            group[
                "total_signature_cost_month"
            ]
            - baseline
        )

    result[
        "extra_cost_vs_ecdsa_year"
    ] = (
        result[
            "extra_cost_vs_ecdsa_month"
        ]
        * 12
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    display = result[
        result[
            "signed_operations_per_month"
        ]
        == 100_000_000
    ]

    print("=" * 135)
    print(
        " DIGITAL SIGNATURE CLOUD COST - "
        "100 MILLION SIGNED OPERATIONS / MONTH"
    )
    print("=" * 135)

    columns = [
        "provider",
        "algorithm",
        "compute_cost_month",
        "network_cost_month",
        "total_signature_cost_month",
        "extra_cost_vs_ecdsa_month",
        "extra_cost_vs_ecdsa_year",
        "pricing_checked_date",
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

    print()
    print("MODEL:")
    print(
        "- Company performs the signing."
    )
    print(
        "- Signature bytes are charged as "
        "outbound network traffic."
    )
    print(
        "- Client verification CPU is excluded "
        "from company cost."
    )
    print(
        "- Network free allowances are assumed "
        "already consumed."
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