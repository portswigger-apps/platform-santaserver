# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SantaServer is a management server for Google's Santa (macOS security agent), providing enterprise-grade allowlisting with approval workflows, multi-team routing, and community voting features.

## Architecture & Tech Stack

**Backend:**
- Python 3 with FastAPI framework
- WebSocket support for real-time features
- FastAPI-Azure-Auth for authentication
- SQLModel ORM with PostgreSQL 17+ database
- Microsoft Entra for authentication

**Frontend:**
- TypeScript with Svelte framework
- Served through Nginx reverse proxy
- Backend API exposed at `/api` endpoint

**Development Environment:**
- Docker/OCI containers for packaging
- Docker Compose for local development
- Nginx as reverse proxy

## Development Commands

**Backend Testing:**
- `pytest` - Run unit tests using FastAPI TestClient and httpx
- `tox` - Run tests across environments
- Test-driven development approach is followed

**Backend Code Quality:**
- `black` - Code formatting (120 character line length)
- `flake8` - Linting (configured for 120 character line length)

**Frontend Code Quality:**
- `typescript-eslint` - TypeScript linting

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