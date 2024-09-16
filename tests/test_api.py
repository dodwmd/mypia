import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from personal_ai_assistant.api.main import app

@pytest.fixture
def client():
    with patch('personal_ai_assistant.api.main.LlamaCppInterface') as mock_llm:
        mock_llm.return_value = MagicMock()
        yield TestClient(app)

@pytest.fixture
def auth_token(client):
    response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to MyPIA API"}

def test_create_user(client):
    response = client.post(
        "/v1/auth/register",
        json={"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
    )
    assert response.status_code == 201
    assert "user_id" in response.json()

def test_login(client):
    response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_user_info(auth_token):
    response = client.get(
        "/v1/user/info",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "username" in response.json()
    assert "email" in response.json()

def test_create_task(auth_token):
    response = client.post(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Test Task", "description": "This is a test task"}
    )
    assert response.status_code == 201
    assert "task_id" in response.json()

def test_list_tasks(auth_token):
    response = client.get(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "tasks" in response.json()

def test_delete_task(auth_token):
    # First, create a task
    create_response = client.post(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Task to Delete", "description": "This task will be deleted"}
    )
    task_id = create_response.json()["task_id"]

    # Now, delete the task
    delete_response = client.delete(
        f"/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted successfully"}

def test_summarize_text(auth_token):
    response = client.post(
        "/v1/nlp/summarize",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": "This is a long text that needs to be summarized.", "max_length": 50, "format": "paragraph"}
    )
    assert response.status_code == 200
    assert "summary" in response.json()

def test_generate_text(auth_token):
    response = client.post(
        "/v1/nlp/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": "Generate a story about", "max_length": 100}
    )
    assert response.status_code == 200
    assert "generated_text" in response.json()

def test_analyze_sentiment(auth_token):
    response = client.post(
        "/v1/nlp/sentiment",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": "I love this product, it's amazing!"}
    )
    assert response.status_code == 200
    assert "sentiment" in response.json()

def test_fetch_emails(auth_token):
    response = client.get(
        "/v1/email",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"limit": 5}
    )
    assert response.status_code == 200
    assert "emails" in response.json()

def test_send_email(auth_token):
    response = client.post(
        "/v1/email/send",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "to": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email sent from the API."
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Email sent successfully"}

def test_add_to_vectordb(auth_token):
    response = client.post(
        "/v1/vectordb/add",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "collection_name": "test_collection",
            "document": "This is a test document to add to the vector database.",
            "metadata": {"source": "api_test"}
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Document added successfully"}

def test_query_vectordb(auth_token):
    response = client.post(
        "/v1/vectordb/query",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "collection_name": "test_collection",
            "query_text": "test document",
            "n_results": 1
        }
    )
    assert response.status_code == 200
    assert "results" in response.json()

def test_create_backup(auth_token):
    response = client.post(
        "/v1/system/backup",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Backup process started"}

def test_sync_data(auth_token):
    response = client.post(
        "/v1/system/sync",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Sync process started"}

def test_unauthorized_access():
    response = client.get("/v1/user/info")
    assert response.status_code == 401

def test_not_found():
    response = client.get("/v1/nonexistent_endpoint")
    assert response.status_code == 404
