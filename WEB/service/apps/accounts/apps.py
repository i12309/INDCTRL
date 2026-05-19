"""Конфигурация приложения accounts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Настройки Django-приложения сотрудников и учетных записей."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Сотрудники и учетные записи"
