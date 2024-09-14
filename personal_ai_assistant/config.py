from pydantic import BaseSettings

class Settings(BaseSettings):
    # Add your configuration variables here
    app_name: str = "Personal AI Assistant"
    debug: bool = False
    llm_model_path: str = "/path/to/your/llama/model.bin"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_db_path: str = "./chroma_db"
    email_host: str = "imap.example.com"
    email_username: str = "your_email@example.com"
    email_password: str = "your_email_password"
    email_use_ssl: bool = True
    smtp_host: str = "smtp.example.com"
    smtp_use_tls: bool = True
    caldav_url: str = "https://example.com/caldav"
    caldav_username: str = "your_username"
    caldav_password: str = "your_password"

    class Config:
        env_file = ".env"

settings = Settings()
