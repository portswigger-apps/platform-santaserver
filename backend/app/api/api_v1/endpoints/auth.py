"""Authentication API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_user_optional
from app.models.auth import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest, TokenResponse, 
    ChangePasswordRequest, MessageResponse, UserProfile
)
from app.services.auth_service import AuthenticationService

router = APIRouter()


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Authenticates user with username/password and returns JWT tokens.
    """
    ip_address, user_agent = get_client_info(request)
    auth_service = AuthenticationService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session and tokens
    token_pair = await auth_service.create_user_session(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return LoginResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer",
        user=UserProfile.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    ip_address, user_agent = get_client_info(request)
    auth_service = AuthenticationService(db)
    
    token_pair = await auth_service.refresh_token(
        refresh_token=refresh_data.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    User logout endpoint.
    
    Revokes the current session token.
    """
    ip_address, user_agent = get_client_info(request)
    auth_service = AuthenticationService(db)
    
    # Extract token from Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization header"
        )
    
    token = auth_header.split(" ", 1)[1]
    
    success = await auth_service.revoke_session(
        user=current_user,
        token=token,
        reason="user_logout",
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout"
        )
    
    return MessageResponse(message="Successfully logged out")


@router.post("/logout-all", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all sessions.
    
    Revokes all active sessions for the current user.
    """
    ip_address, user_agent = get_client_info(request)
    auth_service = AuthenticationService(db)
    
    revoked_count = await auth_service.revoke_all_user_sessions(
        user=current_user,
        reason="user_logout_all"
    )
    
    return MessageResponse(message=f"Successfully logged out from {revoked_count} sessions")


@router.get("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile information.
    """
    return UserProfile.from_orm(current_user)


@router.put("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    profile_data: dict,  # Generic dict for profile updates
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information.
    
    Users can only update their own profile fields (not security-related fields).
    """
    allowed_fields = {
        "first_name", "last_name", "display_name", 
        "department", "title", "phone"
    }
    
    updated = False
    for field, value in profile_data.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
            updated = True
    
    if updated:
        from datetime import datetime, timezone
        current_user.updated_at = datetime.now(timezone.utc)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    
    return UserProfile.from_orm(current_user)


@router.post("/change-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password.
    
    Requires current password for verification and revokes all other sessions.
    """
    ip_address, user_agent = get_client_info(request)
    auth_service = AuthenticationService(db)
    
    success, error_message = await auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return MessageResponse(message="Password changed successfully. Please login again with your new password.")


@router.get("/verify", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def verify_token(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Verify current JWT token and return user information.
    
    This endpoint can be used by frontend applications to verify if a token is still valid.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserProfile.from_orm(current_user)