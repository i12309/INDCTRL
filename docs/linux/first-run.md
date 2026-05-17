# Первый запуск

```bash
git clone <repo-url> INDCTRL
cd INDCTRL
cp .env.example .env
docker compose -f compose.production.yml up -d --build
```

Проверьте состояние:

```bash
docker compose -f compose.production.yml ps
```
