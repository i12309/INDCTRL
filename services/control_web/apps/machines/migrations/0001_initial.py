# Generated manually for INDCTRL task 02.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Создать таблицы станков и ESP32-устройств."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Machine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="название")),
                ("inventory_number", models.CharField(blank=True, max_length=100, null=True, verbose_name="инвентарный номер")),
                ("comment", models.TextField(blank=True, null=True, verbose_name="комментарий")),
                ("is_active", models.BooleanField(default=True, verbose_name="активен")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлен")),
            ],
            options={
                "verbose_name": "станок",
                "verbose_name_plural": "станки",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mac_address", models.CharField(max_length=32, unique=True, verbose_name="MAC-адрес")),
                ("name", models.CharField(blank=True, max_length=150, null=True, verbose_name="название")),
                ("is_active", models.BooleanField(default=True, verbose_name="активно")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлено")),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="devices",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
            ],
            options={
                "verbose_name": "ESP32-устройство",
                "verbose_name_plural": "ESP32-устройства",
                "ordering": ["mac_address"],
                "indexes": [
                    models.Index(fields=["mac_address"], name="device_mac_address_idx"),
                ],
            },
        ),
    ]
