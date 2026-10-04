from algorithms.classical.x25519 import X25519


def test_x25519_shared_secret_round_trip():

    algorithm = X25519()

    (
        alice_private,
        alice_public,
    ) = algorithm.keygen()

    (
        bob_private,
        bob_public,
    ) = algorithm.keygen()

    alice_secret = algorithm.exchange(
        alice_private,
        bob_public,
    )

    bob_secret = algorithm.exchange(
        bob_private,
        alice_public,
    )

    assert alice_secret == bob_secret
    assert len(alice_secret) == 32

    assert (
        len(
            algorithm.public_key_bytes(
                alice_public
            )
        )
        == 32
    )

    assert (
        len(
            algorithm.public_key_bytes(
                bob_public
            )
        )
        == 32
    )

    assert (
        len(
            algorithm.private_key_bytes(
                alice_private
            )
        )
        == 32
    )

    assert (
        len(
            algorithm.private_key_bytes(
                bob_private
            )
        )
        == 32
    )


def test_x25519_independent_keypairs():

    algorithm = X25519()

    private_a, public_a = (
        algorithm.keygen()
    )

    private_b, public_b = (
        algorithm.keygen()
    )

    assert (
        algorithm.private_key_bytes(
            private_a
        )
        != algorithm.private_key_bytes(
            private_b
        )
    )

    assert (
        algorithm.public_key_bytes(
            public_a
        )
        != algorithm.public_key_bytes(
            public_b
        )
    )