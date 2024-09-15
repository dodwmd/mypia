import os
import shutil
import datetime
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.chroma_db = ChromaDBManager(settings.chroma_db_path)
        self.backup_dir = settings.backup_dir

    def create_backup(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)

        # Backup SQLite database
        shutil.copy2(settings.database_url.replace("sqlite:///", ""), os.path.join(backup_path, "database.sqlite"))

        # Backup ChromaDB
        chroma_backup_path = os.path.join(backup_path, "chroma_db")
        shutil.copytree(settings.chroma_db_path, chroma_backup_path)

        logger.info(f"Backup created at {backup_path}")
        return backup_path

    def restore_backup(self, backup_path):
        # Restore SQLite database
        shutil.copy2(os.path.join(backup_path, "database.sqlite"), settings.database_url.replace("sqlite:///", ""))

        # Restore ChromaDB
        chroma_backup_path = os.path.join(backup_path, "chroma_db")
        shutil.rmtree(settings.chroma_db_path)
        shutil.copytree(chroma_backup_path, settings.chroma_db_path)

        logger.info(f"Backup restored from {backup_path}")

    def list_backups(self):
        return [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d)) and d.startswith("backup_")]

    def delete_backup(self, backup_name):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            logger.info(f"Backup {backup_name} deleted")
        else:
            logger.warning(f"Backup {backup_name} not found")
