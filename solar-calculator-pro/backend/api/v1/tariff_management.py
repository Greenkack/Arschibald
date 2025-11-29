"""
Tariff Management API

Provides REST API for tariff management:
- Electricity tariff management
- Feed-in tariff management (by year, type)
- Gas/oil price management for WP comparison
- Regional tariff differences
- Tariff history tracking

Requirements: funktionen.txt - "Tarifverwaltung"
Task: 277. Tariff Management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import uuid

router = APIRouter(prefix="/admin/tariffs", tags=["Tariff Management"])


# ==================== Enums ====================

class TariffType(str, Enum):
    ELECTRICITY = "electricity"
    FEED_IN = "feed_in"
    GAS = "gas"
    OIL = "oil"
    DISTRICT_HEATING = "district_heating"


class FeedInCategory(str, Enum):
    SMALL = "small"  # < 10 kWp
    MEDIUM = "medium"  # 10-40 kWp
    LARGE = "large"  # 40-100 kWp
    VERY_LARGE = "very_large"  # > 100 kWp


class TariffStatus(str, Enum):
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"


# ==================== Pydantic Models ====================

class ElectricityTariff(BaseModel):
    """Electricity tariff"""
    id: str
    name: str
    provider: str
    price_per_kwh_eur: float
    base_fee_eur_month: float = 0
    region: str = "Deutschland"
    valid_from: date
    valid_until: Optional[date] = None
    status: TariffStatus = TariffStatus.ACTIVE
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeedInTariff(BaseModel):
    """Feed-in tariff (Einspeisevergütung)"""
    id: str
    category: FeedInCategory
    min_kwp: float
    max_kwp: float
    price_per_kwh_eur: float
    commissioning_from: date
    commissioning_until: Optional[date] = None
    full_feed_in: bool = False  # Volleinspeisung
    partial_feed_in: bool = True  # Überschusseinspeisung
    source: str = "Bundesnetzagentur"
    status: TariffStatus = TariffStatus.ACTIVE
    created_at: datetime
    updated_at: datetime


class FuelTariff(BaseModel):
    """Fuel tariff (Gas, Oil, District Heating)"""
    id: str
    tariff_type: TariffType
    name: str
    price_per_kwh_eur: float
    efficiency: float = 0.9  # Heating system efficiency
    co2_factor_kg_kwh: float
    region: str = "Deutschland"
    valid_from: date
    valid_until: Optional[date] = None
    status: TariffStatus = TariffStatus.ACTIVE
    created_at: datetime
    updated_at: datetime


class TariffHistory(BaseModel):
    """Tariff history entry"""
    id: str
    tariff_type: TariffType
    price_per_kwh_eur: float
    recorded_date: date
    source: Optional[str] = None


class TariffComparison(BaseModel):
    """Tariff comparison result"""
    electricity_cost_eur: float
    gas_cost_eur: float
    oil_cost_eur: float
    heatpump_cost_eur: float
    savings_vs_gas_eur: float
    savings_vs_oil_eur: float
    annual_consumption_kwh: float


class CreateElectricityTariffRequest(BaseModel):
    """Request to create electricity tariff"""
    name: str
    provider: str
    price_per_kwh_eur: float = Field(ge=0.01, le=1.0)
    base_fee_eur_month: float = Field(default=0, ge=0)
    region: str = "Deutschland"
    valid_from: date
    valid_until: Optional[date] = None


class CreateFeedInTariffRequest(BaseModel):
    """Request to create feed-in tariff"""
    category: FeedInCategory
    min_kwp: float
    max_kwp: float
    price_per_kwh_eur: float = Field(ge=0.01, le=0.20)
    commissioning_from: date
    commissioning_until: Optional[date] = None
    full_feed_in: bool = False
    partial_feed_in: bool = True


# ==================== Mock Data Store ====================

_electricity_tariffs: Dict[str, ElectricityTariff] = {}
_feed_in_tariffs: Dict[str, FeedInTariff] = {}
_fuel_tariffs: Dict[str, FuelTariff] = {}
_tariff_history: List[TariffHistory] = []


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def init_default_tariffs():
    """Initialize default tariffs"""
    now = datetime.now()
    today = date.today()
    
    # Default electricity tariff
    elec_id = generate_id("elec")
    _electricity_tariffs[elec_id] = ElectricityTariff(
        id=elec_id,
        name="Standard Haushaltsstrom",
        provider="Stadtwerke",
        price_per_kwh_eur=0.30,
        base_fee_eur_month=12.50,
        valid_from=date(2024, 1, 1),
        created_at=now,
        updated_at=now
    )
    
    # Feed-in tariffs (2024)
    feed_in_data = [
        (FeedInCategory.SMALL, 0, 10, 0.0820),
        (FeedInCategory.MEDIUM, 10, 40, 0.0710),
        (FeedInCategory.LARGE, 40, 100, 0.0580),
        (FeedInCategory.VERY_LARGE, 100, 1000, 0.0580),
    ]
    
    for cat, min_kw, max_kw, price in feed_in_data:
        fi_id = generate_id("fi")
        _feed_in_tariffs[fi_id] = FeedInTariff(
            id=fi_id,
            category=cat,
            min_kwp=min_kw,
            max_kwp=max_kw,
            price_per_kwh_eur=price,
            commissioning_from=date(2024, 8, 1),
            created_at=now,
            updated_at=now
        )
    
    # Fuel tariffs
    fuel_data = [
        (TariffType.GAS, "Erdgas", 0.08, 0.9, 0.201),
        (TariffType.OIL, "Heizöl", 0.10, 0.85, 0.266),
        (TariffType.DISTRICT_HEATING, "Fernwärme", 0.12, 0.98, 0.150),
    ]
    
    for t_type, name, price, eff, co2 in fuel_data:
        fuel_id = generate_id("fuel")
        _fuel_tariffs[fuel_id] = FuelTariff(
            id=fuel_id,
            tariff_type=t_type,
            name=name,
            price_per_kwh_eur=price,
            efficiency=eff,
            co2_factor_kg_kwh=co2,
            valid_from=date(2024, 1, 1),
            created_at=now,
            updated_at=now
        )


init_default_tariffs()


# ==================== API Endpoints ====================

@router.get("/electricity")
async def get_electricity_tariffs(region: Optional[str] = None, active_only: bool = True):
    """Get electricity tariffs."""
    tariffs = list(_electricity_tariffs.values())
    
    if region:
        tariffs = [t for t in tariffs if t.region == region]
    if active_only:
        tariffs = [t for t in tariffs if t.status == TariffStatus.ACTIVE]
    
    return {"tariffs": tariffs, "total": len(tariffs)}


@router.post("/electricity")
async def create_electricity_tariff(request: CreateElectricityTariffRequest):
    """Create electricity tariff."""
    tariff_id = generate_id("elec")
    now = datetime.now()
    
    tariff = ElectricityTariff(
        id=tariff_id,
        name=request.name,
        provider=request.provider,
        price_per_kwh_eur=request.price_per_kwh_eur,
        base_fee_eur_month=request.base_fee_eur_month,
        region=request.region,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        created_at=now,
        updated_at=now
    )
    
    _electricity_tariffs[tariff_id] = tariff
    return {"tariff": tariff, "created": True}


@router.get("/feed-in")
async def get_feed_in_tariffs(
    category: Optional[FeedInCategory] = None,
    system_size_kwp: Optional[float] = None
):
    """Get feed-in tariffs."""
    tariffs = list(_feed_in_tariffs.values())
    
    if category:
        tariffs = [t for t in tariffs if t.category == category]
    if system_size_kwp:
        tariffs = [t for t in tariffs if t.min_kwp <= system_size_kwp < t.max_kwp]
    
    return {"tariffs": tariffs, "total": len(tariffs)}


@router.post("/feed-in")
async def create_feed_in_tariff(request: CreateFeedInTariffRequest):
    """Create feed-in tariff."""
    tariff_id = generate_id("fi")
    now = datetime.now()
    
    tariff = FeedInTariff(
        id=tariff_id,
        category=request.category,
        min_kwp=request.min_kwp,
        max_kwp=request.max_kwp,
        price_per_kwh_eur=request.price_per_kwh_eur,
        commissioning_from=request.commissioning_from,
        commissioning_until=request.commissioning_until,
        full_feed_in=request.full_feed_in,
        partial_feed_in=request.partial_feed_in,
        created_at=now,
        updated_at=now
    )
    
    _feed_in_tariffs[tariff_id] = tariff
    return {"tariff": tariff, "created": True}


@router.get("/feed-in/lookup")
async def lookup_feed_in_tariff(system_size_kwp: float, commissioning_date: Optional[date] = None):
    """Lookup applicable feed-in tariff."""
    comm_date = commissioning_date or date.today()
    
    for tariff in _feed_in_tariffs.values():
        if tariff.min_kwp <= system_size_kwp < tariff.max_kwp:
            if tariff.commissioning_from <= comm_date:
                if tariff.commissioning_until is None or comm_date <= tariff.commissioning_until:
                    return {
                        "tariff": tariff,
                        "applicable": True,
                        "annual_income_estimate": round(system_size_kwp * 950 * 0.35 * tariff.price_per_kwh_eur, 2)
                    }
    
    raise HTTPException(status_code=404, detail="Kein passender Tarif gefunden")


@router.get("/fuel")
async def get_fuel_tariffs(tariff_type: Optional[TariffType] = None):
    """Get fuel tariffs (gas, oil, district heating)."""
    tariffs = list(_fuel_tariffs.values())
    
    if tariff_type:
        tariffs = [t for t in tariffs if t.tariff_type == tariff_type]
    
    return {"tariffs": tariffs, "total": len(tariffs)}


@router.post("/compare")
async def compare_heating_costs(
    annual_heat_demand_kwh: float,
    electricity_price_eur: float = 0.30,
    heatpump_cop: float = 3.5
):
    """Compare heating costs across different energy sources."""
    # Get current fuel prices
    gas_price = 0.08
    oil_price = 0.10
    
    for tariff in _fuel_tariffs.values():
        if tariff.tariff_type == TariffType.GAS and tariff.status == TariffStatus.ACTIVE:
            gas_price = tariff.price_per_kwh_eur
        elif tariff.tariff_type == TariffType.OIL and tariff.status == TariffStatus.ACTIVE:
            oil_price = tariff.price_per_kwh_eur
    
    # Calculate costs
    gas_cost = annual_heat_demand_kwh / 0.9 * gas_price
    oil_cost = annual_heat_demand_kwh / 0.85 * oil_price
    heatpump_cost = annual_heat_demand_kwh / heatpump_cop * electricity_price_eur
    
    return TariffComparison(
        electricity_cost_eur=round(annual_heat_demand_kwh * electricity_price_eur, 2),
        gas_cost_eur=round(gas_cost, 2),
        oil_cost_eur=round(oil_cost, 2),
        heatpump_cost_eur=round(heatpump_cost, 2),
        savings_vs_gas_eur=round(gas_cost - heatpump_cost, 2),
        savings_vs_oil_eur=round(oil_cost - heatpump_cost, 2),
        annual_consumption_kwh=annual_heat_demand_kwh
    )


@router.get("/history")
async def get_tariff_history(
    tariff_type: TariffType,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get tariff history."""
    history = [h for h in _tariff_history if h.tariff_type == tariff_type]
    
    if start_date:
        history = [h for h in history if h.recorded_date >= start_date]
    if end_date:
        history = [h for h in history if h.recorded_date <= end_date]
    
    return {"history": history, "total": len(history)}


