"""Настройки Django для INDCTRL."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    """Прочитать булеву переменную окружения в формате, понятном администраторам."""

    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Разобрать переменную окружения со списком значений через запятую."""

    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change_me")
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts.apps.AccountsConfig",
    "apps.machines.apps.MachinesConfig",
    "apps.production.apps.ProductionConfig",
    "apps.schedules.apps.SchedulesConfig",
    "apps.api.apps.ApiConfig",
    "apps.reports.apps.ReportsConfig",
    "apps.dashboard.apps.DashboardConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.access.ui_access",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "indctrl"),
        "USER": os.getenv("POSTGRES_USER", "indctrl"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "change_me_strong_password"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = os.getenv("APP_TIMEZONE", "Europe/Berlin")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("DJANGO_STATIC_ROOT", "/app/staticfiles"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
HEARTBEAT_MAX_AGE_SECONDS = int(os.getenv("HEARTBEAT_MAX_AGE_SECONDS", "180"))
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "720"))
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

JAZZMIN_SETTINGS = {
    "site_title": "INDCTRL admin",
    "site_header": "INDCTRL",
    "site_brand": "INDCTRL",
    "welcome_sign": "Администрирование INDCTRL",
    "copyright": "INDCTRL",
    "search_model": [
        "accounts.User",
        "machines.Machine",
        "machines.Device",
        "production.Detail",
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "accounts",
        "machines",
        "schedules",
        "production",
        "auth",
    ],
    "icons": {
        "accounts.User": "fas fa-users",
        "accounts.Role": "fas fa-user-tag",
        "machines.Machine": "fas fa-industry",
        "machines.Device": "fas fa-microchip",
        "schedules.UserMachinePermission": "fas fa-key",
        "schedules.UserMachineSchedule": "fas fa-calendar-alt",
        "production.Work": "fas fa-user-clock",
        "production.AuthSession": "fas fa-id-badge",
        "production.Detail": "fas fa-cogs",
        "production.DetailType": "fas fa-tags",
        "production.DetailState": "fas fa-check-circle",
        "production.InvalidEvent": "fas fa-exclamation-triangle",
        "auth.Group": "fas fa-users-cog",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "default_theme_mode": "light",
    "navbar": "navbar-white navbar-light",
    "sidebar": "sidebar-light-primary",
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "no_navbar_border": True,
    "sidebar_nav_child_indent": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
