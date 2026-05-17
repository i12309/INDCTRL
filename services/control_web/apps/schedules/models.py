"""Модели разрешений и расписаний работы на станках."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class UserMachinePermission(models.Model):
    """Базовое разрешение пользователю работать на станке."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="machine_permissions")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="user_permissions")
    is_allowed = models.BooleanField("разрешено", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        """Один пользователь имеет только одно базовое разрешение на станок."""

        constraints = [
            models.UniqueConstraint(fields=["user", "machine"], name="unique_user_machine_permission"),
        ]
        ordering = ["user", "machine"]
        verbose_name = "разрешение на станок"
        verbose_name_plural = "разрешения на станки"

    def __str__(self) -> str:
        """Вернуть пользователя, станок и состояние разрешения."""

        return f"{self.user} - {self.machine}: {self.is_allowed}"


class UserMachineSchedule(models.Model):
    """Расписание, по которому пользователь может работать на станке.

    Проверка выполняется по серверному времени. В первой версии смена не должна
    пересекать полночь, поэтому `time_from` обязан быть меньше или равен `time_to`.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="machine_schedules")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="user_schedules")
    weekday = models.PositiveSmallIntegerField("день недели")
    time_from = models.TimeField("время с")
    time_to = models.TimeField("время до")
    is_active = models.BooleanField("активно", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        """Ограничения расписания для понятных ошибок и защиты БД."""

        constraints = [
            models.CheckConstraint(
                check=Q(weekday__gte=1) & Q(weekday__lte=7),
                name="schedule_weekday_between_1_and_7",
            ),
            models.CheckConstraint(
                check=Q(time_from__lte=models.F("time_to")),
                name="schedule_time_from_lte_time_to",
            ),
        ]
        ordering = ["user", "machine", "weekday", "time_from"]
        verbose_name = "расписание работы на станке"
        verbose_name_plural = "расписания работы на станках"

    def clean(self) -> None:
        """Запретить расписание, которое пересекает полночь."""

        if self.time_from and self.time_to and self.time_from > self.time_to:
            raise ValidationError("В первой версии смена не может пересекать полночь")

    def __str__(self) -> str:
        """Вернуть краткое описание расписания."""

        return f"{self.user} - {self.machine}: {self.weekday} {self.time_from}-{self.time_to}"
