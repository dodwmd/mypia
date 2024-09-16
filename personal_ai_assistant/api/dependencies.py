from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache

from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import TaskManager
from personal_ai_assistant.web.scraper import WebScraper
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.updater.update_manager import UpdateManager
from personal_ai_assistant.utils.backup_manager import BackupManager
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.sync.sync_manager import SyncManager
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.db_manager import SessionLocal, DatabaseManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@lru_cache()
def get_db_manager():
    return DatabaseManager(settings.database_url)

@lru_cache()
def get_encryption_manager():
    return EncryptionManager(settings.encryption_key)

@lru_cache()
def get_auth_manager(
    db_manager: DatabaseManager = Depends(get_db_manager),
    encryption_manager: EncryptionManager = Depends(get_encryption_manager)
):
    return AuthManager(db_manager, encryption_manager)

@lru_cache()
def get_text_processor():
    return TextProcessor()

@lru_cache()
def get_email_client():
    return EmailClient(settings.EMAIL_IMAP_SERVER, settings.EMAIL_SMTP_SERVER, settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)

@lru_cache()
def get_caldav_client():
    return CalDAVClient(settings.CALDAV_URL, settings.CALDAV_USERNAME, settings.CALDAV_PASSWORD)

@lru_cache()
def get_task_manager():
    return TaskManager()

@lru_cache()
def get_web_scraper():
    return WebScraper()

@lru_cache()
def get_github_client():
    return GitHubClient(settings.GITHUB_TOKEN)

@lru_cache()
def get_chroma_db():
    return ChromaDBManager(settings.chroma_db_path)

@lru_cache()
def get_update_manager():
    return UpdateManager()

@lru_cache()
def get_backup_manager():
    return BackupManager()

@lru_cache()
def get_sync_manager():
    return SyncManager()

@lru_cache()
def get_llm():
    return LlamaCppInterface(settings.LLM_MODEL_PATH)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
