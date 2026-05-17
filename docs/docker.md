# Docker

Локальный запуск:

```bash
cp .env.example .env
docker compose up -d --build
```

Production-запуск:

```bash
docker compose -f compose.production.yml up -d --build
```

В production compose нет bind-mount исходного кода. Сервисы собираются из Dockerfile
и работают через внутреннюю сеть `indctrl`.
