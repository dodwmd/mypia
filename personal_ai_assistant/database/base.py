from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.base_class import Base

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Remove the import of models here
