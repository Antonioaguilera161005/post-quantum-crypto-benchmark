import oqs


class MLKEM:
    """
    Wrapper for ML-KEM using liboqs.

    Supported parameter sets:
        ML-KEM-512
        ML-KEM-768
        ML-KEM-1024
    """

    SUPPORTED = {
        "ML-KEM-512",
        "ML-KEM-768",
        "ML-KEM-1024",
    }

    def __init__(self, algorithm: str = "ML-KEM-768"):
        if algorithm not in self.SUPPORTED:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Choose from {sorted(self.SUPPORTED)}"
            )

        self.algorithm = algorithm

    def keygen(self):
        kem = oqs.KeyEncapsulation(self.algorithm)
        public_key = kem.generate_keypair()

        return kem, public_key

    def encapsulate(self, public_key):
        with oqs.KeyEncapsulation(self.algorithm) as sender:
            ciphertext, shared_secret = sender.encap_secret(public_key)

        return ciphertext, shared_secret

    def decapsulate(self, kem, ciphertext):
        shared_secret = kem.decap_secret(ciphertext)

        return shared_secret