import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from personal_ai_assistant.api.main import app
from personal_ai_assistant.api.dependencies import get_llm, get_auth_manager, get_db
from personal_ai_assistant.tasks.task_manager import TaskManager
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.email.imap_client import EmailClient


@pytest.fixture
def client():
    with patch('personal_ai_assistant.api.dependencies.LlamaCppInterface') as mock_llm, \
            patch('personal_ai_assistant.api.dependencies.AuthManager') as mock_auth_manager, \
            patch('personal_ai_assistant.api.dependencies.SessionLocal') as mock_db, \
            patch('personal_ai_assistant.tasks.task_manager.TaskManager') as mock_task_manager:

        mock_llm.return_value = MagicMock()
        mock_auth_manager.return_value = MagicMock()
        mock_db.return_value = MagicMock()
        mock_task_manager.return_value = MagicMock()

        app.dependency_overrides[get_llm] = lambda: mock_llm.return_value
        app.dependency_overrides[get_auth_manager] = lambda: mock_auth_manager.return_value
        app.dependency_overrides[get_db] = lambda: mock_db.return_value
        app.dependency_overrides[TaskManager] = lambda: mock_task_manager.return_value

        yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    client.post("/v1/auth/register", json=user_data)
    response = client.post(
        "/v1/auth/token", data={"username": user_data["username"], "password": user_data["password"]})
    return response.json()["access_token"]


def test_create_and_list_tasks(client, auth_token):
    # Mock the create_task method
    async def mock_create_task(*args, **kwargs):
        return MagicMock(to_dict=lambda: {
            "id": 1,
            "title": "Integration Test Task",
            "description": "This is an integration test task",
            "completed": False
        })

    with patch.object(TaskManager, 'create_task', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = mock_create_task

        # Create a task
        create_response = client.post(
            "/v1/tasks",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Integration Test Task", "description": "This is an integration test task"}
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        assert "id" in created_task
        assert created_task["title"] == "Integration Test Task"

    # Mock the get_all_tasks method
    async def mock_get_all_tasks(*args, **kwargs):
        return [MagicMock(to_dict=lambda: created_task)]

    with patch.object(TaskManager, 'get_all_tasks', new_callable=AsyncMock) as mock_get_all:
        mock_get_all.side_effect = mock_get_all_tasks

        # List tasks
        list_response = client.get(
            "/v1/tasks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert isinstance(tasks, list)
        assert any(task["id"] == created_task["id"] for task in tasks)

# Add more integration tests for other functionalities (email, calendar, text processing, etc.)
# Make sure to use the correct route prefixes as defined in main.py


def test_end_to_end_workflow(client, auth_token):
    # 1. Create a task
    async def mock_create_task(*args, **kwargs):
        return MagicMock(to_dict=lambda: {
            "id": 1,
            "title": "End-to-end Test Task",
            "description": "This is an end-to-end test task",
            "completed": False
        })

    with patch.object(TaskManager, 'create_task', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = mock_create_task

        create_response = client.post(
            "/v1/tasks",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "End-to-end Test Task", "description": "This is an end-to-end test task"}
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        assert created_task["title"] == "End-to-end Test Task"

    # 2. Process some text
    async def mock_summarize_text(*args, **kwargs):
        return "This is a mock summary of the processed text."

    with patch.object(TextProcessor, 'summarize_text', new_callable=AsyncMock) as mock_summarize:
        mock_summarize.side_effect = mock_summarize_text

        text_to_process = "This is a long text that needs to be summarized for our end-to-end test workflow."
        summarize_response = client.post(
            "/v1/text/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"text": text_to_process, "max_length": 50}
        )
        assert summarize_response.status_code == 200
        summary = summarize_response.json()["summary"]
        assert summary == "This is a mock summary of the processed text."

    # 3. Send an email
    async def mock_send_email(*args, **kwargs):
        return True

    with patch('personal_ai_assistant.api.dependencies.EmailClient', autospec=True) as MockEmailClient:
        mock_email_client = MockEmailClient.return_value
        mock_email_client.send_email.side_effect = mock_send_email

        email_data = {
            "to": "test@example.com",
            "subject": "End-to-end Test Email",
            "body": f"Task created: {created_task['title']}\n\nSummary: {summary}"
        }
        email_response = client.post(
            "/v1/email/send",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=email_data
        )
        assert email_response.status_code == 200
        assert email_response.json()["message"] == "Email sent successfully"

    # 4. Verify the task is completed
    async def mock_complete_task(*args, **kwargs):
        return MagicMock(to_dict=lambda: {
            "id": 1,
            "title": "End-to-end Test Task",
            "description": "This is an end-to-end test task",
            "completed": True
        })

    with patch.object(TaskManager, 'complete_task', new_callable=AsyncMock) as mock_complete:
        mock_complete.side_effect = mock_complete_task

        complete_response = client.post(
            f"/v1/tasks/{created_task['id']}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True  # Changed from == True to is True

    # The end-to-end workflow is complete
    print("End-to-end workflow test completed successfully")
