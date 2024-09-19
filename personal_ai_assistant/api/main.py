from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from personal_ai_assistant.api import auth, tasks, email, calendar, text_processing, github, update, backup, web, vectordb
from personal_ai_assistant.database.base import Base, engine
import logging
import sys
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])  # Make sure this line is present
app.include_router(email.router, prefix="/v1/email", tags=["email"])  # Make sure this line is present
app.include_router(calendar.router, prefix="/v1/calendar", tags=["calendar"])
app.include_router(text_processing.router, prefix="/v1/text", tags=["text processing"])
app.include_router(github.router, prefix="/v1/github", tags=["github"])
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

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                logger.error(f"Response status: {response.status_code}")
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                logger.error(f"Response body: {body.decode()}")
                # Create a new response with the logged body to avoid Content-Length mismatch
                return Response(content=body, status_code=response.status_code, headers=dict(response.headers))
            else:
                logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            error_msg = f"Exception during request processing: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(status_code=500, content={"message": "Internal Server Error", "detail": str(e)})

app.add_middleware(LoggingMiddleware)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Unhandled exception: {str(exc)}"
    logger.error(error_msg)
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred.", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
