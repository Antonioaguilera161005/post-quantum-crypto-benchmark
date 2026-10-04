from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


AGGREGATED_DIR = Path(
    "results/raw/aggregated"
)

ECONOMIC_DIR = Path(
    "results/economic"
)

OUTPUT_DIR = Path(
    "results/figures"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# HELPERS
# ============================================================

def save_plot(filename):
    path = OUTPUT_DIR / filename

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Saved: {path}")


def add_bar_labels(
    ax,
    decimals=2,
    suffix="",
):
    """
    Add numerical labels above every bar in a plot.
    """

    for container in ax.containers:

        labels = []

        for bar in container:

            value = bar.get_height()

            if pd.isna(value):
                labels.append("")
                continue

            if abs(value) >= 1_000_000:
                label = (
                    f"{value / 1_000_000:.2f}M"
                    f"{suffix}"
                )

            elif abs(value) >= 1_000:
                label = (
                    f"{value / 1_000:.1f}k"
                    f"{suffix}"
                )

            else:
                label = (
                    f"{value:.{decimals}f}"
                    f"{suffix}"
                )

            labels.append(label)

        ax.bar_label(
            container,
            labels=labels,
            padding=3,
            fontsize=8,
        )


# ============================================================
# 1. KEY ESTABLISHMENT — TOTAL CRYPTO WORK
# ============================================================

def plot_key_establishment_compute():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "tls_key_establishment_model.csv"
    )

    order = [
        "X25519",
        "ML-KEM-768",
        "X25519MLKEM768",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        df["algorithm"],
        df["total_crypto_ms"],
    )

    ax.set_ylabel(
        "Total cryptographic work (ms)"
    )

    ax.set_title(
        "Key Establishment Cryptographic Work"
    )

    add_bar_labels(
        ax,
        decimals=3,
        suffix=" ms",
    )

    save_plot(
        "key_establishment_compute.png"
    )


# ============================================================
# 2. KEY ESTABLISHMENT — SERVER CRYPTO WORK
# ============================================================

def plot_key_establishment_server_compute():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "tls_key_establishment_model.csv"
    )

    order = [
        "X25519",
        "ML-KEM-768",
        "X25519MLKEM768",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        df["algorithm"],
        df["server_crypto_ms"],
    )

    ax.set_ylabel(
        "Server cryptographic work (ms)"
    )

    ax.set_title(
        "Server-Side Key Establishment Cost"
    )

    add_bar_labels(
        ax,
        decimals=3,
        suffix=" ms",
    )

    save_plot(
        "key_establishment_server_compute.png"
    )


# ============================================================
# 3. KEY ESTABLISHMENT — COMMUNICATION
# ============================================================

def plot_key_establishment_size():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "tls_key_establishment_model.csv"
    )

    order = [
        "X25519",
        "ML-KEM-768",
        "X25519MLKEM768",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        df["algorithm"],
        df["total_transmitted_bytes"],
    )

    ax.set_ylabel(
        "Cryptographic material transmitted (bytes)"
    )

    ax.set_title(
        "Key Establishment Communication Overhead"
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[
                f"{int(bar.get_height())} B"
                for bar in container
            ],
            padding=3,
            fontsize=9,
        )

    save_plot(
        "key_establishment_size.png"
    )


# ============================================================
# 4. SIGNATURE PERFORMANCE
# ============================================================

def plot_signature_performance():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "signature_comparison.csv"
    )

    order = [
        "ECDSA-P256",
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    plot_df = df.set_index(
        "algorithm"
    )[
        [
            "sign_ms",
            "verify_ms",
        ]
    ]

    ax = plot_df.plot(
        kind="bar",
        figsize=(10, 5.5),
    )

    ax.set_ylabel(
        "Execution time (ms)"
    )

    ax.set_xlabel("")

    ax.set_title(
        "Digital Signature Performance"
    )

    ax.legend(
        [
            "Sign",
            "Verify",
        ]
    )

    plt.xticks(
        rotation=0
    )

    add_bar_labels(
        ax,
        decimals=3,
        suffix="",
    )

    save_plot(
        "signature_performance.png"
    )


# ============================================================
# 5. SIGNATURE SIZE
# ============================================================

def plot_signature_size():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "signature_comparison.csv"
    )

    order = [
        "ECDSA-P256",
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        df["algorithm"],
        df["signature_bytes"],
    )

    ax.set_ylabel(
        "Signature size (bytes)"
    )

    ax.set_title(
        "Digital Signature Size"
    )

    add_bar_labels(
        ax,
        decimals=0,
        suffix=" B",
    )

    save_plot(
        "signature_size.png"
    )


# ============================================================
# 6. PUBLIC KEY SIZE
# ============================================================

def plot_signature_public_key_size():

    df = pd.read_csv(
        AGGREGATED_DIR
        / "signature_comparison.csv"
    )

    order = [
        "ECDSA-P256",
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]

    df = (
        df.set_index("algorithm")
        .reindex(order)
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(9, 5.5)
    )

    ax.bar(
        df["algorithm"],
        df["public_key_bytes"],
    )

    ax.set_ylabel(
        "Public key size (bytes)"
    )

    ax.set_title(
        "Digital Signature Public-Key Size"
    )

    add_bar_labels(
        ax,
        decimals=0,
        suffix=" B",
    )

    save_plot(
        "signature_public_key_size.png"
    )


