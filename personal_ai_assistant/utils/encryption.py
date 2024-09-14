from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionManager:
    def __init__(self, key):
        self.fernet = Fernet(key)

    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        key = EncryptionManager.generate_key(password, salt)
        return base64.b64encode(salt + key).decode()

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        decoded = base64.b64decode(stored_password.encode())
        salt, stored_key = decoded[:16], decoded[16:]
        key = EncryptionManager.generate_key(provided_password, salt)
        return key == stored_key
