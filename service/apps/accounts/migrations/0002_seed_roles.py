# Generated manually for INDCTRL task 02.

from django.db import migrations

ROLE_SEEDS = [
    ("admin", "администратор"),
    ("director", "директор"),
    ("manager", "менеджер"),
    ("worker", "работник"),
]


def seed_roles(apps, _schema_editor):
    """Создать начальные роли пользователей."""

    role_model = apps.get_model("accounts", "Role")
    for code, name in ROLE_SEEDS:
        role_model.objects.update_or_create(
            code=code,
            defaults={"name": name, "is_active": True},
        )


class Migration(migrations.Migration):
    """Заполнить справочник ролей."""

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, migrations.RunPython.noop),
    ]
