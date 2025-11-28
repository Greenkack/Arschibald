"""
Database migration for API Integration tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_api_integration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create API integration tables"""
    
    # Create api_integrations table
    op.create_table(
        'api_integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('integration_type', sa.Enum('REST', 'GRAPHQL', 'SOAP', 'WEBHOOK', name='integrationtype'), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=False),
        sa.Column('auth_type', sa.Enum('NONE', 'API_KEY', 'BASIC', 'BEARER', 'OAUTH2', name='authtype'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('timeout', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('retry_delay', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('api_key', sa.String(length=500), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('password', sa.String(length=500), nullable=True),
        sa.Column('bearer_token', sa.Text(), nullable=True),
        sa.Column('oauth_config', sa.JSON(), nullable=True),
        sa.Column('oauth_access_token', sa.Text(), nullable=True),
        sa.Column('oauth_refresh_token', sa.Text(), nullable=True),
        sa.Column('oauth_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('webhook_config', sa.JSON(), nullable=True),
        sa.Column('rate_limit_config', sa.JSON(), nullable=True),
        sa.Column('cache_config', sa.JSON(), nullable=True),
        sa.Column('custom_headers', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_integrations_id', 'api_integrations', ['id'])
    op.create_index('ix_api_integrations_name', 'api_integrations', ['name'])
    
    # Create webhook_deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'DELIVERED', 'FAILED', 'RETRYING', name='webhookdeliverystatus'), nullable=False, server_default='PENDING'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_webhook_deliveries_id', 'webhook_deliveries', ['id'])
    op.create_index('ix_webhook_deliveries_integration_id', 'webhook_deliveries', ['integration_id'])
    op.create_index('ix_webhook_deliveries_event', 'webhook_deliveries', ['event'])
    
    # Create api_call_logs table
    op.create_table(
        'api_call_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('endpoint', sa.String(length=500), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('request_params', sa.JSON(), nullable=True),
        sa.Column('response_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_call_logs_id', 'api_call_logs', ['id'])
    op.create_index('ix_api_call_logs_integration_id', 'api_call_logs', ['integration_id'])
    op.create_index('ix_api_call_logs_created_at', 'api_call_logs', ['created_at'])


def downgrade():
    """Drop API integration tables"""
    op.drop_index('ix_api_call_logs_created_at', table_name='api_call_logs')
    op.drop_index('ix_api_call_logs_integration_id', table_name='api_call_logs')
    op.drop_index('ix_api_call_logs_id', table_name='api_call_logs')
    op.drop_table('api_call_logs')
    
    op.drop_index('ix_webhook_deliveries_event', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_integration_id', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_id', table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    
    op.drop_index('ix_api_integrations_name', table_name='api_integrations')
    op.drop_index('ix_api_integrations_id', table_name='api_integrations')
    op.drop_table('api_integrations')
    
    # Drop enums
    sa.Enum(name='webhookdeliverystatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='authtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='integrationtype').drop(op.get_bind(), checkfirst=True)
