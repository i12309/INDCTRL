"""Конфигурация приложения reports."""

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Настройки Django-приложения отчетов."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    verbose_name = "Отчеты"
