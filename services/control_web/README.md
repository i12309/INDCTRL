# control-web

Django-сервис для admin, dashboard, отчетов, экспорта CSV/XLSX и миграций общей БД.
Здесь находятся доменные модели INDCTRL и миграции PostgreSQL.

## Переменные окружения

Основные переменные: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CSRF_TRUSTED_ORIGINS`, `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `APP_TIMEZONE`.

## Запуск в Docker

```bash
docker compose up -d --build control-web
```

## Endpoint'ы

- `GET /health/` - состояние Django-сервиса.
- `GET /admin/` - Django admin.
- `GET /dashboard/` - временная страница dashboard.
- `GET /reports/` - временная страница отчетов.

## Диагностика и логи

```bash
docker compose logs -f control-web
docker compose exec control-web python manage.py check
docker compose exec control-web python manage.py migrate
```
