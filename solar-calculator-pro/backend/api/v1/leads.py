"""
Lead Management API Endpoints
RESTful API for lead capture, scoring, assignment, and conversion tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.dependencies import get_db
from backend.services.lead_service import LeadService
from backend.models.lead_schemas import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse,
    LeadActivityCreate, LeadActivityUpdate, LeadActivityResponse,
    LeadScoringRuleCreate, LeadScoringRuleUpdate, LeadScoringRuleResponse,
    LeadAssignmentRuleCreate, LeadAssignmentRuleUpdate, LeadAssignmentRuleResponse,
    LeadNurturingCampaignCreate, LeadNurturingCampaignUpdate, LeadNurturingCampaignResponse,
    LeadScoreBreakdown, LeadDashboardMetrics, LeadConversionTrackingResponse,
    LeadSourceAnalyticsResponse, LeadAssignRequest,
    LeadStatusEnum, LeadSourceEnum, LeadPriorityEnum
)

router = APIRouter(prefix="/leads", tags=["leads"])


# Lead CRUD Endpoints

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lead
    
    - **first_name**: Lead's first name (required)
    - **last_name**: Lead's last name (required)
    - **email**: Lead's email address (required, unique)
    - **phone**: Lead's phone number (optional)
    - **company**: Lead's company name (optional)
    - **source**: Lead source (required)
    - **priority**: Lead priority (default: medium)
    - **estimated_value**: Estimated deal value (default: 0)
    """
    service = LeadService(db)
    lead = service.create_lead(lead_data)
    return lead


@router.get("/", response_model=LeadListResponse)
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[LeadStatusEnum] = None,
    source: Optional[LeadSourceEnum] = None,
    priority: Optional[LeadPriorityEnum] = None,
    assigned_to_id: Optional[int] = None,
    min_score: Optional[int] = Query(None, ge=0),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get leads with filtering and pagination
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by lead status
    - **source**: Filter by lead source
    - **priority**: Filter by lead priority
    - **assigned_to_id**: Filter by assigned user
    - **min_score**: Filter by minimum score
    - **search**: Search in name, email, company
    """
    service = LeadService(db)
    leads, total = service.get_leads(
        skip=skip,
        limit=limit,
        status=status,
        source=source,
        priority=priority,
        assigned_to_id=assigned_to_id,
        min_score=min_score,
        search=search
    )
    
    total_pages = (total + limit - 1) // limit
    
    return LeadListResponse(
        leads=leads,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead by ID"""
    service = LeadService(db)
    lead = service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db)
):
    """Update a lead"""
    service = LeadService(db)
    lead = service.update_lead(lead_id, lead_data)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lead"""
    service = LeadService(db)
    success = service.delete_lead(lead_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )


# Lead Scoring Endpoints

@router.get("/{lead_id}/score", response_model=LeadScoreBreakdown)
async def get_lead_score_breakdown(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed score breakdown for a lead"""
    service = LeadService(db)
    breakdown = service.get_lead_score_breakdown(lead_id)
    
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return breakdown


@router.post("/recalculate-scores", response_model=dict)
async def recalculate_all_scores(
    db: Session = Depends(get_db)
):
    """Recalculate scores for all leads"""
    service = LeadService(db)
    count = service.recalculate_all_scores()
    
    return {"message": f"Recalculated scores for {count} leads"}


# Lead Assignment Endpoints

