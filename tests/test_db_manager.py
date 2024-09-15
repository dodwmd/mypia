import pytest
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.database.models import User
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def db_manager(mock_session):
    with patch('sqlalchemy.create_engine'):
        with patch('sqlalchemy.orm.sessionmaker') as mock_sessionmaker:
            mock_sessionmaker.return_value = lambda: mock_session
            return DatabaseManager('sqlite:///:memory:')


def test_create_user(db_manager, mock_session):
    username = 'testuser'
    email = 'test@example.com'
    password = 'password123'

    user_id = db_manager.create_user(username, email, password)

    assert user_id is not None
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_get_user_by_username(db_manager, mock_session):
    username = 'testuser'
    mock_user = User(id=1, username=username, email='test@example.com')
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    user = db_manager.get_user_by_username(username)

    assert user == mock_user
    mock_session.query.assert_called_once_with(User)


def test_get_user_by_id(db_manager, mock_session):
    user_id = 1
    mock_user = User(id=user_id, username='testuser', email='test@example.com')
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    user = db_manager.get_user_by_id(user_id)

    assert user == mock_user
    mock_session.query.assert_called_once_with(User)


def test_update_user_last_login(db_manager, mock_session):
    user_id = 1
    mock_user = User(id=user_id, username='testuser', email='test@example.com')
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    db_manager.update_user_last_login(user_id)

    assert mock_user.last_login is not None
    mock_session.commit.assert_called_once()