@router.get("/regions")
async def get_available_regions():
    """Get available regions for tariffs."""
    return {
        "regions": [
            {"id": "deutschland", "name": "Deutschland (Bundesweit)"},
            {"id": "bayern", "name": "Bayern"},
            {"id": "nrw", "name": "Nordrhein-Westfalen"},
            {"id": "bw", "name": "Baden-Württemberg"},
            {"id": "niedersachsen", "name": "Niedersachsen"},
            {"id": "hessen", "name": "Hessen"}
        ]
    }


@router.get("/summary")
async def get_tariff_summary():
    """Get tariff summary."""
    return {
        "electricity": {
            "count": len(_electricity_tariffs),
            "avg_price": round(sum(t.price_per_kwh_eur for t in _electricity_tariffs.values()) / max(1, len(_electricity_tariffs)), 4)
        },
        "feed_in": {
            "count": len(_feed_in_tariffs),
            "categories": {cat.value: len([t for t in _feed_in_tariffs.values() if t.category == cat]) for cat in FeedInCategory}
        },
        "fuel": {
            "count": len(_fuel_tariffs),
            "types": {t.value: len([f for f in _fuel_tariffs.values() if f.tariff_type == t]) for t in [TariffType.GAS, TariffType.OIL]}
        }
    }


@router.get("/health/check")
async def health_check():
    """Health check for tariff management service."""
    return {
        "status": "healthy",
        "service": "tariff-management",
        "electricity_tariffs": len(_electricity_tariffs),
        "feed_in_tariffs": len(_feed_in_tariffs),
        "fuel_tariffs": len(_fuel_tariffs),
        "timestamp": datetime.now().isoformat()
    }
