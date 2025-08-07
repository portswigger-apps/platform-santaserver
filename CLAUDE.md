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
- `uv run pytest` - Run unit tests using FastAPI TestClient and httpx
- `uv run tox` - Run tests across environments
- Test-driven development approach is followed

**Backend Code Quality:**
- `uv run black` - Code formatting (120 character line length)
- `uv run flake8` - Linting (configured for 120 character line length)

**Frontend Package Management:**
- `yarn install` - Install dependencies (use yarn, not npm)
- `yarn add package-name` - Add new dependency
- `yarn add -D package-name` - Add development dependency

**Frontend Code Quality:**
- `yarn run lint` - ESLint + TypeScript linting
- `yarn run format` - Prettier formatting
- `yarn run check` - TypeScript type checking

## Key Development Notes

- Backend follows TDD methodology
- Line length configured to 120 characters for both Python (black/flake8) and TypeScript
- Authentication is handled via Microsoft Entra integration
- Real-time features implemented using WebSockets
- Database operations use SQLModel for type safety
- Use the Context7 MCP if available
- use conventional commits for any git commit messages

## Project Status

This project is in early development phase. The core architecture has been defined but implementation is pending. When developing:

1. Follow the TDD approach for backend development
2. Ensure all new endpoints use FastAPI patterns
3. Maintain SQLModel usage for database operations
4. Use WebSocket connections for real-time approval workflows
5. Follow the established linting configurations (120 char line length)