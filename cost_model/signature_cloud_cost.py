from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "results/economic/signature_operational_impact.csv"
)

OUTPUT_PATH = Path(
    "results/economic/signature_cloud_cost.csv"
)


# Same pricing assumptions already used elsewhere
# in the project.

PROVIDERS = {
    "Azure": {
        "compute_price_per_vcpu_hour": 0.0535,
        "network_price_per_unit": 0.087,
        "network_unit": "GB",
        "currency": "USD",
    },

    "GCP": {
        "compute_price_per_vcpu_hour": 0.03954,
        "network_price_per_unit": 0.085,
        "network_unit": "GiB",
        "currency": "USD",
    },
}


BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024 ** 3


def gb_to_network_units(gb, unit):

    if unit == "GB":
        return gb

    if unit == "GiB":
        total_bytes = gb * BYTES_PER_GB
        return total_bytes / BYTES_PER_GIB

    raise ValueError(
        f"Unsupported network unit: {unit}"
    )


def main():

    impact = pd.read_csv(
        INPUT_PATH
    )

    rows = []

    for provider, pricing in PROVIDERS.items():

        for _, row in impact.iterrows():

            # ====================================================
            # COMPUTE
            #
            # Company signs on its own infrastructure.
            # Client verification is excluded from the main
            # company-cost scenario.
            # ====================================================

            signer_compute_cost = (
                row["signer_cpu_hours_month"]
                * pricing[
                    "compute_price_per_vcpu_hour"
                ]
            )

            # ====================================================
            # NETWORK
            # ====================================================

            network_units = gb_to_network_units(
                row["signature_traffic_gb_month"],
                pricing["network_unit"],
            )

            network_cost = (
                network_units
                * pricing[
                    "network_price_per_unit"
                ]
            )

            # ====================================================
            # TOTAL
            # ====================================================

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
                        pricing["currency"],
                }
            )

    result = pd.DataFrame(rows)

    # ============================================================
    # EXTRA COST VS ECDSA
    # ============================================================

    result[
        "extra_cost_vs_ecdsa_month"
    ] = 0.0

    for (
        provider,
        operations
    ), group in result.groupby(
        [
            "provider",
            "signed_operations_per_month",
        ]
    ):

        baseline = group[
            group["algorithm"]
            == "ECDSA-P256"
        ].iloc[0][
            "total_signature_cost_month"
        ]

        result.loc[
            group.index,
            "extra_cost_vs_ecdsa_month"
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

    # ============================================================
    # SAVE
    # ============================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ============================================================
    # DISPLAY
    # ============================================================

    display = result[
        result["signed_operations_per_month"]
        == 100_000_000
    ]

    print("=" * 125)

    print(
        " DIGITAL SIGNATURE CLOUD COST — "
        "100 MILLION SIGNED OPERATIONS / MONTH"
    )

    print("=" * 125)

    columns = [
        "provider",
        "algorithm",
        "compute_cost_month",
        "network_cost_month",
        "total_signature_cost_month",
        "extra_cost_vs_ecdsa_month",
        "extra_cost_vs_ecdsa_year",
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
        "\nMODEL:"
        "\n- Company performs the signing."
        "\n- Signature is sent over the network."
        "\n- Client-side verification CPU is not charged "
        "to the company."
        "\n- Network free tiers are assumed already consumed."
    )


if __name__ == "__main__":
    main()