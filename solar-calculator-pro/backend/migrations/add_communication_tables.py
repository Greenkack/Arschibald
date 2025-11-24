"""
Add Communication Tables Migration

Creates all tables for the customer communication system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


def upgrade():
    """Create communication tables"""
    
    # Communications table
    op.create_table(
        'communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('to_addresses', sa.JSON(), nullable=True),
        sa.Column('cc_addresses', sa.JSON(), nullable=True),
        sa.Column('bcc_addresses', sa.JSON(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('replied_at', sa.DateTime(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['template_id'], ['communication_templates.id']),
        sa.ForeignKeyConstraint(['campaign_id'], ['communication_campaigns.id'])
    )
    op.create_index('ix_communications_customer_id', 'communications', ['customer_id'])
    op.create_index('ix_communications_user_id', 'communications', ['user_id'])
    op.create_index('ix_communications_type', 'communications', ['type'])
    op.create_index('ix_communications_status', 'communications', ['status'])
    op.create_index('ix_communications_scheduled_at', 'communications', ['scheduled_at'])
    op.create_index('ix_communications_sent_at', 'communications', ['sent_at'])
    op.create_index('ix_communications_campaign_id', 'communications', ['campaign_id'])
    
    # Communication templates table
    op.create_table(
        'communication_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_communication_templates_user_id', 'communication_templates', ['user_id'])
    op.create_index('ix_communication_templates_name', 'communication_templates', ['name'])
    op.create_index('ix_communication_templates_type', 'communication_templates', ['type'])
    op.create_index('ix_communication_templates_is_active', 'communication_templates', ['is_active'])
    op.create_index('ix_communication_templates_category', 'communication_templates', ['category'])
    
    # Communication campaigns table
    op.create_table(
        'communication_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('target_criteria', sa.JSON(), nullable=True),
        sa.Column('recipient_count', sa.Integer(), default=0),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('sent_count', sa.Integer(), default=0),
        sa.Column('delivered_count', sa.Integer(), default=0),
        sa.Column('opened_count', sa.Integer(), default=0),
        sa.Column('clicked_count', sa.Integer(), default=0),
        sa.Column('replied_count', sa.Integer(), default=0),
        sa.Column('bounced_count', sa.Integer(), default=0),
        sa.Column('failed_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['template_id'], ['communication_templates.id'])
    )
    op.create_index('ix_communication_campaigns_user_id', 'communication_campaigns', ['user_id'])
    op.create_index('ix_communication_campaigns_name', 'communication_campaigns', ['name'])
    op.create_index('ix_communication_campaigns_type', 'communication_campaigns', ['type'])
    op.create_index('ix_communication_campaigns_status', 'communication_campaigns', ['status'])
    op.create_index('ix_communication_campaigns_start_date', 'communication_campaigns', ['start_date'])
    op.create_index('ix_communication_campaigns_end_date', 'communication_campaigns', ['end_date'])
    
    # Communication schedules table
    op.create_table(
        'communication_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), default=False),
        sa.Column('recurrence_pattern', sa.String(50), nullable=True),
        sa.Column('recurrence_interval', sa.Integer(), default=1),
        sa.Column('recurrence_days', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('time_of_day', sa.String(10), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('recipient_criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['template_id'], ['communication_templates.id'])
    )
    op.create_index('ix_communication_schedules_user_id', 'communication_schedules', ['user_id'])
    op.create_index('ix_communication_schedules_name', 'communication_schedules', ['name'])
    op.create_index('ix_communication_schedules_type', 'communication_schedules', ['type'])
    op.create_index('ix_communication_schedules_is_active', 'communication_schedules', ['is_active'])
    op.create_index('ix_communication_schedules_start_date', 'communication_schedules', ['start_date'])
    op.create_index('ix_communication_schedules_next_run_at', 'communication_schedules', ['next_run_at'])
    
    # Communication analytics table
    op.create_table(
        'communication_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('communication_id', sa.Integer(), nullable=False),
        sa.Column('open_count', sa.Integer(), default=0),
        sa.Column('click_count', sa.Integer(), default=0),
        sa.Column('reply_count', sa.Integer(), default=0),
        sa.Column('forward_count', sa.Integer(), default=0),
        sa.Column('time_to_open', sa.Integer(), nullable=True),
        sa.Column('time_to_click', sa.Integer(), nullable=True),
        sa.Column('time_to_reply', sa.Integer(), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('operating_system', sa.String(100), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('links_clicked', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['communication_id'], ['communications.id'])
    )
    op.create_index('ix_communication_analytics_communication_id', 'communication_analytics', ['communication_id'], unique=True)
    
    # Email configurations table
    op.create_table(
        'email_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('smtp_host', sa.String(200), nullable=False),
        sa.Column('smtp_port', sa.Integer(), nullable=False),
        sa.Column('smtp_username', sa.String(200), nullable=False),
        sa.Column('smtp_password', sa.String(500), nullable=False),
        sa.Column('use_tls', sa.Boolean(), default=True),
        sa.Column('use_ssl', sa.Boolean(), default=False),
        sa.Column('from_email', sa.String(200), nullable=False),
        sa.Column('from_name', sa.String(200), nullable=True),
        sa.Column('reply_to_email', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('daily_limit', sa.Integer(), nullable=True),
        sa.Column('hourly_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_email_configurations_user_id', 'email_configurations', ['user_id'])
    op.create_index('ix_email_configurations_is_active', 'email_configurations', ['is_active'])
    
    # SMS configurations table
    op.create_table(
        'sms_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('api_key', sa.String(500), nullable=False),
        sa.Column('api_secret', sa.String(500), nullable=True),
        sa.Column('account_sid', sa.String(200), nullable=True),
        sa.Column('from_number', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('daily_limit', sa.Integer(), nullable=True),
        sa.Column('hourly_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_sms_configurations_user_id', 'sms_configurations', ['user_id'])
    op.create_index('ix_sms_configurations_is_active', 'sms_configurations', ['is_active'])


def downgrade():
    """Drop communication tables"""
    op.drop_table('sms_configurations')
    op.drop_table('email_configurations')
    op.drop_table('communication_analytics')
    op.drop_table('communication_schedules')
    op.drop_table('communication_campaigns')
    op.drop_table('communication_templates')
    op.drop_table('communications')
