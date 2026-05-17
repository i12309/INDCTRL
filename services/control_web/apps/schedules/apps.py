"""Конфигурация приложения schedules."""

from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    """Настройки Django-приложения графиков и смен."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.schedules"
    verbose_name = "Графики и смены"
