from cryptography.fernet import Fernet
import base64
import bcrypt
from typing import Optional
import secrets


class EncryptionManager:
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key is None:
            encryption_key = secrets.token_urlsafe(32)
        self.key = self._get_or_create_key(encryption_key)
        self.fernet = Fernet(self.key)

    def _get_or_create_key(self, encryption_key: str) -> bytes:
        # Ensure the key is exactly 32 bytes
        key_bytes = base64.urlsafe_b64decode(encryption_key + '=' * (4 - len(encryption_key) % 4))
        return base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'\0'))

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
