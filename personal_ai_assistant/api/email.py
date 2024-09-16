from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.config import settings
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

class Email(BaseModel):
    to: str
    subject: str
    body: str

def get_email_client():
    return EmailClient(settings.EMAIL_IMAP_SERVER, settings.EMAIL_SMTP_SERVER, settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)

@router.get("/emails")
async def get_emails(
    limit: int = 10,
    token: str = Depends(oauth2_scheme),
    email_client: EmailClient = Depends(get_email_client)
):
    try:
        emails = await email_client.fetch_emails(limit=limit)
        logger.info(f"Successfully fetched {len(emails)} emails")
        return {"emails": emails}
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching emails")

@router.post("/emails/send")
async def send_email(
    email: Email,
    token: str = Depends(oauth2_scheme),
    email_client: EmailClient = Depends(get_email_client)
):
    try:
        await email_client.send_email(email.to, email.subject, email.body)
        logger.info(f"Successfully sent email to {email.to}")
        return {"message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending email")
