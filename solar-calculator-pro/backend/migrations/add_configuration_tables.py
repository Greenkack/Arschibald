"""
Database Migration: Add Configuration Tables

This migration creates all tables for the dynamic configuration system:
- configurations: Main configuration storage
- configuration_versions: Version history
- configuration_audit_logs: Audit trail
- configuration_backups: Backup snapshots
- configuration_validation_rules: Validation rules
- configuration_templates: Configuration templates

Run this migration to set up the configuration database schema.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, mysql, sqlite
from datetime import datetime


def upgrade():
    """Create configuration tables"""
    
    # 1. Create configurations table
    op.create_table(
        'configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=False, server_default='string'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('namespace', sa.String(length=100), nullable=False, server_default='global'),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('validation_schema', sa.JSON(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['configurations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configurations
    op.create_index('idx_config_key', 'configurations', ['key'])
    op.create_index('idx_config_category', 'configurations', ['category'])
    op.create_index('idx_config_namespace', 'configurations', ['namespace'])
    op.create_index('idx_config_parent_id', 'configurations', ['parent_id'])
    op.create_index('idx_config_is_active', 'configurations', ['is_active'])
    op.create_index('idx_config_key_namespace', 'configurations', ['key', 'namespace'])
    op.create_index('idx_config_category_active', 'configurations', ['category', 'is_active'])
    op.create_index('idx_config_namespace_active', 'configurations', ['namespace', 'is_active'])
    
    # 2. Create configuration_versions table
    op.create_table(
        'configuration_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('configuration_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('change_description', sa.Text(), nullable=True),
        sa.Column('previous_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['configuration_id'], ['configurations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configuration_versions
    op.create_index('idx_version_config_id', 'configuration_versions', ['configuration_id'])
    op.create_index('idx_version_config_version', 'configuration_versions', ['configuration_id', 'version_number'])
    op.create_index('idx_version_created_at', 'configuration_versions', ['created_at'])
    
    # 3. Create configuration_audit_logs table
    op.create_table(
        'configuration_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('configuration_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('action_details', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['configuration_id'], ['configurations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configuration_audit_logs
    op.create_index('idx_audit_config_id', 'configuration_audit_logs', ['configuration_id'])
    op.create_index('idx_audit_action', 'configuration_audit_logs', ['action'])
    op.create_index('idx_audit_user_id', 'configuration_audit_logs', ['user_id'])
    op.create_index('idx_audit_timestamp', 'configuration_audit_logs', ['timestamp'])
    op.create_index('idx_audit_action_timestamp', 'configuration_audit_logs', ['action', 'timestamp'])
    op.create_index('idx_audit_user_timestamp', 'configuration_audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_config_timestamp', 'configuration_audit_logs', ['configuration_id', 'timestamp'])
    
    # 4. Create configuration_backups table
    op.create_table(
        'configuration_backups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('backup_name', sa.String(length=255), nullable=False),
        sa.Column('backup_type', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('configuration_data', sa.JSON(), nullable=False),
        sa.Column('configuration_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_compressed', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('compression_algorithm', sa.String(length=50), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('restored_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('restored_by', sa.String(length=100), nullable=True),
        sa.Column('restore_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configuration_backups
    op.create_index('idx_backup_created_at', 'configuration_backups', ['created_at'])
    op.create_index('idx_backup_type_created', 'configuration_backups', ['backup_type', 'created_at'])
    op.create_index('idx_backup_status', 'configuration_backups', ['status'])
    op.create_index('idx_backup_expires', 'configuration_backups', ['expires_at'])
    
    # 5. Create configuration_validation_rules table
    op.create_table(
        'configuration_validation_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_definition', sa.JSON(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('applies_to_namespace', sa.String(length=100), nullable=True),
        sa.Column('applies_to_category', sa.String(length=100), nullable=True),
        sa.Column('applies_to_key_pattern', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='error'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configuration_validation_rules
    op.create_index('idx_validation_rule_name', 'configuration_validation_rules', ['rule_name'])
    op.create_index('idx_validation_namespace', 'configuration_validation_rules', ['applies_to_namespace'])
    op.create_index('idx_validation_active', 'configuration_validation_rules', ['is_active'])
    
    # 6. Create configuration_templates table
    op.create_table(
        'configuration_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('template_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('configuration_data', sa.JSON(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for configuration_templates
    op.create_index('idx_template_name', 'configuration_templates', ['template_name'])
    op.create_index('idx_template_type_active', 'configuration_templates', ['template_type', 'is_active'])
    op.create_index('idx_template_category', 'configuration_templates', ['category'])
    
    print("✅ Configuration tables created successfully!")


def downgrade():
    """Drop configuration tables"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('configuration_templates')
    op.drop_table('configuration_validation_rules')
    op.drop_table('configuration_backups')
    op.drop_table('configuration_audit_logs')
    op.drop_table('configuration_versions')
    op.drop_table('configurations')
    
    print("✅ Configuration tables dropped successfully!")


if __name__ == "__main__":
    """
    Run migration directly for testing
    """
    print("Configuration Database Migration")
    print("=" * 50)
    print("\nThis migration will create the following tables:")
    print("  1. configurations")
    print("  2. configuration_versions")
    print("  3. configuration_audit_logs")
    print("  4. configuration_backups")
    print("  5. configuration_validation_rules")
    print("  6. configuration_templates")
    print("\nRun with Alembic:")
    print("  alembic upgrade head")
    print("\nOr import and call upgrade() function directly")
