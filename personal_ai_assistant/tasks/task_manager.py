from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import requests
from bs4 import BeautifulSoup
from github import Github
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.web.scraper import WebScraper
from personal_ai_assistant.github.github_client import GitHubClient

class Task(ABC):
    def __init__(self, title: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_at = datetime.now()
        self.completed_at = None

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        pass

    def mark_completed(self):
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "type": self.__class__.__name__
        }

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

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task with id {task_id} not found")

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.tasks]

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        task = self.get_task(task_id)
        result = await task.execute()
        task.mark_completed()
        return result

    def remove_task(self, task_id: str):
        task = self.get_task(task_id)
        self.tasks.remove(task)
