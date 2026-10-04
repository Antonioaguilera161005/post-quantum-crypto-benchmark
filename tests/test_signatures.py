from algorithms.classical.ecdsa_p256 import (
    ECDSAP256,
)

from algorithms.post_quantum.ml_dsa import (
    MLDSA,
)


MESSAGE = (
    b"Post-Quantum Cryptography Benchmark"
)


def test_ecdsa():

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

    print("=" * 60)
    print("ECDSA P-256")
    print("=" * 60)

    print(
        "Public key:",
        len(
            ecdsa.public_key_bytes(
                public_key
            )
        ),
        "bytes",
    )

    print(
        "Signature:",
        len(signature),
        "bytes",
    )

    print(
        "Valid:",
        valid,
    )


def test_mldsa(algorithm):

    mldsa = MLDSA(
        algorithm
    )

    signer, public_key = (
        mldsa.keygen()
    )

    signature = mldsa.sign(
        signer,
        MESSAGE,
    )

    valid = mldsa.verify(
        public_key,
        signature,
        MESSAGE,
    )

    print("\n" + "=" * 60)
    print(algorithm)
    print("=" * 60)

    print(
        "Public key:",
        len(public_key),
        "bytes",
    )

    print(
        "Signature:",
        len(signature),
        "bytes",
    )

    print(
        "Valid:",
        valid,
    )

    signer.free()


if __name__ == "__main__":

    test_ecdsa()

    for algorithm in [
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]:
        test_mldsa(
            algorithm
        )