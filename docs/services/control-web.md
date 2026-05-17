# control-web

`control-web` - Django-сервис для административного управления, dashboard,
отчетов, экспорта CSV/XLSX и миграций общей PostgreSQL-БД.

## Основные URL

### /admin/

Назначение: Django admin для управления справочниками и настройками.

Через admin редактируются роли, пользователи, станки, ESP32-устройства, типы
деталей, состояния деталей, разрешения и расписания. `Detail` и `InvalidEvent`
в admin доступны как диагностические данные; детали штатно создаются только
через `event-service`.

### /dashboard/current-workers/

Назначение: показать активные смены: работник, станок, время начала, последний
heartbeat и состояние связи.

Источник данных: `works` со статусом `active`, связанные `users`, `machines` и
`devices`.

### /reports/details/

Назначение: HTML-отчет по произведенным деталям.

Поддерживаются фильтры: дата с, дата по, станок, работник, смена, тип детали,
состояние детали. На странице есть пагинация и итоги.

### /reports/details/export/csv/

Назначение: CSV-экспорт отчета деталей с теми же фильтрами, что и HTML-отчет.

Экспорт ограничен лимитом строк, чтобы случайный запрос не перегрузил сервер.

### /reports/details/export/xlsx/

Назначение: XLSX-экспорт отчета деталей с теми же фильтрами и итогами.

Файл формируется сервисным кодом `apps.reports.services`.

## Роли и доступ

```text
admin      доступ к /admin/, dashboard и reports
director   доступ к dashboard и reports
manager    доступ к dashboard и reports
worker     нет доступа к reports и dashboard в первой версии
```

Дополнительно для `/admin/` пользователь должен иметь `is_staff=true`.
Django superuser имеет полный доступ.

Проверка доступа к dashboard и reports вынесена в `apps.access`: разрешены роли
`admin`, `director`, `manager`, а также superuser.

## Служебные URL

- `GET /health/` - health endpoint внутри Docker-сети;
- `GET /health-web/` - health endpoint через Nginx.

## Миграции и static files

```bash
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
```

Django-модели и миграции `control-web` являются источником структуры БД для
всех сервисов INDCTRL.
