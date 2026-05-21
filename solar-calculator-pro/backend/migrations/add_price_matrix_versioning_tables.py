"""
Database Migration: Add Price Matrix Versioning Tables

This migration adds the necessary tables for price matrix versioning system:
- price_matrix_versions
- price_matrix_version_changes
- price_matrix_version_comparisons
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from datetime import datetime


def upgrade(engine):
    """Add price matrix versioning tables"""
    metadata = MetaData()

    # Price Matrix Versions table
    price_matrix_versions = Table(
        'price_matrix_versions',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('matrix_id', Integer, ForeignKey('price_matrices.id'), nullable=False),
        Column('version_number', Integer, nullable=False),
        Column('version_name', String(255), nullable=False),
        Column('description', Text, nullable=True),
        Column('matrix_data', JSON, nullable=False),
        Column('metadata', JSON, nullable=True),
        Column('status', String(50), default='draft'),
        Column('is_active', Boolean, default=False),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('approved_by', Integer, ForeignKey('users.id'), nullable=True),
        Column('approved_at', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))

    # Price Matrix Version Changes table
    price_matrix_version_changes = Table(
        'price_matrix_version_changes',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('version_id', Integer, ForeignKey('price_matrix_versions.id'), nullable=False),
        Column('change_type', String(50), nullable=False),
        Column('field_name', String(255), nullable=True),
        Column('old_value', Text, nullable=True),
        Column('new_value', Text, nullable=True),
        Column('change_description', Text, nullable=True),
        Column('changed_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('changed_at', DateTime, default=datetime.utcnow))

    # Price Matrix Version Comparisons table
    price_matrix_version_comparisons = Table(
        'price_matrix_version_comparisons',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('version_a_id', Integer, ForeignKey('price_matrix_versions.id'), nullable=False),
        Column('version_b_id', Integer, ForeignKey('price_matrix_versions.id'), nullable=False),
        Column('differences', JSON, nullable=False),
        Column('summary', JSON, nullable=True),
        Column('compared_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('compared_at', DateTime, default=datetime.utcnow))

    # Create all tables
    metadata.create_all(engine)
    print("✅ Price matrix versioning tables created successfully")


def downgrade(engine):
    """Remove price matrix versioning tables"""
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Drop tables in reverse order (due to foreign keys)
    tables_to_drop = [
        'price_matrix_version_comparisons',
        'price_matrix_version_changes',
        'price_matrix_versions'
    ]

    for table_name in tables_to_drop:
        if table_name in metadata.tables:
            metadata.tables[table_name].drop(engine)
            print(f"✅ Dropped table: {table_name}")


if __name__ == "__main__":
    # Example usage
    import sys
    from backend.core.database import engine

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        print("Running downgrade migration...")
        downgrade(engine)
    else:
        print("Running upgrade migration...")
        upgrade(engine)
