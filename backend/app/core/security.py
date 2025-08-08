"""Security utilities for password hashing and JWT token management."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Security utilities for authentication and authorization."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password against security policy.

        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []

        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")

        if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if settings.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")

        if settings.PASSWORD_REQUIRE_SYMBOLS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def generate_password_expiry() -> datetime:
        """Generate password expiry date based on policy."""
        return datetime.now(timezone.utc) + timedelta(days=settings.PASSWORD_EXPIRY_DAYS)


class JWTManager:
    """JWT token management utilities."""

    @staticmethod
    def create_access_token(
        subject: Union[str, UUID],
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a JWT access token.

        Args:
            subject: User ID or username for the token
            expires_delta: Token expiration time delta
            additional_claims: Additional claims to include in token

        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        # Generate unique token ID for revocation tracking
        jti = str(uuid.uuid4())

        to_encode = {"exp": expire, "sub": str(subject), "jti": jti, "type": "access"}

        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(subject: Union[str, UUID], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT refresh token.

        Args:
            subject: User ID or username for the token
            expires_delta: Token expiration time delta

        Returns:
            JWT refresh token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        # Generate unique token ID for revocation tracking
        jti = str(uuid.uuid4())

        to_encode = {"exp": expire, "sub": str(subject), "jti": jti, "type": "refresh"}

        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            return payload
        except JWTError:
            return None

    @staticmethod
    def extract_jti(token: str) -> Optional[str]:
        """
        Extract JTI (JWT ID) from token without full verification.
        Useful for revocation checks.

        Args:
            token: JWT token string

        Returns:
            JTI string or None if not found
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            return payload.get("jti")
        except JWTError:
            return None

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if token is expired without raising an exception.

        Args:
            token: JWT token string

        Returns:
            True if expired, False otherwise
        """
        try:
            jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            return False  # Token is valid and not expired
        except jwt.ExpiredSignatureError:
            return True  # Token is expired
        except JWTError:
            return True  # Token is invalid, treat as expired


class TokenPair:
    """Data class for access/refresh token pair."""

    def __init__(self, access_token: str, refresh_token: str, token_type: str = "bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type

        # Extract JTIs for session tracking
        self.access_jti = JWTManager.extract_jti(access_token)
        self.refresh_jti = JWTManager.extract_jti(refresh_token)

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API response."""
        return {"access_token": self.access_token, "refresh_token": self.refresh_token, "token_type": self.token_type}


def create_token_pair(user_id: UUID, additional_claims: Optional[Dict[str, Any]] = None) -> TokenPair:
    """
    Create an access/refresh token pair for a user.

    Args:
        user_id: User UUID
        additional_claims: Additional claims for access token

    Returns:
        TokenPair instance
    """
    access_token = JWTManager.create_access_token(subject=user_id, additional_claims=additional_claims)

    refresh_token = JWTManager.create_refresh_token(subject=user_id)

    return TokenPair(access_token, refresh_token)


def generate_secure_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string."""
    return secrets.token_urlsafe(length)
