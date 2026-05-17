# auth-service

Назначение: авторизация работников на ESP32, смены, heartbeat и logout.

Основные endpoint'ы:

- `GET /health`;
- `POST /api/auth/device/workers`;
- `POST /api/auth/login`;
- `POST /api/auth/logout`;
- `POST /api/auth/heartbeat`.
