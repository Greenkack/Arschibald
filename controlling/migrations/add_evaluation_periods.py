"""
Database Migration: Add Evaluation Periods Support

This migration adds support for evaluation periods to the Controlling system.
It creates the new EvaluationPeriod table and adds the period_id foreign key
to the PerformanceData table.

This migration is backwards-compatible - existing performance data without
a period_id will continue to work.
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def migrate_add_evaluation_periods(db_path: str = "data/app_data.db"):
    """
    Add evaluation periods support to the database.
    
    Args:
        db_path: Path to the SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='controlling_evaluation_periods'"
        )
        periods_table_exists = cursor.fetchone() is not None
        
        # Create EvaluationPeriod table if it doesn't exist
        if not periods_table_exists:
            logger.info("Creating controlling_evaluation_periods table...")
            cursor.execute("""
                CREATE TABLE controlling_evaluation_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    period_type VARCHAR(50) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
                    employee_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    completed_at DATETIME,
                    FOREIGN KEY (employee_id) REFERENCES controlling_employees(id)
                )
            """)
            
            # Create indexes
            cursor.execute(
                "CREATE INDEX idx_periods_type ON controlling_evaluation_periods(period_type)"
            )
            cursor.execute(
                "CREATE INDEX idx_periods_start ON controlling_evaluation_periods(start_date)"
            )
            cursor.execute(
                "CREATE INDEX idx_periods_end ON controlling_evaluation_periods(end_date)"
            )
            cursor.execute(
                "CREATE INDEX idx_periods_status ON controlling_evaluation_periods(status)"
            )
            cursor.execute(
                "CREATE INDEX idx_periods_employee ON controlling_evaluation_periods(employee_id)"
            )
            
            logger.info("controlling_evaluation_periods table created successfully")
        else:
            logger.info("controlling_evaluation_periods table already exists")
        
        # Check if period_id column exists in PerformanceData
        cursor.execute("PRAGMA table_info(controlling_performance_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'period_id' not in columns:
            logger.info("Adding period_id column to controlling_performance_data...")
            
            # Add period_id column (nullable for backwards compatibility)
            cursor.execute("""
                ALTER TABLE controlling_performance_data
                ADD COLUMN period_id INTEGER
                REFERENCES controlling_evaluation_periods(id)
            """)
            
            # Create index
            cursor.execute(
                "CREATE INDEX idx_performance_period ON controlling_performance_data(period_id)"
            )
            
            logger.info("period_id column added successfully")
        else:
            logger.info("period_id column already exists in controlling_performance_data")
        
        conn.commit()
        logger.info("Migration completed successfully!")
        
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
        
    finally:
        conn.close()


def verify_migration(db_path: str = "data/app_data.db"):
    """
    Verify that the migration was applied correctly.
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        True if migration is complete, False otherwise
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check for EvaluationPeriod table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='controlling_evaluation_periods'"
        )
        has_periods_table = cursor.fetchone() is not None
        
        # Check for period_id column
        cursor.execute("PRAGMA table_info(controlling_performance_data)")
        columns = [row[1] for row in cursor.fetchall()]
        has_period_id = 'period_id' in columns
        
        if has_periods_table and has_period_id:
            logger.info("Migration verification successful!")
            return True
        else:
            logger.warning("Migration incomplete:")
            if not has_periods_table:
                logger.warning("  - controlling_evaluation_periods table missing")
            if not has_period_id:
                logger.warning("  - period_id column missing in controlling_performance_data")
            return False
            
    finally:
        conn.close()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Controlling System - Evaluation Periods Migration")
    print("=" * 60)
    print()
    
    # Run migration
    try:
        migrate_add_evaluation_periods()
        print()
        
        # Verify
        print("Verifying migration...")
        if verify_migration():
            print()
            print("Migration erfolgreich abgeschlossen!")
            print()
            print("Neue Funktionen:")
            print("  Auswertungsperioden erstellen und verwalten")
            print("  Leistungsdaten mit Perioden verknüpfen")
            print("  Zeitraum-basierte Auswertungen (täglich, wöchentlich, monatlich, etc.)")
            print("  Perioden-Archiv mit Statusverwaltung")
        else:
            print()
            print("Migration unvollständig. Bitte Logs prüfen.")
    
    except Exception as e:
        print(f"\nFehler bei Migration: {e}")
        print("Bitte Logs prüfen und erneut versuchen.")
