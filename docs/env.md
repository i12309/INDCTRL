# Переменные окружения

Пример находится в `.env.example`. Настоящий `.env` не должен попадать в git.

Ключевые группы:

- `APP_*` - режим и часовой пояс;
- `POSTGRES_*` - подключение к PostgreSQL;
- `DJANGO_*` - настройки Django;
- `SESSION_TTL_MINUTES`, `HEARTBEAT_MAX_AGE_SECONDS` - будущие настройки смен.
