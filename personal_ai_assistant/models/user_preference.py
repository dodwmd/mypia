from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from personal_ai_assistant.database.base import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String, default="light")
    language = Column(String, default="en")

    user = relationship("User", back_populates="preferences")
