import sys
import os
import base64
import secrets
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from personal_ai_assistant.database.base import Base, get_db
from personal_ai_assistant.models.user import User
import personal_ai_assistant.database.models
from personal_ai_assistant.config.config import settings
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.github.github_client import GitHubClient
from pydantic import SecretStr
from datetime import datetime, timedelta
import uuid

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def engine():
    return create_engine(settings.database_url)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db_manager():
    return DatabaseManager(settings.database_url)


@pytest.fixture(scope="function")
def encryption_manager():
    return EncryptionManager()


@pytest.fixture(scope="function")
def auth_manager(db_manager, encryption_manager):
    return AuthManager(db_manager, encryption_manager)


@pytest.fixture(scope="function")
def test_user(auth_manager):
    unique_id = uuid.uuid4().hex[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "testpassword"
    user = auth_manager.create_user(username, email, password)
    return user


@pytest.fixture
def auth_token(client, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": test_user.username, "password": "testpassword"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def client(db_manager, auth_manager):
    app.dependency_overrides[DatabaseManager] = lambda: db_manager
    app.dependency_overrides[AuthManager] = lambda: auth_manager
    return TestClient(app)


@pytest.fixture
def mock_redis(monkeypatch):
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    monkeypatch.setattr("redis.Redis", lambda *args, **kwargs: mock_redis)
    return mock_redis


@pytest.fixture
def mock_llama_cpp(monkeypatch):
    mock_llama = Mock()
    mock_llama.generate.return_value = "Generated text"
    mock_llama.summarize.return_value = "Summarized text"
    monkeypatch.setattr("personal_ai_assistant.llm.llama_cpp_interface.LlamaCppInterface",
                        lambda *args, **kwargs: mock_llama)
    return mock_llama


@pytest.fixture
def mock_email_client(monkeypatch):
    mock_client = Mock()
    mock_client.fetch_emails.return_value = []
    mock_client.send_email.return_value = True
    monkeypatch.setattr("personal_ai_assistant.email.imap_client.EmailClient", lambda *args, **kwargs: mock_client)
    return mock_client


@pytest.fixture
def mock_caldav_client(monkeypatch):
    mock_client = Mock()
    mock_client.get_events.return_value = []
    mock_client.create_event.return_value = True
    monkeypatch.setattr("personal_ai_assistant.calendar.caldav_client.CalDAVClient",
                        lambda *args, **kwargs: mock_client)
    return mock_client


@pytest.fixture
def mock_github_client(monkeypatch):
    mock_client = Mock()
    mock_client.get_user_repos.return_value = []
    mock_client.get_repo_issues.return_value = []
    monkeypatch.setattr("personal_ai_assistant.github.github_client.GitHubClient", lambda *args, **kwargs: mock_client)
    return mock_client


@pytest.fixture
def mock_chroma_db(monkeypatch):
    mock_db = Mock()
    mock_db.add_documents.return_value = True
    mock_db.query.return_value = {"results": []}
    monkeypatch.setattr("personal_ai_assistant.vector_db.chroma_db.ChromaDBManager", lambda *args, **kwargs: mock_db)
    return mock_db


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    # Override settings with test values
    test_settings = {
        "database_url": settings.database_url,  # Use the actual database URL from settings
        "redis_url": "redis://localhost:6379/0",
        "llm_model_path": "/app/static/models/llama-2-7b-chat.Q4_K_M.gguf",
        "email_host": "test.email.com",
        "smtp_host": "test.smtp.com",
        "email_username": "test@email.com",
        "email_password": SecretStr("testpassword"),
        "caldav_url": "https://test.caldav.com",
        "caldav_username": "testuser",
        "caldav_password": SecretStr("testpassword"),
        "github_token": SecretStr("test_github_token"),
    }
    for key, value in test_settings.items():
        monkeypatch.setattr(settings, key, value)


@pytest.fixture
def mock_auth_manager():
    return MagicMock(spec=AuthManager)


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.generate.return_value = "Generated text"
    mock.summarize.return_value = "Summarized text"
    return mock


@pytest.fixture
def mock_email_client_instance():
    return MagicMock(spec=EmailClient)


@pytest.fixture
def mock_calendar_client():
    return MagicMock(spec=CalDAVClient)


@pytest.fixture
def mock_github_client_instance():
    return MagicMock(spec=GitHubClient)


@pytest.fixture
def mock_config():
    return {
        'database_url': settings.database_url,
        'secret_key': 'test_secret_key',
        'email_host': 'test_email_host',
        'smtp_host': 'test_smtp_host',
        'email_username': 'test@example.com',
        'email_password': 'test_password',
        'caldav_url': 'test_caldav_url',
        'caldav_username': 'test_caldav_username',
        'caldav_password': 'test_caldav_password',
        'github_token': 'test_github_token',
    }


@pytest.fixture
def app(mock_db_manager, mock_auth_manager, mock_llm, mock_email_client, mock_calendar_client, mock_github_client, mock_config):
    from personal_ai_assistant.app import create_app
    app = create_app(
        db_manager=mock_db_manager,
        auth_manager=mock_auth_manager,
        llm=mock_llm,
        email_client=mock_email_client,
        calendar_client=mock_calendar_client,
        github_client=mock_github_client,
        config=mock_config
    )
    return app


@pytest.fixture
def test_calendar_event(db_manager, test_user):
    event = db_manager.create_calendar_event(
        user_id=test_user.id,
        title="Test Event",
        description="This is a test event",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1)
    )
    return event


@pytest.fixture
def test_email(db_manager, test_user):
    email = db_manager.create_email(
        user_id=test_user.id,
        subject="Test Email",
        body="This is a test email",
        sender="sender@example.com",
        recipient="recipient@example.com",
        timestamp=datetime.utcnow()
    )
    return email


@pytest.fixture
def test_task(db_manager, test_user):
    task = db_manager.create_task(
        user_id=test_user.id,
        title="Test Task",
        description="This is a test task",
        due_date=datetime.utcnow() + timedelta(days=1)
    )
    return task


@pytest.fixture
def test_user_preference(auth_manager, test_user):
    preference = auth_manager.create_user_preference(
        user_id=test_user.id,
        theme="dark",
        language="en"
    )
    return preference
