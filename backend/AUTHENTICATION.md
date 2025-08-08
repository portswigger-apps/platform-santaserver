# Authentication System Documentation

## Overview

SantaServer implements a comprehensive JWT-based authentication system with Role-Based Access Control (RBAC) as defined in PRD 003. The system provides enterprise-grade security with extensible architecture for future SSO and SCIM integration.

## Architecture

### Core Components

- **JWT Authentication**: Token-based authentication with access and refresh tokens
- **RBAC System**: Role-based permissions with hierarchical access control
- **User Management**: Complete CRUD operations with admin controls
- **Session Tracking**: Comprehensive session management with audit trails
- **Security Hardening**: Account lockout, password policies, audit logging

### Database Schema

The authentication system uses 8 core tables managed by Alembic migrations:

```sql
-- Core Tables
users                   -- User accounts with extensible types (local, sso, scim)
roles                   -- Role definitions with JSON permissions
groups                  -- User groups for organization
auth_providers         -- SSO/SCIM provider configuration (future)

-- Relationship Tables  
user_roles             -- Many-to-many user-role assignments
user_groups            -- Many-to-many user-group membership
group_roles            -- Many-to-many group-role assignments

-- Security Tables
user_sessions          -- JWT session tracking with JTI
security_audit_log     -- Comprehensive security event logging
```

## Authentication Flow

### Login Process

1. **Credential Validation**: Username/password verified against bcrypt hash
2. **Account Security Checks**: Account lockout, password expiration validation
3. **Token Generation**: JWT access token (30min) + refresh token (7 days) created
4. **Session Creation**: Session record with JTI tracking for revocation
5. **Audit Logging**: Successful/failed login attempts logged with IP/user agent

```python
# Example login implementation
async def authenticate_user(username: str, password: str, ip_address: str, user_agent: str):
    # 1. Find user and validate account status
    user = await get_user_by_username(username)
    if not user or not user.is_active:
        await log_security_event(None, 'login_failed', ip_address, user_agent)
        return None
    
    # 2. Check account lockout
    if user.locked_until and user.locked_until > datetime.now():
        await log_security_event(user.id, 'login_blocked', ip_address, user_agent)
        return None
    
    # 3. Verify password
    if not verify_password(password, user.password_hash):
        await increment_failed_attempts(user.id)
        await log_security_event(user.id, 'login_failed', ip_address, user_agent)
        return None
    
    # 4. Generate tokens and create session
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    await create_user_session(user.id, access_token.jti, refresh_token.jti)
    
    # 5. Log successful login
    await log_security_event(user.id, 'login_success', ip_address, user_agent)
    return user
```

### Token Management

**Access Tokens**:
- **Duration**: 30 minutes
- **Claims**: user_id, roles, permissions, JTI, expiration
- **Usage**: API authentication via Bearer token

**Refresh Tokens**:
- **Duration**: 7 days  
- **Purpose**: Generate new access tokens without re-authentication
- **Security**: Automatic rotation on use, JTI tracking for revocation

```python
# Token structure
{
  "sub": "user_id",           # Subject (user ID)
  "jti": "unique_token_id",   # JWT ID for revocation
  "roles": ["admin", "user"], # User roles
  "exp": 1234567890,          # Expiration timestamp
  "iat": 1234567880,          # Issued at timestamp
  "type": "access"            # Token type
}
```

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/auth/login` | POST | User login with JWT response | No |
| `/api/v1/auth/refresh` | POST | Refresh access token | Refresh token |
| `/api/v1/auth/logout` | POST | Invalidate current session | Access token |
| `/api/v1/auth/logout-all` | POST | Invalidate all user sessions | Access token |
| `/api/v1/auth/profile` | GET | Get current user profile | Access token |
| `/api/v1/auth/profile` | PUT | Update user profile | Access token |
| `/api/v1/auth/change-password` | POST | Change user password | Access token |
| `/api/v1/auth/verify` | GET | Verify token validity | Access token |

### User Management Endpoints (Admin Only)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/users/` | POST | Create new user | Admin role |
| `/api/v1/users/` | GET | List users (paginated) | Admin role |
| `/api/v1/users/{id}` | GET | Get user details | Admin role |
| `/api/v1/users/{id}` | PUT | Update user | Admin role |
| `/api/v1/users/{id}` | DELETE | Deactivate user | Admin role |

