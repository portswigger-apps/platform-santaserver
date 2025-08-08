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

### Unified Container Design
SantaServer uses a modern unified container architecture for simplified deployment:

- **Single Container**: nginx + FastAPI + static assets in one unified container
- **Backend**: Python 3.13 with FastAPI framework, Unix socket communication
- **Frontend**: TypeScript with SvelteKit (static build)
- **Database**: PostgreSQL 17+ (separate container)
- **Authentication**: JWT-based with RBAC system, extensible for SSO integration
- **Process Management**: Supervisor managing nginx and uvicorn
- **Security**: Non-root execution, minimal attack surface

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

3. Edit `backend/.env` with your configuration values:
   ```bash
   # Required environment variables
   DATABASE_URL=postgresql://user:pass@localhost/santaserver
   JWT_SECRET_KEY=your-secure-jwt-secret-key  # Generate with: openssl rand -hex 32
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=SecurePassword123!
   ADMIN_EMAIL=admin@company.com
   ```

4. Build and start the development environment:
   ```bash
   make build
   make up
   ```

5. Run database migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

6. Access the application:
   - Web Interface: http://localhost:8080
   - API Endpoints: http://localhost:8080/api
   - API Documentation: http://localhost:8080/docs (FastAPI auto-generated)
   - Health Check: http://localhost:8080/api/v1/health

### Development Commands

```bash
make help           # Show all available commands
make validate       # Build with full validation testing
make up             # Start development environment
make down           # Stop development environment
make logs           # View logs from unified container
make shell          # Access unified container shell
make test           # Run backend tests
make lint           # Run linting for both backend and frontend
make format         # Format code for both backend and frontend
```

## Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality (auth, database, security)
│   │   ├── models/        # SQLModel database models
│   │   ├── schemas/       # Pydantic request/response models
│   │   └── services/      # Business logic (authentication, user management)
│   ├── alembic/           # Database migrations
│   ├── tests/             # Comprehensive test suite (50 tests)
│   ├── pyproject.toml     # Python dependencies (uv managed)
│   └── AUTHENTICATION.md  # Authentication system documentation
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

The backend follows Test-Driven Development (TDD) principles with comprehensive authentication system:

**Testing (50 comprehensive tests)**:
- Run tests: `make test` (uses TestContainers for PostgreSQL + SQLite fallback)
- Watch mode: `make test-watch`
- Coverage: `cd backend && uv run pytest --cov=app --cov-report=html`

**Authentication System**:
- JWT-based authentication with RBAC
- 15 API endpoints (authentication + user management)
- Enterprise-grade security (bcrypt, account lockout, audit logging)
- Database migrations: `cd backend && uv run alembic upgrade head`

**Code Quality**:
- Format code: `make format-backend`
- Lint code: `make lint-backend`
- Type checking: `cd backend && uv run mypy app/`

**Documentation**:
- API docs: http://localhost:8080/docs (auto-generated)
- Authentication guide: `backend/AUTHENTICATION.md`

### Frontend Development

- Install dependencies: `cd frontend && yarn install`
- Format code: `make format-frontend`
- Lint code: `make lint-frontend`
- Type checking: `cd frontend && yarn run check`

## Authentication Quick Start

### Initial Admin Setup

After running migrations, create an initial admin user:

```bash
# Admin user will be created automatically from environment variables
# Set these in backend/.env:
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SecurePassword123!
ADMIN_EMAIL=admin@company.com
```

### API Authentication

```bash
# 1. Login to get JWT tokens
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePassword123!"}'

# 2. Use access token for authenticated requests
curl -X GET "http://localhost:8080/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Create new users (admin only)
curl -X POST "http://localhost:8080/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@company.com", "password": "SecurePass123!"}'
```

### Security Features

- **Password Policies**: 8+ chars, complexity requirements, 90-day expiration
- **Account Lockout**: 5 failed attempts = 15-minute lockout
- **JWT Security**: 30-minute access tokens, 7-day refresh tokens with rotation
- **Audit Logging**: All authentication events logged with IP/user agent
- **RBAC**: Role-based permissions (admin, user roles with JSON permissions)

## Production Deployment

### Database Preparation
```bash
# Set production environment variables
export DATABASE_URL="postgresql://user:pass@prod-host:5432/santaserver"
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Run migrations
cd backend && uv run alembic upgrade head
```

### Security Checklist
- [ ] Generate secure JWT_SECRET_KEY (32+ bytes)
- [ ] Set strong admin password
- [ ] Configure HTTPS/TLS termination
- [ ] Set up database connection pooling
- [ ] Configure structured logging for audit events
- [ ] Set up monitoring for failed login attempts
- [ ] Regular backup of user and audit data 