# Generated manually for INDCTRL task 02.

from django.db import migrations

DETAIL_STATE_SEEDS = [
    ("working", "рабочая"),
    ("defect", "брак"),
    ("undefined", "не определено"),
]


def seed_detail_states(apps, _schema_editor):
    """Создать начальные состояния деталей."""

    state_model = apps.get_model("production", "DetailState")
    for code, name in DETAIL_STATE_SEEDS:
        state_model.objects.update_or_create(
            code=code,
            defaults={"name": name, "is_active": True},
        )


class Migration(migrations.Migration):
    """Заполнить справочник состояний деталей."""

    dependencies = [
        ("production", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_detail_states, migrations.RunPython.noop),
    ]
