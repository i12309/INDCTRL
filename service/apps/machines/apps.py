"""Конфигурация приложения machines."""

from django.apps import AppConfig


class MachinesConfig(AppConfig):
    """Настройки Django-приложения станков."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.machines"
    verbose_name = "Станки"
