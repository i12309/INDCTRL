# База данных

Рабочая БД проекта - PostgreSQL. Контейнер `postgres` не публикует порт `5432`
наружу по умолчанию и доступен только внутри Docker-сети.

Миграции выполняются из `control-web`:

```bash
docker compose exec control-web python manage.py migrate
```
