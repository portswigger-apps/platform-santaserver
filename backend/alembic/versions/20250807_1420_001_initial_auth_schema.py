"""initial_auth_schema

Revision ID: 001
Revises: 
Create Date: 2025-08-07 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create custom enum types
    user_type_enum = postgresql.ENUM('local', 'sso', 'scim', name='user_type', create_type=False)
    user_type_enum.create(op.get_bind())
    
    provider_type_enum = postgresql.ENUM('saml2', 'oidc', 'scim_v2', name='provider_type', create_type=False)
    provider_type_enum.create(op.get_bind())

    # Create auth_providers table
    op.create_table('auth_providers',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('provider_type', provider_type_enum, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scim_base_url', sa.String(length=500), nullable=True),
        sa.Column('scim_bearer_token_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('user_type', user_type_enum, nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('password_expires_at', sa.DateTime(), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('provider_name', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_provisioned', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create roles table
    op.create_table('roles',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_system_role', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create groups table
    op.create_table('groups',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('provider_name', sa.String(length=100), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create user_roles table
    op.create_table('user_roles',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('role_id', postgresql.UUID(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create user_groups table
    op.create_table('user_groups',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('group_id', postgresql.UUID(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('added_by', postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )

    # Create group_roles table
    op.create_table('group_roles',
        sa.Column('group_id', postgresql.UUID(), nullable=False),
        sa.Column('role_id', postgresql.UUID(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('group_id', 'role_id')
    )

    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('token_jti', sa.String(length=255), nullable=False),
        sa.Column('refresh_token_jti', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_expires_at', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_reason', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti')
    )

    # Create security_audit_log table
    op.create_table('security_audit_log',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create performance indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_active', 'users', ['is_active'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_users_user_type', 'users', ['user_type'])
    op.create_index('idx_users_external_id', 'users', ['external_id'], postgresql_where=sa.text('external_id IS NOT NULL'))
    op.create_index('idx_users_provider_name', 'users', ['provider_name'], postgresql_where=sa.text('provider_name IS NOT NULL'))
    op.create_index('idx_users_locked_until', 'users', ['locked_until'], postgresql_where=sa.text('locked_until IS NOT NULL'))
    op.create_index('idx_users_password_expires', 'users', ['password_expires_at'], postgresql_where=sa.text('password_expires_at IS NOT NULL'))

    op.create_index('idx_groups_source_type', 'groups', ['source_type'])
    op.create_index('idx_groups_external_id', 'groups', ['external_id'], postgresql_where=sa.text('external_id IS NOT NULL'))
    op.create_index('idx_groups_provider_name', 'groups', ['provider_name'], postgresql_where=sa.text('provider_name IS NOT NULL'))

    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_token_jti', 'user_sessions', ['token_jti'])
    op.create_index('idx_user_sessions_refresh_token_jti', 'user_sessions', ['refresh_token_jti'], postgresql_where=sa.text('refresh_token_jti IS NOT NULL'))
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('idx_user_sessions_is_revoked', 'user_sessions', ['is_revoked'], postgresql_where=sa.text('is_revoked = false'))

    op.create_index('idx_security_audit_user_id', 'security_audit_log', ['user_id'])
    op.create_index('idx_security_audit_event_type', 'security_audit_log', ['event_type'])
    op.create_index('idx_security_audit_timestamp', 'security_audit_log', ['timestamp'])
    op.create_index('idx_security_audit_success', 'security_audit_log', ['success'])
    op.create_index('idx_security_audit_ip_address', 'security_audit_log', ['ip_address'])

    op.create_index('idx_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('idx_user_groups_user_id', 'user_groups', ['user_id'])
    op.create_index('idx_group_roles_group_id', 'group_roles', ['group_id'])

    op.create_index('idx_auth_providers_name', 'auth_providers', ['name'])
    op.create_index('idx_auth_providers_enabled', 'auth_providers', ['is_enabled'], postgresql_where=sa.text('is_enabled = true'))

    # Insert system user for initial setup
    op.execute("""
        INSERT INTO users (id, username, email, user_type, is_active, failed_login_attempts, is_provisioned, created_at, updated_at) 
        VALUES ('00000000-0000-0000-0000-000000000000', 'system', 'system@localhost', 'local', false, 0, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_auth_providers_enabled', table_name='auth_providers')
    op.drop_index('idx_auth_providers_name', table_name='auth_providers')
    op.drop_index('idx_group_roles_group_id', table_name='group_roles')
    op.drop_index('idx_user_groups_user_id', table_name='user_groups')
    op.drop_index('idx_user_roles_user_id', table_name='user_roles')
    op.drop_index('idx_security_audit_ip_address', table_name='security_audit_log')
    op.drop_index('idx_security_audit_success', table_name='security_audit_log')
    op.drop_index('idx_security_audit_timestamp', table_name='security_audit_log')
    op.drop_index('idx_security_audit_event_type', table_name='security_audit_log')
    op.drop_index('idx_security_audit_user_id', table_name='security_audit_log')
    op.drop_index('idx_user_sessions_is_revoked', table_name='user_sessions')
    op.drop_index('idx_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('idx_user_sessions_refresh_token_jti', table_name='user_sessions')
    op.drop_index('idx_user_sessions_token_jti', table_name='user_sessions')
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_index('idx_groups_provider_name', table_name='groups')
    op.drop_index('idx_groups_external_id', table_name='groups')
    op.drop_index('idx_groups_source_type', table_name='groups')
    op.drop_index('idx_users_password_expires', table_name='users')
    op.drop_index('idx_users_locked_until', table_name='users')
    op.drop_index('idx_users_provider_name', table_name='users')
    op.drop_index('idx_users_external_id', table_name='users')
    op.drop_index('idx_users_user_type', table_name='users')
    op.drop_index('idx_users_active', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
    # Drop tables in reverse order
    op.drop_table('security_audit_log')
    op.drop_table('user_sessions')
    op.drop_table('group_roles')
    op.drop_table('user_groups')
    op.drop_table('user_roles')
    op.drop_table('groups')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('auth_providers')
    
    # Drop enums
    op.execute("DROP TYPE provider_type")
    op.execute("DROP TYPE user_type")