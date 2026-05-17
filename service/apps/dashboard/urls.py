"""URL-маршруты dashboard."""

from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("current-workers/", views.current_workers, name="current_workers"),
]
