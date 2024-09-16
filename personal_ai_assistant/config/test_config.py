from pydantic import BaseSettings, SecretStr
from typing import Optional


class TestConfig(BaseSettings):
    database_url: str
    encryption_key: Optional[SecretStr] = None
    llm_model_path: str
    embedding_model: str
    chroma_db_path: str
    email_host: str
    smtp_host: str
    email_username: str
    email_password: SecretStr
    caldav_url: str
    caldav_username: str
    caldav_password: SecretStr
    github_token: SecretStr
    redis_url: str = "redis://redis:6379/0"  # Add this line with a default value

    class Config:
        env_file = ".env.test"


test_settings = TestConfig()
