from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from personal_ai_assistant.database.db_manager import Base


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
