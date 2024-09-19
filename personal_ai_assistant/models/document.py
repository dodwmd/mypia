from sqlalchemy import Column, Integer, String, ForeignKey
from personal_ai_assistant.database.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
