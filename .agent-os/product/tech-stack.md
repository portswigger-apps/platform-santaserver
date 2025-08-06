# Technical Stack

> Last Updated: 2025-08-06
> Version: 1.0.0

## Application Framework

- **Framework:** FastAPI
- **Version:** Latest stable
- **Language:** Python 3.11

## Database

- **Primary Database:** PostgreSQL 17+
- **ORM:** SQLModel

## JavaScript

- **Framework:** Svelte
- **Runtime:** TypeScript
- **Build Tool:** Vite

## CSS Framework

- **Framework:** Custom CSS (to be determined)

## UI Component Library

- **Library:** Custom components

## Fonts Provider

- **Provider:** System fonts

## Icon Library

- **Library:** To be determined

## Authentication

- **Provider:** Microsoft Entra ID
- **Integration:** FastAPI-Azure-Auth

## Application Hosting

- **Platform:** To be determined
- **Container:** Docker/OCI containers

## Database Hosting

- **Platform:** To be determined
- **Version:** PostgreSQL 17+

## Asset Hosting

- **CDN:** To be determined

## Deployment Solution

- **Local Development:** Docker Compose
- **Production:** To be determined

## Code Repository

- **URL:** Private repository

## Development Tools

### Backend
- **Testing:** pytest, fastapi.testclient, httpx, tox (TDD approach)
- **Code Quality:** black (120 char line length), flake8 (120 char line length), isort, mypy
- **Standards:** PEP8 compliance, TDD methodology

### Frontend  
- **Testing:** To be determined
- **Code Quality:** typescript-eslint, prettier
- **Standards:** ESLint-friendly TypeScript, 120 char line length

### Infrastructure
- **Reverse Proxy:** Nginx (backend at /api endpoint)
- **Real-time:** WebSocket support via FastAPI
- **Configuration:** 2-space indentation for YAML files

### Project Automation
- **Build System:** Makefile with comprehensive development commands
- **Container Orchestration:** Docker Compose for development environment
- **Services:** PostgreSQL 17 Alpine, automatic health checks