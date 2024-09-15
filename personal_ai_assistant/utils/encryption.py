from cryptography.fernet import Fernet
from personal_ai_assistant.config import settings
import base64


class EncryptionManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)

    def _get_or_create_key(self):
        if settings.encryption_key:
            return base64.urlsafe_b64encode(settings.encryption_key.encode())
        else:
            return Fernet.generate_key()

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()
