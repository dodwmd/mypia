import pytest
from unittest.mock import patch
from personal_ai_assistant.cli import cli
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_db_manager():
    with patch('personal_ai_assistant.database.db_manager.DatabaseManager') as mock:
        yield mock


@pytest.fixture
def mock_auth_manager():
    with patch('personal_ai_assistant.auth.auth_manager.AuthManager') as mock:
        yield mock


@pytest.fixture
def mock_email_client():
    with patch('personal_ai_assistant.email.imap_client.EmailClient') as mock:
        yield mock


@pytest.fixture
def mock_calendar_client():
    with patch('personal_ai_assistant.calendar.caldav_client.CalDAVClient') as mock:
        yield mock


@pytest.fixture
def mock_github_client():
    with patch('personal_ai_assistant.github.github_client.GitHubClient') as mock:
        yield mock


def test_cli_help(runner):
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_login(runner, mock_auth_manager):
    mock_auth_manager.return_value.authenticate_user.return_value = True
    result = runner.invoke(cli, ['login'], input='testuser\npassword\n')
    assert result.exit_code == 0
    assert 'Login successful' in result.output


def test_login_failure(runner, mock_auth_manager):
    mock_auth_manager.return_value.authenticate_user.return_value = False
    result = runner.invoke(cli, ['login'], input='testuser\nwrongpassword\n')
    assert result.exit_code != 0
    assert 'Login failed' in result.output


def test_process_emails(runner, mock_email_client, mock_db_manager):
    mock_email_client.return_value.fetch_new_emails.return_value = [
        {'subject': 'Test Email', 'from': 'sender@example.com', 'body': 'Test content'}
    ]
    result = runner.invoke(cli, ['process-emails'])
    assert result.exit_code == 0
    assert 'Processed 1 new emails' in result.output


def test_create_task(runner, mock_db_manager):
    result = runner.invoke(cli, ['create-task'], input='Test Task\nTask description\n2023-12-31\n')
    assert result.exit_code == 0
    assert 'Task created successfully' in result.output


def test_list_tasks(runner, mock_db_manager):
    mock_db_manager.return_value.get_all_tasks.return_value = [
        {'id': 1, 'title': 'Test Task', 'description': 'Task description', 'due_date': '2023-12-31'}
    ]
    result = runner.invoke(cli, ['list-tasks'])
    assert result.exit_code == 0
    assert 'Test Task' in result.output


def test_github_pr_review(runner, mock_github_client):
    mock_github_client.return_value.review_pr.return_value = {'status': 'success', 'comments': ['Good job!']}
    result = runner.invoke(cli, ['github', 'review-pr', 'test-repo', '1'])
    assert result.exit_code == 0
    assert 'PR review completed' in result.output


def test_summarize_text(runner, mock_llm):
    result = runner.invoke(cli, ['summarize'], input='This is a long text that needs summarization.\n')
    assert result.exit_code == 0
    assert 'Summarized text' in result.output


if __name__ == '__main__':
    pytest.main()
