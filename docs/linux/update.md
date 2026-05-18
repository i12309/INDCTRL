# Обновление INDCTRL

Перед обновлением production-системы сделайте backup PostgreSQL:

```bash
bash deploy/scripts/backup_postgres.sh
```

Обновление локальной разработки:

```bash
git pull
docker compose build
docker compose up -d
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose ps
curl http://127.0.0.1/health-web/
```

Обновление production без интернета:

```bash
docker load -i indctrl-images.tar
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml exec indctrl python manage.py migrate
docker compose -f compose.production.yml exec indctrl python manage.py collectstatic --noinput
docker compose -f compose.production.yml ps
curl http://127.0.0.1/health-web/
```

Production-сервер использует готовые образы и не выполняет `docker compose build`.

Если после обновления есть ошибка:

```bash
docker compose logs -f indctrl
docker compose logs -f nginx
```
