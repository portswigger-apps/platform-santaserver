"""foreign_key_constraints

Revision ID: 002
Revises: 001
Create Date: 2025-08-07 14:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add foreign key constraints for self-referencing fields (resolves circular dependencies)
    op.create_foreign_key('fk_users_created_by', 'users', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_users_updated_by', 'users', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key('fk_auth_providers_created_by', 'auth_providers', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_auth_providers_updated_by', 'auth_providers', 'users', ['updated_by'], ['id'])
    
    op.create_foreign_key('fk_groups_created_by', 'groups', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_groups_updated_by', 'groups', 'users', ['updated_by'], ['id'])
    
    # Add data integrity constraints
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_password_required_local CHECK (
            (user_type = 'local' AND password_hash IS NOT NULL) OR 
            (user_type IN ('sso', 'scim'))
        );
    """)
    
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_external_id_for_external_users CHECK (
            (user_type = 'local' AND external_id IS NULL) OR
            (user_type IN ('sso', 'scim') AND external_id IS NOT NULL)
        );
    """)
    
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_provider_for_external_users CHECK (
            (user_type = 'local' AND provider_name IS NULL) OR
            (user_type IN ('sso', 'scim') AND provider_name IS NOT NULL)
        );
    """)
    
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_password_expiry CHECK (
            (user_type = 'local' AND password_expires_at IS NOT NULL) OR
            (user_type IN ('sso', 'scim'))
        );
    """)
    
    op.execute("""
        ALTER TABLE groups ADD CONSTRAINT chk_external_group_fields CHECK (
            (source_type = 'local' AND external_id IS NULL AND provider_name IS NULL) OR
            (source_type IN ('scim', 'sso') AND external_id IS NOT NULL AND provider_name IS NOT NULL)
        );
    """)


def downgrade() -> None:
    # Drop check constraints
    op.execute("ALTER TABLE groups DROP CONSTRAINT IF EXISTS chk_external_group_fields;")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_password_expiry;")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_provider_for_external_users;")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_external_id_for_external_users;")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_password_required_local;")
    
    # Drop foreign key constraints
    op.drop_constraint('fk_groups_updated_by', 'groups', type_='foreignkey')
    op.drop_constraint('fk_groups_created_by', 'groups', type_='foreignkey')
    op.drop_constraint('fk_auth_providers_updated_by', 'auth_providers', type_='foreignkey')
    op.drop_constraint('fk_auth_providers_created_by', 'auth_providers', type_='foreignkey')
    op.drop_constraint('fk_users_updated_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_created_by', 'users', type_='foreignkey')