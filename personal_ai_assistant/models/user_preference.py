from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from personal_ai_assistant.database.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    value = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="preferences")
