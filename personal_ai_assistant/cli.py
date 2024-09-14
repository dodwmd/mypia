import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich import print as rprint
from personal_ai_assistant.config import settings
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import TaskManager, CalendarTask, EmailTask, WebLookupTask, GitHubPRReviewTask, GeneralInfoLookupTask
from personal_ai_assistant.web.scraper import WebContentProcessor
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.celery_app import app as celery_app
from personal_ai_assistant.tasks import check_and_process_new_emails, sync_calendar_events
from personal_ai_assistant.nlp.spacy_processor import SpacyProcessor
from personal_ai_assistant.utils.logging_config import setup_logging
from personal_ai_assistant.utils.exceptions import MyPIAException
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
import logging

# Set up logging
logger = setup_logging(log_level=logging.DEBUG if settings.debug else logging.INFO)

console = Console()

# Initialize components
llm = LlamaCppInterface(settings.llm_model_path)
text_processor = TextProcessor(llm)
embeddings = SentenceTransformerEmbeddings(settings.embedding_model)
chroma_db = ChromaDBManager(settings.chroma_db_path)
email_client = EmailClient(
    settings.email_host,
    settings.smtp_host,
    settings.email_username,
    settings.email_password.get_secret_value(),
    settings.email_use_ssl,
    settings.smtp_use_tls,
    text_processor=text_processor
)
caldav_client = CalDAVClient(
    settings.caldav_url,
    settings.caldav_username,
    settings.caldav_password.get_secret_value()
)
task_manager = TaskManager()
web_processor = WebContentProcessor(text_processor)
github_client = GitHubClient(settings.github_token.get_secret_value(), text_processor)
db_manager = DatabaseManager(settings.database_url.get_secret_value())
spacy_processor = SpacyProcessor()

@click.group()
def cli():
    """Personal AI Assistant CLI"""
    pass

# Wrap each command with error handling
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MyPIAException as e:
            logger.error(f"{type(e).__name__}: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        except Exception as e:
            logger.exception("An unexpected error occurred")
            console.print("[bold red]An unexpected error occurred. Please check the logs for more information.[/bold red]")
    return wrapper

# Apply error_handler to all commands
for command in cli.commands.values():
    command.callback = error_handler(command.callback)

@cli.command()
@click.argument('text')
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--format', type=click.Choice(['paragraph', 'bullet_points']), default='paragraph', help='Format of the summary')
def summarize(text: str, max_length: int, format: str):
    """Summarize the given text using the LLM"""
    with console.status("[bold green]Summarizing text..."):
        summary = text_processor.summarize_text(text, max_length, format)
    console.print(Panel(summary, title="Summary", expand=False))

@cli.command()
@click.argument('prompt')
@click.option('--max-tokens', default=100, help='Maximum number of tokens to generate')
@click.option('--temperature', default=0.7, help='Temperature for text generation')
def generate(prompt: str, max_tokens: int, temperature: float):
    """Generate text based on the given prompt"""
    with console.status("[bold green]Generating text..."):
        generated_text = text_processor.generate_text(prompt, max_tokens, temperature)
    console.print(Panel(generated_text, title="Generated Text", expand=False))

@cli.command()
@click.argument('context')
@click.argument('question')
@click.option('--max-tokens', default=100, help='Maximum number of tokens for the answer')
def answer(context: str, question: str, max_tokens: int):
    """Answer a question based on the given context"""
    with console.status("[bold green]Answering question..."):
        answer = text_processor.answer_question(context, question, max_tokens)
    console.print(Panel(f"Q: {question}\n\nA: {answer}", title="Question & Answer", expand=False))

@cli.command()
@click.argument('description')
@click.option('--num-tasks', default=3, help='Number of tasks to generate')
def tasks(description: str, num_tasks: int):
    """Generate tasks based on the given description"""
    with console.status("[bold green]Generating tasks..."):
        generated_tasks = text_processor.generate_tasks(description, num_tasks)
    
    task_tree = Tree("Generated Tasks")
    for i, task in enumerate(generated_tasks, 1):
        task_tree.add(f"Task {i}: {task}")
    console.print(task_tree)

@cli.command()
@click.argument('text')
def sentiment(text: str):
    """Analyze the sentiment of the given text"""
    with console.status("[bold green]Analyzing sentiment..."):
        sentiment_scores = text_processor.analyze_sentiment(text)
    
    table = Table(title="Sentiment Analysis")
    table.add_column("Sentiment", style="cyan")
    table.add_column("Score", style="magenta")
    for sentiment, score in sentiment_scores.items():
        table.add_row(sentiment.capitalize(), f"{score:.2f}")
    console.print(table)

@cli.command()
@click.argument('text')
def embed(text: str):
    """Generate embeddings for the given text"""
    with console.status("[bold green]Generating embeddings..."):
        embedding = embeddings.generate_embeddings(text)
    console.print(f"[bold green]Embedding (shape: {embedding.shape}):[/bold green]")
    console.print(embedding)

@cli.command()
@click.argument('text1')
@click.argument('text2')
def similarity(text1: str, text2: str):
    """Compute similarity between two texts"""
    with console.status("[bold green]Computing similarity..."):
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
    with console.status("[bold green]Querying vector database..."):
        results = chroma_db.query(collection_name, [query_text], n_results)
    
    table = Table(title=f"Query results from collection '{collection_name}'")
    table.add_column("Document", style="cyan")
    table.add_column("Metadata", style="magenta")
    table.add_column("Distance", style="green")

    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
        table.add_row(doc, str(metadata), f"{distance:.4f}")

    console.print(table)

@cli.command()
@click.argument('collection_name')
@click.argument('document')
@click.option('--metadata', type=click.STRING, help='JSON string of metadata')
@click.option('--id', type=click.STRING, help='Document ID')
def add_document_with_embedding(collection_name: str, document: str, metadata: str, id: str):
    """Add a document with its embedding to the vector database"""
    metadata_dict = json.loads(metadata) if metadata else {}
    with console.status("[bold green]Generating embedding..."):
        embedding = embeddings.generate_embeddings(document)
    chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata_dict], [id])
    console.print(f"[bold green]Document and embedding added to collection '{collection_name}'[/bold green]")

