"""
Database Migration: Add agent_name column to controlling_employees table

This migration adds the optional agent_name column to the controlling_employees table.
"""

import sqlite3
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'app_data.db'


def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_agent_name_column():
    """Add agent_name column to controlling_employees table"""
    
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='controlling_employees'"
        )
        if not cursor.fetchone():
            logger.warning("Table 'controlling_employees' does not exist yet - will be created on app startup")
            conn.close()
            return True
        
        # Check if column already exists
        if check_column_exists(conn, 'controlling_employees', 'agent_name'):
            logger.info("Column 'agent_name' already exists in 'controlling_employees' table")
            conn.close()
            return True
        
        # Add the column
        logger.info("Adding 'agent_name' column to 'controlling_employees' table...")
        cursor.execute(
            "ALTER TABLE controlling_employees ADD COLUMN agent_name VARCHAR(100)"
        )
        conn.commit()
        
        # Verify the column was added
        if check_column_exists(conn, 'controlling_employees', 'agent_name'):
            logger.info("SUCCESS: Column 'agent_name' added successfully!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(controlling_employees)")
            columns = cursor.fetchall()
            logger.info("\nCurrent table structure:")
            for col in columns:
                logger.info(f"  - {col[1]} ({col[2]})")
            
            conn.close()
            return True
        else:
            logger.error("FAILED: Column was not added")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def migrate_using_sqlalchemy():
    """Alternative: Use SQLAlchemy to create/update tables"""
    try:
        logger.info("\n" + "="*60)
        logger.info("Using SQLAlchemy migration approach...")
        logger.info("="*60)
        
        from backend.core.database import Base, engine
        from controlling import models  # Import all models
        
        # This will create missing tables and columns
        Base.metadata.create_all(bind=engine)
        
        logger.info("SQLAlchemy migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"SQLAlchemy migration failed: {e}")
        return False


def main():
    """Run the migration"""
    print("\n" + "="*60)
    print("CONTROLLING SYSTEM - DATABASE MIGRATION")
    print("Adding 'agent_name' column to controlling_employees")
    print("="*60 + "\n")
    
    # Method 1: Direct SQL ALTER TABLE
    logger.info("Method 1: Direct SQL Migration")
    success1 = add_agent_name_column()
    
    # Method 2: SQLAlchemy (creates tables if missing)
    logger.info("\nMethod 2: SQLAlchemy Migration")
    success2 = migrate_using_sqlalchemy()
    
    print("\n" + "="*60)
    if success1 or success2:
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nYou can now:")
        print("  1. Restart the Streamlit app")
        print("  2. Go to: Admin Panel -> Controlling Einstellungen")
        print("  3. Add employees with 'Agentname' field")
        print("="*60 + "\n")
        return 0
    else:
        print("MIGRATION FAILED")
        print("="*60)
        print("\nPlease check the error messages above.")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    exit(main())
