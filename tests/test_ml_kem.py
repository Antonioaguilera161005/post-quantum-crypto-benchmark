from algorithms.post_quantum.ml_kem import MLKEM


def test_algorithm(name):
    print(f"\n{'=' * 50}")
    print(name)
    print("=" * 50)

    mlkem = MLKEM(name)

    # Bob generates his key pair
    bob, public_key = mlkem.keygen()

    # Alice encapsulates a shared secret
    ciphertext, alice_secret = mlkem.encapsulate(public_key)

    # Bob decapsulates the same secret
    bob_secret = mlkem.decapsulate(bob, ciphertext)

    print(f"Public key:     {len(public_key):>5} bytes")
    print(f"Ciphertext:     {len(ciphertext):>5} bytes")
    print(f"Shared secret:  {len(alice_secret):>5} bytes")

    print(f"\nAlice: {alice_secret.hex()[:32]}...")
    print(f"Bob:   {bob_secret.hex()[:32]}...")

    print(
        "\nShared secrets match:",
        alice_secret == bob_secret
    )

    bob.free()

    assert alice_secret == bob_secret


if __name__ == "__main__":

    algorithms = [
        "ML-KEM-512",
        "ML-KEM-768",
        "ML-KEM-1024",
    ]

    for algorithm in algorithms:
        test_algorithm(algorithm)