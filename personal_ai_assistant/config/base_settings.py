from pydantic import BaseSettings, SecretStr
from typing import Optional


class BaseSettings(BaseSettings):
    app_name: str = "Personal AI Assistant"
    debug: bool = False
    version: str = "0.1.0"
    update_url: str = "https://api.mypia.com/updates"
    model_dir: str = "/app/models"
    static_dir: str = "/app/static"
    database_url: str
    chroma_db_path: str
    redis_url: str
    llm_model_path: str
    embedding_model: str
    email_host: str
    email_username: str
    email_password: SecretStr
    email_use_ssl: bool
    smtp_host: str
    smtp_use_tls: bool
    caldav_url: str
    caldav_username: str
    caldav_password: SecretStr
    github_token: SecretStr
    encryption_key: Optional[str] = None
    backup_dir: str
    enable_multi_user: bool = False
    max_users: int = 1
    user_registration_open: bool = False
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
