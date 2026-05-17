"""Модели станков и ESP32-устройств."""

from django.db import models


class Machine(models.Model):
    """Производственный станок.

    Станок является бизнес-объектом, к которому привязываются устройства ESP32,
    разрешения пользователей, смены и произведенные детали.
    """

    name = models.CharField("название", max_length=150)
    inventory_number = models.CharField("инвентарный номер", max_length=100, blank=True, null=True)
    comment = models.TextField("комментарий", blank=True, null=True)
    is_active = models.BooleanField("активен", default=True)
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлен", auto_now=True)

    class Meta:
        """Настройки отображения станков."""

        ordering = ["name"]
        verbose_name = "станок"
        verbose_name_plural = "станки"

    def __str__(self) -> str:
        """Вернуть название станка."""

        return self.name


class Device(models.Model):
    """ESP32-устройство, закрепленное за конкретным станком.

    Станок определяется по `mac_address`, потому что `machineID` из запроса ESP32
    нельзя считать доверенным источником.
    """

    mac_address = models.CharField("MAC-адрес", max_length=32, unique=True)
    machine = models.ForeignKey(Machine, verbose_name="станок", on_delete=models.PROTECT, related_name="devices")
    name = models.CharField("название", max_length=150, blank=True, null=True)
    is_active = models.BooleanField("активно", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        """Настройки устройств и индексов поиска по ESP32."""

        indexes = [
            models.Index(fields=["mac_address"], name="device_mac_address_idx"),
        ]
        ordering = ["mac_address"]
        verbose_name = "ESP32-устройство"
        verbose_name_plural = "ESP32-устройства"

    def __str__(self) -> str:
        """Вернуть MAC-адрес и название устройства."""

        return self.name or self.mac_address
