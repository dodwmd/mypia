import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from typing import Dict, Any
import json
from personal_ai_assistant.config import settings
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import TaskManager
from personal_ai_assistant.web.scraper import WebScraper
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.nlp.spacy_processor import SpacyProcessor
from personal_ai_assistant.utils.logging_config import setup_logging
from personal_ai_assistant.utils.exceptions import MyPIAException
from personal_ai_assistant.utils.cache import invalidate_cache
from personal_ai_assistant.utils.profiling import cpu_profile, memory_profile_decorator
from personal_ai_assistant.updater.update_manager import UpdateManager
from personal_ai_assistant.utils.backup_manager import BackupManager
from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.utils.encryption import EncryptionManager
import asyncio
import numpy as np
import logging
import os
from huggingface_hub import hf_hub_download
import secrets

# Set up logging
logger = setup_logging(log_level=logging.DEBUG if settings.debug else logging.INFO)

console = Console()

# Initialize components
db_manager = DatabaseManager(settings.database_url)
if settings.encryption_key:
    encryption_manager = EncryptionManager(settings.encryption_key.get_secret_value())
else:
    # Generate a random key if not provided
    random_key = secrets.token_bytes(32)
    encryption_manager = EncryptionManager(random_key)
auth_manager = AuthManager(db_manager, encryption_manager)
llm = LlamaCppInterface(settings.llm_model_path, db_manager=db_manager)
embedding_model = SentenceTransformerEmbeddings(settings.embedding_model)
chroma_db = ChromaDBManager(settings.chroma_db_path)
email_client = EmailClient(settings.email_host, settings.smtp_host, settings.email_username, settings.email_password.get_secret_value())
caldav_client = CalDAVClient(settings.caldav_url, settings.caldav_username, settings.caldav_password.get_secret_value())
task_manager = TaskManager()
web_processor = WebScraper()
github_client = GitHubClient(settings.github_token.get_secret_value())
spacy_processor = SpacyProcessor()


def ensure_model_exists(model_path, repo_id, filename, cache_dir):
    """Ensure the model file exists, downloading it if necessary."""
    if not os.path.exists(model_path):
        logger.info(f"Model file not found at {model_path}. Downloading...")
        try:
            os.makedirs(cache_dir, exist_ok=True)
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir,
                local_dir=cache_dir,
                local_dir_use_symlinks=False
            )
            logger.info(f"Model downloaded successfully to: {downloaded_path}")
            return downloaded_path
        except Exception as e:
            logger.error(f"Error downloading model: {str(e)}")
            return None
    else:
        logger.info(f"Model file found at {model_path}.")
        return model_path


@click.group()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--offline', is_flag=True, help="Run in offline mode")
@click.option('--profile', type=click.Choice(['cpu', 'memory', 'none']), default='none', help='Enable profiling')
@click.option('--profile-output', type=click.Path(), help='Output file for profiling results')
@click.pass_context
def cli(ctx, username, password, offline, profile, profile_output):
    """Personal AI Assistant CLI"""
    if not auth_manager.authenticate_user(username, password):
        console.print("[bold red]Authentication failed[/bold red]")
        ctx.abort()
    ctx.ensure_object(dict)
    ctx.obj['username'] = username
    ctx.obj['offline'] = offline
    ctx.obj['profile'] = profile
    ctx.obj['profile_output'] = profile_output
    ctx.obj['llm'] = llm


def profile_command(func):
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        if ctx.obj['profile'] == 'cpu':
            cpu_profile(ctx.obj['profile_output'])(func)(*args, **kwargs)
        elif ctx.obj['profile'] == 'memory':
            memory_profile_decorator(ctx.obj['profile_output'])(func)(*args, **kwargs)
        else:
            func(*args, **kwargs)
    return wrapper


