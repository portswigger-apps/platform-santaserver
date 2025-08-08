"""FastAPI dependencies for authentication and authorization."""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.database import get_db
from app.core.security import JWTManager
from app.models.auth import GroupRole, Role, User, UserGroup, UserRole, UserSession

# Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token (optional, returns None if not authenticated).

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User instance or None if not authenticated
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = JWTManager.verify_token(token)

    if not payload:
        return None

    # Check if token is revoked
    jti = payload.get("jti")
    if jti:
        session_stmt = select(UserSession).where(UserSession.token_jti == jti, UserSession.is_revoked.is_(False))
        session_result = db.exec(session_stmt).first()
        if not session_result:
            return None

    # Get user
    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        return None

    user_stmt = select(User).where(User.id == user_uuid, User.is_active.is_(True))
    user = db.exec(user_stmt).first()

    return user


async def get_current_user(user: Optional[User] = Depends(get_current_user_optional)) -> User:
    """
    Get current user from JWT token (required).

    Args:
        user: User from get_current_user_optional dependency

    Returns:
        User instance

    Raises:
        HTTPException: If user not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User instance

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_permissions(
    user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> Dict[str, List[str]]:
    """
    Get effective permissions for current user from roles and groups.

    Args:
        user: Current active user
        db: Database session

    Returns:
        Dictionary of resource -> list of actions
    """
    permissions = {}

    # Get direct user roles
    user_roles_stmt = select(Role).join(UserRole).where(UserRole.user_id == user.id)
    user_roles = db.exec(user_roles_stmt).all()

    # Get roles through groups
    group_roles_stmt = select(Role).join(GroupRole).join(UserGroup).where(UserGroup.user_id == user.id)
    group_roles = db.exec(group_roles_stmt).all()

    # Combine all roles
    all_roles = list(user_roles) + list(group_roles)

    # Merge permissions from all roles
    for role in all_roles:
        if role.permissions:
            for resource, actions in role.permissions.items():
                if resource not in permissions:
                    permissions[resource] = set()
                if isinstance(actions, list):
                    permissions[resource].update(actions)
                elif isinstance(actions, str):
                    permissions[resource].add(actions)

    # Convert sets back to lists
    return {resource: list(actions) for resource, actions in permissions.items()}


def require_permissions(resource: str, action: str):
    """
    Create a dependency that requires specific permissions.

    Args:
        resource: Resource name (e.g., 'users', 'groups')
        action: Action name (e.g., 'create', 'read', 'update', 'delete')

    Returns:
        FastAPI dependency function
    """

    async def permission_dependency(user_permissions: Dict[str, List[str]] = Depends(get_user_permissions)):
        if resource not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied: no permissions for resource '{resource}'"
            )

        if action not in user_permissions[resource]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: action '{action}' not allowed for resource '{resource}'",
            )

        return True

    return permission_dependency


def require_role(role_name: str):
    """
    Create a dependency that requires a specific role.

    Args:
        role_name: Name of required role

    Returns:
        FastAPI dependency function
    """

    async def role_dependency(user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        # Check direct user roles
        user_role_stmt = select(Role).join(UserRole).where(UserRole.user_id == user.id, Role.name == role_name)
        direct_role = db.exec(user_role_stmt).first()

        if direct_role:
            return True

        # Check roles through groups
        group_role_stmt = (
            select(Role).join(GroupRole).join(UserGroup).where(UserGroup.user_id == user.id, Role.name == role_name)
        )
        group_role = db.exec(group_role_stmt).first()

        if group_role:
            return True

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied: role '{role_name}' required")

    return role_dependency


def require_admin():
    """Dependency that requires admin role."""
    return require_role("admin")
