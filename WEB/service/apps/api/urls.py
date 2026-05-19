"""URL API для ESP32."""

from django.urls import path

from apps.api import views

urlpatterns = [
    path("device/workers", views.device_workers, name="api_device_workers"),
    path("device/login", views.device_login, name="api_device_login"),
    path("device/heartbeat", views.device_heartbeat, name="api_device_heartbeat"),
    path("device/logout", views.device_logout, name="api_device_logout"),
    path("device/detail", views.device_detail, name="api_device_detail"),
    path("device/details", views.device_details, name="api_device_details"),
]
