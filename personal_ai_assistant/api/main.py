from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from personal_ai_assistant.api import auth, tasks, email, calendar, text_processing, github, vector_db, update, backup, web, vectordb
from personal_ai_assistant.database.base import Base, engine
import logging

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])  # Make sure this line is present
app.include_router(email.router, prefix="/v1/email", tags=["email"])  # Make sure this line is present
app.include_router(calendar.router, prefix="/v1/calendar", tags=["calendar"])
app.include_router(text_processing.router, prefix="/v1/text", tags=["text processing"])
app.include_router(github.router, prefix="/v1/github", tags=["github"])
app.include_router(vector_db.router, prefix="/v1/vector_db", tags=["vector database"])
app.include_router(update.router, prefix="/v1/update", tags=["update"])
app.include_router(backup.router, prefix="/v1/backup", tags=["backup"])
app.include_router(web.router, prefix="/v1/web", tags=["web"])
app.include_router(vectordb.router, prefix="/v1/vectordb", tags=["vectordb"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Personal AI Assistant API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
