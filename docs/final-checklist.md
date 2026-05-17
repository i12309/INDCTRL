# Финальный чеклист INDCTRL

Используйте этот список перед приемкой production-сборки. Отмечайте пункты после
проверки на чистом окружении или на тестовом сервере, максимально похожем на
production.

```text
[ ] docker compose up -d --build работает
[ ] миграции применяются
[ ] superuser создается
[ ] /admin/ открывается
[ ] создан Machine
[ ] создан Device с macAddress
[ ] создан worker
[ ] worker получил право на станок
[ ] worker получил расписание
[ ] ESP32 device/workers возвращает работника
[ ] login создает Work и AuthSession
[ ] event-service сохраняет Detail
[ ] повтор события возвращает duplicate
[ ] dashboard показывает активную смену
[ ] report details показывает деталь
[ ] CSV export работает
[ ] XLSX export работает
[ ] logout закрывает смену
[ ] backup создается
[ ] restore проверен на тестовой БД
```

## Команды для проверки

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py createsuperuser
```

Health:

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

Логи:

```bash
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
```

Backup:

```bash
bash deploy/scripts/backup_postgres.sh
```

Restore проверяйте только на тестовой БД:

```bash
bash deploy/scripts/restore_postgres.sh ./backups/postgres/machine_control_YYYY-mm-dd_HHMMSS.sql.gz
```