# Wrap each command with error handling
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MyPIAException as e:
            logger.error(f"{type(e).__name__}: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        except Exception as e: # noqa: E261 F841
            logger.exception("An unexpected error occurred")
            console.print("[bold red]An unexpected error occurred. Please check the logs for more information.[/bold red]")
    return wrapper


# Apply error_handler to all commands
for command in cli.commands.values():
    command.callback = error_handler(command.callback)


@cli.command()
@click.pass_context
def user_info(ctx):
    """Display user information"""
    user = db_manager.get_user_by_username(ctx.obj['username'])
    console.print(f"Username: {user.username}")
    console.print(f"Email: {user.email}")
    console.print(f"Last login: {user.last_login}")


@cli.command()
@click.argument('text')
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--format', type=click.Choice(['paragraph', 'bullet_points']), default='paragraph', help='Format of the summary')
@profile_command
def summarize(ctx, text: str, max_length: int, format: str):
    """Summarize the given text using the LLM"""
    if ctx.obj['offline']:
        cached_summary = db_manager.get_cached_data(f"summary_{text}_{max_length}_{format}")
        if cached_summary:
            console.print(cached_summary)
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached summary found.[/yellow]")

    with console.status("[bold green]Summarizing text..."):
        summary = text_processor.summarize_text(text, max_length, format)
    db_manager.cache_data(f"summary_{text}_{max_length}_{format}", summary)
    console.print(Panel(summary, title="Summary", expand=False))


@cli.command()
@click.argument('prompt')
@click.option('--max-tokens', default=100, help='Maximum number of tokens to generate')
@click.option('--temperature', default=0.7, help='Temperature for text generation')
@profile_command
def generate(ctx, prompt: str, max_tokens: int, temperature: float):
    """Generate text based on the given prompt"""
    if ctx.obj['offline']:
        cached_generated_text = db_manager.get_cached_data(f"generate_{prompt}_{max_tokens}_{temperature}")
        if cached_generated_text:
            console.print(cached_generated_text)
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached generated text found.[/yellow]")

    with console.status("[bold green]Generating text..."):
        generated_text = text_processor.generate_text(prompt, max_tokens, temperature)
    db_manager.cache_data(f"generate_{prompt}_{max_tokens}_{temperature}", generated_text)
    console.print(Panel(generated_text, title="Generated Text", expand=False))


@cli.command()
@click.argument('context')
@click.argument('question')
@click.option('--max-tokens', default=100, help='Maximum number of tokens for the answer')
@profile_command
def answer(ctx, context: str, question: str, max_tokens: int):
    """Answer a question based on the given context"""
    if ctx.obj['offline']:
        cached_answer = db_manager.get_cached_data(f"answer_{context}_{question}_{max_tokens}")
        if cached_answer:
            console.print(cached_answer)
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached answer found.[/yellow]")

    with console.status("[bold green]Answering question..."):
        answer = text_processor.answer_question(context, question, max_tokens)
    db_manager.cache_data(f"answer_{context}_{question}_{max_tokens}", answer)
    console.print(Panel(f"Q: {question}\n\nA: {answer}", title="Question & Answer", expand=False))


@cli.command()
@click.argument('description')
@click.option('--num-tasks', default=3, help='Number of tasks to generate')
@profile_command
def tasks(ctx, description: str, num_tasks: int):
    """Generate tasks based on the given description"""
    if ctx.obj['offline']:
        cached_tasks = db_manager.get_cached_data(f"tasks_{description}_{num_tasks}")
        if cached_tasks:
            task_tree = Tree("Generated Tasks")
            for i, task in enumerate(cached_tasks, 1):
                task_tree.add(f"Task {i}: {task}")
            console.print(task_tree)
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached tasks found.[/yellow]")

    with console.status("[bold green]Generating tasks..."):
        generated_tasks = text_processor.generate_tasks(description, num_tasks)
    db_manager.cache_data(f"tasks_{description}_{num_tasks}", generated_tasks)

    task_tree = Tree("Generated Tasks")
    for i, task in enumerate(generated_tasks, 1):
        task_tree.add(f"Task {i}: {task}")
    console.print(task_tree)


@cli.command()
@click.argument('text')
@profile_command
def sentiment(ctx, text: str):
    """Analyze the sentiment of the given text"""
    if ctx.obj['offline']:
        cached_sentiment_scores = db_manager.get_cached_data(f"sentiment_{text}")
        if cached_sentiment_scores:
            table = Table(title="Sentiment Analysis")
            table.add_column("Sentiment", style="cyan")
            table.add_column("Score", style="magenta")
            for sentiment, score in cached_sentiment_scores.items():
                table.add_row(sentiment.capitalize(), f"{score:.2f}")
            console.print(table)
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached sentiment scores found.[/yellow]")

    with console.status("[bold green]Analyzing sentiment..."):
        sentiment_scores = text_processor.analyze_sentiment(text)
    db_manager.cache_data(f"sentiment_{text}", sentiment_scores)

    table = Table(title="Sentiment Analysis")
    table.add_column("Sentiment", style="cyan")
    table.add_column("Score", style="magenta")
    for sentiment, score in sentiment_scores.items():
        table.add_row(sentiment.capitalize(), f"{score:.2f}")
    console.print(table)


@cli.command()
@click.argument('text')
@profile_command
def embed(ctx, text: str):
    """Generate embeddings for the given text"""
    if ctx.obj['offline']:
        cached_embedding = db_manager.get_cached_data(f"embedding_{text}")
        if cached_embedding:
            console.print(f"[bold green]Embedding (shape: {np.array(cached_embedding).shape}):[/bold green]")
            console.print(np.array(cached_embedding))
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached embedding found.[/yellow]")

    with console.status("[bold green]Generating embeddings..."):
        embedding = embeddings.generate_embeddings(text)
    db_manager.cache_data(f"embedding_{text}", embedding.tolist())
    console.print(f"[bold green]Embedding (shape: {embedding.shape}):[/bold green]")
    console.print(embedding)


@cli.command()
@click.argument('text1')
@click.argument('text2')
@profile_command
def similarity(ctx, text1: str, text2: str):
    """Compute similarity between two texts"""
    if ctx.obj['offline']:
        cached_similarity_score = db_manager.get_cached_data(f"similarity_{text1}_{text2}")
        if cached_similarity_score:
            console.print(f"[bold green]Similarity score:[/bold green] {cached_similarity_score:.4f}")
            return
        else:
            console.print("[yellow]Warning: Running in offline mode, but no cached similarity score found.[/yellow]")


@click.group()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--offline', is_flag=True, help="Run in offline mode")
@click.option('--profile', type=click.Choice(['cpu', 'memory', 'none']), default='none', help='Enable profiling')
@click.option('--profile-output', type=click.Path(), help='Output file for profiling results')
@click.pass_context
def cli(ctx, username, password, offline, profile, profile_output):
    """Personal AI Assistant CLI"""
    if not auth_manager.authenticate_user(username, password):
        console.print("[bold red]Authentication failed[/bold red]")
        ctx.abort()
    ctx.ensure_object(dict)
    ctx.obj['username'] = username
    ctx.obj['offline'] = offline
    ctx.obj['profile'] = profile
    ctx.obj['profile_output'] = profile_output
    ctx.obj['llm'] = llm


def profile_command(func):
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        if ctx.obj['profile'] == 'cpu':
            cpu_profile(ctx.obj['profile_output'])(func)(*args, **kwargs)
        elif ctx.obj['profile'] == 'memory':
            memory_profile_decorator(ctx.obj['profile_output'])(func)(*args, **kwargs)
        else:
            func(*args, **kwargs)
    return wrapper


# Wrap each command with error handling
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MyPIAException as e:
            logger.error(f"{type(e).__name__}: {str(e)}")
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        except Exception as e: # noqa: F841 E261
            logger.exception("An unexpected error occurred")
            console.print("[bold red]An unexpected error occurred. Please check the logs for more information.[/bold red]")
    return wrapper


def add_document(ctx, collection_name: str, document: str, metadata: str, id: str):
    """Add a document to the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but adding documents is not supported.[/yellow]")
        return

    metadata_dict = json.loads(metadata) if metadata else {}
    chroma_db.add_documents(collection_name, [document], [metadata_dict], [id])
    console.print(f"[bold green]Document added to collection '{collection_name}'[/bold green]")


@cli.command()
@click.argument('collection_name')
@click.argument('query_text')
@click.option('--n-results', default=5, help='Number of results to return')
@profile_command
def query_db(ctx, collection_name: str, query_text: str, n_results: int):
    """Query the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but querying the database is not supported.[/yellow]")
        return

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
@profile_command
def add_document_with_embedding(ctx, collection_name: str, document: str, metadata: str, id: str):
    """Add a document with its embedding to the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but adding documents is not supported.[/yellow]")
        return

    metadata_dict = json.loads(metadata) if metadata else {}
    with console.status("[bold green]Generating embedding..."):
        embedding = embeddings.generate_embeddings(document)
    chroma_db.add_embeddings(collection_name, [embedding.tolist()], [document], [metadata_dict], [id])
    console.print(f"[bold green]Document and embedding added to collection '{collection_name}'[/bold green]")


@cli.command()
@click.argument('collection_name')
@click.argument('query_text')
@click.option('--n-results', default=5, help='Number of results to return')
@profile_command
def query_db_with_embedding(ctx, collection_name: str, query_text: str, n_results: int):
    """Query the vector database using text embedding"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but querying the database is not supported.[/yellow]")
        return

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
@profile_command
def get_embedding(ctx, collection_name: str, id: str):
    """Retrieve the embedding for a specific document"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but retrieving embeddings is not supported.[/yellow]")
        return

    with console.status("[bold green]Retrieving embedding..."):
        embedding = chroma_db.get_embeddings(collection_name, [id])[0]
    console.print(f"[bold green]Embedding for document '{id}' in collection '{collection_name}':[/bold green]")
    console.print(np.array(embedding))


@cli.command()
@click.argument('collection_name')
@click.argument('id')
@click.argument('document')
@click.option('--metadata', type=click.STRING, help='JSON string of metadata')
@profile_command
def update_document_embedding(ctx, collection_name: str, id: str, document: str, metadata: str):
    """Update the embedding for a specific document"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but updating embeddings is not supported.[/yellow]")
        return

    metadata_dict = json.loads(metadata) if metadata else None
    with console.status("[bold green]Generating new embedding..."):
        new_embedding = embeddings.generate_embeddings(document)
    chroma_db.update_embeddings(collection_name, [id], [new_embedding.tolist()], [
                                document], [metadata_dict] if metadata_dict else None)
    console.print(f"[bold green]Updated embedding for document '{id}' in collection '{collection_name}'[/bold green]")


