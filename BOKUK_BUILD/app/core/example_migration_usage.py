"""Example Usage of Database Migration System

This file demonstrates how to use the database migration system
for common scenarios.
"""

from core.migration_templates import MigrationTemplates, generate_migration_code
from core.migration_manager import (
    create_migration,
    get_migration_manager,
    get_migration_status,
    migrate,
)
from core.database import init_database
import os
import tempfile

# Set up temporary database for examples
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"


def example_1_initialize_with_migrations():
    """Example 1: Initialize database with automatic migrations"""
    print("\n=== Example 1: Initialize Database with Migrations ===")

    # Initialize database and run pending migrations
    init_database(auto_migrate=True)

    print("✓ Database initialized with migrations")


def example_2_check_migration_status():
    """Example 2: Check migration status"""
    print("\n=== Example 2: Check Migration Status ===")

    status = get_migration_status()

    print(f"Current Revision: {status['current_revision']}")
    print(f"Head Revision: {status['head_revision']}")
    print(f"Has Pending: {status['has_pending']}")
    print(f"Pending Migrations: {status['pending_migrations']}")


def example_3_run_migrations():
    """Example 3: Run migrations manually"""
    print("\n=== Example 3: Run Migrations Manually ===")

    # Run all pending migrations
    success = migrate(auto_run=True)

    if success:
        print("✓ Migrations completed successfully")
    else:
        print("✗ Migrations failed")


def example_4_create_migration():
    """Example 4: Create a new migration"""
    print("\n=== Example 4: Create New Migration ===")

    # Create migration with auto-detection
    try:
        revision = create_migration(
            message="Add user profile fields",
            autogenerate=True,
        )
        print(f"✓ Migration created: {revision}")
    except Exception as e:
        print(f"Note: {e}")
        print("(This is expected if no model changes detected)")


def example_5_use_migration_templates():
    """Example 5: Use migration templates"""
    print("\n=== Example 5: Use Migration Templates ===")

    # Generate code for adding a column
    print("\n--- Add Column Template ---")
    code = generate_migration_code(
        "add_column",
        table_name="users",
        column_name="phone",
        column_type="sa.String(20)",
        nullable=True,
        comment="User phone number",
    )
    print("Upgrade code:")
    print(code["upgrade"])

    # Generate code for adding an index
    print("\n--- Add Index Template ---")
    code = generate_migration_code(
        "add_index",
        table_name="users",
        column_names=["email"],
        unique=True,
    )
    print("Upgrade code:")
    print(code["upgrade"])

    # Generate code for creating a table
    print("\n--- Create Table Template ---")
    columns = [
        {"name": "username", "type": "sa.String(100)", "nullable": False},
        {"name": "email", "type": "sa.String(255)", "nullable": False},
        {"name": "age", "type": "sa.Integer()", "nullable": True, "default": 0},
    ]
    code = generate_migration_code(
        "create_table",
        table_name="profiles",
        columns=columns,
        with_timestamps=True,
        with_soft_delete=True,
    )
    print("Upgrade code:")
    print(code["upgrade"][:200] + "...")


def example_6_migration_manager_api():
    """Example 6: Use MigrationManager API"""
    print("\n=== Example 6: MigrationManager API ===")

    manager = get_migration_manager()

    # Get current revision
    current = manager.get_current_revision()
    print(f"Current Revision: {current}")

    # Get head revision
    head = manager.get_head_revision()
    print(f"Head Revision: {head}")

    # Check for pending migrations
    pending = manager.get_pending_migrations()
    print(f"Pending Migrations: {len(pending)}")

    # Get migration history
    history = manager.get_migration_history()
    print(f"Total Migrations: {len(history)}")

    # Verify migrations
    results = manager.verify_migrations()
    print(f"Verification Status: {results['status']}")
    if results["issues"]:
        print(f"Issues: {results['issues']}")


