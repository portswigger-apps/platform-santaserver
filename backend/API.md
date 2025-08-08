# SantaServer API Documentation

## Base URL
```
Development: http://localhost:8080/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

All API endpoints except `/auth/login` require Bearer token authentication:

```http
Authorization: Bearer <access_token>
```

### Token Types
- **Access Token**: 30-minute expiration, used for API requests
- **Refresh Token**: 7-day expiration, used to generate new access tokens

## Authentication Endpoints

### POST /auth/login
Authenticate user with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
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
    "display_name": "Administrator",
    "is_active": true,
    "user_type": "local",
    "roles": ["admin"],
    "permissions": {
      "users": ["create", "read", "update", "delete"],
      "groups": ["create", "read", "update", "delete"],
      "roles": ["create", "read", "update", "delete"],
      "santa": ["create", "read", "update", "delete", "approve"],
      "system": ["configure", "monitor", "audit"]
    },
    "created_at": "2025-08-08T12:00:00Z",
    "last_login": "2025-08-08T12:00:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `423 Locked`: Account locked due to failed attempts
- `422 Validation Error`: Missing or invalid request fields

---

### POST /auth/refresh
Generate new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token
- `422 Validation Error`: Missing refresh token

---

### POST /auth/logout
Invalidate current user session.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

### POST /auth/logout-all
Invalidate all user sessions across all devices.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out from all sessions"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

### GET /auth/profile
Get current user profile information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@company.com",
  "display_name": "Administrator",
  "first_name": "Admin",
  "last_name": "User",
  "department": "IT",
  "title": "System Administrator",
  "phone": "+1-555-0123",
  "is_active": true,
  "user_type": "local",
  "roles": ["admin"],
  "permissions": {
    "users": ["create", "read", "update", "delete"],
    "system": ["configure", "monitor", "audit"]
  },
  "created_at": "2025-08-08T12:00:00Z",
  "updated_at": "2025-08-08T12:00:00Z",
  "last_login": "2025-08-08T12:00:00Z",
  "password_expires_at": "2025-11-06T12:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

### PUT /auth/profile
Update current user profile information.

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "display_name": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "department": "string (optional)",
  "title": "string (optional)",
  "phone": "string (optional)"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@company.com",
  "display_name": "Updated Name",
  // ... rest of profile fields
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `422 Validation Error`: Invalid field values

---

### POST /auth/change-password
Change current user password.

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*(),.?":{}|<>)

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Current password incorrect
- `422 Validation Error`: Password doesn't meet requirements or passwords don't match

---

### GET /auth/verify
Verify current token validity and get user information.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@company.com",
  "roles": ["admin"],
  "permissions": {
    "users": ["create", "read", "update", "delete"]
  },
  "token_valid": true,
  "expires_at": "2025-08-08T12:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid, expired, or missing token

## User Management Endpoints (Admin Only)

### POST /users/
Create a new user account.

**Headers:**
```http
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Required Permissions:** `users.create`