@cli.command()
@click.argument('collection_name')
@click.argument('id')
@profile_command
def delete_document_embedding(ctx, collection_name: str, id: str):
    """Delete a document and its embedding from the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but deleting documents is not supported.[/yellow]")
        return

    chroma_db.delete_embeddings(collection_name, [id])
    console.print(f"[bold green]Deleted document '{id}' from collection '{collection_name}'[/bold green]")


@cli.command()
@click.option('--limit', default=10, help='Number of emails to fetch')
@profile_command
def fetch_emails(ctx, limit: int):
    """Fetch recent emails"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but fetching emails is not supported.[/yellow]")
        return

    with console.status("[bold green]Fetching emails...") as status:  # noqa: F841
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
@profile_command
def summarize_email(ctx, uid: int):
    """Summarize a specific email"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but summarizing emails is not supported.[/yellow]")
        return

    with console.status("[bold green]Summarizing email..."):
        emails = asyncio.run(email_client.fetch_emails(limit=1000))  # Fetch more emails to ensure we find the right one
        email = next((e for e in emails if e['uid'] == uid), None)

        if email:
            summary = text_processor.summarize_text(email['content'], max_length=100)
            console.print(Panel(
                f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}\nSummary: {summary}", title=f"Email Summary (UID: {uid})", expand=False))
        else:
            console.print(f"[bold red]Email with UID {uid} not found.[/bold red]")


@cli.command()
@click.argument('uid', type=int)
@click.argument('collection_name')
@profile_command
def add_email_to_vectordb(ctx, uid: int, collection_name: str):
    """Add an email to the vector database"""
    if ctx.obj['offline']:
        console.print(
            "[yellow]Warning: Running in offline mode, but adding emails to the vector database is not supported.[/yellow]")
        return

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
@profile_command
def ingest_emails(ctx, collection_name: str, limit: int):
    """Ingest emails into the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but ingesting emails is not supported.[/yellow]")
        return

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
            console.print(
                f"[bold green]Email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")


