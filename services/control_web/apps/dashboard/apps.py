"""Конфигурация приложения dashboard."""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Настройки Django-приложения dashboard."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    verbose_name = "Dashboard"
