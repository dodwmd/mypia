import os
import logging
from pydantic import BaseSettings, SecretStr
from typing import Optional
from huggingface_hub import hf_hub_download

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Personal AI Assistant"
    debug: bool = False
    version: str = "0.1.0"
    update_url: str = "https://api.mypia.com/updates"
    model_dir: str = "/app/models"
    static_dir: str = "/app/static"

    # LLM settings
    llm_model_repo: str = "TheBloke/Llama-2-7B-Chat-GGUF"
    llm_model_filename: str = "llama-2-7b-chat.Q4_K_M.gguf"
    llm_model_path: str = "/app/static/models/llama-2-7b-chat.Q4_K_M.gguf"
    embedding_model: str = "dunzhang/stella_en_1.5B_v5"

    # Database settings
    database_url: str = "postgresql://mypia:mypia_password@db/mypia"
    chroma_db_path: str = "/app/data/chroma_db"
    redis_url: str = "redis://redis:6379/0"

    # Email settings
    email_host: str = "imap.example.com"
    email_username: str = "your_email@example.com"
    email_password: SecretStr
    email_use_ssl: bool = True
    smtp_host: str = "smtp.example.com"
    smtp_use_tls: bool = True

    # Calendar settings
    caldav_url: str = "https://example.com/caldav"
    caldav_username: str = "your_username"
    caldav_password: SecretStr

    # GitHub settings
    github_token: SecretStr

    # Encryption settings
    encryption_key: Optional[SecretStr] = None

    # Backup settings
    backup_dir: str = "/app/backups"

    # Multi-user settings
    enable_multi_user: bool = False
    max_users: int = 1
    user_registration_open: bool = False

    # NLP settings
    spacy_model: str = "en_core_web_sm"  # Add this line

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    def get_llm_model_path(self) -> Optional[str]:
        model_path = os.path.join(self.model_dir, self.llm_model_filename)
        logger.info(f"Checking for model at: {model_path}")
        if not os.path.exists(model_path):
            logger.info(f"Model file not found at {model_path}. Attempting to download...")
            try:
                os.makedirs(self.model_dir, exist_ok=True)
                logger.info(f"Downloading model from repo: {self.llm_model_repo}, file: {self.llm_model_filename}")
                model_path = hf_hub_download(
                    repo_id=self.llm_model_repo,
                    filename=self.llm_model_filename,
                    cache_dir=self.model_dir,
                    local_dir=self.model_dir,
                    local_dir_use_symlinks=False
                )
                logger.info(f"Model downloaded successfully to: {model_path}")
            except Exception as e:
                logger.error(f"Error downloading model: {str(e)}")
                logger.error(f"Please ensure the application has write permissions to {self.model_dir}")
                return None
        else:
            logger.info(f"Model file found at: {model_path}")
        return model_path


settings = Settings()
