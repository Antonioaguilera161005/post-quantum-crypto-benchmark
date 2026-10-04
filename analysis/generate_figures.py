from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


AGGREGATED = Path("results/raw/aggregated")
ECONOMIC = Path("results/economic")

OUTPUT = Path("results/figures")
OUTPUT.mkdir(parents=True, exist_ok=True)


def save_plot(filename):
    path = OUTPUT / filename
    plt.tight_layout()
    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(f"Saved: {path}")

def add_bar_labels(ax, decimals=2, suffix=""):
    for container in ax.containers:
        labels = []

        for bar in container:
            value = bar.get_height()

            if abs(value) >= 1_000_000:
                label = f"{value / 1_000_000:.2f}M{suffix}"

            elif abs(value) >= 1_000:
                label = f"{value / 1_000:.1f}k{suffix}"

            else:
                label = f"{value:.{decimals}f}{suffix}"

            labels.append(label)

        ax.bar_label(
            container,
            labels=labels,
            padding=3,
            fontsize=8,
        )
# ============================================================
# 1. KEY ESTABLISHMENT — COMPUTE
# ============================================================

def plot_key_establishment_compute():

    df = pd.read_csv(
        AGGREGATED
        / "key_establishment_component_model.csv"
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["algorithm"],
        df["crypto_work_ms"],
    )

    plt.ylabel(
        "Cryptographic work per establishment (ms)"
    )

    plt.title(
        "Classical vs Post-Quantum Key Establishment"
    )

    plt.xticks(rotation=15)

    save_plot(
        "key_establishment_compute.png"
    )


# ============================================================
# 2. KEY ESTABLISHMENT — TRANSMITTED BYTES
# ============================================================

def plot_key_establishment_size():

    df = pd.read_csv(
        AGGREGATED
        / "key_establishment_component_model.csv"
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["algorithm"],
        df["transmitted_bytes"],
    )

    plt.ylabel(
        "Cryptographic material transmitted (bytes)"
    )

    plt.title(
        "Key Establishment Communication Overhead"
    )

    plt.xticks(rotation=15)

    save_plot(
        "key_establishment_size.png"
    )


# ============================================================
# 3. SIGNATURE PERFORMANCE
# ============================================================

def plot_signature_performance():

    df = pd.read_csv(
        AGGREGATED
        / "signature_comparison.csv"
    )

    algorithms = df["algorithm"]

    x = range(len(algorithms))

    width = 0.35

    plt.figure(figsize=(9, 5))

    plt.bar(
        [i - width / 2 for i in x],
        df["sign_ms"],
        width=width,
        label="Sign",
    )

    plt.bar(
        [i + width / 2 for i in x],
        df["verify_ms"],
        width=width,
        label="Verify",
    )

    plt.xticks(
        list(x),
        algorithms,
    )

    plt.ylabel("Execution time (ms)")

    plt.title(
        "Digital Signature Performance"
    )

    plt.legend()

    save_plot(
        "signature_performance.png"
    )


# ============================================================
# 4. SIGNATURE SIZE
# ============================================================

def plot_signature_size():

    df = pd.read_csv(
        AGGREGATED
        / "signature_comparison.csv"
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["algorithm"],
        df["signature_bytes"],
    )

    plt.ylabel("Signature size (bytes)")

    plt.title(
        "ECDSA vs ML-DSA Signature Size"
    )

    save_plot(
        "signature_size.png"
    )


# ============================================================
# 5. PUBLIC KEY SIZE — SIGNATURE SCHEMES
# ============================================================

def plot_signature_public_keys():

    df = pd.read_csv(
        AGGREGATED
        / "signature_comparison.csv"
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        df["algorithm"],
        df["public_key_bytes"],
    )

    plt.ylabel("Public key size (bytes)")

    plt.title(
        "Digital Signature Public-Key Size"
    )

    save_plot(
        "signature_public_key_size.png"
    )


# ============================================================
# 6. SIGNATURE CLOUD COST
# ============================================================

def plot_signature_cost():

    df = pd.read_csv(
        ECONOMIC
        / "signature_cloud_cost.csv"
    )

    df = df[
        df["signed_operations_per_month"]
        == 100_000_000
    ]

    pivot = df.pivot(
        index="algorithm",
        columns="provider",
        values="extra_cost_vs_ecdsa_month",
    )

    pivot.plot(
        kind="bar",
        figsize=(9, 5),
    )

    plt.ylabel(
        "Additional cost vs ECDSA (USD/month)"
    )

    plt.xlabel("")

    plt.title(
        "PQC Signature Operational Overhead\n"
        "100 Million Signed Operations / Month"
    )

    plt.xticks(rotation=0)

    save_plot(
        "signature_cloud_cost.png"
    )


# ============================================================
# 7. KEY ESTABLISHMENT CLOUD COST
# ============================================================

def plot_key_establishment_cost():

    df = pd.read_csv(
        ECONOMIC
        / "total_operational_cost.csv"
    )

    df = df[
        df["handshakes_per_month"]
        == 100_000_000
    ]

    pivot = df.pivot(
        index="algorithm",
        columns="provider_family",
        values="extra_operational_cost_vs_classical",
    )

    pivot.plot(
        kind="bar",
        figsize=(9, 5),
    )

    plt.ylabel(
        "Additional cost vs X25519 (USD/month)"
    )

    plt.xlabel("")

    plt.title(
        "PQC Key Establishment Operational Overhead\n"
        "100 Million Handshakes / Month"
    )

    plt.xticks(rotation=10)

    save_plot(
        "key_establishment_cloud_cost.png"
    )


# ============================================================
# 8. MIGRATION SENSITIVITY
# ============================================================

def plot_migration_sensitivity():

    df = pd.read_csv(
        ECONOMIC
        / "migration_sensitivity.csv"
    )

    pivot = df.pivot(
        index="company_scenario",
        columns="sensitivity_case",
        values="total_migration_cost",
    )

    order = [
        "Startup",
        "Mid-size",
        "Enterprise",
    ]

    columns = [
        c for c in
        ["Low", "Central", "High"]
        if c in pivot.columns
    ]

    pivot = pivot.reindex(order)
    pivot = pivot[columns]

    ax = pivot.plot(
        kind="bar",
        figsize=(10, 6),
    )

    plt.ylabel(
        "Modelled migration cost (€)"
    )

    plt.xlabel("")

    plt.title(
        "PQC Migration Cost Sensitivity"
    )

    plt.xticks(rotation=0)

    plt.legend(
        title="Scenario"
    )

    # Format Y axis
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(
            lambda value, _:
                f"€{value / 1_000_000:.1f}M"
                if value >= 1_000_000
                else f"€{value / 1_000:.0f}k"
        )
    )

    # Values above bars
    for container in ax.containers:

        labels = []

        for bar in container:

            value = bar.get_height()

            if value >= 1_000_000:
                label = (
                    f"€{value / 1_000_000:.2f}M"
                )
            else:
                label = (
                    f"€{value / 1_000:.1f}k"
                )

            labels.append(label)

        ax.bar_label(
            container,
            labels=labels,
            padding=3,
            fontsize=8,
        )

    save_plot(
        "migration_sensitivity.png"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(" GENERATING PROJECT FIGURES")
    print("=" * 60)

    plot_key_establishment_compute()
    plot_key_establishment_size()

    plot_signature_performance()
    plot_signature_size()
    plot_signature_public_keys()

    plot_signature_cost()
    plot_key_establishment_cost()

    plot_migration_sensitivity()

    print("\nAll figures generated.")
    print(f"Output directory: {OUTPUT}")


if __name__ == "__main__":
    main()