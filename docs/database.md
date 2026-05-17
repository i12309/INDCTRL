# База данных

Рабочая БД проекта - PostgreSQL. Единственный источник структуры БД - Django
модели и миграции в `service`.

## Ключевые правила

- `machineID` определяется по `Device.mac_address` ESP32.
- `Work` создается при успешном `POST /api/device/login`.
- На один станок может быть только один активный `Work`.
- Деталь уникальна по `user_id`, `machine_id`, `work_id`, `detail_number`.
- `sessionID` из `AuthSession` является источником `user_id`, `machine_id` и
  `work_id` для событий деталей.

## Основные таблицы

- `accounts_role` - роли `admin`, `director`, `manager`, `worker`.
- `accounts_user` - пользователи и работники.
- `machines_machine` - станки.
- `machines_device` - ESP32-устройства с уникальным `mac_address`.
- `schedules_usermachinepermission` - разрешения работников на станки.
- `schedules_usermachineschedule` - расписания работников.
- `production_work` - рабочие смены.
- `production_authsession` - UUID-сессии ESP32.
- `production_detailtype` - типы деталей.
- `production_detailstate` - состояния деталей.
- `production_detail` - произведенные детали.
- `production_invalidevent` - некорректные события API.

## Важные ограничения и индексы

- `unique_active_work_per_machine` запрещает две активные смены на одном станке.
- `unique_detail_number_per_work` обеспечивает защиту от дублей деталей.
- `device_mac_address_idx` ускоряет поиск ESP32 по MAC-адресу.
- Индексы `detail_event_time_idx`, `detail_user_event_time_idx`,
  `detail_machine_event_time_idx`, `detail_work_idx` ускоряют отчеты.
- `schedule_weekday_between_1_and_7` и `schedule_time_from_lt_time_to`
  защищают расписания от некорректных значений.

## Миграции

```bash
docker compose exec indctrl python manage.py migrate
```

Изменения схемы делаются только через Django-модели и новые миграции.
