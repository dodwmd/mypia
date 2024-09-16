from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from personal_ai_assistant.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    notes = relationship("Note", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    emails = relationship("Email", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)

    # Add any additional methods or properties here
