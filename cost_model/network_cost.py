import argparse
from pathlib import Path

import pandas as pd


COMPARISON_PATH = Path(
    "results/raw/key_establishment_comparison.csv"
)


def calculate_cost(
    transmitted_bytes,
    handshakes,
    price_per_gb,
):
    total_bytes = transmitted_bytes * handshakes
    total_gb = total_bytes / 1_000_000_000

    cost = total_gb * price_per_gb

    return total_gb, cost


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Estimate network cost of classical, "
            "post-quantum and hybrid key establishment."
        )
    )

    parser.add_argument(
        "--handshakes",
        type=int,
        required=True,
        help="Number of key establishments per month",
    )

    parser.add_argument(
        "--price-per-gb",
        type=float,
        required=True,
        help="Network price in EUR per GB",
    )

    args = parser.parse_args()

    comparison = pd.read_csv(
        COMPARISON_PATH
    )

    x25519 = comparison[
        comparison["algorithm"] == "X25519"
    ].iloc[0]

    baseline_gb, baseline_cost = calculate_cost(
        x25519["transmitted_bytes"],
        args.handshakes,
        args.price_per_gb,
    )

    rows = []

    for _, row in comparison.iterrows():

        traffic_gb, cost = calculate_cost(
            row["transmitted_bytes"],
            args.handshakes,
            args.price_per_gb,
        )

        rows.append(
            {
                "scenario": row["scenario"],
                "algorithm": row["algorithm"],
                "traffic_gb_month": traffic_gb,
                "network_cost_eur_month": cost,
                "extra_traffic_gb":
                    traffic_gb - baseline_gb,
                "extra_cost_eur":
                    cost - baseline_cost,
            }
        )

    results = pd.DataFrame(rows)

    print("=" * 95)
    print(" POST-QUANTUM NETWORK COST MODEL")
    print("=" * 95)

    print(
        f"\nHandshakes/month: "
        f"{args.handshakes:,}"
    )

    print(
        f"Network price: "
        f"€{args.price_per_gb:.4f}/GB\n"
    )

    print(
        results.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}"
        )
    )

    print(
        "\nIMPORTANT: This model includes only "
        "cryptographic key-establishment material."
    )

    print(
        "It does not represent total TLS/network traffic."
    )


if __name__ == "__main__":
    main()