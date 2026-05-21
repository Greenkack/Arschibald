"""
Migration CLI Tool
Command-line interface for running migration scripts
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

from migration_manager import MigrationManager
from database_migrator import DatabaseMigrator
from settings_migrator import SettingsMigrator
from project_data_converter import ProjectDataConverter
from user_data_migrator import UserDataMigrator


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_full_migration(source_path: str, target_path: str):
    """Run complete migration process"""
    logger.info("=" * 80)
    logger.info("STARTING FULL MIGRATION")
    logger.info("=" * 80)
    logger.info(f"Source: {source_path}")
    logger.info(f"Target: {target_path}")
    logger.info("")
    
    manager = MigrationManager(Path(source_path), Path(target_path))
    report = manager.run_full_migration()
    
    # Print summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Status: {'SUCCESS' if report['success'] else 'FAILED'}")
    print(f"Started: {report['started_at']}")
    print(f"Completed: {report['completed_at']}")
    print(f"Backup: {report['backup_path']}")
    print("")
    
    for step in report['steps']:
        status = "✓" if step['success'] else "✗"
        print(f"{status} {step['step']}: {step['message']}")
    
    if report['errors']:
        print("\nErrors:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if not report['success'] and 'rollback' in report:
        print(f"\nRollback: {'SUCCESS' if report['rollback']['success'] else 'FAILED'}")
        print(f"  {report['rollback']['message']}")
    
    print("\n" + "=" * 80)
    
    return 0 if report['success'] else 1


def run_database_migration(source_db: str, target_db: str):
    """Run database migration only"""
    logger.info("Running database migration")
    
    migrator = DatabaseMigrator(Path(source_db), Path(target_db))
    result = migrator.migrate()
    
    print(f"\nDatabase Migration: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Tables migrated: {result['tables_migrated']}")
    print(f"Records migrated: {result['records_migrated']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Validate
    validation = migrator.validate_migration()
    print(f"\nValidation: {'PASSED' if validation['success'] else 'FAILED'}")
    
    return 0 if result['success'] and validation['success'] else 1


def run_settings_migration(source_path: str, target_path: str):
    """Run settings migration only"""
    logger.info("Running settings migration")
    
    migrator = SettingsMigrator(Path(source_path), Path(target_path))
    result = migrator.migrate()
    
    print(f"\nSettings Migration: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Files migrated: {result['files_migrated']}")
    print(f"Settings migrated: {result['settings_migrated']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Validate
    validation = migrator.validate_migration()
    print(f"\nValidation: {'PASSED' if validation['success'] else 'FAILED'}")
    
    return 0 if result['success'] and validation['success'] else 1


def run_project_conversion(source_path: str, target_path: str):
    """Run project data conversion only"""
    logger.info("Running project data conversion")
    
    converter = ProjectDataConverter(Path(source_path), Path(target_path))
    result = converter.convert()
    
    print(f"\nProject Data Conversion: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Projects converted: {result['projects_converted']}")
    print(f"Files converted: {result['files_converted']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Validate
    validation = converter.validate_conversion()
    print(f"\nValidation: {'PASSED' if validation['success'] else 'FAILED'}")
    
    return 0 if result['success'] and validation['success'] else 1


def run_user_migration(source_path: str, target_path: str):
    """Run user data migration only"""
    logger.info("Running user data migration")
    
    migrator = UserDataMigrator(Path(source_path), Path(target_path))
    result = migrator.migrate()
    
    print(f"\nUser Data Migration: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Users migrated: {result['users_migrated']}")
    print(f"Preferences migrated: {result['preferences_migrated']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Validate
    validation = migrator.validate_migration()
    print(f"\nValidation: {'PASSED' if validation['success'] else 'FAILED'}")
    
    return 0 if result['success'] and validation['success'] else 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Migration tool for Streamlit to Electron migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full migration
  python migrate_cli.py full /path/to/streamlit/data /path/to/electron/data
  
  # Run database migration only
  python migrate_cli.py database /path/to/source.db /path/to/target.db
  
  # Run settings migration only
  python migrate_cli.py settings /path/to/source/settings /path/to/target/settings
  
  # Run project data conversion only
  python migrate_cli.py projects /path/to/source/projects /path/to/target/projects
  
  # Run user data migration only
  python migrate_cli.py users /path/to/source/users /path/to/target/users
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Migration command')
    
    # Full migration
    full_parser = subparsers.add_parser('full', help='Run complete migration')
    full_parser.add_argument('source', help='Source data path')
    full_parser.add_argument('target', help='Target data path')
    
    # Database migration
    db_parser = subparsers.add_parser('database', help='Run database migration only')
    db_parser.add_argument('source_db', help='Source database path')
    db_parser.add_argument('target_db', help='Target database path')
    
    # Settings migration
    settings_parser = subparsers.add_parser('settings', help='Run settings migration only')
    settings_parser.add_argument('source', help='Source settings path')
    settings_parser.add_argument('target', help='Target settings path')
    
    # Project conversion
    projects_parser = subparsers.add_parser('projects', help='Run project data conversion only')
    projects_parser.add_argument('source', help='Source projects path')
    projects_parser.add_argument('target', help='Target projects path')
    
    # User migration
    users_parser = subparsers.add_parser('users', help='Run user data migration only')
    users_parser.add_argument('source', help='Source users path')
    users_parser.add_argument('target', help='Target users path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'full':
            return run_full_migration(args.source, args.target)
        elif args.command == 'database':
            return run_database_migration(args.source_db, args.target_db)
        elif args.command == 'settings':
            return run_settings_migration(args.source, args.target)
        elif args.command == 'projects':
            return run_project_conversion(args.source, args.target)
        elif args.command == 'users':
            return run_user_migration(args.source, args.target)
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        print(f"\nERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
