"""URL-маршруты отчетов."""

from django.urls import path

from apps.reports import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("details/", views.details, name="details"),
    path("details/export/csv/", views.details_export_csv, name="details_export_csv"),
    path("details/export/xlsx/", views.details_export_xlsx, name="details_export_xlsx"),
    path("invalid-events/", views.invalid_events, name="invalid_events"),
]
