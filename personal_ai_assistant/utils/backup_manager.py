import os
import shutil
import json
import zipfile
from datetime import datetime
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.utils.logging_config import setup_logging

logger = setup_logging()

class BackupManager:
    def __init__(self, db_manager: DatabaseManager, chroma_db: ChromaDBManager):
        self.db_manager = db_manager
        self.chroma_db = chroma_db
        self.backup_dir = settings.backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)

        # Backup SQLite database
        shutil.copy2(settings.database_url.replace("sqlite:///", ""), os.path.join(backup_path, "mypia.db"))

        # Backup ChromaDB
        chroma_backup_path = os.path.join(backup_path, "chroma_db")
        shutil.copytree(settings.chroma_db_path, chroma_backup_path)

        # Backup user preferences
        user_prefs = self.db_manager.get_all_user_preferences()
        with open(os.path.join(backup_path, "user_preferences.json"), "w") as f:
            json.dump(user_prefs, f)

        # Create a zip file of the backup
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(backup_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), backup_path))

        # Remove the unzipped backup directory
        shutil.rmtree(backup_path)

        logger.info(f"Backup created: {zip_path}")
        return zip_path

    def restore_backup(self, backup_path: str):
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Extract the backup
        extract_path = os.path.join(self.backup_dir, "temp_restore")
        with zipfile.ZipFile(backup_path, "r") as zipf:
            zipf.extractall(extract_path)

        # Restore SQLite database
        shutil.copy2(os.path.join(extract_path, "mypia.db"), settings.database_url.replace("sqlite:///", ""))

        # Restore ChromaDB
        shutil.rmtree(settings.chroma_db_path)
        shutil.copytree(os.path.join(extract_path, "chroma_db"), settings.chroma_db_path)

        # Restore user preferences
        with open(os.path.join(extract_path, "user_preferences.json"), "r") as f:
            user_prefs = json.load(f)
        self.db_manager.restore_user_preferences(user_prefs)

        # Remove the temporary extraction directory
        shutil.rmtree(extract_path)

        logger.info(f"Backup restored from: {backup_path}")

    def list_backups(self):
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith(".zip")]
        return sorted(backups, reverse=True)

    def delete_backup(self, backup_name: str):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            logger.info(f"Backup deleted: {backup_path}")
        else:
            logger.warning(f"Backup not found: {backup_path}")
