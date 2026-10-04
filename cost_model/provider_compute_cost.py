from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "results/economic/operational_impact.csv"
)

OUTPUT_PATH = Path(
    "results/economic/provider_compute_cost.csv"
)


PROVIDERS = {
    "AWS-Spain-m7i.large": {
        "vm_price_per_hour": 0.1124,
        "vcpus": 2,
        "currency": "USD",
    },

    "Azure-Spain-D2s_v5": {
        "vm_price_per_hour": 0.1070,
        "vcpus": 2,
        "currency": "USD",
    },

    "GCP-Madrid-e2-standard-2": {
        "vm_price_per_hour": 0.07908,
        "vcpus": 2,
        "currency": "USD",
    },
}


def main():

    operational = pd.read_csv(
        INPUT_PATH
    )

    rows = []

    for provider, pricing in PROVIDERS.items():

        price_per_vcpu_hour = (
            pricing["vm_price_per_hour"]
            / pricing["vcpus"]
        )

        for _, row in operational.iterrows():

            compute_cost = (
                row["server_cpu_hours_month"]
                * price_per_vcpu_hour
            )

            extra_compute_cost = (
                row[
                    "extra_server_cpu_hours_vs_classical"
                ]
                * price_per_vcpu_hour
            )

            rows.append(
                {
                    "provider": provider,
                    "scenario": row["scenario"],
                    "algorithm": row["algorithm"],

                    "handshakes_per_month":
                        row["handshakes_per_month"],

                    "server_cpu_hours_month":
                        row["server_cpu_hours_month"],

                    "vm_price_per_hour":
                        pricing["vm_price_per_hour"],

                    "vcpus":
                        pricing["vcpus"],

                    "price_per_vcpu_hour":
                        price_per_vcpu_hour,

                    "compute_cost_month":
                        compute_cost,

                    "extra_compute_cost_vs_classical":
                        extra_compute_cost,

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

    print("=" * 120)
    print(
        " PROVIDER COMPUTE COST — "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 120)

    columns = [
        "provider",
        "scenario",
        "server_cpu_hours_month",
        "price_per_vcpu_hour",
        "compute_cost_month",
        "extra_compute_cost_vs_classical",
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
        "\nIMPORTANT:"
        "\nThese are CPU-equivalent marginal cost estimates."
        "\nThey do not represent the full cost of running the VM."
    )


if __name__ == "__main__":
    main()