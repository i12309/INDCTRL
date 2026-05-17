# Обновление production-системы

Перед обновлением production-системы сделайте backup PostgreSQL.

```bash
cd /opt/INDCTRL
bash deploy/scripts/backup_postgres.sh
```

Подробности backup и проверки восстановления описаны в `docs/backup/postgres-backup.md`
и `docs/backup/postgres-restore.md`.

## Обновление кода и контейнеров

```bash
cd /opt/INDCTRL
git pull
docker compose build
docker compose up -d
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose ps
```

## Проверка после обновления

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
docker compose logs --tail=100
```

Если после обновления контейнер не стартует, посмотрите его логи:

```bash
docker compose logs -f control-web
docker compose logs -f auth-service
docker compose logs -f event-service
```

## Через deploy script

Скрипт выполняет сборку, запуск, миграции и `collectstatic`:

```bash
cd /opt/INDCTRL
bash deploy/scripts/deploy.sh
```

Backup перед запуском скрипта все равно выполняется отдельно.
