# Database Migration: Add System Configuration Tables

"""
Migration script to add system configuration management tables.

This migration creates:
- system_configurations: Global system settings
- module_configurations: Module-specific settings
- configuration_versions: Version history for configurations
- configuration_templates: Predefined configuration templates
- configuration_validations: Validation rules for configurations
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


def upgrade():
    """Create system configuration tables"""
    
    # Create system_configurations table
    op.create_table(
        'system_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), default=False),
        sa.Column('is_readonly', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    op.create_index('ix_system_configurations_key', 'system_configurations', ['key'], unique=True)
    op.create_index('ix_system_configurations_category', 'system_configurations', ['category'])
    
    # Create module_configurations table
    op.create_table(
        'module_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_module_configurations_module_name', 'module_configurations', ['module_name'])
    op.create_index('ix_module_configurations_key', 'module_configurations', ['key'])
    
    # Create configuration_versions table
    op.create_table(
        'configuration_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('configuration_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['configuration_id'], ['system_configurations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'])
    )
    op.create_index('ix_configuration_versions_configuration_id', 'configuration_versions', ['configuration_id'])
    
    # Create configuration_templates table
    op.create_table(
        'configuration_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    op.create_index('ix_configuration_templates_name', 'configuration_templates', ['name'], unique=True)
    
    # Create configuration_validations table
    op.create_table(
        'configuration_validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(length=255), nullable=False),
        sa.Column('validation_type', sa.String(length=50), nullable=False),
        sa.Column('validation_rule', sa.Text(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_configuration_validations_config_key', 'configuration_validations', ['config_key'])
    
    # Insert default system configurations
    op.execute("""
        INSERT INTO system_configurations (key, value, value_type, category, description, is_readonly, created_at, updated_at)
        VALUES 
        ('app.name', 'Solar Calculator Pro', 'string', 'general', 'Application name', 1, datetime('now'), datetime('now')),
        ('app.version', '1.0.0', 'string', 'general', 'Application version', 1, datetime('now'), datetime('now')),
        ('app.language', 'de-DE', 'string', 'general', 'Default application language', 0, datetime('now'), datetime('now')),
        ('app.timezone', 'Europe/Berlin', 'string', 'general', 'Default timezone', 0, datetime('now'), datetime('now')),
        ('security.session_timeout', '3600', 'number', 'security', 'Session timeout in seconds', 0, datetime('now'), datetime('now')),
        ('security.max_login_attempts', '5', 'number', 'security', 'Maximum login attempts before lockout', 0, datetime('now'), datetime('now')),
        ('database.backup_enabled', 'true', 'boolean', 'database', 'Enable automatic database backups', 0, datetime('now'), datetime('now')),
        ('database.backup_interval', '86400', 'number', 'database', 'Backup interval in seconds (default: 24 hours)', 0, datetime('now'), datetime('now')),
        ('email.smtp_enabled', 'false', 'boolean', 'email', 'Enable SMTP email sending', 0, datetime('now'), datetime('now')),
        ('logging.level', 'INFO', 'string', 'logging', 'Logging level (DEBUG, INFO, WARNING, ERROR)', 0, datetime('now'), datetime('now')),
        ('performance.cache_enabled', 'true', 'boolean', 'performance', 'Enable application caching', 0, datetime('now'), datetime('now')),
        ('ui.theme', 'light', 'string', 'ui', 'Default UI theme', 0, datetime('now'), datetime('now'))
    """)
    
    # Insert default module configurations
    op.execute("""
        INSERT INTO module_configurations (module_name, key, value, value_type, description, is_enabled, created_at, updated_at)
        VALUES 
        ('solar', 'default_module_efficiency', '0.20', 'number', 'Default solar module efficiency', 1, datetime('now'), datetime('now')),
        ('solar', 'default_system_loss', '0.14', 'number', 'Default system loss factor', 1, datetime('now'), datetime('now')),
        ('heatpump', 'default_cop', '4.0', 'number', 'Default coefficient of performance', 1, datetime('now'), datetime('now')),
        ('pdf', 'default_template', 'standard', 'string', 'Default PDF template', 1, datetime('now'), datetime('now')),
        ('pdf', 'compression_enabled', 'true', 'boolean', 'Enable PDF compression', 1, datetime('now'), datetime('now')),
        ('crm', 'lead_scoring_enabled', 'true', 'boolean', 'Enable lead scoring', 1, datetime('now'), datetime('now')),
        ('pricing', 'currency', 'EUR', 'string', 'Default currency', 1, datetime('now'), datetime('now')),
        ('pricing', 'tax_rate', '0.19', 'number', 'Default tax rate (VAT)', 1, datetime('now'), datetime('now'))
    """)
    
    # Insert default templates
    op.execute("""
        INSERT INTO configuration_templates (name, description, template_data, is_system, is_active, created_at, updated_at)
        VALUES 
        ('Default Configuration', 'Default system configuration', '{"system_configs": [], "module_configs": []}', 1, 1, datetime('now'), datetime('now')),
        ('Development Configuration', 'Configuration for development environment', '{"system_configs": [{"key": "logging.level", "value": "DEBUG", "value_type": "string", "category": "logging"}], "module_configs": []}', 1, 1, datetime('now'), datetime('now')),
        ('Production Configuration', 'Configuration for production environment', '{"system_configs": [{"key": "logging.level", "value": "WARNING", "value_type": "string", "category": "logging"}, {"key": "performance.cache_enabled", "value": "true", "value_type": "boolean", "category": "performance"}], "module_configs": []}', 1, 1, datetime('now'), datetime('now'))
    """)


def downgrade():
    """Drop system configuration tables"""
    op.drop_table('configuration_validations')
    op.drop_table('configuration_templates')
    op.drop_table('configuration_versions')
    op.drop_table('module_configurations')
    op.drop_table('system_configurations')
