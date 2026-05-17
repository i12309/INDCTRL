"""Регистрация моделей станков в Django admin."""

from django.contrib import admin

from apps.machines.models import Device, Machine


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    """Админка станков."""

    list_display = ("id", "name", "inventory_number", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "inventory_number", "comment")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Админка ESP32-устройств."""

    list_display = ("id", "mac_address", "machine", "name", "is_active")
    list_filter = ("is_active", "machine")
    search_fields = ("mac_address", "name", "machine__name")
    readonly_fields = ("created_at", "updated_at")
