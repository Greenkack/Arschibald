"""
CRM API Endpoints

RESTful API endpoints for CRM operations including customer management,
offer tracking, task management, and communication history.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
import logging

from backend.services.crm_service import get_crm_service, CRMService
from backend.models.crm_schemas import (
    # Customer schemas
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerSearchRequest,
    # Offer schemas
    OfferStatusUpdate,
    OfferStatusResponse,
    OfferListResponse,
    OfferStatisticsResponse,
    # Task schemas
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatisticsResponse,
    TaskFilterRequest,
    # Activity schemas
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityStatisticsResponse,
    ActivityFilterRequest,
    ActivitySearchRequest,
    # Generic schemas
    SuccessResponse,
    DeleteResponse
)

# Create router
router = APIRouter(prefix="/crm", tags=["crm"])
logger = logging.getLogger(__name__)


# Dependency to get CRM service
def get_service() -> CRMService:
    """Get the CRM service instance"""
    return get_crm_service()


# ==================== Customer Management Endpoints ====================

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    service: CRMService = Depends(get_service)
):
    """
    Create a new customer.
    
    - **first_name**: Customer first name (required)
    - **last_name**: Customer last name (required)
    - **company_name**: Company name (optional)
    - **email**: Email address (optional)
    - **phone_mobile**: Mobile phone (optional)
    - Additional fields for address and notes
    """
    try:
        created_customer = service.create_customer(customer.dict(exclude_unset=True))
        return CustomerResponse(**created_customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Get a customer by ID.
    
    - **customer_id**: Customer ID
    """
    try:
        customer = service.get_customer(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        return CustomerResponse(**customer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/customers", response_model=CustomerListResponse)
async def list_customers(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    service: CRMService = Depends(get_service)
):
    """
    List all customers with optional search.
    
    - **limit**: Maximum number of results (default: 100)
    - **offset**: Offset for pagination (default: 0)
    - **search**: Search term for filtering customers
    """
    try:
        customers = service.list_customers(limit=limit, offset=offset, search=search)
        
        return CustomerListResponse(
            customers=[CustomerResponse(**c) for c in customers],
            total=len(customers),
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Unexpected error listing customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    service: CRMService = Depends(get_service)
):
    """
    Update an existing customer.
    
    - **customer_id**: Customer ID
    - All fields are optional
    """
    try:
        updated_customer = service.update_customer(
            customer_id,
            customer.dict(exclude_unset=True)
        )
        return CustomerResponse(**updated_customer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/customers/{customer_id}", response_model=DeleteResponse)
async def delete_customer(
    customer_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Delete a customer.
    
    - **customer_id**: Customer ID
    """
    try:
        success = service.delete_customer(customer_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        return DeleteResponse(
            success=True,
            message=f"Customer {customer_id} deleted successfully",
            deleted_id=customer_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Offer Tracking Endpoints ====================

@router.get("/offers/{project_id}", response_model=OfferStatusResponse)
async def get_offer_status(
    project_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Get offer status for a project.
    
    - **project_id**: Project ID
    """
    try:
        offer = service.get_offer_status(project_id)
        
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offer for project {project_id} not found"
            )
        
        return OfferStatusResponse(**offer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting offer status for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/offers/{project_id}/status", response_model=SuccessResponse)
async def update_offer_status(
    project_id: int,
    status_update: OfferStatusUpdate,
    service: CRMService = Depends(get_service)
):
    """
    Update offer status for a project.
    
    - **project_id**: Project ID
    - **new_status**: New status (draft, sent, accepted, rejected)
    - Additional fields based on status
    """
    try:
        update_data = status_update.dict(exclude={'new_status'}, exclude_unset=True)
        success = service.update_offer_status(
            project_id,
            status_update.new_status,
            **update_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        return SuccessResponse(
            success=True,
            message=f"Offer status updated to {status_update.new_status}",
            data={"project_id": project_id, "new_status": status_update.new_status}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating offer status for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/offers", response_model=OfferListResponse)
async def list_offers(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    include_customer_info: bool = Query(True, description="Include customer information"),
    service: CRMService = Depends(get_service)
):
    """
    List all offers with optional status filter.
    
    - **status_filter**: Filter by status (draft, sent, accepted, rejected)
    - **include_customer_info**: Include customer information in response
    """
    try:
        offers = service.list_offers(
            status_filter=status_filter,
            include_customer_info=include_customer_info
        )
        
        return OfferListResponse(
            offers=[OfferStatusResponse(**o) for o in offers],
            total=len(offers)
        )
    except Exception as e:
        logger.error(f"Unexpected error listing offers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/offers/follow-ups/pending", response_model=OfferListResponse)
async def get_pending_follow_ups(
    service: CRMService = Depends(get_service)
):
    """
    Get all offers with pending follow-ups.
    """
    try:
        follow_ups = service.get_pending_follow_ups()
        
        return OfferListResponse(
            offers=[OfferStatusResponse(**f) for f in follow_ups],
            total=len(follow_ups)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting pending follow-ups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/offers/{project_id}/follow-up/complete", response_model=SuccessResponse)
async def mark_follow_up_completed(
    project_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Mark a follow-up as completed.
    
    - **project_id**: Project ID
    """
    try:
        success = service.mark_follow_up_completed(project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found or no follow-up to complete"
            )
        
        return SuccessResponse(
            success=True,
            message=f"Follow-up for project {project_id} marked as completed",
            data={"project_id": project_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error marking follow-up completed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/offers/statistics", response_model=OfferStatisticsResponse)
async def get_offer_statistics(
    service: CRMService = Depends(get_service)
):
    """
    Get offer statistics.
    """
    try:
        stats = service.get_offer_statistics()
        return OfferStatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Unexpected error getting offer statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Task Management Endpoints ====================

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    service: CRMService = Depends(get_service)
):
    """
    Create a new task.
    
    - **title**: Task title (required)
    - **description**: Task description
    - **status**: Task status (open, in_progress, completed)
    - **priority**: Task priority (low, medium, high)
    - **due_date**: Due date
    - Additional fields for associations
    """
    try:
        task_id = service.create_task(task.dict(exclude_unset=True))
        
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )
        
        created_task = service.get_task(task_id)
        return TaskResponse(**created_task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Get a task by ID.
    
    - **task_id**: Task ID
    """
    try:
        task = service.get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        return TaskResponse(**task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    lead_id: Optional[int] = Query(None),
    assigned_to: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    due_soon_days: Optional[int] = Query(None),
    service: CRMService = Depends(get_service)
):
    """
    List all tasks with optional filters.
    
    - **status**: Filter by status
    - **priority**: Filter by priority
    - **customer_id**: Filter by customer
    - **project_id**: Filter by project
    - **lead_id**: Filter by lead
    - **assigned_to**: Filter by assigned user
    - **overdue_only**: Show only overdue tasks
    - **due_soon_days**: Show tasks due in X days
    """
    try:
        filters = {
            'status': status,
            'priority': priority,
            'customer_id': customer_id,
            'project_id': project_id,
            'lead_id': lead_id,
            'assigned_to': assigned_to,
            'overdue_only': overdue_only,
            'due_soon_days': due_soon_days
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        tasks = service.list_tasks(filters)
        
        return TaskListResponse(
            tasks=[TaskResponse(**t) for t in tasks],
            total=len(tasks)
        )
    except Exception as e:
        logger.error(f"Unexpected error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    service: CRMService = Depends(get_service)
):
    """
    Update an existing task.
    
    - **task_id**: Task ID
    - All fields are optional
    """
    try:
        success = service.update_task(task_id, task.dict(exclude_unset=True))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        updated_task = service.get_task(task_id)
        return TaskResponse(**updated_task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/tasks/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Delete a task.
    
    - **task_id**: Task ID
    """
    try:
        success = service.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        return DeleteResponse(
            success=True,
            message=f"Task {task_id} deleted successfully",
            deleted_id=task_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/tasks/{task_id}/complete", response_model=SuccessResponse)
async def mark_task_completed(
    task_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Mark a task as completed.
    
    - **task_id**: Task ID
    """
    try:
        success = service.mark_task_completed(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        return SuccessResponse(
            success=True,
            message=f"Task {task_id} marked as completed",
            data={"task_id": task_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error marking task {task_id} as completed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/tasks/overdue", response_model=TaskListResponse)
async def get_overdue_tasks(
    service: CRMService = Depends(get_service)
):
    """
    Get all overdue tasks.
    """
    try:
        tasks = service.get_overdue_tasks()
        
        return TaskListResponse(
            tasks=[TaskResponse(**t) for t in tasks],
            total=len(tasks)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting overdue tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/tasks/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    service: CRMService = Depends(get_service)
):
    """
    Get task statistics.
    """
    try:
        stats = service.get_task_statistics()
        return TaskStatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Unexpected error getting task statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Activity/Note Management Endpoints ====================

@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: ActivityCreate,
    service: CRMService = Depends(get_service)
):
    """
    Create a new activity/note.
    
    - **customer_id**: Customer ID (required)
    - **activity_type**: Activity type (note, email, call, appointment, meeting, task, other)
    - **title**: Activity title (required)
    - **content**: Activity content
    - **created_by**: Creator name
    - **is_important**: Important flag
    """
    try:
        activity_id = service.create_activity(activity.dict(exclude_unset=True))
        
        if not activity_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create activity"
            )
        
        created_activity = service.get_activity(activity_id)
        return ActivityResponse(**created_activity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Get an activity by ID.
    
    - **activity_id**: Activity ID
    """
    try:
        activity = service.get_activity(activity_id)
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID {activity_id} not found"
            )
        
        return ActivityResponse(**activity)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting activity {activity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/activities/customer/{customer_id}", response_model=ActivityListResponse)
async def get_customer_activities(
    customer_id: int,
    activity_type: Optional[str] = Query(None),
    include_archived: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000),
    service: CRMService = Depends(get_service)
):
    """
    Get all activities for a customer.
    
    - **customer_id**: Customer ID
    - **activity_type**: Filter by activity type
    - **include_archived**: Include archived activities
    - **limit**: Maximum number of results
    """
    try:
        activities = service.get_customer_activities(
            customer_id=customer_id,
            activity_type=activity_type,
            include_archived=include_archived,
            limit=limit
        )
        
        return ActivityListResponse(
            activities=[ActivityResponse(**a) for a in activities],
            total=len(activities)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting activities for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    service: CRMService = Depends(get_service)
):
    """
    Update an existing activity.
    
    - **activity_id**: Activity ID
    - All fields are optional
    """
    try:
        success = service.update_activity(activity_id, activity.dict(exclude_unset=True))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID {activity_id} not found"
            )
        
        updated_activity = service.get_activity(activity_id)
        return ActivityResponse(**updated_activity)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating activity {activity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/activities/{activity_id}", response_model=DeleteResponse)
async def delete_activity(
    activity_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Delete an activity.
    
    - **activity_id**: Activity ID
    """
    try:
        success = service.delete_activity(activity_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID {activity_id} not found"
            )
        
        return DeleteResponse(
            success=True,
            message=f"Activity {activity_id} deleted successfully",
            deleted_id=activity_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting activity {activity_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/activities/search", response_model=ActivityListResponse)
async def search_activities(
    search_term: str = Query(..., min_length=1),
    customer_id: Optional[int] = Query(None),
    activity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    service: CRMService = Depends(get_service)
):
    """
    Search activities.
    
    - **search_term**: Search term (required)
    - **customer_id**: Filter by customer
    - **activity_type**: Filter by activity type
    - **limit**: Maximum number of results
    """
    try:
        activities = service.search_activities(
            search_term=search_term,
            customer_id=customer_id,
            activity_type=activity_type,
            limit=limit
        )
        
        return ActivityListResponse(
            activities=[ActivityResponse(**a) for a in activities],
            total=len(activities)
        )
    except Exception as e:
        logger.error(f"Unexpected error searching activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/activities/statistics/customer/{customer_id}", response_model=ActivityStatisticsResponse)
async def get_activity_statistics(
    customer_id: int,
    service: CRMService = Depends(get_service)
):
    """
    Get activity statistics for a customer.
    
    - **customer_id**: Customer ID
    """
    try:
        stats = service.get_activity_statistics(customer_id)
        return ActivityStatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Unexpected error getting activity statistics for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
