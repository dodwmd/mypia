from pydantic import BaseSettings, SecretStr, HttpUrl
from typing import Optional
import secrets


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Personal AI Assistant"
    debug: bool = False
    version: str = "0.1.0"
    update_url: HttpUrl = "https://api.mypia.com/updates"
    model_dir: str = "/app/models"
    static_dir: str = "/app/static"

    # Database settings
    database_url: str = "sqlite:///./test.db"
    chroma_db_path: str = "/app/data/chroma_db"
    redis_url: str = "redis://redis:6379/0"

    # LLM settings
    llm_model_path: str = "/app/static/models/llama-2-7b-chat.Q4_K_M.gguf"
    embedding_model: str = "dunzhang/stella_en_1.5B_v5"

    # Email settings
    email_host: str = "imap.example.com"
    email_username: str = "your_email@example.com"
    email_password: SecretStr = SecretStr("your_email_password")
    email_use_ssl: bool = True
    smtp_host: str = "smtp.example.com"
    smtp_use_tls: bool = True

    # Calendar settings
    caldav_url: HttpUrl = "https://example.com/caldav"
    caldav_username: str = "your_username"
    caldav_password: SecretStr = SecretStr("your_password")

    # GitHub settings
    github_token: SecretStr = SecretStr("your_github_token")

    # Encryption settings
    encryption_key: str = secrets.token_urlsafe(32)  # Generate a default key if not provided

    # Backup settings
    backup_dir: str = "/app/backups"

    # Multi-user settings
    enable_multi_user: bool = False
    max_users: int = 1
    user_registration_open: bool = False

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Loaded environment variables:")
        for key, value in self.dict().items():
            if isinstance(value, SecretStr):
                print(f"{key}: <secret>")
            else:
                print(f"{key}: {value}")


settings = Settings()
