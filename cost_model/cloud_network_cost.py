from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_DIR = Path("results/economic")
OUTPUT_FILE = OUTPUT_DIR / "cloud_network_cost.csv"


# ============================================================
# PROVIDER ASSUMPTIONS
# ============================================================
#
# These values are modelling inputs.
# We will later move them to a dedicated config file with
# source URL and checked date.
#
# Azure:
#   - Decimal GB
#
# GCP:
#   - Billing model expressed here in GiB
#
# "Standalone":
#   Free allowance is available to the crypto workload.
#
# "Marginal":
#   Existing business traffic has already consumed the
#   provider's free allowance, so every additional unit
#   caused by the cryptographic workload is billed.
# ============================================================

PROVIDERS = {
    "Azure": {
        "price_per_unit": 0.087,
        "free_units_month": 100.0,
        "network_unit": "GB",
        "currency": "USD",
    },
    "GCP": {
        "price_per_unit": 0.085,
        "free_units_month": 200.0,
        "network_unit": "GiB",
        "currency": "USD",
    },
}


BYTES_PER_GIB = 1024 ** 3
BYTES_PER_GB = 1_000_000_000


def decimal_gb_to_gib(decimal_gb):
    """
    Convert decimal GB to binary GiB.
    """
    total_bytes = decimal_gb * BYTES_PER_GB
    return total_bytes / BYTES_PER_GIB


def convert_network_units(decimal_gb, unit):
    if unit == "GB":
        return decimal_gb

    if unit == "GiB":
        return decimal_gb_to_gib(decimal_gb)

    raise ValueError(
        f"Unsupported network billing unit: {unit}"
    )


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing operational impact file: {INPUT_FILE}"
        )

    impact = pd.read_csv(INPUT_FILE)

    required_columns = {
        "handshakes_per_month",
        "scenario",
        "algorithm",
        "server_egress_gb_month",
    }

    missing = required_columns - set(impact.columns)

    if missing:
        raise RuntimeError(
            f"Missing required columns: {sorted(missing)}"
        )

    rows = []

    for provider_name, config in PROVIDERS.items():

        for _, row in impact.iterrows():

            network_units = convert_network_units(
                row["server_egress_gb_month"],
                config["network_unit"],
            )

            # --------------------------------------------
            # Standalone model
            # --------------------------------------------

            billable_standalone = max(
                0.0,
                network_units
                - config["free_units_month"],
            )

            standalone_cost = (
                billable_standalone
                * config["price_per_unit"]
            )

            # --------------------------------------------
            # Marginal / enterprise model
            #
            # Assume free allowance has already been
            # consumed by the organization's normal traffic.
            # --------------------------------------------

            marginal_billable_units = network_units

            marginal_cost = (
                marginal_billable_units
                * config["price_per_unit"]
            )

            rows.append(
                {
                    "handshakes_per_month":
                        row["handshakes_per_month"],

                    "provider":
                        provider_name,

                    "scenario":
                        row["scenario"],

                    "algorithm":
                        row["algorithm"],

                    "server_egress_gb_month":
                        row["server_egress_gb_month"],

                    "network_unit":
                        config["network_unit"],

                    "network_units_month":
                        network_units,

                    "free_units_month":
                        config["free_units_month"],

                    "price_per_unit":
                        config["price_per_unit"],

                    "standalone_billable_units":
                        billable_standalone,

                    "standalone_network_cost_month":
                        standalone_cost,

                    "marginal_billable_units":
                        marginal_billable_units,

                    "marginal_network_cost_month":
                        marginal_cost,

                    "currency":
                        config["currency"],
                }
            )

    result = pd.DataFrame(rows)

    # ========================================================
    # COST DIFFERENCES VS CLASSICAL
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
            group["scenario"] == "Classical"
        ]

        if len(classical) != 1:
            raise RuntimeError(
                "Expected exactly one Classical row for "
                f"{provider}, {handshakes:,} handshakes."
            )

        baseline = classical.iloc[0]

        group[
            "extra_standalone_network_cost_vs_classical"
        ] = (
            group["standalone_network_cost_month"]
            - baseline["standalone_network_cost_month"]
        )

        group[
            "extra_marginal_network_cost_vs_classical"
        ] = (
            group["marginal_network_cost_month"]
            - baseline["marginal_network_cost_month"]
        )

        frames.append(group)

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ========================================================
    # DISPLAY 100M CASE
    # ========================================================

    focus = result[
        result["handshakes_per_month"]
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
    ]

    print("=" * 140)
    print(
        " CLOUD NETWORK COST — "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 140)

    print(
        focus[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("MODEL:")
    print(
        "- Only server egress is charged to the cloud operator."
    )
    print(
        "- Standalone model applies the provider free allowance."
    )
    print(
        "- Marginal model assumes the free allowance has already "
        "been consumed by normal business traffic."
    )
    print(
        "- Azure billing units are modelled as decimal GB."
    )
    print(
        "- GCP traffic is converted from decimal GB to GiB."
    )
    print(
        "- ML-KEM-768 is a conceptual PQ-only baseline."
    )

    print()
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()