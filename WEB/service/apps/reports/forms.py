"""Формы фильтров отчетов."""

from django import forms
from django.contrib.auth import get_user_model

from apps.machines.models import Machine
from apps.production.models import DetailType


class DetailReportFilterForm(forms.Form):
    """Форма фильтров отчета по произведенным деталям."""

    date_from = forms.DateField(
        label="Дата с",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Дата по",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    machine = forms.ModelChoiceField(
        label="Станок",
        queryset=Machine.objects.all().order_by("name"),
        required=False,
    )
    user = forms.ModelChoiceField(
        label="Работник",
        queryset=get_user_model().objects.all().order_by("full_name"),
        required=False,
    )
    work = forms.IntegerField(
        label="ID смены",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Например, 123"}),
    )
    detail_type = forms.ModelChoiceField(
        label="Тип детали",
        queryset=DetailType.objects.all().order_by("name"),
        required=False,
    )
    quality_min = forms.IntegerField(
        label="Качество от, %",
        min_value=0,
        max_value=100,
        required=False,
    )
    quality_max = forms.IntegerField(
        label="Качество до, %",
        min_value=0,
        max_value=100,
        required=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        """Добавить Bootstrap-классы к полям фильтра."""

        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self) -> dict:
        """Проверить согласованность диапазона качества."""

        cleaned_data = super().clean()
        quality_min = cleaned_data.get("quality_min")
        quality_max = cleaned_data.get("quality_max")
        if quality_min is not None and quality_max is not None and quality_min > quality_max:
            raise forms.ValidationError("Минимальное качество не может быть больше максимального")
        return cleaned_data
