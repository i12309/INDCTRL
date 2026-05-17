"""Служебные функции для подключения к PostgreSQL."""

from control_common.config import BaseAppSettings


def build_postgres_dsn(settings: BaseAppSettings) -> str:
    """Собрать DSN PostgreSQL из настроек окружения."""

    return settings.database_url
