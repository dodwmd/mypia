import pytest
import asyncio
from unittest.mock import patch, MagicMock
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import TaskManager, EmailTask, CalendarTask
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.config import settings
from datetime import datetime, timedelta

@pytest.fixture
def email_client():
    return EmailClient(
        settings.email_host,
        settings.smtp_host,
        settings.email_username,
        settings.email_password
    )

@pytest.fixture
def db_manager():
    return DatabaseManager(settings.database_url.get_secret_value())

@pytest.fixture
def chroma_db():
    return ChromaDBManager(settings.chroma_db_path)

@pytest.fixture
def llm_interface():
    return LlamaCppInterface(settings.llm_model_path)

@pytest.fixture
def caldav_client():
    return CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password.get_secret_value())

@pytest.fixture
def task_manager():
    return TaskManager()

@pytest.fixture
def github_client():
    return GitHubClient(settings.github_token)

@pytest.mark.asyncio
async def test_email_workflow(email_client, db_manager, chroma_db, llm_interface, task_manager):
    # Mock incoming email
    mock_email = {
        'uid': '1',
        'subject': 'Meeting Request',
        'from': 'colleague@example.com',
        'date': datetime.now().isoformat(),
        'content': 'Can we schedule a meeting next week to discuss the project?'
    }

    # Process incoming email
    with patch.object(email_client, 'fetch_new_emails', return_value=[mock_email]):
        new_emails = await email_client.fetch_new_emails(last_uid=0)
        
        # Log email in database
        db_manager.log_email(
            user_id=1,
            subject=mock_email['subject'],
            sender=mock_email['from'],
            recipient=settings.email_username,
            is_sent=0
        )
        
        # Add email to vector database
        document = f"Subject: {mock_email['subject']}\n\nFrom: {mock_email['from']}\n\nContent: {mock_email['content']}"
        chroma_db.add_documents("emails", [document], [mock_email], [mock_email['uid']])
        
        # Generate response using LLM
        response_content = llm_interface.generate(f"Generate a polite response to this email:\n{mock_email['content']}")
        
        # Create email response task
        email_task = EmailTask(
            title="Respond to Meeting Request",
            description="Send a response to the meeting request email",
            recipient=mock_email['from'],
            subject=f"Re: {mock_email['subject']}",
            body=response_content,
            email_client=email_client
        )
        task_manager.add_task(email_task)
        
        # Execute email task
        await task_manager.execute_task(email_task.id)
        
        # Verify results
        email_logs = db_manager.get_email_logs(user_id=1, limit=2)
        assert len(email_logs) == 2
        assert email_logs[0].subject == 'Re: Meeting Request'
        assert email_logs[0].is_sent == 1
        
        results = chroma_db.query("emails", ["meeting request"], n_results=1)
        assert len(results['documents'][0]) == 1
        assert "Meeting Request" in results['documents'][0][0]

@pytest.mark.asyncio
async def test_calendar_workflow(caldav_client, db_manager, chroma_db, task_manager):
    # Create a calendar event
    event_details = {
        'summary': 'Team Meeting',
        'start': datetime.now() + timedelta(days=1),
        'end': datetime.now() + timedelta(days=1, hours=1),
        'description': 'Discuss project progress'
    }
    
    calendar_task = CalendarTask(
        title="Schedule Team Meeting",
        description="Create a calendar event for the team meeting",
        start_time=event_details['start'],
        end_time=event_details['end'],
        location="Conference Room A",
        caldav_client=caldav_client
    )
    task_manager.add_task(calendar_task)
    
    # Execute calendar task
    await task_manager.execute_task(calendar_task.id)
    
    # Verify results
    events = await caldav_client.get_events("default", event_details['start'], event_details['end'])
    assert len(events) == 1
    assert events[0]['summary'] == 'Team Meeting'
    
    # Add event to vector database
    document = f"Summary: {event_details['summary']}\nStart: {event_details['start']}\nEnd: {event_details['end']}\nDescription: {event_details['description']}"
    chroma_db.add_documents("calendar_events", [document], [event_details], [events[0]['id']])
    
    results = chroma_db.query("calendar_events", ["team meeting"], n_results=1)
    assert len(results['documents'][0]) == 1
    assert "Team Meeting" in results['documents'][0][0]

@pytest.mark.asyncio
async def test_github_pr_workflow(github_client, db_manager, chroma_db, llm_interface):
    # Mock GitHub PR
    mock_pr = {
        'number': 123,
        'title': 'Add new feature',
        'body': 'This PR adds a new feature to the project.',
        'user': {'login': 'contributor'},
        'html_url': 'https://github.com/owner/repo/pull/123'
    }
    
    with patch.object(github_client, 'get_pull_request', return_value=mock_pr):
        # Review PR
        review_result = await github_client.review_pr("owner/repo", 123)
        
        # Generate review comment using LLM
        review_comment = llm_interface.generate(f"Generate a constructive review comment for this PR:\n{mock_pr['body']}")
        
        # Add review comment
        await github_client.add_pr_comment("owner/repo", 123, review_comment)
        
        # Log PR review in database
        db_manager.log_github_activity(
            user_id=1,
            activity_type="PR_REVIEW",
            repo="owner/repo",
            pr_number=123,
            details=f"Reviewed PR: {mock_pr['title']}"
        )
        
        # Add PR to vector database
        document = f"Title: {mock_pr['title']}\nBody: {mock_pr['body']}\nReview: {review_comment}"
        chroma_db.add_documents("github_prs", [document], [mock_pr], [str(mock_pr['number'])])
        
        # Verify results
        github_logs = db_manager.get_github_activity_logs(user_id=1, limit=1)
        assert len(github_logs) == 1
        assert github_logs[0].activity_type == "PR_REVIEW"
        assert github_logs[0].pr_number == 123
        
        results = chroma_db.query("github_prs", ["new feature"], n_results=1)
        assert len(results['documents'][0]) == 1
        assert "Add new feature" in results['documents'][0][0]

# Add more end-to-end tests for other workflows as needed
