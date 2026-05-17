# Runbook Linux-сервера

Документ описывает эксплуатацию INDCTRL на одном Linux-сервере через Docker
Compose. Примеры предполагают каталог проекта `/opt/INDCTRL`.

## Первый запуск

```bash
cd /opt/INDCTRL
cp .env.example .env
nano .env
docker compose up -d --build
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose exec control-web python manage.py createsuperuser
docker compose ps
```

Проверьте:

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

## Остановка

```bash
cd /opt/INDCTRL
docker compose down
```

Команда не удаляет volume PostgreSQL. Данные остаются в `postgres_data`.

## Перезапуск

```bash
cd /opt/INDCTRL
docker compose restart
docker compose ps
```

Перезапуск одного сервиса:

```bash
docker compose restart auth-service
docker compose restart event-service
docker compose restart control-web
docker compose restart nginx
```

## Обновление

```bash
cd /opt/INDCTRL
git pull
docker compose build
docker compose up -d
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose ps
```

Перед обновлением production-сервера сделайте backup PostgreSQL.

## Миграции

```bash
docker compose exec control-web python manage.py migrate
```

Миграции запускаются только из `control-web`. `auth-service` и `event-service`
схему БД не меняют.

## Создание администратора

```bash
docker compose exec control-web python manage.py createsuperuser
```

После создания администратора войдите в `/admin/` и проверьте роль `admin`,
`is_active=true`, `is_staff=true`.

## Просмотр логов

Все сервисы:

```bash
docker compose logs -f
```

Отдельные сервисы:

```bash
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
docker compose logs -f nginx
docker compose logs -f postgres
```

## Backup

```bash
cd /opt/INDCTRL
bash deploy/scripts/backup_postgres.sh
```

Скрипт читает `.env`, создает dump PostgreSQL и кладет архив в `BACKUP_DIR`
по умолчанию `./backups/postgres`.

## Restore

Restore сначала проверяйте на тестовой БД.

```bash
cd /opt/INDCTRL
docker compose stop auth-service event-service control-web
bash deploy/scripts/restore_postgres.sh ./backups/postgres/machine_control_YYYY-mm-dd_HHMMSS.sql.gz
docker compose up -d auth-service event-service control-web
docker compose ps
```

После restore проверьте health endpoints и количество деталей.

## Проверка места на диске

```bash
df -h
du -sh backups/postgres
docker system df
docker volume ls
```

Если место заканчивается, сначала проверьте размер backup-каталога и Docker
образов. Не удаляйте volume `postgres_data`, если нужен текущий production-набор
данных.

## Проверка health endpoint'ов

Через Nginx:

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

Ожидаемые ответы:

```json
{"status": "ok", "service": "auth-service"}
```

```json
{"status": "ok", "service": "event-service"}
```

```json
{"status": "ok", "service": "control-web"}
```

## Быстрая диагностика

```bash
docker compose ps
docker compose exec control-web python manage.py check
docker compose exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Если Nginx отвечает `502`, проверьте, запущен ли нужный upstream-сервис и нет ли
ошибок подключения к PostgreSQL в его логах.
