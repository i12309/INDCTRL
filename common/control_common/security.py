"""Минимальные функции безопасности, общие для сервисов."""

from hmac import compare_digest


def constant_time_equals(left: str, right: str) -> bool:
    """Сравнить строки без раннего выхода по первому отличию."""

    return compare_digest(left.encode("utf-8"), right.encode("utf-8"))
