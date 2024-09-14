import click
from rich.console import Console
from personal_ai_assistant.config import settings
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.email.imap_client import EmailClient
from rich.table import Table
import json
import numpy as np
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
    emails = email_client.fetch_emails(limit=limit)
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
    emails = email_client.fetch_emails(limit=1000)  # Fetch more emails to ensure we find the right one
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
    emails = email_client.fetch_emails(limit=1000)  # Fetch more emails to ensure we find the right one
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
    emails = email_client.fetch_emails(limit=limit)
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
    new_emails = email_client.fetch_new_emails(last_uid=int(last_uid) if last_uid else 0)
    
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
    email_client.send_email(to, subject, body, cc, bcc)
    console.print("[bold green]Email sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--body', required=True, help='Reply body')
def reply_to_email(original_uid: int, body: str):
    """Reply to an email"""
    email_client.reply_to_email(original_uid, body)
    console.print("[bold green]Reply sent successfully![/bold green]")

@cli.command()
@click.argument('original_uid', type=int)
@click.option('--to', required=True, help='Forward recipient email address')
@click.option('--body', required=True, help='Forward body')
def forward_email(original_uid: int, to: str, body: str):
    """Forward an email"""
    email_client.forward_email(original_uid, to, body)
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
        email_client.watch_for_new_emails(ingest_email, interval)
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")

@cli.command()
@click.option('--max-length', default=100, help='Maximum length of the summary in words')
@click.option('--limit', default=10, help='Number of new emails to summarize')
def summarize_new_emails(max_length: int, limit: int):
    """Summarize new emails"""
    last_uid = email_client.get_latest_uid() - limit  # Get the UID of the last 'limit' emails
    summarized_emails = email_client.summarize_new_emails(last_uid=last_uid, max_length=max_length)
    
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
        email_client.watch_for_new_emails_with_summary(process_email, interval, max_length)
    except KeyboardInterrupt:
        console.print("[bold red]Stopped watching for new emails.[/bold red]")

if __name__ == "__main__":
    cli()
