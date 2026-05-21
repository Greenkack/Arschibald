"""
Quick Calculation as Lead API

Provides REST API for quick calculations that can be saved as CRM leads:
- Quick calculation feature
- Save rough estimates as CRM leads
- Convert quick calculations to full projects
- Track lead source and conversion
- Lead scoring based on calculation results

Requirements: funktionen.txt - "Schnellkalkulationen als Leads"
Task: 262. Quick Calculation as Lead
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/quick-calc", tags=["Quick Calculation"])


# ==================== Enums ====================

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    QUICK_CALC = "quick_calculation"
    WEBSITE = "website"
    REFERRAL = "referral"
    PHONE = "phone"
    EMAIL = "email"


class CalculationType(str, Enum):
    PV_ONLY = "pv_only"
    HEATPUMP_ONLY = "heatpump_only"
    COMBINED = "combined"


class LeadPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HOT = "hot"


# ==================== Pydantic Models ====================

class QuickCalcInput(BaseModel):
    """Input for quick calculation"""
    calculation_type: CalculationType = CalculationType.PV_ONLY
    # PV inputs
    roof_area_m2: Optional[float] = Field(default=None, ge=10, le=1000)
    roof_orientation: Optional[str] = "south"
    roof_tilt: Optional[float] = Field(default=30, ge=0, le=90)
    # Heatpump inputs
    building_area_m2: Optional[float] = Field(default=None, ge=50, le=1000)
    building_year: Optional[int] = Field(default=None, ge=1900, le=2025)
    current_heating: Optional[str] = "gas"
    # Common
    annual_consumption_kwh: Optional[float] = Field(default=4000, ge=1000, le=50000)
    electricity_price_eur: Optional[float] = Field(default=0.30, ge=0.10, le=1.0)


class QuickCalcResult(BaseModel):
    """Result of quick calculation"""
    calculation_id: str
    calculation_type: CalculationType
    # PV results
    pv_power_kwp: Optional[float] = None
    pv_annual_yield_kwh: Optional[float] = None
    pv_self_consumption_percent: Optional[float] = None
    pv_investment_eur: Optional[float] = None
    pv_annual_savings_eur: Optional[float] = None
    # Heatpump results
    hp_power_kw: Optional[float] = None
    hp_annual_cop: Optional[float] = None
    hp_investment_eur: Optional[float] = None
    hp_annual_savings_eur: Optional[float] = None
    # Combined
    total_investment_eur: float
    total_annual_savings_eur: float
    payback_years: float
    co2_savings_kg: float
    lead_score: int = Field(ge=0, le=100)
    created_at: datetime


class LeadContact(BaseModel):
    """Lead contact information"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None


class SaveAsLeadRequest(BaseModel):
    """Request to save calculation as lead"""
    calculation_id: str
    contact: LeadContact
    preferred_contact_method: str = "email"
    interested_in_consultation: bool = True
    newsletter_consent: bool = False


class Lead(BaseModel):
    """CRM Lead from quick calculation"""
    id: str
    calculation_id: str
    contact: LeadContact
    calculation_result: QuickCalcResult
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.MEDIUM
    source: LeadSource = LeadSource.QUICK_CALC
    score: int
    assigned_to: Optional[str] = None
    project_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    converted_at: Optional[datetime] = None


class ConvertToProjectRequest(BaseModel):
    """Request to convert lead to full project"""
    lead_id: str
    project_name: Optional[str] = None
    assign_to: Optional[str] = None
    start_detailed_calculation: bool = True


# ==================== Mock Data Store ====================

_calculations_store: Dict[str, QuickCalcResult] = {}
_leads_store: Dict[str, Lead] = {}


# ==================== Helper Functions ====================

def generate_id(prefix: str) -> str:
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def calculate_lead_score(result: QuickCalcResult, contact: LeadContact) -> int:
    """Calculate lead score based on calculation results and contact info"""
    score = 50  # Base score
    
    # Investment size factor
    if result.total_investment_eur > 30000:
        score += 20
    elif result.total_investment_eur > 20000:
        score += 15
    elif result.total_investment_eur > 10000:
        score += 10
    
    # Payback period factor
    if result.payback_years < 8:
        score += 15
    elif result.payback_years < 12:
        score += 10
    elif result.payback_years < 15:
        score += 5
    
    # Contact completeness
    if contact.email:
        score += 5
    if contact.phone:
        score += 5
    if contact.address:
        score += 5
    
    return min(100, score)


