# Первый запуск на Linux

```bash
cd /opt/INDCTRL
cp .env.example .env
nano .env
docker compose up -d --build
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose exec indctrl python manage.py createsuperuser
```

Проверка:

```bash
curl http://127.0.0.1/health-web/
docker compose ps
```

Основные URL:

- `http://<server>/admin/`
- `http://<server>/dashboard/current-workers/`
- `http://<server>/reports/details/`
- `http://<server>/api/device/workers`
