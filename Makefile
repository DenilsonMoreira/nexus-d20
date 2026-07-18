SHELL := /bin/bash

.PHONY: up down build logs ps test lint typecheck check db-migrate db-revision seed clean

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

test:
	docker compose run --rm api pytest
	docker compose run --rm web npm test

lint:
	docker compose run --rm api ruff check app tests
	docker compose run --rm web npm run lint

typecheck:
	docker compose run --rm api mypy app
	docker compose run --rm web npm run typecheck

check: lint typecheck test

db-migrate:
	docker compose run --rm api alembic upgrade head

db-revision:
	docker compose run --rm api alembic revision --autogenerate -m "$(m)"

seed:
	docker compose run --rm api python -m app.seed

clean:
	docker compose down -v --remove-orphans
