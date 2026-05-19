"""Регистрация моделей графиков в Django admin."""

from django.contrib import admin

from apps.schedules.models import UserMachineSchedule


@admin.register(UserMachineSchedule)
class UserMachineScheduleAdmin(admin.ModelAdmin):
    """Админка расписаний работы пользователя на станке."""

    list_display = ("user", "machine", "weekday", "time_from", "time_to", "is_active")
    list_filter = ("weekday", "is_active", "machine")
    search_fields = ("user__username", "user__full_name", "machine__name")
    readonly_fields = ("created_at", "updated_at")
