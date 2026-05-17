# Задача 09. Подготовить документацию для production-запуска на Linux-сервере

## Цель

Сделать понятную инструкцию для администратора предприятия: как установить Docker, настроить проект, запустить систему, обновлять ее и смотреть логи.

## Общие обязательные требования

- Проект называется `INDCTRL`.
- Язык: Python 3.12+.
- База данных: PostgreSQL.
- Запуск в production: Docker Compose на одном Linux-сервере.
- Сервисы:
  - `auth-service` — FastAPI-сервис авторизации работников на ESP32;
  - `event-service` — FastAPI-сервис приема событий о произведенных деталях;
  - `control-web` — Django-сервис, который содержит админку, dashboard и отчеты;
  - `postgres` — общая PostgreSQL-БД;
  - `nginx` — единая точка входа для HTTP.
- Админка и отчеты должны быть в одном Django-сервисе `control-web`. Внутри Django их надо разделить по приложениям/модулям.
- Django-модели и Django migrations являются основным источником структуры БД.
- FastAPI-сервисы работают с этой же БД напрямую через общий пакет и SQL-запросы, но не запускают миграции.
- Весь код должен быть понятен программисту, который плохо знает Python, FastAPI и Django.
- Все публичные классы, Django-модели, Pydantic-схемы, функции, методы и сервисные классы должны иметь докстринги или комментарии на русском языке.
- Сложная бизнес-логика должна быть пояснена комментариями на русском языке: проверки прав, расписаний, активных смен, идемпотентности, обработки дублей и ошибок.
- Комментарии должны объяснять смысл и причину решения, а не дублировать очевидное действие кода.
- В каждом сервисе должна быть собственная документация `README.md`: назначение, переменные окружения, запуск в Docker, основные endpoint'ы, диагностика и просмотр логов.

## Документы

Создать:

```text
docs/linux/install-docker.md
docs/linux/first-run.md
docs/linux/update.md
docs/linux/logs.md
docs/linux/https.md
docs/env.md
```

## `install-docker.md`

Описать:

```text
какая ОС ожидается: Linux;
что нужен Docker Engine;
что нужен Docker Compose plugin;
как проверить установку docker --version;
как проверить docker compose version;
что пользователь должен иметь права запускать docker;
```

Не привязывать инструкцию жестко к одному дистрибутиву, но можно привести пример для Ubuntu/Debian.

## `first-run.md`

Описать пошаговый запуск:

```bash
cd /opt
git clone <repo-url> INDCTRL
cd INDCTRL
cp .env.example .env
nano .env
docker compose up -d --build
docker compose ps
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose exec control-web python manage.py createsuperuser
```

Проверки:

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

## `update.md`

Описать обновление:

```bash
cd /opt/INDCTRL
git pull
docker compose build
docker compose up -d
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose ps
```

Добавить предупреждение:

```text
Перед обновлением production-системы сделать backup PostgreSQL.
```

## `logs.md`

Описать команды:

```bash
docker compose logs -f
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
docker compose logs -f postgres
docker compose ps
docker compose restart auth-service
docker compose restart event-service
docker compose restart control-web
```

## `https.md`

Описать, что для HTTPS потребуется:

```text
сертификат;
приватный ключ;
доменное имя или внутреннее DNS-имя;
настройка Nginx;
доверие сертификату на рабочих компьютерах и ESP32.
```

Варианты:

```text
самоподписанный сертификат;
внутренний центр сертификации предприятия;
нормальный домен и публичный сертификат.
```

HTTPS не включать в первой версии как обязательное требование, но подготовить место в Nginx-конфиге и документации.

## `env.md`

Описать все переменные `.env`:

```text
APP_ENV
APP_TIMEZONE
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
SESSION_TTL_MINUTES
HEARTBEAT_MAX_AGE_SECONDS
```

Для каждой переменной:

```text
назначение;
пример значения;
можно ли менять после запуска;
нужно ли хранить в секрете.
```

## systemd

Docker Compose можно запускать вручную, но подготовить пример unit-файла:

```text
deploy/systemd/INDCTRL.service.example
```

Задача unit-файла:

```text
поднять docker compose проект после старта сервера;
остановить проект при остановке сервера;
```

При этом в документации указать, что Docker restart policies уже помогают автоматически перезапускать контейнеры.

## Критерии приемки

- Администратор может поднять систему по документации без знания Python.
- Описан первый запуск.
- Описано обновление.
- Описан просмотр логов.
- Описано, что нужно для HTTPS.
- Описаны переменные окружения.
