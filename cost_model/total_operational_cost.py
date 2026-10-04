from pathlib import Path

import pandas as pd


COMPUTE_FILE = Path(
    "results/economic/provider_compute_cost.csv"
)

NETWORK_FILE = Path(
    "results/economic/cloud_network_cost.csv"
)

OUTPUT_FILE = Path(
    "results/economic/total_operational_cost.csv"
)


def main():

    if not COMPUTE_FILE.exists():
        raise FileNotFoundError(
            f"Missing compute cost file: {COMPUTE_FILE}"
        )

    if not NETWORK_FILE.exists():
        raise FileNotFoundError(
            f"Missing network cost file: {NETWORK_FILE}"
        )

    compute = pd.read_csv(COMPUTE_FILE)
    network = pd.read_csv(NETWORK_FILE)

    # ========================================================
    # MERGE
    # ========================================================
    #
    # Network pricing currently exists only for Azure and GCP.
    # Therefore the inner join intentionally excludes AWS.
    # ========================================================

    merge_columns = [
        "handshakes_per_month",
        "provider",
        "scenario",
        "algorithm",
    ]

    result = compute.merge(
        network,
        on=merge_columns,
        how="inner",
        suffixes=("_compute", "_network"),
    )

    if result.empty:
        raise RuntimeError(
            "Compute and network datasets could not be merged."
        )

    # ========================================================
    # TOTAL COSTS
    # ========================================================

    result["standalone_total_cost_month"] = (
        result["compute_cost_month"]
        + result["standalone_network_cost_month"]
    )

    result["marginal_total_cost_month"] = (
        result["compute_cost_month"]
        + result["marginal_network_cost_month"]
    )

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
                "Expected exactly one Classical baseline for "
                f"{provider}, {handshakes:,} handshakes."
            )

        baseline = classical.iloc[0]

        group[
            "extra_standalone_cost_vs_classical_month"
        ] = (
            group["standalone_total_cost_month"]
            - baseline["standalone_total_cost_month"]
        )

        group[
            "extra_operational_cost_vs_classical"
        ] = (
            group["marginal_total_cost_month"]
            - baseline["marginal_total_cost_month"]
        )

        group[
            "extra_operational_cost_vs_classical_year"
        ] = (
            group["extra_operational_cost_vs_classical"]
            * 12
        )

        frames.append(group)

    result = pd.concat(
        frames,
        ignore_index=True,
    )

    # ========================================================
    # CLEAN OUTPUT
    # ========================================================

    output_columns = [
        "handshakes_per_month",
        "provider",
        "scenario",
        "algorithm",

        "server_cpu_hours_month",
        "compute_cost_month",

        "server_egress_gb_month",
        "network_unit",
        "network_units_month",

        "standalone_network_cost_month",
        "marginal_network_cost_month",

        "standalone_total_cost_month",
        "marginal_total_cost_month",

        "extra_standalone_cost_vs_classical_month",
        "extra_operational_cost_vs_classical",
        "extra_operational_cost_vs_classical_year",

        "currency_compute",
    ]

    # Rename currency field to one canonical name.
    result = result[
        output_columns
    ].rename(
        columns={
            "currency_compute": "currency"
        }
    )

    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_FILE.parent.mkdir(
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
        "compute_cost_month",
        "standalone_network_cost_month",
        "marginal_network_cost_month",
        "standalone_total_cost_month",
        "marginal_total_cost_month",
        "extra_operational_cost_vs_classical",
        "extra_operational_cost_vs_classical_year",
    ]

    print("=" * 165)
    print(
        " TOTAL KEY ESTABLISHMENT OPERATIONAL COST "
        "— 100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 165)

    print(
        focus[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("MODEL:")
    print(
        "- Total cost = server cryptographic compute "
        "+ server cryptographic egress."
    )
    print(
        "- Standalone cost allows provider network free tiers."
    )
    print(
        "- Marginal cost assumes free tiers are already "
        "consumed by normal business traffic."
    )
    print(
        "- extra_operational_cost_vs_classical uses the "
        "marginal model."
    )
    print(
        "- Only Azure and GCP are included because AWS "
        "network pricing has not yet been modelled."
    )
    print(
        "- ML-KEM-768 is a conceptual PQ-only baseline."
    )
    print(
        "- X25519MLKEM768 follows RFC 10024 client/server roles."
    )

    print()
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()