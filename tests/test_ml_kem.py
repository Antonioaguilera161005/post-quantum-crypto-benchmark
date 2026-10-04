import pytest

from algorithms.post_quantum.ml_kem import MLKEM


PARAMETER_SETS = [
    (
        "ML-KEM-512",
        800,
        768,
    ),
    (
        "ML-KEM-768",
        1184,
        1088,
    ),
    (
        "ML-KEM-1024",
        1568,
        1568,
    ),
]


@pytest.mark.parametrize(
    (
        "algorithm",
        "expected_public_key_bytes",
        "expected_ciphertext_bytes",
    ),
    PARAMETER_SETS,
)
def test_mlkem_round_trip(
    algorithm,
    expected_public_key_bytes,
    expected_ciphertext_bytes,
):

    mlkem = MLKEM(algorithm)

    receiver, public_key = mlkem.keygen()

    try:
        ciphertext, sender_secret = (
            mlkem.encapsulate(
                public_key
            )
        )

        receiver_secret = (
            mlkem.decapsulate(
                receiver,
                ciphertext,
            )
        )

        assert (
            sender_secret
            == receiver_secret
        )

        assert len(sender_secret) == 32

        assert (
            len(public_key)
            == expected_public_key_bytes
        )

        assert (
            len(ciphertext)
            == expected_ciphertext_bytes
        )

    finally:
        receiver.free()


def test_mlkem_rejects_unsupported_algorithm():

    with pytest.raises(ValueError):
        MLKEM("INVALID-KEM")