# Development Guide

This guide covers development workflows, testing, and contribution guidelines for SantaServer.

## Development Environment

### Initial Setup

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

**Testing (TDD Approach)**:
```bash
# Run all tests
make test

# Watch mode for continuous testing
make test-watch

# Test specific module
cd backend && python -m pytest tests/test_health.py -v
```

**Code Quality**:
```bash
# Format code
make format-backend

# Lint code
make lint-backend

# Type checking
cd backend && mypy app/
```

**Database Management**:
```bash
# Access database shell
make shell-db

# Run migrations (when implemented)
cd backend && alembic upgrade head
```

#### Frontend Development (TypeScript/Svelte)

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
cd frontend && npm install

# Format code
make format-frontend

# Lint code
make lint-frontend

# Type checking
cd frontend && npm run check
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
cd backend && alembic revision --autogenerate -m "Add approval table"

# Run migrations
cd backend && alembic upgrade head

# Rollback migration
cd backend && alembic downgrade -1
```

## Authentication Development

### Azure AD Integration

**Configuration**:
- Uses `fastapi-azure-auth` package
- Configured in `app/core/config.py`
- Requires TENANT_ID, CLIENT_ID, CLIENT_SECRET

**Usage Pattern**:
```python
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.CLIENT_ID,
    tenant_id=settings.TENANT_ID,
    scopes={"api://your-api/access": "Access API"}
)

@router.get("/protected")
async def protected_endpoint(user=Depends(azure_scheme)):
    return {"user": user}
```

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
2. Clear node_modules: `cd frontend && rm -rf node_modules && npm install`
3. Check TypeScript errors: `cd frontend && npm run check`

**Database connection issues**:
1. Verify PostgreSQL is running: `make logs`
2. Check connection settings in docker-compose.yml
3. Test connection: `make shell-db`

### Getting Help

1. Check logs: `make logs`
2. Review configuration files
3. Test with minimal reproduction case
4. Check similar issues in project repository