"""Конфигурация Django-приложения API."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Приложение с JSON API для ESP32."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API ESP32"
