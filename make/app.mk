DC_BASE=docker-compose.yml

.PHONY: up down build shell migrate makemigrations createsuperuser test reset-db logs lint format

up:
	docker compose -f $(DC_BASE) up --build

down:
	docker compose -f $(DC_BASE) down -v

build:
	docker compose -f $(DC_BASE) build

shell:
	docker compose -f $(DC_BASE) exec app bash

djshell:
	docker compose -f $(DC_BASE) exec app poetry run python manage.py shell

migrate:
	docker compose -f $(DC_BASE) exec app poetry run python manage.py migrate

makemigrations:
	docker compose -f $(DC_BASE) exec app poetry run python manage.py makemigrations

createsuperuser:
	docker compose -f $(DC_BASE) exec app poetry run python manage.py createsuperuser

test:
	docker compose -f $(DC_BASE) exec app poetry run pytest

logs:
	docker compose -f $(DC_BASE) logs -f

lint:
	docker compose run --rm ruff

format:
	docker compose run --rm ruff-fix
