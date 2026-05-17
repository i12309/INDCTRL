# control-web

Django-сервис для `/admin/`, `/dashboard/`, `/reports/`, экспорта CSV/XLSX и
миграций общей PostgreSQL-БД. Django-модели и миграции `control-web` являются
главным источником структуры БД для всего проекта INDCTRL.

## Переменные окружения

Основные переменные: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CSRF_TRUSTED_ORIGINS`, `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `APP_TIMEZONE`.

## Запуск в Docker

```bash
docker compose up -d --build control-web
```

Django запускается через Gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Миграции и static files

```bash
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
```

Nginx отдает `/static/` из общего volume `static_data`.

## Администратор

Создание администратора:

```bash
docker compose exec control-web python manage.py createsuperuser
```

Админка доступна по адресу `http://localhost/admin/`.

Доступ к `/admin/` разрешен только пользователю, у которого:

- `is_active=true`;
- `is_staff=true`;
- роль `admin`.

Django superuser также имеет доступ.

## Что редактируется в admin

- роли;
- пользователи;
- станки;
- ESP32-устройства;
- типы деталей;
- состояния деталей;
- разрешения пользователя на станок;
- расписания работы пользователя на станке;
- рабочие смены и сессии авторизации для административного контроля.

## Что только просматривается

- `Detail` - детали создаются только через `event-service`; добавление и изменение
  через admin запрещены, удаление доступно только superuser;
- `InvalidEvent` - некорректные события создаются сервисами и нужны для диагностики,
  поэтому в admin они доступны только для просмотра.

## Endpoint'ы

- `GET /health/` - состояние Django-сервиса;
- `GET /admin/` - Django admin;
- `GET /dashboard/` - dashboard;
- `GET /reports/` - отчеты.

## Диагностика и логи

```bash
docker compose logs -f control-web
docker compose exec control-web python manage.py check
docker compose exec control-web python manage.py migrate
```
