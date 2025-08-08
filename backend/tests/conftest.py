"""Test configuration and fixtures."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from testcontainers.postgres import PostgresContainer

from app.core.config import Settings
from app.core.database import get_db
from app.core.security import SecurityUtils
from app.main import app
from app.models.auth import Role, User, UserRole


@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL testcontainer for the test session (requires Docker)."""
    try:
        with PostgresContainer("postgres:17") as postgres:
            yield postgres
    except Exception:
        # Fallback to None if Docker not available
        yield None


@pytest.fixture(scope="session")
def test_settings(postgres_container):
    """Create test settings with testcontainer database URL or SQLite fallback."""
    if postgres_container:
        # Use testcontainer if available
        os.environ["POSTGRES_SERVER"] = postgres_container.get_container_host_ip()
        os.environ["POSTGRES_PORT"] = str(postgres_container.get_exposed_port(5432))
        os.environ["POSTGRES_USER"] = postgres_container.username
        os.environ["POSTGRES_PASSWORD"] = postgres_container.password
        os.environ["POSTGRES_DB"] = postgres_container.dbname

    # Set common test environment variables
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-jwt-tokens"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["TENANT_ID"] = "test-tenant-id"
    os.environ["CLIENT_ID"] = "test-client-id"
    os.environ["CLIENT_SECRET"] = "test-client-secret"

    # Create settings instance
    return Settings()


@pytest.fixture(scope="session")
def test_engine(test_settings, postgres_container):
    """Create test database engine using testcontainer or SQLite fallback."""
    if postgres_container:
        # Use PostgreSQL testcontainer
        url = str(test_settings.SQLALCHEMY_DATABASE_URI).replace("+asyncpg", "")
        engine = create_engine(url, echo=False)
    else:
        # Fallback to SQLite with threading support for testing without Docker
        engine = create_engine("sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="session")
def create_test_tables(test_engine):
    """Create all database tables for testing."""
    from app.models.auth import SQLModel

    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def test_db(test_engine, create_test_tables):
    """Create test database session with transaction rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()

    # Create session bound to the connection
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_admin_user(test_db):
    """Create a test admin user."""
    # Create admin role
    admin_role = Role(
        name="admin",
        display_name="Administrator",
        description="System administrator with full access",
        permissions={
            "users": ["create", "read", "update", "delete"],
            "groups": ["create", "read", "update", "delete"],
            "roles": ["create", "read", "update", "delete"],
            "system": ["manage", "configure"],
        },
    )
    test_db.add(admin_role)
    test_db.commit()
    test_db.refresh(admin_role)

    # Create admin user
    from datetime import datetime, timezone
    from uuid import uuid4

    admin_user = User(
        id=uuid4(),
        username="admin",
        email="admin@example.com",
        user_type="local",
        first_name="Admin",
        last_name="User",
        display_name="Admin User",
        is_active=True,
        is_provisioned=True,
        password_hash=SecurityUtils.get_password_hash("AdminPass123!"),
        password_changed_at=datetime.now(timezone.utc),
        password_expires_at=SecurityUtils.generate_password_expiry(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by=uuid4(),  # Self-created
        updated_by=uuid4(),
    )
    admin_user.created_by = admin_user.id
    admin_user.updated_by = admin_user.id

    test_db.add(admin_user)
    test_db.commit()
    test_db.refresh(admin_user)

    # Assign admin role to user
    user_role = UserRole(
        user_id=admin_user.id, role_id=admin_role.id, granted_by=admin_user.id, granted_at=datetime.now(timezone.utc)
    )
    test_db.add(user_role)
    test_db.commit()

    return admin_user


@pytest.fixture
def client(test_db, test_admin_user):
    """Create test client with database dependency override."""

    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(test_db, test_admin_user):
    """Create authorization headers for admin user."""
    # Create a JWT token for the admin user
    from app.core.security import JWTManager

    token_data = {"sub": str(test_admin_user.id), "username": test_admin_user.username, "type": "access"}

    access_token = JWTManager.create_access_token(token_data)

    return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
