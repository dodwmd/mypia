import pytest
from unittest.mock import AsyncMock, patch
from personal_ai_assistant.email.imap_client import EmailClient


@pytest.fixture
def email_client():
    return EmailClient("imap.example.com", "smtp.example.com", "user@example.com", "password")


@pytest.mark.asyncio
async def test_connect_imap(email_client):
    with patch('personal_ai_assistant.email.imap_client.aioimaplib.IMAP4_SSL') as mock_imap:
        mock_imap.return_value.wait_hello_from_server = AsyncMock()
        mock_imap.return_value.login = AsyncMock()

        await email_client.connect_imap()

        mock_imap.assert_called_once_with("imap.example.com")
        mock_imap.return_value.wait_hello_from_server.assert_called_once()
        mock_imap.return_value.login.assert_called_once_with("user@example.com", "password")


@pytest.mark.asyncio
async def test_fetch_emails(email_client):
    email_client.imap_client = AsyncMock()
    email_client.imap_client.select.return_value = (AsyncMock(), None)
    email_client.imap_client.search.return_value = (AsyncMock(), [b'1 2 3'])
    email_client.imap_client.fetch.return_value = {
        b'1': {b'RFC822': b'From: sender@example.com\r\nSubject: Test\r\n\r\nTest content'}
    }

    emails = await email_client.fetch_emails(limit=1)

    assert len(emails) == 1
    assert emails[0]['subject'] == 'Test'
    assert emails[0]['from'] == 'sender@example.com'


@pytest.mark.asyncio
async def test_send_email(email_client):
    email_client.smtp_client = AsyncMock()

    await email_client.send_email("recipient@example.com", "Test Subject", "Test Body")

    email_client.smtp_client.send_message.assert_called_once()
