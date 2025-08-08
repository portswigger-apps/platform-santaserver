.PHONY: help build up down logs shell shell-db test lint format clean validate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker commands (unified container architecture)
build: ## Build unified container
	docker-compose build

validate: ## Build with full validation testing
	./scripts/build.sh

up: ## Start development environment (unified container + database)
	docker-compose up -d

down: ## Stop development environment
	docker-compose down

logs: ## Show logs from unified container
	docker-compose logs -f santaserver

logs-db: ## Show database logs
	docker-compose logs -f db

# Shell access
shell: ## Access unified container shell
	docker-compose exec santaserver bash

shell-db: ## Access database shell
	docker-compose exec db psql -U santaserver -d santaserver

# Development commands
test: ## Run backend tests
	cd backend && uv run pytest

test-watch: ## Run backend tests with file watching
	cd backend && uv run pytest --looponfail

lint: ## Run linting for both backend and frontend
	cd backend && uv run flake8 app/ tests/
	cd frontend && yarn run lint

lint-backend: ## Run backend linting
	cd backend && uv run flake8 app/ tests/

lint-frontend: ## Run frontend linting
	cd frontend && yarn run lint

format: ## Format code for both backend and frontend
	cd backend && uv run black app/ tests/ && uv run isort app/ tests/
	cd frontend && yarn run format

format-backend: ## Format backend code
	cd backend && uv run black app/ tests/ && uv run isort app/ tests/

format-frontend: ## Format frontend code
	cd frontend && yarn run format

type-check: ## Run type checking for both backend and frontend
	cd backend && uv run mypy app/
	cd frontend && yarn run check

type-check-backend: ## Run backend type checking
	cd backend && uv run mypy app/

type-check-frontend: ## Run frontend type checking
	cd frontend && yarn run check

test-cov: ## Run backend tests with coverage reporting
	cd backend && uv run pytest --cov=app --cov-report=html

# Setup commands
setup: ## Initial setup - copy env files and install dependencies
	cp backend/.env.example backend/.env
	cd backend && uv sync
	cd frontend && yarn install
	@echo "Please edit backend/.env with your configuration"

install-backend: ## Install backend dependencies using uv
	cd backend && uv sync

install-frontend: ## Install frontend dependencies
	cd frontend && yarn install

sync: ## Sync backend dependencies with uv lock file
	cd backend && uv sync


# Cleanup commands
clean: ## Clean up containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean up everything including images
	docker-compose down -v --remove-orphans
	docker system prune -af