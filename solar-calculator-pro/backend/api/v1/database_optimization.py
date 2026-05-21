"""
Database Optimization API Endpoints

Provides REST API for database optimization operations:
- Query analysis and optimization
- Index management
- Table partitioning analysis
- Data archiving
- Vacuum and analyze operations
- Performance monitoring

Requirements: 8.4
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ...core.database import get_db, get_engine
from ...services.database_optimization_service import DatabaseOptimizationService

router = APIRouter(prefix="/database-optimization", tags=["database-optimization"])


# ==================== Request/Response Models ====================

class QueryAnalysisRequest(BaseModel):
    """Request model for query analysis"""
    query: str = Field(..., description="SQL query to analyze")


class IndexCreateRequest(BaseModel):
    """Request model for creating an index"""
    table_name: str = Field(..., description="Table name")
    columns: List[str] = Field(..., description="Column names for index")
    index_name: Optional[str] = Field(None, description="Custom index name")
    unique: bool = Field(False, description="Whether index should be unique")


class ArchiveDataRequest(BaseModel):
    """Request model for archiving data"""
    table_name: str = Field(..., description="Table name")
    date_column: str = Field(..., description="Date column for filtering")
    threshold_date: datetime = Field(..., description="Date threshold for archiving")
    archive_table_suffix: str = Field("_archive", description="Archive table suffix")


class MaintenanceScheduleRequest(BaseModel):
    """Request model for maintenance schedule"""
    vacuum_enabled: bool = Field(True, description="Enable automatic VACUUM")
    analyze_enabled: bool = Field(True, description="Enable automatic ANALYZE")
    vacuum_schedule: str = Field("weekly", description="VACUUM schedule")
    analyze_schedule: str = Field("daily", description="ANALYZE schedule")


# ==================== Helper Functions ====================

def get_optimization_service(engine: Engine = Depends(get_engine)) -> DatabaseOptimizationService:
    """Get database optimization service instance"""
    return DatabaseOptimizationService(engine)


# ==================== Query Optimization Endpoints ====================

@router.post("/query/analyze")
async def analyze_query(
    request: QueryAnalysisRequest,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Analyze query performance and get optimization suggestions
    
    Args:
        request: Query analysis request
        service: Database optimization service
        
    Returns:
        Query analysis results with suggestions
    """
    try:
        result = service.analyze_query(request.query)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/slow")
async def get_slow_queries(
    threshold_ms: float = Query(1000.0, description="Minimum execution time in ms"),
    limit: int = Query(10, description="Maximum number of queries"),
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> List[Dict[str, Any]]:
    """
    Get list of slow queries
    
    Args:
        threshold_ms: Minimum execution time threshold
        limit: Maximum number of queries to return
        service: Database optimization service
        
    Returns:
        List of slow queries
    """
    try:
        return service.get_slow_queries(threshold_ms, limit)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Index Management Endpoints ====================

@router.get("/indexes")
async def get_indexes(
    table_name: Optional[str] = Query(None, description="Optional table name filter"),
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, List[Dict]]:
    """
    Get all indexes or indexes for specific table
    
    Args:
        table_name: Optional table name to filter
        service: Database optimization service
        
    Returns:
        Dictionary of table indexes
    """
    try:
        return service.get_indexes(table_name)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indexes/analyze/{table_name}")
async def analyze_index_usage(
    table_name: str,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Analyze index usage for a table
    
    Args:
        table_name: Table name to analyze
        service: Database optimization service
        
    Returns:
        Index usage analysis and recommendations
    """
    try:
        result = service.analyze_index_usage(table_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/indexes/create")
async def create_index(
    request: IndexCreateRequest,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Create a new index
    
    Args:
        request: Index creation request
        service: Database optimization service
        
    Returns:
        Index creation result
    """
    try:
        result = service.create_index(
            table_name=request.table_name,
            columns=request.columns,
            index_name=request.index_name,
            unique=request.unique
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/indexes/{index_name}")
async def drop_index(
    index_name: str,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Drop an index
    
    Args:
        index_name: Name of index to drop
        service: Database optimization service
        
    Returns:
        Index drop result
    """
    try:
        result = service.drop_index(index_name)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Partitioning Endpoints ====================

@router.get("/partitioning/candidates")
async def get_partitioning_candidates(
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> List[Dict[str, Any]]:
    """
    Get tables that could benefit from partitioning
    
    Args:
        service: Database optimization service
        
    Returns:
        List of partitioning candidates
    """
    try:
        return service.analyze_partitioning_candidates()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Archiving Endpoints ====================

@router.get("/archiving/candidates")
async def get_archiving_candidates(
    age_threshold_days: int = Query(365, description="Age threshold in days"),
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> List[Dict[str, Any]]:
    """
    Get tables with old data suitable for archiving
    
    Args:
        age_threshold_days: Age threshold for archiving
        service: Database optimization service
        
    Returns:
        List of archiving candidates
    """
    try:
        return service.analyze_archiving_candidates(age_threshold_days)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archiving/archive")
async def archive_old_data(
    request: ArchiveDataRequest,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Archive old data to separate table
    
    Args:
        request: Archive data request
        service: Database optimization service
        
    Returns:
        Archiving result
    """
    try:
        result = service.archive_old_data(
            table_name=request.table_name,
            date_column=request.date_column,
            threshold_date=request.threshold_date,
            archive_table_suffix=request.archive_table_suffix
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Maintenance Endpoints ====================

@router.post("/maintenance/vacuum")
async def vacuum_database(
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Run VACUUM to reclaim space and defragment database
    
    Args:
        service: Database optimization service
        
    Returns:
        VACUUM operation result
    """
    try:
        result = service.vacuum_database()
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/analyze")
async def analyze_tables(
    table_names: Optional[List[str]] = Query(None, description="Optional table names"),
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Run ANALYZE to update statistics
    
    Args:
        table_names: Optional list of specific tables
        service: Database optimization service
        
    Returns:
        ANALYZE operation result
    """
    try:
        result = service.analyze_tables(table_names)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/schedule")
async def schedule_maintenance(
    request: MaintenanceScheduleRequest,
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Configure automatic maintenance schedule
    
    Args:
        request: Maintenance schedule configuration
        service: Database optimization service
        
    Returns:
        Schedule configuration
    """
    try:
        return service.schedule_maintenance(
            vacuum_enabled=request.vacuum_enabled,
            analyze_enabled=request.analyze_enabled,
            vacuum_schedule=request.vacuum_schedule,
            analyze_schedule=request.analyze_schedule
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Monitoring Endpoints ====================

@router.get("/metrics")
async def get_performance_metrics(
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Get comprehensive database performance metrics
    
    Args:
        service: Database optimization service
        
    Returns:
        Performance metrics
    """
    try:
        result = service.get_performance_metrics()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def get_optimization_report(
    service: DatabaseOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Generate comprehensive optimization report
    
    Args:
        service: Database optimization service
        
    Returns:
        Complete optimization analysis report
    """
    try:
        result = service.get_optimization_report()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
