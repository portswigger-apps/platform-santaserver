# PRD 003 - Authentication and RBAC System (MVP)

**Document Version:** 2.0  
**Created:** 2025-08-07  
**Status:** Draft  

## Executive Summary

This PRD defines the MVP authentication and RBAC system for SantaServer, focusing on local user authentication with users, groups, and roles functionality. Designed with extensible architecture to support future SSO sign-in and SCIM provisioning while maintaining MVP simplicity.

## MVP Objectives

### Core Features
- Local user authentication with bcrypt password hashing
- User, Group, and Role management with many-to-many relationships
- JWT-based session management
- Extensible user type system (local, SSO, SCIM) with provider configuration
- Admin interface with user type visibility and management
- Database schema management with Alembic migrations
- Environment-based initial admin user creation

### Success Criteria
- Users can login/logout with username/password
- Admins can manage users, groups, and roles
- Role-based access control enforced on all endpoints
- Database schema versioned with Alembic migrations
- Secure session management with token refresh

## Database Schema (Alembic Managed)

### Core Tables

```sql
-- User authentication types enum for extensibility
CREATE TYPE user_type AS ENUM ('local', 'sso', 'scim');
CREATE TYPE provider_type AS ENUM ('saml2', 'oidc', 'scim_v2');

-- Enhanced Users table with extensibility for future SSO/SCIM support
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    
    -- Authentication type and credentials
    user_type user_type DEFAULT 'local' NOT NULL,
    password_hash VARCHAR(255), -- nullable for SSO/SCIM users
    
    -- External identity integration (for future SSO/SCIM)
    external_id VARCHAR(255), -- Provider-specific user ID
    provider_name VARCHAR(100), -- Reference to auth_providers.name
    
    -- Enhanced profile data (SCIM-compatible)
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(200),
    department VARCHAR(100),
    title VARCHAR(100),
    phone VARCHAR(50),
    
    -- Status and lifecycle management
    is_active BOOLEAN DEFAULT true,
    is_provisioned BOOLEAN DEFAULT false, -- SCIM provisioning status
    last_login TIMESTAMP,
    last_sync TIMESTAMP, -- Last SCIM sync timestamp
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    -- Data integrity constraints
    CONSTRAINT chk_password_required_local CHECK (
        (user_type = 'local' AND password_hash IS NOT NULL) OR 
        (user_type IN ('sso', 'scim'))
    ),
    CONSTRAINT chk_external_id_for_external_users CHECK (
        (user_type = 'local' AND external_id IS NULL) OR
        (user_type IN ('sso', 'scim') AND external_id IS NOT NULL)
    ),
    CONSTRAINT chk_provider_for_external_users CHECK (
        (user_type = 'local' AND provider_name IS NULL) OR
        (user_type IN ('sso', 'scim') AND provider_name IS NOT NULL)
    )
);

-- Authentication providers for future SSO/SCIM integration
CREATE TABLE auth_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'azure_ad', 'okta', 'google'
    display_name VARCHAR(200) NOT NULL,
    provider_type provider_type NOT NULL,
    is_enabled BOOLEAN DEFAULT false,
    
    -- Provider-specific configuration (encrypted)
    configuration JSONB DEFAULT '{}', -- certificates, endpoints, client IDs
    
    -- SCIM-specific settings
    scim_base_url VARCHAR(500),
    scim_bearer_token_hash VARCHAR(255), -- encrypted SCIM bearer token
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}', -- Flexible permissions storage
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Groups table with external source support
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- External source support for SCIM/SSO groups
    source_type VARCHAR(50) DEFAULT 'local',
    external_id VARCHAR(255),
    provider_name VARCHAR(100) REFERENCES auth_providers(name),
    last_sync TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    -- Constraint for external groups
    CONSTRAINT chk_external_group_fields CHECK (
        (source_type = 'local' AND external_id IS NULL AND provider_name IS NULL) OR
        (source_type IN ('scim', 'sso') AND external_id IS NOT NULL AND provider_name IS NOT NULL)
    )
);

-- User-Role relationships (many-to-many)
CREATE TABLE user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- User-Group relationships (many-to-many)
CREATE TABLE user_groups (
    user_id UUID NOT NULL,
    group_id UUID NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by UUID,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(id)
);

-- Group-Role relationships (many-to-many)
CREATE TABLE group_roles (
    group_id UUID NOT NULL,
    role_id UUID NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID,
    PRIMARY KEY (group_id, role_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- Session tracking
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID claim
    expires_at TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Performance Indexes

```sql
-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_external_id ON users(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_users_provider_name ON users(provider_name) WHERE provider_name IS NOT NULL;

-- Groups indexes
CREATE INDEX idx_groups_source_type ON groups(source_type);
CREATE INDEX idx_groups_external_id ON groups(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_groups_provider_name ON groups(provider_name) WHERE provider_name IS NOT NULL;

-- Sessions indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Relationship indexes
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_groups_user_id ON user_groups(user_id);
CREATE INDEX idx_group_roles_group_id ON group_roles(group_id);

-- Auth providers indexes
CREATE INDEX idx_auth_providers_name ON auth_providers(name);
CREATE INDEX idx_auth_providers_enabled ON auth_providers(is_enabled) WHERE is_enabled = true;
```

## Alembic Migration Strategy

### Initial Setup
```bash
# Initialize Alembic in project
alembic init alembic

# Configure alembic.ini with database URL
# Set script_location = alembic
```

### Migration Files Structure
```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_default_roles_data.py
│   └── 003_admin_user_creation.py
├── env.py
└── script.py.mako
```

### Key Migration Commands
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history --verbose
```

### Default Data Migration (002_default_roles_data.py)
```python
def upgrade():
    # Insert default roles
    op.execute("""
        INSERT INTO roles (name, display_name, description, permissions, is_system_role) VALUES
        ('admin', 'Administrator', 'Full system access', 
         '{"users": ["create", "read", "update", "delete"],
           "groups": ["create", "read", "update", "delete"],
           "roles": ["create", "read", "update", "delete"],
           "santa": ["create", "read", "update", "delete", "approve"],
           "system": ["configure", "monitor", "audit"]}', true),
        ('user', 'User', 'Standard user access',
         '{"santa": ["read", "create", "update"],
           "approvals": ["request", "vote"],
           "profile": ["read", "update"]}', true)
    """)
```

## Core API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/login` - User login with JWT response
- `POST /api/v1/auth/logout` - Session invalidation
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/profile` - Current user profile
- `PUT /api/v1/auth/profile` - Update user profile
- `POST /api/v1/auth/change-password` - Password change

### User Management (Admin Only)
- `GET /api/v1/users` - List users with pagination
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Deactivate user

### Group Management (Admin Only)
- `GET /api/v1/groups` - List all groups
- `POST /api/v1/groups` - Create new group
- `GET /api/v1/groups/{id}` - Get group details with members
- `PUT /api/v1/groups/{id}` - Update group
- `DELETE /api/v1/groups/{id}` - Delete group
- `POST /api/v1/groups/{id}/members` - Add users to group
- `DELETE /api/v1/groups/{id}/members/{user_id}` - Remove user from group

### Role Management (Admin Only)
- `GET /api/v1/roles` - List all roles
- `POST /api/v1/roles` - Create custom role
- `GET /api/v1/roles/{id}` - Get role details
- `PUT /api/v1/roles/{id}` - Update role (non-system roles only)

## Security Implementation

### Password Security
- bcrypt hashing with minimum cost factor 12
- Password strength validation (minimum 8 characters)
- Password change requires current password verification

### JWT Token Management
- Access tokens: 30-minute expiration
- Refresh tokens: 7-day expiration
- Secure token storage and validation
- Token blacklist for immediate revocation

### Rate Limiting
- Login attempts: 5 per minute per IP
- Account lockout: 5 failed attempts = 15 minutes lockout
- API endpoints: 100 requests per minute per user

### Authorization Middleware
```python
def require_permission(resource: str, action: str):
    """Check user permissions against role-based access control."""
    user_permissions = get_user_effective_permissions(user_id)
    if not has_permission(user_permissions, resource, action):
        raise HTTPException(403, "Insufficient permissions")
```

## Environment Configuration

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/santaserver

# Initial admin setup
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here
ADMIN_EMAIL=admin@company.com

# JWT configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security settings
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

## Implementation Plan

### Phase 1: Core Authentication (Sprint 1)
1. Alembic setup and initial schema migration
2. User model and JWT authentication
3. Basic login/logout API endpoints
4. Password hashing and validation

### Phase 2: RBAC Foundation (Sprint 1-2)
1. Roles and permissions system
2. User-role relationships
3. Authorization middleware
4. Admin user creation from environment

### Phase 3: Group Management (Sprint 2)
1. Groups table and relationships
2. User-group and group-role assignments
3. Group management API endpoints
4. Permission resolution through groups

### Phase 4: Admin Interface (Sprint 2-3)
1. User management endpoints
2. Group management endpoints
3. Role management endpoints
4. Session management and monitoring

## Acceptance Criteria

### Authentication
- [x] Users login with username/password
- [x] Passwords securely hashed with bcrypt
- [x] JWT tokens generated and validated
- [x] Session refresh mechanism works
- [x] Rate limiting prevents brute force attacks

### Authorization
- [x] Role-based permissions enforced
- [x] Users can be assigned to multiple roles
- [x] Users can belong to multiple groups
- [x] Groups can have multiple roles
- [x] Effective permissions calculated correctly

### Data Management
- [x] All schema changes use Alembic migrations
- [x] Database indexes optimize query performance
- [x] Default roles created automatically
- [x] Admin user created from environment variables
- [x] Data integrity maintained with foreign key constraints

### Security
- [x] No sensitive data logged or exposed
- [x] All endpoints use proper authentication
- [x] Authorization checks prevent privilege escalation
- [x] Sessions can be revoked immediately
- [x] Password policies enforced

This MVP provides a solid foundation for SantaServer's authentication needs while maintaining simplicity and focusing on core functionality that can be extended in future iterations.