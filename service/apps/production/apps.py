"""Конфигурация приложения production."""

from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """Настройки Django-приложения производственных событий."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.production"
    verbose_name = "Производство"
