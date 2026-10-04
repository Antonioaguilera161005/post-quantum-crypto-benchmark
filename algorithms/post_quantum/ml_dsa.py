import oqs


class MLDSA:

    SUPPORTED = {
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    }

    def __init__(
        self,
        algorithm="ML-DSA-65",
    ):

        if algorithm not in self.SUPPORTED:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}"
            )

        self.algorithm = algorithm

    def keygen(self):

        signer = oqs.Signature(
            self.algorithm
        )

        public_key = (
            signer.generate_keypair()
        )

        return signer, public_key

    def sign(
        self,
        signer,
        message: bytes,
    ):

        return signer.sign(message)

    def verify(
        self,
        public_key,
        signature,
        message,
    ):

        with oqs.Signature(
            self.algorithm
        ) as verifier:

            return verifier.verify(
                message,
                signature,
                public_key,
            )   