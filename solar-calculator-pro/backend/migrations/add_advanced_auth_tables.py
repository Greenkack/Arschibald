"""
Database migration for advanced authentication tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Create advanced authentication tables"""
    
    # User Two-Factor table
    op.create_table(
        'user_two_factor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('method', sa.Enum('totp', 'sms', 'email', 'backup_codes', name='twofactormethod'), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=False),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('totp_secret', sa.String(255), nullable=True),
        sa.Column('phone_number', sa.String(50), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('backup_codes', sa.Text(), nullable=True),
        sa.Column('backup_codes_used', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_two_factor_id', 'user_two_factor', ['id'])
    op.create_index('ix_user_two_factor_user_id', 'user_two_factor', ['user_id'])
    
    # User SSO table
    op.create_table(
        'user_sso',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('google', 'microsoft', 'github', 'okta', 'custom_saml', 'custom_oidc', name='ssoprovider'), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('provider_name', sa.String(255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('saml_name_id', sa.String(255), nullable=True),
        sa.Column('oidc_sub', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sso_id', 'user_sso', ['id'])
    op.create_index('ix_user_sso_user_id', 'user_sso', ['user_id'])
    
    # User Biometric table
    op.create_table(
        'user_biometric',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('biometric_type', sa.Enum('fingerprint', 'face_id', 'windows_hello', 'touch_id', name='biometrictype'), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('device_platform', sa.String(50), nullable=True),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('credential_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_biometric_id', 'user_biometric', ['id'])
    op.create_index('ix_user_biometric_user_id', 'user_biometric', ['user_id'])
    op.create_index('ix_user_biometric_device_id', 'user_biometric', ['device_id'])
    
    # User Sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(255), nullable=False),
        sa.Column('refresh_token', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('platform', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('auth_method', sa.Enum('password', 'two_factor', 'sso', 'biometric', name='authmethodtype'), nullable=False),
        sa.Column('two_factor_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_reason', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
        sa.UniqueConstraint('refresh_token')
    )
    op.create_index('ix_user_sessions_id', 'user_sessions', ['id'])
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_session_token', 'user_sessions', ['session_token'])
    
    # Login Attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('auth_method', sa.Enum('password', 'two_factor', 'sso', 'biometric', name='authmethodtype'), nullable=False),
        sa.Column('failure_reason', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('platform', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('attempted_at', sa.DateTime(), nullable=False),
        sa.Column('is_suspicious', sa.Boolean(), default=False),
        sa.Column('is_blocked', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_login_attempts_id', 'login_attempts', ['id'])
    op.create_index('ix_login_attempts_username', 'login_attempts', ['username'])
    op.create_index('ix_login_attempts_ip_address', 'login_attempts', ['ip_address'])
    op.create_index('ix_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])
    
    # Password Policy table
    op.create_table(
        'password_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('min_length', sa.Integer(), default=8),
        sa.Column('max_length', sa.Integer(), default=128),
        sa.Column('require_uppercase', sa.Boolean(), default=True),
        sa.Column('require_lowercase', sa.Boolean(), default=True),
        sa.Column('require_numbers', sa.Boolean(), default=True),
        sa.Column('require_special_chars', sa.Boolean(), default=True),
        sa.Column('special_chars_allowed', sa.String(100), default='!@#$%^&*()_+-=[]{}|;:,.<>?'),
        sa.Column('prevent_reuse_count', sa.Integer(), default=5),
        sa.Column('expires_after_days', sa.Integer(), default=90),
        sa.Column('warn_before_expiry_days', sa.Integer(), default=7),
        sa.Column('max_failed_attempts', sa.Integer(), default=5),
        sa.Column('lockout_duration_minutes', sa.Integer(), default=30),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_password_policies_id', 'password_policies', ['id'])
    
    # Password History table
    op.create_table(
        'password_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_history_id', 'password_history', ['id'])
    op.create_index('ix_password_history_user_id', 'password_history', ['user_id'])
    
    # Account Lockout table
    op.create_table(
        'account_lockouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('locked_at', sa.DateTime(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('failed_attempts_count', sa.Integer(), default=0),
        sa.Column('unlocked_at', sa.DateTime(), nullable=True),
        sa.Column('unlocked_by', sa.Integer(), nullable=True),
        sa.Column('unlock_reason', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['unlocked_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_account_lockouts_id', 'account_lockouts', ['id'])
    op.create_index('ix_account_lockouts_user_id', 'account_lockouts', ['user_id'])
    
    # Insert default password policy
    op.execute("""
        INSERT INTO password_policies (
            name, is_active, min_length, max_length,
            require_uppercase, require_lowercase, require_numbers, require_special_chars,
            special_chars_allowed, prevent_reuse_count, expires_after_days, warn_before_expiry_days,
            max_failed_attempts, lockout_duration_minutes, created_at, updated_at
        ) VALUES (
            'Default Policy', true, 8, 128,
            true, true, true, true,
            '!@#$%^&*()_+-=[]{}|;:,.<>?', 5, 90, 7,
            5, 30, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """)


def downgrade():
    """Drop advanced authentication tables"""
    op.drop_table('account_lockouts')
    op.drop_table('password_history')
    op.drop_table('password_policies')
    op.drop_table('login_attempts')
    op.drop_table('user_sessions')
    op.drop_table('user_biometric')
    op.drop_table('user_sso')
    op.drop_table('user_two_factor')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS twofactormethod')
    op.execute('DROP TYPE IF EXISTS ssoprovider')
    op.execute('DROP TYPE IF EXISTS biometrictype')
    op.execute('DROP TYPE IF EXISTS authmethodtype')
