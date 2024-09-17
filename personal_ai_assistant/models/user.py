from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from personal_ai_assistant.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    preferences = relationship("UserPreference", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    notes = relationship("Note", back_populates="user")
    emails = relationship("Email", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
