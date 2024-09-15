from personal_ai_assistant.celery_app import app
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
from personal_ai_assistant.utils.backup_manager import BackupManager
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@app.task
def create_periodic_backup():
    db_manager = DatabaseManager(settings.database_url)
    backup_manager = BackupManager(db_manager)
    try:
        backup_path = backup_manager.create_backup()
        db_manager.log_backup(backup_path, TaskStatus.COMPLETED.value)
        return {"status": "success", "message": f"Backup created at {backup_path}"}
    except Exception as e:
        db_manager.log_backup(None, TaskStatus.FAILED.value, str(e))
        return {"status": "error", "message": f"Backup creation failed: {str(e)}"}


@app.task
def cleanup_old_backups():
    db_manager = DatabaseManager(settings.database_url)
    backup_manager = BackupManager(db_manager)
    deleted_backups = backup_manager.cleanup_old_backups()
    return {"status": "success", "message": f"Deleted {len(deleted_backups)} old backups"}


@app.task
def verify_backups():
    db_manager = DatabaseManager(settings.database_url)
    backup_manager = BackupManager(db_manager)
    verification_results = backup_manager.verify_backups()
    return {"status": "success", "results": verification_results}