def example_7_rollback_migration():
    """Example 7: Rollback migrations"""
    print("\n=== Example 7: Rollback Migrations ===")

    # Note: This is a demonstration - actual rollback should be done carefully
    print("Rollback operations:")
    print("- rollback(target_revision='-1')  # Rollback one migration")
    print("- rollback(target_revision='abc123')  # Rollback to specific revision")
    print("- rollback(target_revision='base')  # Rollback all migrations")
    print("\nNote: Rollback includes safety checks in production")


def example_8_all_migration_templates():
    """Example 8: Demonstrate all migration templates"""
    print("\n=== Example 8: All Migration Templates ===")

    templates = MigrationTemplates()

    # 1. Add Column
    print("\n1. Add Column:")
    result = templates.add_column_template(
        table_name="users",
        column_name="bio",
        column_type="sa.Text()",
        nullable=True,
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 2. Add Index
    print("\n2. Add Index:")
    result = templates.add_index_template(
        table_name="users", column_names=["username"], unique=True
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 3. Add Foreign Key
    print("\n3. Add Foreign Key:")
    result = templates.add_foreign_key_template(
        table_name="posts",
        column_name="user_id",
        ref_table="users",
        ondelete="CASCADE",
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 4. Create Table
    print("\n4. Create Table:")
    result = templates.create_table_template(
        table_name="comments",
        columns=[{"name": "content", "type": "sa.Text()"}],
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 5. Rename Column
    print("\n5. Rename Column:")
    result = templates.rename_column_template(
        table_name="users", old_name="name", new_name="full_name"
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 6. Add Check Constraint
    print("\n6. Add Check Constraint:")
    result = templates.add_check_constraint_template(
        table_name="users",
        constraint_name="check_age",
        condition="age >= 18",
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")

    # 7. Data Migration
    print("\n7. Data Migration:")
    result = templates.data_migration_template(
        description="Set default status",
        upgrade_sql="UPDATE users SET status = 'active'",
    )
    print(f"   Upgrade: {result['upgrade'][:80]}...")


def example_9_zero_downtime_migration():
    """Example 9: Zero-downtime migration pattern"""
    print("\n=== Example 9: Zero-Downtime Migration Pattern ===")

    print("\nScenario: Rename 'name' column to 'full_name'")
    print("\nStep 1: Add new column")
    code = generate_migration_code(
        "add_column",
        table_name="users",
        column_name="full_name",
        column_type="sa.String(255)",
        nullable=True,
    )
    print(code["upgrade"][:100] + "...")

    print("\nStep 2: Copy data (data migration)")
    code = generate_migration_code(
        "data_migration",
        description="Copy name to full_name",
        upgrade_sql="UPDATE users SET full_name = name WHERE full_name IS NULL",
    )
    print(code["upgrade"][:100] + "...")

    print("\nStep 3: Update application code to use 'full_name'")
    print("(Deploy application update)")

    print("\nStep 4: Remove old column")
    print("op.drop_column('users', 'name')")


def example_10_migration_verification():
    """Example 10: Verify migration integrity"""
    print("\n=== Example 10: Migration Verification ===")

    manager = get_migration_manager()
    results = manager.verify_migrations()

    print(f"Status: {results['status']}")
    print(f"Current Revision: {results['current_revision']}")
    print(f"Head Revision: {results['head_revision']}")
    print(f"Pending Migrations: {len(results['pending_migrations'])}")

    if results["issues"]:
        print("\nIssues Found:")
        for issue in results["issues"]:
            print(f"  - {issue}")
    else:
        print("\n✓ No issues found")


def run_all_examples():
    """Run all examples"""
    print("=" * 70)
    print("DATABASE MIGRATION SYSTEM - EXAMPLE USAGE")
    print("=" * 70)

    try:
        example_1_initialize_with_migrations()
        example_2_check_migration_status()
        example_3_run_migrations()
        example_4_create_migration()
        example_5_use_migration_templates()
        example_6_migration_manager_api()
        example_7_rollback_migration()
        example_8_all_migration_templates()
        example_9_zero_downtime_migration()
        example_10_migration_verification()

        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
