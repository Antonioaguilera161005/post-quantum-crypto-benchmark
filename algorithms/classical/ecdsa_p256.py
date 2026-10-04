from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)


class ECDSAP256:

    def keygen(self):
        private_key = ec.generate_private_key(
            ec.SECP256R1()
        )

        public_key = private_key.public_key()

        return private_key, public_key

    def sign(self, private_key, message: bytes):

        return private_key.sign(
            message,
            ec.ECDSA(hashes.SHA256())
        )

    def verify(
        self,
        public_key,
        signature,
        message,
    ):

        public_key.verify(
            signature,
            message,
            ec.ECDSA(hashes.SHA256())
        )

        return True

    @staticmethod
    def public_key_bytes(public_key):

        return public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint,
        )

    @staticmethod
    def private_key_bytes(private_key):

        return private_key.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )