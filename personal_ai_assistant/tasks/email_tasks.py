from celery import shared_task
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.database.db_manager import db_manager
from personal_ai_assistant.models.email import Email
from datetime import datetime, timedelta


@shared_task
def check_and_process_new_emails():
    email_client = EmailClient()
    chroma_db = ChromaDBManager()
    
    with db_manager.SessionLocal() as db:
        new_emails = email_client.fetch_new_emails()
        for email in new_emails:
            # Process and store email in the database
            db_email = Email(
                subject=email['subject'],
                sender=email['from'],
                recipient=email['to'],
                body=email['body'],
                timestamp=email['date']
            )
            db.add(db_email)
            db.commit()
            db.refresh(db_email)

            # Add email to vector database for semantic search
            chroma_db.add_documents(
                collection_name="emails",
                documents=[email['body']],
                metadatas=[{"subject": email['subject'], "date": str(email['date'])}],
                ids=[str(db_email.id)]
            )


@shared_task
def clean_up_old_emails():
    chroma_db = ChromaDBManager()

    with db_manager.SessionLocal() as db:
        # Define the cutoff date (e.g., emails older than 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Query for old emails
        old_emails = db.query(Email).filter(Email.timestamp < cutoff_date).all()

        for email in old_emails:
            # Remove from the database
            db.delete(email)

            # Remove from the vector database
            chroma_db.delete_documents(
                collection_name="emails",
                filter={"id": str(email.id)}
            )

        db.commit()
