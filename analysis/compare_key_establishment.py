from pathlib import Path

import pandas as pd


MLKEM_PATH = Path("results/raw/ml_kem_benchmark.csv")
X25519_PATH = Path("results/raw/x25519_benchmark.csv")
HYBRID_PATH = Path("results/raw/hybrid_benchmark.csv")

OUTPUT_PATH = Path(
    "results/raw/key_establishment_comparison.csv"
)

SCALES = [
    1_000_000,
    100_000_000,
    1_000_000_000,
]


def main():

    mlkem = pd.read_csv(MLKEM_PATH)
    x25519 = pd.read_csv(X25519_PATH)
    hybrid = pd.read_csv(HYBRID_PATH)

    # ============================================================
    # X25519
    # ============================================================

    x_keygen = x25519[
        x25519["operation"] == "keygen"
    ].iloc[0]

    x_exchange = x25519[
        x25519["operation"] == "exchange"
    ].iloc[0]

    # Two participants:
    # 2 keygens + 2 shared-secret derivations
    x_crypto_ms = (
        2 * x_keygen["mean_ms"]
        + 2 * x_exchange["mean_ms"]
    )

    x_bytes = (
        2 * int(x_keygen["public_key_bytes"])
    )

    rows = [
        {
            "scenario": "Classical",
            "algorithm": "X25519",
            "crypto_work_ms": x_crypto_ms,
            "transmitted_bytes": x_bytes,
            "measurement_type": "primitive_sum",
        }
    ]

    # ============================================================
    # POST-QUANTUM
    # ============================================================

    for algorithm in mlkem["algorithm"].unique():

        data = mlkem[
            mlkem["algorithm"] == algorithm
        ]

        keygen = data[
            data["operation"] == "keygen"
        ].iloc[0]

        encaps = data[
            data["operation"] == "encaps"
        ].iloc[0]

        decaps = data[
            data["operation"] == "decaps"
        ].iloc[0]

        crypto_ms = (
            keygen["mean_ms"]
            + encaps["mean_ms"]
            + decaps["mean_ms"]
        )

        transmitted_bytes = (
            int(keygen["public_key_bytes"])
            + int(keygen["ciphertext_bytes"])
        )

        rows.append(
            {
                "scenario": "Post-Quantum",
                "algorithm": algorithm,
                "crypto_work_ms": crypto_ms,
                "transmitted_bytes": transmitted_bytes,
                "measurement_type": "primitive_sum",
            }
        )

    # ============================================================
    # HYBRID
    # ============================================================

    hybrid_row = hybrid.iloc[0]

    rows.append(
        {
            "scenario": "Hybrid",
            "algorithm": "X25519+ML-KEM-768",
            "crypto_work_ms": hybrid_row["mean_ms"],
            "transmitted_bytes":
                int(hybrid_row["transmitted_bytes"]),
            "measurement_type": "end_to_end",
        }
    )

    comparison = pd.DataFrame(rows)

    # ============================================================
    # RATIOS
    # ============================================================

    comparison["compute_ratio_vs_x25519"] = (
        comparison["crypto_work_ms"]
        / x_crypto_ms
    )

    comparison["traffic_ratio_vs_x25519"] = (
        comparison["transmitted_bytes"]
        / x_bytes
    )

    # ============================================================
    # SCALE
    # ============================================================

    for handshakes in SCALES:

        comparison[
            f"traffic_GB_{handshakes}"
        ] = (
            comparison["transmitted_bytes"]
            * handshakes
            / 1_000_000_000
        )

        comparison[
            f"extra_GB_vs_x25519_{handshakes}"
        ] = (
            (
                comparison["transmitted_bytes"]
                - x_bytes
            )
            * handshakes
            / 1_000_000_000
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    comparison.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ============================================================
    # DISPLAY
    # ============================================================

    print("=" * 100)
    print(" KEY ESTABLISHMENT SCENARIOS")
    print("=" * 100)

    columns = [
        "scenario",
        "algorithm",
        "crypto_work_ms",
        "transmitted_bytes",
        "compute_ratio_vs_x25519",
        "traffic_ratio_vs_x25519",
        "measurement_type",
    ]

    print(
        comparison[columns].to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}"
        )
    )

    print("\n")
    print("=" * 100)
    print(" TRAFFIC IMPACT — 100 MILLION HANDSHAKES / MONTH")
    print("=" * 100)

    print(
        comparison[
            [
                "scenario",
                "algorithm",
                "traffic_GB_100000000",
                "extra_GB_vs_x25519_100000000",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}"
        )
    )

    print(
        f"\nResults saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()