### Request/Response Examples

**Login Request**:
```json
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "SecurePassword123!"
}
```

**Login Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@company.com",
    "roles": ["admin"],
    "permissions": {
      "users": ["create", "read", "update", "delete"],
      "system": ["configure", "monitor", "audit"]
    }
  }
}
```

## Security Features

### Password Security

- **Hashing**: bcrypt with 12 rounds (configurable)
- **Complexity Requirements**: 8+ characters, uppercase, lowercase, numbers, symbols
- **Expiration**: 90-day password expiration (configurable)
- **History**: Prevent reuse of last 5 passwords
- **Account Lockout**: 5 failed attempts = 15-minute lockout

```python
# Password validation
def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Uppercase
        return False
    if not re.search(r'[a-z]', password):  # Lowercase
        return False
    if not re.search(r'\d', password):     # Numbers
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Symbols
        return False
    return True
```

### Session Security

- **JTI Tracking**: Every JWT has unique ID for individual revocation
- **Device Fingerprinting**: IP address and User-Agent tracking
- **Session Limits**: Configurable maximum concurrent sessions
- **Automatic Cleanup**: Expired sessions automatically purged

### Rate Limiting & Protection

- **Login Attempts**: Max 5 attempts per minute per IP
- **Account Lockout**: Progressive lockout duration
- **API Rate Limits**: 100 requests per minute per authenticated user
- **Brute Force Protection**: IP-based and account-based protections

## Role-Based Access Control (RBAC)

### Permission Model

Permissions are stored as JSON in the roles table, allowing flexible permission schemes:

```json
{
  "users": ["create", "read", "update", "delete"],
  "groups": ["create", "read", "update", "delete"],
  "roles": ["create", "read", "update", "delete"],
  "santa": ["create", "read", "update", "delete", "approve"],
  "system": ["configure", "monitor", "audit"]
}
```

### Default Roles

**Admin Role**:
- Full system access including user management
- Can create, modify, and delete users, groups, and roles
- Access to system configuration and monitoring
- Santa rule approval and management

**User Role**:
- Standard user access for Santa management
- Can create and manage own Santa rules
- Can request approvals and participate in voting
- Limited to own profile management

### Permission Checking

```python
# FastAPI dependency for permission checking
def require_permission(resource: str, action: str):
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = get_effective_permissions(current_user)
        if not has_permission(user_permissions, resource, action):
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return permission_checker

# Usage in endpoints
@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("users", "create"))
):
    return await create_new_user(user_data)
```

## Database Migrations

The authentication system is implemented through 3 Alembic migrations:

### Migration 001: Initial Schema
- Creates all tables, indexes, and constraints
- Defines custom enum types (user_type, provider_type)
- Sets up extensible architecture for SSO/SCIM

### Migration 002: Foreign Key Constraints
- Resolves circular dependencies in user audit fields
- Adds proper referential integrity constraints

### Migration 003: Default Data
- Creates default admin and user roles
- Inserts system user for automated operations
- Sets up initial permission structures

```bash
# Run migrations
cd backend
uv run alembic upgrade head

# Check migration status
uv run alembic current
uv run alembic history --verbose
```

## Testing

### Test Infrastructure

The authentication system uses comprehensive testing with TestContainers:

- **PostgreSQL TestContainers**: Production-like database testing
- **SQLite Fallback**: CI/CD friendly testing without Docker
- **Transaction Isolation**: Each test in isolated transaction with rollback
- **Fixture Management**: Admin user, JWT token, and database fixtures

### Test Coverage

50 comprehensive tests covering:

- **Authentication Flows**: Login, logout, token refresh, password change
- **Authorization**: Permission checking, role-based access control
- **Security**: Password validation, account lockout, audit logging
- **User Management**: CRUD operations, admin-only access
- **Edge Cases**: Invalid tokens, expired sessions, locked accounts

```bash
# Run all authentication tests
cd backend
uv run pytest tests/test_auth_endpoints.py -v

# Run with coverage
uv run pytest --cov=app tests/ --cov-report=html
```

## Environment Configuration

### Required Settings

```bash
# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:pass@localhost/santaserver