# ============================================================
# 7. KEY ESTABLISHMENT CLOUD COST
# ============================================================

def plot_key_establishment_cloud_cost():

    df = pd.read_csv(
        ECONOMIC_DIR
        / "total_operational_cost.csv"
    )

    df = df[
        df["handshakes_per_month"]
        == 100_000_000
    ].copy()

    algorithm_order = [
        "X25519",
        "ML-KEM-768",
        "X25519MLKEM768",
    ]

    pivot = df.pivot(
        index="algorithm",
        columns="provider",
        values="extra_operational_cost_vs_classical",
    )

    pivot = pivot.reindex(
        algorithm_order
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 5.5),
    )

    ax.set_ylabel(
        "Additional cost vs X25519 (USD/month)"
    )

    ax.set_xlabel("")

    ax.set_title(
        "Key Establishment Operational Overhead\n"
        "100 Million Handshakes / Month"
    )

    plt.xticks(
        rotation=0
    )

    add_bar_labels(
        ax,
        decimals=2,
        suffix="",
    )

    save_plot(
        "key_establishment_cloud_cost.png"
    )


# ============================================================
# 8. SIGNATURE CLOUD COST
# ============================================================

def plot_signature_cloud_cost():

    df = pd.read_csv(
        ECONOMIC_DIR
        / "signature_cloud_cost.csv"
    )

    df = df[
        df["signed_operations_per_month"]
        == 100_000_000
    ].copy()

    algorithm_order = [
        "ECDSA-P256",
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]

    pivot = df.pivot(
        index="algorithm",
        columns="provider",
        values="extra_cost_vs_ecdsa_month",
    )

    pivot = pivot.reindex(
        algorithm_order
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 5.5),
    )

    ax.set_ylabel(
        "Additional cost vs ECDSA (USD/month)"
    )

    ax.set_xlabel("")

    ax.set_title(
        "Digital Signature Operational Overhead\n"
        "100 Million Signed Operations / Month"
    )

    plt.xticks(
        rotation=0
    )

    add_bar_labels(
        ax,
        decimals=2,
        suffix="",
    )

    save_plot(
        "signature_cloud_cost.png"
    )


# ============================================================
# 9. MIGRATION SENSITIVITY
# ============================================================

def plot_migration_sensitivity():

    df = pd.read_csv(
        ECONOMIC_DIR
        / "migration_sensitivity.csv"
    )

    pivot = df.pivot(
        index="company_scenario",
        columns="sensitivity_case",
        values="total_migration_cost",
    )

    scenario_order = [
        "Startup",
        "Mid-size",
        "Enterprise",
    ]

    sensitivity_order = [
        "Low",
        "Central",
        "High",
    ]

    pivot = pivot.reindex(
        scenario_order
    )

    pivot = pivot[
        sensitivity_order
    ]

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6),
    )

    ax.set_ylabel(
        "Modelled migration cost (scenario assumptions)"
    )

    ax.set_xlabel("")

    ax.set_title(
        "Hypothetical PQC Migration Cost Sensitivity"
    )

    ax.legend(
        title="Sensitivity case"
    )

    plt.xticks(
        rotation=0
    )

    ax.yaxis.set_major_formatter(
        FuncFormatter(
            lambda value, _:
                (
                    f"{value / 1_000_000:.1f}M"
                    if abs(value) >= 1_000_000
                    else
                    f"{value / 1_000:.0f}k"
                )
        )
    )

    add_bar_labels(
        ax,
        decimals=0,
    )

    save_plot(
        "migration_sensitivity.png"
    )


# ============================================================
# 10. SERVER COST COMPOSITION — HYBRID
# ============================================================

def plot_hybrid_cost_composition():

    df = pd.read_csv(
        ECONOMIC_DIR
        / "total_operational_cost.csv"
    )

    df = df[
        (
            df["handshakes_per_month"]
            == 100_000_000
        )
        &
        (
            df["algorithm"]
            == "X25519MLKEM768"
        )
    ].copy()

    df = df.set_index(
        "provider"
    )

    composition = df[
        [
            "compute_cost_month",
            "marginal_network_cost_month",
        ]
    ]

    composition.columns = [
        "Compute",
        "Network",
    ]

    ax = composition.plot(
        kind="bar",
        stacked=True,
        figsize=(8, 5.5),
    )

    ax.set_ylabel(
        "Operational cost (USD/month)"
    )

    ax.set_xlabel("")

    ax.set_title(
        "X25519MLKEM768 Cost Composition\n"
        "100 Million Handshakes / Month"
    )

    plt.xticks(
        rotation=0
    )

    add_bar_labels(
        ax,
        decimals=2,
    )

    save_plot(
        "hybrid_cost_composition.png"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        " GENERATING FINAL PROJECT FIGURES"
    )
    print("=" * 70)

    plot_key_establishment_compute()
    plot_key_establishment_server_compute()
    plot_key_establishment_size()

    plot_signature_performance()
    plot_signature_size()
    plot_signature_public_key_size()

    plot_key_establishment_cloud_cost()
    plot_signature_cloud_cost()

    plot_migration_sensitivity()

    plot_hybrid_cost_composition()

    print()
    print("=" * 70)
    print(" FIGURE GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"\nOutput directory: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()