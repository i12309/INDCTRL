COMPOSE=docker compose

.PHONY: build up down logs ps migrate createsuperuser collectstatic test lint format backup

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

migrate:
	$(COMPOSE) exec control-web python manage.py migrate

createsuperuser:
	$(COMPOSE) exec control-web python manage.py createsuperuser

collectstatic:
	$(COMPOSE) exec control-web python manage.py collectstatic --noinput

test:
	pytest

lint:
	ruff check common services tests

format:
	black common services tests
	ruff check --fix common services tests

backup:
	bash deploy/scripts/backup_postgres.sh
