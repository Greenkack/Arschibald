"""
Demo script for System Maintenance Tools

This script demonstrates all maintenance operations:
- Database maintenance
- Cache management
- Log cleanup
- Temp file cleanup
- System diagnostics
- Repair tools
"""

import asyncio
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.maintenance_service import MaintenanceService
from backend.models.maintenance_schemas import (
    DatabaseMaintenanceRequest,
    CacheClearRequest,
    LogCleanupRequest,
    TempFileCleanupRequest,
    DiagnosticRequest,
    RepairRequest,
    RepairOperation
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_database_maintenance(service: MaintenanceService):
    """Demonstrate database maintenance"""
    print_section("DATABASE MAINTENANCE")
    
    # Vacuum database
    print("1. Vacuuming database...")
    result = service.perform_database_maintenance(
        DatabaseMaintenanceRequest(operation="vacuum", full=False),
        user="demo_user"
    )
    print(f"    Status: {result.status}")
    print(f"    Tables processed: {len(result.tables_processed)}")
    print(f"    Duration: {result.duration_seconds:.2f}s")
    
    # Analyze database
    print("\n2. Analyzing database...")
    result = service.perform_database_maintenance(
        DatabaseMaintenanceRequest(operation="analyze"),
        user="demo_user"
    )
    print(f"    Status: {result.status}")
    print(f"    Tables processed: {len(result.tables_processed)}")
    
    # Optimize database
    print("\n3. Optimizing database...")
    result = service.perform_database_maintenance(
        DatabaseMaintenanceRequest(operation="optimize"),
        user="demo_user"
    )
    print(f"    Status: {result.status}")
    print(f"    Tables processed: {len(result.tables_processed)}")


def demo_cache_management(service: MaintenanceService):
    """Demonstrate cache management"""
    print_section("CACHE MANAGEMENT")
    
    # Get cache stats
    print("1. Getting cache statistics...")
    stats = service.get_cache_stats()
    print(f"    Total entries: {stats.total_entries}")
    print(f"    Total size: {stats.total_size_mb} MB")
    print(f"    Hit rate: {stats.hit_rate}")
    print(f"    Cache types: {stats.cache_types}")
    
    # Clear unused cache
    print("\n2. Clearing unused cache entries...")
    result = service.clear_cache(
        CacheClearRequest(unused_only=True),
        user="demo_user"
    )
    print(f"    Entries cleared: {result.entries_cleared}")
    print(f"    Size freed: {result.size_freed_mb} MB")
    
    # Clear old cache
    print("\n3. Clearing cache older than 7 days...")
    result = service.clear_cache(
        CacheClearRequest(older_than_days=7),
        user="demo_user"
    )
    print(f"    Entries cleared: {result.entries_cleared}")
    print(f"    Size freed: {result.size_freed_mb} MB")


def demo_log_management(service: MaintenanceService):
    """Demonstrate log management"""
    print_section("LOG MANAGEMENT")
    
    # Get log stats
    print("1. Getting log statistics...")
    stats = service.get_log_stats()
    print(f"    Total log files: {stats.total_log_files}")
    print(f"    Total size: {stats.total_size_mb} MB")
    print(f"    Log types: {stats.log_types}")
    print(f"    Errors (24h): {stats.error_count_24h}")
    print(f"    Warnings (24h): {stats.warning_count_24h}")
    
    # Cleanup old logs
    print("\n2. Cleaning up logs older than 30 days...")
    result = service.cleanup_logs(
        LogCleanupRequest(older_than_days=30, compress_before_delete=True),
        user="demo_user"
    )
    print(f"    Files deleted: {result.files_deleted}")
    print(f"    Files compressed: {result.files_compressed}")
    print(f"    Size freed: {result.size_freed_mb} MB")


def demo_temp_file_cleanup(service: MaintenanceService):
    """Demonstrate temp file cleanup"""
    print_section("TEMP FILE CLEANUP")
    
    # Get temp file stats
    print("1. Getting temp file statistics...")
    stats = service.get_temp_file_stats()
    print(f"    Total files: {stats.total_files}")
    print(f"    Total size: {stats.total_size_mb} MB")
    print(f"    File types: {stats.file_types}")
    print(f"    Files to delete: {stats.files_to_delete}")
    
    # Cleanup old temp files
    print("\n2. Cleaning up temp files older than 24 hours...")
    result = service.cleanup_temp_files(
        TempFileCleanupRequest(older_than_hours=24),
        user="demo_user"
    )
    print(f"    Files deleted: {result.files_deleted}")
    print(f"    Size freed: {result.size_freed_mb} MB")


def demo_system_diagnostics(service: MaintenanceService):
    """Demonstrate system diagnostics"""
    print_section("SYSTEM DIAGNOSTICS")
    
    # Run full diagnostics
    print("Running comprehensive system diagnostics...\n")
    result = service.run_diagnostics(
        DiagnosticRequest(detailed=True)
    )
    
    print(f"Overall Status: {result.overall_status.value.upper()}")
    print(f"\nSummary:")
    print(f"  - Total diagnostics: {result.summary['total_diagnostics']}")
    print(f"  - Healthy: {result.summary['healthy']}")
    print(f"  - Warnings: {result.summary['warnings']}")
    print(f"  - Critical: {result.summary['critical']}")
    
    print("\nDetailed Results:")
    for diag in result.diagnostics:
        status_icon = "" if diag.status.value == "healthy" else "" if diag.status.value == "warning" else ""
        print(f"\n{status_icon} {diag.diagnostic_type.upper()}")
        print(f"   Status: {diag.status.value}")
        print(f"   Metrics: {diag.metrics}")
        if diag.issues:
            print(f"   Issues: {', '.join(diag.issues)}")
        if diag.recommendations:
            print(f"   Recommendations: {', '.join(diag.recommendations)}")


def demo_repair_tools(service: MaintenanceService):
    """Demonstrate repair tools"""
    print_section("REPAIR TOOLS")
    
    # Dry run repair
    print("1. Running repair in dry-run mode (no changes)...")
    result = service.perform_repair(
        RepairRequest(
            operation=RepairOperation.RESET_CACHE,
            dry_run=True,
            backup_first=False
        ),
        user="demo_user"
    )
    print(f"    Operation: {result.operation.value}")
    print(f"    Status: {result.status}")
    print(f"    Items to repair: {result.items_repaired}")
    
    # Rebuild indexes
    print("\n2. Rebuilding database indexes...")
    result = service.perform_repair(
        RepairRequest(
            operation=RepairOperation.REBUILD_INDEX,
            dry_run=False,
            backup_first=True
        ),
        user="demo_user"
    )
    print(f"    Operation: {result.operation.value}")
    print(f"    Status: {result.status}")
    print(f"    Items repaired: {result.items_repaired}")
    if result.backup_created:
        print(f"    Backup created: {result.backup_created}")


def demo_maintenance_logs(service: MaintenanceService):
    """Demonstrate maintenance logs"""
    print_section("MAINTENANCE LOGS")
    
    # Get recent logs
    print("Recent maintenance operations:\n")
    logs = service.get_maintenance_logs(limit=10)
    
    for log in logs:
        status_icon = "" if log.status == "success" else "" if log.status == "failed" else "⏳"
        print(f"{status_icon} {log.operation_type.upper()}: {log.operation_name}")
        print(f"   Started: {log.started_at}")
        if log.completed_at:
            print(f"   Completed: {log.completed_at}")
            print(f"   Duration: {log.duration_seconds:.2f}s")
        print(f"   Performed by: {log.performed_by}")
        if log.error_message:
            print(f"   Error: {log.error_message}")
        print()


def main():
    """Run all maintenance demos"""
    print("\n" + "=" * 80)
    print("  SYSTEM MAINTENANCE TOOLS - COMPREHENSIVE DEMO")
    print("=" * 80)
    
    # Create database session
    db = SessionLocal()
    service = MaintenanceService(db)
    
    try:
        # Run all demos
        demo_database_maintenance(service)
        demo_cache_management(service)
        demo_log_management(service)
        demo_temp_file_cleanup(service)
        demo_system_diagnostics(service)
        demo_repair_tools(service)
        demo_maintenance_logs(service)
        
        print_section("DEMO COMPLETED")
        print(" All maintenance operations demonstrated successfully!")
        print("\nNext steps:")
        print("  1. Review the maintenance logs")
        print("  2. Schedule regular maintenance tasks")
        print("  3. Set up monitoring and alerts")
        print("  4. Configure automated cleanup policies")
        
    except Exception as e:
        print(f"\n Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
