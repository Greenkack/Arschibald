"""
Solar Calculator API Endpoints

This module provides REST API endpoints for solar system calculations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.solar_schemas import (
    SolarCalculationRequest,
    SolarCalculationResponse,
    SolarProjectCreate,
    SolarProjectResponse,
    SolarProjectUpdate,
    SolarProjectList
)
from backend.services.solar_service import get_solar_service, SolarCalculatorService
from backend.core.auth_dependencies import get_current_user
from backend.models.auth_schemas import UserResponse
from backend.core.dependencies import get_db


router = APIRouter(prefix="/solar", tags=["solar"])


@router.post("/calculate", response_model=SolarCalculationResponse)
async def calculate_solar_system(
    request: SolarCalculationRequest,
    current_user: UserResponse = Depends(get_current_user),
    solar_service: SolarCalculatorService = Depends(get_solar_service)
) -> SolarCalculationResponse:
    """
    Calculate solar system performance and economics.
    
    This endpoint performs a complete solar system calculation including:
    - System sizing
    - Energy production (using PVGIS or manual calculation)
    - Self-consumption analysis
    - Economic analysis (payback, savings, ROI)
    - Environmental impact (CO2 savings)
    - Battery storage analysis (if included)
    
    Args:
        request: Solar calculation parameters
        current_user: Authenticated user
        solar_service: Solar calculator service instance
        
    Returns:
        Complete calculation results
        
    Raises:
        HTTPException: If calculation fails
    """
    try:
        result = solar_service.calculate_solar_system(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/health", response_model=dict)
async def solar_service_health(
    solar_service: SolarCalculatorService = Depends(get_solar_service)
) -> dict:
    """
    Check solar calculator service health.
    
    Returns:
        Health check result with service status
    """
    health_result = solar_service.health_check()
    return health_result.to_dict()


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats(
    current_user: UserResponse = Depends(get_current_user),
    solar_service: SolarCalculatorService = Depends(get_solar_service)
) -> dict:
    """
    Get cache statistics.
    
    Returns:
        Cache statistics including size and age
    """
    return solar_service.get_cache_stats()


@router.delete("/cache", response_model=dict)
async def clear_cache(
    current_user: UserResponse = Depends(get_current_user),
    solar_service: SolarCalculatorService = Depends(get_solar_service)
) -> dict:
    """
    Clear calculation cache.
    
    Requires authentication. Clears all cached calculation results.
    
    Returns:
        Number of entries cleared
    """
    count = solar_service.clear_cache()
    return {"message": f"Cleared {count} cache entries", "count": count}


# Project management endpoints

@router.post("/projects", response_model=SolarProjectResponse, status_code=201)
async def create_project(
    project: SolarProjectCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SolarProjectResponse:
    """
    Create a new solar project.
    
    Args:
        project: Project creation data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created project with ID
    """
    from backend.services.project_service import ProjectService
    
    try:
        service = ProjectService(db)
        return service.create_project(project, current_user.id)
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=SolarProjectList)
async def list_projects(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in project name")
) -> SolarProjectList:
    """
    List all solar projects for the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number
        page_size: Number of items per page
        project_type: Filter by project type (solar, heatpump, combined)
        status: Filter by status (draft, active, completed, archived)
        search: Search term for project name
        
    Returns:
        Paginated list of projects
    """
    from backend.services.project_service import ProjectService
    
    try:
        service = ProjectService(db)
        return service.list_projects(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            project_type=project_type,
            status=status,
            search=search
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}", response_model=SolarProjectResponse)
async def get_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SolarProjectResponse:
    """
    Get a specific solar project by ID.
    
    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Project details
    """
    from backend.services.project_service import ProjectService
    
    try:
        service = ProjectService(db)
        return service.get_project(project_id, current_user.id)
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}", response_model=SolarProjectResponse)
async def update_project(
    project_id: int,
    project_update: SolarProjectUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SolarProjectResponse:
    """
    Update a solar project.
    
    Args:
        project_id: Project ID
        project_update: Updated project data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated project
    """
    from backend.services.project_service import ProjectService
    
    try:
        service = ProjectService(db)
        return service.update_project(project_id, project_update, current_user.id)
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a solar project.
    
    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session
    """
    from backend.services.project_service import ProjectService
    
    try:
        service = ProjectService(db)
        service.delete_project(project_id, current_user.id)
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))
