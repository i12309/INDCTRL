# Задача 02. Реализовать Django-модели предметной области и миграции PostgreSQL

## Цель

Описать структуру БД через Django-модели и создать миграции. Django является главным источником структуры БД.

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

## Важное правило

FastAPI-сервисы не должны создавать таблицы и не должны управлять миграциями. Все таблицы создаются миграциями Django из сервиса `control-web`.

## Django-приложения и модели

### `apps.accounts`

Модели:

```text
Role
User
```

#### Role

Поля:

```text
id
code           unique, например admin/director/manager/worker
name           человекочитаемое название
is_active
created_at
updated_at
```

Начальные роли:

```text
admin      администратор
director   директор
manager    менеджер
worker     работник
```

#### User

Создать кастомную модель пользователя Django. Использовать ее с самого начала проекта, чтобы потом не менять AUTH_USER_MODEL.

Поля:

```text
id
username       логин. Для ESP32 можно использовать выбранного пользователя по ID.
full_name      ФИО работника
password       стандартное поле Django с password hash
role           FK на Role
is_active
is_staff
is_superuser
created_at
updated_at
```

Требования:

- `AUTH_USER_MODEL` должен указывать на эту модель.
- Для паролей использовать стандартное Django-хеширование.
- FastAPI `auth-service` будет читать поле `password` и проверять пароль через общий helper.

### `apps.machines`

Модели:

```text
Machine
Device
```

#### Machine

Поля:

```text
id
name
inventory_number nullable/blank
comment nullable/blank
is_active
created_at
updated_at
```

#### Device

ESP32-устройство. Один ESP32 всегда закреплен за одним станком.

Поля:

```text
id
mac_address unique
machine FK Machine
name nullable/blank
is_active
created_at
updated_at
```

Требования:

- `machineID` не должен приниматься от ESP32 как доверенное значение.
- Станок определяется только через `mac_address` устройства.

### `apps.production`

Модели:

```text
DetailType
DetailState
Work
AuthSession
Detail
InvalidEvent
```

#### DetailType

Справочник типов деталей.

Поля:

```text
id
code unique
name
is_active
created_at
updated_at
```

#### DetailState

Справочник состояний деталей.

Поля:

```text
id
code unique
name
is_active
created_at
updated_at
```

Начальные состояния:

```text
working      рабочая
defect       брак
undefined    не определено
```

#### Work

Рабочая смена. Создается при успешном входе работника на ESP32.

Поля:

```text
id
user FK User
machine FK Machine
device FK Device
started_at
finished_at nullable
last_seen_at nullable
status
created_at
updated_at
```

Статусы:

```text
active     работает сейчас
finished   смена завершена нормально
expired    смена зависла или ESP32 давно не отвечал
cancelled  смена отменена администратором
```

Ограничение:

```text
Один пользователь теоретически может работать за несколькими станками.
Один станок в первой версии не должен иметь двух активных работников одновременно.
```

Создать partial unique index:

```text
UNIQUE machine WHERE status = 'active'
```

В Django это сделать через `UniqueConstraint(condition=...)`.

#### AuthSession

Сессия работника, созданная после успешного входа на ESP32.

Поля:

```text
id UUID primary key
user FK User
machine FK Machine
device FK Device
work FK Work
created_at
expires_at
is_active
```

Требования:

- `sessionID` возвращается ESP32 после успешного входа.
- `event-service` должен определять `user_id`, `machine_id`, `work_id` через `sessionID`.

#### Detail

Основная таблица произведенных деталей.

Поля:

```text
id
user FK User
machine FK Machine
work FK Work
detail_number integer
detail_type FK DetailType
detail_state FK DetailState
event_time timestamp
created_at
updated_at
```

Ключевое ограничение идемпотентности:

```text
UNIQUE (user_id, machine_id, work_id, detail_number)
```

Это означает, что номер детали уникален только внутри рабочей смены конкретного пользователя на конкретном станке.

#### InvalidEvent

Таблица битых или некорректных входящих событий.

Поля:

```text
id
received_at
source_ip nullable/blank
raw_body text
error_text text
service_name text
created_at
```

Требования:

- Сохранять сюда сырой JSON или сырой request body, если событие невозможно обработать.
- Если событие корректно распарсилось и сохранено в `Detail`, сырой JSON хранить не надо.

### `apps.schedules`

Модели:

```text
UserMachinePermission
UserMachineSchedule
```

#### UserMachinePermission

Базовое разрешение пользователю работать на станке.

Поля:

```text
id
user FK User
machine FK Machine
is_allowed
created_at
updated_at
```

Ограничение:

```text
UNIQUE (user_id, machine_id)
```

#### UserMachineSchedule

Расписание, по которому пользователь может работать на станке.

Поля:

```text
id
user FK User
machine FK Machine
weekday integer 1..7
time_from time
time_to time
is_active
created_at
updated_at
```

Требования:

- Проверка расписания выполняется по времени сервера.
- В первой версии можно считать, что смена не пересекает полночь. Если `time_from > time_to`, вернуть понятную ошибку в админке.

## Seed-данные

Создать management command или data migration для начальных данных:

```text
roles: admin, director, manager, worker
detail_states: working, defect, undefined
```

Можно добавить тестовые типы деталей только в dev-режиме, но не в production по умолчанию.

## Индексы

Добавить индексы:

```text
Device.mac_address
Work.status
Work.machine + status
Detail.event_time
Detail.user + event_time
Detail.machine + event_time
Detail.work
InvalidEvent.received_at
```

## Комментарии и понятность

В каждой Django-модели добавить русскоязычный docstring:

```python
class Work(models.Model):
    """Рабочая смена пользователя на конкретном станке.

    Запись создается в момент успешного входа работника на ESP32.
    Пока status='active', директор может видеть, что пользователь работает за станком.
    """
```

Сложные constraints и индексы прокомментировать рядом с `Meta`.

## Критерии приемки

- `docker compose exec control-web python manage.py makemigrations` создает миграции.
- `docker compose exec control-web python manage.py migrate` успешно применяет миграции.
- В БД есть все перечисленные таблицы.
- Есть начальные роли и состояния деталей.
- Нельзя создать две активные смены на один станок.
- Нельзя создать дубль детали с одинаковыми `user_id`, `machine_id`, `work_id`, `detail_number`.
- Django admin видит созданные модели.
