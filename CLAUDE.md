# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SantaServer is a management server for Google's Santa (macOS security agent), providing enterprise-grade allowlisting with approval workflows, multi-team routing, and community voting features.

## Architecture & Tech Stack

**Unified Container Architecture:**
- Single container with nginx + FastAPI + static frontend assets
- Unix socket communication between nginx and uvicorn (`/tmp/sockets/uvicorn.sock`)
- Supervisor process management for nginx and uvicorn
- Non-root execution as nginx user (UID 101) for security

**Backend:**
- Python 3.13+ with FastAPI framework
- uv for dependency and virtual environment management
- WebSocket support for real-time features
- FastAPI-Azure-Auth for authentication
- SQLModel ORM with PostgreSQL 17+ database
- Microsoft Entra for authentication

**Frontend:**
- TypeScript with SvelteKit framework (static adapter)
- Yarn package manager (chosen over npm for better dependency resolution)
- Static assets served by nginx
- Backend API exposed at `/api` endpoint

**Development Environment:**
- Unified Docker container for simplified deployment
- Docker Compose with PostgreSQL database container
- Single port exposure (8080) for all services

## Development Commands

**Backend Testing:**
- `uv run pytest` - Run 50 comprehensive tests using TestContainers (PostgreSQL) + SQLite fallback
- `uv run pytest --cov=app --cov-report=html` - Run tests with coverage reporting
- `uv run pytest -v tests/test_auth_endpoints.py` - Run specific authentication test module
- `uv run tox` - Run tests across environments
- Test-driven development approach is followed with comprehensive authentication testing

**Backend Code Quality:**
- `uv run black` - Code formatting (120 character line length)
- `uv run flake8` - Linting (configured for 120 character line length)
- `uv run autoflake --remove-all-unused-imports --recursive app/ tests/` - Remove unused imports

**Database Management:**
- `uv run alembic upgrade head` - Run database migrations (3 migrations for authentication)
- `uv run alembic current` - Check current migration status
- `uv run alembic history --verbose` - View migration history

**Frontend Package Management:**
- `yarn install` - Install dependencies (use yarn, not npm)
- `yarn add package-name` - Add new dependency
- `yarn add -D package-name` - Add development dependency

**Frontend Code Quality:**
- `yarn run lint` - ESLint + TypeScript linting
- `yarn run format` - Prettier formatting
- `yarn run check` - TypeScript type checking

## Key Development Notes

- Backend follows TDD methodology with 50 comprehensive tests
- Line length configured to 120 characters for both Python (black/flake8) and TypeScript
- **Authentication System (PRD 003 - COMPLETED)**: JWT-based with RBAC, bcrypt hashing, account lockout
- Authentication includes 15 API endpoints (auth + user management) with admin-only controls
- Real-time features implemented using WebSockets
- Database operations use SQLModel for type safety with Alembic migrations
- TestContainers for PostgreSQL testing + SQLite fallback for CI/CD
- Use the Context7 MCP if available
- Use conventional commits for any git commit messages

## Authentication System

**Status**: ✅ **PRODUCTION READY** (PRD 003 Complete)

**Features**:
- JWT authentication with 30-min access tokens + 7-day refresh tokens
- RBAC with admin/user roles and JSON permissions
- Password security: bcrypt 12 rounds, complexity requirements, account lockout
- Comprehensive audit logging with IP/user agent tracking
- Session management with JTI tracking for token revocation
- Database: 3 Alembic migrations with extensible schema for SSO/SCIM

**API Endpoints**:
- Authentication: `/api/v1/auth/{login,logout,refresh,profile,change-password,verify}`
- User Management: `/api/v1/users/{GET,POST,PUT,DELETE}` (admin-only)
- Health: `/api/v1/health/` 

**Documentation**:
- Complete system docs: `backend/AUTHENTICATION.md`
- API docs: http://localhost:8080/docs (FastAPI auto-generated)
- Test suite: 50 tests with 100% pass rate

## File Naming Conventions

**PRD (Product Requirements Document) Files:**
- Location: `.prds/` directory
- Format: `{number}-{descriptive-name}.md`
- Examples: `001-single-container-architecture-migration.md`, `002-read-only-filesystem-nginx-tmp.md`
- Numbering: Sequential starting from 001, zero-padded to 3 digits

## Project Status

This project is in early development phase. The core architecture has been defined but implementation is pending. When developing:

1. Follow the TDD approach for backend development
2. Ensure all new endpoints use FastAPI patterns
3. Maintain SQLModel usage for database operations
4. Use WebSocket connections for real-time approval workflows
5. Follow the established linting configurations (120 char line length)