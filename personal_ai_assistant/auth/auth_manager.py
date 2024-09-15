from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.utils.exceptions import AuthenticationError
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, List


class AuthManager:
    def __init__(self, db_manager: DatabaseManager, secret_key: str):
        self.db_manager = db_manager
        self.encryption_manager = EncryptionManager()
        self.secret_key = secret_key

    def authenticate_user(self, username: str, password: str) -> bool:
        user = self.db_manager.get_user_by_username(username)
        if user and self.encryption_manager.verify_password(password, user.password_hash):
            self.db_manager.update_user_last_login(user.id)
            return True
        return False

    def create_user(self, username: str, email: str, password: str) -> int:
        hashed_password = self.encryption_manager.hash_password(password)
        return self.db_manager.create_user(username, email, hashed_password)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = self.db_manager.get_user_by_id(user_id)
        if user and self.encryption_manager.verify_password(old_password, user.password_hash):
            new_hashed_password = self.encryption_manager.hash_password(new_password)
            self.db_manager.update_user_password(user_id, new_hashed_password)
            return True
        return False

    def generate_token(self, user_id: int) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        user = self.db_manager.get_user_by_id(user_id)
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at,
                'last_login': user.last_login
            }
        return None

    def delete_user(self, user_id: int) -> bool:
        return self.db_manager.delete_user(user_id)

    def update_user_email(self, user_id: int, new_email: str) -> bool:
        return self.db_manager.update_user_email(user_id, new_email)

    def is_admin(self, user_id: int) -> bool:
        user = self.db_manager.get_user_by_id(user_id)
        return user.is_admin if user else False

    def set_user_role(self, user_id: int, is_admin: bool) -> bool:
        return self.db_manager.set_user_role(user_id, is_admin)

    def get_all_users(self) -> List[Dict[str, Any]]:
        users = self.db_manager.get_all_users()
        return [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at,
                'last_login': user.last_login,
                'is_admin': user.is_admin
            }
            for user in users
        ]