@cli.command()
@click.argument('collection_name')
@profile_command
def ingest_new_emails(ctx, collection_name: str):
    """Ingest new emails into the vector database"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but ingesting new emails is not supported.[/yellow]")
        return

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
            console.print(
                f"[bold green]New email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")

        if not new_emails:
            console.print("[bold yellow]No new emails to ingest.[/bold yellow]")


@cli.command()
@click.option('--to', required=True, help='Recipient email address')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
@click.option('--cc', help='CC recipients (comma-separated)')
@click.option('--bcc', help='BCC recipients (comma-separated)')
@profile_command
def send_email(ctx, to: str, subject: str, body: str, cc: str = None, bcc: str = None):
    """Send an email"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but sending emails is not supported.[/yellow]")
        return

    with console.status("[bold green]Sending email..."):
        asyncio.run(email_client.send_email(to, subject, body, cc, bcc))
    console.print("[bold green]Email sent successfully![/bold green]")


@cli.command()
@click.argument('original_uid', type=int)
@click.option('--body', required=True, help='Reply body')
@profile_command
def reply_to_email(ctx, original_uid: int, body: str):
    """Reply to an email"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but replying to emails is not supported.[/yellow]")
        return

    with console.status("[bold green]Replying to email..."):
        asyncio.run(email_client.reply_to_email(original_uid, body))
    console.print("[bold green]Reply sent successfully![/bold green]")


@cli.command()
@click.argument('original_uid', type=int)
@click.option('--to', required=True, help='Forward recipient email address')
@click.option('--body', required=True, help='Forward body')
@profile_command
def forward_email(ctx, original_uid: int, to: str, body: str):
    """Forward an email"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but forwarding emails is not supported.[/yellow]")
        return

    with console.status("[bold green]Forwarding email..."):
        asyncio.run(email_client.forward_email(original_uid, to, body))
    console.print("[bold green]Email forwarded successfully![/bold green]")


