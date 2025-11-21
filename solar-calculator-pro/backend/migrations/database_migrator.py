"""
Database Migration Script
Handles SQLite database schema migration and data transformation
Requirement: 5.1
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database schema migration and data transformation"""
    
    def __init__(self, source_db: Path, target_db: Path):
        """
        Initialize database migrator
        
        Args:
            source_db: Path to source SQLite database
            target_db: Path to target SQLite database
        """
        self.source_db = Path(source_db)
        self.target_db = Path(target_db)
        self.schema_mappings: Dict[str, Dict[str, str]] = {}
        self.data_transformers: Dict[str, callable] = {}
        
        logger.info(f"Database Migrator initialized: {self.source_db} -> {self.target_db}")
    
    def migrate(self) -> Dict[str, Any]:
        """
        Perform database migration
        
        Returns:
            Migration result with statistics
        """
        logger.info("Starting database migration")
        
        result = {
            "success": False,
            "tables_migrated": 0,
            "records_migrated": 0,
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        source_conn = None
        target_conn = None
        
        try:
            # Connect to databases
            source_conn = sqlite3.connect(self.source_db)
            source_conn.row_factory = sqlite3.Row
            target_conn = sqlite3.connect(self.target_db)
            
            # Get all tables from source
            tables = self._get_tables(source_conn)
            logger.info(f"Found {len(tables)} tables to migrate")
            
            for table in tables:
                try:
                    table_result = self._migrate_table(source_conn, target_conn, table)
                    result["tables_migrated"] += 1
                    result["records_migrated"] += table_result["records"]
                    logger.info(f"Migrated table '{table}': {table_result['records']} records")
                except Exception as e:
                    error_msg = f"Failed to migrate table '{table}': {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    result["errors"].append(error_msg)
            
            # Commit all changes
            target_conn.commit()
            
            result["success"] = len(result["errors"]) == 0
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Database migration completed: {result['tables_migrated']} tables, {result['records_migrated']} records")
            
        except Exception as e:
            error_msg = f"Database migration failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
            
            if target_conn:
                target_conn.rollback()
        
        finally:
            if source_conn:
                source_conn.close()
            if target_conn:
                target_conn.close()
        
        return result
    
    def _get_tables(self, conn: sqlite3.Connection) -> List[str]:
        """Get list of all tables in database"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in cursor.fetchall()]
    
    def _migrate_table(self, source_conn: sqlite3.Connection, target_conn: sqlite3.Connection, table: str) -> Dict[str, int]:
        """
        Migrate a single table
        
        Args:
            source_conn: Source database connection
            target_conn: Target database connection
            table: Table name
            
        Returns:
            Migration statistics
        """
        # Get table schema
        schema = self._get_table_schema(source_conn, table)
        
        # Apply schema mapping if exists
        if table in self.schema_mappings:
            schema = self._apply_schema_mapping(schema, self.schema_mappings[table])
        
        # Create table in target
        create_sql = self._generate_create_table_sql(table, schema)
        target_conn.execute(create_sql)
        
        # Migrate data
        records = self._migrate_table_data(source_conn, target_conn, table, schema)
        
        return {"records": records}
    
    def _get_table_schema(self, conn: sqlite3.Connection, table: str) -> List[Dict[str, str]]:
        """Get table schema"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        
        schema = []
        for row in cursor.fetchall():
            schema.append({
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default": row[4],
                "pk": row[5]
            })
        
        return schema
    
    def _apply_schema_mapping(self, schema: List[Dict[str, str]], mapping: Dict[str, str]) -> List[Dict[str, str]]:
        """Apply schema mapping to rename or transform columns"""
        mapped_schema = []
        
        for column in schema:
            if column["name"] in mapping:
                column["name"] = mapping[column["name"]]
            mapped_schema.append(column)
        
        return mapped_schema
    
    def _generate_create_table_sql(self, table: str, schema: List[Dict[str, str]]) -> str:
        """Generate CREATE TABLE SQL statement"""
        columns = []
        
        for column in schema:
            col_def = f"{column['name']} {column['type']}"
            
            if column["notnull"]:
                col_def += " NOT NULL"
            
            if column["default"] is not None:
                col_def += f" DEFAULT {column['default']}"
            
            if column["pk"]:
                col_def += " PRIMARY KEY"
            
            columns.append(col_def)
        
        return f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
    
    def _migrate_table_data(self, source_conn: sqlite3.Connection, target_conn: sqlite3.Connection, 
                           table: str, schema: List[Dict[str, str]]) -> int:
        """Migrate table data with optional transformation"""
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        # Get all data from source
        source_cursor.execute(f"SELECT * FROM {table}")
        rows = source_cursor.fetchall()
        
        if not rows:
            return 0
        
        # Get column names
        columns = [col["name"] for col in schema]
        
        # Apply data transformation if exists
        if table in self.data_transformers:
            rows = [self.data_transformers[table](dict(row)) for row in rows]
        else:
            rows = [dict(row) for row in rows]
        
        # Insert into target
        placeholders = ','.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        
        for row in rows:
            values = [row.get(col) for col in columns]
            target_cursor.execute(insert_sql, values)
        
        return len(rows)
    
    def add_schema_mapping(self, table: str, column_mapping: Dict[str, str]):
        """
        Add schema mapping for column renaming
        
        Args:
            table: Table name
            column_mapping: Dictionary mapping old column names to new names
        """
        self.schema_mappings[table] = column_mapping
        logger.info(f"Added schema mapping for table '{table}': {column_mapping}")
    
    def add_data_transformer(self, table: str, transformer: callable):
        """
        Add data transformer function for a table
        
        Args:
            table: Table name
            transformer: Function that takes a row dict and returns transformed row dict
        """
        self.data_transformers[table] = transformer
        logger.info(f"Added data transformer for table '{table}'")
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate migration by comparing source and target
        
        Returns:
            Validation result
        """
        logger.info("Validating database migration")
        
        result = {
            "success": False,
            "tables_validated": 0,
            "mismatches": [],
            "errors": []
        }
        
        source_conn = None
        target_conn = None
        
        try:
            source_conn = sqlite3.connect(self.source_db)
            target_conn = sqlite3.connect(self.target_db)
            
            source_tables = self._get_tables(source_conn)
            target_tables = self._get_tables(target_conn)
            
            # Check if all tables exist
            missing_tables = set(source_tables) - set(target_tables)
            if missing_tables:
                result["mismatches"].append(f"Missing tables: {missing_tables}")
            
            # Validate each table
            for table in source_tables:
                if table in target_tables:
                    table_validation = self._validate_table(source_conn, target_conn, table)
                    result["tables_validated"] += 1
                    
                    if not table_validation["match"]:
                        result["mismatches"].append({
                            "table": table,
                            "issue": table_validation["issue"]
                        })
            
            result["success"] = len(result["mismatches"]) == 0
            logger.info(f"Validation completed: {result['tables_validated']} tables validated")
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append(error_msg)
        
        finally:
            if source_conn:
                source_conn.close()
            if target_conn:
                target_conn.close()
        
        return result
    
    def _validate_table(self, source_conn: sqlite3.Connection, target_conn: sqlite3.Connection, table: str) -> Dict[str, Any]:
        """Validate a single table"""
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        # Count records
        source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        source_count = source_cursor.fetchone()[0]
        
        target_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        target_count = target_cursor.fetchone()[0]
        
        if source_count != target_count:
            return {
                "match": False,
                "issue": f"Record count mismatch: source={source_count}, target={target_count}"
            }
        
        return {"match": True, "issue": None}


# Example usage and transformers
def example_user_transformer(row: Dict[str, Any]) -> Dict[str, Any]:
    """Example transformer for user table"""
    # Add created_at if missing
    if 'created_at' not in row:
        row['created_at'] = datetime.now().isoformat()
    
    # Hash password if plain text
    if 'password' in row and not row['password'].startswith('$2b$'):
        import bcrypt
        row['password'] = bcrypt.hashpw(row['password'].encode(), bcrypt.gensalt()).decode()
    
    return row


def example_project_transformer(row: Dict[str, Any]) -> Dict[str, Any]:
    """Example transformer for project table"""
    # Convert old status values to new ones
    status_mapping = {
        'active': 'in_progress',
        'done': 'completed',
        'pending': 'draft'
    }
    
    if 'status' in row and row['status'] in status_mapping:
        row['status'] = status_mapping[row['status']]
    
    return row
