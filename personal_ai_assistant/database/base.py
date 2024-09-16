from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here to ensure they are registered with the Base
from personal_ai_assistant.models.user import User
from personal_ai_assistant.models.note import Note
from personal_ai_assistant.models.calendar_event import CalendarEvent
from personal_ai_assistant.models.email import Email
from personal_ai_assistant.models.task import Task
from personal_ai_assistant.models.user_preference import UserPreference
