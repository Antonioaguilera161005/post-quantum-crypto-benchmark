from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_PATH = Path(
    "results/economic/cloud_network_cost.csv"
)


# Simplified current public pricing scenarios.
#
# IMPORTANT:
# These values are assumptions derived from provider public pricing
# and should be periodically reviewed.

PROVIDERS = {
    "Azure-Europe-Premium": {
        "unit": "GB",
        "free_monthly": 100.0,
        "price_per_unit": 0.087,
        "currency": "USD",
    },

    "GCP-Madrid-Standard": {
        "unit": "GiB",
        "free_monthly": 200.0,
        "price_per_unit": 0.085,
        "currency": "USD",
    },
}


BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024 ** 3


def gb_to_provider_units(gb, unit):

    total_bytes = gb * BYTES_PER_GB

    if unit == "GB":
        return gb

    if unit == "GiB":
        return total_bytes / BYTES_PER_GIB

    raise ValueError(
        f"Unsupported unit: {unit}"
    )


def standalone_cost(
    traffic_units,
    free_monthly,
    price_per_unit,
):
    """
    Cost when the measured cryptographic traffic is treated
    as the account's only outbound traffic.
    """

    billable = max(
        traffic_units - free_monthly,
        0
    )

    return billable * price_per_unit


def marginal_cost(
    extra_units,
    price_per_unit,
):
    """
    Incremental cost assuming the provider free allowance
    has already been consumed by normal company traffic.
    """

    return (
        max(extra_units, 0)
        * price_per_unit
    )


def main():

    operational = pd.read_csv(
        INPUT_PATH
    )

    rows = []

    for provider, pricing in PROVIDERS.items():

        for _, row in operational.iterrows():

            traffic_units = gb_to_provider_units(
                row["server_egress_gb_month"],
                pricing["unit"],
            )

            extra_units = gb_to_provider_units(
                row[
                    "extra_server_egress_gb_vs_classical"
                ],
                pricing["unit"],
            )

            isolated_cost = standalone_cost(
                traffic_units,
                pricing["free_monthly"],
                pricing["price_per_unit"],
            )

            incremental_cost = marginal_cost(
                extra_units,
                pricing["price_per_unit"],
            )

            rows.append(
                {
                    "provider": provider,
                    "scenario": row["scenario"],
                    "algorithm": row["algorithm"],
                    "handshakes_per_month":
                        row["handshakes_per_month"],

                    "server_egress_gb_month":
                        row["server_egress_gb_month"],

                    "provider_traffic_units":
                        traffic_units,

                    "provider_unit":
                        pricing["unit"],

                    "free_monthly_units":
                        pricing["free_monthly"],

                    "price_per_unit":
                        pricing["price_per_unit"],

                    "standalone_network_cost":
                        isolated_cost,

                    "marginal_extra_network_cost_vs_classical":
                        incremental_cost,

                    "currency":
                        pricing["currency"],
                }
            )

    result = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    display = result[
        result["handshakes_per_month"]
        == 100_000_000
    ]

    print("=" * 110)
    print(
        " CLOUD NETWORK COST — "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 110)

    columns = [
        "provider",
        "scenario",
        "algorithm",
        "server_egress_gb_month",
        "standalone_network_cost",
        "marginal_extra_network_cost_vs_classical",
        "currency",
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
        "\nInterpretation:"
        "\nstandalone_network_cost = "
        "crypto traffic treated in isolation."
        "\nmarginal_extra_network_cost_vs_classical = "
        "incremental PQC cost assuming free allowance "
        "is already consumed."
    )


if __name__ == "__main__":
    main()