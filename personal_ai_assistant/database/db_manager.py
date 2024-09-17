from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List
from personal_ai_assistant.database.base import Base
from personal_ai_assistant.config import settings
from personal_ai_assistant.models.user import User
from personal_ai_assistant.models.contact import ContactSubmission
from personal_ai_assistant.models.note import Note
from personal_ai_assistant.models.calendar_event import CalendarEvent
from personal_ai_assistant.models.email import Email
from personal_ai_assistant.models.task import Task
from personal_ai_assistant.models.user_preference import UserPreference
from datetime import datetime

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


db_manager = DatabaseManager(settings.database_url)
get_db = db_manager.get_db()

# ... (other methods)