@cli.command()
@click.argument('collection_name')
@click.option('--interval', default=60, help='Interval in seconds between email checks')
@profile_command
def watch_emails(ctx, collection_name: str, interval: int):
    """Watch for new emails and ingest them into the vector database in real-time"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but watching for new emails is not supported.[/yellow]")
        return

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
        console.print(
            f"[bold green]New email (UID: {email['uid']}) ingested into collection '{collection_name}'[/bold green]")

    console.print(f"[bold blue]Watching for new emails every {interval} seconds...[/bold blue]")
    console.print("[bold yellow]Press Ctrl+C to stop watching.[/bold yellow]")

    try:
        asyncio.run(email_client.watch_for_new_emails(ingest_email, interval))
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")


@cli.command()
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--limit', default=10, help='Number of new emails to summarize')
@profile_command
def summarize_new_emails(ctx, max_length: int, limit: int):
    """Summarize new emails"""
    if ctx.obj['offline']:
        console.print("[yellow]Warning: Running in offline mode, but summarizing new emails is not supported.[/yellow]")
        return

    last_uid = asyncio.run(email_client.get_latest_uid()) - limit  # Get the UID of the last 'limit' emails
    with console.status("[bold green]Summarizing new emails..."):
        summarized_emails = asyncio.run(email_client.summarize_new_emails(last_uid=last_uid, max_length=max_length))

        for email in summarized_emails:
            console.print(Panel(f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}\nSummary: {email['summary']}",
                          title=f"Email Summary (UID: {email['uid']})", expand=False))


@cli.command()
@click.argument('collection_name')
@click.option('--interval', default=60, help='Interval in seconds between email checks')
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@profile_command
def watch_emails_with_summary(ctx, collection_name: str, interval: int, max_length: int):
    """Watch for new emails, summarize them, and ingest them into the vector database in real-time"""
    if ctx.obj['offline']:
        console.print(
            "[yellow]Warning: Running in offline mode, but watching for new emails with summary is not supported.[/yellow]")
        return

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
        console.print(
            f"[bold green]New email (UID: {email['uid']}) summarized and ingested into collection '{collection_name}'[/bold green]")
        console.print(f"Summary: {email['summary']}")

    console.print(f"[bold blue]Watching for new emails every {interval} seconds...[/bold blue]")
    console.print("[bold yellow]Press Ctrl+C to stop watching.[/bold yellow]")

    try:
        asyncio.run(email_client.watch_for_new_emails_with_summary(process_email, interval, max_length))
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")


@cli.command()
@click.argument('user_id', type=int)
@profile_command
async def get_user_tasks(user_id: int):
    """Get tasks for a user"""
    tasks = await db_manager.get_user_tasks(user_id)
    console.print(tasks)


@cli.command()
@click.argument('user_id', type=int)
@profile_command
async def get_user_preferences(user_id: int):
    """Get preferences for a user"""
    preferences = await db_manager.get_user_preferences(user_id)
    console.print(preferences)


@cli.command()
@click.argument('pattern')
@profile_command
def clear_cache(pattern: str):
    """Clear cache entries matching the given pattern"""
    invalidate_cache(pattern)
    console.print(f"Cache entries matching '{pattern}' have been cleared.")


@cli.command()
@click.option('--check-only', is_flag=True, help="Only check for updates without applying them")
@profile_command
async def update(check_only: bool):
    """Check for and apply updates"""
    updater = UpdateManager()
    if await updater.check_for_updates():
        if check_only:
            console.print("[bold green]Updates are available.[/bold green]")
        else:
            await updater.update_all()
            console.print("[bold green]Updates have been applied.[/bold green]")
    else:
        console.print("[bold green]No updates available.[/bold green]")


@cli.group()
def backup():
    """Backup and recovery commands"""
    pass


@backup.command()
@click.pass_context
def create(ctx):
    """Create a new backup"""
    db_manager = ctx.obj['db_manager']
    chroma_db = ctx.obj['chroma_db']
    backup_manager = BackupManager(db_manager, chroma_db)
    backup_path = backup_manager.create_backup()
    console.print(f"[bold green]Backup created:[/bold green] {backup_path}")


@backup.command()
@click.argument('backup_file')
@click.pass_context
def restore(ctx, backup_file):
    """Restore from a backup"""
    db_manager = ctx.obj['db_manager']
    chroma_db = ctx.obj['chroma_db']
    backup_manager = BackupManager(db_manager, chroma_db)
    backup_manager.restore_backup(backup_file)
    console.print(f"[bold green]Backup restored from:[/bold green] {backup_file}")


@backup.command()
@click.pass_context
def list(ctx):
    """List available backups"""
    db_manager = ctx.obj['db_manager']
    chroma_db = ctx.obj['chroma_db']
    backup_manager = BackupManager(db_manager, chroma_db)
    backups = backup_manager.list_backups()
    if backups:
        console.print("[bold green]Available backups:[/bold green]")
        for backup in backups:
            console.print(backup)
    else:
        console.print("[yellow]No backups found[/yellow]")


@backup.command()
@click.argument('backup_file')
@click.pass_context
def delete(ctx, backup_file):
    """Delete a backup"""
    db_manager = ctx.obj['db_manager']
    chroma_db = ctx.obj['chroma_db']
    backup_manager = BackupManager(db_manager, chroma_db)
    backup_manager.delete_backup(backup_file)
    console.print(f"[bold green]Backup deleted:[/bold green] {backup_file}")


# Set up logging
logger = setup_logging(log_level=logging.DEBUG if settings.debug else logging.INFO)

console = Console()


# Initialize components
db_manager = DatabaseManager(settings.database_url)
if settings.encryption_key:
    encryption_manager = EncryptionManager(settings.encryption_key.get_secret_value())
else:
    # Generate a random key if not provided
    random_key = secrets.token_bytes(32)
    encryption_manager = EncryptionManager(random_key)
auth_manager = AuthManager(db_manager, encryption_manager)


try:
    logger.info("Attempting to get model path...")
    model_path = settings.llm_model_path
    if model_path:
        logger.info(f"Model path obtained: {model_path}")
        logger.info("Initializing LlamaCppInterface...")
        llm = LlamaCppInterface(model_path, db_manager=db_manager)
        logger.info("LlamaCppInterface initialized successfully")
    else:
        raise ValueError("Failed to get model path")
except Exception as e:  # noqa: F841
    logger.exception(f"Failed to initialize LLM: {str(e)}")
    console.print(f"[bold red]Failed to initialize LLM: {str(e)}[/bold red]")
    console.print("[bold yellow]The application will continue without LLM functionality.[/bold yellow]")
    llm = None


try:
    embedding_model_path = ensure_model_exists(
        settings.embedding_model,
        settings.embedding_model,
        "pytorch_model.bin",
        os.path.join(os.path.dirname(settings.llm_model_path), "embeddings")
    )
    embeddings = SentenceTransformerEmbeddings(embedding_model_path)
except Exception as e:
    logger.error(f"Failed to initialize embeddings: {str(e)}")
    console.print(f"[bold red]Failed to initialize embeddings: {str(e)}[/bold red]")
    console.print("[bold yellow]The application will continue without embedding functionality.[/bold yellow]")
    embeddings = None

chroma_db = ChromaDBManager(settings.chroma_db_path)

# Initialize TextProcessor
text_processor = TextProcessor(llm)

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
web_processor = WebScraper()
github_client = GitHubClient(settings.github_token.get_secret_value())

try:
    spacy_processor = SpacyProcessor()
except Exception as e:
    logger.error(f"Failed to initialize SpacyProcessor: {str(e)}")
    logger.warning("The application will continue without SpaCy functionality.")
    spacy_processor = None


try:
    logger.info("Attempting to get model path...")
    model_path = settings.llm_model_path
    if model_path:
        logger.info(f"Model path obtained: {model_path}")
        logger.info("Initializing LlamaCppInterface...")
        llm = LlamaCppInterface(model_path, db_manager=db_manager)
        logger.info("LlamaCppInterface initialized successfully")
    else:
        raise ValueError("Failed to get model path")
except Exception as e:
    logger.exception(f"Failed to initialize LLM: {str(e)}")
    console.print(f"[bold red]Failed to initialize LLM: {str(e)}[/bold red]")
    console.print("[bold yellow]The application will continue without LLM functionality.[/bold yellow]")
    llm = None


try:
    embedding_model_path = ensure_model_exists(
        settings.embedding_model,
        settings.embedding_model,
        "pytorch_model.bin",
        os.path.join(os.path.dirname(settings.llm_model_path), "embeddings")
    )
    embeddings = SentenceTransformerEmbeddings(embedding_model_path)
except Exception as e:
    logger.error(f"Failed to initialize embeddings: {str(e)}")
    console.print(f"[bold red]Failed to initialize embeddings: {str(e)}[/bold red]")
    console.print("[bold yellow]The application will continue without embedding functionality.[/bold yellow]")
    embeddings = None

chroma_db = ChromaDBManager(settings.chroma_db_path)

# Initialize TextProcessor
text_processor = TextProcessor(llm)

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
web_processor = WebScraper()
github_client = GitHubClient(settings.github_token.get_secret_value())

try:
    spacy_processor = SpacyProcessor()
except Exception as e:  # noqa: F841
    logger.error(f"Failed to initialize SpacyProcessor: {str(e)}")
    logger.warning("The application will continue without SpaCy functionality.")
    spacy_processor = None


# Apply error_handler to all commands
for command in cli.commands.values():
    command.callback = error_handler(command.callback)


if __name__ == "__main__":
    cli()
