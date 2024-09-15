from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime)
    last_login = Column(DateTime)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    due_date = Column(DateTime)

    user = relationship("User", back_populates="tasks")


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


class CalendarEvent(Base):
    __tablename__ = 'calendar_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String(255))

    user = relationship("User", back_populates="calendar_events")


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
