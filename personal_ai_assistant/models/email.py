from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from personal_ai_assistant.database.base import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    body = Column(String)
    sender = Column(String)
    recipient = Column(String)
    timestamp = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="emails")
