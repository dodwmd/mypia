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
