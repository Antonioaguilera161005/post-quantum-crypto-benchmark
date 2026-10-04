from algorithms.hybrid.x25519_mlkem768 import (
    X25519MLKEM768
)


def main():

    hybrid = X25519MLKEM768()

    result = hybrid.establish()

    print("=" * 60)
    print(" HYBRID X25519 + ML-KEM-768")
    print("=" * 60)

    print(
        f"\nX25519 secret: "
        f"{result['x25519_secret'].hex()[:32]}..."
    )

    print(
        f"ML-KEM secret: "
        f"{result['mlkem_secret'].hex()[:32]}..."
    )

    print(
        f"Hybrid secret: "
        f"{result['alice_secret'].hex()[:32]}..."
    )

    print(
        "\nShared hybrid secrets match:",
        result["alice_secret"]
        == result["bob_secret"]
    )

    print("\nTransmitted cryptographic material:")

    print(
        "X25519 public keys:",
        2 * result["x25519_public_key_bytes"],
        "bytes"
    )

    print(
        "ML-KEM public key:",
        result["mlkem_public_key_bytes"],
        "bytes"
    )

    print(
        "ML-KEM ciphertext:",
        result["mlkem_ciphertext_bytes"],
        "bytes"
    )

    total = (
        2 * result["x25519_public_key_bytes"]
        + result["mlkem_public_key_bytes"]
        + result["mlkem_ciphertext_bytes"]
    )

    print(
        f"\nTotal hybrid material: {total} bytes"
    )


if __name__ == "__main__":
    main()