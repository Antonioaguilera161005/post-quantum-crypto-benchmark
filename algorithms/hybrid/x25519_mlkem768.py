import oqs

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class X25519MLKEM768:
    """
    Hybrid key establishment using:

        X25519
        +
        ML-KEM-768

    Both shared secrets are combined using HKDF-SHA256.
    """

    MLKEM_ALGORITHM = "ML-KEM-768"

    @staticmethod
    def combine_secrets(
        x25519_secret: bytes,
        mlkem_secret: bytes,
    ) -> bytes:

        combined = x25519_secret + mlkem_secret

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"pqc-benchmark-hybrid-x25519-mlkem768",
        )

        return hkdf.derive(combined)

    def establish(self):

        # ==========================================================
        # X25519
        # ==========================================================

        alice_x_private = x25519.X25519PrivateKey.generate()
        alice_x_public = alice_x_private.public_key()

        bob_x_private = x25519.X25519PrivateKey.generate()
        bob_x_public = bob_x_private.public_key()

        alice_x_secret = alice_x_private.exchange(
            bob_x_public
        )

        bob_x_secret = bob_x_private.exchange(
            alice_x_public
        )

        assert alice_x_secret == bob_x_secret

        # ==========================================================
        # ML-KEM-768
        # ==========================================================

        with oqs.KeyEncapsulation(
            self.MLKEM_ALGORITHM
        ) as bob_kem:

            bob_mlkem_public = bob_kem.generate_keypair()

            with oqs.KeyEncapsulation(
                self.MLKEM_ALGORITHM
            ) as alice_kem:

                ciphertext, alice_mlkem_secret = (
                    alice_kem.encap_secret(
                        bob_mlkem_public
                    )
                )

            bob_mlkem_secret = bob_kem.decap_secret(
                ciphertext
            )

        assert alice_mlkem_secret == bob_mlkem_secret

        # ==========================================================
        # HYBRID COMBINATION
        # ==========================================================

        alice_hybrid = self.combine_secrets(
            alice_x_secret,
            alice_mlkem_secret,
        )

        bob_hybrid = self.combine_secrets(
            bob_x_secret,
            bob_mlkem_secret,
        )

        assert alice_hybrid == bob_hybrid

        return {
            "alice_secret": alice_hybrid,
            "bob_secret": bob_hybrid,

            "x25519_secret": alice_x_secret,
            "mlkem_secret": alice_mlkem_secret,

            "mlkem_public_key_bytes":
                len(bob_mlkem_public),

            "mlkem_ciphertext_bytes":
                len(ciphertext),

            "x25519_public_key_bytes":
                32,
        }