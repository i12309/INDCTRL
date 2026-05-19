# Установка Docker

INDCTRL рассчитан на Linux-сервер с Docker Engine и Docker Compose Plugin. Администратору не нужно устанавливать Python, PostgreSQL или Nginx на хост: эти компоненты работают в контейнерах.

## Требования

- Linux-сервер предприятия.
- Docker Engine.
- Docker Compose Plugin, команда должна выглядеть как `docker compose`, а не только `docker-compose`.
- Пользователь, который запускает систему, должен иметь право выполнять команды Docker.

## Проверка установки

```bash
docker --version
docker compose version
```

Обе команды должны завершаться без ошибки.

## Права пользователя

Если Docker запускается только через `sudo`, используйте `sudo docker ...` во всех командах или добавьте администратора в группу `docker` согласно правилам вашей организации.

Пример для Ubuntu/Debian:

```bash
sudo usermod -aG docker $USER
```

После изменения групп нужно выйти из SSH-сессии и войти заново.

## Пример установки для Ubuntu/Debian

Ниже приведен ориентир. На production-сервере лучше свериться с официальной инструкцией Docker для вашего дистрибутива.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc >/dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Дальше добавьте репозиторий Docker для вашей версии Ubuntu/Debian и установите:

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Финальная проверка:

```bash
docker --version
docker compose version
```
