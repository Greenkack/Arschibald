"""
Multi-Database Support Demo
Demonstrates database abstraction and migration capabilities.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database_abstraction import (
    DatabaseType,
    DatabaseConfig,
    DatabaseManager,
    DatabaseFactory
)
from services.database_migration_service import DatabaseMigrationService
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DemoUser(Base):
    """Demo user model"""
    __tablename__ = "demo_users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class DemoProject(Base):
    """Demo project model"""
    __tablename__ = "demo_projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(500))
    budget = Column(Float)
    created_at = Column(DateTime, default=datetime.now)


def demo_sqlite():
    """Demonstrate SQLite database operations"""
    print("\n" + "="*60)
    print("DEMO 1: SQLite Database Operations")
    print("="*60)
    
    # Create configuration
    config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./demo_sqlite.db",
        echo=True
    )
    
    # Create manager
    manager = DatabaseManager(config)
    manager.adapter.Base = Base
    
    print("\n1. Connecting to SQLite database...")
    manager.connect()
    
    print("\n2. Creating tables...")
    manager.create_tables()
    
    print("\n3. Inserting sample data...")
    session = manager.get_session()
    
    # Insert users
    users = [
        DemoUser(name="John Doe", email="john@example.com"),
        DemoUser(name="Jane Smith", email="jane@example.com"),
        DemoUser(name="Bob Johnson", email="bob@example.com")
    ]
    session.add_all(users)
    
    # Insert projects
    projects = [
        DemoProject(name="Solar Installation A", description="Residential solar project", budget=15000.00),
        DemoProject(name="Solar Installation B", description="Commercial solar project", budget=50000.00),
        DemoProject(name="Heat Pump Installation", description="Heat pump upgrade", budget=12000.00)
    ]
    session.add_all(projects)
    
    session.commit()
    
    print("\n4. Querying data...")
    users = session.query(DemoUser).all()
    print(f"\nFound {len(users)} users:")
    for user in users:
        print(f"  - {user.name} ({user.email})")
    
    projects = session.query(DemoProject).all()
    print(f"\nFound {len(projects)} projects:")
    for project in projects:
        print(f"  - {project.name}: ${project.budget:,.2f}")
    
    print("\n5. Executing raw SQL...")
    result = manager.execute_raw_sql("SELECT COUNT(*) as count FROM demo_users")
    print(f"User count from raw SQL: {result[0][0]}")
    
    print("\n6. Creating backup...")
    backup_path = "./demo_sqlite_backup.db"
    if manager.backup(backup_path):
        print(f"Backup created: {backup_path}")
    
    session.close()
    manager.disconnect()
    
    print("\n SQLite demo completed successfully!")


def demo_database_types():
    """Demonstrate different database type configurations"""
    print("\n" + "="*60)
    print("DEMO 2: Database Type Configurations")
    print("="*60)
    
    # SQLite
    print("\n1. SQLite Configuration:")
    sqlite_config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./app.db"
    )
    print(f"   Connection string: {sqlite_config.get_connection_string()}")
    
    # PostgreSQL
    print("\n2. PostgreSQL Configuration:")
    pg_config = DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="solar_calculator",
        username="postgres",
        password="password",
        pool_size=10,
        max_overflow=20
    )
    print(f"   Connection string: {pg_config.get_connection_string()}")
    print(f"   Pool size: {pg_config.pool_size}")
    print(f"   Max overflow: {pg_config.max_overflow}")
    
    # MySQL
    print("\n3. MySQL Configuration:")
    mysql_config = DatabaseConfig(
        db_type=DatabaseType.MYSQL,
        host="localhost",
        port=3306,
        database="solar_calculator",
        username="root",
        password="password",
        pool_size=5,
        max_overflow=10
    )
    print(f"   Connection string: {mysql_config.get_connection_string()}")
    print(f"   Pool size: {mysql_config.pool_size}")
    
    print("\n Configuration demo completed!")


def demo_migration():
    """Demonstrate database migration"""
    print("\n" + "="*60)
    print("DEMO 3: Database Migration")
    print("="*60)
    
    # Create source database (SQLite)
    print("\n1. Setting up source database (SQLite)...")
    source_config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./demo_source.db"
    )
    
    source_manager = DatabaseManager(source_config)
    source_manager.adapter.Base = Base
    source_manager.connect()
    source_manager.create_tables()
    
    # Add sample data
    session = source_manager.get_session()
    for i in range(100):
        session.add(DemoUser(
            name=f"User {i}",
            email=f"user{i}@example.com"
        ))
    session.commit()
    session.close()
    source_manager.disconnect()
    
    print(f"   Created source database with 100 users")
    
    # Create target database (SQLite for demo)
    print("\n2. Setting up target database (SQLite)...")
    target_config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./demo_target.db"
    )
    
    # Create migration service
    print("\n3. Creating migration service...")
    migration_service = DatabaseMigrationService(source_config, target_config)
    
    # Validate migration
    print("\n4. Validating migration...")
    validation = migration_service.validate_migration()
    if validation["valid"]:
        print("    Validation passed")
        if validation["warnings"]:
            print(f"     Warnings: {validation['warnings']}")
    else:
        print(f"    Validation failed: {validation['errors']}")
        return
    
    # Perform migration
    print("\n5. Performing migration...")
    progress = migration_service.migrate_all(batch_size=25)
    
    print(f"\n   Migration Results:")
    print(f"   - Total tables: {progress.total_tables}")
    print(f"   - Completed tables: {progress.completed_tables}")
    print(f"   - Total rows: {progress.total_rows}")
    print(f"   - Migrated rows: {progress.migrated_rows}")
    print(f"   - Progress: {progress.get_progress_percentage():.2f}%")
    
    if progress.errors:
        print(f"   - Errors: {progress.errors}")
    
    # Verify migration
    print("\n6. Verifying migration...")
    verification = migration_service.verify_migration()
    
    if verification["success"]:
        print("    Verification passed")
        print(f"   - Tables verified: {verification['tables_verified']}")
        print(f"   - Tables failed: {verification['tables_failed']}")
    else:
        print("    Verification failed")
        print(f"   - Mismatches: {verification['row_count_mismatches']}")
    
    print("\n Migration demo completed!")


def demo_context_manager():
    """Demonstrate context manager usage"""
    print("\n" + "="*60)
    print("DEMO 4: Context Manager Usage")
    print("="*60)
    
    config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./demo_context.db"
    )
    
    print("\n1. Using context manager...")
    with DatabaseManager(config) as manager:
        manager.adapter.Base = Base
        manager.create_tables()
        
        session = manager.get_session()
        session.add(DemoUser(name="Context User", email="context@example.com"))
        session.commit()
        
        users = session.query(DemoUser).all()
        print(f"   Found {len(users)} users")
        
        session.close()
    
    print("    Context manager automatically disconnected")
    print("\n Context manager demo completed!")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n" + "="*60)
    print("DEMO 5: Error Handling")
    print("="*60)
    
    # Test invalid configuration
    print("\n1. Testing invalid SQLite path...")
    try:
        config = DatabaseConfig(db_type=DatabaseType.SQLITE)
        config.get_connection_string()
    except ValueError as e:
        print(f"    Caught expected error: {e}")
    
    # Test invalid PostgreSQL configuration
    print("\n2. Testing invalid PostgreSQL configuration...")
    try:
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost"
        )
        config.get_connection_string()
    except ValueError as e:
        print(f"    Caught expected error: {e}")
    
    # Test connection to non-existent database
    print("\n3. Testing connection to non-existent database...")
    try:
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="/nonexistent/path/database.db"
        )
        manager = DatabaseManager(config)
        manager.connect()
    except Exception as e:
        print(f"    Caught expected error: {type(e).__name__}")
    
    print("\n Error handling demo completed!")


def cleanup():
    """Clean up demo files"""
    print("\n" + "="*60)
    print("Cleaning up demo files...")
    print("="*60)
    
    demo_files = [
        "./demo_sqlite.db",
        "./demo_sqlite_backup.db",
        "./demo_source.db",
        "./demo_target.db",
        "./demo_context.db"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
    
    print("\n Cleanup completed!")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("MULTI-DATABASE SUPPORT DEMONSTRATION")
    print("="*60)
    print("\nThis demo showcases the multi-database support system:")
    print("  1. SQLite database operations")
    print("  2. Database type configurations")
    print("  3. Database migration")
    print("  4. Context manager usage")
    print("  5. Error handling")
    
    try:
        # Run demos
        demo_sqlite()
        demo_database_types()
        demo_migration()
        demo_context_manager()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY! ")
        print("="*60)
        
    except Exception as e:
        print(f"\n Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        cleanup()


if __name__ == "__main__":
    main()
