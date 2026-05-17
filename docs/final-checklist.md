# Финальный чеклист INDCTRL

```text
[ ] docker compose up -d --build работает
[ ] миграции применяются через indctrl
[ ] superuser создается
[ ] /admin/ открывается
[ ] создан Machine
[ ] создан Device с macAddress
[ ] создан worker
[ ] worker получил право на станок
[ ] worker получил расписание
[ ] POST /api/device/workers возвращает работника
[ ] POST /api/device/login создает Work и AuthSession
[ ] POST /api/device/detail сохраняет Detail
[ ] повтор detail возвращает duplicate
[ ] POST /api/device/heartbeat обновляет last_seen_at
[ ] dashboard показывает активную смену
[ ] report details показывает деталь
[ ] CSV export работает
[ ] XLSX export работает
[ ] POST /api/device/logout закрывает смену
[ ] backup создается
[ ] restore проверен на тестовой БД
```

## Команды

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py createsuperuser
curl http://127.0.0.1/health-web/
```

Логи:

```bash
docker compose logs -f indctrl
docker compose logs -f nginx
docker compose logs -f postgres
```
