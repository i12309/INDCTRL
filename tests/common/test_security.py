"""Тесты проверки Django password hash."""

from control_common.security import verify_django_password

DJANGO_HASH = "pbkdf2_sha256$720000$testsalt$1Gcs0kxgCMnRfX3SeHtQ/XAmc0Vp6UZQGId2xXfmeck="


def test_verify_django_password_accepts_valid_password() -> None:
    """Правильный пароль проходит проверку по Django hash."""

    assert verify_django_password("secret", DJANGO_HASH) is True


def test_verify_django_password_rejects_invalid_password() -> None:
    """Неправильный пароль не проходит проверку по тому же hash."""

    assert verify_django_password("wrong-secret", DJANGO_HASH) is False


def test_verify_django_password_rejects_invalid_hash() -> None:
    """Некорректная строка hash не должна приводить к успешной проверке."""

    assert verify_django_password("secret", "not-a-django-hash") is False
