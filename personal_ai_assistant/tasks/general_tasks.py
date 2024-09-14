from personal_ai_assistant.celery_app import app
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.config import settings
from personal_ai_assistant.updater.update_manager import run_update_check
from personal_ai_assistant.utils.backup_manager import BackupManager
import asyncio
import datetime
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@app.task
def update_task_statuses():
    db_manager = DatabaseManager(settings.database_url)
    # Update overdue tasks to 'cancelled'
    db_manager.update_overdue_tasks()

@app.task
def generate_daily_summary():
    db_manager = DatabaseManager(settings.database_url)
    chroma_db = ChromaDBManager(settings.chroma_db_path)

    # Get today's emails
    today = datetime.utcnow().date()
    today_emails = chroma_db.query("emails", filter={"date": {"$gte": today.isoformat()}})

    # Get today's calendar events
    today_events = chroma_db.query("calendar_events", filter={"start": {"$gte": today.isoformat(), "$lt": (today + timedelta(days=1)).isoformat()}})

    # Get pending tasks
    pending_tasks = db_manager.get_tasks_by_status(TaskStatus.PENDING)

    # Generate summary
    summary = f"Daily Summary for {today}:\n"
    summary += f"New Emails: {len(today_emails)}\n"
    summary += f"Today's Events: {len(today_events)}\n"
    summary += f"Pending Tasks: {len(pending_tasks)}\n"

    # Store the summary in the database or send it via email
    db_manager.store_daily_summary(summary)

@app.task
def check_for_updates():
    asyncio.run(run_update_check())

@app.task
def create_periodic_backup():
    db_manager = DatabaseManager(settings.database_url)
    chroma_db = ChromaDBManager(settings.chroma_db_path)
    backup_manager = BackupManager(db_manager, chroma_db)
    backup_path = backup_manager.create_backup()
    logger.info(f"Periodic backup created: {backup_path}")
