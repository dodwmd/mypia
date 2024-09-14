import click
from rich.console import Console
from personal_ai_assistant.config import settings
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import (
    TaskManager, CalendarTask, EmailTask, WebLookupTask, GitHubPRReviewTask, GeneralInfoLookupTask
)
from rich.table import Table
import json
import numpy as np
from datetime import datetime, timedelta
from personal_ai_assistant.web.scraper import WebScraper, WebContentProcessor
from personal_ai_assistant.github.github_client import GitHubClient
import asyncio

console = Console()
llm = LlamaCppInterface(settings.llm_model_path)
text_processor = TextProcessor(llm)
embeddings = SentenceTransformerEmbeddings(settings.embedding_model)
chroma_db = ChromaDBManager(settings.chroma_db_path)
email_client = EmailClient(
    settings.email_host,
    settings.smtp_host,
    settings.email_username,
    settings.email_password,
    settings.email_use_ssl,
    settings.smtp_use_tls,
    text_processor=text_processor
)
caldav_client = CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password)
task_manager = TaskManager()
web_processor = WebContentProcessor(text_processor)
github_client = GitHubClient(settings.github_token, text_processor)

@click.group()
def cli():
    """Personal AI Assistant CLI"""
    pass

@cli.command()
@click.argument('text')
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--format', type=click.Choice(['paragraph', 'bullet_points']), default='paragraph', help='Format of the summary')
def summarize(text: str, max_length: int, format: str):
    """Summarize the given text using the LLM"""
    summary = text_processor.summarize_text(text, max_length, format)
    console.print(f"[bold green]Summary:[/bold green]\n{summary}")

@cli.command()
@click.argument('prompt')
@click.option('--max-tokens', default=100, help='Maximum number of tokens to generate')
@click.option('--temperature', default=0.7, help='Temperature for text generation')
def generate(prompt: str, max_tokens: int, temperature: float):
    """Generate text based on the given prompt"""
    generated_text = text_processor.generate_text(prompt, max_tokens, temperature)
    console.print(f"[bold green]Generated Text:[/bold green]\n{generated_text}")

@cli.command()
@click.argument('context')
@click.argument('question')
@click.option('--max-tokens', default=100, help='Maximum number of tokens for the answer')
def answer(context: str, question: str, max_tokens: int):
    """Answer a question based on the given context"""
    answer = text_processor.answer_question(context, question, max_tokens)
    console.print(f"[bold green]Answer:[/bold green]\n{answer}")

@cli.command()
@click.argument('description')
@click.option('--num-tasks', default=3, help='Number of tasks to generate')
def tasks(description: str, num_tasks: int):
    """Generate tasks based on the given description"""
    generated_tasks = text_processor.generate_tasks(description, num_tasks)
    console.print("[bold green]Generated Tasks:[/bold green]")
    for i, task in enumerate(generated_tasks, 1):
        console.print(f"{i}. {task}")

@cli.command()
@click.argument('text')
def sentiment(text: str):
    """Analyze the sentiment of the given text"""
    sentiment_scores = text_processor.analyze_sentiment(text)
    console.print("[bold green]Sentiment Analysis:[/bold green]")
    for sentiment, score in sentiment_scores.items():
        console.print(f"{sentiment.capitalize()}: {score:.2f}")

@cli.command()
@click.argument('text')
def embed(text: str):
    """Generate embeddings for the given text"""
    embedding = embeddings.generate_embeddings(text)
    console.print(f"[bold green]Embedding (shape: {embedding.shape}):[/bold green]")
    console.print(embedding)

@cli.command()
@click.argument('text1')
@click.argument('text2')
def similarity(text1: str, text2: str):
    """Compute similarity between two texts"""
    similarity_score = embeddings.compute_similarity(text1, text2)
    console.print(f"[bold green]Similarity score:[/bold green] {similarity_score:.4f}")

