# Generated manually for INDCTRL task 02.

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Создать производственные таблицы."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("machines", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DetailState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=32, unique=True, verbose_name="код")),
                ("name", models.CharField(max_length=100, verbose_name="название")),
                ("is_active", models.BooleanField(default=True, verbose_name="активно")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлено")),
            ],
            options={
                "verbose_name": "состояние детали",
                "verbose_name_plural": "состояния деталей",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="DetailType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True, verbose_name="код")),
                ("name", models.CharField(max_length=150, verbose_name="название")),
                ("is_active", models.BooleanField(default=True, verbose_name="активен")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлен")),
            ],
            options={
                "verbose_name": "тип детали",
                "verbose_name_plural": "типы деталей",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="InvalidEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("received_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="получено")),
                ("source_ip", models.CharField(blank=True, max_length=64, null=True, verbose_name="IP-адрес источника")),
                ("raw_body", models.TextField(verbose_name="сырой request body")),
                ("error_text", models.TextField(verbose_name="текст ошибки")),
                ("service_name", models.CharField(max_length=100, verbose_name="сервис")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
            ],
            options={
                "verbose_name": "некорректное событие",
                "verbose_name_plural": "некорректные события",
                "ordering": ["-received_at"],
                "indexes": [
                    models.Index(fields=["received_at"], name="invalid_event_received_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Work",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="начало смены")),
                ("finished_at", models.DateTimeField(blank=True, null=True, verbose_name="завершение смены")),
                ("last_seen_at", models.DateTimeField(blank=True, null=True, verbose_name="последний heartbeat")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "работает сейчас"),
                            ("finished", "смена завершена нормально"),
                            ("expired", "смена зависла"),
                            ("cancelled", "смена отменена"),
                        ],
                        default="active",
                        max_length=16,
                        verbose_name="статус",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлена")),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="works",
                        to="machines.device",
                        verbose_name="устройство",
                    ),
                ),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="works",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="works",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "рабочая смена",
                "verbose_name_plural": "рабочие смены",
                "ordering": ["-started_at"],
                "indexes": [
                    models.Index(fields=["status"], name="work_status_idx"),
                    models.Index(fields=["machine", "status"], name="work_machine_status_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(status="active"),
                        fields=("machine",),
                        name="unique_active_work_per_machine",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="AuthSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создана")),
                ("expires_at", models.DateTimeField(verbose_name="истекает")),
                ("is_active", models.BooleanField(default=True, verbose_name="активна")),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="auth_sessions",
                        to="machines.device",
                        verbose_name="устройство",
                    ),
                ),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="auth_sessions",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="auth_sessions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="auth_sessions",
                        to="production.work",
                        verbose_name="смена",
                    ),
                ),
            ],
            options={
                "verbose_name": "сессия авторизации",
                "verbose_name_plural": "сессии авторизации",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Detail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("detail_number", models.IntegerField(verbose_name="номер детали")),
                ("event_time", models.DateTimeField(verbose_name="время события")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлена")),
                (
                    "detail_state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="details",
                        to="production.detailstate",
                        verbose_name="состояние детали",
                    ),
                ),
                (
                    "detail_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="details",
                        to="production.detailtype",
                        verbose_name="тип детали",
                    ),
                ),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="details",
                        to="machines.machine",
                        verbose_name="станок",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="details",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="details",
                        to="production.work",
                        verbose_name="смена",
                    ),
                ),
            ],
            options={
                "verbose_name": "деталь",
                "verbose_name_plural": "детали",
                "ordering": ["-event_time"],
                "indexes": [
                    models.Index(fields=["event_time"], name="detail_event_time_idx"),
                    models.Index(fields=["user", "event_time"], name="detail_user_event_time_idx"),
                    models.Index(fields=["machine", "event_time"], name="detail_machine_event_time_idx"),
                    models.Index(fields=["work"], name="detail_work_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "machine", "work", "detail_number"),
                        name="unique_detail_number_per_work",
                    ),
                ],
            },
        ),
    ]
