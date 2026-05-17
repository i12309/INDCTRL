# Восстановление PostgreSQL

Restore - опасная операция. Она может перезаписать или смешать данные в рабочей БД.
Для production сначала проверьте backup на отдельной машине или тестовой БД.

## Подготовка

1. Убедитесь, что backup-файл существует.
2. Сообщите пользователям о downtime.
3. Остановите прикладные сервисы:

```bash
cd /opt/INDCTRL
docker compose stop indctrl
```

PostgreSQL должен продолжать работать.

## Восстановление

```bash
bash deploy/scripts/restore_postgres.sh ./backups/postgres/indctrl_2026-05-17_030000.sql.gz
```

Скрипт попросит ввести:

```text
RESTORE
```

Без этого подтверждения восстановление не начнется.

Скрипт поддерживает `.sql.gz` и обычные `.sql` файлы.

## После восстановления

Запустите сервисы:

```bash
docker compose up -d indctrl
docker compose ps
```

Проверьте health:

```bash
curl http://127.0.0.1/health-web/
```

Проверьте количество деталей:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM production_detail;"
```

## Восстановление в тестовую БД

Самая безопасная проверка backup - отдельный сервер или тестовый compose-проект.
Не проверяйте restore на production-БД без необходимости.

Общий порядок:

```bash
cp .env.example .env
# задайте другое имя POSTGRES_DB или используйте отдельный сервер
docker compose up -d postgres
bash deploy/scripts/restore_postgres.sh ./backups/postgres/indctrl_YYYY-mm-dd_HHMMSS.sql.gz
```

## Если нужно полностью заменить БД

Остановите все сервисы, кроме `postgres`, и перед восстановлением очистите БД только
если понимаете последствия. В первой версии скрипт не делает `DROP DATABASE`
автоматически: это осознанная защита от случайной потери данных.
