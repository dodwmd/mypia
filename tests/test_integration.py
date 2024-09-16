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

def test_create_and_summarize_email(client, auth_token):
    # Create an email
    create_response = client.post(
        "/v1/email/send",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "to": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email for integration testing."
        }
    )
    assert create_response.status_code == 200

    # Fetch and summarize emails
    summarize_response = client.get(
        "/v1/email/summarize_new",
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"max_length": 50, "limit": 1}
    )
    assert summarize_response.status_code == 200
    summarized_emails = summarize_response.json()["summarized_emails"]
    assert len(summarized_emails) > 0
    assert "summary" in summarized_emails[0]

def test_nlp_workflow(client, auth_token):
    # Generate text
    generate_response = client.post(
        "/v1/nlp/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": "Write a short story about", "max_length": 100}
    )
    assert generate_response.status_code == 200
    generated_text = generate_response.json()["generated_text"]

    # Summarize the generated text
    summarize_response = client.post(
        "/v1/nlp/summarize",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": generated_text, "max_length": 50, "format": "paragraph"}
    )
    assert summarize_response.status_code == 200
    summary = summarize_response.json()["summary"]

    # Analyze sentiment of the summary
    sentiment_response = client.post(
        "/v1/nlp/sentiment",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": summary}
    )
    assert sentiment_response.status_code == 200
    sentiment = sentiment_response.json()["sentiment"]

    assert all(key in sentiment for key in ["positive", "negative", "neutral"])

def test_vector_db_workflow(client, auth_token):
    # Add document to vector database
    add_response = client.post(
        "/v1/vectordb/add",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "collection_name": "test_collection",
            "document": "This is a test document for vector database integration testing.",
            "metadata": {"source": "integration_test"}
        }
    )
    assert add_response.status_code == 200

    # Query vector database
    query_response = client.post(
        "/v1/vectordb/query",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "collection_name": "test_collection",
            "query_text": "test document",
            "n_results": 1
        }
    )
    assert query_response.status_code == 200
    results = query_response.json()["results"]
    assert len(results["documents"][0]) > 0
    assert "integration_test" in results["metadatas"][0][0]["source"]

def test_system_operations(client, auth_token):
    # Create backup
    backup_response = client.post(
        "/v1/system/backup",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert backup_response.status_code == 200
    assert backup_response.json()["message"] == "Backup process started"

    # Sync data
    sync_response = client.post(
        "/v1/system/sync",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert sync_response.status_code == 200
    assert sync_response.json()["message"] == "Sync process started"

    # List backups
    list_backups_response = client.get(
        "/v1/system/backup/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert list_backups_response.status_code == 200
    backups = list_backups_response.json()["backups"]
    assert isinstance(backups, list)

def test_end_to_end_workflow(client, auth_token):
    # Create a task
    task_response = client.post(
        "/v1/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Write a report", "description": "Write a report on the latest project status"}
    )
    assert task_response.status_code == 201
    task_id = task_response.json()["task_id"]

    # Generate a report using NLP
    generate_response = client.post(
        "/v1/nlp/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": "Generate a project status report", "max_length": 200}
    )
    assert generate_response.status_code == 200
    report = generate_response.json()["generated_text"]

    # Summarize the report
    summarize_response = client.post(
        "/v1/nlp/summarize",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"text": report, "max_length": 50, "format": "paragraph"}
    )
    assert summarize_response.status_code == 200
    summary = summarize_response.json()["summary"]

    # Add the report to the vector database
    add_response = client.post(
        "/v1/vectordb/add",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "collection_name": "reports",
            "document": report,
            "metadata": {"task_id": task_id, "type": "project_status"}
        }
    )
    assert add_response.status_code == 200

    # Send an email with the report summary
    email_response = client.post(
        "/v1/email/send",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "to": "manager@example.com",
            "subject": "Project Status Report",
            "body": f"Here's a summary of the latest project status:\n\n{summary}"
        }
    )
    assert email_response.status_code == 200

    # Update task status
    update_task_response = client.put(
        f"/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"status": "completed"}
    )
    assert update_task_response.status_code == 200

    # Verify task is completed
    task_response = client.get(
        f"/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert task_response.status_code == 200
    assert task_response.json()["status"] == "completed"