# Security Settings
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Password Policies
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SYMBOLS=true
PASSWORD_EXPIRY_DAYS=90
PASSWORD_HISTORY_COUNT=5

# Initial Admin Setup (optional)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here
ADMIN_EMAIL=admin@company.com
```

### Production Considerations

- **JWT Secret**: Use cryptographically secure random key (32+ bytes)
- **Database**: Use connection pooling for production loads
- **Logging**: Configure structured logging for security events
- **Monitoring**: Set up alerts for failed login attempts and account lockouts
- **Backup**: Regular backup of user and audit data

## Extensibility

### SSO Integration (Future)

The system is designed for future SSO integration:

```python
# User types support external authentication
class UserType(str, Enum):
    LOCAL = "local"      # Current username/password
    SSO = "sso"         # SAML/OIDC integration
    SCIM = "scim"       # SCIM provisioning

# Provider configuration ready for SAML/OIDC
class AuthProvider(SQLModel, table=True):
    name: str                    # "azure_ad", "okta", etc.
    provider_type: ProviderType  # "saml2", "oidc", "scim_v2"
    configuration: dict          # Provider-specific config
    is_enabled: bool = False
```

### SCIM Provisioning (Future)

Schema includes SCIM-compatible fields:

- `external_id`: Provider-specific user identifier
- `provider_name`: Reference to auth provider
- `last_sync`: SCIM synchronization timestamp
- `is_provisioned`: SCIM provisioning status

## Troubleshooting

### Common Issues

**JWT Token Invalid**:
- Check token expiration and refresh if needed
- Verify JWT_SECRET_KEY matches between token creation and validation
- Ensure token includes required claims (sub, jti, exp)

**Account Locked**:
- Check `locked_until` field in users table
- Reset lockout: `UPDATE users SET failed_login_attempts=0, locked_until=NULL WHERE username='user'`
- Verify lockout duration configuration

**Permission Denied**:
- Verify user has required role assignments in `user_roles` table
- Check role permissions JSON for required resource/action
- Ensure effective permissions calculation includes group roles

**Database Connection**:
- Verify PostgreSQL is running and accessible
- Check DATABASE_URL configuration
- Run migrations: `uv run alembic upgrade head`

### Logging and Monitoring

Security events are logged to `security_audit_log` table:

```sql
-- View recent login attempts
SELECT user_id, event_type, success, ip_address, timestamp 
FROM security_audit_log 
WHERE event_type IN ('login_success', 'login_failed')
ORDER BY timestamp DESC LIMIT 50;

-- Check account lockouts
SELECT username, failed_login_attempts, locked_until
FROM users 
WHERE locked_until IS NOT NULL AND locked_until > NOW();

-- Monitor failed login patterns
SELECT ip_address, COUNT(*) as failed_attempts
FROM security_audit_log 
WHERE event_type = 'login_failed' 
  AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
ORDER BY failed_attempts DESC;
```

## API Usage Examples

### Authentication Flow

```python
import httpx

# 1. Login
login_response = httpx.post("http://localhost:8080/api/v1/auth/login", json={
    "username": "admin",
    "password": "password"
})
tokens = login_response.json()

# 2. Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
profile = httpx.get("http://localhost:8080/api/v1/auth/profile", headers=headers)

# 3. Refresh token when expired
refresh_response = httpx.post("http://localhost:8080/api/v1/auth/refresh", json={
    "refresh_token": tokens['refresh_token']
})
new_tokens = refresh_response.json()

# 4. Logout
httpx.post("http://localhost:8080/api/v1/auth/logout", headers=headers)
```

### User Management (Admin)

```python
# Create user
new_user = httpx.post("http://localhost:8080/api/v1/users/", headers=admin_headers, json={
    "username": "newuser",
    "email": "newuser@company.com",
    "password": "SecurePassword123!",
    "roles": ["user"]
})

# List users with pagination
users = httpx.get("http://localhost:8080/api/v1/users/?skip=0&limit=50", headers=admin_headers)

# Update user
updated_user = httpx.put(f"http://localhost:8080/api/v1/users/{user_id}", 
                        headers=admin_headers, json={"is_active": False})
```