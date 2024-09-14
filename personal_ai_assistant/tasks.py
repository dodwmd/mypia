from .celery_app import app
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
import asyncio
import datetime
import timedelta
from personal_ai_assistant.updater.update_manager import run_update_check
from personal_ai_assistant.utils.backup_manager import BackupManager

@app.task
def check_and_process_new_emails():
    email_client = EmailClient(settings.email_host, settings.smtp_host, settings.email_username, settings.email_password)
    chroma_db = ChromaDBManager(settings.chroma_db_path)
    db_manager = DatabaseManager(settings.database_url)

    async def process_emails():
        last_uid = chroma_db.get_latest_document_id("emails")
        new_emails = await email_client.fetch_new_emails(last_uid=int(last_uid) if last_uid else 0)
        
        for email in new_emails:
            document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
            metadata = {
                'uid': email['uid'],
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'].isoformat()
            }
            chroma_db.add_documents("emails", [document], [metadata], [str(email['uid'])])
            
            # Log the email in the database
            db_manager.log_email(
                user_id=1,  # Assuming a default user ID of 1
                subject=email['subject'],
                sender=email['from'],
                recipient=settings.email_username,
                is_sent=0  # 0 for received email
            )

    asyncio.run(process_emails())

@app.task
def sync_calendar_events():
    caldav_client = CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password)
    chroma_db = ChromaDBManager(settings.chroma_db_path)

    async def sync_events():
        calendars = await caldav_client.get_calendars()
        for calendar in calendars:
            events = await caldav_client.get_events(calendar['name'], start=None, end=None)  # Fetch all events
            for event in events:
                document = f"Summary: {event['summary']}\nStart: {event['start']}\nEnd: {event['end']}\nDescription: {event['description']}"
                metadata = {
                    'id': event['id'],
                    'summary': event['summary'],
                    'start': event['start'].isoformat(),
                    'end': event['end'].isoformat() if event['end'] else None,
                }
                chroma_db.add_documents("calendar_events", [document], [metadata], [event['id']])

    asyncio.run(sync_events())

@app.task
def clean_up_old_data():
    chroma_db = ChromaDBManager(settings.chroma_db_path)
    db_manager = DatabaseManager(settings.database_url)

    # Delete emails older than 30 days from ChromaDB
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    chroma_db.delete_documents("emails", filter={"date": {"$lt": thirty_days_ago}})

    # Delete email logs older than 30 days from the database
    db_manager.delete_old_email_logs(days=30)

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

    # Generate summary (you can use your LLM here for a more sophisticated summary)
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
