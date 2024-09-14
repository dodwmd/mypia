from personal_ai_assistant.celery_app import app
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.config import settings
import asyncio

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
