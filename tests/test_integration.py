import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from personal_ai_assistant.api.main import app
from personal_ai_assistant.api.dependencies import get_llm, get_auth_manager, get_db

@pytest.fixture
def client():
    with patch('personal_ai_assistant.api.dependencies.LlamaCppInterface') as mock_llm, \
         patch('personal_ai_assistant.api.dependencies.AuthManager') as mock_auth_manager, \
         patch('personal_ai_assistant.api.dependencies.SessionLocal') as mock_db:
        
        mock_llm.return_value = MagicMock()
        mock_auth_manager.return_value = MagicMock()
        mock_db.return_value = MagicMock()
        
        app.dependency_overrides[get_llm] = lambda: mock_llm.return_value
        app.dependency_overrides[get_auth_manager] = lambda: mock_auth_manager.return_value
        app.dependency_overrides[get_db] = lambda: mock_db.return_value
        
        yield TestClient(app)
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_token(client):
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    client.post("/v1/auth/register", json=user_data)
    response = client.post("/v1/auth/token", data={"username": user_data["username"], "password": user_data["password"]})
    return response.json()["access_token"]

def test_create_and_list_tasks(client, auth_token):
    # Create a task
    create_response = client.post(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Integration Test Task", "description": "This is an integration test task"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["task_id"]

    # List tasks
    list_response = client.get(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert list_response.status_code == 200
    tasks = list_response.json()["tasks"]
    assert any(task["id"] == task_id for task in tasks)

# Add more integration tests for other functionalities (email, calendar, text processing, etc.)
# Make sure to use the correct route prefixes as defined in main.py

def test_end_to_end_workflow(client, auth_token):
    # This test should cover a complete workflow using multiple endpoints
    # For example: create a task, process some text, send an email, etc.
    pass
