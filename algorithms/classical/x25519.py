from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)


class X25519:
    """
    Wrapper for X25519 key exchange.
    """

    def keygen(self):
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()

        return private_key, public_key

    def exchange(self, private_key, peer_public_key):
        return private_key.exchange(peer_public_key)

    @staticmethod
    def public_key_bytes(public_key):
        return public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )

    @staticmethod
    def private_key_bytes(private_key):
        return private_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=NoEncryption(),
        )