from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from personal_ai_assistant.api import auth, text_processing, email, calendar, tasks, web, github, vector_db, update, backup
from personal_ai_assistant.config import settings
from personal_ai_assistant.database.base import Base
from personal_ai_assistant.database.db_manager import engine
from personal_ai_assistant.utils.logging_config import setup_logging

app = FastAPI(title="Personal AI Assistant API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup database
Base.metadata.create_all(bind=engine)

# Setup logging
setup_logging()

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["authentication"])
app.include_router(text_processing.router, prefix="/v1/text", tags=["text processing"])
app.include_router(email.router, prefix="/v1/email", tags=["email"])
app.include_router(calendar.router, prefix="/v1/calendar", tags=["calendar"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(web.router, prefix="/v1/web", tags=["web"])
app.include_router(github.router, prefix="/v1/github", tags=["github"])
app.include_router(vector_db.router, prefix="/v1/vectordb", tags=["vector database"])
app.include_router(update.router, prefix="/v1/update", tags=["update"])
app.include_router(backup.router, prefix="/v1/backup", tags=["backup"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to MyPIA API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
