"""
Database Migration: Add Encryption Tables

Creates tables for encryption settings, encrypted fields registry,
encryption keys metadata, audit logs, and policies.

Requirements: 11.3
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
import os


def upgrade(engine):
    """
    Create encryption-related tables.
    
    Args:
        engine: SQLAlchemy engine
    """
    metadata = MetaData()
    
    # Encryption Settings Table
    encryption_settings = Table(
        'encryption_settings',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('setting_key', String(255), unique=True, nullable=False, index=True),
        Column('setting_value', Text, nullable=False),
        Column('description', Text),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # Encrypted Fields Registry Table
    encrypted_fields = Table(
        'encrypted_fields',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('table_name', String(255), nullable=False, index=True),
        Column('field_name', String(255), nullable=False, index=True),
        Column('encryption_algorithm', String(100), default='Fernet'),
        Column('key_name', String(255), nullable=False),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # Encryption Keys Metadata Table
    encryption_keys = Table(
        'encryption_keys',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('key_name', String(255), unique=True, nullable=False, index=True),
        Column('key_type', String(100), default='symmetric'),
        Column('algorithm', String(100), default='Fernet'),
        Column('purpose', String(255)),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('last_rotated_at', DateTime(timezone=True)),
        Column('rotation_schedule', String(100))
    )
    
    # Encryption Audit Log Table
    encryption_audit_log = Table(
        'encryption_audit_log',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('timestamp', DateTime(timezone=True), server_default=func.now(), index=True),
        Column('operation', String(100), nullable=False, index=True),
        Column('data_type', String(100), nullable=False, index=True),
        Column('user_id', String(255), index=True),
        Column('success', Boolean, default=True, index=True),
        Column('error_message', Text),
        Column('metadata', JSON),
        Column('ip_address', String(45)),
        Column('user_agent', String(500))
    )
    
    # Encryption Policies Table
    encryption_policies = Table(
        'encryption_policies',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('policy_name', String(255), unique=True, nullable=False, index=True),
        Column('description', Text),
        Column('data_classification', String(100)),
        Column('encryption_required', Boolean, default=True),
        Column('encryption_algorithm', String(100), default='Fernet'),
        Column('key_rotation_days', Integer, default=90),
        Column('applies_to_tables', JSON),
        Column('applies_to_fields', JSON),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # Create all tables
    metadata.create_all(engine)
    
    print("✅ Encryption tables created successfully")
    
    # Insert default encryption settings
    with engine.connect() as conn:
        # Default encryption enabled
        conn.execute(
            encryption_settings.insert().values(
                setting_key='encryption_enabled',
                setting_value='true',
                description='Master switch for encryption system',
                is_active=True
            )
        )
        
        # Default encryption algorithm
        conn.execute(
            encryption_settings.insert().values(
                setting_key='default_algorithm',
                setting_value='Fernet',
                description='Default encryption algorithm',
                is_active=True
            )
        )
        
        # Key rotation interval
        conn.execute(
            encryption_settings.insert().values(
                setting_key='key_rotation_days',
                setting_value='90',
                description='Default key rotation interval in days',
                is_active=True
            )
        )
        
        # Audit logging enabled
        conn.execute(
            encryption_settings.insert().values(
                setting_key='audit_logging_enabled',
                setting_value='true',
                description='Enable encryption audit logging',
                is_active=True
            )
        )
        
        # Default encryption policy
        conn.execute(
            encryption_policies.insert().values(
                policy_name='default_policy',
                description='Default encryption policy for sensitive data',
                data_classification='confidential',
                encryption_required=True,
                encryption_algorithm='Fernet',
                key_rotation_days=90,
                applies_to_tables=['users', 'customers', 'contracts'],
                applies_to_fields=['password', 'email', 'phone', 'ssn', 'credit_card'],
                is_active=True
            )
        )
        
        conn.commit()
        
    print("✅ Default encryption settings and policies created")


def downgrade(engine):
    """
    Drop encryption-related tables.
    
    Args:
        engine: SQLAlchemy engine
    """
    metadata = MetaData()
    
    # Define tables to drop
    table_names = [
        'encryption_policies',
        'encryption_audit_log',
        'encryption_keys',
        'encrypted_fields',
        'encryption_settings'
    ]
    
    # Drop tables in reverse order
    for table_name in table_names:
        table = Table(table_name, metadata)
        table.drop(engine, checkfirst=True)
        print(f"✅ Dropped table: {table_name}")


def run_migration():
    """Run the migration."""
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./solar_calculator.db')
    
    # Create engine
    engine = create_engine(database_url)
    
    print("🔄 Running encryption tables migration...")
    upgrade(engine)
    print("✅ Migration completed successfully")


if __name__ == '__main__':
    run_migration()
