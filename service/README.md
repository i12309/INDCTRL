# Django INDCTRL

Единое Django-приложение INDCTRL. Содержит admin, dashboard, отчеты, CSV/XLSX
экспорт, API для ESP32 и миграции PostgreSQL.

## Переменные окружения

Основные переменные: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `POSTGRES_DB`,
`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`,
`APP_TIMEZONE`, `SESSION_TTL_MINUTES`, `HEARTBEAT_MAX_AGE_SECONDS`.

## Запуск в Docker

```bash
docker compose up -d --build indctrl
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
```

## API для ESP32

- `POST /api/device/workers`
- `POST /api/device/login`
- `POST /api/device/heartbeat`
- `POST /api/device/logout`
- `POST /api/device/detail`

## Web

- `/admin/`
- `/dashboard/current-workers/`
- `/reports/details/`
- `/reports/details/export/csv/`
- `/reports/details/export/xlsx/`
- `/health/`

Bootstrap хранится локально в `static/vendor/bootstrap/`, поэтому интерфейс не
требует доступа в интернет после установки.
Django admin использует тему `django-jazzmin`; ее static-файлы поставляются через
Python-пакет и собираются обычной командой `collectstatic`.

## Диагностика

```bash
docker compose logs -f indctrl
docker compose exec indctrl python manage.py check
docker compose exec indctrl python manage.py migrate
```
