from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "cost_model/config/migration_scenarios.csv"
)

OUTPUT_FILE = Path(
    "results/economic/migration_sensitivity.csv"
)


HOUR_COLUMNS = [
    "crypto_inventory_hours",
    "implementation_hours",
    "testing_hours",
    "pki_hours",
    "deployment_hours",
    "training_hours",
]


SENSITIVITY_CASES = {
    "Low": {
        "engineering_hours_multiplier": 0.75,
        "hourly_cost_multiplier": 0.90,
        "hsm_cost_multiplier": 0.50,
    },

    "Central": {
        "engineering_hours_multiplier": 1.00,
        "hourly_cost_multiplier": 1.00,
        "hsm_cost_multiplier": 1.00,
    },

    "High": {
        "engineering_hours_multiplier": 1.50,
        "hourly_cost_multiplier": 1.20,
        "hsm_cost_multiplier": 1.50,
    },
}


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing migration scenario file: {INPUT_FILE}"
        )

    scenarios = pd.read_csv(INPUT_FILE)

    rows = []

    for _, scenario in scenarios.iterrows():

        base_hours = sum(
            scenario[column]
            for column in HOUR_COLUMNS
        )

        for (
            sensitivity_case,
            assumptions,
        ) in SENSITIVITY_CASES.items():

            adjusted_hours = (
                base_hours
                * assumptions[
                    "engineering_hours_multiplier"
                ]
            )

            adjusted_hourly_cost = (
                scenario[
                    "hourly_engineering_cost"
                ]
                * assumptions[
                    "hourly_cost_multiplier"
                ]
            )

            engineering_labor_cost = (
                adjusted_hours
                * adjusted_hourly_cost
            )

            adjusted_hsm_cost = (
                scenario[
                    "hsm_upgrade_cost"
                ]
                * assumptions[
                    "hsm_cost_multiplier"
                ]
            )

            total_migration_cost = (
                engineering_labor_cost
                + adjusted_hsm_cost
            )

            # ------------------------------------------------
            # IDEALIZED PARALLELISM INDICATOR
            # ------------------------------------------------
            #
            # This is NOT a real calendar-duration estimate.
            #
            # It assumes:
            #   - 160 productive hours per engineer/month
            #   - every task is perfectly parallelizable
            #   - no dependencies, approvals, vendor delays,
            #     testing gates or deployment windows
            #
            # It is retained only as a workload-normalization
            # indicator.
            # ------------------------------------------------

            idealized_parallel_months = (
                adjusted_hours
                / (
                    scenario["engineers"]
                    * 160
                )
            )

            rows.append(
                {
                    "company_scenario":
                        scenario["scenario"],

                    "sensitivity_case":
                        sensitivity_case,

                    "applications":
                        scenario["applications"],

                    "engineers":
                        scenario["engineers"],

                    "engineering_hours_multiplier":
                        assumptions[
                            "engineering_hours_multiplier"
                        ],

                    "hourly_cost_multiplier":
                        assumptions[
                            "hourly_cost_multiplier"
                        ],

                    "hsm_cost_multiplier":
                        assumptions[
                            "hsm_cost_multiplier"
                        ],

                    "adjusted_engineering_hours":
                        adjusted_hours,

                    "adjusted_hourly_engineering_cost":
                        adjusted_hourly_cost,

                    "engineering_labor_cost":
                        engineering_labor_cost,

                    "adjusted_hsm_upgrade_cost":
                        adjusted_hsm_cost,

                    "total_migration_cost":
                        total_migration_cost,

                    "idealized_parallel_months":
                        idealized_parallel_months,

                    "model_type":
                        "hypothetical_sensitivity_scenario",

                    "empirical_market_estimate":
                        False,
                }
            )

    result = pd.DataFrame(rows)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("=" * 120)
    print(
        " PQC MIGRATION COST SENSITIVITY "
        "— HYPOTHETICAL SCENARIOS"
    )
    print("=" * 120)

    display_columns = [
        "company_scenario",
        "sensitivity_case",
        "adjusted_engineering_hours",
        "engineering_labor_cost",
        "adjusted_hsm_upgrade_cost",
        "total_migration_cost",
        "idealized_parallel_months",
    ]

    print(
        result[display_columns]
        .round(2)
        .to_string(index=False)
    )

    print()
    print("IMPORTANT:")
    print(
        "- Cost values are hypothetical scenario outputs, "
        "not observed market migration costs."
    )
    print(
        "- idealized_parallel_months is NOT an estimate of "
        "real migration duration."
    )
    print(
        "- It assumes perfect parallelism and 160 productive "
        "hours per engineer per month."
    )
    print(
        "- Real PQC migrations can include dependencies, "
        "procurement, interoperability testing, vendor support "
        "and staged deployment."
    )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()