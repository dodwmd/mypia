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
def test_user(client):
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    response = client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Personal AI Assistant API"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user(client):
    user_data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
    response = client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}


def test_login(client, test_user):
    response = client.post(
        "/v1/auth/token", data={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert isinstance(token["access_token"], str)
    assert token["token_type"] == "bearer"

# Add more tests for other endpoints (text processing, email, calendar, tasks, etc.)
# Make sure to use the correct route prefixes as defined in main.py
