import caldav
from typing import List, Dict, Any
import asyncio
from functools import lru_cache
from datetime import datetime


class CalDAVClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.client = None

    async def connect(self):
        self.client = caldav.DAVClient(url=self.url, username=self.username, password=self.password)
        self.principal = self.client.principal()

    @lru_cache(maxsize=32)
    async def get_calendars(self) -> List[Dict[str, Any]]:
        if not self.client:
            await self.connect()
        calendars = await asyncio.to_thread(self.principal.calendars)
        return [{'name': cal.name, 'url': cal.url} for cal in calendars]

    async def get_events(self, calendar_name: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        if not self.client:
            await self.connect()
        calendars = await self.get_calendars()
        calendar = next((cal for cal in calendars if cal['name'] == calendar_name), None)
        if not calendar:
            raise ValueError(f"Calendar '{calendar_name}' not found")

        cal = self.client.calendar(url=calendar['url'])
        events = await asyncio.to_thread(cal.date_search, start, end)
        return [
            {
                'id': event.id,
                'summary': event.instance.vevent.summary.value,
                'start': event.instance.vevent.dtstart.value,
                'end': event.instance.vevent.dtend.value,
                'description': event.instance.vevent.description.value if hasattr(event.instance.vevent, 'description') else '',
                'location': event.instance.vevent.location.value if hasattr(event.instance.vevent, 'location') else ''
            }
            for event in events
        ]

    async def create_event(self, calendar_name: str, summary: str, start: datetime, end: datetime, description: str = '', location: str = '') -> Dict[str, Any]:
        if not self.client:
            await self.connect()
        calendars = await self.get_calendars()
        calendar = next((cal for cal in calendars if cal['name'] == calendar_name), None)
        if not calendar:
            raise ValueError(f"Calendar '{calendar_name}' not found")

        cal = self.client.calendar(url=calendar['url'])
        event = await asyncio.to_thread(
            cal.save_event,
            summary=summary,
            dtstart=start,
            dtend=end,
            description=description,
            location=location
        )
        return {
            'id': event.id,
            'summary': summary,
            'start': start,
            'end': end,
            'description': description,
            'location': location
        }

    async def update_event(self, calendar_name: str, event_id: str, summary: str, start: datetime, end: datetime, description: str = '', location: str = '') -> Dict[str, Any]:
        if not self.client:
            await self.connect()
        calendars = await self.get_calendars()
        calendar = next((cal for cal in calendars if cal['name'] == calendar_name), None)
        if not calendar:
            raise ValueError(f"Calendar '{calendar_name}' not found")

        cal = self.client.calendar(url=calendar['url'])
        event = await asyncio.to_thread(cal.event, event_id)
        await asyncio.to_thread(
            event.load,
            summary=summary,
            dtstart=start,
            dtend=end,
            description=description,
            location=location
        )
        await asyncio.to_thread(event.save)
        return {
            'id': event_id,
            'summary': summary,
            'start': start,
            'end': end,
            'description': description,
            'location': location
        }

    async def delete_event(self, calendar_name: str, event_id: str):
        if not self.client:
            await self.connect()
        calendars = await self.get_calendars()
        calendar = next((cal for cal in calendars if cal['name'] == calendar_name), None)
        if not calendar:
            raise ValueError(f"Calendar '{calendar_name}' not found")

        cal = self.client.calendar(url=calendar['url'])
        event = await asyncio.to_thread(cal.event, event_id)
        await asyncio.to_thread(event.delete)
