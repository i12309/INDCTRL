# Generated manually for INDCTRL task 02.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Создать таблицы разрешений и расписаний работы на станках."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("machines", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserMachinePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_allowed", models.BooleanField(default=True, verbose_name="разрешено")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлено")),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="user_permissions",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="machine_permissions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "разрешение на станок",
                "verbose_name_plural": "разрешения на станки",
                "ordering": ["user", "machine"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "machine"),
                        name="unique_user_machine_permission",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserMachineSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.PositiveSmallIntegerField(verbose_name="день недели")),
                ("time_from", models.TimeField(verbose_name="время с")),
                ("time_to", models.TimeField(verbose_name="время до")),
                ("is_active", models.BooleanField(default=True, verbose_name="активно")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлено")),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="user_schedules",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="machine_schedules",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "расписание работы на станке",
                "verbose_name_plural": "расписания работы на станках",
                "ordering": ["user", "machine", "weekday", "time_from"],
                "constraints": [
                    models.CheckConstraint(
                        check=models.Q(weekday__gte=1) & models.Q(weekday__lte=7),
                        name="schedule_weekday_between_1_and_7",
                    ),
                    models.CheckConstraint(
                        check=models.Q(time_from__lt=models.F("time_to")),
                        name="schedule_time_from_lt_time_to",
                    ),
                ],
            },
        ),
    ]
