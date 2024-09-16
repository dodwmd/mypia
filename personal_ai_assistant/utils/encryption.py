from cryptography.fernet import Fernet
import base64
import bcrypt
from typing import Optional

class EncryptionManager:
    def __init__(self, encryption_key: Optional[str] = None):
        self.key = self._get_or_create_key(encryption_key)
        self.fernet = Fernet(self.key)

    def _get_or_create_key(self, encryption_key: Optional[str]):
        if encryption_key is None:
            return Fernet.generate_key()
        elif isinstance(encryption_key, str):
            return base64.urlsafe_b64encode(encryption_key.encode())
        elif isinstance(encryption_key, bytes):
            return base64.urlsafe_b64encode(encryption_key)
        else:
            raise ValueError("Invalid encryption key type")

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
