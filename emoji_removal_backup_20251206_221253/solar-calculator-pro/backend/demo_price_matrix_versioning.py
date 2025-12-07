"""
Price Matrix Versioning System - Demo Script

This script demonstrates all features of the price matrix versioning system:
- Creating versions
- Approval workflow
- Version comparison
- Version rollback
- Version history
- Version migration
"""

from datetime import datetime
from backend.services.price_matrix_version_service import PriceMatrixVersionService
from backend.models.price_matrix_version_schemas import (
    PriceMatrixVersionCreate,
    PriceMatrixVersionUpdate,
    PriceMatrixVersionApprove,
    PriceMatrixVersionReject,
    PriceMatrixVersionRollback,
    PriceMatrixVersionCompare
)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_version_creation(service):
    """Demonstrate version creation"""
    print_section("1. VERSION CREATION")
    
    # Create first version
    print("Creating Version 1.0...")
    version1_data = PriceMatrixVersionCreate(
        matrix_id=1,
        version_name="Q1 2024 Pricing",
        description="Initial pricing for Q1 2024",
        matrix_data={
            "modules": {
                "5": {"10kWh": 15000, "15kWh": 18000, "20kWh": 21000},
                "10": {"10kWh": 25000, "15kWh": 28000, "20kWh": 31000},
                "15": {"10kWh": 35000, "15kWh": 38000, "20kWh": 41000}
            },
            "metadata": {
                "currency": "EUR",
                "last_updated": "2024-01-01",
                "author": "John Doe"
            }
        },
        metadata={"department": "Pricing", "region": "EU"}
    )
    
    version1 = service.create_version(version1_data, user_id=1)
    print(f"✅ Created Version {version1.version_number}: {version1.version_name}")
    print(f"   Status: {version1.status}")
    print(f"   Created by: User {version1.created_by}")
    print(f"   Created at: {version1.created_at}")
    
    # Create second version
    print("\nCreating Version 2.0...")
    version2_data = PriceMatrixVersionCreate(
        matrix_id=1,
        version_name="Q1 2024 Pricing - Updated",
        description="Updated pricing with market adjustments",
        matrix_data={
            "modules": {
                "5": {"10kWh": 16000, "15kWh": 19000, "20kWh": 22000},  # Increased
                "10": {"10kWh": 26000, "15kWh": 29000, "20kWh": 32000},  # Increased
                "15": {"10kWh": 36000, "15kWh": 39000, "20kWh": 42000},  # Increased
                "20": {"10kWh": 45000, "15kWh": 48000, "20kWh": 51000}   # New tier
            },
            "metadata": {
                "currency": "EUR",
                "last_updated": "2024-01-15",
                "author": "Jane Smith"
            }
        }
    )
    
    version2 = service.create_version(version2_data, user_id=1)
    print(f"✅ Created Version {version2.version_number}: {version2.version_name}")
    
    return version1, version2


def demo_approval_workflow(service, version):
    """Demonstrate approval workflow"""
    print_section("2. APPROVAL WORKFLOW")
    
    # Submit for approval
    print(f"Submitting Version {version.version_number} for approval...")
    version = service.submit_for_approval(version.id, user_id=1)
    print(f"✅ Status changed to: {version.status}")
    
    # Approve version
    print(f"\nApproving Version {version.version_number}...")
    approval_data = PriceMatrixVersionApprove(
        approval_notes="Pricing reviewed and approved. Ready for activation."
    )
    version = service.approve_version(version.id, approval_data, user_id=2)
    print(f"✅ Status changed to: {version.status}")
    print(f"   Approved by: User {version.approved_by}")
    print(f"   Approved at: {version.approved_at}")
    
    # Activate version
    print(f"\nActivating Version {version.version_number}...")
    version = service.activate_version(version.id, user_id=1)
    print(f"✅ Status changed to: {version.status}")
    print(f"   Is active: {version.is_active}")
    
    return version


