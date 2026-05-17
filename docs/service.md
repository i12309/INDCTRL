# Django-сервис

`indctrl` - единственный прикладной сервис INDCTRL. Он заменяет прежние отдельные
auth/event сервисы и содержит web-интерфейс, admin, dashboard, reports, API для
ESP32 и миграции.

## Web URL

- `/admin/` - Django admin;
- `/dashboard/current-workers/` - активные смены и состояние heartbeat;
- `/reports/details/` - HTML-отчет по деталям;
- `/reports/details/export/csv/` - CSV-экспорт;
- `/reports/details/export/xlsx/` - XLSX-экспорт;
- `/health/` и `/health-web/` - health endpoint.

## API для ESP32

- `POST /api/device/workers`
- `POST /api/device/login`
- `POST /api/device/heartbeat`
- `POST /api/device/logout`
- `POST /api/device/detail`

API реализован обычными Django JSON views в `apps.api`.

## Роли

```text
admin      доступ к /admin/, dashboard и reports
director   доступ к dashboard и reports
manager    доступ к dashboard и reports
worker     нет доступа к reports и dashboard в первой версии
```

Для `/admin/` дополнительно нужен `is_staff=true`. Django superuser имеет полный
доступ.

## Миграции и static files

```bash
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
```