@cli.command()
@click.argument('collection_name')
@click.argument('document')
@click.option('--metadata', type=click.STRING, help='JSON string of metadata')
@click.option('--id', type=click.STRING, help='Document ID')
def add_document(collection_name: str, document: str, metadata: str, id: str):
    """Add a document to the vector database"""
    metadata_dict = json.loads(metadata) if metadata else {}
    chroma_db.add_documents(collection_name, [document], [metadata_dict], [id])
    console.print(f"[bold green]Document added to collection '{collection_name}'[/bold green]")

@cli.command()
@click.argument('collection_name')
@click.argument('query_text')
@click.option('--n-results', default=5, help='Number of results to return')
def query_db(collection_name: str, query_text: str, n_results: int):
    """Query the vector database"""
    results = chroma_db.query(collection_name, [query_text], n_results)
    console.print(f"[bold green]Query results from collection '{collection_name}':[/bold green]")
    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
        console.print(f"{i}. Document: {doc}")
        console.print(f"   Metadata: {metadata}")
        console.print(f"   Distance: {distance}")
        console.print()

@cli.command()
@click.argument('collection_name')
@click.argument('document')
@click.option('--metadata', type=click.STRING, help='JSON string of metadata')
@click.option('--id', type=click.STRING, help='Document ID')
def add_document_with_embedding(collection_name: str, document: str, metadata: str, id: str):
    """Add a document with its embedding to the vector database"""
    metadata_dict = json.loads(metadata) if metadata else {}
    embedding = embeddings.generate_embeddings(document)
    chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata_dict], [id])
    console.print(f"[bold green]Document and embedding added to collection '{collection_name}'[/bold green]")

@cli.command()
@click.argument('collection_name')
@click.argument('query_text')
@click.option('--n-results', default=5, help='Number of results to return')
def query_db_with_embedding(collection_name: str, query_text: str, n_results: int):
    """Query the vector database using text embedding"""
    query_embedding = embeddings.generate_embeddings(query_text)
    results = chroma_db.query_by_embeddings(collection_name, [query_embedding.tolist()], n_results)
    console.print(f"[bold green]Query results from collection '{collection_name}':[/bold green]")
    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
        console.print(f"{i}. Document: {doc}")
        console.print(f"   Metadata: {metadata}")
        console.print(f"   Distance: {distance}")
        console.print()

@cli.command()
@click.argument('collection_name')
@click.argument('id')
def get_embedding(collection_name: str, id: str):
    """Retrieve the embedding for a specific document"""
    embedding = chroma_db.get_embeddings(collection_name, [id])[0]
    console.print(f"[bold green]Embedding for document '{id}' in collection '{collection_name}':[/bold green]")
    console.print(np.array(embedding))

@cli.command()
@click.argument('collection_name')
@click.argument('id')
@click.argument('document')
@click.option('--metadata', type=click.STRING, help='JSON string of metadata')
def update_document_embedding(collection_name: str, id: str, document: str, metadata: str):
    """Update the embedding for a specific document"""
    metadata_dict = json.loads(metadata) if metadata else None
    new_embedding = embeddings.generate_embeddings(document)
    chroma_db.update_embeddings(collection_name, [id], [new_embedding.tolist()], [document], [metadata_dict] if metadata_dict else None)
    console.print(f"[bold green]Updated embedding for document '{id}' in collection '{collection_name}'[/bold green]")

@cli.command()
@click.argument('collection_name')
@click.argument('id')
def delete_document_embedding(collection_name: str, id: str):
    """Delete a document and its embedding from the vector database"""
    chroma_db.delete_embeddings(collection_name, [id])
    console.print(f"[bold green]Deleted document '{id}' from collection '{collection_name}'[/bold green]")

@cli.command()
@click.option('--limit', default=10, help='Number of emails to fetch')
def fetch_emails(limit: int):
    """Fetch recent emails"""
    emails = asyncio.run(email_client.fetch_emails(limit=limit))
    table = Table(title=f"Recent {limit} Emails")
    table.add_column("UID", style="cyan")
    table.add_column("Subject", style="magenta")
    table.add_column("From", style="green")
    table.add_column("Date", style="yellow")

    for email in emails:
        table.add_row(
            str(email['uid']),
            email['subject'],
            email['from'],
            email['date'].strftime("%Y-%m-%d %H:%M:%S")
        )

    console.print(table)

