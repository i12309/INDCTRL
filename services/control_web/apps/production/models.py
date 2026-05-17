"""Производственные модели: смены, сессии, детали и ошибки событий."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from control_common.constants import (
    WORK_STATUS_ACTIVE,
    WORK_STATUS_CANCELLED,
    WORK_STATUS_EXPIRED,
    WORK_STATUS_FINISHED,
)


class DetailType(models.Model):
    """Справочник типов деталей."""

    code = models.CharField("код", max_length=64, unique=True)
    name = models.CharField("название", max_length=150)
    is_active = models.BooleanField("активен", default=True)
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлен", auto_now=True)

    class Meta:
        """Настройки справочника типов деталей."""

        ordering = ["code"]
        verbose_name = "тип детали"
        verbose_name_plural = "типы деталей"

    def __str__(self) -> str:
        """Вернуть название типа детали."""

        return self.name


class DetailState(models.Model):
    """Справочник состояний деталей."""

    code = models.CharField("код", max_length=32, unique=True)
    name = models.CharField("название", max_length=100)
    is_active = models.BooleanField("активно", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        """Настройки справочника состояний деталей."""

        ordering = ["code"]
        verbose_name = "состояние детали"
        verbose_name_plural = "состояния деталей"

    def __str__(self) -> str:
        """Вернуть название состояния детали."""

        return self.name


class Work(models.Model):
    """Рабочая смена пользователя на конкретном станке.

    Запись создается в момент успешного входа работника на ESP32. Пока
    `status='active'`, система считает, что станок занят этим работником.
    """

    STATUS_ACTIVE = WORK_STATUS_ACTIVE
    STATUS_FINISHED = WORK_STATUS_FINISHED
    STATUS_EXPIRED = WORK_STATUS_EXPIRED
    STATUS_CANCELLED = WORK_STATUS_CANCELLED

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "работает сейчас"),
        (STATUS_FINISHED, "смена завершена нормально"),
        (STATUS_EXPIRED, "смена зависла"),
        (STATUS_CANCELLED, "смена отменена"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="works")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="works")
    device = models.ForeignKey("machines.Device", verbose_name="устройство", on_delete=models.PROTECT, related_name="works")
    started_at = models.DateTimeField("начало смены", default=timezone.now)
    finished_at = models.DateTimeField("завершение смены", blank=True, null=True)
    last_seen_at = models.DateTimeField("последний heartbeat", blank=True, null=True)
    status = models.CharField("статус", max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        """Ограничения активной смены и индексы для текущего состояния цеха."""

        constraints = [
            # В первой версии один станок не может иметь две активные смены сразу.
            models.UniqueConstraint(
                fields=["machine"],
                condition=Q(status=WORK_STATUS_ACTIVE),
                name="unique_active_work_per_machine",
            ),
        ]
        indexes = [
            models.Index(fields=["status"], name="work_status_idx"),
            models.Index(fields=["machine", "status"], name="work_machine_status_idx"),
        ]
        ordering = ["-started_at"]
        verbose_name = "рабочая смена"
        verbose_name_plural = "рабочие смены"

    def __str__(self) -> str:
        """Вернуть краткое описание смены."""

        return f"{self.user} - {self.machine} ({self.status})"


class AuthSession(models.Model):
    """Сессия авторизации работника, возвращаемая ESP32 как `sessionID`.

    `event-service` использует UUID сессии, чтобы определить пользователя, станок и
    рабочую смену без доверия к значениям, пришедшим от устройства.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="auth_sessions")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="auth_sessions")
    device = models.ForeignKey("machines.Device", verbose_name="устройство", on_delete=models.PROTECT, related_name="auth_sessions")
    work = models.ForeignKey(Work, verbose_name="смена", on_delete=models.PROTECT, related_name="auth_sessions")
    created_at = models.DateTimeField("создана", auto_now_add=True)
    expires_at = models.DateTimeField("истекает")
    is_active = models.BooleanField("активна", default=True)

    class Meta:
        """Настройки сессий авторизации."""

        ordering = ["-created_at"]
        verbose_name = "сессия авторизации"
        verbose_name_plural = "сессии авторизации"

    def __str__(self) -> str:
        """Вернуть UUID сессии."""

        return str(self.id)


class Detail(models.Model):
    """Произведенная деталь в рамках конкретной рабочей смены."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="details")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="details")
    work = models.ForeignKey(Work, verbose_name="смена", on_delete=models.PROTECT, related_name="details")
    detail_number = models.IntegerField("номер детали")
    detail_type = models.ForeignKey(DetailType, verbose_name="тип детали", on_delete=models.PROTECT, related_name="details")
    detail_state = models.ForeignKey(DetailState, verbose_name="состояние детали", on_delete=models.PROTECT, related_name="details")
    event_time = models.DateTimeField("время события")
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        """Идемпотентность приема деталей и индексы отчетов."""

        constraints = [
            # Номер детали уникален только внутри смены конкретного работника на станке.
            models.UniqueConstraint(
                fields=["user", "machine", "work", "detail_number"],
                name="unique_detail_number_per_work",
            ),
        ]
        indexes = [
            models.Index(fields=["event_time"], name="detail_event_time_idx"),
            models.Index(fields=["user", "event_time"], name="detail_user_event_time_idx"),
            models.Index(fields=["machine", "event_time"], name="detail_machine_event_time_idx"),
            models.Index(fields=["work"], name="detail_work_idx"),
        ]
        ordering = ["-event_time"]
        verbose_name = "деталь"
        verbose_name_plural = "детали"

    def __str__(self) -> str:
        """Вернуть номер детали и станок."""

        return f"Деталь {self.detail_number} - {self.machine}"


class InvalidEvent(models.Model):
    """Некорректное входящее событие, которое не удалось сохранить как деталь."""

    received_at = models.DateTimeField("получено", default=timezone.now)
    source_ip = models.CharField("IP-адрес источника", max_length=64, blank=True, null=True)
    raw_body = models.TextField("сырой request body")
    error_text = models.TextField("текст ошибки")
    service_name = models.CharField("сервис", max_length=100)
    created_at = models.DateTimeField("создано", auto_now_add=True)

    class Meta:
        """Индекс времени нужен для быстрой диагностики последних ошибок."""

        indexes = [
            models.Index(fields=["received_at"], name="invalid_event_received_idx"),
        ]
        ordering = ["-received_at"]
        verbose_name = "некорректное событие"
        verbose_name_plural = "некорректные события"

    def __str__(self) -> str:
        """Вернуть сервис и время ошибки."""

        return f"{self.service_name} - {self.received_at}"
