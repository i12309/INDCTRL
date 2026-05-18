# Generated manually for INDCTRL clean initial schema.

from django.db import migrations, models

USER_PERMISSIONS = [
    ("view_reports", "Может просматривать dashboard и отчеты"),
    ("use_esp32_api", "Может работать через ESP32 API"),
]

GROUPS = {
    "Администраторы": ["view_reports"],
    "Руководители": ["view_reports"],
    "Менеджеры": ["view_reports"],
    "Работники ESP32": ["use_esp32_api"],
}


def seed_groups_and_permissions(apps, _schema_editor):
    """Создать стартовые группы и бизнес-права для чистой БД."""

    content_type_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    group_model = apps.get_model("auth", "Group")

    user_content_type, _ = content_type_model.objects.get_or_create(
        app_label="accounts",
        model="user",
    )

    permissions = {}
    for codename, name in USER_PERMISSIONS:
        permission, _ = permission_model.objects.get_or_create(
            content_type=user_content_type,
            codename=codename,
            defaults={"name": name},
        )
        permissions[codename] = permission

    for group_name, permission_codenames in GROUPS.items():
        group, _ = group_model.objects.get_or_create(name=group_name)
        group.permissions.add(*(permissions[codename] for codename in permission_codenames))


class Migration(migrations.Migration):
    """Создать кастомную модель пользователя."""

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
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
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
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
                "permissions": USER_PERMISSIONS,
            },
        ),
        migrations.RunPython(seed_groups_and_permissions, migrations.RunPython.noop),
    ]
