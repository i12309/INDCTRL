"""Общие настройки окружения для сервисов INDCTRL."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Базовые настройки, которые читаются из `.env` или переменных окружения."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    app_timezone: str = Field(default="Europe/Berlin", alias="APP_TIMEZONE")
    postgres_db: str = Field(default="machine_control", alias="POSTGRES_DB")
    postgres_user: str = Field(default="machine_control", alias="POSTGRES_USER")
    postgres_password: str = Field(default="change_me_strong_password", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    session_ttl_minutes: int = Field(default=720, alias="SESSION_TTL_MINUTES")
    heartbeat_max_age_seconds: int = Field(default=180, alias="HEARTBEAT_MAX_AGE_SECONDS")

    @property
    def database_url(self) -> str:
        """Вернуть DSN PostgreSQL для psycopg."""

        return build_postgres_dsn(self)


def build_postgres_dsn(settings: BaseAppSettings) -> str:
    """Собрать DSN PostgreSQL из настроек окружения."""

    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


@lru_cache
def get_settings() -> BaseAppSettings:
    """Вернуть настройки приложения с кэшированием на время жизни процесса."""

    return BaseAppSettings()
