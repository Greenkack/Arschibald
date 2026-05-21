"""
Result History API Endpoints

Provides REST API endpoints for managing calculation result history.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.models.user_schemas import UserResponse
from backend.models.result_history_schemas import (
    ResultHistoryCreate, ResultHistoryUpdate, ResultHistoryResponse,
    ResultHistoryListResponse, ResultSearchRequest, ResultComparisonCreate,
    ResultComparisonResponse, ResultComparisonData, ResultShareCreate,
    ResultShareResponse, ResultVersionTree, ResultStatistics
)
from backend.services.result_history_service import ResultHistoryService


router = APIRouter(prefix="/result-history", tags=["Result History"])


# Result History CRUD

@router.post("/", response_model=ResultHistoryResponse, status_code=201)
def create_result(
    data: ResultHistoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new result history entry"""
    service = ResultHistoryService(db)
    result = service.create_result(current_user.id, data)
    
    # Add tags to response
    result_dict = ResultHistoryResponse.from_orm(result).dict()
    result_dict["tags"] = [tag.tag_name for tag in result.tags]
    
    return result_dict


@router.get("/{result_id}", response_model=ResultHistoryResponse)
def get_result(
    result_id: int,
    include_archived: bool = Query(False),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a result by ID"""
    service = ResultHistoryService(db)
    result = service.get_result(result_id, current_user.id, include_archived)
    
    # Add tags to response
    result_dict = ResultHistoryResponse.from_orm(result).dict()
    result_dict["tags"] = [tag.tag_name for tag in result.tags]
    
    return result_dict


@router.put("/{result_id}", response_model=ResultHistoryResponse)
def update_result(
    result_id: int,
    data: ResultHistoryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a result"""
    service = ResultHistoryService(db)
    result = service.update_result(result_id, current_user.id, data)
    
    # Add tags to response
    result_dict = ResultHistoryResponse.from_orm(result).dict()
    result_dict["tags"] = [tag.tag_name for tag in result.tags]
    
    return result_dict


@router.delete("/{result_id}", status_code=204)
def delete_result(
    result_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a result"""
    service = ResultHistoryService(db)
    service.delete_result(result_id, current_user.id)
    return None


# Result Search and Filtering

@router.post("/search", response_model=ResultHistoryListResponse)
def search_results(
    search: ResultSearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search and filter results"""
    service = ResultHistoryService(db)
    results, total = service.search_results(current_user.id, search)
    
    # Add tags to each result
    results_with_tags = []
    for result in results:
        result_dict = ResultHistoryResponse.from_orm(result).dict()
        result_dict["tags"] = [tag.tag_name for tag in result.tags]
        results_with_tags.append(result_dict)
    
    has_more = (search.page * search.page_size) < total
    
    return {
        "results": results_with_tags,
        "total": total,
        "page": search.page,
        "page_size": search.page_size,
        "has_more": has_more
    }


@router.get("/favorites/list", response_model=List[ResultHistoryResponse])
def get_favorites(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get favorite results"""
    service = ResultHistoryService(db)
    results = service.get_favorites(current_user.id, limit)
    
    # Add tags to each result
    results_with_tags = []
    for result in results:
        result_dict = ResultHistoryResponse.from_orm(result).dict()
        result_dict["tags"] = [tag.tag_name for tag in result.tags]
        results_with_tags.append(result_dict)
    
    return results_with_tags


@router.get("/recent/list", response_model=List[ResultHistoryResponse])
def get_recent_results(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent results"""
    service = ResultHistoryService(db)
    results = service.get_recent_results(current_user.id, limit)
    
    # Add tags to each result
    results_with_tags = []
    for result in results:
        result_dict = ResultHistoryResponse.from_orm(result).dict()
        result_dict["tags"] = [tag.tag_name for tag in result.tags]
        results_with_tags.append(result_dict)
    
    return results_with_tags


# Result Versioning

@router.get("/{result_id}/versions", response_model=ResultVersionTree)
def get_version_tree(
    result_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get version tree for a result"""
    service = ResultHistoryService(db)
    tree = service.get_version_tree(result_id, current_user.id)
    
    return {
        "current": {
            "id": tree["current"].id,
            "version": tree["current"].version,
            "result_name": tree["current"].result_name,
            "created_at": tree["current"].created_at,
            "parent_id": tree["current"].parent_id,
            "has_children": len(tree["children"]) > 0
        },
        "parent": {
            "id": tree["parent"].id,
            "version": tree["parent"].version,
            "result_name": tree["parent"].result_name,
            "created_at": tree["parent"].created_at,
            "parent_id": tree["parent"].parent_id,
            "has_children": True
        } if tree["parent"] else None,
        "children": [
            {
                "id": child.id,
                "version": child.version,
                "result_name": child.result_name,
                "created_at": child.created_at,
                "parent_id": child.parent_id,
                "has_children": False
            }
            for child in tree["children"]
        ],
        "all_versions": [
            {
                "id": version.id,
                "version": version.version,
                "result_name": version.result_name,
                "created_at": version.created_at,
                "parent_id": version.parent_id,
                "has_children": any(v.parent_id == version.id for v in tree["all_versions"])
            }
            for version in tree["all_versions"]
        ]
    }


@router.post("/{result_id}/versions", response_model=ResultHistoryResponse, status_code=201)
def create_version(
    result_id: int,
    data: ResultHistoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new version of a result"""
    service = ResultHistoryService(db)
    result = service.create_version(result_id, current_user.id, data)
    
    # Add tags to response
    result_dict = ResultHistoryResponse.from_orm(result).dict()
    result_dict["tags"] = [tag.tag_name for tag in result.tags]
    
    return result_dict


# Result Comparison

@router.post("/comparisons", response_model=ResultComparisonResponse, status_code=201)
def create_comparison(
    data: ResultComparisonCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a result comparison"""
    service = ResultHistoryService(db)
    comparison = service.create_comparison(current_user.id, data)
    
    # Get results for comparison
    results = [service.get_result(rid, current_user.id) for rid in comparison.result_ids]
    
    comparison_dict = ResultComparisonResponse.from_orm(comparison).dict()
    comparison_dict["results"] = [
        {**ResultHistoryResponse.from_orm(r).dict(), "tags": [tag.tag_name for tag in r.tags]}
        for r in results
    ]
    
    return comparison_dict


@router.get("/comparisons/{comparison_id}", response_model=ResultComparisonResponse)
def get_comparison(
    comparison_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a comparison by ID"""
    service = ResultHistoryService(db)
    comparison = service.get_comparison(comparison_id, current_user.id)
    
    # Get results for comparison
    results = [service.get_result(rid, current_user.id) for rid in comparison.result_ids]
    
    comparison_dict = ResultComparisonResponse.from_orm(comparison).dict()
    comparison_dict["results"] = [
        {**ResultHistoryResponse.from_orm(r).dict(), "tags": [tag.tag_name for tag in r.tags]}
        for r in results
    ]
    
    return comparison_dict


@router.get("/comparisons/list/all", response_model=List[ResultComparisonResponse])
def get_comparisons(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comparisons for a user"""
    service = ResultHistoryService(db)
    comparisons = service.get_comparisons(current_user.id)
    
    # Get results for each comparison
    comparisons_with_results = []
    for comparison in comparisons:
        results = [service.get_result(rid, current_user.id) for rid in comparison.result_ids]
        comparison_dict = ResultComparisonResponse.from_orm(comparison).dict()
        comparison_dict["results"] = [
            {**ResultHistoryResponse.from_orm(r).dict(), "tags": [tag.tag_name for tag in r.tags]}
            for r in results
        ]
        comparisons_with_results.append(comparison_dict)
    
    return comparisons_with_results


@router.delete("/comparisons/{comparison_id}", status_code=204)
def delete_comparison(
    comparison_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comparison"""
    service = ResultHistoryService(db)
    service.delete_comparison(comparison_id, current_user.id)
    return None


@router.post("/compare", response_model=ResultComparisonData)
def compare_results(
    result_ids: List[int],
    metrics: Optional[List[str]] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare multiple results"""
    service = ResultHistoryService(db)
    comparison_data = service.compare_results(result_ids, current_user.id, metrics)
    
    # Format response
    results_with_tags = []
    for result in comparison_data["results"]:
        result_dict = ResultHistoryResponse.from_orm(result).dict()
        result_dict["tags"] = [tag.tag_name for tag in result.tags]
        results_with_tags.append(result_dict)
    
    return {
        "comparison_id": 0,  # Temporary comparison
        "comparison_name": "Temporary Comparison",
        "results": results_with_tags,
        "differences": comparison_data["differences"],
        "summary": comparison_data["summary"]
    }


# Result Sharing

@router.post("/shares", response_model=ResultShareResponse, status_code=201)
def create_share(
    data: ResultShareCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a result share"""
    service = ResultHistoryService(db)
    share = service.create_share(current_user.id, data)
    return ResultShareResponse.from_orm(share)


@router.get("/shares/token/{share_token}", response_model=ResultHistoryResponse)
def get_shared_result(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get a shared result by token"""
    service = ResultHistoryService(db)
    share = service.get_share_by_token(share_token)
    
    # Get the result (bypass user check for shared results)
    result = db.query(service.db.query(ResultHistory).filter(
        ResultHistory.id == share.result_id
    ).first())
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # Add tags to response
    result_dict = ResultHistoryResponse.from_orm(result).dict()
    result_dict["tags"] = [tag.tag_name for tag in result.tags]
    
    return result_dict


@router.get("/{result_id}/shares", response_model=List[ResultShareResponse])
def get_shares_for_result(
    result_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all shares for a result"""
    service = ResultHistoryService(db)
    shares = service.get_shares_for_result(result_id, current_user.id)
    return [ResultShareResponse.from_orm(share) for share in shares]


@router.delete("/shares/{share_id}", status_code=204)
def delete_share(
    share_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a share"""
    service = ResultHistoryService(db)
    service.delete_share(share_id, current_user.id)
    return None


# Statistics

@router.get("/statistics/summary", response_model=ResultStatistics)
def get_statistics(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get result statistics for the current user"""
    service = ResultHistoryService(db)
    stats = service.get_statistics(current_user.id)
    
    # Add tags to recent results
    recent_with_tags = []
    for result in stats["recent_results"]:
        result_dict = ResultHistoryResponse.from_orm(result).dict()
        result_dict["tags"] = [tag.tag_name for tag in result.tags]
        recent_with_tags.append(result_dict)
    
    stats["recent_results"] = recent_with_tags
    stats["most_compared"] = []  # TODO: Implement most compared logic
    
    return stats
