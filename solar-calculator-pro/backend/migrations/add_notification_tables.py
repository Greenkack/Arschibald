"""
Database Migration: Add Notification Tables

This migration creates the tables for the notification system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_notification_tables'
down_revision = None  # Update this with the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Create notification tables"""
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('action_label', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('channels', sa.String(255), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False, default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('sent_in_app', sa.Boolean(), nullable=False, default=False),
        sa.Column('sent_desktop', sa.Boolean(), nullable=False, default=False),
        sa.Column('sent_email', sa.Boolean(), nullable=False, default=False),
        sa.Column('sent_sms', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for notifications
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_is_archived', 'notifications', ['is_archived'])
    op.create_index('ix_notifications_category', 'notifications', ['category'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    
    # Create notification_actions table
    op.create_table(
        'notification_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('label', sa.String(100), nullable=False),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('is_executed', sa.Boolean(), nullable=False, default=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE')
    )
    
    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enable_in_app', sa.Boolean(), nullable=False, default=True),
        sa.Column('enable_desktop', sa.Boolean(), nullable=False, default=True),
        sa.Column('enable_email', sa.Boolean(), nullable=False, default=True),
        sa.Column('enable_sms', sa.Boolean(), nullable=False, default=False),
        sa.Column('enabled_types', sa.Text(), nullable=True),
        sa.Column('enable_quiet_hours', sa.Boolean(), nullable=False, default=False),
        sa.Column('quiet_hours_start', sa.String(5), nullable=True),
        sa.Column('quiet_hours_end', sa.String(5), nullable=True),
        sa.Column('digest_mode', sa.Boolean(), nullable=False, default=False),
        sa.Column('digest_frequency', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create notification_templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('title_template', sa.String(255), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('default_channels', sa.String(255), nullable=False),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_key')
    )
    
    # Create index for template_key
    op.create_index('ix_notification_templates_template_key', 'notification_templates', ['template_key'])
    
    # Insert default notification templates
    op.execute("""
        INSERT INTO notification_templates (
            template_key, name, description, type, priority,
            title_template, message_template, default_channels,
            icon, category, is_active, created_at, updated_at
        ) VALUES
        (
            'calculation_complete',
            'Calculation Complete',
            'Notification when a solar calculation is completed',
            'calculation_complete',
            'normal',
            'Calculation Complete: {project_name}',
            'Your solar calculation for {project_name} has been completed successfully. System size: {system_size} kWp',
            'in_app,desktop',
            'calculator',
            'calculations',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'pdf_generated',
            'PDF Generated',
            'Notification when a PDF is generated',
            'pdf_generated',
            'normal',
            'PDF Ready: {document_name}',
            'Your PDF document "{document_name}" has been generated and is ready for download.',
            'in_app,desktop,email',
            'file-pdf',
            'documents',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'project_updated',
            'Project Updated',
            'Notification when a project is updated',
            'project_updated',
            'low',
            'Project Updated: {project_name}',
            'The project "{project_name}" has been updated by {updated_by}.',
            'in_app',
            'project',
            'projects',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'system_alert',
            'System Alert',
            'Important system alerts',
            'system_alert',
            'high',
            'System Alert: {alert_title}',
            '{alert_message}',
            'in_app,desktop,email',
            'alert-triangle',
            'system',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
    """)


def downgrade():
    """Drop notification tables"""
    op.drop_table('notification_templates')
    op.drop_table('notification_preferences')
    op.drop_table('notification_actions')
    op.drop_table('notifications')
