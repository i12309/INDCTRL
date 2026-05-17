"""Модели сотрудников, ролей и учетных записей."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class Role(models.Model):
    """Роль пользователя в системе INDCTRL.

    Роль хранится отдельной таблицей, чтобы FastAPI-сервисы могли быстро понимать
    права пользователя без привязки к внутренним Django-группам.
    """

    code = models.CharField("код", max_length=32, unique=True)
    name = models.CharField("название", max_length=100)
    is_active = models.BooleanField("активна", default=True)
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        """Настройки отображения ролей в Django."""

        ordering = ["code"]
        verbose_name = "роль"
        verbose_name_plural = "роли"

    def __str__(self) -> str:
        """Вернуть человекочитаемое название роли."""

        return self.name


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
        """Создать администратора Django с ролью admin."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("full_name", username)
        extra_fields.setdefault("role", Role.objects.get_or_create(code="admin", defaults={"name": "администратор"})[0])

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь INDCTRL.

    Модель создается с начала проекта как `AUTH_USER_MODEL`, чтобы позже не менять
    связи в миграциях. Поле `password` остается стандартным Django password hash,
    его сможет проверять FastAPI `auth-service` через общий helper.
    """

    username = models.CharField("логин", max_length=150, unique=True)
    full_name = models.CharField("ФИО", max_length=255)
    role = models.ForeignKey(Role, verbose_name="роль", on_delete=models.PROTECT, related_name="users")
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

    def __str__(self) -> str:
        """Вернуть ФИО или логин пользователя."""

        return self.full_name or self.username
