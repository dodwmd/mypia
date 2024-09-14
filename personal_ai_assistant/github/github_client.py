import asyncio
from aioimaplib import aioimaplib
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import email.utils
import datetime
import aiosmtplib
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.utils.cache import cache
from github import Github


class GitHubClient:
    def __init__(self, access_token: str):
        self.github = Github(access_token)

    def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        user = self.github.get_user(username)
        return [
            {
                "name": repo.name,
                "description": repo.description,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count
            }
            for repo in user.get_repos()
        ]

    def get_repo_issues(self, repo_full_name: str) -> List[Dict[str, Any]]:
        repo = self.github.get_repo(repo_full_name)
        return [
            {
                "title": issue.title,
                "number": issue.number,
                "state": issue.state,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
                "url": issue.html_url
            }
            for issue in repo.get_issues(state="all")
        ]

    def create_issue(self, repo_full_name: str, title: str, body: str) -> Dict[str, Any]:
        repo = self.github.get_repo(repo_full_name)
        issue = repo.create_issue(title=title, body=body)
        return {
            "title": issue.title,
            "number": issue.number,
            "state": issue.state,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "url": issue.html_url
        }

    def get_pull_requests(self, repo_full_name: str) -> List[Dict[str, Any]]:
        repo = self.github.get_repo(repo_full_name)
        return [
            {
                "title": pr.title,
                "number": pr.number,
                "state": pr.state,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at,
                "url": pr.html_url
            }
            for pr in repo.get_pulls(state="all")
        ]