@cli.command()
@click.argument('uid', type=int)
def summarize_email(uid: int):
    """Summarize a specific email"""
    emails = asyncio.run(email_client.fetch_emails(limit=1000))  # Fetch more emails to ensure we find the right one
    email = next((e for e in emails if e['uid'] == uid), None)

    if email:
        summary = text_processor.summarize_text(email['content'], max_length=100)
        console.print(f"[bold green]Email Summary (UID: {uid}):[/bold green]")
        console.print(f"Subject: {email['subject']}")
        console.print(f"From: {email['from']}")
        console.print(f"Date: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"Summary: {summary}")
    else:
        console.print(f"[bold red]Email with UID {uid} not found.[/bold red]")

@cli.command()
@click.argument('uid', type=int)
@click.argument('collection_name')
def add_email_to_vectordb(uid: int, collection_name: str):
    """Add an email to the vector database"""
    emails = asyncio.run(email_client.fetch_emails(limit=1000))  # Fetch more emails to ensure we find the right one
    email = next((e for e in emails if e['uid'] == uid), None)

    if email:
        document = f"Subject: {email['subject']}\n\nContent: {email['content']}"
        metadata = {
            'uid': email['uid'],
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'].isoformat()
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [str(uid)])
        console.print(f"[bold green]Email (UID: {uid}) added to collection '{collection_name}'[/bold green]")
    else:
        console.print(f"[bold red]Email with UID {uid} not found.[/bold red]")

@cli.command()
@click.argument('collection_name')
@click.option('--limit', default=10, help='Number of emails to ingest')
def ingest_emails(collection_name: str, limit: int):
    """Ingest emails into the vector database"""
    emails = asyncio.run(email_client.fetch_emails(limit=limit))
    for email in emails:
        document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
        metadata = {
            'uid': email['uid'],
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'].isoformat()
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [str(email['uid'])])
        console.print(f"[bold green]Email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")

@cli.command()
@click.argument('collection_name')
def ingest_new_emails(collection_name: str):
    """Ingest new emails into the vector database"""
    last_uid = chroma_db.get_latest_document_id(collection_name)
    new_emails = asyncio.run(email_client.fetch_new_emails(last_uid=int(last_uid) if last_uid else 0))
    
    for email in new_emails:
        document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
        metadata = {
            'uid': email['uid'],
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'].isoformat()
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [str(email['uid'])])
        console.print(f"[bold green]New email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")

    if not new_emails:
        console.print("[bold yellow]No new emails to ingest.[/bold yellow]")

@cli.command()
@click.option('--to', required=True, help='Recipient email address')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
@click.option('--cc', help='CC recipients (comma-separated)')
@click.option('--bcc', help='BCC recipients (comma-separated)')
def send_email(to: str, subject: str, body: str, cc: str = None, bcc: str = None):
    """Send an email"""
    asyncio.run(email_client.send_email(to, subject, body, cc, bcc))
    console.print("[bold green]Email sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--body', required=True, help='Reply body')
def reply_to_email(original_uid: int, body: str):
    """Reply to an email"""
    asyncio.run(email_client.reply_to_email(original_uid, body))
    console.print("[bold green]Reply sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--to', required=True, help='Forward recipient email address')
@click.option('--body', required=True, help='Forward body')
def forward_email(original_uid: int, to: str, body: str):
    """Forward an email"""
    asyncio.run(email_client.forward_email(original_uid, to, body))
    console.print("[bold green]Email forwarded successfully![/bold green]")

@cli.command()
@click.argument('collection_name')
@click.option('--interval', default=60, help='Interval in seconds between email checks')
def watch_emails(collection_name: str, interval: int):
    """Watch for new emails and ingest them into the vector database in real-time"""
    def ingest_email(email: Dict[str, Any]):
        document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nContent: {email['content']}"
        metadata = {
            'uid': email['uid'],
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'].isoformat()
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [str(email['uid'])])
        console.print(f"[bold green]New email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")

    console.print(f"[bold blue]Watching for new emails every {interval} seconds...[/bold blue]")
    console.print("[bold yellow]Press Ctrl+C to stop watching.[/bold yellow]")

    try:
        asyncio.run(email_client.watch_for_new_emails(ingest_email, interval))
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")

@cli.command()
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--limit', default=10, help='Number of new emails to summarize')
def summarize_new_emails(max_length: int, limit: int):
    """Summarize new emails"""
    last_uid = asyncio.run(email_client.get_latest_uid()) - limit  # Get the UID of the last 'limit' emails
    summarized_emails = asyncio.run(email_client.summarize_new_emails(last_uid=last_uid, max_length=max_length))
    
    for email in summarized_emails:
        console.print(f"[bold green]Email UID: {email['uid']}[/bold green]")
        console.print(f"Subject: {email['subject']}")
        console.print(f"From: {email['from']}")
        console.print(f"Date: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"Summary: {email['summary']}")
        console.print("---")

@cli.command()
@click.argument('collection_name')
@click.option('--interval', default=60, help='Interval in seconds between email checks')
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
def watch_emails_with_summary(collection_name: str, interval: int, max_length: int):
    """Watch for new emails, summarize them, and ingest them into the vector database in real-time"""
    def process_email(email: Dict[str, Any]):
        document = f"Subject: {email['subject']}\n\nFrom: {email['from']}\n\nSummary: {email['summary']}\n\nContent: {email['content']}"
        metadata = {
            'uid': email['uid'],
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'].isoformat(),
            'summary': email['summary']
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [str(email['uid'])])
        console.print(f"[bold green]New email (UID: {email['uid']}) summarized and ingested into collection '{collection_name}'[/bold green]")
        console.print(f"Summary: {email['summary']}")

    console.print(f"[bold blue]Watching for new emails every {interval} seconds...[/bold blue]")
    console.print("[bold yellow]Press Ctrl+C to stop watching.[/bold yellow]")

    try:
        asyncio.run(email_client.watch_for_new_emails_with_summary(process_email, interval, max_length))
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")

@cli.command()
def list_calendars():
    """List available calendars"""
    calendars = asyncio.run(caldav_client.get_calendars())
    for calendar in calendars:
        console.print(f"[bold green]Calendar:[/bold green] {calendar.name}")

@cli.command()
@click.argument('calendar_name')
@click.option('--days', default=7, help='Number of days to fetch events for')
def list_events(calendar_name: str, days: int):
    """List events in a calendar"""
    start = datetime.now()
    end = start + timedelta(days=days)
    events = asyncio.run(caldav_client.get_events(calendar_name, start, end))
    
    for event in events:
        console.print(f"[bold green]Event:[/bold green] {event['summary']}")
        console.print(f"Start: {event['start']}")
        console.print(f"End: {event['end']}")
        console.print(f"Description: {event['description']}")
        console.print("---")

@cli.command()
@click.argument('calendar_name')
@click.option('--summary', required=True, help='Event summary')
@click.option('--start', required=True, help='Event start time (YYYY-MM-DD HH:MM)')
@click.option('--end', required=True, help='Event end time (YYYY-MM-DD HH:MM)')
@click.option('--description', default='', help='Event description')
def create_event(calendar_name: str, summary: str, start: str, end: str, description: str):
    """Create a new event in a calendar"""
    start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")
    event = asyncio.run(caldav_client.create_event(calendar_name, summary, start_dt, end_dt, description))
    console.print(f"[bold green]Event created:[/bold green] {event['summary']}")

@cli.command()
@click.argument('calendar_name')
@click.argument('event_id')
@click.option('--summary', help='New event summary')
@click.option('--start', help='New event start time (YYYY-MM-DD HH:MM)')
@click.option('--end', help='New event end time (YYYY-MM-DD HH:MM)')
@click.option('--description', help='New event description')
def update_event(calendar_name: str, event_id: str, summary: str, start: str, end: str, description: str):
    """Update an existing event in a calendar"""
    start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M") if start else None
    end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M") if end else None
    event = asyncio.run(caldav_client.update_event(calendar_name, event_id, summary, start_dt, end_dt, description))
    console.print(f"[bold green]Event updated:[/bold green] {event['summary']}")

@cli.command()
@click.argument('calendar_name')
@click.argument('event_id')
def delete_event(calendar_name: str, event_id: str):
    """Delete an event from a calendar"""
    asyncio.run(caldav_client.delete_event(calendar_name, event_id))
    console.print(f"[bold green]Event deleted:[/bold green] {event_id}")

@cli.command()
@click.argument('calendar_name')
@click.argument('collection_name')
@click.option('--days', default=30, help='Number of days to fetch events for')
def ingest_past_events(calendar_name: str, collection_name: str, days: int):
    """Ingest past calendar events into the vector database"""
    past_events = asyncio.run(caldav_client.get_past_events(calendar_name, days))
    for event in past_events:
        document = f"Summary: {event['summary']}\nStart: {event['start']}\nEnd: {event['end']}\nDescription: {event['description']}\nLocation: {event['location']}\nAttendees: {', '.join(event['attendees'])}"
        metadata = {
            'id': event['id'],
            'summary': event['summary'],
            'start': event['start'].isoformat(),
            'end': event['end'].isoformat() if event['end'] else None,
            'type': 'past_event'
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [event['id']])
        console.print(f"[bold green]Past event ingested:[/bold green] {event['summary']}")

@cli.command()
@click.argument('calendar_name')
@click.argument('collection_name')
@click.option('--days', default=30, help='Number of days to fetch events for')
def ingest_future_events(calendar_name: str, collection_name: str, days: int):
    """Ingest future calendar events into the vector database"""
    future_events = asyncio.run(caldav_client.get_future_events(calendar_name, days))
    for event in future_events:
        document = f"Summary: {event['summary']}\nStart: {event['start']}\nEnd: {event['end']}\nDescription: {event['description']}\nLocation: {event['location']}\nAttendees: {', '.join(event['attendees'])}"
        metadata = {
            'id': event['id'],
            'summary': event['summary'],
            'start': event['start'].isoformat(),
            'end': event['end'].isoformat() if event['end'] else None,
            'type': 'future_event'
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [event['id']])
        console.print(f"[bold green]Future event ingested:[/bold green] {event['summary']}")

@cli.command()
@click.argument('calendar_name')
@click.argument('collection_name')
@click.option('--past-days', default=30, help='Number of past days to fetch events for')
@click.option('--future-days', default=30, help='Number of future days to fetch events for')
def ingest_all_events(calendar_name: str, collection_name: str, past_days: int, future_days: int):
    """Ingest all calendar events (past and future) into the vector database"""
    past_events = asyncio.run(caldav_client.get_past_events(calendar_name, past_days))
    future_events = asyncio.run(caldav_client.get_future_events(calendar_name, future_days))
    all_events = past_events + future_events

    for event in all_events:
        document = f"Summary: {event['summary']}\nStart: {event['start']}\nEnd: {event['end']}\nDescription: {event['description']}\nLocation: {event['location']}\nAttendees: {', '.join(event['attendees'])}"
        metadata = {
            'id': event['id'],
            'summary': event['summary'],
            'start': event['start'].isoformat(),
            'end': event['end'].isoformat() if event['end'] else None,
            'type': 'past_event' if event['start'] < datetime.now() else 'future_event'
        }
        embedding = embeddings.generate_embeddings(document)
        chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata], [event['id']])
        console.print(f"[bold green]Event ingested:[/bold green] {event['summary']}")

    console.print(f"[bold green]Ingested {len(all_events)} events into the vector database.[/bold green]")

@cli.group()
def task():
    """Task management commands"""
    pass

@task.command()
@click.option('--title', required=True, help='Task title')
@click.option('--description', default='', help='Task description')
@click.option('--start-time', required=True, help='Event start time (YYYY-MM-DD HH:MM)')
@click.option('--end-time', required=True, help='Event end time (YYYY-MM-DD HH:MM)')
@click.option('--location', default='', help='Event location')
def add_calendar_task(title: str, description: str, start_time: str, end_time: str, location: str):
    """Add a calendar task"""
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    task = CalendarTask(title, description, start, end, location, caldav_client)
    task_manager.add_task(task)
    console.print(f"[bold green]Calendar task added:[/bold green] {task.title}")

@task.command()
@click.option('--title', required=True, help='Task title')
@click.option('--description', default='', help='Task description')
@click.option('--recipient', required=True, help='Email recipient')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
def add_email_task(title: str, description: str, recipient: str, subject: str, body: str):
    """Add an email task"""
    task = EmailTask(title, description, recipient, subject, body, email_client)
    task_manager.add_task(task)
    console.print(f"[bold green]Email task added:[/bold green] {task.title}")

@task.command()
@click.option('--title', required=True, help='Task title')
@click.option('--description', default='', help='Task description')
@click.option('--url', required=True, help='URL to look up')
def add_web_lookup_task(title: str, description: str, url: str):
    """Add a web lookup task"""
    task = WebLookupTask(title, description, url, web_processor)
    task_manager.add_task(task)
    console.print(f"[bold green]Web lookup task added:[/bold green] {task.title}")

@task.command()
@click.option('--title', required=True, help='Task title')
@click.option('--description', default='', help='Task description')
@click.option('--pr-url', required=True, help='GitHub PR URL')
@click.option('--github-token', required=True, help='GitHub personal access token')
def add_github_pr_review_task(title: str, description: str, pr_url: str, github_token: str):
    """Add a GitHub PR review task"""
    task = GitHubPRReviewTask(title, description, pr_url, github_token, text_processor)
    task_manager.add_task(task)
    console.print(f"[bold green]GitHub PR review task added:[/bold green] {task.title}")

@task.command()
@click.option('--title', required=True, help='Task title')
@click.option('--description', default='', help='Task description')
@click.option('--query', required=True, help='Information query')
def add_general_info_lookup_task(title: str, description: str, query: str):
    """Add a general information lookup task"""
    task = GeneralInfoLookupTask(title, description, query, text_processor)
    task_manager.add_task(task)
    console.print(f"[bold green]General information lookup task added:[/bold green] {task.title}")

@task.command()
def list_tasks():
    """List all tasks"""
    tasks = task_manager.list_tasks()
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Created At", style="yellow")
    table.add_column("Completed At", style="blue")

    for task in tasks:
        table.add_row(
            task['id'],
            task['title'],
            task['__class__.__name__'],
            task['created_at'],
            task['completed_at'] or "Not completed"
        )

    console.print(table)

@task.command()
@click.argument('task_id')
def execute_task(task_id: str):
    """Execute a specific task"""
    result = asyncio.run(task_manager.execute_task(task_id))
    console.print(f"[bold green]Task executed:[/bold green] {result['message']}")

@task.command()
@click.argument('task_id')
def remove_task(task_id: str):
    """Remove a specific task"""
    task_manager.remove_task(task_id)
    console.print(f"[bold green]Task removed:[/bold green] {task_id}")

@cli.command()
@click.argument('url')
@click.option('--summarize', is_flag=True, help='Summarize the scraped content')
def scrape_web(url: str, summarize: bool):
    """Scrape content from a web page"""
    scraped_data = asyncio.run(WebScraper.scrape_url(url))
    if not scraped_data:
        console.print(f"[bold red]Failed to scrape content from {url}[/bold red]")
        return

    console.print(f"[bold green]Title:[/bold green] {scraped_data['title']}")
    console.print(f"[bold green]Author:[/bold green] {scraped_data['author']}")
    console.print(f"[bold green]Date:[/bold green] {scraped_data['date']}")
    
    if summarize:
        summary = text_processor.summarize_text(scraped_data['content'], max_length=200)
        console.print(f"[bold green]Summary:[/bold green] {summary}")
    else:
        console.print(f"[bold green]Content:[/bold green] {scraped_data['content'][:500]}...")

@cli.group()
def web():
    """Web content processing commands"""
    pass

@web.command()
@click.argument('url')
def process_url(url: str):
    """Process and analyze a web page"""
    result = asyncio.run(web_processor.process_url(url))
    if result['status'] == 'success':
        console.print(f"[bold green]Title:[/bold green] {result['title']}")
        console.print(f"[bold green]Author:[/bold green] {result['author']}")
        console.print(f"[bold green]Date:[/bold green] {result['date']}")
        console.print(f"[bold green]Summary:[/bold green] {result['summary']}")
        console.print(f"[bold green]Keywords:[/bold green] {', '.join(result['keywords'])}")
        console.print(f"[bold green]Sentiment:[/bold green] {result['sentiment']}")
    else:
        console.print(f"[bold red]Error:[/bold red] {result['message']}")

@web.command()
@click.argument('url1')
@click.argument('url2')
def compare_urls(url1: str, url2: str):
    """Compare two web pages"""
    result = asyncio.run(web_processor.compare_urls(url1, url2))
    if result['status'] == 'success':
        console.print(f"[bold green]URL 1:[/bold green] {result['url1']['url']}")
        console.print(f"[bold green]URL 2:[/bold green] {result['url2']['url']}")
        console.print(f"[bold green]Comparison:[/bold green] {result['comparison']}")
    else:
        console.print(f"[bold red]Error:[/bold red] {result['message']}")

@web.command()
@click.argument('topic')
@click.option('--num-urls', default=3, help='Number of URLs to analyze')
def analyze_topic(topic: str, num_urls: int):
    """Analyze a topic by processing multiple web pages"""
    result = asyncio.run(web_processor.analyze_topic(topic, num_urls))
    if result['status'] == 'success':
        console.print(f"[bold green]Topic:[/bold green] {result['topic']}")
        console.print(f"[bold green]Analysis:[/bold green] {result['analysis']}")
        console.print("[bold green]Sources:[/bold green]")
        for source in result['sources']:
            if source['status'] == 'success':
                console.print(f"  - {source['url']}")
    else:
        console.print(f"[bold red]Error:[/bold red] {result['message']}")

@cli.group()
def github():
    """GitHub operations"""
    pass

@github.command()
@click.argument('repo_name')
@click.argument('pr_number', type=int)
def review_pr(repo_name: str, pr_number: int):
    """Review a GitHub Pull Request"""
    result = asyncio.run(github_client.review_pr(repo_name, pr_number))
    if result['status'] == 'success':
        console.print(f"[bold green]{result['message']}[/bold green]")
        console.print(f"Review ID: {result['review_id']}")
        console.print("Comments:")
        for comment in result['comments']:
            console.print(comment)
    else:
        console.print(f"[bold red]Error: {result['message']}[/bold red]")

@github.command()
@click.argument('repo_name')
@click.argument('pr_number', type=int)
def get_pr_details(repo_name: str, pr_number: int):
    """Get details of a GitHub Pull Request"""
    details = asyncio.run(github_client.get_pr_details(repo_name, pr_number))
    console.print(f"[bold green]PR #{pr_number} in {repo_name}:[/bold green]")
    for key, value in details.items():
        console.print(f"{key}: {value}")

@github.command()
@click.argument('repo_name')
@click.option('--state', default='open', help='State of issues to fetch (open/closed/all)')
def list_issues(repo_name: str, state: str):
    """List issues in a GitHub repository"""
    issues = asyncio.run(github_client.get_repo_issues(repo_name, state))
    console.print(f"[bold green]Issues in {repo_name} ({state}):[/bold green]")
    for issue in issues:
        console.print(f"#{issue['number']} - {issue['title']} ({issue['state']})")

@github.command()
@click.argument('repo_name')
@click.option('--title', prompt=True, help='Issue title')
@click.option('--body', prompt=True, help='Issue body')
def create_issue(repo_name: str, title: str, body: str):
    """Create a new issue in a GitHub repository"""
    issue = asyncio.run(github_client.create_issue(repo_name, title, body))
    console.print(f"[bold green]Created issue #{issue['number']} in {repo_name}[/bold green]")
    console.print(f"Title: {issue['title']}")
    console.print(f"Body: {issue['body']}")

@github.command()
@click.argument('repo_name')
def repo_stats(repo_name: str):
    """Get statistics for a GitHub repository"""
    stats = asyncio.run(github_client.get_repo_stats(repo_name))
    console.print(f"[bold green]Stats for {repo_name}:[/bold green]")
    for key, value in stats.items():
        console.print(f"{key}: {value}")

@github.command()
@click.argument('repo_name')
@click.argument('pr_number', type=int)
def review_pr_with_fixes(repo_name: str, pr_number: int):
    """Review a GitHub Pull Request, parse action logs, and suggest fixes"""
    review_result = asyncio.run(github_client.review_pr(repo_name, pr_number))
    action_logs = asyncio.run(github_client.parse_action_logs(repo_name, pr_number))
    suggested_fixes = asyncio.run(github_client.suggest_fixes(repo_name, pr_number))
    
    console.print(f"[bold green]PR Review for {repo_name}#{pr_number}:[/bold green]")
    console.print(f"Review ID: {review_result['review_id']}")
    console.print("Comments:")
    for comment in review_result['comments']:
        console.print(comment)
    
    console.print("\n[bold green]Action Logs:[/bold green]")
    for log in action_logs['logs']:
        console.print(f"Name: {log['name']}")
        console.print(f"Conclusion: {log['conclusion']}")
        console.print(f"Summary: {log['summary']}")
        console.print("---")
    
    console.print("\n[bold green]Suggested Fixes:[/bold green]")
    for fix in suggested_fixes['suggestions']:
        console.print(f"File: {fix['file']}")
        console.print(f"Suggestion: {fix['suggestion']}")
        console.print("---")

@github.command()
@click.argument('repo_name')
@click.argument('pr_number', type=int)
def review_pr_with_automation(repo_name: str, pr_number: int):
    """Review a GitHub Pull Request with automated updates and responses"""
    result = asyncio.run(github_client.review_pr(repo_name, pr_number))
    action_logs = asyncio.run(github_client.parse_action_logs(repo_name, pr_number))
    suggested_fixes = asyncio.run(github_client.suggest_fixes(repo_name, pr_number))
    auto_update_result = asyncio.run(github_client.auto_update_pr(repo_name, pr_number))
    auto_respond_result = asyncio.run(github_client.auto_respond_to_pr_comments(repo_name, pr_number))
    
    console.print(f"[bold green]PR Review and Automation for {repo_name}#{pr_number}:[/bold green]")
    console.print(f"Review ID: {result['review_id']}")
    console.print("Comments:")
    for comment in result['comments']:
        console.print(comment)
    
    console.print("\n[bold green]Action Logs:[/bold green]")
    for log in action_logs['logs']:
        console.print(f"Name: {log['name']}")
        console.print(f"Conclusion: {log['conclusion']}")
        console.print(f"Summary: {log['summary']}")
        console.print("---")
    
    console.print("\n[bold green]Suggested Fixes:[/bold green]")
    for fix in suggested_fixes['suggestions']:
        console.print(f"File: {fix['file']}")
        console.print(f"Suggestion: {fix['suggestion']}")
        console.print("---")
    
    console.print("\n[bold green]Automated Updates:[/bold green]")
    console.print(f"Updated files: {', '.join(auto_update_result['updated_files'])}")
    
    console.print("\n[bold green]Automated Responses:[/bold green]")
    for response in auto_respond_result['responses']:
        console.print(f"Original comment: {response['original']}")
        console.print(f"Response: {response['response']}")
        console.print("---")

if __name__ == "__main__":
    cli()
