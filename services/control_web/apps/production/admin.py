"""Регистрация производственных моделей в Django admin."""

from django.contrib import admin

from apps.production.models import (
    AuthSession,
    Detail,
    DetailState,
    DetailType,
    InvalidEvent,
    Work,
)


@admin.register(DetailType)
class DetailTypeAdmin(admin.ModelAdmin):
    """Админка типов деталей."""

    list_display = ("code", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DetailState)
class DetailStateAdmin(admin.ModelAdmin):
    """Админка состояний деталей."""

    list_display = ("code", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """Админка рабочих смен."""

    list_display = ("user", "machine", "device", "status", "started_at", "finished_at", "last_seen_at")
    list_filter = ("status", "machine")
    search_fields = ("user__username", "user__full_name", "machine__name", "device__mac_address")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    """Админка сессий авторизации."""

    list_display = ("id", "user", "machine", "device", "work", "expires_at", "is_active", "created_at")
    list_filter = ("is_active", "machine")
    search_fields = ("id", "user__username", "user__full_name", "machine__name", "device__mac_address")
    readonly_fields = ("id", "created_at")


@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    """Админка произведенных деталей."""

    list_display = ("detail_number", "user", "machine", "work", "detail_type", "detail_state", "event_time")
    list_filter = ("detail_type", "detail_state", "machine")
    search_fields = ("detail_number", "user__username", "user__full_name", "machine__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InvalidEvent)
class InvalidEventAdmin(admin.ModelAdmin):
    """Админка некорректных событий."""

    list_display = ("service_name", "source_ip", "received_at", "created_at")
    list_filter = ("service_name", "received_at")
    search_fields = ("source_ip", "raw_body", "error_text", "service_name")
    readonly_fields = ("received_at", "created_at")
