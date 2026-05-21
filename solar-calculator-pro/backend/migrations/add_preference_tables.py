# backend/migrations/add_preference_tables.py

"""
Migration: Add user preference tables

This migration creates tables for:
- User preferences (user-specific settings)
- Preference templates (reusable preference sets)
- Preference sync (cross-device synchronization)
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Create preference tables"""
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=200), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'))
    
    # Create indexes for user_preferences
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    op.create_index('ix_user_preferences_category', 'user_preferences', ['category'])
    op.create_index('ix_user_preferences_key', 'user_preferences', ['key'])
    op.create_index('ix_user_preferences_user_category_key', 'user_preferences', 
                    ['user_id', 'category', 'key'], unique=True)
    
    # Create preference_templates table
    op.create_table(
        'preference_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('preferences', sa.Text(), nullable=False),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'))
    
    # Create indexes for preference_templates
    op.create_index('ix_preference_templates_name', 'preference_templates', ['name'], unique=True)
    op.create_index('ix_preference_templates_category', 'preference_templates', ['category'])
    
    # Create preference_syncs table
    op.create_table(
        'preference_syncs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=200), nullable=False),
        sa.Column('device_name', sa.String(length=200)),
        sa.Column('last_sync_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('sync_status', sa.String(length=50), default='success'),
        sa.Column('sync_data', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'))
    
    # Create indexes for preference_syncs
    op.create_index('ix_preference_syncs_user_id', 'preference_syncs', ['user_id'])
    op.create_index('ix_preference_syncs_device_id', 'preference_syncs', ['device_id'])
    op.create_index('ix_preference_syncs_user_device', 'preference_syncs', 
                    ['user_id', 'device_id'])


def downgrade():
    """Drop preference tables"""
    
    # Drop indexes
    op.drop_index('ix_preference_syncs_user_device', 'preference_syncs')
    op.drop_index('ix_preference_syncs_device_id', 'preference_syncs')
    op.drop_index('ix_preference_syncs_user_id', 'preference_syncs')
    
    op.drop_index('ix_preference_templates_category', 'preference_templates')
    op.drop_index('ix_preference_templates_name', 'preference_templates')
    
    op.drop_index('ix_user_preferences_user_category_key', 'user_preferences')
    op.drop_index('ix_user_preferences_key', 'user_preferences')
    op.drop_index('ix_user_preferences_category', 'user_preferences')
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    
    # Drop tables
    op.drop_table('preference_syncs')
    op.drop_table('preference_templates')
    op.drop_table('user_preferences')
