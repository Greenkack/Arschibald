"""
Database Service Wrapper

This service wraps the existing database.py functionality and provides:
- CRUD operations for all entities
- Query optimization with indexes
- Transaction management
- Database backup utilities
- Connection pooling
- Error handling and logging

Requirements: 1.2, 5.1, 8.4
"""

import sqlite3
import json
import os
import shutil
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager
from functools import wraps
import logging

# Import existing database functions
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as legacy_db

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database errors"""
    pass


class ConnectionError(DatabaseError):
    """Database connection error"""
    pass


class TransactionError(DatabaseError):
    """Transaction error"""
    pass


class QueryError(DatabaseError):
    """Query execution error"""
    pass


def handle_db_errors(func: Callable) -> Callable:
    """Decorator for handling database errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper


class DatabaseService:
    """
    Comprehensive database service wrapper
    
    Wraps existing database.py functionality and provides:
    - Connection management with pooling
    - CRUD operations for all entities
    - Transaction management
    - Query optimization
    - Backup and restore utilities
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database service"""
        self.db_path = db_path or legacy_db.DB_PATH
        self.data_dir = os.path.dirname(self.db_path)
        self._connection_pool: List[sqlite3.Connection] = []
        self._pool_size = 5
        self._initialize_pool()
        logger.info(f"DatabaseService initialized with path: {self.db_path}")
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self._pool_size):
            conn = self._create_connection()
            if conn:
                self._connection_pool.append(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool (context manager)"""
        conn = None
        try:
            if self._connection_pool:
                conn = self._connection_pool.pop()
            else:
                conn = self._create_connection()
            
            if not conn:
                raise ConnectionError("Failed to get database connection")
            
            yield conn
        finally:
            if conn and len(self._connection_pool) < self._pool_size:
                self._connection_pool.append(conn)
            elif conn:
                conn.close()
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back: {e}")
                raise TransactionError(f"Transaction failed: {str(e)}")
    
    # ==================== CRUD Operations ====================
    
    @handle_db_errors
    def create(self, table: str, data: Dict[str, Any]) -> int:
        """
        Generic create operation
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
            
        Returns:
            ID of created record
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid
    
    @handle_db_errors
    def read(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """
        Generic read operation
        
        Args:
            table: Table name
            id: Record ID
            
        Returns:
            Dictionary of record data or None
        """
        query = f"SELECT * FROM {table} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @handle_db_errors
    def read_all(self, table: str, filters: Optional[Dict[str, Any]] = None,
                 order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generic read all operation with filtering
        
        Args:
            table: Table name
            filters: Optional dictionary of column:value filters
            order_by: Optional ORDER BY clause
            limit: Optional LIMIT value
            
        Returns:
            List of record dictionaries
        """
        query = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            where_clauses = [f"{col} = ?" for col in filters.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params = list(filters.values())
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    @handle_db_errors
    def update(self, table: str, id: int, data: Dict[str, Any]) -> bool:
        """
        Generic update operation
        
        Args:
            table: Table name
            id: Record ID
            data: Dictionary of column:value pairs to update
            
        Returns:
            True if successful
        """
        set_clauses = [f"{col} = ?" for col in data.keys()]
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE id = ?"
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (*data.values(), id))
            return cursor.rowcount > 0
    
    @handle_db_errors
    def delete(self, table: str, id: int) -> bool:
        """
        Generic delete operation
        
        Args:
            table: Table name
            id: Record ID
            
        Returns:
            True if successful
        """
        query = f"DELETE FROM {table} WHERE id = ?"
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id))
            return cursor.rowcount > 0
    
    @handle_db_errors
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute custom query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    @handle_db_errors
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute query with multiple parameter sets
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    # ==================== Query Optimization ====================
    
    @handle_db_errors
    def create_index(self, table: str, columns: List[str], unique: bool = False) -> bool:
        """
        Create index for query optimization
        
        Args:
            table: Table name
            columns: List of column names
            unique: Whether index should be unique
            
        Returns:
            True if successful
        """
        index_name = f"idx_{table}_{'_'.join(columns)}"
        unique_clause = "UNIQUE" if unique else ""
        columns_str = ', '.join(columns)
        query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {table}({columns_str})"
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            logger.info(f"Created index {index_name} on {table}({columns_str})")
            return True
    
    @handle_db_errors
    def analyze_table(self, table: str) -> Dict[str, Any]:
        """
        Analyze table for query optimization
        
        Args:
            table: Table name
            
        Returns:
            Dictionary with analysis results
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Get index info
            cursor.execute(f"PRAGMA index_list({table})")
            indexes = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            row_count = cursor.fetchone()['count']
            
            return {
                'table': table,
                'columns': [dict(col) for col in columns],
                'indexes': [dict(idx) for idx in indexes],
                'row_count': row_count
            }
    
    @handle_db_errors
    def optimize_database(self) -> bool:
        """
        Optimize database (VACUUM and ANALYZE)
        
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            logger.info("Database optimized (VACUUM and ANALYZE)")
            return True
    
    # ==================== Backup and Restore ====================
    
    @handle_db_errors
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create database backup
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            Path to backup file
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.data_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")
        
        # Close all connections before backup
        for conn in self._connection_pool:
            conn.close()
        self._connection_pool.clear()
        
        # Perform backup
        shutil.copy2(self.db_path, backup_path)
        
        # Reinitialize pool
        self._initialize_pool()
        
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    
    @handle_db_errors
    def restore(self, backup_path: str) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        if not os.path.exists(backup_path):
            raise DatabaseError(f"Backup file not found: {backup_path}")
        
        # Close all connections
        for conn in self._connection_pool:
            conn.close()
        self._connection_pool.clear()
        
        # Restore backup
        shutil.copy2(backup_path, self.db_path)
        
        # Reinitialize pool
        self._initialize_pool()
        
        logger.info(f"Database restored from: {backup_path}")
        return True
    
    @handle_db_errors
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        backup_dir = os.path.join(self.data_dir, 'backups')
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    # ==================== Legacy Database Wrapper Methods ====================
    
    def get_admin_setting(self, key: str, default: Any = None) -> Any:
        """Wrapper for legacy load_admin_setting"""
        return legacy_db.load_admin_setting(key, default)
    
    def set_admin_setting(self, key: str, value: Any) -> bool:
        """Wrapper for legacy save_admin_setting"""
        return legacy_db.save_admin_setting(key, value)
    
    def get_pricing_mode(self) -> str:
        """Wrapper for legacy get_pricing_calculation_mode"""
        return legacy_db.get_pricing_calculation_mode()
    
    def set_pricing_mode(self, mode: str) -> bool:
        """Wrapper for legacy set_pricing_calculation_mode"""
        return legacy_db.set_pricing_calculation_mode(mode)
    
    def get_brand_logo(self, brand_name: str) -> Optional[str]:
        """Wrapper for legacy get_brand_logo"""
        return legacy_db.get_brand_logo(brand_name)
    
    def add_customer_document(self, customer_id: int, file_bytes: bytes,
                             display_name: str, doc_type: str = "other",
                             project_id: Optional[int] = None,
                             suggested_filename: Optional[str] = None) -> Optional[int]:
        """Wrapper for legacy add_customer_document"""
        return legacy_db.add_customer_document(
            customer_id, file_bytes, display_name, doc_type, project_id, suggested_filename
        )
    
    def list_customer_documents(self, customer_id: int,
                               project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Wrapper for legacy list_customer_documents"""
        return legacy_db.list_customer_documents(customer_id, project_id)
    
    def delete_customer_document(self, document_id: int) -> bool:
        """Wrapper for legacy delete_customer_document"""
        return legacy_db.delete_customer_document(document_id)
    
    def export_settings(self) -> Dict[str, Any]:
        """Wrapper for legacy export_admin_settings"""
        return legacy_db.export_admin_settings()
    
    def import_settings(self, settings: Dict[str, Any]) -> bool:
        """Wrapper for legacy import_admin_settings"""
        return legacy_db.import_admin_settings(settings)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Wrapper for legacy get_database_statistics"""
        return legacy_db.get_database_statistics()
    
    def validate_integrity(self) -> Dict[str, Any]:
        """Wrapper for legacy validate_database_integrity"""
        return legacy_db.validate_database_integrity()
    
    # ==================== Health and Monitoring ====================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check
        
        Returns:
            Dictionary with health status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            stats = self.get_statistics()
            
            return {
                'status': 'healthy',
                'connection_pool_size': len(self._connection_pool),
                'database_size_mb': stats.get('database_size_mb', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_table_list(self) -> List[str]:
        """
        Get list of all tables in database
        
        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
  
      with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [row['name'] for row in cursor.fetchall()]
    
    def close(self):
        """Close all connections in pool"""
        for conn in self._connection_pool:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        self._connection_pool.clear()
        logger.info("DatabaseService closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# Singleton instance
_database_service_instance: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """
    Get singleton database service instance
    
    Returns:
        DatabaseService instance
    """
    global _database_service_instance
    if _database_service_instance is None:
        _database_service_instance = DatabaseService()
    return _database_service_instance
