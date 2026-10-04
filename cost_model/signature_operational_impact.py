from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "results/raw/aggregated/signature_comparison.csv"
)

OUTPUT_PATH = Path(
    "results/economic/signature_operational_impact.csv"
)


SCALES = [
    1_000_000,
    100_000_000,
    1_000_000_000,
]


def main():

    signatures = pd.read_csv(
        INPUT_PATH
    )

    rows = []

    # Classical baseline
    baseline = signatures[
        signatures["algorithm"] == "ECDSA-P256"
    ].iloc[0]

    baseline_sign_ms = baseline["sign_ms"]
    baseline_verify_ms = baseline["verify_ms"]
    baseline_signature_bytes = baseline["signature_bytes"]

    for _, algorithm in signatures.iterrows():

        for operations in SCALES:

            # ====================================================
            # CPU COST
            # ====================================================

            # Assume the server signs.
            signer_cpu_hours = (
                algorithm["sign_ms"]
                * operations
                / 3_600_000
            )

            # Assume one verifier validates each signature.
            verifier_cpu_hours = (
                algorithm["verify_ms"]
                * operations
                / 3_600_000
            )

            total_cpu_hours = (
                signer_cpu_hours
                + verifier_cpu_hours
            )

            # ====================================================
            # NETWORK
            # ====================================================

            # Only signature bytes are counted per signed object.
            # Public keys/certificates are treated separately,
            # because they are normally reused.
            signature_traffic_gb = (
                algorithm["signature_bytes"]
                * operations
                / 1_000_000_000
            )

            # ====================================================
            # EXTRA COST VS ECDSA
            # ====================================================

            baseline_signer_hours = (
                baseline_sign_ms
                * operations
                / 3_600_000
            )

            baseline_verifier_hours = (
                baseline_verify_ms
                * operations
                / 3_600_000
            )

            baseline_total_hours = (
                baseline_signer_hours
                + baseline_verifier_hours
            )

            baseline_traffic_gb = (
                baseline_signature_bytes
                * operations
                / 1_000_000_000
            )

            extra_signer_hours = (
                signer_cpu_hours
                - baseline_signer_hours
            )

            extra_verifier_hours = (
                verifier_cpu_hours
                - baseline_verifier_hours
            )

            extra_total_cpu_hours = (
                total_cpu_hours
                - baseline_total_hours
            )

            extra_signature_traffic_gb = (
                signature_traffic_gb
                - baseline_traffic_gb
            )

            # ====================================================
            # RESULT
            # ====================================================

            rows.append(
                {
                    "type":
                        algorithm["type"],

                    "algorithm":
                        algorithm["algorithm"],

                    "signed_operations_per_month":
                        operations,

                    "sign_ms":
                        algorithm["sign_ms"],

                    "verify_ms":
                        algorithm["verify_ms"],

                    "signature_bytes":
                        algorithm["signature_bytes"],

                    "public_key_bytes":
                        algorithm["public_key_bytes"],

                    "signer_cpu_hours_month":
                        signer_cpu_hours,

                    "verifier_cpu_hours_month":
                        verifier_cpu_hours,

                    "total_signature_cpu_hours_month":
                        total_cpu_hours,

                    "signature_traffic_gb_month":
                        signature_traffic_gb,

                    "extra_signer_cpu_hours_vs_ecdsa":
                        extra_signer_hours,

                    "extra_verifier_cpu_hours_vs_ecdsa":
                        extra_verifier_hours,

                    "extra_total_cpu_hours_vs_ecdsa":
                        extra_total_cpu_hours,

                    "extra_signature_traffic_gb_vs_ecdsa":
                        extra_signature_traffic_gb,
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

    # ============================================================
    # DISPLAY — 100 MILLION SIGNATURES
    # ============================================================

    display = result[
        result["signed_operations_per_month"]
        == 100_000_000
    ]

    print("=" * 125)

    print(
        " DIGITAL SIGNATURE OPERATIONAL IMPACT — "
        "100 MILLION SIGNED OPERATIONS / MONTH"
    )

    print("=" * 125)

    columns = [
        "algorithm",
        "signer_cpu_hours_month",
        "verifier_cpu_hours_month",
        "total_signature_cpu_hours_month",
        "signature_traffic_gb_month",
        "extra_total_cpu_hours_vs_ecdsa",
        "extra_signature_traffic_gb_vs_ecdsa",
    ]

    print(
        display[
            columns
        ].to_string(
            index=False,
            float_format=lambda x:
                f"{x:.3f}",
        )
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        "\nNOTES:"
        "\n- One signing operation and one verification "
        "are assumed per signed object."
        "\n- Signature bytes are counted as network traffic."
        "\n- Public-key bytes are NOT transmitted once per "
        "signature in this model."
        "\n- Certificate / public-key distribution will be "
        "modelled separately."
    )


if __name__ == "__main__":
    main()