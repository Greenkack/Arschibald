"""
Database Type Management API
Endpoints for managing database type selection and migration.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

from backend.core.database_abstraction import (
    DatabaseType,
    DatabaseConfig,
    DatabaseManager
)
from backend.services.database_migration_service import (
    DatabaseMigrationService,
    MigrationProgress
)

router = APIRouter(prefix="/database-type", tags=["database-type"])


# Pydantic models
class DatabaseTypeEnum(str, Enum):
    """Database type enum for API"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class DatabaseConfigRequest(BaseModel):
    """Database configuration request"""
    db_type: DatabaseTypeEnum
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    sqlite_path: Optional[str] = None
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=60, le=86400)
    echo: bool = False


class DatabaseConfigResponse(BaseModel):
    """Database configuration response"""
    db_type: DatabaseTypeEnum
    host: Optional[str]
    port: Optional[int]
    database: Optional[str]
    username: Optional[str]
    sqlite_path: Optional[str]
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int
    echo: bool


class DatabaseTestConnectionRequest(BaseModel):
    """Test database connection request"""
    config: DatabaseConfigRequest


class DatabaseTestConnectionResponse(BaseModel):
    """Test database connection response"""
    success: bool
    message: str
    db_type: DatabaseTypeEnum


class MigrationRequest(BaseModel):
    """Database migration request"""
    source_config: DatabaseConfigRequest
    target_config: DatabaseConfigRequest
    tables: Optional[List[str]] = None
    batch_size: int = Field(default=1000, ge=100, le=10000)


class MigrationProgressResponse(BaseModel):
    """Migration progress response"""
    total_tables: int
    completed_tables: int
    total_rows: int
    migrated_rows: int
    current_table: Optional[str]
    progress_percentage: float
    table_progress_percentage: float
    errors: List[str]
    start_time: Optional[str]
    end_time: Optional[str]


class MigrationValidationResponse(BaseModel):
    """Migration validation response"""
    valid: bool
    errors: List[str]
    warnings: List[str]


class MigrationVerificationResponse(BaseModel):
    """Migration verification response"""
    success: bool
    tables_verified: int
    tables_failed: int
    row_count_matches: List[Dict[str, Any]]
    row_count_mismatches: List[Dict[str, Any]]


# Helper functions
def convert_config_to_database_config(config: DatabaseConfigRequest) -> DatabaseConfig:
    """Convert API config to DatabaseConfig"""
    return DatabaseConfig(
        db_type=DatabaseType(config.db_type.value),
        host=config.host,
        port=config.port,
        database=config.database,
        username=config.username,
        password=config.password,
        sqlite_path=config.sqlite_path,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        echo=config.echo
    )


# API endpoints
@router.get("/supported-types", response_model=List[str])
async def get_supported_database_types():
    """Get list of supported database types"""
    return [db_type.value for db_type in DatabaseType]


@router.post("/test-connection", response_model=DatabaseTestConnectionResponse)
async def test_database_connection(request: DatabaseTestConnectionRequest):
    """Test database connection"""
    try:
        config = convert_config_to_database_config(request.config)
        manager = DatabaseManager(config)
        
        # Try to connect
        manager.connect()
        
        # Try to get a session
        session = manager.get_session()
        session.close()
        
        manager.disconnect()
        
        return DatabaseTestConnectionResponse(
            success=True,
            message=f"Successfully connected to {config.db_type.value} database",
            db_type=DatabaseTypeEnum(config.db_type.value)
        )
    
    except Exception as e:
        return DatabaseTestConnectionResponse(
            success=False,
            message=f"Failed to connect: {str(e)}",
            db_type=request.config.db_type
        )


@router.post("/validate-migration", response_model=MigrationValidationResponse)
async def validate_migration(request: MigrationRequest):
    """Validate that migration is possible"""
    try:
        source_config = convert_config_to_database_config(request.source_config)
        target_config = convert_config_to_database_config(request.target_config)
        
        migration_service = DatabaseMigrationService(source_config, target_config)
        validation_result = migration_service.validate_migration()
        
        return MigrationValidationResponse(**validation_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migrate", response_model=MigrationProgressResponse)
async def migrate_database(
    request: MigrationRequest,
    background_tasks: BackgroundTasks
):
    """Migrate database from source to target"""
    try:
        source_config = convert_config_to_database_config(request.source_config)
        target_config = convert_config_to_database_config(request.target_config)
        
        migration_service = DatabaseMigrationService(source_config, target_config)
        
        # Run migration
        progress = migration_service.migrate_all(
            tables=request.tables,
            batch_size=request.batch_size
        )
        
        return MigrationProgressResponse(**progress.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-migration", response_model=MigrationVerificationResponse)
async def verify_migration(request: MigrationRequest):
    """Verify that migration was successful"""
    try:
        source_config = convert_config_to_database_config(request.source_config)
        target_config = convert_config_to_database_config(request.target_config)
        
        migration_service = DatabaseMigrationService(source_config, target_config)
        verification_result = migration_service.verify_migration()
        
        return MigrationVerificationResponse(**verification_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback-migration")
async def rollback_migration(request: MigrationRequest):
    """Rollback migration by dropping all tables in target database"""
    try:
        target_config = convert_config_to_database_config(request.target_config)
        
        migration_service = DatabaseMigrationService(
            source_config=target_config,  # Dummy source
            target_config=target_config
        )
        
        success = migration_service.rollback_migration()
        
        if success:
            return {"message": "Migration rolled back successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to rollback migration")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-config", response_model=DatabaseConfigResponse)
async def get_current_database_config():
    """Get current database configuration"""
    # This would typically read from application settings
    # For now, return a placeholder
    return DatabaseConfigResponse(
        db_type=DatabaseTypeEnum.SQLITE,
        host=None,
        port=None,
        database=None,
        username=None,
        sqlite_path="./database.db",
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
        echo=False
    )


@router.post("/set-config")
async def set_database_config(config: DatabaseConfigRequest):
    """Set database configuration"""
    try:
        # Validate configuration by testing connection
        db_config = convert_config_to_database_config(config)
        manager = DatabaseManager(db_config)
        manager.connect()
        manager.disconnect()
        
        # Save configuration (implementation depends on settings management)
        # For now, just return success
        return {
            "message": "Database configuration set successfully",
            "db_type": config.db_type.value
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
