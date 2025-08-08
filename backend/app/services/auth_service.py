"""Authentication service for user login, session management, and security audit."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import JWTManager, SecurityUtils, TokenPair, create_token_pair
from app.models.auth import SecurityAuditLog, User, UserSession, UserTypeEnum


class AuthenticationService:
    """Service for handling user authentication and session management."""

    def __init__(self, db: Session):
        self.db = db

    async def authenticate_user(
        self, username: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> Optional[User]:
        """
        Authenticate user with username/password.

        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            User instance if authentication successful, None otherwise
        """
        # Find user by username or email
        user_stmt = select(User).where((User.username == username) | (User.email == username))
        user = self.db.exec(user_stmt).first()

        if not user:
            await self._log_security_event(
                None,
                "login_failed",
                {"reason": "user_not_found", "username": username},
                ip_address,
                user_agent,
                success=False,
                failure_reason="User not found",
            )
            return None

        # Check if user is active
        if not user.is_active:
            await self._log_security_event(
                user.id,
                "login_failed",
                {"reason": "account_inactive"},
                ip_address,
                user_agent,
                success=False,
                failure_reason="Account inactive",
            )
            return None

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            await self._log_security_event(
                user.id,
                "login_failed",
                {"reason": "account_locked"},
                ip_address,
                user_agent,
                success=False,
                failure_reason="Account locked",
            )
            return None

        # Verify password for local users
        if user.user_type == UserTypeEnum.LOCAL:
            if not user.password_hash:
                await self._log_security_event(
                    user.id,
                    "login_failed",
                    {"reason": "no_password_set"},
                    ip_address,
                    user_agent,
                    success=False,
                    failure_reason="No password set",
                )
                return None

            if not SecurityUtils.verify_password(password, user.password_hash):
                # Increment failed attempts
                user.failed_login_attempts += 1

                # Lock account if too many failures
                if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(
                        minutes=settings.LOCKOUT_DURATION_MINUTES
                    )

                    await self._log_security_event(
                        user.id,
                        "account_locked",
                        {"failed_attempts": user.failed_login_attempts},
                        ip_address,
                        user_agent,
                        success=False,
                        failure_reason="Too many failed attempts",
                    )
                else:
                    await self._log_security_event(
                        user.id,
                        "login_failed",
                        {"reason": "invalid_password", "failed_attempts": user.failed_login_attempts},
                        ip_address,
                        user_agent,
                        success=False,
                        failure_reason="Invalid password",
                    )

                self.db.add(user)
                self.db.commit()
                return None

        # Reset failed attempts on successful authentication
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.locked_until = None

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.add(user)
        self.db.commit()

        await self._log_security_event(
            user.id, "login_successful", {"user_type": user.user_type.value}, ip_address, user_agent, success=True
        )

        return user

    async def create_user_session(
        self, user: User, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> TokenPair:
        """
        Create a new user session with JWT tokens.

        Args:
            user: Authenticated user
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            TokenPair with access and refresh tokens
        """
        # Create token pair
        token_pair = create_token_pair(
            user_id=user.id,
            additional_claims={"username": user.username, "email": user.email, "user_type": user.user_type.value},
        )

        # Calculate expiration times
        access_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        # Store session in database
        session = UserSession(
            user_id=user.id,
            token_jti=token_pair.access_jti,
            refresh_token_jti=token_pair.refresh_jti,
            expires_at=access_expires,
            refresh_expires_at=refresh_expires,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(session)
        self.db.commit()

        await self._log_security_event(
            user.id, "session_created", {"session_id": str(session.id)}, ip_address, user_agent, success=True
        )

        return token_pair

    async def refresh_token(
        self, refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> Optional[TokenPair]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: JWT refresh token
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            New TokenPair or None if refresh failed
        """
        # Verify refresh token
        payload = JWTManager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        refresh_jti = payload.get("jti")
        user_id = payload.get("sub")

        if not refresh_jti or not user_id:
            return None

        # Find session
        session_stmt = select(UserSession).where(
            UserSession.refresh_token_jti == refresh_jti, UserSession.is_revoked.is_(False)
        )
        session = self.db.exec(session_stmt).first()

        if not session or session.refresh_expires_at < datetime.now(timezone.utc):
            return None

        # Get user
        user_stmt = select(User).where(User.id == UUID(user_id), User.is_active.is_(True))
        user = self.db.exec(user_stmt).first()

        if not user:
            return None

        # Create new token pair
        new_token_pair = create_token_pair(
            user_id=user.id,
            additional_claims={"username": user.username, "email": user.email, "user_type": user.user_type.value},
        )

        # Update session with new tokens
        session.token_jti = new_token_pair.access_jti
        session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        # Rotate refresh token if configured
        if settings.REFRESH_TOKEN_ROTATION:
            session.refresh_token_jti = new_token_pair.refresh_jti
            session.refresh_expires_at = datetime.now(timezone.utc) + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )

        self.db.add(session)
        self.db.commit()

        await self._log_security_event(
            user.id, "token_refreshed", {"session_id": str(session.id)}, ip_address, user_agent, success=True
        )

        return new_token_pair

    async def revoke_session(
        self,
        user: User,
        token: str,
        reason: str = "user_logout",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """
        Revoke a user session.

        Args:
            user: User who owns the session
            token: Access or refresh token
            reason: Revocation reason
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            True if session was revoked, False otherwise
        """
        jti = JWTManager.extract_jti(token)
        if not jti:
            return False

        # Find session by either access or refresh token JTI
        session_stmt = select(UserSession).where(
            UserSession.user_id == user.id,
            (UserSession.token_jti == jti) | (UserSession.refresh_token_jti == jti),
            UserSession.is_revoked.is_(False),
        )
        session = self.db.exec(session_stmt).first()

        if not session:
            return False

        # Revoke session
        session.is_revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = reason

        self.db.add(session)
        self.db.commit()

        await self._log_security_event(
            user.id,
            "session_revoked",
            {"session_id": str(session.id), "reason": reason},
            ip_address,
            user_agent,
            success=True,
        )

        return True

    async def revoke_all_user_sessions(
        self, user: User, reason: str = "admin_action", exclude_session_id: Optional[UUID] = None
    ) -> int:
        """
        Revoke all sessions for a user.

        Args:
            user: User whose sessions to revoke
            reason: Revocation reason
            exclude_session_id: Session ID to exclude from revocation

        Returns:
            Number of sessions revoked
        """
        sessions_stmt = select(UserSession).where(UserSession.user_id == user.id, UserSession.is_revoked.is_(False))

        if exclude_session_id:
            sessions_stmt = sessions_stmt.where(UserSession.id != exclude_session_id)

        sessions = self.db.exec(sessions_stmt).all()
        revoked_count = 0

        for session in sessions:
            session.is_revoked = True
            session.revoked_at = datetime.now(timezone.utc)
            session.revoked_reason = reason
            self.db.add(session)
            revoked_count += 1

        if revoked_count > 0:
            self.db.commit()

            await self._log_security_event(
                user.id, "all_sessions_revoked", {"revoked_count": revoked_count, "reason": reason}, success=True
            )

        return revoked_count

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password.

        Args:
            user: User changing password
            current_password: Current password for verification
            new_password: New password
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (success, error_message)
        """
        # Verify current password for local users
        if user.user_type == UserTypeEnum.LOCAL:
            if not user.password_hash or not SecurityUtils.verify_password(current_password, user.password_hash):
                await self._log_security_event(
                    user.id,
                    "password_change_failed",
                    {"reason": "invalid_current_password"},
                    ip_address,
                    user_agent,
                    success=False,
                    failure_reason="Invalid current password",
                )
                return False, "Current password is incorrect"

        # Validate new password strength
        validation = SecurityUtils.validate_password_strength(new_password)
        if not validation["valid"]:
            return False, "; ".join(validation["errors"])

        # Update password
        user.password_hash = SecurityUtils.get_password_hash(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        user.password_expires_at = SecurityUtils.generate_password_expiry()

        self.db.add(user)
        self.db.commit()

        await self._log_security_event(user.id, "password_changed", {}, ip_address, user_agent, success=True)

        # Revoke all other sessions for security
        await self.revoke_all_user_sessions(user, "password_changed")

        return True, None

    async def _log_security_event(
        self,
        user_id: Optional[UUID],
        event_type: str,
        event_details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None,
    ) -> None:
        """
        Log security event for audit trail.

        Args:
            user_id: User ID associated with event
            event_type: Type of security event
            event_details: Additional event details
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether event was successful
            failure_reason: Reason for failure if applicable
        """
        audit_log = SecurityAuditLog(
            user_id=user_id,
            event_type=event_type,
            event_details=event_details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
        )

        self.db.add(audit_log)
        self.db.commit()
