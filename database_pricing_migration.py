#!/usr/bin/env python3
"""
Database Migration Script for Enhanced Pricing System
Adds pricing-related fields and tables to support the enhanced pricing functionality.
"""

import os
import sqlite3
import traceback
from datetime import datetime


def get_db_connection() -> sqlite3.Connection | None:
    """Get database connection with row factory"""
    try:
        from database import get_db_connection as db_get_connection
        return db_get_connection()
    except ImportError:
        # Fallback if database module not available
        try:
            from database import DB_PATH
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        except ImportError:
            # Last resort - use default path
            db_path = os.path.join('data', 'app_data.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                return conn
            print(f"Database file not found at {db_path}")
            return None


def backup_database() -> bool:
    """Create a backup of the database before migration"""
    try:
        from database import DB_PATH
        backup_path = f"{DB_PATH}.backup_{
            datetime.now().strftime('%Y%m%d_%H%M%S')}"

        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"Failed to create database backup: {e}")
        return False


def add_pricing_fields_to_products(conn: sqlite3.Connection) -> bool:
    """Add enhanced pricing fields to the products table"""
    cursor = conn.cursor()

    # Get current table structure
    cursor.execute("PRAGMA table_info(products)")
    existing_columns = {row[1]: row for row in cursor.fetchall()}

    # Define new pricing fields to add
    new_pricing_fields = {
        # "Stück", "Meter", "pauschal", "kWp", etc.
        'calculate_per': 'TEXT DEFAULT "Stück"',
        'purchase_price_net': 'REAL DEFAULT 0.0',
        'margin_type': 'TEXT DEFAULT "percentage"',  # "percentage" or "fixed"
        'margin_value': 'REAL DEFAULT 0.0',
        'margin_priority': 'INTEGER DEFAULT 0',
        'pricing_category': 'TEXT DEFAULT ""',
        'last_price_update': 'TEXT DEFAULT ""',
        'technology': 'TEXT DEFAULT ""',  # For technology-specific pricing
        'feature': 'TEXT DEFAULT ""',    # For feature-based pricing
        'design': 'TEXT DEFAULT ""',     # For design-specific pricing
        'upgrade': 'TEXT DEFAULT ""',    # For upgrade pricing
        'max_kwh_capacity': 'REAL DEFAULT 0.0',
        'outdoor_opt': 'TEXT DEFAULT ""',
        'self_supply_feature': 'TEXT DEFAULT ""',
        'shadow_fading': 'TEXT DEFAULT ""',
        'smart_home': 'TEXT DEFAULT ""'
    }

    # Add missing fields
    added_fields = []
    for field_name, field_definition in new_pricing_fields.items():
        if field_name not in existing_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE products ADD COLUMN {field_name} {field_definition}")
                conn.commit()
                added_fields.append(field_name)
                print(f"Added field '{field_name}' to products table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"Error adding field '{field_name}': {e}")
                    return False

    if added_fields:
        print(
            f"Successfully added {
                len(added_fields)} pricing fields to products table")
    else:
        print("All pricing fields already exist in products table")

    return True


def create_pricing_rules_table(conn: sqlite3.Connection) -> bool:
    """Create the pricing_rules table for advanced pricing configurations"""
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL, -- 'margin', 'discount', 'surcharge'
                applies_to TEXT NOT NULL, -- 'product', 'category', 'global'
                target_id INTEGER, -- product_id or category reference
                rule_config TEXT, -- JSON configuration
                is_active INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Created pricing_rules table")
        return True
    except sqlite3.Error as e:
        print(f"Error creating pricing_rules table: {e}")
        return False


def create_pricing_history_table(conn: sqlite3.Connection) -> bool:
    """Create the pricing_history table for audit trail"""
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_reason TEXT,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)
        conn.commit()
        print("Created pricing_history table")
        return True
    except sqlite3.Error as e:
        print(f"Error creating pricing_history table: {e}")
        return False


