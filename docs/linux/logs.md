# Логи и диагностика

## Состояние контейнеров

```bash
docker compose ps
```

## Все логи

```bash
docker compose logs -f
```

## Логи отдельных сервисов

```bash
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
docker compose logs -f postgres
docker compose logs -f nginx
```

Для просмотра последних строк без постоянного ожидания:

```bash
docker compose logs --tail=200 control-web
```

## Перезапуск сервисов

```bash
docker compose restart auth-service
docker compose restart event-service
docker compose restart control-web
```

Перезапуск PostgreSQL выполняйте аккуратно:

```bash
docker compose restart postgres
```

## Проверка HTTP

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

## Типовые проблемы

- `postgres` unhealthy: проверьте `.env`, особенно `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- `control-web` не отвечает: проверьте миграции и логи `control-web`.
- `nginx` отвечает 502: backend-контейнер не запущен или не слушает `8000`.
- Нет static files: выполните `docker compose exec control-web python manage.py collectstatic --noinput`.
