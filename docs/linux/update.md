# Обновление INDCTRL

Перед обновлением production-системы сделайте backup PostgreSQL:

```bash
bash deploy/scripts/backup_postgres.sh
```

Обновление:

```bash
git pull
docker compose build
docker compose up -d
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose ps
curl http://127.0.0.1/health-web/
```

Если после обновления есть ошибка:

```bash
docker compose logs -f indctrl
docker compose logs -f nginx
```