@cli.command()
@click.argument('collection_name')
@click.argument('query_text')
@click.option('--n-results', default=5, help='Number of results to return')
def query_db_with_embedding(collection_name: str, query_text: str, n_results: int):
    """Query the vector database using text embedding"""
    with console.status("[bold green]Generating query embedding..."):
        query_embedding = embeddings.generate_embeddings(query_text)
    with console.status("[bold green]Querying vector database..."):
        results = chroma_db.query_by_embeddings(collection_name, [query_embedding.tolist()], n_results)
    
    table = Table(title=f"Query results from collection '{collection_name}'")
    table.add_column("Document", style="cyan")
    table.add_column("Metadata", style="magenta")
    table.add_column("Distance", style="green")

    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1):
        table.add_row(doc, str(metadata), f"{distance:.4f}")

    console.print(table)

@cli.command()
@click.argument('collection_name')
@click.argument('id')
def get_embedding(collection_name: str, id: str):
    """Retrieve the embedding for a specific document"""
    with console.status("[bold green]Retrieving embedding..."):
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
    with console.status("[bold green]Generating new embedding..."):
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
    with console.status("[bold green]Fetching emails...") as status:
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
    with console.status("[bold green]Summarizing email..."):
        emails = asyncio.run(email_client.fetch_emails(limit=1000))  # Fetch more emails to ensure we find the right one
        email = next((e for e in emails if e['uid'] == uid), None)

        if email:
            summary = text_processor.summarize_text(email['content'], max_length=100)
            console.print(Panel(f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}\nSummary: {summary}", title=f"Email Summary (UID: {uid})", expand=False))
        else:
            console.print(f"[bold red]Email with UID {uid} not found.[/bold red]")

@cli.command()
@click.argument('uid', type=int)
@click.argument('collection_name')
def add_email_to_vectordb(uid: int, collection_name: str):
    """Add an email to the vector database"""
    with console.status("[bold green]Adding email to vector database..."):
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
    with console.status("[bold green]Ingesting emails into vector database..."):
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
    with console.status("[bold green]Ingesting new emails into vector database..."):
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
    with console.status("[bold green]Sending email..."):
        asyncio.run(email_client.send_email(to, subject, body, cc, bcc))
    console.print("[bold green]Email sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--body', required=True, help='Reply body')
def reply_to_email(original_uid: int, body: str):
    """Reply to an email"""
    with console.status("[bold green]Replying to email..."):
        asyncio.run(email_client.reply_to_email(original_uid, body))
    console.print("[bold green]Reply sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--to', required=True, help='Forward recipient email address')
@click.option('--body', required=True, help='Forward body')
def forward_email(original_uid: int, to: str, body: str):
    """Forward an email"""
    with console.status("[bold green]Forwarding email..."):
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
    with console.status("[bold green]Summarizing new emails..."):
        summarized_emails = asyncio.run(email_client.summarize_new_emails(last_uid=last_uid, max_length=max_length))
        
        for email in summarized_emails:
            console.print(Panel(f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}\nSummary: {email['summary']}", title=f"Email Summary (UID: {email['uid']})", expand=False))

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
    with console.status("[bold green]Listing calendars..."):
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
    with console.status("[bold green]Fetching events..."):
        events = asyncio.run(caldav_client.get_events(calendar_name, start, end))
    
    table = Table(title=f"Events in calendar '{calendar_name}'")
    table.add_column("Summary", style="cyan")
    table.add_column("Start", style="magenta")
    table.add_column("End", style="green")
    table.add_column("Description", style="yellow")

    for event in events:
        table.add_row(
            event['summary'],
            event['start'].strftime("%Y-%m-%d %H:%M:%S"),
            event['end'].strftime("%Y-%m-%d %H:%M:%S"),
            event['description']
        )

    console.print(table)

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
    with console.status("[bold green]Creating event..."):
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
    with console.status("[bold green]Updating event..."):
        event = asyncio.run(caldav_client.update_event(calendar_name, event_id, summary, start_dt, end_dt, description))
    console.print(f"[bold green]Event updated:[/bold green] {event['summary']}")

@cli.command()
@click.argument('calendar_name')
@click.argument('event_id')
def delete_event(calendar_name: str, event_id: str):
    """Delete an event from a calendar"""
    with console.status("[bold green]Deleting event..."):
        asyncio.run(caldav_client.delete_event(calendar_name, event_id))
    console.print(f"[bold green]Event deleted:[/bold green] {event_id}")

@cli.command()
@click.argument('calendar_name')
@click.argument('collection_name')
@click.option('--days', default=30, help='Number of days to fetch events for')
def ingest_past_events(calendar_name: str, collection_name: str, days: int):
    """Ingest past calendar events into the vector database"""
    with console.status("[bold green]Ingesting past events..."):
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
    with console.status("[bold green]Ingesting future events..."):
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
    with console.status("[bold green]Ingesting all events..."):
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
