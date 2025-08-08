"""Authentication-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")


class RefreshRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(..., description="JWT refresh token")


class ChangePasswordRequest(BaseModel):
    """Request model for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class TokenResponse(BaseModel):
    """Response model for JWT tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserProfile" = Field(..., description="User profile information")


class UserProfile(BaseModel):
    """User profile information for API responses."""
    
    id: UUID = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    display_name: Optional[str] = Field(None, description="Display name")
    department: Optional[str] = Field(None, description="Department")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(..., description="Account active status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    user_type: str = Field(..., description="User type (local, sso, scim)")
    
    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """Response model for user operations."""
    
    id: UUID = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    display_name: Optional[str] = Field(None, description="Display name")
    department: Optional[str] = Field(None, description="Department")
    title: Optional[str] = Field(None, description="Job title")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(..., description="Account active status")
    is_provisioned: bool = Field(..., description="Provisioning status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    user_type: str = Field(..., description="User type (local, sso, scim)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: Optional[str] = Field(None, min_length=8, description="Password (required for local users)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    user_type: str = Field(default="local", description="User type (local, sso, scim)")


class UpdateUserRequest(BaseModel):
    """Request model for updating user information."""
    
    email: Optional[EmailStr] = Field(None, description="Email address")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    is_active: Optional[bool] = Field(None, description="Account active status")


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Application-specific error code")


# Forward reference resolution
LoginResponse.model_rebuild()