"""
Solar Project Management Service

This service handles CRUD operations for solar projects, including
creation, retrieval, updating, and deletion of projects.

Requirements: 7.1
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import json

from backend.models.database_models import Project, Customer
from backend.models.solar_schemas import (
    SolarProjectCreate,
    SolarProjectUpdate,
    SolarProjectResponse,
    SolarProjectList
)
from backend.core.exceptions import APIError
from backend.core.dynamic_keys import KeyPrefix


class ProjectService:
    """Service for managing solar projects"""
    
    def __init__(self, db: Session):
        """
        Initialize project service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_project(
        self,
        project_data: SolarProjectCreate,
        user_id: int
    ) -> SolarProjectResponse:
        """
        Create a new solar project.
        
        Args:
            project_data: Project creation data
            user_id: ID of the user creating the project
            
        Returns:
            Created project
            
        Raises:
            APIError: If customer not found or creation fails
        """
        # Verify customer exists
        customer = self.db.query(Customer).filter(
            Customer.id == project_data.customer_id
        ).first()
        
        if not customer:
            raise APIError(
                status_code=404,
                message=f"Customer with ID {project_data.customer_id} not found"
            )
        
        # Create project
        project = Project(
            name=project_data.name,
            customer_id=project_data.customer_id,
            project_type=project_data.project_type,
            status='draft',
            data=json.dumps(project_data.data) if project_data.data else None
        )
        
        # Generate dynamic key
        project.generate_and_store_key(KeyPrefix.PROJECT)
        
        try:
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            
            return self._to_response(project)
        except Exception as e:
            self.db.rollback()
            raise APIError(
                status_code=500,
                message=f"Failed to create project: {str(e)}"
            )
    
    def get_project(
        self,
        project_id: int,
        user_id: int
    ) -> SolarProjectResponse:
        """
        Get a specific project by ID.
        
        Args:
            project_id: Project ID
            user_id: ID of the requesting user
            
        Returns:
            Project details
            
        Raises:
            APIError: If project not found
        """
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            raise APIError(
                status_code=404,
                message=f"Project with ID {project_id} not found"
            )
        
        return self._to_response(project)
    
    def list_projects(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        project_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> SolarProjectList:
        """
        List projects with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-indexed)
            page_size: Number of items per page
            project_type: Filter by project type
            status: Filter by status
            search: Search in project name
            
        Returns:
            Paginated list of projects
        """
        # Build query
        query = self.db.query(Project)
        
        # Apply filters
        if project_type:
            query = query.filter(Project.project_type == project_type)
        
        if status:
            query = query.filter(Project.status == status)
        
        if search:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.dynamic_key.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        projects = query.order_by(Project.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Convert to response
        items = [self._to_response(p) for p in projects]
        
        return SolarProjectList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    def update_project(
        self,
        project_id: int,
        project_update: SolarProjectUpdate,
        user_id: int
    ) -> SolarProjectResponse:
        """
        Update a project.
        
        Args:
            project_id: Project ID
            project_update: Updated project data
            user_id: ID of the requesting user
            
        Returns:
            Updated project
            
        Raises:
            APIError: If project not found or update fails
        """
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            raise APIError(
                status_code=404,
                message=f"Project with ID {project_id} not found"
            )
        
        # Update fields
        if project_update.name is not None:
            project.name = project_update.name
        
        if project_update.status is not None:
            project.status = project_update.status
        
        if project_update.data is not None:
            project.data = json.dumps(project_update.data)
        
        try:
            self.db.commit()
            self.db.refresh(project)
            
            return self._to_response(project)
        except Exception as e:
            self.db.rollback()
            raise APIError(
                status_code=500,
                message=f"Failed to update project: {str(e)}"
            )
    
    def delete_project(
        self,
        project_id: int,
        user_id: int
    ) -> None:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            user_id: ID of the requesting user
            
        Raises:
            APIError: If project not found or deletion fails
        """
        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            raise APIError(
                status_code=404,
                message=f"Project with ID {project_id} not found"
            )
        
        try:
            self.db.delete(project)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise APIError(
                status_code=500,
                message=f"Failed to delete project: {str(e)}"
            )
    
    def _to_response(self, project: Project) -> SolarProjectResponse:
        """
        Convert database model to response schema.
        
        Args:
            project: Project database model
            
        Returns:
            Project response schema
        """
        # Parse JSON data
        data = {}
        if project.data:
            try:
                data = json.loads(project.data)
            except json.JSONDecodeError:
                data = {}
        
        return SolarProjectResponse(
            id=project.id,
            name=project.name,
            customer_id=project.customer_id,
            project_type=project.project_type,
            status=project.status,
            data=data,
            dynamic_key=project.dynamic_key,
            created_at=project.created_at,
            updated_at=project.updated_at
        )


def get_project_service(db: Session) -> ProjectService:
    """
    Dependency injection for project service.
    
    Args:
        db: Database session
        
    Returns:
        ProjectService instance
    """
    return ProjectService(db)
