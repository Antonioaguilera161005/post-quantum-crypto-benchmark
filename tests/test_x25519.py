from algorithms.classical.x25519 import X25519


def main():
    x25519 = X25519()

    # Alice
    alice_private, alice_public = x25519.keygen()

    # Bob
    bob_private, bob_public = x25519.keygen()

    # Both derive the shared secret
    alice_secret = x25519.exchange(
        alice_private,
        bob_public,
    )

    bob_secret = x25519.exchange(
        bob_private,
        alice_public,
    )

    print("=" * 50)
    print("X25519")
    print("=" * 50)

    print(
        f"Public key:    "
        f"{len(x25519.public_key_bytes(alice_public))} bytes"
    )

    print(
        f"Private key:   "
        f"{len(x25519.private_key_bytes(alice_private))} bytes"
    )

    print(
        f"Shared secret: "
        f"{len(alice_secret)} bytes"
    )

    print()
    print(f"Alice: {alice_secret.hex()[:32]}...")
    print(f"Bob:   {bob_secret.hex()[:32]}...")

    print(
        "\nShared secrets match:",
        alice_secret == bob_secret
    )

    assert alice_secret == bob_secret


if __name__ == "__main__":
    main()