def migrate_existing_data(conn: sqlite3.Connection) -> bool:
    """Migrate existing data to preserve compatibility"""
    cursor = conn.cursor()

    try:
        # Set default calculate_per based on category
        category_mappings = {
            'Modul': 'Stück',
            'Wechselrichter': 'Stück',
            'Batteriespeicher': 'Stück',
            'Kabel': 'Meter',
            'Montagesystem': 'kWp',
            'Installation': 'pauschal',
            'Service': 'pauschal'
        }

        for category, calc_method in category_mappings.items():
            cursor.execute(
                "UPDATE products SET calculate_per = ? WHERE category = ? AND calculate_per IS NULL",
                (calc_method, category)
            )

        # Set default margin values for existing products
        cursor.execute("""
            UPDATE products
            SET margin_type = 'percentage',
                margin_value = 25.0,
                pricing_category = category
            WHERE margin_type IS NULL OR margin_type = ''
        """)

        conn.commit()
        print("Successfully migrated existing product data")
        return True
    except sqlite3.Error as e:
        print(f"Error migrating existing data: {e}")
        return False


def create_indexes(conn: sqlite3.Connection) -> bool:
    """Create indexes for better performance on pricing queries"""
    cursor = conn.cursor()

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_products_calculate_per ON products(calculate_per)",
        "CREATE INDEX IF NOT EXISTS idx_products_pricing_category ON products(pricing_category)",
        "CREATE INDEX IF NOT EXISTS idx_products_last_price_update ON products(last_price_update)",
        "CREATE INDEX IF NOT EXISTS idx_pricing_rules_applies_to ON pricing_rules(applies_to, target_id)",
        "CREATE INDEX IF NOT EXISTS idx_pricing_rules_active ON pricing_rules(is_active, priority)",
        "CREATE INDEX IF NOT EXISTS idx_pricing_history_product ON pricing_history(product_id, changed_at)"]

    try:
        for index_sql in indexes:
            cursor.execute(index_sql)
        conn.commit()
        print("Created performance indexes for pricing tables")
        return True
    except sqlite3.Error as e:
        print(f"Error creating indexes: {e}")
        return False


def verify_migration(conn: sqlite3.Connection) -> bool:
    """Verify that the migration was successful"""
    cursor = conn.cursor()

    try:
        # Check that new fields exist in products table
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        required_fields = [
            'calculate_per',
            'purchase_price_net',
            'margin_type',
            'margin_value',
            'technology',
            'feature',
            'design',
            'upgrade']

        missing_fields = [
            field for field in required_fields if field not in columns]
        if missing_fields:
            print(
                f"Migration verification failed: Missing fields {missing_fields}")
            return False

        # Check that new tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['pricing_rules', 'pricing_history']
        missing_tables = [
            table for table in required_tables if table not in tables]
        if missing_tables:
            print(
                f"Migration verification failed: Missing tables {missing_tables}")
            return False

        # Check that data was migrated properly
        cursor.execute(
            "SELECT COUNT(*) FROM products WHERE calculate_per IS NOT NULL")
        products_with_calc_per = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        if total_products > 0 and products_with_calc_per == 0:
            print("Migration verification failed: No products have calculate_per set")
            return False

        print("Migration verification successful")
        return True

    except sqlite3.Error as e:
        print(f"Error during migration verification: {e}")
        return False


def run_migration() -> bool:
    """Run the complete database migration"""
    print("Starting enhanced pricing system database migration...")

    # Create backup
    if not backup_database():
        print("Warning: Could not create database backup")

    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Error: Could not connect to database")
        return False

    try:
        # Run migration steps
        steps = [
            ("Adding pricing fields to products table", add_pricing_fields_to_products),
            ("Creating pricing_rules table", create_pricing_rules_table),
            ("Creating pricing_history table", create_pricing_history_table),
            ("Migrating existing data", migrate_existing_data),
            ("Creating performance indexes", create_indexes),
            ("Verifying migration", verify_migration)
        ]

        for step_name, step_function in steps:
            print(f"\n{step_name}...")
            if not step_function(conn):
                print(f"Migration failed at step: {step_name}")
                return False

        print("\n✓ Enhanced pricing system database migration completed successfully!")
        return True

    except Exception as e:
        print(f"Migration failed with error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    if not success:
        print("\nMigration failed. Please check the errors above.")
        exit(1)
    else:
        print("\nMigration completed successfully!")
