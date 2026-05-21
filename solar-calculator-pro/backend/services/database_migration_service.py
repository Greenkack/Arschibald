"""
Database Migration Service
Handles migration between different database types (SQLite, PostgreSQL, MySQL).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import inspect, MetaData, Table
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from backend.core.database_abstraction import (
    DatabaseManager,
    DatabaseConfig,
    DatabaseType
)

logger = logging.getLogger(__name__)


class MigrationProgress:
    """Track migration progress"""
    
    def __init__(self):
        self.total_tables = 0
        self.completed_tables = 0
        self.total_rows = 0
        self.migrated_rows = 0
        self.current_table = None
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def get_progress_percentage(self) -> float:
        """Get overall progress percentage"""
        if self.total_rows == 0:
            return 0.0
        return (self.migrated_rows / self.total_rows) * 100
    
    def get_table_progress_percentage(self) -> float:
        """Get table progress percentage"""
        if self.total_tables == 0:
            return 0.0
        return (self.completed_tables / self.total_tables) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_tables": self.total_tables,
            "completed_tables": self.completed_tables,
            "total_rows": self.total_rows,
            "migrated_rows": self.migrated_rows,
            "current_table": self.current_table,
            "progress_percentage": self.get_progress_percentage(),
            "table_progress_percentage": self.get_table_progress_percentage(),
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class DatabaseMigrationService:
    """Service for migrating data between different database types"""
    
    def __init__(
        self,
        source_config: DatabaseConfig,
        target_config: DatabaseConfig
    ):
        self.source_manager = DatabaseManager(source_config)
        self.target_manager = DatabaseManager(target_config)
        self.progress = MigrationProgress()
    
    def validate_migration(self) -> Dict[str, Any]:
        """Validate that migration is possible"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Connect to both databases
            self.source_manager.connect()
            self.target_manager.connect()
            
            # Check if source database is accessible
            source_session = self.source_manager.get_session()
            source_session.close()
            
            # Check if target database is accessible
            target_session = self.target_manager.get_session()
            target_session.close()
            
            # Check if source and target are different
            if (self.source_manager.get_database_type() == 
                self.target_manager.get_database_type()):
                validation_result["warnings"].append(
                    "Source and target databases are of the same type"
                )
            
            logger.info("Migration validation successful")
        
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))
            logger.error(f"Migration validation failed: {e}")
        
        finally:
            self.source_manager.disconnect()
            self.target_manager.disconnect()
        
        return validation_result
    
    def get_table_list(self) -> List[str]:
        """Get list of tables from source database"""
        try:
            self.source_manager.connect()
            inspector = inspect(self.source_manager.adapter.engine)
            tables = inspector.get_table_names()
            logger.info(f"Found {len(tables)} tables in source database")
            return tables
        
        except Exception as e:
            logger.error(f"Failed to get table list: {e}")
            raise
        
        finally:
            self.source_manager.disconnect()
    
    def count_rows(self, table_name: str) -> int:
        """Count rows in a table"""
        try:
            session = self.source_manager.get_session()
            metadata = MetaData()
            metadata.reflect(bind=self.source_manager.adapter.engine)
            table = metadata.tables[table_name]
            count = session.query(table).count()
            session.close()
            return count
        
        except Exception as e:
            logger.error(f"Failed to count rows in {table_name}: {e}")
            return 0
    
    def migrate_table_schema(self, table_name: str) -> bool:
        """Migrate table schema from source to target"""
        try:
            # Get table metadata from source
            source_metadata = MetaData()
            source_metadata.reflect(
                bind=self.source_manager.adapter.engine,
                only=[table_name]
            )
            
            source_table = source_metadata.tables[table_name]
            
            # Create table in target database
            target_metadata = MetaData()
            target_table = Table(
                table_name,
                target_metadata,
                *[column.copy() for column in source_table.columns],
                extend_existing=True
            )
            
            target_metadata.create_all(
                bind=self.target_manager.adapter.engine,
                tables=[target_table]
            )
            
            logger.info(f"Migrated schema for table: {table_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to migrate schema for {table_name}: {e}")
            self.progress.errors.append(f"Schema migration failed for {table_name}: {e}")
            return False
    
    def migrate_table_data(
        self,
        table_name: str,
        batch_size: int = 1000
    ) -> bool:
        """Migrate table data from source to target"""
        try:
            # Get table metadata
            source_metadata = MetaData()
            source_metadata.reflect(
                bind=self.source_manager.adapter.engine,
                only=[table_name]
            )
            source_table = source_metadata.tables[table_name]
            
            target_metadata = MetaData()
            target_metadata.reflect(
                bind=self.target_manager.adapter.engine,
                only=[table_name]
            )
            target_table = target_metadata.tables[table_name]
            
            # Get source session
            source_session = self.source_manager.get_session()
            target_session = self.target_manager.get_session()
            
            # Count total rows
            total_rows = source_session.query(source_table).count()
            migrated_rows = 0
            
            # Migrate data in batches
            offset = 0
            while True:
                # Fetch batch from source
                rows = source_session.query(source_table).limit(batch_size).offset(offset).all()
                
                if not rows:
                    break
                
                # Convert rows to dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for column in source_table.columns:
                        row_dict[column.name] = getattr(row, column.name)
                    data.append(row_dict)
                
                # Insert into target
                target_session.execute(target_table.insert(), data)
                target_session.commit()
                
                migrated_rows += len(rows)
                self.progress.migrated_rows += len(rows)
                
                logger.info(
                    f"Migrated {migrated_rows}/{total_rows} rows from {table_name}"
                )
                
                offset += batch_size
            
            source_session.close()
            target_session.close()
            
            logger.info(f"Successfully migrated all data from {table_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to migrate data for {table_name}: {e}")
            self.progress.errors.append(f"Data migration failed for {table_name}: {e}")
            return False
    
    def migrate_all(
        self,
        tables: Optional[List[str]] = None,
        batch_size: int = 1000
    ) -> MigrationProgress:
        """Migrate all tables from source to target"""
        try:
            self.progress.start_time = datetime.now()
            
            # Connect to both databases
            self.source_manager.connect()
            self.target_manager.connect()
            
            # Get list of tables to migrate
            if tables is None:
                tables = self.get_table_list()
            
            self.progress.total_tables = len(tables)
            
            # Count total rows
            for table_name in tables:
                row_count = self.count_rows(table_name)
                self.progress.total_rows += row_count
            
            logger.info(
                f"Starting migration of {self.progress.total_tables} tables "
                f"with {self.progress.total_rows} total rows"
            )
            
            # Migrate each table
            for table_name in tables:
                self.progress.current_table = table_name
                logger.info(f"Migrating table: {table_name}")
                
                # Migrate schema
                schema_success = self.migrate_table_schema(table_name)
                if not schema_success:
                    continue
                
                # Migrate data
                data_success = self.migrate_table_data(table_name, batch_size)
                if data_success:
                    self.progress.completed_tables += 1
            
            self.progress.end_time = datetime.now()
            
            logger.info(
                f"Migration completed: {self.progress.completed_tables}/"
                f"{self.progress.total_tables} tables migrated successfully"
            )
        
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.progress.errors.append(f"Migration failed: {e}")
        
        finally:
            self.source_manager.disconnect()
            self.target_manager.disconnect()
        
        return self.progress
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful"""
        verification_result = {
            "success": True,
            "tables_verified": 0,
            "tables_failed": 0,
            "row_count_matches": [],
            "row_count_mismatches": []
        }
        
        try:
            self.source_manager.connect()
            self.target_manager.connect()
            
            tables = self.get_table_list()
            
            for table_name in tables:
                try:
                    # Count rows in source
                    source_count = self.count_rows(table_name)
                    
                    # Count rows in target
                    target_session = self.target_manager.get_session()
                    target_metadata = MetaData()
                    target_metadata.reflect(
                        bind=self.target_manager.adapter.engine,
                        only=[table_name]
                    )
                    target_table = target_metadata.tables[table_name]
                    target_count = target_session.query(target_table).count()
                    target_session.close()
                    
                    # Compare counts
                    if source_count == target_count:
                        verification_result["tables_verified"] += 1
                        verification_result["row_count_matches"].append({
                            "table": table_name,
                            "count": source_count
                        })
                    else:
                        verification_result["success"] = False
                        verification_result["tables_failed"] += 1
                        verification_result["row_count_mismatches"].append({
                            "table": table_name,
                            "source_count": source_count,
                            "target_count": target_count
                        })
                
                except Exception as e:
                    verification_result["success"] = False
                    verification_result["tables_failed"] += 1
                    logger.error(f"Verification failed for {table_name}: {e}")
        
        except Exception as e:
            verification_result["success"] = False
            logger.error(f"Verification failed: {e}")
        
        finally:
            self.source_manager.disconnect()
            self.target_manager.disconnect()
        
        return verification_result
    
    def rollback_migration(self) -> bool:
        """Rollback migration by dropping all tables in target database"""
        try:
            self.target_manager.connect()
            self.target_manager.drop_tables()
            logger.info("Migration rolled back successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            return False
        
        finally:
            self.target_manager.disconnect()
