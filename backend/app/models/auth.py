"""Authentication and authorization models."""

import enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import (
    JSON,
    Column,
)
from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class UserTypeEnum(str, enum.Enum):
    """User authentication type enumeration."""

    LOCAL = "local"
    SSO = "sso"
    SCIM = "scim"


class ProviderTypeEnum(str, enum.Enum):
    """Authentication provider type enumeration."""

    SAML2 = "saml2"
    OIDC = "oidc"
    SCIM_V2 = "scim_v2"


class AuthProvider(SQLModel, table=True):
    """Authentication providers for future SSO/SCIM integration."""

    __tablename__ = "auth_providers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100, unique=True, description="Provider name (e.g., 'azure_ad', 'okta')")
    display_name: str = Field(max_length=200, description="Human readable provider name")
    provider_type: ProviderTypeEnum = Field(description="Type of authentication provider")
    is_enabled: bool = Field(default=False, description="Whether provider is currently enabled")

    # Provider-specific configuration (encrypted)
    configuration: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON), description="Provider configuration (encrypted)"
    )

    # SCIM-specific settings
    scim_base_url: Optional[str] = Field(default=None, max_length=500, description="SCIM endpoint base URL")
    scim_bearer_token_hash: Optional[str] = Field(
        default=None, max_length=255, description="Encrypted SCIM bearer token"
    )

    # Audit fields
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class User(SQLModel, table=True):
    """Enhanced Users table with extensibility for future SSO/SCIM support."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(max_length=255, unique=True, description="Unique username")
    email: str = Field(max_length=255, unique=True, description="User email address")

    # Authentication type and credentials
    user_type: UserTypeEnum = Field(default=UserTypeEnum.LOCAL, description="Authentication type")
    password_hash: Optional[str] = Field(default=None, max_length=255, description="Hashed password for local users")

    # Password security and policies
    password_expires_at: Optional[datetime] = Field(default=None, description="Password expiration timestamp")
    password_changed_at: Optional[datetime] = Field(default=None, description="Last password change timestamp")
    failed_login_attempts: int = Field(default=0, description="Number of failed login attempts")
    locked_until: Optional[datetime] = Field(default=None, description="Account lock expiration")

    # External identity integration (for future SSO/SCIM)
    external_id: Optional[str] = Field(default=None, max_length=255, description="Provider-specific user ID")
    provider_name: Optional[str] = Field(default=None, max_length=100, description="Reference to auth_providers.name")

    # Enhanced profile data (SCIM-compatible)
    first_name: Optional[str] = Field(default=None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(default=None, max_length=100, description="User's last name")
    display_name: Optional[str] = Field(default=None, max_length=200, description="Display name")
    department: Optional[str] = Field(default=None, max_length=100, description="Department")
    title: Optional[str] = Field(default=None, max_length=100, description="Job title")
    phone: Optional[str] = Field(default=None, max_length=50, description="Phone number")

    # Status and lifecycle management
    is_active: bool = Field(default=True, description="Whether user account is active")
    is_provisioned: bool = Field(default=False, description="SCIM provisioning status")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    last_sync: Optional[datetime] = Field(default=None, description="Last SCIM sync timestamp")

    # Audit fields (nullable to resolve circular reference)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None, foreign_key="users.id")

    # Relationships - we'll define these after all tables are defined
    # roles: List["UserRole"] = relationship(back_populates="user")
    # groups: List["UserGroup"] = relationship(back_populates="user")
    # sessions: List["UserSession"] = relationship(back_populates="user")


class Role(SQLModel, table=True):
    """Roles table for RBAC system."""

    __tablename__ = "roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True, description="Role name")
    display_name: str = Field(max_length=100, description="Human readable role name")
    description: Optional[str] = Field(default=None, description="Role description")
    permissions: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON), description="Flexible permissions storage"
    )
    is_system_role: bool = Field(default=False, description="Whether this is a system role")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Group(SQLModel, table=True):
    """Enhanced Groups table with external source support."""

    __tablename__ = "groups"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True, description="Group name")
    display_name: str = Field(max_length=100, description="Human readable group name")
    description: Optional[str] = Field(default=None, description="Group description")

    # External source support for SCIM/SSO groups
    source_type: str = Field(default="local", max_length=50, description="Source of the group")
    external_id: Optional[str] = Field(default=None, max_length=255, description="External provider group ID")
    provider_name: Optional[str] = Field(default=None, max_length=100, description="Provider name")
    last_sync: Optional[datetime] = Field(default=None, description="Last sync timestamp")

    # Audit fields
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    updated_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class UserRole(SQLModel, table=True):
    """User-Role relationships (many-to-many)."""

    __tablename__ = "user_roles"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    assigned_at: datetime = Field(default_factory=utc_now)
    assigned_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class UserGroup(SQLModel, table=True):
    """User-Group relationships (many-to-many)."""

    __tablename__ = "user_groups"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    group_id: UUID = Field(foreign_key="groups.id", primary_key=True)
    joined_at: datetime = Field(default_factory=utc_now)
    added_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class GroupRole(SQLModel, table=True):
    """Group-Role relationships (many-to-many)."""

    __tablename__ = "group_roles"

    group_id: UUID = Field(foreign_key="groups.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    assigned_at: datetime = Field(default_factory=utc_now)
    assigned_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class UserSession(SQLModel, table=True):
    """Session tracking with enhanced security."""

    __tablename__ = "user_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    token_jti: str = Field(max_length=255, unique=True, description="JWT ID claim")
    refresh_token_jti: Optional[str] = Field(default=None, max_length=255, description="Refresh token JTI")
    expires_at: datetime = Field(description="Token expiration timestamp")
    refresh_expires_at: Optional[datetime] = Field(default=None, description="Refresh token expiration")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    is_revoked: bool = Field(default=False, description="Whether session is revoked")
    revoked_at: Optional[datetime] = Field(default=None, description="Revocation timestamp")
    revoked_reason: Optional[str] = Field(default=None, max_length=100, description="Revocation reason")
    created_at: datetime = Field(default_factory=utc_now)


class SecurityAuditLog(SQLModel, table=True):
    """Security audit log for compliance and security monitoring."""

    __tablename__ = "security_audit_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    event_type: str = Field(max_length=50, description="Type of security event")
    event_details: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON), description="Event-specific details"
    )
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    success: bool = Field(description="Whether the event was successful")
    failure_reason: Optional[str] = Field(default=None, max_length=255, description="Failure reason if applicable")
    timestamp: datetime = Field(default_factory=utc_now)
