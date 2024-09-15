from personal_ai_assistant.celery_app import app
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
import asyncio
from datetime import datetime, timedelta


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
            db_manager.log_email(
                user_id=1,  # Assuming a default user ID of 1
                subject=email['subject'],
                sender=email['from'],
                recipient=settings.email_username,
                is_sent=0  # 0 for received email
            )

    asyncio.run(process_emails())


@app.task
def clean_up_old_emails():
    chroma_db = ChromaDBManager(settings.chroma_db_path)
    db_manager = DatabaseManager(settings.database_url)
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    chroma_db.delete_documents("emails", filter={"date": {"$lt": thirty_days_ago}})
    db_manager.delete_old_email_logs(days=30)
