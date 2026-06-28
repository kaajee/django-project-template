.DEFAULT_GOAL := help
DC := docker compose

.PHONY: help install run migrate makemigrations superuser shell \
        lint fmt typecheck test cov security check-deploy schema ci \
        up down logs build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install deps + git hooks
	uv sync --group dev
	uv run pre-commit install

run: ## Run the dev server
	uv run python manage.py runserver

migrate: ## Apply database migrations
	uv run python manage.py migrate

makemigrations: ## Create new migrations
	uv run python manage.py makemigrations

superuser: ## Create an admin user
	uv run python manage.py createsuperuser

shell: ## Open shell_plus
	uv run python manage.py shell_plus

lint: ## Lint + format check
	uv run ruff check .
	uv run ruff format --check .

fmt: ## Auto-fix lint + format
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Run mypy
	uv run mypy .

test: ## Run tests with coverage
	uv run pytest

cov: ## Tests + HTML coverage report
	uv run pytest --cov-report=html
	@echo "Open htmlcov/index.html"

security: ## Run bandit + pip-audit
	uv run bandit -c pyproject.toml -r apps config
	uv run pip-audit

check-deploy: ## Run Django deploy checks against prod settings
	DJANGO_SETTINGS_MODULE=config.settings.prod \
	DJANGO_SECRET_KEY=local-check DATABASE_URL=postgres://u:p@localhost/db \
	DJANGO_ALLOWED_HOSTS=example.com \
	uv run python manage.py check --deploy

schema: ## Export the OpenAPI schema to schema.yml
	uv run python manage.py spectacular --file schema.yml

ci: lint typecheck test security ## Run the full CI suite locally

build: ## Build the Docker image
	$(DC) build

up: ## Start the full stack (web, db, redis, worker, beat)
	$(DC) up --build

down: ## Stop the stack
	$(DC) down

logs: ## Tail service logs
	$(DC) logs -f
