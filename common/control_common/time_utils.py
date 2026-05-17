"""Функции для единообразной работы со временем."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Вернуть текущий момент времени в UTC."""

    return datetime.now(tz=UTC)
