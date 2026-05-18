# Django-сервис

`indctrl` - единственный прикладной сервис INDCTRL. Он заменяет прежние отдельные
auth/event сервисы и содержит web-интерфейс, admin, dashboard, reports, API для
ESP32 и миграции.

## Web URL

- `/login/` - панель авторизации;
- `/admin/` - Django admin;
- `/dashboard/` - главная страница единого интерфейса;
- `/dashboard/current-workers/` - активные смены и состояние heartbeat;
- `/reports/details/` - HTML-отчет по деталям;
- `/reports/details/export/csv/` - CSV-экспорт;
- `/reports/details/export/xlsx/` - XLSX-экспорт;
- `/reports/invalid-events/` - некорректные события API;
- `/health/` и `/health-web/` - health endpoint.

Bootstrap лежит локально в `service/static/vendor/bootstrap/`; web-интерфейс не
обращается к CDN и работает в сети без интернета.

## API для ESP32

- `POST /api/device/workers`
- `POST /api/device/login`
- `POST /api/device/heartbeat`
- `POST /api/device/logout`
- `POST /api/device/detail`

API реализован обычными Django JSON views в `apps.api`.

## Группы и права

```text
accounts.view_reports      dashboard и reports
accounts.use_esp32_api     работа через ESP32 API
```

Для `/admin/` нужен стандартный флаг `is_staff=true`. Разделы и действия внутри
admin определяются стандартными правами моделей `view/add/change/delete`. Django
superuser имеет полный доступ. Группы используются как контейнеры прав, поэтому
API и отчеты проверяют `user.has_perm(...)`, а не название группы.

## Миграции и static files

```bash
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
```
