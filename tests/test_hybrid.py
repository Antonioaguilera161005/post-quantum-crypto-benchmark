from algorithms.hybrid.x25519_mlkem768 import (
    X25519MLKEM768,
)


def test_x25519_mlkem768_shared_secret():

    hybrid = X25519MLKEM768()

    result = hybrid.establish()

    assert (
        result["client_secret"]
        == result["server_secret"]
    )

    assert (
        result["hybrid_secret_bytes"]
        == 64
    )


def test_x25519_mlkem768_secret_layout():

    hybrid = X25519MLKEM768()

    result = hybrid.establish()

    shared_secret = (
        result["client_secret"]
    )

    # RFC 10024:
    #
    # ML-KEM shared secret
    # ||
    # X25519 shared secret

    assert (
        shared_secret[:32]
        == result["mlkem_secret"]
    )

    assert (
        shared_secret[32:]
        == result["x25519_secret"]
    )


def test_x25519_mlkem768_sizes():

    hybrid = X25519MLKEM768()

    result = hybrid.establish()

    assert (
        result["mlkem_public_key_bytes"]
        == 1184
    )

    assert (
        result["mlkem_ciphertext_bytes"]
        == 1088
    )

    assert (
        result["x25519_public_key_bytes"]
        == 32
    )

    assert (
        result["client_share_bytes"]
        == 1216
    )

    assert (
        result["server_share_bytes"]
        == 1120
    )