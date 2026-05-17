"""Общий пул подключений к PostgreSQL для FastAPI-сервисов."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from psycopg import Connection
    from psycopg_pool import ConnectionPool

from control_common.config import BaseAppSettings, get_settings

_pool: "ConnectionPool | None" = None


def init_connection_pool(
    settings: BaseAppSettings | None = None,
    *,
    min_size: int = 1,
    max_size: int = 10,
    open_pool: bool = False,
) -> "ConnectionPool":
    """Инициализировать общий пул подключений к PostgreSQL.

    FastAPI-приложения вызывают эту функцию на старте процесса. По умолчанию пул
    создается лениво, чтобы health endpoint мог подняться даже до первого SQL-запроса.
    """

    global _pool

    if _pool is not None:
        return _pool

    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool

    app_settings = settings or get_settings()
    _pool = ConnectionPool(
        conninfo=app_settings.database_url,
        min_size=min_size,
        max_size=max_size,
        kwargs={"row_factory": dict_row},
        open=open_pool,
    )
    return _pool


def get_connection_pool() -> "ConnectionPool":
    """Вернуть текущий пул подключений, создав его при первом обращении."""

    return init_connection_pool()


@contextmanager
def get_connection() -> Iterator["Connection"]:
    """Выдать PostgreSQL connection из общего пула.

    Контекстный менеджер сам возвращает connection в пул после блока `with`.
    FastAPI-сервисы должны использовать эту функцию вместо собственных подключений.
    """

    pool = get_connection_pool()
    if pool.closed:
        pool.open(wait=True)

    with pool.connection() as connection:
        yield connection


def close_connection_pool() -> None:
    """Закрыть пул подключений при завершении FastAPI-приложения."""

    global _pool

    if _pool is not None:
        _pool.close()
        _pool = None
