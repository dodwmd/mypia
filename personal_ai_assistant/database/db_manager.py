from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from personal_ai_assistant.database.base import Base
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from personal_ai_assistant.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_user_by_username(self, username: str) -> Optional['User']:
        from personal_ai_assistant.models.user import User
        with self.SessionLocal() as session:
            return session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional['User']:
        from personal_ai_assistant.models.user import User
        with self.SessionLocal() as session:
            return session.query(User).filter(User.id == user_id).first()

    def create_contact_submission(self, name: str, email: str, message: str):
        from personal_ai_assistant.models.contact import ContactSubmission
        with self.SessionLocal() as session:
            new_submission = ContactSubmission(name=name, email=email, message=message)
            session.add(new_submission)
            session.commit()
            session.refresh(new_submission)
            return new_submission

    def get_contact_submissions(self, skip: int = 0, limit: int = 100) -> List['ContactSubmission']:
        from personal_ai_assistant.models.contact import ContactSubmission
        with self.SessionLocal() as session:
            return session.query(ContactSubmission).offset(skip).limit(limit).all()

    # ... (other methods)
