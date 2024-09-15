import caldav
from typing import List, Dict, Any
import asyncio
from personal_ai_assistant.utils.cache import cache


class CalDAVClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.client = None

    async def connect(self):
        self.client = caldav.DAVClient(url=self.url, username=self.username, password=self.password)
        self.principal = self.client.principal()

    @cache(expire=3600)  # Cache for 1 hour
    async def get_calendars(self) -> List[Dict[str, Any]]:
        if not self.client:
            await self.connect()
        calendars = await asyncio.to_thread(self.principal.calendars)
        return [{'name': cal.name, 'url': cal.url} for cal in calendars]

    # ... (rest of the code remains unchanged)