**Request Body:**
```json
{
  "username": "string",
  "email": "string (valid email format)",
  "password": "string (must meet complexity requirements)",
  "display_name": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "department": "string (optional)",
  "title": "string (optional)",
  "phone": "string (optional)",
  "roles": ["string"] // Array of role names, optional, defaults to ["user"]
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "newuser",
  "email": "newuser@company.com",
  "display_name": "New User",
  "first_name": "New",
  "last_name": "User",
  "department": "Engineering",
  "title": "Developer",
  "phone": "+1-555-0124",
  "is_active": true,
  "user_type": "local",
  "roles": ["user"],
  "created_at": "2025-08-08T12:00:00Z",
  "updated_at": "2025-08-08T12:00:00Z",
  "last_login": null,
  "password_expires_at": "2025-11-06T12:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `409 Conflict`: Username or email already exists
- `422 Validation Error`: Invalid field values or password requirements not met

---

### GET /users/
List users with pagination and filtering.

**Headers:**
```http
Authorization: Bearer <admin_access_token>
```

**Required Permissions:** `users.read`

**Query Parameters:**
- `skip` (integer, optional): Number of users to skip (default: 0)
- `limit` (integer, optional): Maximum number of users to return (default: 50, max: 100)
- `search` (string, optional): Search in username, email, display_name
- `is_active` (boolean, optional): Filter by active status
- `user_type` (string, optional): Filter by user type (local, sso, scim)
- `role` (string, optional): Filter by role name

**Example Request:**
```http
GET /users/?skip=0&limit=25&search=admin&is_active=true&role=admin
```

**Response (200):**
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "admin",
      "email": "admin@company.com",
      "display_name": "Administrator",
      "first_name": "Admin",
      "last_name": "User",
      "department": "IT",
      "title": "System Administrator",
      "is_active": true,
      "user_type": "local",
      "roles": ["admin"],
      "created_at": "2025-08-08T12:00:00Z",
      "updated_at": "2025-08-08T12:00:00Z",
      "last_login": "2025-08-08T12:00:00Z"
    }
    // ... more users
  ],
  "total": 1,
  "skip": 0,
  "limit": 25,
  "has_more": false
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `422 Validation Error`: Invalid query parameters

---

### GET /users/{user_id}
Get detailed information about a specific user.

**Headers:**
```http
Authorization: Bearer <admin_access_token>
```

**Required Permissions:** `users.read`

**Path Parameters:**
- `user_id` (uuid): The user ID to retrieve

**Response (200):**
```json
{
  "id": "uuid",
  "username": "user123",
  "email": "user123@company.com",
  "display_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "department": "Engineering",
  "title": "Senior Developer",
  "phone": "+1-555-0125",
  "is_active": true,
  "user_type": "local",
  "roles": ["user"],
  "groups": ["developers", "senior-staff"],
  "permissions": {
    "santa": ["read", "create", "update"],
    "approvals": ["request", "vote"],
    "profile": ["read", "update"]
  },
  "created_at": "2025-08-08T12:00:00Z",
  "updated_at": "2025-08-08T12:00:00Z",
  "last_login": "2025-08-08T11:45:00Z",
  "password_expires_at": "2025-11-06T12:00:00Z",
  "failed_login_attempts": 0,
  "locked_until": null
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

---

### PUT /users/{user_id}
Update user information.

**Headers:**
```http
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**Required Permissions:** `users.update`

**Path Parameters:**
- `user_id` (uuid): The user ID to update

**Request Body:**
```json
{
  "email": "string (optional, valid email format)",
  "display_name": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "department": "string (optional)",
  "title": "string (optional)",
  "phone": "string (optional)",
  "is_active": "boolean (optional)",
  "roles": ["string"] // Array of role names, optional
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "user123",
  "email": "updated@company.com",
  // ... rest of user fields with updated values
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `409 Conflict`: Email already exists (if email updated)
- `422 Validation Error`: Invalid field values

---

### DELETE /users/{user_id}
Deactivate a user account (soft delete).

**Headers:**
```http
Authorization: Bearer <admin_access_token>
```

**Required Permissions:** `users.delete`

**Path Parameters:**
- `user_id` (uuid): The user ID to deactivate

**Response (200):**
```json
{
  "message": "User deactivated successfully"
}
```

**Note:** This endpoint deactivates the user (sets `is_active` to `false`) rather than permanently deleting the record. This preserves audit trails and allows for potential reactivation.

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `400 Bad Request`: Cannot deactivate your own account

## Health Check Endpoints

### GET /health/
Basic health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T12:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### GET /health/
Extended health check with system information (when running in Docker).

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T12:00:00Z",
  "version": "1.0.0",
  "environment": "development",
  "system": {
    "database": "connected",
    "redis": "connected",
    "docker": true,
    "container_id": "abc123..."
  },
  "uptime": "2h 15m 30s"
}
```

## Error Handling

All API endpoints return consistent error responses:

### Standard Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-08-08T12:00:00Z",
  "path": "/api/v1/endpoint"
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data or parameters
- **401 Unauthorized**: Authentication required or token invalid
- **403 Forbidden**: Access denied, insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists (e.g., username/email taken)
- **422 Unprocessable Entity**: Validation errors in request data
- **423 Locked**: Account locked due to security policy
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Authentication Error Codes

- `TOKEN_EXPIRED`: Access token has expired, use refresh token
- `TOKEN_INVALID`: Token is malformed or invalid
- `TOKEN_REVOKED`: Token has been revoked
- `ACCOUNT_LOCKED`: Account locked due to failed login attempts
- `PASSWORD_EXPIRED`: User password has expired
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions

### Validation Error Example

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 8}
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

## Rate Limiting

API endpoints have the following rate limits:

### Authentication Endpoints
- **Login**: 5 attempts per minute per IP address
- **Password Change**: 3 attempts per minute per user
- **Token Refresh**: 10 requests per minute per user

### General API Endpoints
- **Authenticated Users**: 100 requests per minute
- **Admin Operations**: 50 requests per minute (user management)

### Rate Limit Headers

When rate limits are approached, responses include headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
X-RateLimit-Retry-After: 60
```

### Rate Limit Error Response

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## Security Features

### Account Security
- **Password Policies**: Enforced complexity requirements
- **Account Lockout**: 5 failed attempts locks account for 15 minutes
- **Password Expiration**: 90-day expiration (configurable)
- **Password History**: Prevents reuse of last 5 passwords

### Session Security
- **JWT Security**: Cryptographically signed tokens
- **Token Expiration**: Short-lived access tokens (30 minutes)
- **Token Revocation**: Individual session revocation via JTI tracking
- **Device Tracking**: IP address and User-Agent logging

### Audit Logging
All authentication and authorization events are logged:
- Login attempts (successful/failed)
- Password changes
- Token generation/revocation
- Permission checks
- Administrative actions

## SDK Examples

### Python (httpx)

```python
import httpx
from datetime import datetime, timedelta

class SantaServerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        
    async def login(self, username: str, password: str):
        """Authenticate and store tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"])
            
            return data["user"]
    
    async def _ensure_valid_token(self):
        """Refresh token if needed"""
        if self.token_expires and datetime.now() >= self.token_expires:
            await self.refresh_access_token()
    
    async def refresh_access_token(self):
        """Refresh the access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"])
    
    async def get_profile(self):
        """Get current user profile"""
        await self._ensure_valid_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/auth/profile",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def create_user(self, user_data: dict):
        """Create a new user (admin only)"""
        await self._ensure_valid_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/",
                json=user_data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()

# Usage example
async def main():
    client = SantaServerClient("http://localhost:8080")
    
    # Login
    user = await client.login("admin", "password")
    print(f"Logged in as: {user['username']}")
    
    # Get profile
    profile = await client.get_profile()
    print(f"User roles: {profile['roles']}")
    
    # Create user (admin only)
    new_user = await client.create_user({
        "username": "newuser",
        "email": "newuser@company.com",
        "password": "SecurePass123!",
        "roles": ["user"]
    })
    print(f"Created user: {new_user['username']}")
```

### JavaScript/Node.js (fetch)

```javascript
class SantaServerClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpires = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        
        if (!response.ok) {
            throw new Error(`Login failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.accessToken = data.access_token;
        this.refreshToken = data.refresh_token;
        this.tokenExpires = new Date(Date.now() + data.expires_in * 1000);
        
        return data.user;
    }
    
    async ensureValidToken() {
        if (this.tokenExpires && new Date() >= this.tokenExpires) {
            await this.refreshAccessToken();
        }
    }
    
    async refreshAccessToken() {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh_token: this.refreshToken})
        });
        
        if (!response.ok) {
            throw new Error(`Token refresh failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.accessToken = data.access_token;
        this.refreshToken = data.refresh_token;
        this.tokenExpires = new Date(Date.now() + data.expires_in * 1000);
    }
    
    async apiRequest(path, options = {}) {
        await this.ensureValidToken();
        
        const response = await fetch(`${this.baseUrl}${path}`, {
            ...options,
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API request failed: ${error.detail}`);
        }
        
        return response.json();
    }
    
    async getProfile() {
        return this.apiRequest('/api/v1/auth/profile');
    }
    
    async listUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.apiRequest(`/api/v1/users/${query ? `?${query}` : ''}`);
    }
    
    async createUser(userData) {
        return this.apiRequest('/api/v1/users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
}

// Usage example
async function main() {
    const client = new SantaServerClient('http://localhost:8080');
    
    try {
        // Login
        const user = await client.login('admin', 'password');
        console.log(`Logged in as: ${user.username}`);
        
        // Get profile
        const profile = await client.getProfile();
        console.log(`User roles: ${profile.roles}`);
        
        // List users
        const users = await client.listUsers({limit: 10});
        console.log(`Found ${users.total} users`);
        
        // Create user
        const newUser = await client.createUser({
            username: 'newuser',
            email: 'newuser@company.com',
            password: 'SecurePass123!',
            roles: ['user']
        });
        console.log(`Created user: ${newUser.username}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}
```

## Interactive API Documentation

Visit the interactive API documentation at:
- **Development**: http://localhost:8080/docs
- **OpenAPI JSON**: http://localhost:8080/openapi.json

The interactive documentation provides:
- Complete endpoint documentation with examples
- Authentication testing interface
- Request/response schema validation
- Try-it-out functionality for all endpoints