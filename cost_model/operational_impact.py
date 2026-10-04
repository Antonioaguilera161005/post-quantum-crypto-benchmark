from pathlib import Path

import pandas as pd


AGGREGATED_DIR = Path(
    "results/raw/aggregated"
)

OUTPUT_DIR = Path(
    "results/economic"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


SCALES = [
    1_000_000,
    100_000_000,
    1_000_000_000,
]


def get_operation(
    df,
    algorithm,
    operation,
):
    return df[
        (df["algorithm"] == algorithm)
        & (df["operation"] == operation)
    ].iloc[0]["mean_ms"]


def main():

    mlkem = pd.read_csv(
        AGGREGATED_DIR / "ml_kem.csv"
    )

    x25519 = pd.read_csv(
        AGGREGATED_DIR / "x25519.csv"
    )

    hkdf = pd.read_csv(
        AGGREGATED_DIR / "hkdf.csv"
    )

    # ============================================================
    # X25519
    # ============================================================

    x_keygen = get_operation(
        x25519,
        "X25519",
        "keygen",
    )

    x_exchange = get_operation(
        x25519,
        "X25519",
        "exchange",
    )

    x_server_ms = (
        x_keygen
        + x_exchange
    )

    x_client_ms = (
        x_keygen
        + x_exchange
    )

    # Server sends one 32-byte public key.
    x_server_egress = 32

    # Client sends one 32-byte public key.
    x_client_egress = 32

    # ============================================================
    # ML-KEM-768
    # ============================================================

    kem_keygen = get_operation(
        mlkem,
        "ML-KEM-768",
        "keygen",
    )

    kem_encaps = get_operation(
        mlkem,
        "ML-KEM-768",
        "encaps",
    )

    kem_decaps = get_operation(
        mlkem,
        "ML-KEM-768",
        "decaps",
    )

    # In our simplified model:
    #
    # Server:
    #   KeyGen + Decaps
    #
    # Client:
    #   Encaps

    kem_server_ms = (
        kem_keygen
        + kem_decaps
    )

    kem_client_ms = kem_encaps

    # Server sends ML-KEM public key.
    kem_server_egress = 1184

    # Client sends ciphertext.
    kem_client_egress = 1088

    # ============================================================
    # HKDF
    # ============================================================

    hkdf_ms = get_operation(
        hkdf,
        "HKDF-SHA256",
        "derive",
    )

    # ============================================================
    # HYBRID
    # ============================================================

    hybrid_server_ms = (
        x_server_ms
        + kem_server_ms
        + hkdf_ms
    )

    hybrid_client_ms = (
        x_client_ms
        + kem_client_ms
        + hkdf_ms
    )

    hybrid_server_egress = (
        x_server_egress
        + kem_server_egress
    )

    hybrid_client_egress = (
        x_client_egress
        + kem_client_egress
    )

    # ============================================================
    # SCENARIOS
    # ============================================================

    scenarios = [
        {
            "scenario": "Classical",
            "algorithm": "X25519",
            "server_crypto_ms":
                x_server_ms,
            "client_crypto_ms":
                x_client_ms,
            "server_egress_bytes":
                x_server_egress,
            "client_egress_bytes":
                x_client_egress,
        },

        {
            "scenario": "Post-Quantum",
            "algorithm": "ML-KEM-768",
            "server_crypto_ms":
                kem_server_ms,
            "client_crypto_ms":
                kem_client_ms,
            "server_egress_bytes":
                kem_server_egress,
            "client_egress_bytes":
                kem_client_egress,
        },

        {
            "scenario": "Hybrid",
            "algorithm":
                "X25519+ML-KEM-768",
            "server_crypto_ms":
                hybrid_server_ms,
            "client_crypto_ms":
                hybrid_client_ms,
            "server_egress_bytes":
                hybrid_server_egress,
            "client_egress_bytes":
                hybrid_client_egress,
        },
    ]

    rows = []

    # ============================================================
    # SCALE MODELS
    # ============================================================

    for scenario in scenarios:

        total_crypto_ms = (
            scenario["server_crypto_ms"]
            + scenario["client_crypto_ms"]
        )

        total_bytes = (
            scenario["server_egress_bytes"]
            + scenario["client_egress_bytes"]
        )

        for handshakes in SCALES:

            # Equivalent serial CPU core-hours.
            server_cpu_hours = (
                scenario["server_crypto_ms"]
                * handshakes
                / 3_600_000
            )

            total_cpu_hours = (
                total_crypto_ms
                * handshakes
                / 3_600_000
            )

            server_egress_gb = (
                scenario["server_egress_bytes"]
                * handshakes
                / 1_000_000_000
            )

            total_traffic_gb = (
                total_bytes
                * handshakes
                / 1_000_000_000
            )

            rows.append(
                {
                    **scenario,

                    "handshakes_per_month":
                        handshakes,

                    "total_crypto_ms":
                        total_crypto_ms,

                    "total_transmitted_bytes":
                        total_bytes,

                    "server_cpu_hours_month":
                        server_cpu_hours,

                    "total_cpu_hours_month":
                        total_cpu_hours,

                    "server_egress_gb_month":
                        server_egress_gb,

                    "total_crypto_traffic_gb_month":
                        total_traffic_gb,
                }
            )

    df = pd.DataFrame(rows)

    # ============================================================
    # DIFFERENCE AGAINST CLASSICAL BASELINE
    # ============================================================

    for handshakes in SCALES:

        mask = (
            df["handshakes_per_month"]
            == handshakes
        )

        subset = df[mask]

        classical = subset[
            subset["scenario"]
            == "Classical"
        ].iloc[0]

        df.loc[
            mask,
            "extra_server_cpu_hours_vs_classical",
        ] = (
            subset["server_cpu_hours_month"]
            - classical[
                "server_cpu_hours_month"
            ]
        ).values

        df.loc[
            mask,
            "extra_server_egress_gb_vs_classical",
        ] = (
            subset["server_egress_gb_month"]
            - classical[
                "server_egress_gb_month"
            ]
        ).values

    output_path = (
        OUTPUT_DIR
        / "operational_impact.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    # ============================================================
    # DISPLAY 100M SCENARIO
    # ============================================================

    display = df[
        df["handshakes_per_month"]
        == 100_000_000
    ]

    print("=" * 110)
    print(
        " OPERATIONAL IMPACT — "
        "100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 110)

    columns = [
        "scenario",
        "algorithm",
        "server_crypto_ms",
        "server_cpu_hours_month",
        "server_egress_gb_month",
        "extra_server_cpu_hours_vs_classical",
        "extra_server_egress_gb_vs_classical",
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
        f"{output_path}"
    )

    print(
        "\nNOTE:"
        "\nCPU-hours are equivalent serial "
        "core-hours derived from measured "
        "cryptographic execution time."
        "\nThey are NOT yet cloud billing figures."
    )


if __name__ == "__main__":
    main()