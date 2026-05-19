# Runbook Linux-сервера

Эксплуатация INDCTRL после перехода на Django-only. Рабочие контейнеры:
`indctrl`, `postgres`, `nginx`.

## Первый запуск

Для локальной разработки можно использовать сборку на месте:

```bash
cd /opt/INDCTRL
cp .env.example .env
nano .env
docker compose up -d --build
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose exec indctrl python manage.py createsuperuser
curl http://127.0.0.1/health-web/
```

Для production без интернета сначала загрузите заранее подготовленные Docker-образы,
затем запускайте `compose.production.yml`:

```bash
docker load -i indctrl-images.tar
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml exec indctrl python manage.py migrate
docker compose -f compose.production.yml exec indctrl python manage.py collectstatic --noinput
```

## Остановка

```bash
docker compose down
```

## Перезапуск

```bash
docker compose restart
docker compose restart indctrl
docker compose restart nginx
```

## Обновление

Локальная разработка:

```bash
git pull
docker compose build
docker compose up -d
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose ps
```

Production:

```bash
docker load -i indctrl-images.tar
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml exec indctrl python manage.py migrate
docker compose -f compose.production.yml exec indctrl python manage.py collectstatic --noinput
```

Перед обновлением сделайте backup PostgreSQL. На production-сервере сборка образов
не выполняется.

## Миграции

```bash
docker compose exec indctrl python manage.py migrate
```

## Создание администратора

```bash
docker compose exec indctrl python manage.py createsuperuser
```

## Логи

```bash
docker compose logs -f
docker compose logs -f indctrl
docker compose logs -f nginx
docker compose logs -f postgres
```

## Backup

```bash
bash deploy/scripts/backup_postgres.sh
```

## Restore

```bash
docker compose stop indctrl
bash deploy/scripts/restore_postgres.sh ./backups/postgres/indctrl_YYYY-mm-dd_HHMMSS.sql.gz
docker compose up -d indctrl
curl http://127.0.0.1/health-web/
```

Restore сначала проверяйте на тестовой БД.

## Проверка места на диске

```bash
df -h
du -sh backups/postgres
docker system df
docker volume ls
```

## Health

```bash
curl http://127.0.0.1/health-web/
```

Ожидаемый ответ:

```json
{"status": "ok", "service": "indctrl"}
```
