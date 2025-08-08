# Development Guide

This guide covers development workflows, testing, and contribution guidelines for SantaServer.

## Architecture Overview

SantaServer uses a **unified container architecture** that consolidates nginx, FastAPI backend, and frontend static assets into a single container for simplified deployment and improved performance.

### Container Architecture
- **Single Unified Container**: nginx + uvicorn (FastAPI) + static assets
- **Communication**: Unix socket between nginx and FastAPI (`/tmp/sockets/uvicorn.sock`)
- **Process Management**: Supervisor managing both nginx and uvicorn processes
- **Database**: Separate PostgreSQL 17+ container
- **Security**: All processes run as non-root nginx user (UID 101), nginx auth_request protection

## Development Environment

### Initial Setup

**Prerequisites**:
- [uv](https://docs.astral.sh/uv/) - Python package and project manager
- Docker & Docker Compose
- Node.js 18+ for frontend
- [Yarn](https://yarnpkg.com/) - Package manager for frontend dependencies

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd platform-santaserver
   make setup
   ```

2. **Configure Environment**:
   Edit `backend/.env` with your settings:
   ```bash
   # Required for Azure AD authentication
   TENANT_ID=your_tenant_id
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   
   # Generate with: openssl rand -hex 32
   SECRET_KEY=your_secret_key
   ```

3. **Start Development Environment**:
   ```bash
   make build
   make up
   ```

### Development Workflow

#### Backend Development (Python/FastAPI)

**Python Environment**:
- Python 3.13+ with uv for dependency management
- Virtual environment automatically managed by uv
- Dependencies defined in `pyproject.toml`

**File Structure**:
```
backend/app/
├── api/v1/endpoints/    # API route handlers
├── core/               # Configuration, security, utilities
├── db/                 # Database session, base classes
├── models/            # SQLModel database models
├── schemas/           # Pydantic request/response models
└── services/          # Business logic layer
```

**Dependency Management with uv**:
```bash
# Install/sync dependencies (automatically creates .venv)
cd backend && uv sync

# Add new dependency
cd backend && uv add package-name

# Add development dependency
cd backend && uv add --dev package-name

# Run commands in uv environment
cd backend && uv run python script.py
cd backend && uv run pytest
```

**Testing (TDD Approach - 50 Tests)**:
```bash
# Run all tests (uses TestContainers for PostgreSQL + SQLite fallback)
make test

# Watch mode for continuous testing
make test-watch

# Test specific authentication module
cd backend && uv run pytest tests/test_auth_endpoints.py -v
cd backend && uv run pytest tests/test_user_management.py -v

# Test with coverage reporting
cd backend && uv run pytest --cov=app --cov-report=html

# Test specific functionality
cd backend && uv run pytest -k "test_login" -v
cd backend && uv run pytest tests/test_health.py -v
```

**Code Quality**:
```bash
# Format code
make format-backend

# Lint code
make lint-backend

# Type checking
cd backend && uv run mypy app/
```

**Database Management**:
```bash
# Access database shell
make shell-db

# Run migrations (3 migrations for authentication system)
cd backend && uv run alembic upgrade head

# Check migration status  
cd backend && uv run alembic current
cd backend && uv run alembic history --verbose

# Create new migration (example)
cd backend && uv run alembic revision --autogenerate -m "Add new feature"
```

#### Frontend Development (TypeScript/Svelte)

**Package Management**:
- Uses Yarn for better dependency resolution and lockfile consistency
- Yarn chosen over npm for improved handling of peer dependency conflicts
- Lockfile (`yarn.lock`) ensures reproducible installs across environments

**File Structure**:
```
frontend/src/
├── lib/               # Shared components, utilities
├── routes/            # SvelteKit file-based routing
│   ├── +layout.svelte # Root layout
│   └── +page.svelte   # Homepage
└── app.html          # HTML shell
```

**Development Commands**:
```bash
# Install dependencies
cd frontend && yarn install

# Add new dependency
cd frontend && yarn add package-name

# Add development dependency
cd frontend && yarn add -D package-name

# Format code
make format-frontend

# Lint code
make lint-frontend

# Type checking
cd frontend && yarn run check
```

### Docker Development

**Service Access**:
```bash
# Backend shell
make shell-backend

# Frontend shell
make shell-frontend

# Database shell
make shell-db

# View logs
make logs
make logs-backend
make logs-frontend
```

**Container Management**:
```bash
# Rebuild containers
make build

# Stop all services
make down

# Clean up (removes volumes)
make clean
```

## Code Standards

### Backend Standards

- **Line Length**: 120 characters (configured in pyproject.toml)
- **Formatting**: Black with 120 character line length
- **Imports**: isort with black profile
- **Type Hints**: Required for all functions (enforced by mypy)
- **Testing**: pytest with TDD approach
- **API Documentation**: Automatic via FastAPI OpenAPI

### Frontend Standards

- **Line Length**: 120 characters (configured in .prettierrc)
- **Formatting**: Prettier with tabs
- **Linting**: ESLint with TypeScript support
- **Type Safety**: Strict TypeScript configuration
- **Components**: Svelte single-file components

### Git Workflow

**Branch Naming**:
- `feature/description` - New features
- `fix/description` - Bug fixes  
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

**Commit Messages**:
Follow conventional commits:
```
feat: add user authentication
fix: resolve database connection timeout
docs: update development guide
test: add approval workflow tests
```

## Testing Strategy

### Backend Testing

**Test Structure**:
```
tests/
├── test_health.py         # Health endpoint tests
├── test_auth.py          # Authentication tests
├── test_approvals.py     # Approval workflow tests
└── conftest.py           # Pytest configuration
```

**Testing Patterns**:
- Use FastAPI TestClient for API testing
- Mock external dependencies (Azure AD, database)
- Test both success and error scenarios
- Maintain ≥80% code coverage

### Frontend Testing

**Testing Tools** (to be implemented):
- Playwright for E2E testing
- Vitest for unit testing
- Testing Library for component testing

## Database Development

### Model Development

**SQLModel Patterns**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApprovalBase(SQLModel):
    application_hash: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Approval(ApprovalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalRead(ApprovalBase):
    id: int
```

### Migration Management

**Alembic Setup** (when implemented):
```bash
# Generate migration
cd backend && uv run alembic revision --autogenerate -m "Add approval table"

# Run migrations
cd backend && uv run alembic upgrade head

# Rollback migration
cd backend && uv run alembic downgrade -1
```

## Authentication Development

SantaServer implements a comprehensive JWT-based authentication system with RBAC (Role-Based Access Control) as defined in PRD 003.

**System Status**: ✅ **PRODUCTION READY** - Complete implementation with 50 passing tests

### JWT Authentication System

**Architecture**:
- **Token Types**: 30-minute access tokens, 7-day refresh tokens with rotation
- **Security**: bcrypt hashing (12 rounds), account lockout, audit logging
- **RBAC**: Role-based permissions with admin/user roles and JSON permissions
- **Session Management**: JTI tracking for individual token revocation
- **Static File Protection**: nginx auth_request prevents unauthorized access to frontend routes

**Key Components**:
```python
# Authentication service
from app.services.auth_service import AuthenticationService

# JWT utilities
from app.core.security import SecurityUtils

# Permission checking
from app.core.deps import get_current_active_user, require_permission

# Example protected endpoint
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"user": current_user}

# Example admin-only endpoint
@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("users", "create"))
):
    return await create_new_user(user_data)
```

**Database Schema**:
- **3 Alembic Migrations**: Complete authentication schema with extensible design
- **8 Core Tables**: users, roles, groups, sessions, audit logs, etc.
- **Future-Ready**: Schema supports SSO/SCIM integration without breaking changes

**API Endpoints (15 total)**:
- **Authentication**: `/api/v1/auth/{login,logout,refresh,profile,change-password,verify}`
- **User Management**: `/api/v1/users/{GET,POST,PUT,DELETE}` (admin-only)
- **Health**: `/api/v1/health/`

**Documentation**:
- **System Guide**: `backend/AUTHENTICATION.md`
- **API Reference**: `backend/API.md`
- **Interactive Docs**: http://localhost:8080/docs

### Testing Infrastructure

**TestContainers Implementation**:
- **PostgreSQL 17**: Production-like testing environment
- **SQLite Fallback**: CI/CD friendly testing without Docker
- **Transaction Isolation**: Each test in isolated transaction with rollback
- **Comprehensive Coverage**: 50 tests covering all authentication flows

**Example Test**:
```python
def test_login_success(test_client, admin_user, test_db):
    response = test_client.post("/api/v1/auth/login", json={
        "username": admin_user.username,
        "password": "password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == admin_user.username
```

### Security Architecture

**Multi-Layer Protection**:
- **Client-Side**: Svelte authentication state management with route guards
- **Server-Side**: nginx auth_request validates all static file access against JWT tokens
- **API Layer**: FastAPI dependencies enforce authentication and authorization
- **Database Layer**: Encrypted password storage and audit trail logging

**nginx auth_request Flow**:
```nginx
location / {
    auth_request /api/v1/auth/verify;  # Validates JWT token
    error_page 401 = @error401;        # Redirect to login on failure
    try_files $uri $uri/ /index.html;
}

location @error401 {
    return 302 /login?redirect=$request_uri;
}
```

### Future Extensibility

The authentication system is designed for enterprise integration:

**SSO Ready**:
- User types enum supports local, SSO, and SCIM users
- Auth providers table configured for SAML/OIDC integration
- External ID fields for provider-specific user identification

**SCIM Provisioning**:
- Schema includes SCIM-compatible fields and synchronization tracking
- Provider configuration supports SCIM endpoints and bearer tokens
- User provisioning status and last sync timestamps

## WebSocket Development

### Real-time Features

**Implementation Pattern**:
```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Handle messages
```

## Performance Considerations

### Backend Optimization

- Use async/await for all I/O operations
- Implement connection pooling for database
- Use SQLModel select() for efficient queries
- Implement caching for frequent lookups

### Frontend Optimization

- Lazy load routes and components
- Implement virtual scrolling for large lists
- Use Svelte stores for state management
- Optimize bundle size with tree shaking

## Debugging

### Backend Debugging

**Logging**:
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/approvals")
async def create_approval(approval: ApprovalCreate):
    logger.info(f"Creating approval for hash: {approval.application_hash}")
    # Implementation
```

**Database Query Debugging**:
```python
# Enable SQL logging in development
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Frontend Debugging

**Browser DevTools**:
- Use Svelte DevTools extension
- Monitor network requests to `/api` endpoints
- Check console for TypeScript errors

## Deployment

### Development Deployment

```bash
# Standard development
make up

# With file watching
docker-compose up --watch
```

### Production Deployment

```bash
# Build production images
make prod-build

# Deploy to production
make prod-up
```

## Troubleshooting

### Common Issues

**Backend won't start**:
1. Check database connection in logs: `make logs-backend`
2. Verify environment variables in `backend/.env`
3. Ensure database is running: `make logs`

**Frontend build fails**:
1. Check Node.js version compatibility
2. Clear node_modules and reinstall: `cd frontend && rm -rf node_modules yarn.lock && yarn install`
3. Check TypeScript errors: `cd frontend && yarn run check`
4. For persistent dependency issues, try: `cd frontend && yarn install --frozen-lockfile`

**Database connection issues**:
1. Verify PostgreSQL is running: `make logs`
2. Check connection settings in docker-compose.yml
3. Test connection: `make shell-db`

### Getting Help

1. Check logs: `make logs`
2. Review configuration files
3. Test with minimal reproduction case
4. Check similar issues in project repository