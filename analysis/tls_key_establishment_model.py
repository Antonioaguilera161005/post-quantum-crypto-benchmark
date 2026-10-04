from pathlib import Path

import pandas as pd


AGGREGATED_DIR = Path("results/raw/aggregated")
OUTPUT_FILE = AGGREGATED_DIR / "tls_key_establishment_model.csv"


def load_aggregated_operations():
    """
    Load all aggregated CSV files that contain:
        algorithm, operation, mean_ms

    This avoids depending on specific aggregate filenames.
    """

    frames = []

    for path in AGGREGATED_DIR.glob("*.csv"):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue

        required = {"algorithm", "operation", "mean_ms"}

        if required.issubset(df.columns):
            frames.append(df)

    if not frames:
        raise RuntimeError(
            "No aggregated benchmark CSV containing "
            "algorithm/operation/mean_ms was found."
        )

    return pd.concat(frames, ignore_index=True)


def get_mean_ms(df, algorithm, operation):
    rows = df[
        (df["algorithm"] == algorithm)
        & (df["operation"] == operation)
    ]

    if rows.empty:
        raise RuntimeError(
            f"Could not find {algorithm} / {operation}"
        )

    return float(rows.iloc[0]["mean_ms"])


def main():

    measurements = load_aggregated_operations()

    # ========================================================
    # Measured primitive timings
    # ========================================================

    x25519_keygen = get_mean_ms(
        measurements,
        "X25519",
        "keygen",
    )

    x25519_exchange = get_mean_ms(
        measurements,
        "X25519",
        "exchange",
    )

    mlkem_keygen = get_mean_ms(
        measurements,
        "ML-KEM-768",
        "keygen",
    )

    mlkem_encaps = get_mean_ms(
        measurements,
        "ML-KEM-768",
        "encaps",
    )

    mlkem_decaps = get_mean_ms(
        measurements,
        "ML-KEM-768",
        "decaps",
    )

    # ========================================================
    # Classical X25519
    #
    # Client:
    #   key generation + exchange
    #
    # Server:
    #   key generation + exchange
    # ========================================================

    classical_client_ms = (
        x25519_keygen
        + x25519_exchange
    )

    classical_server_ms = (
        x25519_keygen
        + x25519_exchange
    )

    classical_total_ms = (
        classical_client_ms
        + classical_server_ms
    )

    # Each side sends a 32-byte X25519 share.
    classical_client_egress = 32
    classical_server_egress = 32

    # ========================================================
    # Pure ML-KEM-768 conceptual exchange
    #
    # Client:
    #   ML-KEM key generation + decapsulation
    #
    # Server:
    #   encapsulation
    #
    # Client sends encapsulation key: 1184 B
    # Server sends ciphertext:       1088 B
    #
    # This is useful as a conceptual PQ-only baseline.
    # It is NOT the RFC 10024 hybrid TLS group.
    # ========================================================

    pq_client_ms = (
        mlkem_keygen
        + mlkem_decaps
    )

    pq_server_ms = mlkem_encaps

    pq_total_ms = (
        pq_client_ms
        + pq_server_ms
    )

    pq_client_egress = 1184
    pq_server_egress = 1088

    # ========================================================
    # RFC 10024 — X25519MLKEM768
    #
    # Client:
    #   X25519 keygen
    #   X25519 exchange
    #   ML-KEM keygen
    #   ML-KEM decapsulation
    #
    # Server:
    #   X25519 keygen
    #   X25519 exchange
    #   ML-KEM encapsulation
    #
    # Client share:
    #   ML-KEM encapsulation key 1184 B
    #   X25519 share                32 B
    #   -------------------------------
    #                              1216 B
    #
    # Server share:
    #   ML-KEM ciphertext         1088 B
    #   X25519 share                32 B
    #   -------------------------------
    #                              1120 B
    #
    # RFC 10024 defines the group shared secret as:
    #
    #   ML-KEM shared secret || X25519 shared secret
    #
    # Therefore no additional hybrid-specific HKDF operation
    # is added here.
    # ========================================================

    hybrid_client_ms = (
        classical_client_ms
        + pq_client_ms
    )

    hybrid_server_ms = (
        classical_server_ms
        + pq_server_ms
    )

    hybrid_total_ms = (
        hybrid_client_ms
        + hybrid_server_ms
    )

    hybrid_client_egress = 1216
    hybrid_server_egress = 1120

    # ========================================================
    # Build comparison
    # ========================================================

    rows = [
        {
            "scenario": "Classical",
            "algorithm": "X25519",
            "client_crypto_ms": classical_client_ms,
            "server_crypto_ms": classical_server_ms,
            "total_crypto_ms": classical_total_ms,
            "client_egress_bytes": classical_client_egress,
            "server_egress_bytes": classical_server_egress,
            "total_transmitted_bytes":
                classical_client_egress
                + classical_server_egress,
            "shared_secret_bytes": 32,
            "standard": "RFC 7748 / TLS 1.3",
        },
        {
            "scenario": "Post-Quantum",
            "algorithm": "ML-KEM-768",
            "client_crypto_ms": pq_client_ms,
            "server_crypto_ms": pq_server_ms,
            "total_crypto_ms": pq_total_ms,
            "client_egress_bytes": pq_client_egress,
            "server_egress_bytes": pq_server_egress,
            "total_transmitted_bytes":
                pq_client_egress
                + pq_server_egress,
            "shared_secret_bytes": 32,
            "standard": "Conceptual PQ-only baseline",
        },
        {
            "scenario": "Hybrid",
            "algorithm": "X25519MLKEM768",
            "client_crypto_ms": hybrid_client_ms,
            "server_crypto_ms": hybrid_server_ms,
            "total_crypto_ms": hybrid_total_ms,
            "client_egress_bytes": hybrid_client_egress,
            "server_egress_bytes": hybrid_server_egress,
            "total_transmitted_bytes":
                hybrid_client_egress
                + hybrid_server_egress,
            "shared_secret_bytes": 64,
            "standard": "RFC 10024",
        },
    ]

    result = pd.DataFrame(rows)

    classical_total = result.loc[
        result["scenario"] == "Classical",
        "total_crypto_ms",
    ].iloc[0]

    classical_server = result.loc[
        result["scenario"] == "Classical",
        "server_crypto_ms",
    ].iloc[0]

    classical_traffic = result.loc[
        result["scenario"] == "Classical",
        "total_transmitted_bytes",
    ].iloc[0]

    result["total_compute_ratio_vs_x25519"] = (
        result["total_crypto_ms"]
        / classical_total
    )

    result["server_compute_ratio_vs_x25519"] = (
        result["server_crypto_ms"]
        / classical_server
    )

    result["traffic_ratio_vs_x25519"] = (
        result["total_transmitted_bytes"]
        / classical_traffic
    )

    AGGREGATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("=" * 125)
    print(
        " TLS KEY ESTABLISHMENT MODEL "
        "— RFC 10024 ROLE ASSIGNMENT"
    )
    print("=" * 125)

    display_columns = [
        "scenario",
        "algorithm",
        "client_crypto_ms",
        "server_crypto_ms",
        "total_crypto_ms",
        "client_egress_bytes",
        "server_egress_bytes",
        "total_transmitted_bytes",
        "total_compute_ratio_vs_x25519",
        "server_compute_ratio_vs_x25519",
        "traffic_ratio_vs_x25519",
    ]

    print(
        result[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("Model notes:")
    print(
        "- X25519MLKEM768 follows the client/server "
        "roles defined in RFC 10024."
    )
    print(
        "- The server performs ML-KEM encapsulation."
    )
    print(
        "- The client performs ML-KEM key generation "
        "and decapsulation."
    )
    print(
        "- Hybrid shared secret = "
        "ML-KEM secret || X25519 secret."
    )
    print(
        "- HKDF is not counted as a hybrid-specific "
        "operation because TLS applies its key schedule "
        "after group key agreement."
    )
    print(
        "- ML-KEM-768 alone is retained only as a "
        "conceptual PQ-only comparison."
    )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()