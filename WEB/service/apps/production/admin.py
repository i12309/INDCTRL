"""Регистрация производственных моделей в Django admin."""

from django.contrib import admin

from apps.production.models import (
    AuthSession,
    Detail,
    DetailType,
    InvalidEvent,
    Work,
)


class ReadOnlyAdminMixin:
    """Mixin для моделей, которые создаются сервисами и в admin только просматриваются."""

    def has_add_permission(self, _request) -> bool:
        """Запретить ручное создание записей через admin."""

        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Разрешить открывать страницу записи, но запретить сохранение изменений."""

        return request.method in {"GET", "HEAD", "OPTIONS"} and self.has_view_permission(request, obj)

    def get_readonly_fields(self, _request, obj=None) -> tuple[str, ...]:
        """Сделать все поля модели недоступными для редактирования."""

        return tuple(field.name for field in self.model._meta.fields)


@admin.register(DetailType)
class DetailTypeAdmin(admin.ModelAdmin):
    """Админка типов деталей."""

    list_display = ("code", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """Админка рабочих смен.

    Активные смены видны через колонку `status` и фильтр по статусу, чтобы
    администратор быстро находил занятые станки.
    """

    list_display = ("id", "user", "machine", "status", "started_at", "finished_at", "last_seen_at")
    list_filter = ("status", "machine", "started_at")
    search_fields = ("user__username", "user__full_name", "machine__name", "device__mac_address")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "started_at"
    list_select_related = ("user", "machine", "device")


@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    """Админка сессий авторизации."""

    list_display = ("id", "user", "machine", "device", "work", "expires_at", "is_active", "created_at")
    list_filter = ("is_active", "machine")
    search_fields = ("id", "user__username", "user__full_name", "machine__name", "device__mac_address")
    readonly_fields = ("id", "created_at")


@admin.register(Detail)
class DetailAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Админка для просмотра произведенных деталей.

    Детали создаются только через Django API, поэтому ручное добавление и
    изменение запрещены. Удаление разрешено только superuser как аварийная операция.
    """

    list_display = ("id", "event_time", "user", "machine", "work", "detail_number", "detail_type", "quality_percent")
    list_filter = ("event_time", "machine", "user", "detail_type", "quality_percent")
    search_fields = ("detail_number", "user__username", "user__full_name", "machine__name")
    date_hierarchy = "event_time"
    list_select_related = ("user", "machine", "work", "detail_type")

    def has_delete_permission(self, request, obj=None) -> bool:
        """Разрешить удаление деталей только superuser."""

        return request.user.is_superuser


@admin.register(InvalidEvent)
class InvalidEventAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Админка для просмотра некорректных событий.

    Такие записи создаются Django API при ошибках входящих запросов, чтобы
    администратор видел сырой body и причину отказа.
    """

    list_display = ("id", "received_at", "source_ip", "service_name", "short_error")
    list_filter = ("service_name", "received_at")
    search_fields = ("source_ip", "raw_body", "error_text", "service_name")
    date_hierarchy = "received_at"

    @admin.display(description="ошибка")
    def short_error(self, obj: InvalidEvent) -> str:
        """Вернуть короткий текст ошибки для списка событий."""

        if len(obj.error_text) <= 80:
            return obj.error_text
        return f"{obj.error_text[:77]}..."

    def has_delete_permission(self, _request, obj=None) -> bool:
        """Запретить удаление некорректных событий из admin."""

        return False
