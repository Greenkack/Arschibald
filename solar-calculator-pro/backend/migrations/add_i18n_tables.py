"""
Migration: Add i18n tables
Creates tables for translations and user language preferences
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, ForeignKey, Index
from datetime import datetime
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./solar_calculator.db")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define translations table
translations = Table(
    'translations',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('key', String(255), nullable=False, index=True),
    Column('namespace', String(100), nullable=False, index=True),
    Column('language', String(10), nullable=False, index=True),
    Column('value', Text, nullable=False),
    Column('modified_by', String(100)),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now),
    Index('idx_translation_lookup', 'key', 'namespace', 'language'),
    Index('idx_namespace_language', 'namespace', 'language'))

# Define user_language_preferences table
user_language_preferences = Table(
    'user_language_preferences',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('user_id', Integer, ForeignKey('users.id'), unique=True, nullable=False),
    Column('language', String(10), nullable=False, default='de'),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now))

# Define translation_history table
translation_history = Table(
    'translation_history',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('translation_id', Integer, ForeignKey('translations.id'), nullable=False),
    Column('old_value', Text),
    Column('new_value', Text, nullable=False),
    Column('modified_by', String(100), nullable=False),
    Column('modified_at', DateTime, default=datetime.now))


def upgrade():
    """Create i18n tables"""
    print("Creating i18n tables...")
    metadata.create_all(engine)
    print("✓ i18n tables created successfully")


def downgrade():
    """Drop i18n tables"""
    print("Dropping i18n tables...")
    metadata.drop_all(engine)
    print("✓ i18n tables dropped successfully")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
