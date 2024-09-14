import asyncio
from aioimaplib import aioimaplib
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import email.utils
import datetime
import aiosmtplib
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.utils.cache import cache

class EmailClient:
    def __init__(self, imap_host: str, smtp_host: str, username: str, password: str, imap_use_ssl: bool = True, smtp_use_tls: bool = True, text_processor: TextProcessor = None):
        self.imap_host = imap_host
        self.smtp_host = smtp_host
        self.username = username
        self.password = password
        self.imap_use_ssl = imap_use_ssl
        self.smtp_use_tls = smtp_use_tls
        self.imap_client = None
        self.smtp_client = None
        self.text_processor = text_processor

    async def connect_imap(self):
        self.imap_client = aioimaplib.IMAP4_SSL(self.imap_host) if self.imap_use_ssl else aioimaplib.IMAP4(self.imap_host)
        await self.imap_client.wait_hello_from_server()
        await self.imap_client.login(self.username, self.password)

    async def connect_smtp(self):
        self.smtp_client = aiosmtplib.SMTP(hostname=self.smtp_host, use_tls=self.smtp_use_tls)
        await self.smtp_client.connect()
        await self.smtp_client.login(self.username, self.password)

    async def disconnect(self):
        if self.imap_client:
            await self.imap_client.logout()
        if self.smtp_client:
            await self.smtp_client.quit()

    async def fetch_emails(self, folder: str = 'INBOX', limit: int = 10) -> List[Dict[str, Any]]:
        if not self.imap_client:
            await self.connect_imap()

        await self.imap_client.select(folder)
        _, messages = await self.imap_client.search('ALL')
        message_numbers = messages[0].split()
        emails = []

        for num in message_numbers[-limit:]:
            _, msg_data = await self.imap_client.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = message_from_bytes(email_body)
            
            subject = self._decode_header(email_message['Subject'])
            from_ = self._decode_header(email_message['From'])
            date = email.utils.parsedate_to_datetime(email_message['Date'])

            content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        content += part.get_payload(decode=True).decode()
            else:
                content = email_message.get_payload(decode=True).decode()

            emails.append({
                'uid': num.decode(),
                'subject': subject,
                'from': from_,
                'date': date,
                'content': content
            })

        return emails

    async def fetch_new_emails(self, last_processed_uid: str, folder: str = 'INBOX') -> List[Dict[str, Any]]:
        if not self.imap_client:
            await self.connect_imap()

        await self.imap_client.select(folder)
        _, messages = await self.imap_client.search('UID', f'{int(last_processed_uid)+1}:*')
        message_numbers = messages[0].split()
        emails = []

        for num in message_numbers:
            _, msg_data = await self.imap_client.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = message_from_bytes(email_body)
            
            subject = self._decode_header(email_message['Subject'])
            from_ = self._decode_header(email_message['From'])
            date = email.utils.parsedate_to_datetime(email_message['Date'])

            content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        content += part.get_payload(decode=True).decode()
            else:
                content = email_message.get_payload(decode=True).decode()

            emails.append({
                'uid': num.decode(),
                'subject': subject,
                'from': from_,
                'date': date,
                'content': content
            })

        return emails

    async def summarize_email(self, email: Dict[str, Any]) -> str:
        if self.text_processor:
            return await self.text_processor.generate_text(f"Summarize this email:\n{email['content']}")
        else:
            return "Email summarization not available."

    async def summarize_new_emails(self, last_processed_uid: str, max_length: int = 50, limit: int = 5) -> List[Dict[str, Any]]:
        new_emails = await self.fetch_new_emails(last_processed_uid)
        summarized_emails = []

        for email in new_emails[:limit]:
            summary = await self.summarize_email(email)
            summarized_emails.append({
                'uid': email['uid'],
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'],
                'summary': summary[:max_length]
            })

        return summarized_emails

    async def watch_for_new_emails(self, callback, interval: int = 60, folder: str = 'INBOX'):
        last_processed_uid = '0'

        while True:
            new_emails = await self.fetch_new_emails(last_processed_uid, folder)
            if new_emails:
                last_processed_uid = new_emails[-1]['uid']
                await callback(new_emails)
            await asyncio.sleep(interval)

    async def watch_emails_with_summary(self, callback, interval: int = 60, max_length: int = 50, folder: str = 'INBOX'):
        last_processed_uid = '0'

        while True:
            summarized_emails = await self.summarize_new_emails(last_processed_uid, max_length, limit=10)
            if summarized_emails:
                last_processed_uid = summarized_emails[-1]['uid']
                await callback(summarized_emails)
            await asyncio.sleep(interval)

    async def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None):
        if not self.smtp_client:
            await self.connect_smtp()

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc

        msg.attach(MIMEText(body, 'plain'))

        recipients = [to]
        if cc:
            recipients.extend(cc.split(','))
        if bcc:
            recipients.extend(bcc.split(','))

        await self.smtp_client.send_message(msg)

    async def reply_to_email(self, original_email_uid: str, body: str):
        if not self.imap_client:
            await self.connect_imap()

        _, msg_data = await self.imap_client.fetch(original_email_uid, '(RFC822)')
        email_body = msg_data[0][1]
        email_message = message_from_bytes(email_body)

        reply = MIMEMultipart()
        reply['From'] = self.username
        reply['To'] = email_message['From']
        reply['Subject'] = f"Re: {email_message['Subject']}"
        reply['In-Reply-To'] = email_message['Message-ID']
        reply['References'] = email_message['Message-ID']

        reply.attach(MIMEText(body, 'plain'))

        await self.send_email(reply['To'], reply['Subject'], reply.as_string())

    async def forward_email(self, original_email_uid: str, to: str, body: str):
        if not self.imap_client:
            await self.connect_imap()

        _, msg_data = await self.imap_client.fetch(original_email_uid, '(RFC822)')
        email_body = msg_data[0][1]
        email_message = message_from_bytes(email_body)

        forward = MIMEMultipart()
        forward['From'] = self.username
        forward['To'] = to
        forward['Subject'] = f"Fwd: {email_message['Subject']}"

        forward.attach(MIMEText(body, 'plain'))
        forward.attach(MIMEText(email_body.decode(), 'plain'))

        await self.send_email(forward['To'], forward['Subject'], forward.as_string())

    def _decode_header(self, header):
        decoded_header = ""
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_header += part.decode(encoding or 'utf-8')
            else:
                decoded_header += part
        return decoded_header
