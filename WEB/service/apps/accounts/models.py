"""Модели сотрудников и учетных записей."""

import hashlib
import hmac

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер кастомной модели пользователя."""

    def create_user(self, username: str, password: str | None = None, **extra_fields):
        """Создать обычного пользователя со стандартным Django-хешированием пароля."""

        if not username:
            raise ValueError("Логин пользователя обязателен")
        user = self.model(username=self.model.normalize_username(username), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str | None = None, **extra_fields):
        """Создать администратора Django."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("full_name", username)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь INDCTRL.

    Модель создается с начала проекта как `AUTH_USER_MODEL`, чтобы позже не менять
    связи в миграциях. Поле `password` остается стандартным Django password hash,
    его проверяет Django API через стандартный `check_password`.
    """

    username_validator = ASCIIUsernameValidator()

    username = models.CharField(
        "логин",
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text="Только латинские буквы, цифры и символы @/./+/-/_.",
    )
    full_name = models.CharField("ФИО", max_length=255)
    pin_hash = models.CharField("ESP32 PIN hash", max_length=64, unique=True, blank=True, null=True)
    is_active = models.BooleanField("активен", default=True)
    is_staff = models.BooleanField("доступ в admin", default=False)
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлен", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        """Настройки пользовательской модели Django."""

        ordering = ["username"]
        swappable = "AUTH_USER_MODEL"
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        permissions = [
            ("view_reports", "Может просматривать dashboard и отчеты"),
            ("use_esp32_api", "Может работать через ESP32 API"),
        ]

    def __str__(self) -> str:
        """Вернуть ФИО или логин пользователя."""

        return self.full_name or self.username

    @staticmethod
    def normalize_pin(pin: str | int | None) -> str:
        """Return a validated numeric ESP32 PIN."""

        value = "" if pin is None else str(pin).strip()
        if not value:
            return ""
        if not value.isdigit():
            raise ValueError("PIN must contain digits only")
        if len(value) > 10:
            raise ValueError("PIN must contain no more than 10 digits")
        return value

    @staticmethod
    def hash_pin(pin: str | int | None) -> str:
        """Return deterministic HMAC hash used for unique PIN lookup."""

        value = User.normalize_pin(pin)
        if not value:
            return ""
        key = settings.SECRET_KEY.encode("utf-8")
        return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def set_pin(self, pin: str | int | None) -> None:
        """Set or clear ESP32 PIN hash."""

        self.pin_hash = self.hash_pin(pin) or None

    def check_pin(self, pin: str | int | None) -> bool:
        """Check ESP32 PIN without storing it in clear text."""

        expected = self.hash_pin(pin)
        return bool(expected and self.pin_hash and hmac.compare_digest(self.pin_hash, expected))
