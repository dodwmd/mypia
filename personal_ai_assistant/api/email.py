from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.api.dependencies import get_email_client
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


class EmailData(BaseModel):
    to: str
    subject: str
    body: str


@router.post("/send")
async def send_email(
    email: EmailData,
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
