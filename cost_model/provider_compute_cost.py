from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_DIR = Path("results/economic")
OUTPUT_FILE = OUTPUT_DIR / "provider_compute_cost.csv"


# ============================================================
# PROVIDER COMPUTE ASSUMPTIONS
# ============================================================
#
# These are modelling inputs already used in the project.
# Later we will move them into a config CSV with:
#
# provider
# region
# instance
# VM price
# vCPU count
# source
# checked date
#
# For now we keep the same assumptions so the model remains
# internally consistent while we correct the cryptographic data.
# ============================================================

PROVIDERS = {
    "AWS": {
        "instance": "m7i.large",
        "region": "Spain",
        "vm_price_per_hour": 0.1124,
        "vcpus": 2,
        "currency": "USD",
    },
    "Azure": {
        "instance": "D2s_v5",
        "region": "Spain",
        "vm_price_per_hour": 0.1070,
        "vcpus": 2,
        "currency": "USD",
    },
    "GCP": {
        "instance": "e2-standard-2",
        "region": "Madrid",
        "vm_price_per_hour": 0.07908,
        "vcpus": 2,
        "currency": "USD",
    },
}


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
        "server_cpu_hours_month",
    }

    missing = required_columns - set(impact.columns)

    if missing:
        raise RuntimeError(
            f"Missing required columns: {sorted(missing)}"
        )

    rows = []

    for provider_name, config in PROVIDERS.items():

        price_per_vcpu_hour = (
            config["vm_price_per_hour"]
            / config["vcpus"]
        )

        for _, row in impact.iterrows():

            server_cpu_hours = (
                row["server_cpu_hours_month"]
            )

            compute_cost = (
                server_cpu_hours
                * price_per_vcpu_hour
            )

            rows.append(
                {
                    "handshakes_per_month":
                        row["handshakes_per_month"],

                    "provider":
                        provider_name,

                    "region":
                        config["region"],

                    "instance":
                        config["instance"],

                    "scenario":
                        row["scenario"],

                    "algorithm":
                        row["algorithm"],

                    "server_cpu_hours_month":
                        server_cpu_hours,

                    "vm_price_per_hour":
                        config["vm_price_per_hour"],

                    "vcpus":
                        config["vcpus"],

                    "price_per_vcpu_hour":
                        price_per_vcpu_hour,

                    "compute_cost_month":
                        compute_cost,

                    "currency":
                        config["currency"],
                }
            )

    result = pd.DataFrame(rows)

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
            group["scenario"] == "Classical"
        ]

        if len(classical) != 1:
            raise RuntimeError(
                "Expected exactly one Classical row for "
                f"{provider}, {handshakes:,} handshakes."
            )

        baseline = classical.iloc[0]

        group[
            "extra_compute_cost_vs_classical"
        ] = (
            group["compute_cost_month"]
            - baseline["compute_cost_month"]
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
        "server_cpu_hours_month",
        "price_per_vcpu_hour",
        "compute_cost_month",
        "extra_compute_cost_vs_classical",
    ]

    print("=" * 125)
    print(
        " PROVIDER COMPUTE COST — "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 125)

    print(
        focus[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("MODEL:")
    print(
        "- Only server-side cryptographic CPU is charged."
    )
    print(
        "- Client-side computation is excluded from the "
        "cloud operator cost."
    )
    print(
        "- Equivalent CPU-hours are multiplied by an "
        "estimated USD/vCPU-hour rate."
    )
    print(
        "- This is a simplified resource-cost model, not "
        "full VM billing."
    )
    print(
        "- ML-KEM-768 is a conceptual PQ-only baseline."
    )
    print(
        "- X25519MLKEM768 follows the RFC 10024 role model."
    )

    print()
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()