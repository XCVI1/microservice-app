from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    APP_PORT: int = 8002

    DATABASE_URL: str = "postgresql+asyncpg://user:password@postgres:5432/core_db"

    AUTH_SERVICE_URL: str = "http://auth-service:8001"


settings = Settings()