def determine_priority(score: int) -> LeadPriority:
    """Determine lead priority based on score"""
    if score >= 85:
        return LeadPriority.HOT
    elif score >= 70:
        return LeadPriority.HIGH
    elif score >= 50:
        return LeadPriority.MEDIUM
    return LeadPriority.LOW


def perform_quick_calculation(input_data: QuickCalcInput) -> QuickCalcResult:
    """Perform quick calculation"""
    calc_id = generate_id("calc")
    
    pv_power = pv_yield = pv_self = pv_invest = pv_savings = None
    hp_power = hp_cop = hp_invest = hp_savings = None
    total_invest = 0
    total_savings = 0
    
    # PV calculation
    if input_data.calculation_type in [CalculationType.PV_ONLY, CalculationType.COMBINED]:
        if input_data.roof_area_m2:
            pv_power = round(input_data.roof_area_m2 * 0.18, 1)  # ~180W/m²
            pv_yield = round(pv_power * 950, 0)  # ~950 kWh/kWp
            pv_self = round(min(70, 30 + (input_data.annual_consumption_kwh / pv_yield) * 40), 1)
            pv_invest = round(pv_power * 1400, 0)  # ~1400€/kWp
            pv_savings = round(pv_yield * pv_self / 100 * input_data.electricity_price_eur, 0)
            total_invest += pv_invest
            total_savings += pv_savings
    
    # Heatpump calculation
    if input_data.calculation_type in [CalculationType.HEATPUMP_ONLY, CalculationType.COMBINED]:
        if input_data.building_area_m2:
            # Simplified heat load calculation
            heat_factor = 0.08 if input_data.building_year and input_data.building_year > 2000 else 0.12
            hp_power = round(input_data.building_area_m2 * heat_factor, 1)
            hp_cop = 3.5
            hp_invest = round(hp_power * 2500 + 5000, 0)  # Base + per kW
            # Savings vs gas
            gas_cost = input_data.building_area_m2 * 80 * 0.08  # 80 kWh/m², 0.08€/kWh gas
            hp_cost = (input_data.building_area_m2 * 80 / hp_cop) * input_data.electricity_price_eur
            hp_savings = round(gas_cost - hp_cost, 0)
            total_invest += hp_invest
            total_savings += hp_savings
    
    # Calculate payback
    payback = round(total_invest / total_savings, 1) if total_savings > 0 else 99
    
    # CO2 savings
    co2_savings = round((pv_yield or 0) * 0.4 + (hp_savings or 0) * 2, 0)
    
    # Lead score
    lead_score = 50
    if total_invest > 20000:
        lead_score += 20
    if payback < 10:
        lead_score += 15
    if input_data.calculation_type == CalculationType.COMBINED:
        lead_score += 10
    
    return QuickCalcResult(
        calculation_id=calc_id,
        calculation_type=input_data.calculation_type,
        pv_power_kwp=pv_power,
        pv_annual_yield_kwh=pv_yield,
        pv_self_consumption_percent=pv_self,
        pv_investment_eur=pv_invest,
        pv_annual_savings_eur=pv_savings,
        hp_power_kw=hp_power,
        hp_annual_cop=hp_cop,
        hp_investment_eur=hp_invest,
        hp_annual_savings_eur=hp_savings,
        total_investment_eur=total_invest,
        total_annual_savings_eur=total_savings,
        payback_years=payback,
        co2_savings_kg=co2_savings,
        lead_score=min(100, lead_score),
        created_at=datetime.now()
    )


# ==================== API Endpoints ====================

@router.post("/calculate")
async def quick_calculate(input_data: QuickCalcInput):
    """Perform quick calculation without saving."""
    result = perform_quick_calculation(input_data)
    _calculations_store[result.calculation_id] = result
    
    return {
        "result": result,
        "can_save_as_lead": True,
        "recommendation": "Basierend auf Ihren Angaben empfehlen wir eine detaillierte Beratung."
    }


@router.get("/calculation/{calculation_id}")
async def get_calculation(calculation_id: str):
    """Get a specific calculation result."""
    if calculation_id not in _calculations_store:
        raise HTTPException(status_code=404, detail="Berechnung nicht gefunden")
    
    return {"result": _calculations_store[calculation_id]}


