# auth-service

Назначение: авторизация работников на ESP32, смены, heartbeat и logout.

Основные endpoint'ы:

- `GET /health`;
- `GET /health-auth/` через Nginx;
- `POST /api/auth/device/workers`;
- `POST /api/auth/login`;
- `POST /api/auth/logout`;
- `POST /api/auth/heartbeat`.
