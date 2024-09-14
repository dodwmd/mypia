from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.config import settings
import jwt
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def authenticate_user(self, username: str, password: str) -> bool:
        user = self.db_manager.get_user_by_username(username)
        if user and EncryptionManager.verify_password(user.password_hash, password):
            self.db_manager.update_user_last_login(user.id)
            return True
        return False

    def create_access_token(self, username: str) -> str:
        user = self.db_manager.get_user_by_username(username)
        if not user:
            raise ValueError("User not found")
        
        payload = {
            "sub": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
