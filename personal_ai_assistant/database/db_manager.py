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
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self.SessionLocal() as session:
            return session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self.SessionLocal() as session:
            return session.query(User).filter(User.id == user_id).first()

    def create_contact_submission(self, name: str, email: str, message: str) -> ContactSubmission:
        with self.SessionLocal() as session:
            new_submission = ContactSubmission(name=name, email=email, message=message)
            session.add(new_submission)
            session.commit()
            session.refresh(new_submission)
            return new_submission

    def get_contact_submissions(self, skip: int = 0, limit: int = 100) -> List[ContactSubmission]:
        with self.SessionLocal() as session:
            return session.query(ContactSubmission).offset(skip).limit(limit).all()

    def create_user(self, username: str, email: str, password_hash: str) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        with self.SessionLocal() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def delete_user(self, user_id: int):
        with self.SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()

    def create_note(self, user_id: int, title: str, content: str) -> Note:
        with self.SessionLocal() as session:
            note = Note(user_id=user_id, title=title, content=content)
            session.add(note)
            session.commit()
            session.refresh(note)
        return note

    def get_notes_by_user(self, user_id: int) -> List[Note]:
        with self.SessionLocal() as session:
            return session.query(Note).filter(Note.user_id == user_id).all()

    def create_calendar_event(self, user_id: int, title: str, description: str, start_time: datetime, end_time: datetime) -> CalendarEvent:
        with self.SessionLocal() as session:
            event = CalendarEvent(user_id=user_id, title=title, description=description, start_time=start_time, end_time=end_time)
            session.add(event)
            session.commit()
            session.refresh(event)
        return event

    def get_calendar_events_by_user(self, user_id: int) -> List[CalendarEvent]:
        with self.SessionLocal() as session:
            return session.query(CalendarEvent).filter(CalendarEvent.user_id == user_id).all()

    def create_email(self, user_id: int, subject: str, body: str, sender: str, recipient: str, timestamp: datetime) -> Email:
        with self.SessionLocal() as session:
            email = Email(user_id=user_id, subject=subject, body=body, sender=sender, recipient=recipient, timestamp=timestamp)
            session.add(email)
            session.commit()
            session.refresh(email)
        return email

    def get_emails_by_user(self, user_id: int) -> List[Email]:
        with self.SessionLocal() as session:
            return session.query(Email).filter(Email.user_id == user_id).all()

    def create_task(self, user_id: int, title: str, description: str, due_date: datetime) -> Task:
        with self.SessionLocal() as session:
            task = Task(user_id=user_id, title=title, description=description, due_date=due_date)
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        with self.SessionLocal() as session:
            return session.query(Task).filter(Task.user_id == user_id).all()

    def create_user_preference(self, user_id: int, theme: str = "light", language: str = "en") -> UserPreference:
        with self.SessionLocal() as session:
            preference = UserPreference(user_id=user_id, theme=theme, language=language)
            session.add(preference)
            session.commit()
            session.refresh(preference)
        return preference

    def get_user_preference(self, user_id: int) -> UserPreference:
        with self.SessionLocal() as session:
            return session.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    # ... (other methods)