def demo_version_comparison(service, version1, version2):
    """Demonstrate version comparison"""
    print_section("3. VERSION COMPARISON")
    
    print(f"Comparing Version {version1.version_number} vs Version {version2.version_number}...")
    
    comparison_data = PriceMatrixVersionCompare(
        version_a_id=version1.id,
        version_b_id=version2.id,
        include_details=True
    )
    
    comparison = service.compare_versions(comparison_data, user_id=1)
    
    print(f"\n📊 Comparison Summary:")
    print(f"   Total changes: {comparison.summary['total_changes']}")
    print(f"   Added: {comparison.summary['total_added']}")
    print(f"   Modified: {comparison.summary['total_modified']}")
    print(f"   Removed: {comparison.summary['total_removed']}")
    print(f"   Unchanged: {comparison.summary['total_unchanged']}")
    
    if comparison.differences['added']:
        print(f"\n➕ Added items:")
        for item in comparison.differences['added'][:3]:  # Show first 3
            print(f"   - {item['key']}: {item['new_value']}")
    
    if comparison.differences['modified']:
        print(f"\n✏️  Modified items:")
        for item in comparison.differences['modified'][:3]:  # Show first 3
            print(f"   - {item['key']}")
            print(f"     Old: {item['old_value']}")
            print(f"     New: {item['new_value']}")
    
    return comparison


def demo_version_update(service, version):
    """Demonstrate version update"""
    print_section("4. VERSION UPDATE")
    
    print(f"Updating Version {version.version_number} (draft status)...")
    
    update_data = PriceMatrixVersionUpdate(
        version_name=f"{version.version_name} - Revised",
        description="Updated description with additional notes"
    )
    
    updated_version = service.update_version(version.id, update_data, user_id=1)
    print(f"✅ Version updated successfully")
    print(f"   New name: {updated_version.version_name}")
    print(f"   Updated at: {updated_version.updated_at}")
    
    return updated_version


def demo_version_rollback(service, target_version):
    """Demonstrate version rollback"""
    print_section("5. VERSION ROLLBACK")
    
    print(f"Rolling back to Version {target_version.version_number}...")
    
    rollback_data = PriceMatrixVersionRollback(
        rollback_reason="Reverting to previous pricing due to market conditions",
        create_backup=True
    )
    
    result = service.rollback_to_version(target_version.id, rollback_data, user_id=1)
    
    print(f"✅ Rollback completed successfully")
    print(f"   Rolled back to version: {result['rolled_back_to_version']}")
    print(f"   Previous version: {result['previous_version']}")
    print(f"   Backup version ID: {result['backup_version_id']}")
    print(f"   Rollback time: {result['rollback_time']:.3f} seconds")
    
    # Verify active version
    active_version = service.get_active_version(matrix_id=1)
    print(f"\n   Current active version: {active_version.version_number}")
    
    return result


def demo_version_history(service, matrix_id):
    """Demonstrate version history"""
    print_section("6. VERSION HISTORY")
    
    print(f"Retrieving version history for Matrix {matrix_id}...")
    
    history = service.get_version_history(matrix_id=matrix_id, limit=10)
    
    print(f"\n📚 Version History:")
    print(f"   Total versions: {history['total_count']}")
    
    if history['active_version']:
        print(f"   Active version: {history['active_version'].version_number}")
    
    print(f"\n   All versions:")
    for version in history['versions']:
        status_icon = "🟢" if version.is_active else "⚪"
        print(f"   {status_icon} Version {version.version_number}: {version.version_name}")
        print(f"      Status: {version.status}")
        print(f"      Created: {version.created_at}")
    
    return history


