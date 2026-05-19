"""Регистрация моделей сотрудников в Django admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка кастомной модели пользователя."""

    model = User
    list_display = ("id", "username", "full_name", "is_active", "is_staff")
    list_filter = ("groups", "is_active", "is_staff")
    search_fields = ("username", "full_name")
    ordering = ("username",)
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональные данные", {"fields": ("full_name",)}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "full_name", "password1", "password2", "is_staff", "is_superuser", "groups"),
            },
        ),
    )
