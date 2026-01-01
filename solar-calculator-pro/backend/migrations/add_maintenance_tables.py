"""
Database migration: Add maintenance tables

This migration creates tables for:
- Maintenance logs
- System diagnostics
- Cache entries
- Temporary file tracking
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
import os
from pathlib import Path


def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv("DATABASE_URL", "sqlite:///./solar_calculator.db")


def upgrade():
    """Create maintenance tables"""
    engine = create_engine(get_database_url())
    metadata = MetaData()

    # Maintenance Logs table
    maintenance_logs = Table(
        'maintenance_logs',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('operation_type', String(100), nullable=False, index=True),
        Column('operation_name', String(200), nullable=False),
        Column('status', String(50), nullable=False),
        Column('details', JSON),
        Column('error_message', Text, nullable=True),
        Column('started_at', DateTime(timezone=True), server_default=func.now()),
        Column('completed_at', DateTime(timezone=True), nullable=True),
        Column('duration_seconds', Float, nullable=True),
        Column('performed_by', String(100), nullable=True))

    # System Diagnostics table
    system_diagnostics = Table(
        'system_diagnostics',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('diagnostic_type', String(100), nullable=False, index=True),
        Column('status', String(50), nullable=False),
        Column('metrics', JSON),
        Column('issues', JSON, nullable=True),
        Column('recommendations', JSON, nullable=True),
        Column('checked_at', DateTime(timezone=True), server_default=func.now()))

    # Cache Entries table
    cache_entries = Table(
        'cache_entries',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('cache_key', String(500), unique=True, nullable=False, index=True),
        Column('cache_type', String(100), nullable=False, index=True),
        Column('size_bytes', Integer, nullable=False),
        Column('hit_count', Integer, default=0),
        Column('last_accessed', DateTime(timezone=True), server_default=func.now()),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('expires_at', DateTime(timezone=True), nullable=True),
        Column('is_valid', Boolean, default=True))

    # Temp Files table
    temp_files = Table(
        'temp_files',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('file_path', String(1000), nullable=False),
        Column('file_type', String(100), nullable=False),
        Column('size_bytes', Integer, nullable=False),
        Column('created_by', String(100), nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('last_accessed', DateTime(timezone=True), server_default=func.now()),
        Column('should_delete', Boolean, default=False),
        Column('delete_after', DateTime(timezone=True), nullable=True))

    # Create all tables
    metadata.create_all(engine)
    print("✅ Maintenance tables created successfully")


def downgrade():
    """Drop maintenance tables"""
    engine = create_engine(get_database_url())
    metadata = MetaData()

    # Define tables to drop
    table_names = [
        'maintenance_logs',
        'system_diagnostics',
        'cache_entries',
        'temp_files'
    ]

    for table_name in table_names:
        table = Table(table_name, metadata)
        table.drop(engine, checkfirst=True)

    print("✅ Maintenance tables dropped successfully")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
