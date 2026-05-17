# event-service

Назначение: прием событий о произведенных деталях от ESP32.

Основные endpoint'ы:

- `GET /health`;
- `GET /api/events/health`;
- `POST /api/events/detail`.

`sessionID` является главным источником `user_id`, `machine_id` и `work_id`; значения
из ESP32, если они появятся в запросе, сверяются с активной сессией.
