from pydantic import BaseSettings, SecretStr
from typing import Optional
from personal_ai_assistant.utils.encryption import EncryptionManager

class Settings(BaseSettings):
    # Add your configuration variables here
    app_name: str = "Personal AI Assistant"
    debug: bool = False
    llm_model_path: str = "/path/to/your/llama/model.bin"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_db_path: str = "./chroma_db"
    
    # Sensitive data as SecretStr
    email_host: str
    email_username: str
    email_password: SecretStr
    email_use_ssl: bool = True
    smtp_host: str
    smtp_use_tls: bool = True
    caldav_url: str
    caldav_username: str
    caldav_password: SecretStr
    database_url: SecretStr
    redis_url: SecretStr
    github_token: SecretStr
    encryption_password: SecretStr

    # Update settings
    version: str = "0.1.0"
    update_url: str = "https://api.mypia.com/updates"
    model_dir: str = "./models"

    # Backup settings
    backup_dir: str = "./backups"

    # Multi-user settings
    enable_multi_user: bool = False
    max_users: int = 1
    user_registration_open: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
encryption_key = EncryptionManager.generate_key(settings.encryption_password.get_secret_value())
encryption_manager = EncryptionManager(encryption_key)