def demo_version_changes(service, version):
    """Demonstrate version change tracking"""
    print_section("7. VERSION CHANGE TRACKING")
    
    print(f"Retrieving changes for Version {version.version_number}...")
    
    changes, total_count = service.get_version_changes(version.id, limit=10)
    
    print(f"\n📝 Change Log:")
    print(f"   Total changes: {total_count}")
    
    for change in changes:
        print(f"\n   {change.change_type.upper()}")
        print(f"   - Changed by: User {change.changed_by}")
        print(f"   - Changed at: {change.changed_at}")
        if change.change_description:
            print(f"   - Description: {change.change_description}")
        if change.field_name:
            print(f"   - Field: {change.field_name}")
            if change.old_value and change.new_value:
                print(f"     Old: {change.old_value}")
                print(f"     New: {change.new_value}")
    
    return changes


def demo_version_migration(service, from_version, to_version):
    """Demonstrate version migration"""
    print_section("8. VERSION MIGRATION")
    
    print(f"Migrating data from Version {from_version.version_number} to Version {to_version.version_number}...")
    
    # Define migration rules
    migration_rules = {
        "add_migration_timestamp": {
            "type": "add_default",
            "key": "migrated_at",
            "default": datetime.utcnow().isoformat()
        },
        "add_migration_source": {
            "type": "add_default",
            "key": "migrated_from_version",
            "default": from_version.version_number
        }
    }
    
    result = service.migrate_version_data(
        from_version_id=from_version.id,
        to_version_id=to_version.id,
        migration_rules=migration_rules,
        user_id=1
    )
    
    print(f"\n✅ Migration completed")
    print(f"   Success: {result['success']}")
    print(f"   From version: {result['from_version']}")
    print(f"   To version: {result['to_version']}")
    print(f"   Migrated records: {result['migrated_records']}")
    print(f"   Migration time: {result['migration_time']:.3f} seconds")
    
    if result['errors']:
        print(f"\n   ⚠️  Errors:")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result['warnings']:
        print(f"\n   ⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    return result


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  PRICE MATRIX VERSIONING SYSTEM - COMPLETE DEMO")
    print("=" * 80)
    
    # Initialize service (assuming db session is available)
    from backend.core.database import SessionLocal
    db = SessionLocal()
    service = PriceMatrixVersionService(db)
    
    try:
        # 1. Create versions
        version1, version2 = demo_version_creation(service)
        
        # 2. Demonstrate approval workflow
        approved_version = demo_approval_workflow(service, version1)
        
        # 3. Compare versions
        comparison = demo_version_comparison(service, version1, version2)
        
        # 4. Update a draft version
        updated_version = demo_version_update(service, version2)
        
        # 5. Approve and activate second version
        print_section("ACTIVATING SECOND VERSION")
        service.submit_for_approval(version2.id, user_id=1)
        service.approve_version(version2.id, PriceMatrixVersionApprove(), user_id=2)
        service.activate_version(version2.id, user_id=1)
        print("✅ Version 2 activated")
        
        # 6. Rollback to first version
        rollback_result = demo_version_rollback(service, version1)
        
        # 7. View version history
        history = demo_version_history(service, matrix_id=1)
        
        # 8. View version changes
        changes = demo_version_changes(service, version1)
        
        # 9. Demonstrate migration
        # Create a new version for migration demo
        version3_data = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Q2 2024 Pricing",
            description="New version for migration demo",
            matrix_data={}
        )
        version3 = service.create_version(version3_data, user_id=1)
        migration_result = demo_version_migration(service, version1, version3)
        
        print_section("DEMO COMPLETED SUCCESSFULLY")
        print("✅ All versioning features demonstrated successfully!")
        print("\nKey Features Demonstrated:")
        print("  1. ✅ Version creation with auto-incrementing version numbers")
        print("  2. ✅ Complete approval workflow (draft → pending → approved → active)")
        print("  3. ✅ Detailed version comparison with change tracking")
        print("  4. ✅ Version updates (draft versions only)")
        print("  5. ✅ Version rollback with automatic backup")
        print("  6. ✅ Complete version history tracking")
        print("  7. ✅ Detailed change log for each version")
        print("  8. ✅ Version migration with custom rules")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
