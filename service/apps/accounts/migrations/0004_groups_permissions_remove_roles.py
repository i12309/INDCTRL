# Generated manually for INDCTRL access migration.

from django.db import migrations

USER_PERMISSIONS = [
    ("view_reports", "Может просматривать dashboard и отчеты"),
    ("use_esp32_api", "Может работать через ESP32 API"),
]

GROUPS = {
    "admin": ("Администраторы", ["view_reports"]),
    "director": ("Руководители", ["view_reports"]),
    "manager": ("Менеджеры", ["view_reports"]),
    "worker": ("Работники ESP32", ["use_esp32_api"]),
}


def migrate_roles_to_groups(apps, _schema_editor):
    """Перенести старые роли в стандартные Django-группы и права."""

    content_type_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    group_model = apps.get_model("auth", "Group")
    user_model = apps.get_model("accounts", "User")

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

    groups = {}
    for _role_code, (group_name, permission_codenames) in GROUPS.items():
        group, _ = group_model.objects.get_or_create(name=group_name)
        group.permissions.add(*(permissions[codename] for codename in permission_codenames))
        groups[_role_code] = group

    for user in user_model.objects.select_related("role").filter(role__isnull=False):
        group = groups.get(user.role.code)
        if group is not None:
            user.groups.add(group)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_groups_alter_user_is_superuser_and_more"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ["username"],
                "permissions": USER_PERMISSIONS,
                "swappable": "AUTH_USER_MODEL",
                "verbose_name": "пользователь",
                "verbose_name_plural": "пользователи",
            },
        ),
        migrations.RunPython(migrate_roles_to_groups, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="user",
            name="role",
        ),
        migrations.DeleteModel(
            name="Role",
        ),
    ]
