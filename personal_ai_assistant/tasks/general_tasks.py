from personal_ai_assistant.celery_app import app
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.updater.update_manager import UpdateManager
from personal_ai_assistant.utils.backup_manager import BackupManager
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@app.task
def update_task_statuses():
    db_manager = DatabaseManager(settings.database_url)
    tasks = db_manager.get_all_tasks()
    for task in tasks:
        if task.status == TaskStatus.PENDING.value and task.start_time <= datetime.now():
            db_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS.value)
        elif task.status == TaskStatus.IN_PROGRESS.value and task.end_time <= datetime.now():
            db_manager.update_task_status(task.id, TaskStatus.COMPLETED.value)


@app.task
def generate_daily_summary():
    db_manager = DatabaseManager(settings.database_url)
    text_processor = TextProcessor()
    today = datetime.now().date()
    completed_tasks = db_manager.get_completed_tasks(today)
    task_descriptions = [task.description for task in completed_tasks]
    summary = text_processor.summarize_text("\n".join(task_descriptions))
    db_manager.store_daily_summary(today, summary)


@app.task
def check_for_updates():
    update_manager = UpdateManager()
    if update_manager.check_for_updates():
        update_manager.apply_updates()


@app.task
def create_periodic_backup():
    backup_manager = BackupManager()
    backup_manager.create_backup()
