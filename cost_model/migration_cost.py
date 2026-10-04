from pathlib import Path

import pandas as pd


CONFIG_PATH = Path(
    "cost_model/config/migration_scenarios.csv"
)

OUTPUT_PATH = Path(
    "results/economic/migration_cost.csv"
)


LABOR_FIELDS = [
    "crypto_inventory_hours",
    "implementation_hours",
    "testing_hours",
    "pki_hours",
    "deployment_hours",
    "training_hours",
]


def main():

    scenarios = pd.read_csv(
        CONFIG_PATH
    )

    rows = []

    for _, row in scenarios.iterrows():

        hourly_rate = (
            row["hourly_engineering_cost"]
        )

        # ---------------------------------------------------------
        # Individual labor components
        # ---------------------------------------------------------

        inventory_cost = (
            row["crypto_inventory_hours"]
            * hourly_rate
        )

        implementation_cost = (
            row["implementation_hours"]
            * hourly_rate
        )

        testing_cost = (
            row["testing_hours"]
            * hourly_rate
        )

        pki_cost = (
            row["pki_hours"]
            * hourly_rate
        )

        deployment_cost = (
            row["deployment_hours"]
            * hourly_rate
        )

        training_cost = (
            row["training_hours"]
            * hourly_rate
        )

        labor_cost = (
            inventory_cost
            + implementation_cost
            + testing_cost
            + pki_cost
            + deployment_cost
            + training_cost
        )

        infrastructure_cost = (
            row["hsm_upgrade_cost"]
        )

        total_migration_cost = (
            labor_cost
            + infrastructure_cost
        )

        total_hours = sum(
            row[field]
            for field in LABOR_FIELDS
        )

        rows.append(
            {
                "scenario":
                    row["scenario"],

                "applications":
                    row["applications"],

                "engineers":
                    row["engineers"],

                "hourly_engineering_cost":
                    hourly_rate,

                "total_engineering_hours":
                    total_hours,

                "crypto_inventory_cost":
                    inventory_cost,

                "implementation_cost":
                    implementation_cost,

                "testing_cost":
                    testing_cost,

                "pki_cost":
                    pki_cost,

                "deployment_cost":
                    deployment_cost,

                "training_cost":
                    training_cost,

                "labor_cost":
                    labor_cost,

                "hsm_upgrade_cost":
                    infrastructure_cost,

                "total_migration_cost":
                    total_migration_cost,
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

    print("=" * 110)
    print(
        " POST-QUANTUM MIGRATION COST MODEL"
    )
    print("=" * 110)

    columns = [
        "scenario",
        "applications",
        "engineers",
        "total_engineering_hours",
        "labor_cost",
        "hsm_upgrade_cost",
        "total_migration_cost",
    ]

    print(
        result[
            columns
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.2f}",
        )
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nIMPORTANT:"
        "\nThese are configurable scenario assumptions."
        "\nThey are NOT claims about actual migration costs."
    )


if __name__ == "__main__":
    main()