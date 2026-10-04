import oqs

from cryptography.hazmat.primitives.asymmetric import x25519


class X25519MLKEM768:
    """
    Experimental implementation of the X25519MLKEM768
    hybrid key-agreement structure defined by RFC 10024.

    This models the cryptographic operations and byte layout
    of the TLS 1.3 supported group.

    It is NOT a complete TLS implementation.
    """

    MLKEM_ALGORITHM = "ML-KEM-768"

    MLKEM_PUBLIC_KEY_BYTES = 1184
    MLKEM_CIPHERTEXT_BYTES = 1088
    X25519_PUBLIC_KEY_BYTES = 32

    CLIENT_SHARE_BYTES = (
        MLKEM_PUBLIC_KEY_BYTES
        + X25519_PUBLIC_KEY_BYTES
    )

    SERVER_SHARE_BYTES = (
        MLKEM_CIPHERTEXT_BYTES
        + X25519_PUBLIC_KEY_BYTES
    )

    @staticmethod
    def combine_secrets(
        mlkem_secret: bytes,
        x25519_secret: bytes,
    ) -> bytes:
        """
        RFC 10024 X25519MLKEM768 shared secret:

            ML-KEM shared secret || X25519 shared secret

        32 bytes + 32 bytes = 64 bytes.
        """

        return mlkem_secret + x25519_secret

    def establish(self):

        # ====================================================
        # CLIENT — X25519
        # ====================================================

        client_x_private = (
            x25519.X25519PrivateKey.generate()
        )

        client_x_public = (
            client_x_private.public_key()
        )

        # ====================================================
        # SERVER — X25519
        # ====================================================

        server_x_private = (
            x25519.X25519PrivateKey.generate()
        )

        server_x_public = (
            server_x_private.public_key()
        )

        # Both sides calculate X25519 shared secret.

        client_x_secret = (
            client_x_private.exchange(
                server_x_public
            )
        )

        server_x_secret = (
            server_x_private.exchange(
                client_x_public
            )
        )

        assert (
            client_x_secret
            == server_x_secret
        )

        # ====================================================
        # CLIENT — ML-KEM-768 KEY GENERATION
        # ====================================================

        with oqs.KeyEncapsulation(
            self.MLKEM_ALGORITHM
        ) as client_kem:

            client_mlkem_public = (
                client_kem.generate_keypair()
            )

            # ================================================
            # SERVER — ML-KEM ENCAPSULATION
            # ================================================

            with oqs.KeyEncapsulation(
                self.MLKEM_ALGORITHM
            ) as server_kem:

                (
                    ciphertext,
                    server_mlkem_secret,
                ) = server_kem.encap_secret(
                    client_mlkem_public
                )

            # ================================================
            # CLIENT — ML-KEM DECAPSULATION
            # ================================================

            client_mlkem_secret = (
                client_kem.decap_secret(
                    ciphertext
                )
            )

        assert (
            client_mlkem_secret
            == server_mlkem_secret
        )

        # ====================================================
        # RFC 10024 HYBRID SHARED SECRET
        # ====================================================

        client_hybrid_secret = (
            self.combine_secrets(
                client_mlkem_secret,
                client_x_secret,
            )
        )

        server_hybrid_secret = (
            self.combine_secrets(
                server_mlkem_secret,
                server_x_secret,
            )
        )

        assert (
            client_hybrid_secret
            == server_hybrid_secret
        )

        return {
            # Canonical names
            "client_secret":
                client_hybrid_secret,

            "server_secret":
                server_hybrid_secret,

            "x25519_secret":
                client_x_secret,

            "mlkem_secret":
                client_mlkem_secret,

            # Sizes
            "mlkem_public_key_bytes":
                len(client_mlkem_public),

            "mlkem_ciphertext_bytes":
                len(ciphertext),

            "x25519_public_key_bytes":
                self.X25519_PUBLIC_KEY_BYTES,

            "client_share_bytes":
                len(client_mlkem_public)
                + self.X25519_PUBLIC_KEY_BYTES,

            "server_share_bytes":
                len(ciphertext)
                + self.X25519_PUBLIC_KEY_BYTES,

            "hybrid_secret_bytes":
                len(client_hybrid_secret),

            # Backwards-compatible aliases so older
            # benchmark code does not immediately break.
            "alice_secret":
                client_hybrid_secret,

            "bob_secret":
                server_hybrid_secret,
        }