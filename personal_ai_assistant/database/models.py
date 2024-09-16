from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from personal_ai_assistant.models.user import User
from personal_ai_assistant.models.task import Task
from personal_ai_assistant.models.email import Email
from personal_ai_assistant.models.calendar_event import CalendarEvent
from personal_ai_assistant.models.note import Note
from personal_ai_assistant.models.contact import ContactSubmission

Base = declarative_base()


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(String(50), nullable=False)
    value = Column(String(255))

    user = relationship("User", back_populates="preferences")


class EmailLog(Base):
    __tablename__ = 'email_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subject = Column(String(255))
    sender = Column(String(120))
    recipient = Column(String(120))
    timestamp = Column(DateTime)
    is_sent = Column(Boolean)

    user = relationship("User", back_populates="email_logs")


class LLMInteraction(Base):
    __tablename__ = 'llm_interactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    prompt = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime)

    user = relationship("User", back_populates="llm_interactions")


class Backup(Base):
    __tablename__ = 'backups'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    backup_path = Column(String(255))
    created_at = Column(DateTime)
    status = Column(String(20))

    user = relationship("User", back_populates="backups")


class Update(Base):
    __tablename__ = 'updates'

    id = Column(Integer, primary_key=True)
    version = Column(String(20))
    applied_at = Column(DateTime)
    status = Column(String(20))
