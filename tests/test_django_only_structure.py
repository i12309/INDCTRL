"""Проверки структуры Django-only проекта."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    """Прочитать текстовый файл проекта."""

    return (ROOT / path).read_text(encoding="utf-8")


def test_compose_contains_only_indctrl_postgres_nginx() -> None:
    """В Docker Compose не должно быть отдельных auth/event сервисов."""

    compose = read("docker-compose.yml")

    assert "  indctrl:" in compose
    assert "  postgres:" in compose
    assert "  nginx:" in compose
    assert "  django:" not in compose
    assert "auth-service" not in compose
    assert "event-service" not in compose


def test_django_code_lives_in_single_service_directory() -> None:
    """Единственное Django-приложение должно лежать в `service/`."""

    assert (ROOT / "service" / "manage.py").is_file()
    assert (ROOT / "service" / "apps" / "api" / "views.py").is_file()
    assert not (ROOT / "services").exists()


def test_nginx_routes_to_single_django_upstream() -> None:
    """Nginx должен проксировать запросы в единый Django upstream."""

    nginx_config = read("docker/nginx/default.conf")

    assert "upstream indctrl" in nginx_config
    assert "proxy_pass http://indctrl" in nginx_config
    assert "upstream django" not in nginx_config
    assert "auth_service" not in nginx_config
    assert "event_service" not in nginx_config


def test_esp32_api_uses_new_urls() -> None:
    """Документация должна описывать новые Django API URL."""

    docs = read("docs/esp32-api.md")

    for url in (
        "/api/device/workers",
        "/api/device/login",
        "/api/device/heartbeat",
        "/api/device/logout",
        "/api/device/detail",
    ):
        assert url in docs

    assert "/api/auth" not in docs
    assert "/api/events" not in docs


def test_web_interface_has_login_sidebar_and_bootstrap() -> None:
    """Единый web-интерфейс должен иметь вход, sidebar и локальный Bootstrap."""

    urls = read("service/config/urls.py")
    base = read("service/templates/base.html")
    login = read("service/templates/registration/login.html")

    assert 'path("login/", IndctrlLoginView.as_view(), name="login")' in urls
    assert "vendor/bootstrap/bootstrap.min.css" in base
    assert "vendor/bootstrap/bootstrap.bundle.min.js" in base
    assert "vendor/bootstrap/bootstrap.min.css" in login
    assert "cdn.jsdelivr.net" not in base
    assert "cdn.jsdelivr.net" not in login
    assert (ROOT / "service" / "static" / "vendor" / "bootstrap" / "bootstrap.min.css").is_file()
    assert (
        ROOT / "service" / "static" / "vendor" / "bootstrap" / "bootstrap.bundle.min.js"
    ).is_file()
    assert "form.role" not in login
    assert "Панель администратора" in base
    assert "Отчеты" in base
    assert "Админка" not in base
    assert "Справочники" not in base


def test_access_uses_groups_and_permissions_instead_of_roles() -> None:
    """Web и ESP32 API должны проверять Django permissions, а не Role."""

    models = read("service/apps/accounts/models.py")
    admin = read("service/apps/accounts/admin.py")
    access = read("service/apps/access.py")
    api_views = read("service/apps/api/views.py")

    assert "class Role" not in models
    assert "role =" not in models
    assert "RoleAdmin" not in admin
    assert "use_admin_panel" not in models
    assert "view_reports" in models
    assert "use_esp32_api" in models
    assert "PERM_USE_ADMIN_PANEL" not in access
    assert "has_perm(PERM_VIEW_REPORTS)" in access
    assert "has_perm(PERM_USE_ESP32_API)" in api_views
    assert "role__code" not in api_views
    assert "user.role" not in api_views


def test_django_admin_uses_jazzmin_without_cdn() -> None:
    """Django admin должен использовать готовую offline-тему Jazzmin."""

    settings = read("service/config/settings.py")
    requirements = read("service/requirements.txt")

    assert "django-jazzmin" in requirements
    assert '"jazzmin",' in settings
    assert settings.index('"jazzmin",') < settings.index('"django.contrib.admin",')
    assert "JAZZMIN_SETTINGS" in settings
    assert "JAZZMIN_UI_TWEAKS" in settings
    assert "INDCTRL" in settings
    assert "cdn.jsdelivr.net" not in settings
    assert "https://cdn" not in settings


def test_reports_include_invalid_events_page() -> None:
    """Некорректные события должны быть доступны как защищенный отчет."""

    report_urls = read("service/apps/reports/urls.py")
    report_views = read("service/apps/reports/views.py")

    assert 'path("invalid-events/", views.invalid_events, name="invalid_events")' in report_urls
    assert "@report_access_required\ndef invalid_events" in report_views


def test_production_compose_uses_prebuilt_image() -> None:
    """Production compose должен запускать готовые образы без сборки."""

    production_compose = read("compose.production.yml")

    assert "image: indctrl/indctrl:0.1.0" in production_compose
    assert "build:" not in production_compose
    assert "latest" not in production_compose


def test_env_and_makefile_are_operational_minimum() -> None:
    """Env и Makefile не должны содержать лишние dev-настройки."""

    env_example = read(".env.example")
    makefile = read("Makefile")

    assert "DJANGO_PORT" not in env_example
    assert "\ntest:" not in makefile
    assert "\nlint:" not in makefile
    assert "\nformat:" not in makefile
