from pydantic import BaseSettings

class Settings(BaseSettings):
    # Add your configuration variables here
    app_name: str = "Personal AI Assistant"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
