"""User management API endpoints (Admin only)."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.core.database import get_db
from app.core.deps import require_admin, get_current_active_user
from app.core.security import SecurityUtils
from app.models.auth import User, UserTypeEnum
from app.schemas.auth import CreateUserRequest, UpdateUserRequest, UserResponse, MessageResponse
from app.services.auth_service import AuthenticationService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin()),  # Require admin role
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new user (Admin only).

    Requires admin role to access.
    """
    # Check if username already exists
    existing_user_stmt = select(User).where(User.username == user_data.username)
    existing_user = db.exec(existing_user_stmt).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    # Check if email already exists
    existing_email_stmt = select(User).where(User.email == user_data.email)
    existing_email = db.exec(existing_email_stmt).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    # Validate password for local users
    if user_data.user_type == "local":
        if not user_data.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required for local users")

        validation = SecurityUtils.validate_password_strength(user_data.password)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Password validation failed: {'; '.join(validation['errors'])}",
            )

    # Create new user
    from datetime import datetime, timezone
    from uuid import uuid4

    user = User(
        id=uuid4(),
        username=user_data.username,
        email=user_data.email,
        user_type=UserTypeEnum(user_data.user_type),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        display_name=user_data.display_name,
        department=user_data.department,
        title=user_data.title,
        phone=user_data.phone,
        is_active=True,
        is_provisioned=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    # Set password for local users
    if user_data.user_type == "local" and user_data.password:
        user.password_hash = SecurityUtils.get_password_hash(user_data.password)
        user.password_changed_at = datetime.now(timezone.utc)
        user.password_expires_at = SecurityUtils.generate_password_expiry()

    db.add(user)
    db.commit()
    db.refresh(user)

    # Log the user creation
    auth_service = AuthenticationService(db)
    await auth_service._log_security_event(
        current_user.id, "user_created", {"created_user_id": str(user.id), "username": user.username}, success=True
    )

    return UserResponse.model_validate(user)


@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin()),  # Require admin role
):
    """
    List all users with pagination (Admin only).

    Requires admin role to access.
    """
    stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    users = db.exec(stmt).all()

    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID, db: Session = Depends(get_db), _: bool = Depends(require_admin())  # Require admin role
):
    """
    Get user details by ID (Admin only).

    Requires admin role to access.
    """
    stmt = select(User).where(User.id == user_id)
    user = db.exec(stmt).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_data: UpdateUserRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin()),  # Require admin role
    current_user: User = Depends(get_current_active_user),
):
    """
    Update user information (Admin only).

    Requires admin role to access.
    """
    # Find user
    stmt = select(User).where(User.id == user_id)
    user = db.exec(stmt).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if email is being changed and already exists
    if user_data.email and user_data.email != user.email:
        existing_email_stmt = select(User).where(User.email == user_data.email)
        existing_email = db.exec(existing_email_stmt).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    # Update audit fields
    from datetime import datetime, timezone

    user.updated_at = datetime.now(timezone.utc)
    user.updated_by = current_user.id

    db.add(user)
    db.commit()
    db.refresh(user)

    # Log the user update
    auth_service = AuthenticationService(db)
    await auth_service._log_security_event(
        current_user.id,
        "user_updated",
        {"updated_user_id": str(user.id), "username": user.username, "fields": list(update_data.keys())},
        success=True,
    )

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin()),  # Require admin role
    current_user: User = Depends(get_current_active_user),
):
    """
    Deactivate user (soft delete) (Admin only).

    This doesn't actually delete the user, just deactivates them.
    Requires admin role to access.
    """
    # Find user
    stmt = select(User).where(User.id == user_id)
    user = db.exec(stmt).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")

    # Deactivate user
    user.is_active = False
    from datetime import datetime, timezone

    user.updated_at = datetime.now(timezone.utc)
    user.updated_by = current_user.id

    db.add(user)
    db.commit()

    # Revoke all user sessions
    auth_service = AuthenticationService(db)
    revoked_count = await auth_service.revoke_all_user_sessions(user=user, reason="admin_deactivated")

    # Log the user deactivation
    await auth_service._log_security_event(
        current_user.id,
        "user_deactivated",
        {"deactivated_user_id": str(user.id), "username": user.username, "sessions_revoked": revoked_count},
        success=True,
    )

    return MessageResponse(message=f"User {user.username} has been deactivated")
