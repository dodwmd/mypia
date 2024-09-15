from aioimaplib import aioimaplib
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import email.utils
import aiosmtplib


class EmailClient:
    def __init__(self, imap_host: str, smtp_host: str, username: str, password: str):
        self.imap_host = imap_host
        self.smtp_host = smtp_host
        self.username = username
        self.password = password

    async def fetch_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        imap_client = aioimaplib.IMAP4_SSL(self.imap_host)
        await imap_client.wait_hello_from_server()
        await imap_client.login(self.username, self.password)
        await imap_client.select('INBOX')
        _, message_numbers = await imap_client.search('ALL')
        message_numbers = message_numbers[0].split()
        emails = []
        for num in message_numbers[-limit:]:
            _, msg_data = await imap_client.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    sender = msg['From']
                    date = email.utils.parsedate_to_datetime(msg['Date'])
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    emails.append({
                        'subject': subject,
                        'from': sender,
                        'date': date,
                        'body': body,
                        'uid': num.decode()
                    })
        await imap_client.logout()
        return emails

    async def send_email(self, to: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        smtp = aiosmtplib.SMTP(hostname=self.smtp_host, port=587, use_tls=False)
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(self.username, self.password)
        await smtp.send_message(msg)
        await smtp.quit()

    async def fetch_new_emails(self, last_uid: int = 0) -> List[Dict[str, Any]]:
        imap_client = aioimaplib.IMAP4_SSL(self.imap_host)
        await imap_client.wait_hello_from_server()
        await imap_client.login(self.username, self.password)
        await imap_client.select('INBOX')
        _, message_numbers = await imap_client.search(f'UID {last_uid+1}:*')
        message_numbers = message_numbers[0].split()
        new_emails = []
        for num in message_numbers:
            _, msg_data = await imap_client.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    email_message = message_from_bytes(response_part[1])
                    subject, encoding = decode_header(email_message['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    sender = email_message['From']
                    date = email.utils.parsedate_to_datetime(email_message['Date'])
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    new_emails.append({
                        'subject': subject,
                        'from': sender,
                        'date': date,
                        'body': body,
                        'uid': int(num.decode())
                    })
        await imap_client.logout()
        return new_emails
