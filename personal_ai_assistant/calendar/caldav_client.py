import aiohttp
import asyncio
from caldav import DAVClient
from caldav.elements import dav, cdav
from datetime import datetime, timedelta
from typing import List, Dict, Any
from personal_ai_assistant.utils.cache import cache

class CalDAVClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.client = None

    async def connect(self):
        self.client = DAVClient(url=self.url, username=self.username, password=self.password)
        self.principal = self.client.principal()

    @cache(expire=3600)  # Cache for 1 hour
    async def get_calendars(self) -> List[Dict[str, Any]]:
        if not self.client:
            await self.connect()
        calendars = await asyncio.to_thread(self.principal.calendars)
        return [{'name': cal.name, 'url': cal.url} for cal in calendars]

    @cache(expire=300)  # Cache for 5 minutes
    async def get_events(self, calendar_name: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        if not self.client:
            await self.connect()
        calendar = await asyncio.to_thread(self._get_calendar_by_name, calendar_name)
        events = await asyncio.to_thread(calendar.date_search, start, end)
        return [await asyncio.to_thread(self._event_to_dict, event) for event in events]

    # ... (other methods remain similar, but use async/await and asyncio.to_thread where appropriate)
