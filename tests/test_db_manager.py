import pytest
from unittest.mock import MagicMock, patch
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.database.models import User, Task, UserPreference

@pytest.fixture
def db_manager():
    with patch('personal_ai_assistant.database.db_manager.init_db') as mock_init_db:
        mock_init_db.return_value = MagicMock()
        return DatabaseManager('sqlite:///:memory:')

def test_create_user(db_manager):
    with patch.object(db_manager, 'Session') as mock_session:
        mock_session.return_value.__enter__.return_value.add = MagicMock()
        mock_session.return_value.__enter__.return_value.commit = MagicMock()
        
        user_id = db_manager.create_user("testuser", "test@example.com", "password123")
        
        assert user_id is not None
        mock_session.return_value.__enter__.return_value.add.assert_called_once()
        mock_session.return_value.__enter__.return_value.commit.assert_called_once()

def test_get_user(db_manager):
    with patch.object(db_manager, 'Session') as mock_session:
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_user
        
        user = db_manager.get_user(1)
        
        assert user.id == 1
        assert user.username == "testuser"

def test_create_task(db_manager):
    with patch.object(db_manager, 'Session') as mock_session:
        mock_session.return_value.__enter__.return_value.add = MagicMock()
        mock_session.return_value.__enter__.return_value.commit = MagicMock()
        
        task_id = db_manager.create_task(1, "Test Task", "This is a test task")
        
        assert task_id is not None
        mock_session.return_value.__enter__.return_value.add.assert_called_once()
        mock_session.return_value.__enter__.return_value.commit.assert_called_once()

def test_set_user_preference(db_manager):
    with patch.object(db_manager, 'Session') as mock_session:
        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = None
        mock_session.return_value.__enter__.return_value.add = MagicMock()
        mock_session.return_value.__enter__.return_value.commit = MagicMock()
        
        result = db_manager.set_user_preference(1, "theme", "dark")
        
        assert result is True
        mock_session.return_value.__enter__.return_value.add.assert_called_once()
        mock_session.return_value.__enter__.return_value.commit.assert_called_once()
