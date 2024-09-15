from personal_ai_assistant.celery_app import app
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
from datetime import datetime, timedelta


@app.task
def sync_calendar_events():
    caldav_client = CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password)
    db_manager = DatabaseManager(settings.database_url)

    # Fetch events from CalDAV server
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)  # Sync events for the next 30 days
    events = caldav_client.get_events(start_date, end_date)

    # Update local database with fetched events
    for event in events:
        db_manager.update_or_create_event(
            event_id=event['id'],
            title=event['summary'],
            start_time=event['start'],
            end_time=event['end'],
            description=event.get('description', ''),
            location=event.get('location', '')
        )

    # Remove events from local database that no longer exist on the CalDAV server
    db_manager.remove_non_existent_events([event['id'] for event in events], start_date, end_date)
