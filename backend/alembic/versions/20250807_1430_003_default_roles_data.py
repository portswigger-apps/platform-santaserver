"""default_roles_data

Revision ID: 003
Revises: 002
Create Date: 2025-08-07 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert default roles with permissions
    admin_permissions = {
        "users": ["create", "read", "update", "delete"],
        "groups": ["create", "read", "update", "delete"],
        "roles": ["create", "read", "update", "delete"],
        "santa": ["create", "read", "update", "delete", "approve"],
        "system": ["configure", "monitor", "audit"]
    }
    
    user_permissions = {
        "santa": ["read", "create", "update"],
        "approvals": ["request", "vote"],
        "profile": ["read", "update"]
    }
    
    op.execute(f"""
        INSERT INTO roles (id, name, display_name, description, permissions, is_system_role, created_at, updated_at) VALUES
        (gen_random_uuid(), 'admin', 'Administrator', 'Full system access', '{json.dumps(admin_permissions)}', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        (gen_random_uuid(), 'user', 'User', 'Standard user access', '{json.dumps(user_permissions)}', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)


def downgrade() -> None:
    # Remove default roles
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'user') AND is_system_role = true")