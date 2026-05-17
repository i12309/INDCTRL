# Первый запуск на Linux-сервере

Инструкция предполагает установку проекта в `/opt/INDCTRL`.

## 1. Получить код

```bash
cd /opt
git clone <repo-url> INDCTRL
cd INDCTRL
```

Если репозиторий приватный, заранее настройте SSH-ключ или другой разрешенный способ доступа к Git.

## 2. Создать `.env`

```bash
cp .env.example .env
nano .env
```

Обязательно поменяйте:

- `POSTGRES_PASSWORD`;
- `DJANGO_SECRET_KEY`;
- `DJANGO_ALLOWED_HOSTS`;
- `DJANGO_CSRF_TRUSTED_ORIGINS`;
- при необходимости `APP_TIMEZONE`.

Файл `.env` содержит секреты и не должен попадать в git.

## 3. Собрать и запустить контейнеры

```bash
docker compose up -d --build
docker compose ps
```

Снаружи должен быть открыт только Nginx на `80:80`. PostgreSQL не публикуется наружу.

## 4. Применить миграции

```bash
docker compose exec control-web python manage.py migrate
```

Миграции создает и применяет только Django-сервис `control-web`.

## 5. Собрать static files

```bash
docker compose exec control-web python manage.py collectstatic --noinput
```

Nginx отдает static files из Docker volume `static_data`.

## 6. Создать администратора

```bash
docker compose exec control-web python manage.py createsuperuser
```

После создания убедитесь, что у пользователя есть роль `admin`, `is_active=true` и `is_staff=true`.

## 7. Проверить health endpoints

```bash
curl http://127.0.0.1/health-auth/
curl http://127.0.0.1/health-events/
curl http://127.0.0.1/health-web/
```

Ожидаемый ответ:

```json
{"status": "ok", "service": "..."}
```

## 8. Открыть интерфейсы

- `http://<server>/admin/` - Django admin.
- `http://<server>/dashboard/current-workers/` - dashboard текущей работы.
- `http://<server>/reports/details/` - отчет по деталям.

## 9. Автозапуск через systemd

Docker restart policies `restart: unless-stopped` уже перезапускают отдельные контейнеры после падения. Если нужно поднимать весь compose-проект после старта сервера через systemd, используйте пример:

```text
deploy/systemd/INDCTRL.service.example
```

Установка примера:

```bash
sudo cp deploy/systemd/INDCTRL.service.example /etc/systemd/system/INDCTRL.service
sudo systemctl daemon-reload
sudo systemctl enable INDCTRL.service
sudo systemctl start INDCTRL.service
sudo systemctl status INDCTRL.service
```

Перед установкой проверьте `WorkingDirectory=/opt/INDCTRL` в unit-файле.
