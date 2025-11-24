"""
Result History Pydantic Schemas

Defines request/response schemas for result history API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResultType(str, Enum):
    """Result type enumeration"""
    SOLAR = "solar"
    HEATPUMP = "heatpump"
    COMBINED = "combined"


class ComparisonType(str, Enum):
    """Comparison type enumeration"""
    SIDE_BY_SIDE = "side-by-side"
    OVERLAY = "overlay"
    DIFFERENCE = "difference"


# Result History Schemas

class ResultHistoryCreate(BaseModel):
    """Schema for creating a result history entry"""
    result_type: ResultType
    result_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    project_id: Optional[int] = None
    parent_id: Optional[int] = None
    tags: Optional[List[str]] = []


class ResultHistoryUpdate(BaseModel):
    """Schema for updating a result history entry"""
    result_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    tags: Optional[List[str]] = None


class ResultHistoryResponse(BaseModel):
    """Schema for result history response"""
    id: int
    user_id: int
    project_id: Optional[int]
    result_type: str
    result_name: str
    description: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    version: int
    parent_id: Optional[int]
    is_favorite: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    
    class Config:
        from_attributes = True


class ResultHistoryListResponse(BaseModel):
    """Schema for paginated result history list"""
    results: List[ResultHistoryResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Result Search Schemas

class ResultSearchRequest(BaseModel):
    """Schema for searching results"""
    query: Optional[str] = None
    result_type: Optional[ResultType] = None
    tags: Optional[List[str]] = []
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    project_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", pattern="^(created_at|updated_at|result_name)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# Result Comparison Schemas

class ResultComparisonCreate(BaseModel):
    """Schema for creating a result comparison"""
    comparison_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    result_ids: List[int] = Field(..., min_items=2, max_items=10)
    comparison_type: ComparisonType = ComparisonType.SIDE_BY_SIDE
    metrics_to_compare: Optional[List[str]] = None


class ResultComparisonResponse(BaseModel):
    """Schema for result comparison response"""
    id: int
    user_id: int
    comparison_name: str
    description: Optional[str]
    result_ids: List[int]
    comparison_type: str
    metrics_to_compare: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    results: List[ResultHistoryResponse] = []
    
    class Config:
        from_attributes = True


class ResultComparisonData(BaseModel):
    """Schema for comparison data analysis"""
    comparison_id: int
    comparison_name: str
    results: List[ResultHistoryResponse]
    differences: Dict[str, Any]
    summary: Dict[str, Any]


# Result Share Schemas

class ResultShareCreate(BaseModel):
    """Schema for creating a result share"""
    result_id: int
    shared_with_user_id: Optional[int] = None
    is_public: bool = False
    can_edit: bool = False
    expires_at: Optional[datetime] = None


class ResultShareResponse(BaseModel):
    """Schema for result share response"""
    id: int
    result_id: int
    shared_by_user_id: int
    shared_with_user_id: Optional[int]
    share_token: str
    is_public: bool
    can_edit: bool
    expires_at: Optional[datetime]
    created_at: datetime
    accessed_at: Optional[datetime]
    access_count: int
    
    class Config:
        from_attributes = True


# Result Version Schemas

class ResultVersionResponse(BaseModel):
    """Schema for result version information"""
    id: int
    version: int
    result_name: str
    created_at: datetime
    parent_id: Optional[int]
    has_children: bool


class ResultVersionTree(BaseModel):
    """Schema for result version tree"""
    current: ResultVersionResponse
    parent: Optional[ResultVersionResponse]
    children: List[ResultVersionResponse]
    all_versions: List[ResultVersionResponse]


# Statistics Schemas

class ResultStatistics(BaseModel):
    """Schema for result statistics"""
    total_results: int
    results_by_type: Dict[str, int]
    favorite_count: int
    archived_count: int
    recent_results: List[ResultHistoryResponse]
    most_compared: List[ResultHistoryResponse]
    tags_usage: Dict[str, int]
