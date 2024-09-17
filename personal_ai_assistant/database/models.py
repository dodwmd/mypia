# This file is used to ensure all models are imported and available for database operations
from personal_ai_assistant.models.user import User
from personal_ai_assistant.models.task import Task
from personal_ai_assistant.models.calendar_event import CalendarEvent
from personal_ai_assistant.models.user_preference import UserPreference
from personal_ai_assistant.models.note import Note
from personal_ai_assistant.models.contact import Contact
from personal_ai_assistant.models.email import Email

__all__ = ['User', 'Task', 'CalendarEvent', 'UserPreference', 'Note', 'Contact', 'Email']