@router.post("/save-as-lead")
async def save_as_lead(request: SaveAsLeadRequest):
    """Save quick calculation as CRM lead."""
    if request.calculation_id not in _calculations_store:
        raise HTTPException(status_code=404, detail="Berechnung nicht gefunden")
    
    calc_result = _calculations_store[request.calculation_id]
    lead_id = generate_id("lead")
    score = calculate_lead_score(calc_result, request.contact)
    
    lead = Lead(
        id=lead_id,
        calculation_id=request.calculation_id,
        contact=request.contact,
        calculation_result=calc_result,
        status=LeadStatus.NEW,
        priority=determine_priority(score),
        source=LeadSource.QUICK_CALC,
        score=score,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _leads_store[lead_id] = lead
    
    return {
        "lead": lead,
        "message": f"Lead erfolgreich erstellt mit Score {score}",
        "next_steps": [
            "Kontaktaufnahme innerhalb von 24h",
            "Detaillierte Bedarfsanalyse",
            "Vor-Ort-Termin vereinbaren"
        ]
    }


@router.get("/leads")
async def get_leads(
    status: Optional[LeadStatus] = None,
    priority: Optional[LeadPriority] = None,
    min_score: Optional[int] = None,
    limit: int = Query(default=50, le=100)
):
    """Get all leads with optional filters."""
    leads = list(_leads_store.values())
    
    if status:
        leads = [l for l in leads if l.status == status]
    if priority:
        leads = [l for l in leads if l.priority == priority]
    if min_score:
        leads = [l for l in leads if l.score >= min_score]
    
    leads.sort(key=lambda l: (-l.score, l.created_at))
    
    return {
        "leads": leads[:limit],
        "total": len(leads),
        "by_status": {s.value: len([l for l in leads if l.status == s]) for s in LeadStatus},
        "by_priority": {p.value: len([l for l in leads if l.priority == p]) for p in LeadPriority}
    }


@router.get("/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get a specific lead."""
    if lead_id not in _leads_store:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    return {"lead": _leads_store[lead_id]}


@router.put("/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, status: LeadStatus):
    """Update lead status."""
    if lead_id not in _leads_store:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    lead = _leads_store[lead_id]
    lead.status = status
    lead.updated_at = datetime.now()
    
    if status == LeadStatus.CONVERTED:
        lead.converted_at = datetime.now()
    
    return {"lead": lead, "updated": True}


@router.post("/leads/{lead_id}/convert")
async def convert_to_project(lead_id: str, request: ConvertToProjectRequest):
    """Convert lead to full project."""
    if lead_id not in _leads_store:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    lead = _leads_store[lead_id]
    project_id = generate_id("proj")
    
    lead.status = LeadStatus.CONVERTED
    lead.project_id = project_id
    lead.converted_at = datetime.now()
    lead.updated_at = datetime.now()
    
    if request.assign_to:
        lead.assigned_to = request.assign_to
    
    return {
        "lead": lead,
        "project_id": project_id,
        "project_name": request.project_name or f"Projekt {lead.contact.name}",
        "message": "Lead erfolgreich in Projekt konvertiert",
        "next_steps": [
            "Detaillierte Kalkulation starten",
            "Angebot erstellen",
            "Vor-Ort-Termin planen"
        ]
    }


@router.get("/statistics")
async def get_statistics():
    """Get quick calculation and lead statistics."""
    leads = list(_leads_store.values())
    
    converted = [l for l in leads if l.status == LeadStatus.CONVERTED]
    conversion_rate = len(converted) / len(leads) * 100 if leads else 0
    
    avg_score = sum(l.score for l in leads) / len(leads) if leads else 0
    avg_investment = sum(l.calculation_result.total_investment_eur for l in leads) / len(leads) if leads else 0
    
    return {
        "total_calculations": len(_calculations_store),
        "total_leads": len(leads),
        "conversion_rate_percent": round(conversion_rate, 1),
        "average_lead_score": round(avg_score, 1),
        "average_investment_eur": round(avg_investment, 0),
        "leads_by_type": {
            t.value: len([l for l in leads if l.calculation_result.calculation_type == t])
            for t in CalculationType
        },
        "hot_leads": len([l for l in leads if l.priority == LeadPriority.HOT])
    }


@router.get("/health/check")
async def health_check():
    """Health check for quick calculation service."""
    return {
        "status": "healthy",
        "service": "quick-calculation",
        "calculations_count": len(_calculations_store),
        "leads_count": len(_leads_store),
        "timestamp": datetime.now().isoformat()
    }
