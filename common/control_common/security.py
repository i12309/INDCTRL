"""Функции безопасности, общие для сервисов."""

import base64
import hashlib
from hmac import compare_digest


def constant_time_equals(left: str, right: str) -> bool:
    """Сравнить строки без раннего выхода по первому отличию."""

    return compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def verify_django_password(raw_password: str, encoded_password: str) -> bool:
    """Проверяет обычный пароль пользователя по hash, сохраненному Django.

    Пароль нельзя хранить открытым текстом: при утечке БД злоумышленник сразу
    получит реальные пароли работников. Django хранит salted hash, поэтому FastAPI
    сравнивает введенный пароль с hash без знания исходного значения.
    """

    try:
        from django.contrib.auth.hashers import check_password
    except ImportError:
        return _verify_pbkdf2_sha256_password(raw_password, encoded_password)

    return check_password(raw_password, encoded_password)


def _verify_pbkdf2_sha256_password(raw_password: str, encoded_password: str) -> bool:
    """Проверить стандартный Django hash `pbkdf2_sha256` без импорта Django."""

    try:
        algorithm, iterations_text, salt, stored_hash = encoded_password.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256" or not stored_hash:
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    calculated_hash = base64.b64encode(derived).decode("ascii").strip()
    return constant_time_equals(calculated_hash, stored_hash)
