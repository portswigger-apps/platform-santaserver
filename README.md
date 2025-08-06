# SantaServer

A Server for https://github.com/northpolesec/santa management.

## Say Goodbye to Allowlisting Nightmares

- No more bottlenecks or frustrated users. No more security compromises. Assign distinct approval workflows for each team to balance security, compliance and productivity
- Route requests to the right people and require multiple approvers when needed for added oversight
- Democratize software approvals with community voting, perfect for collaborative environments

## What is Santa?

Santa is the open-source macOS security agent pioneered at Google and now maintained by North Pole Security.
Santaserver transforms Santa into a complete enterprise platform with scalable allowlisting

## What is SantaServer?

SantaServer provides all of the APIs for Google's Santa Client and a slick intuitive user interface to audit, authorise and manage Santa across the enterprise.

## Architecture

- **Backend**: Python 3.11 with FastAPI framework, PostgreSQL 17+ database
- **Frontend**: TypeScript with Svelte framework
- **Authentication**: Microsoft Entra (Azure AD)
- **Deployment**: Docker containers with Nginx reverse proxy

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd platform-santaserver
   ```

2. Copy environment configuration:
   ```bash
   make setup
   ```

3. Edit `backend/.env` with your configuration values

4. Build and start the development environment:
   ```bash
   make build
   make up
   ```

5. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - Direct backend: http://localhost:8000
   - Direct frontend: http://localhost:3000

### Development Commands

```bash
make help           # Show all available commands
make up             # Start development environment
make down           # Stop development environment
make logs           # View logs from all services
make test           # Run backend tests
make lint           # Run linting for both backend and frontend
make format         # Format code for both backend and frontend
```

## Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   └── services/      # Business logic
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/              # Svelte frontend
│   ├── src/              # Frontend source code
│   │   ├── lib/         # Shared components
│   │   └── routes/      # Page routes
│   └── package.json     # Node.js dependencies
├── nginx/                # Nginx configuration
├── docker-compose.yml    # Development environment
└── Makefile             # Development commands
```

## Development

### Backend Development

The backend follows Test-Driven Development (TDD) principles:

- Run tests: `make test`
- Format code: `make format-backend`
- Lint code: `make lint-backend`
- Type checking: `cd backend && mypy app/`

### Frontend Development

- Install dependencies: `cd frontend && npm install`
- Format code: `make format-frontend`
- Lint code: `make lint-frontend`
- Type checking: `cd frontend && npm run check`

## Production Deployment

Production deployment configuration to be determined based on target infrastructure requirements. 