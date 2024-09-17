from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import logging
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


class CalendarEvent(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None


def get_caldav_client():
    return CalDAVClient(settings.CALDAV_URL, settings.CALDAV_USERNAME, settings.CALDAV_PASSWORD)


@router.get("/events")
async def get_calendar_events(
    token: str = Depends(oauth2_scheme),
    caldav_client: CalDAVClient = Depends(get_caldav_client)
):
    try:
        events = await caldav_client.get_events()
        logger.info(f"Successfully fetched {len(events)} calendar events")
        return {"events": events}
    except Exception as e:
        logger.error(f"Error fetching calendar events: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching calendar events")


@router.post("/events")
async def create_calendar_event(
    event: CalendarEvent,
    token: str = Depends(oauth2_scheme),
    caldav_client: CalDAVClient = Depends(get_caldav_client)
):
    try:
        created_event = await caldav_client.create_event(event.title, event.start_time, event.end_time, event.description)
        logger.info(f"Successfully created calendar event: {event.title}")
        return {"message": "Event created successfully", "event": created_event}
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating calendar event")
