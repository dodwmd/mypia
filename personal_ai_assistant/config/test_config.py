from .base_settings import BaseSettings
from pydantic import SecretStr
from typing import Optional


class TestConfig(BaseSettings):
    # Override settings for testing
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    chroma_db_path: str = "/tmp/test_chroma_db"
    redis_url: str = "redis://localhost:6379/1"
    llm_model_path: str = "/tmp/test_llm_model.gguf"
    embedding_model: str = "test_embedding_model"
    email_host: str = "test.example.com"
    email_username: str = "test@example.com"
    email_password: SecretStr = SecretStr("test_password")
    caldav_url: str = "https://test.example.com/caldav"
    caldav_username: str = "test_user"
    caldav_password: SecretStr = SecretStr("test_password")
    github_token: SecretStr = SecretStr("test_github_token")
    encryption_key: Optional[str] = "test_encryption_key"
    backup_dir: str = "/tmp/test_backups"
    secret_key: str = "test_secret_key"
    user_registration_open: bool = True

    class Config:
        env_file = ".env.test"

test_settings = TestConfig()
