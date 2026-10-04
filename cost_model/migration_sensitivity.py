from pathlib import Path

import pandas as pd


CONFIG_PATH = Path(
    "cost_model/config/migration_scenarios.csv"
)

OUTPUT_PATH = Path(
    "results/economic/migration_sensitivity.csv"
)


# These are sensitivity assumptions, NOT market estimates.
#
# They answer:
# "What happens if our central assumptions are too low or too high?"

SENSITIVITY_CASES = {
    "Low": {
        "hours_multiplier": 0.75,
        "hourly_cost_multiplier": 0.90,
        "hsm_multiplier": 0.50,
    },

    "Central": {
        "hours_multiplier": 1.00,
        "hourly_cost_multiplier": 1.00,
        "hsm_multiplier": 1.00,
    },

    "High": {
        "hours_multiplier": 1.50,
        "hourly_cost_multiplier": 1.20,
        "hsm_multiplier": 1.50,
    },
}


LABOR_FIELDS = [
    "crypto_inventory_hours",
    "implementation_hours",
    "testing_hours",
    "pki_hours",
    "deployment_hours",
    "training_hours",
]


ENGINEER_HOURS_PER_MONTH = 160


def main():

    scenarios = pd.read_csv(
        CONFIG_PATH
    )

    rows = []

    for _, company in scenarios.iterrows():

        base_total_hours = sum(
            company[field]
            for field in LABOR_FIELDS
        )

        for case_name, params in SENSITIVITY_CASES.items():

            adjusted_hours = (
                base_total_hours
                * params["hours_multiplier"]
            )

            adjusted_hourly_cost = (
                company["hourly_engineering_cost"]
                * params["hourly_cost_multiplier"]
            )

            labor_cost = (
                adjusted_hours
                * adjusted_hourly_cost
            )

            hsm_cost = (
                company["hsm_upgrade_cost"]
                * params["hsm_multiplier"]
            )

            total_cost = (
                labor_cost
                + hsm_cost
            )

            # Simple calendar-duration estimate.
            # Assumes work can be distributed across engineers.
            estimated_months = (
                adjusted_hours
                / (
                    company["engineers"]
                    * ENGINEER_HOURS_PER_MONTH
                )
            )

            cost_per_application = (
                total_cost
                / company["applications"]
            )

            rows.append(
                {
                    "company_scenario":
                        company["scenario"],

                    "sensitivity_case":
                        case_name,

                    "applications":
                        company["applications"],

                    "engineers":
                        company["engineers"],

                    "engineering_hours":
                        adjusted_hours,

                    "hourly_engineering_cost":
                        adjusted_hourly_cost,

                    "labor_cost":
                        labor_cost,

                    "hsm_cost":
                        hsm_cost,

                    "total_migration_cost":
                        total_cost,

                    "estimated_calendar_months":
                        estimated_months,

                    "cost_per_application":
                        cost_per_application,
                }
            )

    result = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("=" * 120)
    print(
        " PQC MIGRATION COST — "
        "SENSITIVITY ANALYSIS"
    )
    print("=" * 120)

    columns = [
        "company_scenario",
        "sensitivity_case",
        "engineering_hours",
        "labor_cost",
        "hsm_cost",
        "total_migration_cost",
        "estimated_calendar_months",
        "cost_per_application",
    ]

    print(
        result[
            columns
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.2f}"
        )
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nIMPORTANT:"
        "\nLow/Central/High are sensitivity scenarios,"
        "\nnot externally validated cost estimates."
    )


if __name__ == "__main__":
    main()