# База данных

Рабочая БД проекта - PostgreSQL. Схема создается миграциями Django-сервиса
`control-web`; FastAPI-сервисы читают и пишут эти же таблицы напрямую через SQL,
но не управляют миграциями.

В коде Django используются физические имена таблиц с префиксами приложений
(`accounts_role`, `production_detail` и т.д.). В документации ниже рядом указаны
логические имена из технического задания.

## Ключевые правила

- `machineID` определяется по `Device.mac_address` ESP32. ID станка из запроса
  устройства не считается доверенным источником.
- `Work` создается при успешном `POST /api/auth/login`.
- В первой версии на один станок может быть только один активный `Work`.
- Деталь уникальна по `user_id`, `machine_id`, `work_id`, `detail_number`.
  Это обеспечивает идемпотентность `event-service`.
- `sessionID` из `AuthSession` является главным источником `user_id`,
  `machine_id` и `work_id` для событий деталей.

## Таблицы

### roles (`accounts_role`)

Назначение: справочник ролей пользователей.

Ключевые поля: `id`, `code`, `name`, `is_active`, `created_at`, `updated_at`.

Индексы и ограничения: `code` уникален.

Пишет: `control-web` через миграции seed и admin.

Читает: `control-web`, `auth-service`.

### users (`accounts_user`)

Назначение: учетные записи сотрудников и администраторов.

Ключевые поля: `id`, `username`, `password`, `full_name`, `role_id`,
`is_active`, `is_staff`, `is_superuser`.

Индексы и ограничения: `username` уникален; `role_id` защищен через
`on_delete=PROTECT`; пароль хранится как Django password hash.

Пишет: `control-web`.

Читает: `control-web`, `auth-service`, `event-service` косвенно через связи,
dashboard и reports.

### machines (`machines_machine`)

Назначение: производственные станки.

Ключевые поля: `id`, `name`, `inventory_number`, `comment`, `is_active`.

Индексы и ограничения: сортировка по `name`; явных уникальных ограничений на
название нет.

Пишет: `control-web`.

Читает: все прикладные сервисы.

### devices (`machines_device`)

Назначение: ESP32-устройства, закрепленные за станками.

Ключевые поля: `id`, `mac_address`, `machine_id`, `name`, `is_active`.

Индексы и ограничения: `mac_address` уникален; есть индекс
`device_mac_address_idx`; `machine_id` защищен через `on_delete=PROTECT`.

Пишет: `control-web`.

Читает: `auth-service` при определении станка по `macAddress`, `control-web`.

### user_machine_permissions (`schedules_usermachinepermission`)

Назначение: базовое разрешение пользователю работать на станке.

Ключевые поля: `id`, `user_id`, `machine_id`, `is_allowed`.

Индексы и ограничения: уникальная пара `user_id`, `machine_id`
(`unique_user_machine_permission`).

Пишет: `control-web`.

Читает: `auth-service` при выдаче списка работников и login, `control-web`.

### user_machine_schedules (`schedules_usermachineschedule`)

Назначение: расписание, в которое работник может входить на станок.

Ключевые поля: `id`, `user_id`, `machine_id`, `weekday`, `time_from`,
`time_to`, `is_active`.

Индексы и ограничения: `weekday` от 1 до 7; `time_from` меньше `time_to`;
смены, пересекающие полночь, в первой версии запрещены.

Пишет: `control-web`.

Читает: `auth-service`, `control-web`.

### works (`production_work`)

Назначение: рабочая смена пользователя на конкретном станке.

Ключевые поля: `id`, `user_id`, `machine_id`, `device_id`, `started_at`,
`finished_at`, `last_seen_at`, `status`.

Индексы и ограничения: partial unique constraint
`unique_active_work_per_machine` запрещает две активные смены на одном станке;
индексы `work_status_idx` и `work_machine_status_idx` ускоряют dashboard.

Пишет: `auth-service` при login, heartbeat и logout.

Читает: `event-service`, `control-web`.

### auth_sessions (`production_authsession`)

Назначение: UUID-сессия работника, которую ESP32 использует как `sessionID`.

Ключевые поля: `id`, `user_id`, `machine_id`, `device_id`, `work_id`,
`created_at`, `expires_at`, `is_active`.

Индексы и ограничения: `id` является UUID primary key; связи защищены через
`on_delete=PROTECT`.

Пишет: `auth-service` при login и logout.

Читает: `event-service`, `auth-service`, `control-web`.

### detail_types (`production_detailtype`)

Назначение: справочник типов деталей.

Ключевые поля: `id`, `code`, `name`, `is_active`.

Индексы и ограничения: `code` уникален.

Пишет: `control-web`.

Читает: `event-service`, `control-web`.

### detail_states (`production_detailstate`)

Назначение: справочник состояний деталей.

Ключевые поля: `id`, `code`, `name`, `is_active`.

Индексы и ограничения: `code` уникален. Начальные состояния создаются миграцией
`production.0002_seed_detail_states`.

Пишет: `control-web` через миграции seed и admin.

Читает: `event-service`, `control-web`.

### details (`production_detail`)

Назначение: произведенные детали в рамках рабочей смены.

Ключевые поля: `id`, `user_id`, `machine_id`, `work_id`, `detail_number`,
`detail_type_id`, `detail_state_id`, `event_time`.

Индексы и ограничения: уникальность
`user_id`, `machine_id`, `work_id`, `detail_number`
(`unique_detail_number_per_work`); индексы по `event_time`, пользователю,
станку и смене ускоряют отчеты.

Пишет: `event-service`.

Читает: `control-web`.

### invalid_events (`production_invalidevent`)

Назначение: диагностический журнал событий, которые нельзя сохранить как
`Detail`.

Ключевые поля: `id`, `received_at`, `source_ip`, `raw_body`, `error_text`,
`service_name`, `created_at`.

Индексы и ограничения: индекс `invalid_event_received_idx` по времени получения.

Пишет: `event-service`.

Читает: `control-web`.

## Миграции

```bash
docker compose exec control-web python manage.py migrate
```

После изменения Django-моделей нужно создать миграции в `control-web`, проверить
их локально и только затем обновлять FastAPI SQL-запросы под новую схему.
