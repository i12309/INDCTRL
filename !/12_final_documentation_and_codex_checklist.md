# Задача 12. Финальная документация, API-описание и контрольный чеклист Codex

## Цель

Собрать проект в понятное состояние: документация, описание API, описание БД, инструкции запуска, инструкции эксплуатации и итоговая проверка всей системы.

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

## Документация по архитектуре

Обновить `docs/architecture.md`.

Описать:

```text
общую схему сервисов;
почему PostgreSQL;
почему Docker Compose;
почему auth-service и event-service сделаны на FastAPI;
почему admin/reports/dashboard объединены в Django control-web;
как сервисы взаимодействуют через общую БД;
какие границы ответственности у каждого сервиса;
```

## Документация по БД

Обновить `docs/database.md`.

Описать таблицы:

```text
roles
users
machines
devices
user_machine_permissions
user_machine_schedules
works
auth_sessions
detail_types
detail_states
details
invalid_events
```

Для каждой таблицы:

```text
назначение;
ключевые поля;
важные индексы;
важные ограничения;
какой сервис пишет;
какой сервис читает;
```

Обязательно описать:

```text
уникальность details: user_id, machine_id, work_id, detail_number;
один active Work на один machine;
machineID определяется по macAddress ESP32;
Work создается при login;
```

## API auth-service

В `docs/services/auth-service.md` описать:

```text
GET /health
POST /api/auth/device/workers
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/heartbeat
```

Для каждого endpoint:

```text
назначение;
пример запроса;
пример успешного ответа;
пример ошибки;
что меняется в БД;
```

## API event-service

В `docs/services/event-service.md` описать:

```text
GET /health
POST /api/events/detail
```

Обязательно описать:

```text
рекомендуемый JSON;
роль sessionID;
идемпотентность;
когда возвращается saved;
когда возвращается duplicate;
когда создается InvalidEvent;
```

## Документация control-web

В `docs/services/control-web.md` описать:

```text
/admin/
/dashboard/current-workers/
/reports/details/
/reports/details/export/csv/
/reports/details/export/xlsx/
```

Описать роли:

```text
admin      доступ к admin, dashboard, reports;
director   dashboard и reports;
manager    dashboard и reports;
worker     нет доступа к reports в первой версии;
```

## Документация для ESP32-разработчика

Создать `docs/esp32-api.md`.

Описать последовательность работы ESP32:

```text
1. Отправить macAddress и получить список работников.
2. Работник выбирает ФИО и вводит пароль.
3. ESP32 отправляет login.
4. Получает sessionID, userID, machineID, workID.
5. Отправляет события деталей с sessionID.
6. Периодически отправляет heartbeat.
7. При завершении работы отправляет logout.
```

Добавить примеры JSON.

## Финальный Docker runbook

Создать `docs/linux/runbook.md`.

Включить:

```text
первый запуск;
остановка;
перезапуск;
обновление;
миграции;
создание администратора;
просмотр логов;
backup;
restore;
проверка места на диске;
проверка health endpoint'ов;
```

## Чеклист финальной проверки

Создать `docs/final-checklist.md`:

```text
[ ] docker compose up -d --build работает
[ ] миграции применяются
[ ] superuser создается
[ ] /admin/ открывается
[ ] создан Machine
[ ] создан Device с macAddress
[ ] создан worker
[ ] worker получил право на станок
[ ] worker получил расписание
[ ] ESP32 device/workers возвращает работника
[ ] login создает Work и AuthSession
[ ] event-service сохраняет Detail
[ ] повтор события возвращает duplicate
[ ] dashboard показывает активную смену
[ ] report details показывает деталь
[ ] CSV export работает
[ ] XLSX export работает
[ ] logout закрывает смену
[ ] backup создается
[ ] restore проверен на тестовой БД
```

## Критерии приемки

- В проекте есть полная документация для разработчика, администратора и ESP32-разработчика.
- Все сервисы имеют README.
- Есть общий runbook.
- Есть финальный чеклист.
- Проект можно поднять на чистом Linux-сервере через Docker Compose по инструкции.
- В коде и документации соблюдено требование понятных русских комментариев.
