"""
Migration: Add Teams to Controlling System

Adds the controlling_teams table and team_id foreign key to controlling_employees.
This enables team-based organization and reporting.

Run this migration after the controlling system is initialized.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database import get_db_connection
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_teams():
    """
    Add teams table and team_id column to employees.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if teams table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='controlling_teams'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            logger.info("Creating controlling_teams table...")
            
            cursor.execute("""
                CREATE TABLE controlling_teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    team_leader_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (team_leader_id) REFERENCES controlling_employees(id)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX ix_controlling_teams_id ON controlling_teams(id)
            """)
            
            cursor.execute("""
                CREATE INDEX ix_controlling_teams_name ON controlling_teams(name)
            """)
            
            conn.commit()
            logger.info("controlling_teams table created")
        else:
            logger.info("controlling_teams table already exists")
        
        # Check if team_id column exists in employees
        cursor.execute("PRAGMA table_info(controlling_employees)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'team_id' not in columns:
            logger.info("Adding team_id column to controlling_employees...")
            
            cursor.execute("""
                ALTER TABLE controlling_employees
                ADD COLUMN team_id INTEGER
            """)
            
            cursor.execute("""
                CREATE INDEX ix_controlling_employees_team_id ON controlling_employees(team_id)
            """)
            
            conn.commit()
            logger.info("team_id column added to controlling_employees")
        else:
            logger.info("team_id column already exists in controlling_employees")
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*60)
    print("CONTROLLING SYSTEM - TEAMS MIGRATION")
    print("="*60)
    print()
    print("This migration will:")
    print("  1. Create controlling_teams table")
    print("  2. Add team_id column to controlling_employees")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_add_teams()
        print()
        print("="*60)
        print("Migration completed! You can now use team management.")
        print("="*60)
    else:
        print("Migration cancelled.")
