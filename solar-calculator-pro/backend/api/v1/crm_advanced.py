"""
CRM Advanced API Endpoints

This module provides REST API endpoints for the CRM Advanced Service.

Requirements: 1.3, 6.1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Import the CRM Advanced Service
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from services.crm_advanced_service import CRMAdvancedService


router = APIRouter(prefix="/api/v1/crm-advanced", tags=["CRM Advanced"])


# Dependency to get CRM service instance
def get_crm_service() -> CRMAdvancedService:
    """Get CRM Advanced Service instance."""
    return CRMAdvancedService()


# ==================== Pydantic Models ====================

class LeadScoreRequest(BaseModel):
    """Request model for lead scoring."""
    lead_id: int = Field(..., description="ID of the lead")


class LeadScoreWeightsUpdate(BaseModel):
    """Request model for updating lead score weights."""
    weights: Dict[str, float] = Field(..., description="Scoring weights")


class PipelineAutomationRequest(BaseModel):
    """Request model for pipeline automation."""
    lead_id: int = Field(..., description="ID of the lead")
    rules: Dict[str, Any] = Field(..., description="Automation rules")


class EmailCampaignCreate(BaseModel):
    """Request model for creating email campaign."""
    name: str = Field(..., description="Campaign name")
    subject: str = Field(..., description="Email subject")
    content: str = Field(..., description="Email content")
    template_id: Optional[int] = Field(None, description="Template ID")
    segment_id: Optional[int] = Field(None, description="Target segment ID")


class EmailCampaignSend(BaseModel):
    """Request model for sending campaign."""
    campaign_id: int = Field(..., description="Campaign ID")
    recipient_ids: List[int] = Field(..., description="List of recipient IDs")


class CustomerSegmentCreate(BaseModel):
    """Request model for creating customer segment."""
    name: str = Field(..., description="Segment name")
    criteria: Dict[str, Any] = Field(..., description="Segmentation criteria")
    description: Optional[str] = Field(None, description="Segment description")


class ForecastRequest(BaseModel):
    """Request model for sales forecast."""
    period: str = Field(..., description="Forecast period (month, quarter, year)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Forecast parameters")


class ContractCreate(BaseModel):
    """Request model for creating contract."""
    customer_id: int = Field(..., description="Customer ID")
    contract_type: str = Field(..., description="Contract type")
    start_date: datetime = Field(..., description="Contract start date")
    end_date: datetime = Field(..., description="Contract end date")
    value: float = Field(..., description="Contract value")
    terms: Dict[str, Any] = Field(..., description="Contract terms")


class WarrantyRegister(BaseModel):
    """Request model for registering warranty."""
    product_id: int = Field(..., description="Product ID")
    customer_id: int = Field(..., description="Customer ID")
    purchase_date: datetime = Field(..., description="Purchase date")
    warranty_period_months: int = Field(..., description="Warranty period in months")
    terms: Optional[Dict[str, Any]] = Field(None, description="Warranty terms")


class FeedbackSubmit(BaseModel):
    """Request model for submitting feedback."""
    customer_id: int = Field(..., description="Customer ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    category: str = Field(..., description="Feedback category")
    comment: str = Field(..., description="Feedback comment")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GeocodeRequest(BaseModel):
    """Request model for geocoding."""
    address: str = Field(..., description="Address to geocode")


class CustomersInAreaRequest(BaseModel):
    """Request model for getting customers in area."""
    center: Dict[str, float] = Field(..., description="Center coordinates (lat, lon)")
    radius_km: float = Field(..., description="Radius in kilometers")


class KBArticleCreate(BaseModel):
    """Request model for creating KB article."""
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    category: str = Field(..., description="Article category")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    author_id: int = Field(..., description="Author ID")


# ==================== Lead Scoring Endpoints ====================

@router.post("/lead-scoring/calculate")
async def calculate_lead_score(
    request: LeadScoreRequest,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Calculate lead score for a specific lead.
    
    Returns lead score with breakdown of scoring factors.
    """
    try:
        result = crm_service.calculate_lead_score(request.lead_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-scoring/scores")
async def get_lead_scores(
    min_score: Optional[int] = Query(None, description="Minimum score filter"),
    max_score: Optional[int] = Query(None, description="Maximum score filter"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get lead scores with optional filtering.
    """
    try:
        filters = {}
        if min_score is not None:
            filters['min_score'] = min_score
        if max_score is not None:
            filters['max_score'] = max_score
        
        result = crm_service.get_lead_scores(filters if filters else None)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/lead-scoring/weights")
async def update_lead_score_weights(
    request: LeadScoreWeightsUpdate,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Update lead scoring weights.
    """
    try:
        result = crm_service.update_lead_score_weights(request.weights)
        return {"success": True, "data": {"updated": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Pipeline Automation Endpoints ====================

@router.post("/pipeline/automate")
async def automate_pipeline_stage(
    request: PipelineAutomationRequest,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Automatically move lead through pipeline stages based on rules.
    """
    try:
        result = crm_service.automate_pipeline_stage(request.lead_id, request.rules)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Email Campaign Endpoints ====================

@router.post("/email-campaigns")
async def create_email_campaign(
    request: EmailCampaignCreate,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Create a new email campaign.
    """
    try:
        campaign_id = crm_service.create_email_campaign(request.dict())
        return {"success": True, "data": {"campaign_id": campaign_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email-campaigns/send")
async def send_campaign_email(
    request: EmailCampaignSend,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Send campaign emails to recipients.
    """
    try:
        result = crm_service.send_campaign_email(request.campaign_id, request.recipient_ids)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email-campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get analytics for an email campaign.
    """
    try:
        result = crm_service.get_campaign_analytics(campaign_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Customer Segmentation Endpoints ====================

@router.post("/segments")
async def create_customer_segment(
    request: CustomerSegmentCreate,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Create a customer segment.
    """
    try:
        segment_id = crm_service.create_customer_segment(request.dict())
        return {"success": True, "data": {"segment_id": segment_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments/{segment_id}/customers")
async def get_segment_customers(
    segment_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get all customers in a segment.
    """
    try:
        result = crm_service.get_segment_customers(segment_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments/{segment_id}/analyze")
async def analyze_segment(
    segment_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Analyze a customer segment.
    """
    try:
        result = crm_service.analyze_segment(segment_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Forecasting Endpoints ====================

@router.post("/forecasting/sales")
async def generate_sales_forecast(
    request: ForecastRequest,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Generate sales forecast for specified period.
    """
    try:
        result = crm_service.generate_sales_forecast(request.period, request.parameters)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasting/pipeline")
async def get_pipeline_forecast(
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get forecast based on current sales pipeline.
    """
    try:
        result = crm_service.get_pipeline_forecast()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecasting/accuracy/{period}")
async def analyze_forecast_accuracy(
    period: str,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Analyze accuracy of past forecasts.
    """
    try:
        result = crm_service.analyze_forecast_accuracy(period)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Contract Management Endpoints ====================

@router.post("/contracts")
async def create_contract(
    request: ContractCreate,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Create a new contract.
    """
    try:
        contract_id = crm_service.create_contract(request.dict())
        return {"success": True, "data": {"contract_id": contract_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/{contract_id}")
async def get_contract(
    contract_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get contract details.
    """
    try:
        result = crm_service.get_contract(contract_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contracts/expiring")
async def get_expiring_contracts(
    days: int = Query(30, description="Number of days to look ahead"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get contracts expiring within specified days.
    """
    try:
        result = crm_service.get_expiring_contracts(days)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Warranty Tracking Endpoints ====================

@router.post("/warranties")
async def register_warranty(
    request: WarrantyRegister,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Register a new warranty.
    """
    try:
        warranty_id = crm_service.register_warranty(request.dict())
        return {"success": True, "data": {"warranty_id": warranty_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/warranties/{warranty_id}")
async def get_warranty_status(
    warranty_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get warranty status and details.
    """
    try:
        result = crm_service.get_warranty_status(warranty_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/warranties/active")
async def get_active_warranties(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get all active warranties.
    """
    try:
        result = crm_service.get_active_warranties(customer_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Customer Feedback Endpoints ====================

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackSubmit,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Submit customer feedback.
    """
    try:
        feedback_id = crm_service.submit_feedback(request.dict())
        return {"success": True, "data": {"feedback_id": feedback_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/{feedback_id}")
async def get_feedback(
    feedback_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get feedback details.
    """
    try:
        result = crm_service.get_feedback(feedback_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/analyze")
async def analyze_feedback(
    category: Optional[str] = Query(None, description="Filter by category"),
    rating: Optional[int] = Query(None, description="Filter by rating"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Analyze customer feedback.
    """
    try:
        filters = {}
        if category:
            filters['category'] = category
        if rating:
            filters['rating'] = rating
        
        result = crm_service.analyze_feedback(filters if filters else None)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/trends")
async def get_feedback_trends(
    period: str = Query("month", description="Time period for trends"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get feedback trends over time.
    """
    try:
        result = crm_service.get_feedback_trends(period)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Geo Mapping Endpoints ====================

@router.post("/geo/geocode")
async def geocode_address(
    request: GeocodeRequest,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Convert address to geographic coordinates.
    """
    try:
        result = crm_service.geocode_address(request.address)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geo/customers-in-area")
async def get_customers_in_area(
    request: CustomersInAreaRequest,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get customers within specified radius of a location.
    """
    try:
        result = crm_service.get_customers_in_area(request.center, request.radius_km)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Knowledge Base Endpoints ====================

@router.post("/knowledge-base/articles")
async def create_kb_article(
    request: KBArticleCreate,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Create a knowledge base article.
    """
    try:
        article_id = crm_service.create_kb_article(request.dict())
        return {"success": True, "data": {"article_id": article_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/search")
async def search_kb(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Search knowledge base.
    """
    try:
        filters = {'category': category} if category else None
        result = crm_service.search_kb(query, filters)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/articles/{article_id}")
async def get_kb_article(
    article_id: int,
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get knowledge base article.
    """
    try:
        result = crm_service.get_kb_article(article_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/popular")
async def get_popular_kb_articles(
    limit: int = Query(10, description="Maximum number of articles"),
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Get most popular knowledge base articles.
    """
    try:
        result = crm_service.get_popular_kb_articles(limit)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check Endpoint ====================

@router.get("/health")
async def health_check(
    crm_service: CRMAdvancedService = Depends(get_crm_service)
) -> Dict[str, Any]:
    """
    Check health of all CRM modules.
    """
    try:
        result = crm_service.health_check()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
