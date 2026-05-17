"""Формы фильтров отчетов."""

from django import forms
from django.contrib.auth import get_user_model

from apps.machines.models import Machine
from apps.production.models import DetailState, DetailType, Work


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
    work = forms.ModelChoiceField(
        label="Смена",
        queryset=Work.objects.all().select_related("user", "machine").order_by("-started_at"),
        required=False,
    )
    detail_type = forms.ModelChoiceField(
        label="Тип детали",
        queryset=DetailType.objects.all().order_by("name"),
        required=False,
    )
    detail_state = forms.ModelChoiceField(
        label="Состояние",
        queryset=DetailState.objects.all().order_by("name"),
        required=False,
    )
