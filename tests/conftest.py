import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from personal_ai_assistant.database.models import Base
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.github.github_client import GitHubClient
from pydantic import SecretStr

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def mock_db_engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def mock_db_session(mock_db_engine):
    Session = sessionmaker(bind=mock_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

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
    monkeypatch.setattr("personal_ai_assistant.llm.llama_cpp_interface.LlamaCppInterface", lambda *args, **kwargs: mock_llama)
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
    monkeypatch.setattr("personal_ai_assistant.calendar.caldav_client.CalDAVClient", lambda *args, **kwargs: mock_client)
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
        "database_url": "sqlite:///:memory:",
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

@pytest.fixture(autouse=True)
def mock_db_manager(mock_db_session, monkeypatch):
    mock_manager = Mock()
    mock_manager.Session.return_value = mock_db_session
    monkeypatch.setattr("personal_ai_assistant.database.db_manager.DatabaseManager", lambda *args, **kwargs: mock_manager)
    return mock_manager

@pytest.fixture
def mock_db_manager():
    return MagicMock(spec=DatabaseManager)

@pytest.fixture
def mock_auth_manager():
    return MagicMock(spec=AuthManager)

@pytest.fixture
def mock_llm():
    return MagicMock(spec=LlamaCppInterface)

@pytest.fixture
def mock_email_client():
    return MagicMock(spec=EmailClient)

@pytest.fixture
def mock_calendar_client():
    return MagicMock(spec=CalDAVClient)

@pytest.fixture
def mock_github_client():
    return MagicMock(spec=GitHubClient)

@pytest.fixture
def mock_config():
    return {
        'database_url': 'sqlite:///:memory:',
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
