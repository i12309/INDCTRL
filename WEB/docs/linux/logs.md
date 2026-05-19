# Логи и диагностика

```bash
docker compose logs -f
docker compose logs -f indctrl
docker compose logs -f nginx
docker compose logs -f postgres
```

Проверка Django:

```bash
docker compose exec indctrl python manage.py check
docker compose exec indctrl python manage.py showmigrations
curl http://127.0.0.1/health-web/
```

Перезапуск:

```bash
docker compose restart indctrl
docker compose restart nginx
```
