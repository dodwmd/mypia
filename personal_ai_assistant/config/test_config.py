from pydantic import BaseSettings, SecretStr

class TestConfig(BaseSettings):
    database_url: str
    encryption_key: SecretStr
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

    class Config:
        env_file = ".env.test"

test_settings = TestConfig()
