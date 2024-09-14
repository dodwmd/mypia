import pytest
import asyncio
from unittest.mock import patch, MagicMock
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.config import settings

@pytest.fixture
def email_client():
    return EmailClient(settings.email_host, settings.smtp_host, settings.email_username, settings.email_password.get_secret_value())

@pytest.fixture
def db_manager():
    return DatabaseManager(settings.database_url.get_secret_value())

@pytest.fixture
def chroma_db():
    return ChromaDBManager(settings.chroma_db_path)

@pytest.fixture
def llm_interface():
    return LlamaCppInterface(settings.llm_model_path)

@pytest.mark.asyncio
async def test_email_ingestion_and_summarization(email_client, db_manager, chroma_db, llm_interface):
    # Mock email fetching
    mock_emails = [
        {
            'uid': '1',
            'subject': 'Test Email',
            'from': 'sender@example.com',
            'date': '2023-06-01 10:00:00',
            'content': 'This is a test email content.'
        }
    ]
    with patch.object(email_client, 'fetch_new_emails', return_value=mock_emails):
        # Fetch and process new emails
        new_emails = await email_client.fetch_new_emails(last_uid=0)
        
        # Log email in database
        for email in new_emails:
            db_manager.log_email(
                user_id=1,
                subject=email['subject'],
                sender=email['from'],
                recipient=settings.email_username,
                is_sent=0
            )
        
        # Add email to vector database
        for email in new_emails:
            document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
            chroma_db.add_documents("emails", [document], [email], [email['uid']])
        
        # Summarize email using LLM
        email_content = new_emails[0]['content']
        summary = llm_interface.summarize(email_content, max_length=50)
        
        # Verify results
        assert len(new_emails) == 1
        assert new_emails[0]['subject'] == 'Test Email'
        
        # Check if email was logged in database
        email_logs = db_manager.get_email_logs(user_id=1, limit=1)
        assert len(email_logs) == 1
        assert email_logs[0].subject == 'Test Email'
        
        # Check if email was added to vector database
        results = chroma_db.query("emails", ["test email"], n_results=1)
        assert len(results['documents'][0]) == 1
        assert "Test Email" in results['documents'][0][0]
        
        # Check if summary was generated
        assert len(summary) > 0
        assert len(summary.split()) <= 50

@pytest.mark.asyncio
async def test_task_creation_and_execution(db_manager, chroma_db, llm_interface):
    # Create a task
    task_id = db_manager.create_task(user_id=1, title="Test Task", description="This is a test task")
    
    # Verify task creation
    task = db_manager.get_task(task_id)
    assert task.title == "Test Task"
    
    # Simulate task execution
    task_content = f"{task.title}: {task.description}"
    task_result = llm_interface.generate(f"Execute the following task: {task_content}")
    
    # Update task status
    db_manager.update_task(task_id, status="completed")
    
    # Add task result to vector database
    chroma_db.add_documents("task_results", [task_result], [{"task_id": task_id}], [str(task_id)])
    
    # Verify results
    updated_task = db_manager.get_task(task_id)
    assert updated_task.status == "completed"
    
    results = chroma_db.query("task_results", ["test task"], n_results=1)
    assert len(results['documents'][0]) == 1
    assert task_result in results['documents'][0][0]

@pytest.mark.asyncio
async def test_email_response_generation(email_client, db_manager, chroma_db, llm_interface):
    # Mock received email
    received_email = {
        'uid': '1',
        'subject': 'Question about Project X',
        'from': 'client@example.com',
        'content': 'What is the status of Project X?'
    }
    
    # Generate response using LLM
    context = chroma_db.query("project_documents", ["Project X"], n_results=3)
    context_text = "\n".join([doc for doc in context['documents'][0]])
    prompt = f"Given the following context:\n{context_text}\n\nRespond to this email:\n{received_email['content']}"
    response_content = llm_interface.generate(prompt, max_tokens=200)
    
    # Create email response
    with patch.object(email_client, 'send_email') as mock_send_email:
        await email_client.send_email(
            to=received_email['from'],
            subject=f"Re: {received_email['subject']}",
            body=response_content
        )
    
    # Verify email was sent
    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args[1]
    assert call_args['to'] == 'client@example.com'
    assert call_args['subject'] == 'Re: Question about Project X'
    assert call_args['body'] == response_content
    
    # Log sent email
    db_manager.log_email(
        user_id=1,
        subject=f"Re: {received_email['subject']}",
        sender=settings.email_username,
        recipient=received_email['from'],
        is_sent=1
    )
    
    # Verify email was logged
    email_logs = db_manager.get_email_logs(user_id=1, limit=1)
    assert len(email_logs) == 1
    assert email_logs[0].subject == 'Re: Question about Project X'
    assert email_logs[0].is_sent == 1
