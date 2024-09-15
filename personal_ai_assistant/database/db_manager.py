from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base, User, UserPreference
from personal_ai_assistant.utils.encryption import EncryptionManager
from typing import List, Dict, Any, Optional
from personal_ai_assistant.config import settings
from datetime import datetime


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(settings.database_url)
        self.Session = sessionmaker(bind=self.engine)

    def init_db():
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(engine)

    def create_user(self, username: str, email: str, password: str) -> int:
        with self.Session() as session:
            hashed_password = EncryptionManager.hash_password(password)
            user = User(username=username, email=email, password_hash=hashed_password)
            session.add(user)
            session.commit()
            return user.id

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self.Session() as session:
            return session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self.Session() as session:
            return session.query(User).filter(User.id == user_id).first()

    def update_user_last_login(self, user_id: int):
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                session.commit()

    # ... (other methods remain similar, but add user_id parameter where necessary)

    def get_user_preferences(self, user_id: int) -> List[Dict[str, Any]]:
        with self.Session() as session:
            prefs = session.query(UserPreference).filter(UserPreference.user_id == user_id).all()
            return [{"key": pref.key, "value": pref.value} for pref in prefs]

    def set_user_preference(self, user_id: int, key: str, value: str):
        with self.Session() as session:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.key == key
            ).first()
            if pref:
                pref.value = value
            else:
                pref = UserPreference(user_id=user_id, key=key, value=value)
                session.add(pref)
            session.commit()

    # ... (implement other user-specific methods)
