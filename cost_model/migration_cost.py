from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "cost_model/config/migration_scenarios.csv"
)

OUTPUT_FILE = Path(
    "results/economic/migration_cost.csv"
)


HOUR_COLUMNS = [
    "crypto_inventory_hours",
    "implementation_hours",
    "testing_hours",
    "pki_hours",
    "deployment_hours",
    "training_hours",
]


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing migration scenario file: {INPUT_FILE}"
        )

    scenarios = pd.read_csv(INPUT_FILE)

    required_columns = {
        "scenario",
        "applications",
        "engineers",
        "hourly_engineering_cost",
        "hsm_upgrade_cost",
        *HOUR_COLUMNS,
    }

    missing = required_columns - set(
        scenarios.columns
    )

    if missing:
        raise RuntimeError(
            f"Missing columns: {sorted(missing)}"
        )

    result = scenarios.copy()

    result["total_engineering_hours"] = (
        result[HOUR_COLUMNS].sum(axis=1)
    )

    result["engineering_labor_cost"] = (
        result["total_engineering_hours"]
        * result["hourly_engineering_cost"]
    )

    result["total_migration_cost"] = (
        result["engineering_labor_cost"]
        + result["hsm_upgrade_cost"]
    )

    result["model_type"] = (
        "hypothetical_configurable_scenario"
    )

    result["empirical_market_estimate"] = False

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("=" * 105)
    print(
        " PQC MIGRATION COST MODEL "
        "— HYPOTHETICAL SCENARIOS"
    )
    print("=" * 105)

    display_columns = [
        "scenario",
        "applications",
        "engineers",
        "total_engineering_hours",
        "hourly_engineering_cost",
        "engineering_labor_cost",
        "hsm_upgrade_cost",
        "total_migration_cost",
    ]

    print(
        result[display_columns]
        .round(2)
        .to_string(index=False)
    )

    print()
    print("IMPORTANT:")
    print(
        "- These are configurable scenario outputs."
    )
    print(
        "- They are NOT empirical market estimates."
    )
    print(
        "- Engineering hours and HSM costs are modelling "
        "assumptions defined in migration_scenarios.csv."
    )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()