"""
Database Management Service

Provides comprehensive database management functionality including:
- Backup and restore operations
- Database optimization
- Data export in multiple formats
- Database statistics and health monitoring
"""

import os
import shutil
import sqlite3
import gzip
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManagementService:
    """Service for managing database operations"""
    
    def __init__(self, database_url: str):
        """
        Initialize database management service
        
        Args:
            database_url: SQLite database file path
        """
        self.database_url = database_url
        self.db_path = Path(database_url.replace('sqlite:///', ''))
        self.backup_dir = Path('backups/database')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir = Path('exports/database')
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== Backup Operations ====================
    
    def create_backup(self, description: str = "", compress: bool = True) -> Dict[str, Any]:
        """
        Create a database backup
        
        Args:
            description: Optional description for the backup
            compress: Whether to compress the backup file
            
        Returns:
            Dictionary with backup information
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.db"
            
            if compress:
                backup_name += ".gz"
            
            backup_path = self.backup_dir / backup_name
            
            # Create backup
            if compress:
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(self.db_path, backup_path)
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            
            # Create metadata file
            metadata = {
                'filename': backup_name,
                'created_at': datetime.now().isoformat(),
                'description': description,
                'compressed': compress,
                'size_bytes': backup_size,
                'size_mb': round(backup_size / (1024 * 1024), 2),
                'original_db': str(self.db_path),
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Database backup created: {backup_name}")
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_file in self.backup_dir.glob('backup_*.db*'):
            if backup_file.suffix == '.json':
                continue
            
            metadata_file = backup_file.with_suffix('.json')
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            else:
                # Create basic metadata if not exists
                backups.append({
                    'filename': backup_file.name,
                    'created_at': datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat(),
                    'size_bytes': backup_file.stat().st_size,
                    'size_mb': round(backup_file.stat().st_size / (1024 * 1024), 2),
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_filename: str, create_backup_before: bool = True) -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_filename: Name of the backup file to restore
            create_backup_before: Whether to create a backup before restoring
            
        Returns:
            Dictionary with restore operation result
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f'Backup file not found: {backup_filename}'
                }
            
            # Create safety backup before restore
            if create_backup_before:
                safety_backup = self.create_backup(
                    description="Auto-backup before restore",
                    compress=True
                )
                if not safety_backup['success']:
                    return {
                        'success': False,
                        'error': 'Failed to create safety backup before restore'
                    }
            
            # Restore from backup
            if backup_filename.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Database restored from: {backup_filename}")
            
            return {
                'success': True,
                'restored_from': backup_filename,
                'restored_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        Delete a backup file
        
        Args:
            backup_filename: Name of the backup file to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            backup_path = self.backup_dir / backup_filename
            metadata_path = backup_path.with_suffix('.json')
            
            if backup_path.exists():
                backup_path.unlink()
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.info(f"Backup deleted: {backup_filename}")
            
            return {
                'success': True,
                'deleted': backup_filename
            }
            
        except Exception as e:
            logger.error(f"Backup deletion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== Optimization Operations ====================
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Optimize database (VACUUM, ANALYZE, REINDEX)
        
        Returns:
            Dictionary with optimization results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get size before optimization
            size_before = self.db_path.stat().st_size
            
            # Run VACUUM to reclaim space
            cursor.execute('VACUUM')
            
            # Run ANALYZE to update statistics
            cursor.execute('ANALYZE')
            
            # Reindex all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f'REINDEX {table_name}')
            
            conn.commit()
            conn.close()
            
            # Get size after optimization
            size_after = self.db_path.stat().st_size
            space_saved = size_before - size_after
            
            logger.info(f"Database optimized. Space saved: {space_saved} bytes")
            
            return {
                'success': True,
                'size_before_mb': round(size_before / (1024 * 1024), 2),
                'size_after_mb': round(size_after / (1024 * 1024), 2),
                'space_saved_mb': round(space_saved / (1024 * 1024), 2),
                'optimized_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_integrity(self) -> Dict[str, Any]:
        """
        Check database integrity
        
        Returns:
            Dictionary with integrity check results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()
            
            conn.close()
            
            is_ok = result[0] == 'ok'
            
            return {
                'success': True,
                'integrity_ok': is_ok,
                'message': result[0],
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integrity check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== Statistics Operations ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get database size
            db_size = self.db_path.stat().st_size
            
            # Get table information
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()
            
            table_stats = []
            total_rows = 0
            
            for table in tables:
                table_name = table[0]
                
                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                # Get column count
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()
                column_count = len(columns)
                
                table_stats.append({
                    'name': table_name,
                    'rows': row_count,
                    'columns': column_count
                })
            
            # Get index information
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            index_count = cursor.fetchone()[0]
            
            # Get page size and page count
            cursor.execute('PRAGMA page_size')
            page_size = cursor.fetchone()[0]
            
            cursor.execute('PRAGMA page_count')
            page_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'database': {
                    'path': str(self.db_path),
                    'size_bytes': db_size,
                    'size_mb': round(db_size / (1024 * 1024), 2),
                    'page_size': page_size,
                    'page_count': page_count,
                },
                'tables': {
                    'count': len(tables),
                    'total_rows': total_rows,
                    'details': table_stats
                },
                'indexes': {
                    'count': index_count
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== Export Operations ====================
    
    def export_table_to_csv(self, table_name: str) -> Dict[str, Any]:
        """
        Export a table to CSV format
        
        Args:
            table_name: Name of the table to export
            
        Returns:
            Dictionary with export result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table data
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = [col[1] for col in cursor.fetchall()]
            
            conn.close()
            
            # Create export file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"{table_name}_{timestamp}.csv"
            export_path = self.export_dir / export_filename
            
            # Write CSV
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            logger.info(f"Table exported to CSV: {table_name}")
            
            return {
                'success': True,
                'table': table_name,
                'export_path': str(export_path),
                'rows_exported': len(rows),
                'exported_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_table_to_json(self, table_name: str) -> Dict[str, Any]:
        """
        Export a table to JSON format
        
        Args:
            table_name: Name of the table to export
            
        Returns:
            Dictionary with export result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get table data
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = [dict(row) for row in rows]
            
            conn.close()
            
            # Create export file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"{table_name}_{timestamp}.json"
            export_path = self.export_dir / export_filename
            
            # Write JSON
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Table exported to JSON: {table_name}")
            
            return {
                'success': True,
                'table': table_name,
                'export_path': str(export_path),
                'rows_exported': len(data),
                'exported_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"JSON export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_full_database(self, format: str = 'json') -> Dict[str, Any]:
        """
        Export entire database to specified format
        
        Args:
            format: Export format ('json' or 'sql')
            
        Returns:
            Dictionary with export result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"full_database_{timestamp}.{format}"
            export_path = self.export_dir / export_filename
            
            if format == 'sql':
                # Export as SQL dump
                with open(export_path, 'w', encoding='utf-8') as f:
                    for line in conn.iterdump():
                        f.write(f'{line}\n')
            
            elif format == 'json':
                # Export as JSON
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = cursor.fetchall()
                
                database_export = {}
                
                for table in tables:
                    table_name = table[0]
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(f'SELECT * FROM {table_name}')
                    rows = cursor.fetchall()
                    database_export[table_name] = [dict(row) for row in rows]
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(database_export, f, indent=2, default=str)
            
            conn.close()
            
            export_size = export_path.stat().st_size
            
            logger.info(f"Full database exported: {export_filename}")
            
            return {
                'success': True,
                'export_path': str(export_path),
                'format': format,
                'size_bytes': export_size,
                'size_mb': round(export_size / (1024 * 1024), 2),
                'exported_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Full database export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
