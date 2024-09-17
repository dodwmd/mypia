from typing import List, Dict, Any, Optional
from datetime import datetime
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.web.scraper import WebScraper
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.models.task import Task
from sqlalchemy.orm import Session


class TaskManager:
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, title: str, description: str) -> Task:
        new_task = Task(title=title, description=description)
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def get_all_tasks(self) -> List[Task]:
        return await self.db.query(Task).all()

    async def get_task(self, task_id: int) -> Task:
        return self.db.query(Task).filter(Task.id == task_id).first()

    async def update_task(self, task_id: int, title: str, description: str) -> Task:
        task = await self.get_task(task_id)
        if task:
            task.title = title
            task.description = description
            self.db.commit()
            self.db.refresh(task)
        return task

    async def delete_task(self, task_id: int) -> bool:
        task = await self.get_task(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False

    async def complete_task(self, task_id: int) -> Task:
        task = await self.get_task(task_id)
        if task:
            task.completed = True
            task.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(task)
        return task


class ScheduledTask(Task):
    def __init__(self, title: str, description: str, start_time: datetime, end_time: Optional[datetime] = None):
        super().__init__(title, description)
        self.start_time = start_time
        self.end_time = end_time

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        })
        return task_dict


class CommunicationTask(Task):
    def __init__(self, title: str, description: str, recipient: str):
        super().__init__(title, description)
        self.recipient = recipient

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "recipient": self.recipient,
        })
        return task_dict


class CalendarTask(ScheduledTask):
    def __init__(self, title: str, description: str, start_time: datetime, end_time: datetime, location: str = "", caldav_client: CalDAVClient = None):
        super().__init__(title, description, start_time, end_time)
        self.location = location
        self.caldav_client = caldav_client

    async def execute(self) -> Dict[str, Any]:
        if not self.caldav_client:
            return {"status": "error", "message": "CalDAV client not initialized"}
        event = await self.caldav_client.create_event("default", self.title, self.start_time, self.end_time, self.description)
        return {"status": "success", "message": f"Calendar event '{self.title}' created", "event_id": event['id']}

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "location": self.location,
        })
        return task_dict


class EmailTask(CommunicationTask):
    def __init__(self, title: str, description: str, recipient: str, subject: str, body: str, email_client: EmailClient = None):
        super().__init__(title, description, recipient)
        self.subject = subject
        self.body = body
        self.email_client = email_client

    async def execute(self) -> Dict[str, Any]:
        if not self.email_client:
            return {"status": "error", "message": "Email client not initialized"}
        await self.email_client.send_email(self.recipient, self.subject, self.body)
        return {"status": "success", "message": f"Email '{self.subject}' sent to {self.recipient}"}

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "subject": self.subject,
        })
        return task_dict


class WebLookupTask(Task):
    def __init__(self, title: str, description: str, url: str, text_processor: TextProcessor = None):
        super().__init__(title, description)
        self.url = url
        self.text_processor = text_processor

    async def execute(self) -> Dict[str, Any]:
        scraped_data = await WebScraper.scrape_url(self.url)
        if not scraped_data:
            return {"status": "error", "message": f"Failed to scrape content from {self.url}"}
        if self.text_processor:
            summary = await self.text_processor.summarize_text(scraped_data['content'], max_length=200)
        else:
            summary = await WebScraper.summarize_content(scraped_data['content'], max_length=200)
        return {
            "status": "success",
            "message": f"Looked up information from {self.url}",
            "title": scraped_data['title'],
            "author": scraped_data['author'],
            "date": scraped_data['date'],
            "summary": summary
        }

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "url": self.url,
        })
        return task_dict


class GitHubPRReviewTask(Task):
    def __init__(self, title: str, description: str, repo_name: str, pr_number: int, github_client: GitHubClient):
        super().__init__(title, description)
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.github_client = github_client

    async def execute(self) -> Dict[str, Any]:
        review_result = await self.github_client.review_pr(self.repo_name, self.pr_number)
        action_logs = await self.github_client.parse_action_logs(self.repo_name, self.pr_number)
        suggested_fixes = await self.github_client.suggest_fixes(self.repo_name, self.pr_number)
        auto_update_result = await self.github_client.auto_update_pr(self.repo_name, self.pr_number)
        auto_respond_result = await self.github_client.auto_respond_to_pr_comments(self.repo_name, self.pr_number)
        return {
            "status": "success",
            "message": f"Completed review and automated actions for PR #{self.pr_number} in {self.repo_name}",
            "review": review_result,
            "action_logs": action_logs,
            "suggested_fixes": suggested_fixes,
            "auto_update": auto_update_result,
            "auto_respond": auto_respond_result
        }

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        task_dict.update({
            "repo_name": self.repo_name,
            "pr_number": self.pr_number,
        })
        return task_dict


class GeneralInfoLookupTask(Task):
    def __init__(self, title: str, description: str, query: str, text_processor: TextProcessor = None):
        super().__init__(title, description)
        self.query = query
        self.text_processor = text_processor

    async def execute(self) -> Dict[str, Any]:
        if not self.text_processor:
            return {"status": "error", "message": "Text processor not initialized"}
        response = await self.text_processor.generate_text(f"Provide information about: {self.query}")
        return {"status": "success", "message": "Information lookup completed", "response": response}

    def to_dict(self) -> Dict[str, Any]:
        task_dict = super().to_dict()
        return task_dict
