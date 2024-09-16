from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from functools import lru_cache
import logging

from personal_ai_assistant.auth.auth_manager import AuthManager
from personal_ai_assistant.llm.text_processor import TextProcessor
from personal_ai_assistant.email.imap_client import EmailClient
from personal_ai_assistant.calendar.caldav_client import CalDAVClient
from personal_ai_assistant.tasks.task_manager import TaskManager
from personal_ai_assistant.web.scraper import WebScraper
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.updater.update_manager import UpdateManager
from personal_ai_assistant.utils.backup_manager import BackupManager
from personal_ai_assistant.utils.encryption import EncryptionManager
from personal_ai_assistant.sync.sync_manager import SyncManager
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.db_manager import SessionLocal, engine
from personal_ai_assistant.database import models
from personal_ai_assistant.utils.logging_config import setup_logging

app = FastAPI(title="Personal AI Assistant API")
api_router = APIRouter(prefix="/v1")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Setup database
models.Base.metadata.create_all(bind=engine)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Pydantic models for request/response bodies
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    password: str

class Task(BaseModel):
    title: str
    description: str

class Email(BaseModel):
    to: str
    subject: str
    body: str

class CalendarEvent(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None

class VectorDBDocument(BaseModel):
    collection_name: str
    document: str
    metadata: Optional[dict] = None

class VectorDBQuery(BaseModel):
    collection_name: str
    query_text: str
    n_results: int = 5

# Dependency injection functions
@lru_cache()
def get_auth_manager():
    return AuthManager()

@lru_cache()
def get_text_processor():
    return TextProcessor()

@lru_cache()
def get_email_client():
    return EmailClient(settings.EMAIL_IMAP_SERVER, settings.EMAIL_SMTP_SERVER, settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)

@lru_cache()
def get_caldav_client():
    return CalDAVClient(settings.CALDAV_URL, settings.CALDAV_USERNAME, settings.CALDAV_PASSWORD)

@lru_cache()
def get_task_manager():
    return TaskManager()

@lru_cache()
def get_web_scraper():
    return WebScraper()

@lru_cache()
def get_github_client():
    return GitHubClient(settings.GITHUB_TOKEN)

@lru_cache()
def get_chroma_db():
    return ChromaDBManager(settings.chroma_db_path)

@lru_cache()
def get_update_manager():
    return UpdateManager()

@lru_cache()
def get_backup_manager():
    return BackupManager()

@lru_cache()
def get_encryption_manager():
    return EncryptionManager()

@lru_cache()
def get_sync_manager():
    return SyncManager()

@lru_cache()
def get_llm():
    return LlamaCppInterface(settings.LLM_MODEL_PATH)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Perform startup tasks."""
    logger.info("Starting up MyPIA API")
    # Add any necessary startup tasks here

@app.on_event("shutdown")
async def shutdown_event():
    """Perform shutdown tasks."""
    logger.info("Shutting down MyPIA API")
    # Add any necessary shutdown tasks here

# Root and health check endpoints
@api_router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to MyPIA API"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Authentication endpoints
@api_router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_manager.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: User,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    created_user = auth_manager.create_user(user.username, user.email, user.password)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    return {"message": "User created successfully"}


# Text processing endpoints
@api_router.post("/summarize")
async def summarize_text(
    text: str,
    max_length: int = 100,
    token: str = Depends(oauth2_scheme),
    text_processor: TextProcessor = Depends(get_text_processor)
):
    try:
        summary = await text_processor.summarize_text(text, max_length)
        logger.info(f"Successfully summarized text of length {len(text)}")
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error summarizing text")

@api_router.post("/generate")
async def generate_text(
    prompt: str,
    max_length: int = 100,
    token: str = Depends(oauth2_scheme),
    text_processor: TextProcessor = Depends(get_text_processor)
):
    try:
        generated_text = await text_processor.generate_text(prompt, max_length)
        logger.info(f"Successfully generated text from prompt of length {len(prompt)}")
        return {"generated_text": generated_text}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating text")

# Email endpoints
@api_router.get("/emails")
async def get_emails(
    limit: int = 10,
    token: str = Depends(oauth2_scheme),
    email_client: EmailClient = Depends(get_email_client)
):
    try:
        emails = await email_client.fetch_emails(limit=limit)
        logger.info(f"Successfully fetched {len(emails)} emails")
        return {"emails": emails}
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching emails")

@api_router.post("/emails/send")
async def send_email(
    email: Email,
    token: str = Depends(oauth2_scheme),
    email_client: EmailClient = Depends(get_email_client)
):
    try:
        await email_client.send_email(email.to, email.subject, email.body)
        logger.info(f"Successfully sent email to {email.to}")
        return {"message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending email")

# Calendar endpoints
@api_router.get("/calendar/events")
async def get_calendar_events(
    token: str = Depends(oauth2_scheme),
    caldav_client: CalDAVClient = Depends(get_caldav_client)
):
    try:
        events = await caldav_client.get_events()
        logger.info(f"Successfully fetched {len(events)} calendar events")
        return {"events": events}
    except Exception as e:
        logger.error(f"Error fetching calendar events: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching calendar events")

@api_router.post("/calendar/events")
async def create_calendar_event(
    event: CalendarEvent,
    token: str = Depends(oauth2_scheme),
    caldav_client: CalDAVClient = Depends(get_caldav_client)
):
    try:
        created_event = await caldav_client.create_event(event.title, event.start_time, event.end_time, event.description)
        logger.info(f"Successfully created calendar event: {event.title}")
        return {"message": "Event created successfully", "event": created_event}
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating calendar event")

# Task management endpoints
@api_router.get("/tasks")
async def get_tasks(
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        tasks = await task_manager.get_all_tasks()
        logger.info(f"Successfully fetched {len(tasks)} tasks")
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")

@api_router.post("/tasks")
async def create_task(
    task: Task,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        created_task = await task_manager.create_task(task.title, task.description)
        logger.info(f"Successfully created task: {task.title}")
        return {"message": "Task created successfully", "task": created_task}
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating task")

# Web scraping endpoint
@api_router.get("/scrape")
async def scrape_url(
    url: str,
    token: str = Depends(oauth2_scheme),
    web_scraper: WebScraper = Depends(get_web_scraper)
):
    try:
        scraped_data = await web_scraper.scrape_url(url)
        logger.info(f"Successfully scraped data from URL: {url}")
        return {"scraped_data": scraped_data}
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scraping URL")

# GitHub integration endpoints
@api_router.get("/github/repos")
async def get_github_repos(
    username: str,
    token: str = Depends(oauth2_scheme),
    github_client: GitHubClient = Depends(get_github_client)
):
    try:
        repos = await github_client.get_user_repos(username)
        logger.info(f"Successfully fetched GitHub repos for user: {username}")
        return {"repos": repos}
    except Exception as e:
        logger.error(f"Error fetching GitHub repos for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching GitHub repos")

@api_router.get("/github/issues")
async def get_github_issues(
    repo_full_name: str,
    token: str = Depends(oauth2_scheme),
    github_client: GitHubClient = Depends(get_github_client)
):
    try:
        issues = await github_client.get_repo_issues(repo_full_name)
        logger.info(f"Successfully fetched GitHub issues for repo: {repo_full_name}")
        return {"issues": issues}
    except Exception as e:
        logger.error(f"Error fetching GitHub issues for repo {repo_full_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching GitHub issues")

# Vector database endpoints
@api_router.post("/vectordb/add")
async def add_to_vectordb(
    document: VectorDBDocument,
    token: str = Depends(oauth2_scheme),
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    try:
        await chroma_db.add_documents(document.collection_name, [document.document], [document.metadata])
        logger.info(f"Successfully added document to vector database collection: {document.collection_name}")
        return {"message": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error adding document to vector database: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding document to vector database")

@api_router.post("/vectordb/query")
async def query_vectordb(
    query: VectorDBQuery,
    token: str = Depends(oauth2_scheme),
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    try:
        results = await chroma_db.query(query.collection_name, [query.query_text], query.n_results)
        logger.info(f"Successfully queried vector database collection: {query.collection_name}")
        return {"results": results}
    except Exception as e:
        logger.error(f"Error querying vector database: {str(e)}")
        raise HTTPException(status_code=500, detail="Error querying vector database")

# Update management endpoint
@api_router.post("/update")
async def check_and_apply_updates(
    token: str = Depends(oauth2_scheme),
    update_manager: UpdateManager = Depends(get_update_manager)
):
    try:
        updates_available = await update_manager.check_for_updates()
        if updates_available:
            await update_manager.update_all()
            logger.info("Successfully applied updates")
            return {"message": "Updates applied successfully"}
        logger.info("No updates available")
        return {"message": "No updates available"}
    except Exception as e:
        logger.error(f"Error checking or applying updates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking or applying updates")

# Backup management endpoints
@api_router.post("/backup/create")
async def create_backup(
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        backup_path = await backup_manager.create_backup()
        logger.info(f"Successfully created backup at: {backup_path}")
        return {"message": "Backup created successfully", "backup_path": backup_path}
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating backup")

@api_router.post("/backup/restore")
async def restore_backup(
    backup_file: str,
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        await backup_manager.restore_backup(backup_file)
        logger.info(f"Successfully restored backup from: {backup_file}")
        return {"message": "Backup restored successfully"}
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error restoring backup")

@api_router.get("/backup/list")
async def list_backups(
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        backups = await backup_manager.list_backups()
        logger.info(f"Successfully listed {len(backups)} backups")
        return {"backups": backups}
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing backups")

# Include the API router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
