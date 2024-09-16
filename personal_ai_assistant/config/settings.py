from pydantic import BaseSettings, SecretStr
from typing import Optional

class Settings(BaseSettings):
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
