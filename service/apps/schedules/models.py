"""Модели расписаний работы на станках."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class UserMachineSchedule(models.Model):
    """Расписание, по которому пользователь может работать на станке.

    Пустой день недели не ограничивает доступ по дням. Пустые `time_from` и
    `time_to` не ограничивают доступ по времени. Если время указано, смена не
    должна пересекать полночь.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="пользователь", on_delete=models.PROTECT, related_name="machine_schedules")
    machine = models.ForeignKey("machines.Machine", verbose_name="станок", on_delete=models.PROTECT, related_name="user_schedules")
    weekday = models.PositiveSmallIntegerField("день недели", blank=True, null=True)
    time_from = models.TimeField("время с", blank=True, null=True)
    time_to = models.TimeField("время до", blank=True, null=True)
    is_active = models.BooleanField("активно", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        """Ограничения расписания для понятных ошибок и защиты БД."""

        constraints = [
            models.CheckConstraint(
                check=Q(weekday__isnull=True) | (Q(weekday__gte=1) & Q(weekday__lte=7)),
                name="schedule_weekday_null_or_between_1_and_7",
            ),
            models.CheckConstraint(
                check=(
                    Q(time_from__isnull=True, time_to__isnull=True)
                    | (
                        Q(time_from__isnull=False, time_to__isnull=False)
                        & Q(time_from__lt=models.F("time_to"))
                    )
                ),
                name="schedule_time_empty_or_from_lt_to",
            ),
        ]
        ordering = ["user", "machine", "weekday", "time_from"]
        verbose_name = "расписание работы на станке"
        verbose_name_plural = "расписания работы на станках"

    def clean(self) -> None:
        """Запретить расписание, которое пересекает полночь."""

        if bool(self.time_from) != bool(self.time_to):
            raise ValidationError("Время начала и окончания нужно заполнять вместе")
        if self.time_from and self.time_to and self.time_from >= self.time_to:
            raise ValidationError("Время начала должно быть раньше времени окончания")

    def __str__(self) -> str:
        """Вернуть краткое описание расписания."""

        weekday = self.weekday if self.weekday is not None else "любой день"
        time_range = f"{self.time_from}-{self.time_to}" if self.time_from else "любое время"
        return f"{self.user} - {self.machine}: {weekday} {time_range}"
