"""
Example Migration: Add User Columns
Demonstrates schema migration with validation and rollback.
"""

from migration_manager import MigrationStep, MigrationType
from data_validator import DataValidator


def create_migration() -> MigrationStep:
    """Create migration step for adding user columns"""
    
    # Define up migration (apply changes)
    up_sql = """
        ALTER TABLE users ADD COLUMN email TEXT;
        ALTER TABLE users ADD COLUMN phone TEXT;
        ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """
    
    # Define down migration (rollback changes)
    down_sql = """
        ALTER TABLE users DROP COLUMN email;
        ALTER TABLE users DROP COLUMN phone;
        ALTER TABLE users DROP COLUMN created_at;
        ALTER TABLE users DROP COLUMN updated_at;
    """
    
    # Define validation function
    def validate(session):
        """Validate that columns were added correctly"""
        validator = DataValidator(session)
        
        # Check that columns exist
        validator.add_column_exists('users', 'email')
        validator.add_column_exists('users', 'phone')
        validator.add_column_exists('users', 'created_at')
        validator.add_column_exists('users', 'updated_at')
        
        result = validator.validate()
        return result['valid']
    
    return MigrationStep(
        id="001_add_user_columns",
        name="Add User Contact Columns",
        description="Add email, phone, and timestamp columns to users table",
        type=MigrationType.SCHEMA,
        up_sql=up_sql,
        down_sql=down_sql,
        validation_function=validate,
        dependencies=[]
    )
