import rsa
from rsa.key import AbstractKey, PrivateKey, PublicKey


class RSA:
    @classmethod
    def generate_keys(cls, size: int = 512) -> tuple:
        return rsa.newkeys(size)

    @classmethod
    def export_key_pkcs1(cls, public_key: PublicKey, format: str = "PEM") -> bytes:
        return PublicKey.save_pkcs1(public_key, format=format)

    @classmethod
    def load_key_pkcs1(cls, public_key_pem: bytes) -> AbstractKey:
        return PublicKey.load_pkcs1(public_key_pem)

    @classmethod
    def sign_message(cls, message: bytes, private_key: PrivateKey, algorithm: str = "SHA-1") -> bytes:
        return rsa.sign(message, private_key, algorithm)
