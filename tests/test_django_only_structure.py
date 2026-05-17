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
    """Единый web-интерфейс должен иметь вход, sidebar и Bootstrap."""

    urls = read("service/config/urls.py")
    base = read("service/templates/base.html")
    login = read("service/templates/registration/login.html")

    assert 'path("login/", RoleLoginView.as_view(), name="login")' in urls
    assert "bootstrap@5.3.8" in base
    assert "bootstrap@5.3.8" in login
    for label in ("Админка", "Справочники", "Отчеты"):
        assert label in base


def test_reports_include_invalid_events_page() -> None:
    """Некорректные события должны быть доступны как защищенный отчет."""

    report_urls = read("service/apps/reports/urls.py")
    report_views = read("service/apps/reports/views.py")

    assert 'path("invalid-events/", views.invalid_events, name="invalid_events")' in report_urls
    assert "@report_access_required\ndef invalid_events" in report_views
