"""
Database Migration: Add Component Toggles Table

Creates the component_toggles table for managing component-level feature toggles.
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.sql import func
import os


def upgrade(engine):
    """Create component_toggles table"""
    metadata = MetaData()
    
    component_toggles = Table(
        'component_toggles',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('category', Enum(
            'chart', 'form_field', 'calculation_option', 
            'export_format', 'ui_theme', 'language',
            name='component_toggle_category'
        ), nullable=False, index=True),
        Column('component_key', String(255), nullable=False, index=True),
        Column('component_name', String(255), nullable=False),
        Column('enabled', Boolean, default=True, nullable=False),
        Column('toggle_type', Enum(
            'visibility', 'feature', 'permission',
            name='component_toggle_type'
        ), default='feature'),
        Column('user_id', Integer, nullable=True, index=True),
        Column('metadata', JSON, default={}),
        Column('description', String(500), nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    metadata.create_all(engine)
    print("✅ Created component_toggles table")


def downgrade(engine):
    """Drop component_toggles table"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if 'component_toggles' in metadata.tables:
        metadata.tables['component_toggles'].drop(engine)
        print("✅ Dropped component_toggles table")


def run_migration():
    """Run the migration"""
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./solar_calculator.db')
    engine = create_engine(database_url)
    
    print("Running component toggles migration...")
    upgrade(engine)
    print("Migration complete!")


if __name__ == "__main__":
    run_migration()
