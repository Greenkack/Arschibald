"""
Database Migration: Add Universal Data Columns

This migration adds dynamic_key and pdf_bytes columns to all existing tables.

Requirements: 14.4, 14.7
"""

import sqlite3
from typing import List, Tuple
from datetime import datetime


class UniversalColumnsMigration:
    """Migration to add universal data columns to all tables"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in database"""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get list of columns for a table"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in self.cursor.fetchall()]
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table"""
        columns = self.get_table_columns(table_name)
        return column_name in columns
    
    def add_dynamic_key_column(self, table_name: str) -> bool:
        """Add dynamic_key column to table"""
        if self.column_exists(table_name, 'dynamic_key'):
            print(f"  Column 'dynamic_key' already exists in {table_name}")
            return False
        
        try:
            self.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN dynamic_key TEXT"
            )
            print(f"  Added 'dynamic_key' column to {table_name}")
            return True
        except Exception as e:
            print(f"  Error adding 'dynamic_key' to {table_name}: {e}")
            return False
    
    def add_pdf_bytes_column(self, table_name: str) -> bool:
        """Add pdf_bytes column to table"""
        if self.column_exists(table_name, 'pdf_bytes'):
            print(f"  Column 'pdf_bytes' already exists in {table_name}")
            return False
        
        try:
            self.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN pdf_bytes BLOB"
            )
            print(f"  Added 'pdf_bytes' column to {table_name}")
            return True
        except Exception as e:
            print(f"  Error adding 'pdf_bytes' to {table_name}: {e}")
            return False
    
    def create_dynamic_key_index(self, table_name: str) -> bool:
        """Create index on dynamic_key column"""
        index_name = f"idx_{table_name}_dynamic_key"
        
        try:
            self.cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}(dynamic_key)"
            )
            print(f"  Created index {index_name}")
            return True
        except Exception as e:
            print(f"  Error creating index {index_name}: {e}")
            return False
    
    def migrate_table(self, table_name: str) -> Tuple[bool, bool, bool]:
        """
        Migrate a single table by adding universal columns.
        
        Returns:
            Tuple of (dynamic_key_added, pdf_bytes_added, index_created)
        """
        print(f"\nMigrating table: {table_name}")
        
        key_added = self.add_dynamic_key_column(table_name)
        pdf_added = self.add_pdf_bytes_column(table_name)
        index_created = False
        
        # Only create index if column was added or already exists
        if key_added or self.column_exists(table_name, 'dynamic_key'):
            index_created = self.create_dynamic_key_index(table_name)
        
        return key_added, pdf_added, index_created
    
    def migrate_all_tables(self, exclude_tables: List[str] = None) -> dict:
        """
        Migrate all tables in database.
        
        Args:
            exclude_tables: List of table names to exclude from migration
        
        Returns:
            Dictionary with migration statistics
        """
        exclude_tables = exclude_tables or []
        tables = self.get_all_tables()
        
        stats = {
            'total_tables': len(tables),
            'migrated_tables': 0,
            'skipped_tables': 0,
            'dynamic_key_added': 0,
            'pdf_bytes_added': 0,
            'indexes_created': 0,
            'errors': []
        }
        
        print(f"\nFound {len(tables)} tables to migrate")
        print(f"Excluding: {exclude_tables}")
        
        for table in tables:
            if table in exclude_tables:
                print(f"\nSkipping table: {table} (excluded)")
                stats['skipped_tables'] += 1
                continue
            
            try:
                key_added, pdf_added, index_created = self.migrate_table(table)
                
                stats['migrated_tables'] += 1
                if key_added:
                    stats['dynamic_key_added'] += 1
                if pdf_added:
                    stats['pdf_bytes_added'] += 1
                if index_created:
                    stats['indexes_created'] += 1
                    
            except Exception as e:
                error_msg = f"Error migrating {table}: {e}"
                print(f"  {error_msg}")
                stats['errors'].append(error_msg)
        
        return stats
    
    def run(self, exclude_tables: List[str] = None, commit: bool = True) -> dict:
        """
        Run the migration.
        
        Args:
            exclude_tables: List of table names to exclude
            commit: Whether to commit changes (False for dry run)
        
        Returns:
            Dictionary with migration statistics
        """
        print("=" * 60)
        print("Universal Data Columns Migration")
        print("=" * 60)
        print(f"Database: {self.db_path}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Commit changes: {commit}")
        print("=" * 60)
        
        try:
            self.connect()
            stats = self.migrate_all_tables(exclude_tables)
            
            if commit:
                self.conn.commit()
                print("\n✓ Changes committed to database")
            else:
                self.conn.rollback()
                print("\n✗ Dry run - changes rolled back")
            
            print("\n" + "=" * 60)
            print("Migration Summary")
            print("=" * 60)
            print(f"Total tables: {stats['total_tables']}")
            print(f"Migrated tables: {stats['migrated_tables']}")
            print(f"Skipped tables: {stats['skipped_tables']}")
            print(f"Dynamic key columns added: {stats['dynamic_key_added']}")
            print(f"PDF bytes columns added: {stats['pdf_bytes_added']}")
            print(f"Indexes created: {stats['indexes_created']}")
            
            if stats['errors']:
                print(f"\nErrors: {len(stats['errors'])}")
                for error in stats['errors']:
                    print(f"  - {error}")
            else:
                print("\n✓ No errors")
            
            print("=" * 60)
            
            return stats
            
        finally:
            self.close()


def run_migration(
    db_path: str,
    exclude_tables: List[str] = None,
    dry_run: bool = False
) -> dict:
    """
    Run the universal columns migration.
    
    Args:
        db_path: Path to SQLite database file
        exclude_tables: List of table names to exclude
        dry_run: If True, don't commit changes
    
    Returns:
        Dictionary with migration statistics
    """
    migration = UniversalColumnsMigration(db_path)
    return migration.run(exclude_tables=exclude_tables, commit=not dry_run)


if __name__ == "__main__":
    import sys
    import os
    
    # Default database path
    default_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'app_data.db')
    
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    
    # Check if dry run
    dry_run = '--dry-run' in sys.argv
    
    # Tables to exclude (system tables, etc.)
    exclude = ['sqlite_sequence', 'alembic_version']
    
    # Run migration
    stats = run_migration(db_path, exclude_tables=exclude, dry_run=dry_run)
    
    # Exit with error code if there were errors
    sys.exit(1 if stats['errors'] else 0)
