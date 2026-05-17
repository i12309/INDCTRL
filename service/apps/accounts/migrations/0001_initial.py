# Generated manually for INDCTRL task 02.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Создать роли и кастомную модель пользователя."""

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=32, unique=True, verbose_name="код")),
                ("name", models.CharField(max_length=100, verbose_name="название")),
                ("is_active", models.BooleanField(default=True, verbose_name="активна")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлена")),
            ],
            options={
                "verbose_name": "роль",
                "verbose_name_plural": "роли",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, verbose_name="superuser status")),
                ("username", models.CharField(max_length=150, unique=True, verbose_name="логин")),
                ("full_name", models.CharField(max_length=255, verbose_name="ФИО")),
                ("is_active", models.BooleanField(default=True, verbose_name="активен")),
                ("is_staff", models.BooleanField(default=False, verbose_name="доступ в admin")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлен")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="users",
                        to="accounts.role",
                        verbose_name="роль",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "пользователь",
                "verbose_name_plural": "пользователи",
                "ordering": ["username"],
                "swappable": "AUTH_USER_MODEL",
            },
        ),
    ]
