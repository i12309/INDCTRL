COMPOSE=docker compose

.PHONY: build up down logs ps migrate createsuperuser collectstatic test lint format backup

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

migrate:
	$(COMPOSE) exec indctrl python manage.py migrate

createsuperuser:
	$(COMPOSE) exec indctrl python manage.py createsuperuser

collectstatic:
	$(COMPOSE) exec indctrl python manage.py collectstatic --noinput

test:
	pytest

lint:
	python -m ruff check service tests

format:
	black service tests
	python -m ruff check --fix service tests

backup:
	bash deploy/scripts/backup_postgres.sh
