from imapclient import IMAPClient
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import email.utils
import datetime
import smtplib
import time
from typing import Callable
from personal_ai_assistant.llm.text_processor import TextProcessor

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

    def connect_imap(self):
        self.imap_client = IMAPClient(self.imap_host, use_uid=True, ssl=self.imap_use_ssl)
        self.imap_client.login(self.username, self.password)

    def connect_smtp(self):
        if self.smtp_use_tls:
            self.smtp_client = smtplib.SMTP(self.smtp_host, 587)
            self.smtp_client.starttls()
        else:
            self.smtp_client = smtplib.SMTP(self.smtp_host, 25)
        self.smtp_client.login(self.username, self.password)

    def disconnect(self):
        if self.imap_client:
            self.imap_client.logout()
        if self.smtp_client:
            self.smtp_client.quit()

    def fetch_emails(self, folder: str = 'INBOX', limit: int = 10) -> List[Dict[str, Any]]:
        if not self.imap_client:
            self.connect_imap()

        self.imap_client.select_folder(folder)
        messages = self.imap_client.search(['ALL'])
        emails = []

        for uid, message_data in self.imap_client.fetch(messages[-limit:], ['RFC822']).items():
            email_body = message_data[b'RFC822']
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
                'uid': uid,
                'subject': subject,
                'from': from_,
                'date': date,
                'content': content
            })

        return emails

    def _decode_header(self, header):
        decoded_header, encoding = decode_header(header)[0]
        if isinstance(decoded_header, bytes):
            return decoded_header.decode(encoding or 'utf-8')
        return decoded_header

    def fetch_new_emails(self, folder: str = 'INBOX', last_uid: int = 0) -> List[Dict[str, Any]]:
        if not self.imap_client:
            self.connect_imap()

        self.imap_client.select_folder(folder)
        messages = self.imap_client.search(['UID', f'{last_uid+1}:*'])
        emails = []

        for uid, message_data in self.imap_client.fetch(messages, ['RFC822']).items():
            email_body = message_data[b'RFC822']
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
                'uid': uid,
                'subject': subject,
                'from': from_,
                'date': date,
                'content': content
            })

        return emails

    def get_latest_uid(self, folder: str = 'INBOX') -> int:
        if not self.imap_client:
            self.connect_imap()

        self.imap_client.select_folder(folder)
        messages = self.imap_client.search(['ALL'])
        return max(messages) if messages else 0

    def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None):
        if not self.smtp_client:
            self.connect_smtp()

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

        self.smtp_client.send_message(msg, from_addr=self.username, to_addrs=recipients)

    def reply_to_email(self, original_uid: int, reply_body: str):
        if not self.imap_client:
            self.connect_imap()
        if not self.smtp_client:
            self.connect_smtp()

        self.imap_client.select_folder('INBOX')
        messages = self.imap_client.fetch([original_uid], ['RFC822'])
        original_email = message_from_bytes(messages[original_uid][b'RFC822'])

        reply_msg = MIMEMultipart()
        reply_msg['From'] = self.username
        reply_msg['To'] = original_email['From']
        reply_msg['Subject'] = f"Re: {original_email['Subject']}"
        reply_msg['In-Reply-To'] = original_email['Message-ID']
        reply_msg['References'] = original_email['Message-ID']

        reply_body = f"On {original_email['Date']}, {original_email['From']} wrote:\n\n" + \
                     "\n".join([f"> {line}" for line in original_email.get_payload(decode=True).decode().split('\n')]) + \
                     f"\n\n{reply_body}"

        reply_msg.attach(MIMEText(reply_body, 'plain'))

        self.smtp_client.send_message(reply_msg, from_addr=self.username, to_addrs=[original_email['From']])

    def forward_email(self, original_uid: int, forward_to: str, forward_body: str):
        if not self.imap_client:
            self.connect_imap()
        if not self.smtp_client:
            self.connect_smtp()

        self.imap_client.select_folder('INBOX')
        messages = self.imap_client.fetch([original_uid], ['RFC822'])
        original_email = message_from_bytes(messages[original_uid][b'RFC822'])

        forward_msg = MIMEMultipart()
        forward_msg['From'] = self.username
        forward_msg['To'] = forward_to
        forward_msg['Subject'] = f"Fwd: {original_email['Subject']}"

        forward_body = f"{forward_body}\n\n-------- Forwarded Message --------\n" + \
                       f"Subject: {original_email['Subject']}\n" + \
                       f"Date: {original_email['Date']}\n" + \
                       f"From: {original_email['From']}\n" + \
                       f"To: {original_email['To']}\n\n" + \
                       f"{original_email.get_payload(decode=True).decode()}"

        forward_msg.attach(MIMEText(forward_body, 'plain'))

        self.smtp_client.send_message(forward_msg, from_addr=self.username, to_addrs=[forward_to])

    def watch_for_new_emails(self, callback: Callable[[Dict[str, Any]], None], interval: int = 60):
        """
        Continuously watch for new emails and call the callback function for each new email.

        :param callback: A function that takes a single email dictionary as an argument
        :param interval: The interval in seconds between checks for new emails
        """
        if not self.imap_client:
            self.connect_imap()

        last_uid = self.get_latest_uid()

        while True:
            try:
                new_emails = self.fetch_new_emails(last_uid=last_uid)
                for email in new_emails:
                    callback(email)
                    last_uid = max(last_uid, email['uid'])

                time.sleep(interval)
            except Exception as e:
                print(f"Error while watching for new emails: {e}")
                # Reconnect and continue watching
                self.disconnect()
                self.connect_imap()

    def summarize_new_emails(self, folder: str = 'INBOX', last_uid: int = 0, max_length: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch new emails and summarize them using the LLM.

        :param folder: The email folder to check
        :param last_uid: The UID of the last processed email
        :param max_length: Maximum length of the summary in words
        :return: List of dictionaries containing email details and summaries
        """
        if not self.text_processor:
            raise ValueError("TextProcessor is not initialized. Please provide a TextProcessor instance.")

        new_emails = self.fetch_new_emails(folder, last_uid)
        summarized_emails = []

        for email in new_emails:
            summary = self.text_processor.summarize_text(email['content'], max_length)
            email['summary'] = summary
            summarized_emails.append(email)

        return summarized_emails

    def watch_for_new_emails_with_summary(self, callback: Callable[[Dict[str, Any]], None], interval: int = 60, max_length: int = 100):
        """
        Continuously watch for new emails, summarize them, and call the callback function for each new email.

        :param callback: A function that takes a single email dictionary (including summary) as an argument
        :param interval: The interval in seconds between checks for new emails
        :param max_length: Maximum length of the summary in words
        """
        if not self.imap_client:
            self.connect_imap()

        last_uid = self.get_latest_uid()

        while True:
            try:
                summarized_emails = self.summarize_new_emails(last_uid=last_uid, max_length=max_length)
                for email in summarized_emails:
                    callback(email)
                    last_uid = max(last_uid, email['uid'])

                time.sleep(interval)
            except Exception as e:
                print(f"Error while watching for new emails: {e}")
                # Reconnect and continue watching
                self.disconnect()
                self.connect_imap()
