# Задача 06. Реализовать Django `control-web`: админка и управление справочниками

## Цель

Настроить Django-сервис `control-web` для управления пользователями, ролями, станками, ESP32, справочниками, правами и расписаниями через Django admin.

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

## Назначение `control-web`

`control-web` содержит:

```text
/admin/      Django admin для администратора;
/reports/    отчеты;
/dashboard/  экран текущей работы станков;
/health/     проверка состояния сервиса.
```

Эта задача касается именно admin-части.

## Доступ к админке

Доступ к `/admin/`:

```text
только пользователь с ролью admin;
пользователь должен быть is_active=true;
пользователь должен быть is_staff=true.
```

Если Django superuser есть, он тоже должен иметь доступ.

## Настроить admin для моделей

Добавить админку для:

```text
Role
User
Machine
Device
DetailType
DetailState
UserMachinePermission
UserMachineSchedule
Work
AuthSession
Detail
InvalidEvent
```

## Требования к отображению

### User

`list_display`:

```text
id, username, full_name, role, is_active, is_staff
```

Фильтры:

```text
role, is_active, is_staff
```

Поиск:

```text
username, full_name
```

### Machine

`list_display`:

```text
id, name, inventory_number, is_active
```

### Device

`list_display`:

```text
id, mac_address, machine, name, is_active
```

Поиск по `mac_address`.

### Work

`list_display`:

```text
id, user, machine, status, started_at, finished_at, last_seen_at
```

Фильтры:

```text
status, machine, started_at
```

Активные смены должны быть хорошо видны администратору.

### Detail

Сущность детали редактировать не надо. Только просмотр.

Требования:

- запретить добавление через admin;
- запретить изменение через admin;
- разрешить просмотр;
- можно разрешить удаление только superuser или полностью запретить удаление.

`list_display`:

```text
id, event_time, user, machine, work, detail_number, detail_type, detail_state
```

Фильтры:

```text
event_time, machine, user, detail_type, detail_state
```

### InvalidEvent

Только просмотр.

`list_display`:

```text
id, received_at, source_ip, service_name, short_error
```

## Управление правами на станки

В admin должна быть возможность назначить:

```text
какой пользователь может работать на каком станке;
разрешено или запрещено;
```

Через `UserMachinePermission`.

## Управление расписанием

Через `UserMachineSchedule` администратор задает:

```text
пользователь;
станок;
день недели;
время с;
время по;
активность правила.
```

Добавить валидацию:

```text
weekday от 1 до 7;
time_from < time_to;
```

## Health endpoint

Реализовать:

```http
GET /health/
```

Ответ:

```json
{"status": "ok", "service": "control-web"}
```

## Docker

Django должен запускаться через Gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Static files:

```bash
python manage.py collectstatic --noinput
```

В Nginx:

```text
/admin/      -> control-web:8000
/static/     -> static volume
```

## Документация

В `services/control_web/README.md` описать:

- назначение Django-сервиса;
- как выполнить миграции;
- как создать администратора;
- как открыть `/admin/`;
- какие справочники редактируются;
- какие сущности только просматриваются;
- как смотреть логи контейнера.

## Комментарии

У всех кастомных `ModelAdmin`-классов добавить краткие комментарии на русском, например:

```python
class DetailAdmin(admin.ModelAdmin):
    """Админка для просмотра произведенных деталей.

    Детали создаются только через event-service, поэтому ручное добавление и изменение запрещены.
    """
```

## Критерии приемки

- `/admin/` доступен только администратору.
- Через admin можно редактировать пользователей, станки, ESP32, справочники, права и расписания.
- Детали и некорректные события доступны только для просмотра.
- Static files корректно отдаются через Nginx.
- Документация по `control-web` создана.
