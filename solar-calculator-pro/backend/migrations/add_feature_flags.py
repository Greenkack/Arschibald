"""
Database Migration: Add Feature Flags Tables

This migration creates the necessary tables for the feature flag system.
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
import os
from pathlib import Path

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./solar_calculator.db')

def upgrade():
    """Create feature flag tables"""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    
    # Create roles table
    roles = Table(
        'roles',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), unique=True, nullable=False, index=True),
        Column('description', Text, nullable=True)
    )
    
    # Create feature_flags table
    feature_flags = Table(
        'feature_flags',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('key', String(255), unique=True, nullable=False, index=True),
        Column('name', String(255), nullable=False),
        Column('description', Text, nullable=True),
        Column('enabled', Boolean, default=False, nullable=False),
        Column('flag_type', String(50), default='global', nullable=False),
        Column('rollout_percentage', Integer, default=0, nullable=False),
        Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column('updated_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=True)
    )
    
    # Create feature_flag_users association table
    feature_flag_users = Table(
        'feature_flag_users',
        metadata,
        Column('feature_flag_id', Integer, ForeignKey('feature_flags.id'), primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    )
    
    # Create feature_flag_roles association table
    feature_flag_roles = Table(
        'feature_flag_roles',
        metadata,
        Column('feature_flag_id', Integer, ForeignKey('feature_flags.id'), primary_key=True),
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    print("✅ Feature flag tables created successfully")


def downgrade():
    """Drop feature flag tables"""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    
    # Define tables in reverse order for proper dropping
    feature_flag_roles = Table('feature_flag_roles', metadata, autoload_with=engine)
    feature_flag_users = Table('feature_flag_users', metadata, autoload_with=engine)
    feature_flags = Table('feature_flags', metadata, autoload_with=engine)
    roles = Table('roles', metadata, autoload_with=engine)
    
    # Drop tables
    feature_flag_roles.drop(engine)
    feature_flag_users.drop(engine)
    feature_flags.drop(engine)
    roles.drop(engine)
    
    print("✅ Feature flag tables dropped successfully")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
