from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = Path(
    "results/raw/aggregated/tls_key_establishment_model.csv"
)

OUTPUT_DIR = Path("results/economic")
OUTPUT_FILE = OUTPUT_DIR / "operational_impact.csv"


# ============================================================
# WORKLOADS
# ============================================================

HANDSHAKE_VOLUMES = [
    1_000_000,
    100_000_000,
    1_000_000_000,
]


def ms_to_cpu_hours(milliseconds_per_operation, operations):
    """
    Convert per-operation milliseconds into equivalent
    serial CPU-hours.

    This is NOT VM wall-clock time or a cloud bill by itself.
    """
    total_ms = milliseconds_per_operation * operations
    total_seconds = total_ms / 1000
    return total_seconds / 3600


def bytes_to_decimal_gb(bytes_per_operation, operations):
    """
    Convert bytes to decimal GB.

    1 GB = 1,000,000,000 bytes
    """
    total_bytes = bytes_per_operation * operations
    return total_bytes / 1_000_000_000


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing canonical TLS model: {INPUT_FILE}"
        )

    model = pd.read_csv(INPUT_FILE)

    required_columns = {
        "scenario",
        "algorithm",
        "client_crypto_ms",
        "server_crypto_ms",
        "total_crypto_ms",
        "client_egress_bytes",
        "server_egress_bytes",
        "total_transmitted_bytes",
    }

    missing = required_columns - set(model.columns)

    if missing:
        raise RuntimeError(
            f"Missing columns in TLS model: {sorted(missing)}"
        )

    rows = []

    for handshakes in HANDSHAKE_VOLUMES:

        for _, row in model.iterrows():

            client_cpu_hours = ms_to_cpu_hours(
                row["client_crypto_ms"],
                handshakes,
            )

            server_cpu_hours = ms_to_cpu_hours(
                row["server_crypto_ms"],
                handshakes,
            )

            total_cpu_hours = ms_to_cpu_hours(
                row["total_crypto_ms"],
                handshakes,
            )

            client_egress_gb = bytes_to_decimal_gb(
                row["client_egress_bytes"],
                handshakes,
            )

            server_egress_gb = bytes_to_decimal_gb(
                row["server_egress_bytes"],
                handshakes,
            )

            total_crypto_traffic_gb = bytes_to_decimal_gb(
                row["total_transmitted_bytes"],
                handshakes,
            )

            rows.append(
                {
                    "handshakes_per_month": handshakes,
                    "scenario": row["scenario"],
                    "algorithm": row["algorithm"],

                    "client_crypto_ms":
                        row["client_crypto_ms"],

                    "server_crypto_ms":
                        row["server_crypto_ms"],

                    "total_crypto_ms":
                        row["total_crypto_ms"],

                    "client_cpu_hours_month":
                        client_cpu_hours,

                    "server_cpu_hours_month":
                        server_cpu_hours,

                    "total_cpu_hours_month":
                        total_cpu_hours,

                    "client_egress_bytes_per_handshake":
                        row["client_egress_bytes"],

                    "server_egress_bytes_per_handshake":
                        row["server_egress_bytes"],

                    "client_egress_gb_month":
                        client_egress_gb,

                    "server_egress_gb_month":
                        server_egress_gb,

                    "total_crypto_traffic_gb_month":
                        total_crypto_traffic_gb,
                }
            )

    result = pd.DataFrame(rows)

    # ========================================================
    # COMPUTE DIFFERENCES VS CLASSICAL
    # ========================================================

    output_frames = []

    for handshakes, group in result.groupby(
        "handshakes_per_month"
    ):

        group = group.copy()

        classical = group[
            group["scenario"] == "Classical"
        ]

        if len(classical) != 1:
            raise RuntimeError(
                "Expected exactly one Classical row "
                f"for {handshakes:,} handshakes."
            )

        baseline = classical.iloc[0]

        group[
            "extra_server_cpu_hours_vs_classical"
        ] = (
            group["server_cpu_hours_month"]
            - baseline["server_cpu_hours_month"]
        )

        group[
            "extra_server_egress_gb_vs_classical"
        ] = (
            group["server_egress_gb_month"]
            - baseline["server_egress_gb_month"]
        )

        group[
            "extra_total_cpu_hours_vs_classical"
        ] = (
            group["total_cpu_hours_month"]
            - baseline["total_cpu_hours_month"]
        )

        group[
            "extra_total_crypto_traffic_gb_vs_classical"
        ] = (
            group["total_crypto_traffic_gb_month"]
            - baseline["total_crypto_traffic_gb_month"]
        )

        output_frames.append(group)

    result = pd.concat(
        output_frames,
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
        "scenario",
        "algorithm",
        "server_crypto_ms",
        "server_cpu_hours_month",
        "server_egress_gb_month",
        "extra_server_cpu_hours_vs_classical",
        "extra_server_egress_gb_vs_classical",
    ]

    print("=" * 120)
    print(
        " KEY ESTABLISHMENT OPERATIONAL IMPACT "
        "— 100 MILLION HANDSHAKES / MONTH"
    )
    print("=" * 120)

    print(
        focus[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("Additional context:")

    context_columns = [
        "scenario",
        "client_cpu_hours_month",
        "server_cpu_hours_month",
        "total_cpu_hours_month",
        "client_egress_gb_month",
        "server_egress_gb_month",
        "total_crypto_traffic_gb_month",
    ]

    print(
        focus[context_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("MODEL:")
    print(
        "- Roles come from the canonical TLS key-establishment model."
    )
    print(
        "- X25519MLKEM768 uses RFC 10024 client/server roles."
    )
    print(
        "- Server-side compute and server egress are the quantities "
        "used for company/cloud cost estimation."
    )
    print(
        "- Client-side resource use is reported separately and is "
        "not charged to the server operator."
    )
    print(
        "- CPU-hours are equivalent serial CPU-hours, not VM "
        "wall-clock hours."
    )
    print(
        "- Traffic values use decimal GB."
    )
    print(
        "- ML-KEM-768 alone is a conceptual PQ-only baseline, "
        "not the RFC 10024 hybrid group."
    )

    print()
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()