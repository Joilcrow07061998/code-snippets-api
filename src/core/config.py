from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Code Snippets API"
    debug: bool = False
    secret_key: str = "dev-only-change-this-secret"
    access_token_expire_minutes: int = 30
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/snippets_db"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