@router.post("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(
    lead_id: int,
    assignment: LeadAssignRequest,
    db: Session = Depends(get_db)
):
    """Manually assign a lead to a user"""
    service = LeadService(db)
    lead = service.assign_lead(lead_id, assignment.assign_to_user_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return lead


# Lead Activity Endpoints

@router.post("/{lead_id}/activities", response_model=LeadActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_lead_activity(
    lead_id: int,
    activity_data: LeadActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new activity for a lead"""
    # Ensure lead_id matches
    activity_data.lead_id = lead_id
    
    service = LeadService(db)
    activity = service.create_activity(activity_data)
    
    return activity


@router.get("/{lead_id}/activities", response_model=List[LeadActivityResponse])
async def get_lead_activities(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get all activities for a lead"""
    service = LeadService(db)
    activities = service.get_lead_activities(lead_id)
    
    return activities


# Lead Nurturing Endpoints

@router.post("/{lead_id}/nurturing", response_model=LeadNurturingCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_nurturing_campaign(
    lead_id: int,
    campaign_data: LeadNurturingCampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a nurturing campaign for a lead"""
    # Ensure lead_id matches
    campaign_data.lead_id = lead_id
    
    service = LeadService(db)
    campaign = service.create_nurturing_campaign(campaign_data)
    
    return campaign


@router.get("/nurturing/active", response_model=List[LeadNurturingCampaignResponse])
async def get_active_nurturing_campaigns(
    db: Session = Depends(get_db)
):
    """Get all active nurturing campaigns"""
    service = LeadService(db)
    campaigns = service.get_active_nurturing_campaigns()
    
    return campaigns


# Lead Conversion Endpoints

@router.post("/{lead_id}/convert", response_model=LeadResponse)
async def convert_lead(
    lead_id: int,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Convert a lead to a customer"""
    service = LeadService(db)
    lead = service.convert_lead(lead_id, customer_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    return lead


@router.get("/conversion/tracking", response_model=List[LeadConversionTrackingResponse])
async def get_conversion_tracking(
    start_date: datetime = Query(..., description="Start date for tracking period"),
    end_date: datetime = Query(..., description="End date for tracking period"),
    db: Session = Depends(get_db)
):
    """Get lead conversion tracking data"""
    service = LeadService(db)
    tracking_data = service.get_conversion_tracking(start_date, end_date)
    
    return tracking_data


# Analytics Endpoints

@router.get("/analytics/dashboard", response_model=LeadDashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db)
):
    """Get lead dashboard metrics"""
    service = LeadService(db)
    metrics = service.get_dashboard_metrics()
    
    return metrics


@router.get("/analytics/sources", response_model=List[LeadSourceAnalyticsResponse])
async def get_source_analytics(
    start_date: datetime = Query(..., description="Start date for analytics period"),
    end_date: datetime = Query(..., description="End date for analytics period"),
    db: Session = Depends(get_db)
):
    """Get lead source analytics"""
    service = LeadService(db)
    analytics = service.get_source_analytics(start_date, end_date)
    
    return analytics


# Scoring Rules Management

@router.post("/scoring-rules", response_model=LeadScoringRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_scoring_rule(
    rule_data: LeadScoringRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new lead scoring rule"""
    from backend.models.lead_models import LeadScoringRule
    
    rule = LeadScoringRule(**rule_data.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/scoring-rules", response_model=List[LeadScoringRuleResponse])
async def get_scoring_rules(
    active_only: bool = Query(True, description="Return only active rules"),
    db: Session = Depends(get_db)
):
    """Get all lead scoring rules"""
    from backend.models.lead_models import LeadScoringRule
    
    query = db.query(LeadScoringRule)
    if active_only:
        query = query.filter(LeadScoringRule.active == True)
    
    rules = query.order_by(LeadScoringRule.priority.desc()).all()
    return rules


# Assignment Rules Management

@router.post("/assignment-rules", response_model=LeadAssignmentRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment_rule(
    rule_data: LeadAssignmentRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new lead assignment rule"""
    from backend.models.lead_models import LeadAssignmentRule
    import json
    
    rule = LeadAssignmentRule(
        **rule_data.dict(exclude={'conditions'}),
        conditions=json.dumps(rule_data.conditions)
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/assignment-rules", response_model=List[LeadAssignmentRuleResponse])
async def get_assignment_rules(
    active_only: bool = Query(True, description="Return only active rules"),
    db: Session = Depends(get_db)
):
    """Get all lead assignment rules"""
    from backend.models.lead_models import LeadAssignmentRule
    
    query = db.query(LeadAssignmentRule)
    if active_only:
        query = query.filter(LeadAssignmentRule.active == True)
    
    rules = query.order_by(LeadAssignmentRule.priority.desc()).all()
    return rules
