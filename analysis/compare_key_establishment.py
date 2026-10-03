from pathlib import Path

import pandas as pd


MLKEM_PATH = Path("results/raw/ml_kem_benchmark.csv")
X25519_PATH = Path("results/raw/x25519_benchmark.csv")

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

    # ----------------------------------------------------
    # X25519
    # ----------------------------------------------------

    x_keygen = x25519[
        x25519["operation"] == "keygen"
    ].iloc[0]

    x_exchange = x25519[
        x25519["operation"] == "exchange"
    ].iloc[0]

    # Two peers:
    # 2 key generations + 2 exchanges
    x_handshake_ms = (
        2 * x_keygen["mean_ms"]
        + 2 * x_exchange["mean_ms"]
    )

    x_transmitted_bytes = (
        2 * int(x_keygen["public_key_bytes"])
    )

    rows = []

    rows.append({
        "algorithm": "X25519",
        "crypto_work_ms": x_handshake_ms,
        "transmitted_bytes": x_transmitted_bytes,
        "compute_ratio_vs_x25519": 1.0,
        "traffic_ratio_vs_x25519": 1.0,
    })

    # ----------------------------------------------------
    # ML-KEM
    # ----------------------------------------------------

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

        crypto_work_ms = (
            keygen["mean_ms"]
            + encaps["mean_ms"]
            + decaps["mean_ms"]
        )

        transmitted_bytes = (
            int(keygen["public_key_bytes"])
            + int(keygen["ciphertext_bytes"])
        )

        rows.append({
            "algorithm": algorithm,
            "crypto_work_ms": crypto_work_ms,
            "transmitted_bytes": transmitted_bytes,
            "compute_ratio_vs_x25519":
                crypto_work_ms / x_handshake_ms,
            "traffic_ratio_vs_x25519":
                transmitted_bytes
                / x_transmitted_bytes,
        })

    comparison = pd.DataFrame(rows)

    # ----------------------------------------------------
    # Traffic at different scales
    # ----------------------------------------------------

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
                - x_transmitted_bytes
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

    print("=" * 80)
    print(" CLASSICAL VS POST-QUANTUM KEY ESTABLISHMENT")
    print("=" * 80)

    print(
        comparison[
            [
                "algorithm",
                "crypto_work_ms",
                "transmitted_bytes",
                "compute_ratio_vs_x25519",
                "traffic_ratio_vs_x25519",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}"
        )
    )

    print("\n")
    print("=" * 80)
    print(" TRAFFIC IMPACT — 100 MILLION HANDSHAKES")
    print("=" * 80)

    print(
        comparison[
            [
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