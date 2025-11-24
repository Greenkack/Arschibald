"""
Database Migration: Add Audit System Tables

This migration adds all tables required for the audit system:
- audit_logs: Track all database changes
- data_access_logs: Track data access (read operations)
- user_action_logs: Track user actions and activities
- compliance_logs: Track compliance events
- audit_reports: Store generated audit reports
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


def upgrade():
    """Create audit system tables"""
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=False),
        sa.Column('record_id', sa.String(length=255), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('request_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit_logs
    op.create_index('idx_audit_timestamp_action', 'audit_logs', ['timestamp', 'action'])
    op.create_index('idx_audit_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_table_record', 'audit_logs', ['table_name', 'record_id'])
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'])
    op.create_index(op.f('ix_audit_logs_record_id'), 'audit_logs', ['record_id'])
    op.create_index(op.f('ix_audit_logs_session_id'), 'audit_logs', ['session_id'])
    op.create_index(op.f('ix_audit_logs_table_name'), 'audit_logs', ['table_name'])
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])
    op.create_index(op.f('ix_audit_logs_request_id'), 'audit_logs', ['request_id'])
    
    # Create data_access_logs table
    op.create_table(
        'data_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('table_name', sa.String(length=255), nullable=False),
        sa.Column('record_id', sa.String(length=255), nullable=True),
        sa.Column('query_type', sa.String(length=50), nullable=False),
        sa.Column('query_params', sa.JSON(), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('request_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for data_access_logs
    op.create_index('idx_access_timestamp_user', 'data_access_logs', ['timestamp', 'user_id'])
    op.create_index('idx_access_table_timestamp', 'data_access_logs', ['table_name', 'timestamp'])
    op.create_index(op.f('ix_data_access_logs_session_id'), 'data_access_logs', ['session_id'])
    op.create_index(op.f('ix_data_access_logs_table_name'), 'data_access_logs', ['table_name'])
    op.create_index(op.f('ix_data_access_logs_timestamp'), 'data_access_logs', ['timestamp'])
    op.create_index(op.f('ix_data_access_logs_user_id'), 'data_access_logs', ['user_id'])
    op.create_index(op.f('ix_data_access_logs_request_id'), 'data_access_logs', ['request_id'])
    
    # Create user_action_logs table
    op.create_table(
        'user_action_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('action_category', sa.String(length=50), nullable=False),
        sa.Column('action_details', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('request_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for user_action_logs
    op.create_index('idx_action_timestamp_user', 'user_action_logs', ['timestamp', 'user_id'])
    op.create_index('idx_action_type_timestamp', 'user_action_logs', ['action_type', 'timestamp'])
    op.create_index('idx_action_category_status', 'user_action_logs', ['action_category', 'status'])
    op.create_index(op.f('ix_user_action_logs_action_category'), 'user_action_logs', ['action_category'])
    op.create_index(op.f('ix_user_action_logs_action_type'), 'user_action_logs', ['action_type'])
    op.create_index(op.f('ix_user_action_logs_session_id'), 'user_action_logs', ['session_id'])
    op.create_index(op.f('ix_user_action_logs_timestamp'), 'user_action_logs', ['timestamp'])
    op.create_index(op.f('ix_user_action_logs_user_id'), 'user_action_logs', ['user_id'])
    op.create_index(op.f('ix_user_action_logs_request_id'), 'user_action_logs', ['request_id'])
    
    # Create compliance_logs table
    op.create_table(
        'compliance_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('compliance_type', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('affected_data', sa.JSON(), nullable=True),
        sa.Column('compliance_status', sa.String(length=50), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for compliance_logs
    op.create_index('idx_compliance_type_timestamp', 'compliance_logs', ['compliance_type', 'timestamp'])
    op.create_index('idx_compliance_status', 'compliance_logs', ['compliance_status'])
    op.create_index(op.f('ix_compliance_logs_compliance_type'), 'compliance_logs', ['compliance_type'])
    op.create_index(op.f('ix_compliance_logs_timestamp'), 'compliance_logs', ['timestamp'])
    op.create_index(op.f('ix_compliance_logs_user_id'), 'compliance_logs', ['user_id'])
    
    # Create audit_reports table
    op.create_table(
        'audit_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('date_from', sa.DateTime(), nullable=False),
        sa.Column('date_to', sa.DateTime(), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_format', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit_reports
    op.create_index('idx_report_type_created', 'audit_reports', ['report_type', 'created_at'])
    op.create_index('idx_report_status', 'audit_reports', ['status'])
    op.create_index(op.f('ix_audit_reports_created_at'), 'audit_reports', ['created_at'])
    op.create_index(op.f('ix_audit_reports_report_type'), 'audit_reports', ['report_type'])


def downgrade():
    """Drop audit system tables"""
    
    # Drop audit_reports table
    op.drop_index('idx_report_status', table_name='audit_reports')
    op.drop_index('idx_report_type_created', table_name='audit_reports')
    op.drop_index(op.f('ix_audit_reports_report_type'), table_name='audit_reports')
    op.drop_index(op.f('ix_audit_reports_created_at'), table_name='audit_reports')
    op.drop_table('audit_reports')
    
    # Drop compliance_logs table
    op.drop_index('idx_compliance_status', table_name='compliance_logs')
    op.drop_index('idx_compliance_type_timestamp', table_name='compliance_logs')
    op.drop_index(op.f('ix_compliance_logs_user_id'), table_name='compliance_logs')
    op.drop_index(op.f('ix_compliance_logs_timestamp'), table_name='compliance_logs')
    op.drop_index(op.f('ix_compliance_logs_compliance_type'), table_name='compliance_logs')
    op.drop_table('compliance_logs')
    
    # Drop user_action_logs table
    op.drop_index('idx_action_category_status', table_name='user_action_logs')
    op.drop_index('idx_action_type_timestamp', table_name='user_action_logs')
    op.drop_index('idx_action_timestamp_user', table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_user_id'), table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_timestamp'), table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_session_id'), table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_action_type'), table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_action_category'), table_name='user_action_logs')
    op.drop_index(op.f('ix_user_action_logs_request_id'), table_name='user_action_logs')
    op.drop_table('user_action_logs')
    
    # Drop data_access_logs table
    op.drop_index('idx_access_table_timestamp', table_name='data_access_logs')
    op.drop_index('idx_access_timestamp_user', table_name='data_access_logs')
    op.drop_index(op.f('ix_data_access_logs_user_id'), table_name='data_access_logs')
    op.drop_index(op.f('ix_data_access_logs_timestamp'), table_name='data_access_logs')
    op.drop_index(op.f('ix_data_access_logs_table_name'), table_name='data_access_logs')
    op.drop_index(op.f('ix_data_access_logs_session_id'), table_name='data_access_logs')
    op.drop_index(op.f('ix_data_access_logs_request_id'), table_name='data_access_logs')
    op.drop_table('data_access_logs')
    
    # Drop audit_logs table
    op.drop_index('idx_audit_table_record', table_name='audit_logs')
    op.drop_index('idx_audit_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_timestamp_action', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_table_name'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_session_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_record_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_request_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
