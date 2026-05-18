"""Модели сотрудников и учетных записей."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
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

    username = models.CharField("логин", max_length=150, unique=True)
    full_name = models.CharField("ФИО", max_length=255)
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
