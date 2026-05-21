"""
Sales Pipeline API Endpoints
RESTful API for pipeline management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.dependencies import get_db, get_current_user
from backend.services.pipeline_service import PipelineService
from backend.models.pipeline_schemas import (
    PipelineStageCreate, PipelineStageUpdate, PipelineStageResponse, PipelineStageListResponse,
    OpportunityCreate, OpportunityUpdate, OpportunityResponse, OpportunityListResponse,
    OpportunityStageChange, OpportunityWin, OpportunityLoss,
    OpportunityActivityCreate, OpportunityActivityResponse,
    OpportunityProductCreate, OpportunityProductResponse,
    PipelineAnalytics, WinLossAnalysis, PipelineForecastData,
    PipelineAutomationCreate, PipelineAutomationUpdate, PipelineAutomationResponse
)
from backend.models.pipeline_models import OpportunityStatus

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


# ==================== Pipeline Stages ====================

@router.post("/stages", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline_stage(
    stage_data: PipelineStageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new pipeline stage"""
    service = PipelineService(db)
    return service.create_stage(stage_data, current_user['id'])


@router.get("/stages", response_model=PipelineStageListResponse)
async def get_pipeline_stages(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all pipeline stages"""
    service = PipelineService(db)
    stages = service.get_stages(include_inactive)
    return PipelineStageListResponse(stages=stages, total=len(stages))


@router.get("/stages/{stage_id}", response_model=PipelineStageResponse)
async def get_pipeline_stage(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pipeline stage by ID"""
    service = PipelineService(db)
    return service.get_stage(stage_id)


@router.put("/stages/{stage_id}", response_model=PipelineStageResponse)
async def update_pipeline_stage(
    stage_id: int,
    stage_data: PipelineStageUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update pipeline stage"""
    service = PipelineService(db)
    return service.update_stage(stage_id, stage_data)


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline_stage(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete pipeline stage"""
    service = PipelineService(db)
    service.delete_stage(stage_id)


@router.post("/stages/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_pipeline_stages(
    stage_orders: List[dict],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reorder pipeline stages"""
    service = PipelineService(db)
    service.reorder_stages(stage_orders)


# ==================== Opportunities ====================

@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opp_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new opportunity"""
    service = PipelineService(db)
    return service.create_opportunity(opp_data)


@router.get("/opportunities", response_model=OpportunityListResponse)
async def get_opportunities(
    stage_id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    status: Optional[OpportunityStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get opportunities with filters"""
    service = PipelineService(db)
    skip = (page - 1) * page_size
    opportunities, total = service.get_opportunities(
        stage_id=stage_id,
        owner_id=owner_id,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    return OpportunityListResponse(
        opportunities=opportunities,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get opportunity by ID"""
    service = PipelineService(db)
    return service.get_opportunity(opportunity_id)


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opp_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update opportunity"""
    service = PipelineService(db)
    return service.update_opportunity(opportunity_id, opp_data)


@router.post("/opportunities/{opportunity_id}/change-stage", response_model=OpportunityResponse)
async def change_opportunity_stage(
    opportunity_id: int,
    stage_change: OpportunityStageChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Move opportunity to different stage"""
    service = PipelineService(db)
    return service.change_stage(opportunity_id, stage_change, current_user['id'])


@router.post("/opportunities/{opportunity_id}/win", response_model=OpportunityResponse)
async def win_opportunity(
    opportunity_id: int,
    win_data: OpportunityWin,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark opportunity as won"""
    service = PipelineService(db)
    return service.win_opportunity(opportunity_id, win_data)


@router.post("/opportunities/{opportunity_id}/lose", response_model=OpportunityResponse)
async def lose_opportunity(
    opportunity_id: int,
    loss_data: OpportunityLoss,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark opportunity as lost"""
    service = PipelineService(db)
    return service.lose_opportunity(opportunity_id, loss_data)


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete opportunity"""
    service = PipelineService(db)
    service.delete_opportunity(opportunity_id)


# ==================== Activities ====================

@router.post("/opportunities/{opportunity_id}/activities", response_model=OpportunityActivityResponse)
async def create_activity(
    opportunity_id: int,
    activity_data: OpportunityActivityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create activity for opportunity"""
    # TODO: Implement activity creation
    pass


@router.get("/opportunities/{opportunity_id}/activities", response_model=List[OpportunityActivityResponse])
async def get_activities(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get activities for opportunity"""
    # TODO: Implement activity retrieval
    pass


# ==================== Products ====================

@router.post("/opportunities/{opportunity_id}/products", response_model=OpportunityProductResponse)
async def add_product(
    opportunity_id: int,
    product_data: OpportunityProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add product to opportunity"""
    # TODO: Implement product addition
    pass


@router.get("/opportunities/{opportunity_id}/products", response_model=List[OpportunityProductResponse])
async def get_products(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get products for opportunity"""
    # TODO: Implement product retrieval
    pass


# ==================== Analytics ====================

@router.get("/analytics", response_model=PipelineAnalytics)
async def get_pipeline_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive pipeline analytics"""
    service = PipelineService(db)
    return service.get_pipeline_analytics(start_date, end_date)


@router.get("/analytics/win-loss", response_model=WinLossAnalysis)
async def get_win_loss_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get win/loss analysis"""
    service = PipelineService(db)
    return service.get_win_loss_analysis(start_date, end_date)


@router.post("/forecast", response_model=PipelineForecastData)
async def generate_forecast(
    period_start: datetime,
    period_end: datetime,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate pipeline forecast"""
    service = PipelineService(db)
    return service.generate_forecast(period_start, period_end, current_user['id'])


# ==================== Automation ====================

@router.post("/automations", response_model=PipelineAutomationResponse)
async def create_automation(
    automation_data: PipelineAutomationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create pipeline automation rule"""
    # TODO: Implement automation creation
    pass


@router.get("/automations", response_model=List[PipelineAutomationResponse])
async def get_automations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all automation rules"""
    # TODO: Implement automation retrieval
    pass


@router.put("/automations/{automation_id}", response_model=PipelineAutomationResponse)
async def update_automation(
    automation_id: int,
    automation_data: PipelineAutomationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update automation rule"""
    # TODO: Implement automation update
    pass


@router.delete("/automations/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete automation rule"""
    # TODO: Implement automation deletion
    pass
