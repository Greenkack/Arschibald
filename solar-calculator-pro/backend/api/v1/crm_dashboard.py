"""
CRM Dashboard API

Provides REST API for CRM dashboard:
- CRM overview dashboard
- Sales activities and offer statistics
- Pipeline status (offers in preparation, open, closed)

Requirements: funktionen.txt - "CRM-System"
Task: 260. CRM Dashboard Implementation
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/crm/dashboard", tags=["CRM Dashboard"])


# ==================== Enums ====================

class OfferStatus(str, Enum):
    """Offer status"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    EXPIRED = "expired"


class ActivityType(str, Enum):
    """Activity type"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    OFFER_SENT = "offer_sent"
    OFFER_WON = "offer_won"
    NOTE = "note"


# ==================== Pydantic Models ====================

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_customers: int
    active_offers: int
    offers_this_month: int
    revenue_this_month_eur: float
    conversion_rate_percent: float
    avg_deal_size_eur: float


class PipelineStage(BaseModel):
    """Pipeline stage data"""
    stage: str
    label: str
    count: int
    value_eur: float
    color: str


class RecentActivity(BaseModel):
    """Recent activity"""
    id: str
    type: ActivityType
    description: str
    customer_name: str
    timestamp: datetime
    user: str


class TopCustomer(BaseModel):
    """Top customer"""
    id: str
    name: str
    total_revenue_eur: float
    offers_count: int
    last_activity: datetime


class SalesMetric(BaseModel):
    """Sales metric"""
    label: str
    value: float
    unit: str
    change_percent: float
    trend: str


class DashboardResponse(BaseModel):
    """Complete dashboard response"""
    stats: DashboardStats
    pipeline: List[PipelineStage]
    recent_activities: List[RecentActivity]
    top_customers: List[TopCustomer]
    sales_metrics: List[SalesMetric]
    chart_data: Dict[str, Any]


# ==================== Sample Data ====================

def generate_sample_stats() -> DashboardStats:
    """Generate sample dashboard statistics"""
    return DashboardStats(
        total_customers=156,
        active_offers=23,
        offers_this_month=12,
        revenue_this_month_eur=87500.00,
        conversion_rate_percent=34.5,
        avg_deal_size_eur=18750.00
    )


def generate_pipeline_data() -> List[PipelineStage]:
    """Generate sample pipeline data"""
    return [
        PipelineStage(stage="draft", label="Entwurf", count=8, value_eur=145000, color="#9CA3AF"),
        PipelineStage(stage="sent", label="Versendet", count=12, value_eur=234000, color="#3B82F6"),
        PipelineStage(stage="viewed", label="Angesehen", count=7, value_eur=156000, color="#8B5CF6"),
        PipelineStage(stage="negotiation", label="Verhandlung", count=5, value_eur=112000, color="#F59E0B"),
        PipelineStage(stage="won", label="Gewonnen", count=15, value_eur=287500, color="#10B981"),
        PipelineStage(stage="lost", label="Verloren", count=6, value_eur=98000, color="#EF4444")
    ]


def generate_recent_activities() -> List[RecentActivity]:
    """Generate sample recent activities"""
    activities = [
        RecentActivity(
            id="act-1", type=ActivityType.OFFER_WON, description="Angebot #2024-089 gewonnen",
            customer_name="Familie Müller", timestamp=datetime.now() - timedelta(hours=2), user="Max Mustermann"
        ),
        RecentActivity(
            id="act-2", type=ActivityType.CALL, description="Beratungsgespräch geführt",
            customer_name="Herr Schmidt", timestamp=datetime.now() - timedelta(hours=5), user="Anna Weber"
        ),
        RecentActivity(
            id="act-3", type=ActivityType.OFFER_SENT, description="Angebot #2024-092 versendet",
            customer_name="Familie Bauer", timestamp=datetime.now() - timedelta(hours=8), user="Max Mustermann"
        ),
        RecentActivity(
            id="act-4", type=ActivityType.MEETING, description="Vor-Ort-Termin durchgeführt",
            customer_name="Firma Meier GmbH", timestamp=datetime.now() - timedelta(days=1), user="Thomas Klein"
        ),
        RecentActivity(
            id="act-5", type=ActivityType.EMAIL, description="Nachfass-E-Mail gesendet",
            customer_name="Herr Wagner", timestamp=datetime.now() - timedelta(days=1, hours=3), user="Anna Weber"
        )
    ]
    return activities


def generate_top_customers() -> List[TopCustomer]:
    """Generate sample top customers"""
    return [
        TopCustomer(id="cust-1", name="Firma Meier GmbH", total_revenue_eur=45000, offers_count=3, last_activity=datetime.now() - timedelta(days=2)),
        TopCustomer(id="cust-2", name="Familie Müller", total_revenue_eur=32500, offers_count=2, last_activity=datetime.now() - timedelta(hours=2)),
        TopCustomer(id="cust-3", name="Herr Dr. Fischer", total_revenue_eur=28000, offers_count=1, last_activity=datetime.now() - timedelta(days=5)),
        TopCustomer(id="cust-4", name="Familie Schneider", total_revenue_eur=24500, offers_count=2, last_activity=datetime.now() - timedelta(days=7)),
        TopCustomer(id="cust-5", name="Bauunternehmen Weber", total_revenue_eur=21000, offers_count=1, last_activity=datetime.now() - timedelta(days=10))
    ]


def generate_sales_metrics() -> List[SalesMetric]:
    """Generate sample sales metrics"""
    return [
        SalesMetric(label="Umsatz", value=87500, unit="EUR", change_percent=12.5, trend="up"),
        SalesMetric(label="Angebote", value=12, unit="Stück", change_percent=8.3, trend="up"),
        SalesMetric(label="Abschlussquote", value=34.5, unit="%", change_percent=-2.1, trend="down"),
        SalesMetric(label="Ø Auftragswert", value=18750, unit="EUR", change_percent=5.2, trend="up")
    ]


def generate_chart_data() -> Dict[str, Any]:
    """Generate sample chart data"""
    months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    current_month = datetime.now().month
    
    return {
        "revenue_by_month": {
            "labels": months[:current_month],
            "data": [45000, 52000, 48000, 61000, 55000, 72000, 68000, 75000, 82000, 79000, 87500][:current_month],
            "previous_year": [42000, 48000, 45000, 55000, 51000, 65000, 62000, 70000, 75000, 72000, 80000][:current_month]
        },
        "offers_by_status": {
            "labels": ["Entwurf", "Versendet", "Angesehen", "Verhandlung", "Gewonnen", "Verloren"],
            "data": [8, 12, 7, 5, 15, 6],
            "colors": ["#9CA3AF", "#3B82F6", "#8B5CF6", "#F59E0B", "#10B981", "#EF4444"]
        },
        "conversion_funnel": {
            "stages": ["Anfragen", "Beratung", "Angebot", "Verhandlung", "Abschluss"],
            "values": [100, 75, 45, 25, 15]
        },
        "activity_by_type": {
            "labels": ["Anrufe", "E-Mails", "Termine", "Angebote"],
            "data": [45, 78, 23, 34]
        }
    }


# ==================== API Endpoints ====================

@router.get("/", response_model=DashboardResponse)
async def get_dashboard():
    """
    Get complete CRM dashboard data.
    """
    return DashboardResponse(
        stats=generate_sample_stats(),
        pipeline=generate_pipeline_data(),
        recent_activities=generate_recent_activities(),
        top_customers=generate_top_customers(),
        sales_metrics=generate_sales_metrics(),
        chart_data=generate_chart_data()
    )


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    """Get dashboard statistics."""
    return generate_sample_stats()


@router.get("/pipeline", response_model=List[PipelineStage])
async def get_pipeline():
    """Get pipeline data."""
    return generate_pipeline_data()


@router.get("/activities", response_model=List[RecentActivity])
async def get_recent_activities(limit: int = Query(10, ge=1, le=50)):
    """Get recent activities."""
    activities = generate_recent_activities()
    return activities[:limit]


@router.get("/top-customers", response_model=List[TopCustomer])
async def get_top_customers(limit: int = Query(5, ge=1, le=20)):
    """Get top customers by revenue."""
    customers = generate_top_customers()
    return customers[:limit]


@router.get("/metrics", response_model=List[SalesMetric])
async def get_sales_metrics():
    """Get sales metrics."""
    return generate_sales_metrics()


@router.get("/charts")
async def get_chart_data():
    """Get chart data for dashboard."""
    return generate_chart_data()


@router.get("/summary")
async def get_quick_summary():
    """Get quick summary for dashboard header."""
    stats = generate_sample_stats()
    return {
        "total_customers": stats.total_customers,
        "active_offers": stats.active_offers,
        "revenue_this_month": f"{stats.revenue_this_month_eur:,.0f} €",
        "conversion_rate": f"{stats.conversion_rate_percent:.1f}%",
        "pending_tasks": 7,
        "upcoming_appointments": 3
    }


@router.get("/health/check")
async def health_check():
    """Health check for CRM dashboard service."""
    return {
        "status": "healthy",
        "service": "crm-dashboard",
        "timestamp": datetime.now().isoformat()
    }
