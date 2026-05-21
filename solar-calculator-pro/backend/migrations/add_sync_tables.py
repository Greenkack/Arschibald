"""
Database Migration: Add Synchronization Tables
Creates tables for data synchronization system
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_sync_tables'
down_revision = None  # Update with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Create synchronization tables"""
    
    # Create sync_operations table
    op.create_table(
        'sync_operations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', 'conflict', name='syncstatus'), nullable=False),
        sa.Column('conflict_resolution', sa.Enum('server_wins', 'client_wins', 'manual', 'merge', 'latest_wins', name='conflictresolution'), nullable=True),
        sa.Column('data_snapshot', sa.JSON(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('conflict_data', sa.JSON(), nullable=True),
        sa.Column('client_timestamp', sa.DateTime(), nullable=False),
        sa.Column('server_timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('parent_version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for sync_operations
    op.create_index('ix_sync_operations_user_id', 'sync_operations', ['user_id'])
    op.create_index('ix_sync_operations_device_id', 'sync_operations', ['device_id'])
    op.create_index('ix_sync_operations_entity_type', 'sync_operations', ['entity_type'])
    op.create_index('ix_sync_operations_entity_id', 'sync_operations', ['entity_id'])
    op.create_index('ix_sync_operations_status', 'sync_operations', ['status'])
    
    # Create sync_schedules table
    op.create_table(
        'sync_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('sync_interval', sa.Integer(), default=300),
        sa.Column('auto_sync', sa.Boolean(), default=True),
        sa.Column('sync_on_startup', sa.Boolean(), default=True),
        sa.Column('sync_on_shutdown', sa.Boolean(), default=True),
        sa.Column('entity_types', sa.JSON(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('last_sync_status', sa.Enum('pending', 'in_progress', 'completed', 'failed', 'conflict', name='syncstatus'), nullable=True),
        sa.Column('next_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for sync_schedules
    op.create_index('ix_sync_schedules_user_id', 'sync_schedules', ['user_id'])
    op.create_index('ix_sync_schedules_device_id', 'sync_schedules', ['device_id'])
    
    # Create sync_conflicts table
    op.create_table(
        'sync_conflicts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_operation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('conflict_type', sa.String(50), nullable=False),
        sa.Column('server_data', sa.JSON(), nullable=False),
        sa.Column('client_data', sa.JSON(), nullable=False),
        sa.Column('server_version', sa.Integer(), nullable=False),
        sa.Column('client_version', sa.Integer(), nullable=False),
        sa.Column('server_timestamp', sa.DateTime(), nullable=False),
        sa.Column('client_timestamp', sa.DateTime(), nullable=False),
        sa.Column('resolution_strategy', sa.Enum('server_wins', 'client_wins', 'manual', 'merge', 'latest_wins', name='conflictresolution'), nullable=True),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for sync_conflicts
    op.create_index('ix_sync_conflicts_sync_operation_id', 'sync_conflicts', ['sync_operation_id'])
    op.create_index('ix_sync_conflicts_user_id', 'sync_conflicts', ['user_id'])
    
    # Create sync_logs table
    op.create_table(
        'sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('sync_session_id', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('operations_total', sa.Integer(), default=0),
        sa.Column('operations_completed', sa.Integer(), default=0),
        sa.Column('operations_failed', sa.Integer(), default=0),
        sa.Column('conflicts_detected', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for sync_logs
    op.create_index('ix_sync_logs_user_id', 'sync_logs', ['user_id'])
    op.create_index('ix_sync_logs_device_id', 'sync_logs', ['device_id'])
    op.create_index('ix_sync_logs_sync_session_id', 'sync_logs', ['sync_session_id'])
    
    # Create offline_sync_queue table
    op.create_table(
        'offline_sync_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('queued_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for offline_sync_queue
    op.create_index('ix_offline_sync_queue_user_id', 'offline_sync_queue', ['user_id'])
    op.create_index('ix_offline_sync_queue_device_id', 'offline_sync_queue', ['device_id'])


def downgrade():
    """Drop synchronization tables"""
    
    # Drop indexes
    op.drop_index('ix_offline_sync_queue_device_id', 'offline_sync_queue')
    op.drop_index('ix_offline_sync_queue_user_id', 'offline_sync_queue')
    op.drop_index('ix_sync_logs_sync_session_id', 'sync_logs')
    op.drop_index('ix_sync_logs_device_id', 'sync_logs')
    op.drop_index('ix_sync_logs_user_id', 'sync_logs')
    op.drop_index('ix_sync_conflicts_user_id', 'sync_conflicts')
    op.drop_index('ix_sync_conflicts_sync_operation_id', 'sync_conflicts')
    op.drop_index('ix_sync_schedules_device_id', 'sync_schedules')
    op.drop_index('ix_sync_schedules_user_id', 'sync_schedules')
    op.drop_index('ix_sync_operations_status', 'sync_operations')
    op.drop_index('ix_sync_operations_entity_id', 'sync_operations')
    op.drop_index('ix_sync_operations_entity_type', 'sync_operations')
    op.drop_index('ix_sync_operations_device_id', 'sync_operations')
    op.drop_index('ix_sync_operations_user_id', 'sync_operations')
    
    # Drop tables
    op.drop_table('offline_sync_queue')
    op.drop_table('sync_logs')
    op.drop_table('sync_conflicts')
    op.drop_table('sync_schedules')
    op.drop_table('sync_operations')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS conflictresolution')
    op.execute('DROP TYPE IF EXISTS syncstatus')
