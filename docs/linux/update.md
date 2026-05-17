# Обновление

```bash
git pull
docker compose -f compose.production.yml build
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml exec control-web python manage.py migrate
```
