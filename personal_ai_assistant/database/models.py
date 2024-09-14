from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)

    tasks = relationship('Task', back_populates='user')
    preferences = relationship('UserPreference', back_populates='user')
    email_logs = relationship('EmailLog', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='tasks')

class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(50), nullable=False)
    value = Column(String(255))

    user = relationship('User', back_populates='preferences')

class EmailLog(Base):
    __tablename__ = 'email_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(255))
    sender = Column(String(255))
    recipient = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_sent = Column(Integer, default=0)  # 0 for received, 1 for sent

    user = relationship('User', back_populates='email_logs')

class OfflineCache(Base):
    __tablename__ = 'offline_cache'

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OfflineAction(Base):
    __tablename__ = 'offline_actions'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    synced = Column(Boolean, default=False)

class SyncInfo(Base):
    __tablename__ = 'sync_info'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), unique=True, nullable=False)
    last_synced = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(engine):
    Base.metadata.create_all(engine)
