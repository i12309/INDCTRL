# Резервное копирование PostgreSQL

Backup PostgreSQL обязателен для production, потому что в БД хранятся пользователи,
станки, смены, произведенные детали и некорректные события.

## Ручной backup

```bash
cd /opt/INDCTRL
bash deploy/scripts/backup_postgres.sh
```

Скрипт:

- читает `.env`;
- создает каталог из `BACKUP_DIR`, по умолчанию `./backups/postgres`;
- выполняет `pg_dump` внутри контейнера `postgres`;
- сжимает результат через `gzip`;
- создает файл вида `machine_control_2026-05-17_030000.sql.gz`;
- удаляет backup-файлы старше `BACKUP_RETENTION_DAYS`.

## Настройки

В `.env`:

```env
BACKUP_RETENTION_DAYS=30
BACKUP_DIR=./backups/postgres
```

Пароль PostgreSQL не хранится в скрипте. Он берется из `.env` вместе с
`POSTGRES_DB` и `POSTGRES_USER`.

## Cron

Пример ежедневного backup в 03:00:

```cron
0 3 * * * cd /opt/INDCTRL && ./deploy/scripts/backup_postgres.sh >> /var/log/INDCTRL-backup.log 2>&1
```

Проверьте, что пользователь cron имеет права запускать Docker.

## systemd timer

Можно создать service:

```ini
[Unit]
Description=INDCTRL PostgreSQL backup

[Service]
Type=oneshot
WorkingDirectory=/opt/INDCTRL
ExecStart=/opt/INDCTRL/deploy/scripts/backup_postgres.sh
```

И timer:

```ini
[Unit]
Description=Run INDCTRL PostgreSQL backup daily

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## Проверка backup

Backup считается рабочим только после тестового восстановления. Периодически
восстанавливайте свежий backup на отдельной машине или в тестовой БД.

Рекомендуется копировать backup на другой диск или другой сервер. Backup на том же
диске, что и PostgreSQL, не защищает от отказа диска.

## Полезные команды обслуживания

Размер текущей БД:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

Размер таблицы деталей:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT pg_size_pretty(pg_total_relation_size('production_detail'));"
```

Количество деталей:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM production_detail;"
```

Количество деталей по дням:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT event_time::date AS day, count(*) FROM production_detail GROUP BY day ORDER BY day DESC;"
```

Свободное место на диске:

```bash
df -h
du -sh backups/postgres
docker system df
```
