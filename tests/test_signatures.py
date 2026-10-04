import pytest

from cryptography.exceptions import InvalidSignature

from algorithms.classical.ecdsa_p256 import (
    ECDSAP256,
)

from algorithms.post_quantum.ml_dsa import (
    MLDSA,
)


MESSAGE = (
    b"Post-Quantum Cryptography Benchmark"
)

ALTERED_MESSAGE = (
    b"Post-Quantum Cryptography Benchmark!"
)


MLDSA_PARAMETER_SETS = [
    (
        "ML-DSA-44",
        1312,
        2420,
    ),
    (
        "ML-DSA-65",
        1952,
        3309,
    ),
    (
        "ML-DSA-87",
        2592,
        4627,
    ),
]


def test_ecdsa_round_trip():

    ecdsa = ECDSAP256()

    private_key, public_key = (
        ecdsa.keygen()
    )

    signature = ecdsa.sign(
        private_key,
        MESSAGE,
    )

    valid = ecdsa.verify(
        public_key,
        signature,
        MESSAGE,
    )

    assert valid is True

    assert (
        len(
            ecdsa.public_key_bytes(
                public_key
            )
        )
        == 65
    )

    # ECDSA signatures are DER encoded, so their size
    # can vary slightly between signatures.
    assert 68 <= len(signature) <= 72


def test_ecdsa_rejects_modified_message():

    ecdsa = ECDSAP256()

    private_key, public_key = (
        ecdsa.keygen()
    )

    signature = ecdsa.sign(
        private_key,
        MESSAGE,
    )

    with pytest.raises(
        InvalidSignature
    ):
        ecdsa.verify(
            public_key,
            signature,
            ALTERED_MESSAGE,
        )


@pytest.mark.parametrize(
    (
        "algorithm",
        "expected_public_key_bytes",
        "expected_signature_bytes",
    ),
    MLDSA_PARAMETER_SETS,
)
def test_mldsa_round_trip(
    algorithm,
    expected_public_key_bytes,
    expected_signature_bytes,
):

    mldsa = MLDSA(algorithm)

    signer, public_key = (
        mldsa.keygen()
    )

    try:

        signature = mldsa.sign(
            signer,
            MESSAGE,
        )

        valid = mldsa.verify(
            public_key,
            signature,
            MESSAGE,
        )

        assert valid is True

        assert (
            len(public_key)
            == expected_public_key_bytes
        )

        assert (
            len(signature)
            == expected_signature_bytes
        )

    finally:
        signer.free()


@pytest.mark.parametrize(
    "algorithm",
    [
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ],
)
def test_mldsa_rejects_modified_message(
    algorithm,
):

    mldsa = MLDSA(algorithm)

    signer, public_key = (
        mldsa.keygen()
    )

    try:

        signature = mldsa.sign(
            signer,
            MESSAGE,
        )

        valid = mldsa.verify(
            public_key,
            signature,
            ALTERED_MESSAGE,
        )

        assert valid is False

    finally:
        signer.free()


def test_mldsa_rejects_unsupported_algorithm():

    with pytest.raises(ValueError):
        MLDSA("INVALID-SIGNATURE")