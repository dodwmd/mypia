import asyncio
from typing import List, Dict, Any
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.config import settings

class SyncManager:
    def __init__(self, db_manager: DatabaseManager, chroma_db: ChromaDBManager):
        self.db_manager = db_manager
        self.chroma_db = chroma_db
        self.email_client = EmailClient(settings.email_host, settings.smtp_host, settings.email_username, settings.email_password.get_secret_value())
        self.caldav_client = CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password.get_secret_value())
        self.github_client = GitHubClient(settings.github_token.get_secret_value())

    async def sync_all(self):
        """Synchronize all data when internet connection is restored."""
        await asyncio.gather(
            self.sync_emails(),
            self.sync_calendar(),
            self.sync_github(),
            self.sync_offline_actions()
        )

    async def sync_emails(self):
        """Synchronize emails."""
        last_synced_uid = self.db_manager.get_last_synced_email_uid()
        new_emails = await self.email_client.fetch_new_emails(last_synced_uid)
        for email in new_emails:
            self.db_manager.log_email(
                user_id=1,  # Assuming a default user ID of 1
                subject=email['subject'],
                sender=email['from'],
                recipient=settings.email_username,
                is_sent=0
            )
            document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
            self.chroma_db.add_documents("emails", [document], [email], [str(email['uid'])])
        self.db_manager.update_last_synced_email_uid(new_emails[-1]['uid'] if new_emails else last_synced_uid)

    async def sync_calendar(self):
        """Synchronize calendar events."""
        last_synced_date = self.db_manager.get_last_synced_calendar_date()
        new_events = await self.caldav_client.get_events("default", start=last_synced_date)
        for event in new_events:
            self.db_manager.log_calendar_event(
                user_id=1,
                summary=event['summary'],
                start=event['start'],
                end=event['end'],
                description=event['description']
            )
            document = f"Summary: {event['summary']}\nStart: {event['start']}\nEnd: {event['end']}\nDescription: {event['description']}"
            self.chroma_db.add_documents("calendar_events", [document], [event], [event['id']])
        self.db_manager.update_last_synced_calendar_date(max(event['end'] for event in new_events) if new_events else last_synced_date)

    async def sync_github(self):
        """Synchronize GitHub data."""
        last_synced_date = self.db_manager.get_last_synced_github_date()
        new_activities = await self.github_client.get_user_activities(since=last_synced_date)
        for activity in new_activities:
            self.db_manager.log_github_activity(
                user_id=1,
                activity_type=activity['type'],
                repo=activity['repo']['name'],
                details=activity['payload']
            )
            document = f"Type: {activity['type']}\nRepo: {activity['repo']['name']}\nDetails: {activity['payload']}"
            self.chroma_db.add_documents("github_activities", [document], [activity], [activity['id']])
        self.db_manager.update_last_synced_github_date(max(activity['created_at'] for activity in new_activities) if new_activities else last_synced_date)

    async def sync_offline_actions(self):
        """Synchronize actions performed while offline."""
        offline_actions = self.db_manager.get_offline_actions()
        for action in offline_actions:
            if action['type'] == 'email':
                await self.email_client.send_email(action['to'], action['subject'], action['body'])
            elif action['type'] == 'calendar':
                await self.caldav_client.create_event(action['calendar'], action['summary'], action['start'], action['end'], action['description'])
            elif action['type'] == 'github':
                if action['action'] == 'create_issue':
                    await self.github_client.create_issue(action['repo'], action['title'], action['body'])
                elif action['action'] == 'create_pr':
                    await self.github_client.create_pull_request(action['repo'], action['title'], action['body'], action['base'], action['head'])
            self.db_manager.mark_offline_action_synced(action['id'])

    @staticmethod
    async def is_internet_available():
        """Check if internet connection is available."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, __import__, 'http.client')
            return True
        except ImportError:
            return False
