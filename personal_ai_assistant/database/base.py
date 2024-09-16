from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from personal_ai_assistant.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models here to ensure they are registered with the Base
from personal_ai_assistant.models.user import User
from personal_ai_assistant.models.note import Note
from personal_ai_assistant.models.calendar_event import CalendarEvent
from personal_ai_assistant.models.email import Email
from personal_ai_assistant.models.task import Task
from personal_ai_assistant.models.user_preference import UserPreference
