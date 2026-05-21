"""
Search API Endpoints

Provides REST API endpoints for search and filter functionality
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.services.search_service import (
    SearchService,
    FilterService,
    SavedSearchService
)


router = APIRouter(prefix="/search", tags=["search"])


# Request/Response Models

class GlobalSearchRequest(BaseModel):
    """Request model for global search"""
    query: str = Field(..., min_length=2, description="Search query")
    entity_types: Optional[List[str]] = Field(
        None,
        description="Entity types to search (projects, customers, products, etc.)"
    )
    limit: int = Field(50, ge=1, le=100, description="Maximum results per entity type")
    fuzzy: bool = Field(True, description="Enable fuzzy matching")


class SearchResult(BaseModel):
    """Search result item"""
    id: int
    entity_type: str
    title: str
    description: Optional[str]
    metadata: Dict[str, Any]
    relevance_score: float


class GlobalSearchResponse(BaseModel):
    """Response model for global search"""
    results: Dict[str, List[Dict[str, Any]]]
    total_results: int
    query: str
    execution_time_ms: float


class FilterRequest(BaseModel):
    """Request model for filtering"""
    entity_type: str = Field(..., description="Entity type to filter")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Results per page")


class FilterResponse(BaseModel):
    """Response model for filtering"""
    results: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SavedSearchCreate(BaseModel):
    """Request model for creating saved search"""
    name: str = Field(..., min_length=1, max_length=100)
    entity_type: str
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = Field(False)


class SavedSearchUpdate(BaseModel):
    """Request model for updating saved search"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class SavedSearchResponse(BaseModel):
    """Response model for saved search"""
    id: int
    user_id: int
    name: str
    entity_type: str
    query: str
    filters: Dict[str, Any]
    is_public: bool
    created_at: str
    updated_at: str


class SearchSuggestionResponse(BaseModel):
    """Response model for search suggestions"""
    suggestions: List[str]
    query: str


class SearchAnalyticsResponse(BaseModel):
    """Response model for search analytics"""
    total_searches: int
    recent_searches: List[str]
    popular_searches: List[Dict[str, Any]]
    search_trends: Dict[str, Any]


# API Endpoints

@router.post("/global", response_model=GlobalSearchResponse)
async def global_search(
    request: GlobalSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform global search across all entity types
    
    - **query**: Search query string (minimum 2 characters)
    - **entity_types**: Optional list of entity types to search
    - **limit**: Maximum results per entity type (1-100)
    - **fuzzy**: Enable fuzzy matching for typo tolerance
    """
    import time
    start_time = time.time()
    
    search_service = SearchService(db)
    
    results = search_service.global_search(
        query=request.query,
        entity_types=request.entity_types,
        limit=request.limit,
        fuzzy=request.fuzzy
    )
    
    # Calculate total results
    total_results = sum(len(items) for items in results.values())
    
    execution_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return GlobalSearchResponse(
        results=results,
        total_results=total_results,
        query=request.query,
        execution_time_ms=round(execution_time, 2)
    )


@router.post("/filter", response_model=FilterResponse)
async def apply_filters(
    request: FilterRequest,
    db: Session = Depends(get_db)
):
    """
    Apply advanced filters to entity query
    
    - **entity_type**: Type of entity to filter
    - **filters**: Dictionary of filter criteria
    - **sort_by**: Field to sort results by
    - **sort_order**: Sort order (asc or desc)
    - **page**: Page number (1-indexed)
    - **page_size**: Number of results per page (1-100)
    """
    filter_service = FilterService(db)
    
    result = filter_service.apply_filters(
        entity_type=request.entity_type,
        filters=request.filters,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        page=request.page,
        page_size=request.page_size
    )
    
    return FilterResponse(**result)


@router.get("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    
    - **query**: Partial search query (minimum 2 characters)
    - **limit**: Maximum number of suggestions (1-20)
    """
    search_service = SearchService(db)
    
    suggestions = search_service.get_search_suggestions(
        partial_query=query,
        limit=limit
    )
    
    return SearchSuggestionResponse(
        suggestions=suggestions,
        query=query
    )


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    db: Session = Depends(get_db)
):
    """
    Get search analytics data
    
    Returns statistics about search usage including:
    - Total number of searches
    - Recent searches
    - Popular search terms
    - Search trends
    """
    search_service = SearchService(db)
    
    analytics = search_service.get_search_analytics()
    
    return SearchAnalyticsResponse(**analytics)


@router.get("/filter-options/{entity_type}")
async def get_filter_options(
    entity_type: str,
    db: Session = Depends(get_db)
):
    """
    Get available filter options for entity type
    
    - **entity_type**: Type of entity (projects, customers, products, etc.)
    
    Returns available filter fields and their possible values
    """
    filter_service = FilterService(db)
    
    options = filter_service.get_filter_options(entity_type)
    
    if not options:
        raise HTTPException(
            status_code=404,
            detail=f"No filter options found for entity type: {entity_type}"
        )
    
    return options


# Saved Searches Endpoints

@router.post("/saved", response_model=SavedSearchResponse)
async def create_saved_search(
    request: SavedSearchCreate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Save a search for later use
    
    - **name**: Name for the saved search
    - **entity_type**: Type of entity being searched
    - **query**: Search query string
    - **filters**: Filter criteria
    - **is_public**: Whether search is public (default: false)
    """
    saved_search_service = SavedSearchService(db)
    
    saved_search = saved_search_service.save_search(
        user_id=user_id,
        name=request.name,
        entity_type=request.entity_type,
        query=request.query,
        filters=request.filters,
        is_public=request.is_public
    )
    
    return SavedSearchResponse(**saved_search)


@router.get("/saved", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    user_id: int = Query(..., description="User ID"),
    include_public: bool = Query(True, description="Include public searches"),
    db: Session = Depends(get_db)
):
    """
    Get saved searches for user
    
    - **user_id**: ID of user
    - **include_public**: Include public saved searches (default: true)
    """
    saved_search_service = SavedSearchService(db)
    
    searches = saved_search_service.get_saved_searches(
        user_id=user_id,
        include_public=include_public
    )
    
    return [SavedSearchResponse(**search) for search in searches]


@router.put("/saved/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    request: SavedSearchUpdate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Update a saved search
    
    - **search_id**: ID of search to update
    - **user_id**: ID of user (for authorization)
    - Updates can include: name, query, filters, is_public
    """
    saved_search_service = SavedSearchService(db)
    
    updates = request.dict(exclude_unset=True)
    
    updated_search = saved_search_service.update_saved_search(
        search_id=search_id,
        user_id=user_id,
        updates=updates
    )
    
    if not updated_search:
        raise HTTPException(
            status_code=404,
            detail=f"Saved search not found: {search_id}"
        )
    
    return SavedSearchResponse(**updated_search)


@router.delete("/saved/{search_id}")
async def delete_saved_search(
    search_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Delete a saved search
    
    - **search_id**: ID of search to delete
    - **user_id**: ID of user (for authorization)
    """
    saved_search_service = SavedSearchService(db)
    
    success = saved_search_service.delete_saved_search(
        search_id=search_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Saved search not found: {search_id}"
        )
    
    return {"message": "Saved search deleted successfully"}
