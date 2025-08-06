.PHONY: help build up down logs shell-backend shell-frontend test lint format clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker commands
build: ## Build all containers
	docker-compose build

up: ## Start development environment
	docker-compose up -d

down: ## Stop development environment
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

# Shell access
shell-backend: ## Access backend container shell
	docker-compose exec backend bash

shell-frontend: ## Access frontend container shell
	docker-compose exec frontend sh

shell-db: ## Access database shell
	docker-compose exec db psql -U santaserver -d santaserver

# Development commands
test: ## Run backend tests
	cd backend && python -m pytest

test-watch: ## Run backend tests with file watching
	cd backend && python -m pytest -f

lint: ## Run linting for both backend and frontend
	cd backend && flake8 app/ tests/
	cd frontend && npm run lint

lint-backend: ## Run backend linting
	cd backend && flake8 app/ tests/

lint-frontend: ## Run frontend linting
	cd frontend && npm run lint

format: ## Format code for both backend and frontend
	cd backend && black app/ tests/ && isort app/ tests/
	cd frontend && npm run format

format-backend: ## Format backend code
	cd backend && black app/ tests/ && isort app/ tests/

format-frontend: ## Format frontend code
	cd frontend && npm run format

type-check: ## Run type checking
	cd backend && mypy app/
	cd frontend && npm run check

# Setup commands
setup: ## Initial setup - copy env files and install dependencies
	cp backend/.env.example backend/.env
	@echo "Please edit backend/.env with your configuration"

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install


# Cleanup commands
clean: ## Clean up containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean up everything including images
	docker-compose down -v --remove-orphans
	docker system prune -af