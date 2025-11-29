"""
Scenario Comparison Tools API

Provides REST API for scenario comparison:
- Scenario switchers
- With/without PV comparison
- With/without storage comparison
- Financing scenario comparison
- Tariff scenario comparison

Requirements: funktionen.txt - "Szenario-Vergleiche"
Task: 284. Scenario Comparison Tools
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/scenarios", tags=["Scenario Comparison"])


# ==================== Enums ====================

class ScenarioType(str, Enum):
    PV_COMPARISON = "pv_comparison"
    STORAGE_COMPARISON = "storage_comparison"
    FINANCING_COMPARISON = "financing_comparison"
    TARIFF_COMPARISON = "tariff_comparison"
    HEATPUMP_COMPARISON = "heatpump_comparison"
    COMBINED_COMPARISON = "combined_comparison"


class ComparisonMetric(str, Enum):
    INVESTMENT = "investment"
    ANNUAL_SAVINGS = "annual_savings"
    PAYBACK_YEARS = "payback_years"
    ROI = "roi"
    AUTARKY = "autarky"
    SELF_CONSUMPTION = "self_consumption"
    CO2_SAVINGS = "co2_savings"
    TOTAL_SAVINGS_20Y = "total_savings_20y"


# ==================== Pydantic Models ====================

class ScenarioResult(BaseModel):
    """Single scenario result"""
    scenario_id: str
    scenario_name: str
    description: Optional[str] = None
    metrics: Dict[str, float]
    is_recommended: bool = False
    highlight_color: Optional[str] = None


class ScenarioComparison(BaseModel):
    """Scenario comparison result"""
    comparison_type: ScenarioType
    title: str
    description: str
    scenarios: List[ScenarioResult]
    best_scenario_id: str
    comparison_metrics: List[ComparisonMetric]
    chart_data: Optional[List[Dict[str, Any]]] = None


class PVComparisonInput(BaseModel):
    """Input for PV comparison"""
    annual_consumption_kwh: float = 4000
    electricity_price_eur: float = 0.30
    system_power_kwp: float = 10.0
    annual_yield_kwh: float = 9500
    investment_eur: float = 18500
    feed_in_tariff_eur: float = 0.082


class StorageComparisonInput(BaseModel):
    """Input for storage comparison"""
    annual_consumption_kwh: float = 4000
    annual_yield_kwh: float = 9500
    electricity_price_eur: float = 0.30
    base_self_consumption_rate: float = 30
    storage_sizes_kwh: List[float] = [0, 5, 10, 15]
    storage_price_per_kwh: float = 800


class FinancingComparisonInput(BaseModel):
    """Input for financing comparison"""
    total_investment_eur: float = 18500
    annual_savings_eur: float = 1850
    loan_interest_rates: List[float] = [0, 3.5, 5.0, 7.0]
    loan_term_years: int = 10
    down_payment_percent: float = 0


class TariffComparisonInput(BaseModel):
    """Input for tariff comparison"""
    annual_consumption_kwh: float = 4000
    annual_yield_kwh: float = 9500
    self_consumption_rate: float = 35
    tariff_scenarios: List[Dict[str, float]] = [
        {"name": "Aktuell", "price": 0.30, "feed_in": 0.082},
        {"name": "Preissteigerung 5%", "price": 0.315, "feed_in": 0.082},
        {"name": "Preissteigerung 10%", "price": 0.33, "feed_in": 0.082},
    ]


# ==================== Calculation Functions ====================

def calculate_pv_scenario(
    with_pv: bool,
    annual_consumption: float,
    electricity_price: float,
    annual_yield: float = 0,
    investment: float = 0,
    feed_in_tariff: float = 0.082,
    self_consumption_rate: float = 35
) -> Dict[str, float]:
    """Calculate PV scenario metrics."""
    if not with_pv:
        return {
            "investment": 0,
            "annual_cost": annual_consumption * electricity_price,
            "annual_savings": 0,
            "payback_years": 0,
            "autarky": 0,
            "self_consumption": 0,
            "co2_savings": 0,
            "total_savings_20y": 0
        }
    
    self_consumed = annual_yield * (self_consumption_rate / 100)
    fed_in = annual_yield - self_consumed
    
    savings_self_consumption = self_consumed * electricity_price
    revenue_feed_in = fed_in * feed_in_tariff
    annual_savings = savings_self_consumption + revenue_feed_in
    
    remaining_consumption = annual_consumption - self_consumed
    annual_cost = remaining_consumption * electricity_price
    
    payback = investment / annual_savings if annual_savings > 0 else 99
    autarky = (self_consumed / annual_consumption) * 100 if annual_consumption > 0 else 0
    co2_savings = annual_yield * 0.4  # 400g CO2 per kWh
    
    return {
        "investment": investment,
        "annual_cost": annual_cost,
        "annual_savings": annual_savings,
        "payback_years": payback,
        "autarky": autarky,
        "self_consumption": self_consumption_rate,
        "co2_savings": co2_savings,
        "total_savings_20y": annual_savings * 20 - investment
    }


def calculate_storage_scenario(
    storage_kwh: float,
    annual_consumption: float,
    annual_yield: float,
    electricity_price: float,
    base_self_consumption: float,
    storage_price_per_kwh: float
) -> Dict[str, float]:
    """Calculate storage scenario metrics."""
    # Self-consumption increases with storage
    # Simplified model: +10% per 5kWh storage, max 80%
    additional_self_consumption = min(storage_kwh * 2, 50)  # Max +50%
    self_consumption_rate = min(base_self_consumption + additional_self_consumption, 80)
    
    storage_investment = storage_kwh * storage_price_per_kwh
    
    self_consumed = annual_yield * (self_consumption_rate / 100)
    fed_in = annual_yield - self_consumed
    
    savings_self_consumption = self_consumed * electricity_price
    revenue_feed_in = fed_in * 0.082
    annual_savings = savings_self_consumption + revenue_feed_in
    
    autarky = (self_consumed / annual_consumption) * 100 if annual_consumption > 0 else 0
    
    return {
        "storage_kwh": storage_kwh,
        "investment": storage_investment,
        "self_consumption": self_consumption_rate,
        "autarky": autarky,
        "annual_savings": annual_savings,
        "payback_years": storage_investment / annual_savings if annual_savings > 0 else 99,
        "total_savings_20y": annual_savings * 20 - storage_investment
    }


def calculate_financing_scenario(
    total_investment: float,
    annual_savings: float,
    interest_rate: float,
    loan_term_years: int,
    down_payment_percent: float
) -> Dict[str, float]:
    """Calculate financing scenario metrics."""
    down_payment = total_investment * (down_payment_percent / 100)
    loan_amount = total_investment - down_payment
    
    if interest_rate == 0:
        monthly_payment = loan_amount / (loan_term_years * 12) if loan_term_years > 0 else 0
        total_interest = 0
    else:
        monthly_rate = interest_rate / 100 / 12
        n_payments = loan_term_years * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        total_interest = (monthly_payment * n_payments) - loan_amount
    
    annual_payment = monthly_payment * 12
    net_annual_benefit = annual_savings - annual_payment
    
    total_cost = down_payment + (monthly_payment * loan_term_years * 12)
    effective_payback = total_cost / annual_savings if annual_savings > 0 else 99
    
    return {
        "interest_rate": interest_rate,
        "loan_amount": loan_amount,
        "monthly_payment": monthly_payment,
        "annual_payment": annual_payment,
        "total_interest": total_interest,
        "total_cost": total_cost,
        "net_annual_benefit": net_annual_benefit,
        "effective_payback": effective_payback,
        "total_savings_20y": (annual_savings * 20) - total_cost
    }


def calculate_tariff_scenario(
    annual_consumption: float,
    annual_yield: float,
    self_consumption_rate: float,
    electricity_price: float,
    feed_in_tariff: float
) -> Dict[str, float]:
    """Calculate tariff scenario metrics."""
    self_consumed = annual_yield * (self_consumption_rate / 100)
    fed_in = annual_yield - self_consumed
    
    savings_self_consumption = self_consumed * electricity_price
    revenue_feed_in = fed_in * feed_in_tariff
    annual_savings = savings_self_consumption + revenue_feed_in
    
    remaining_consumption = annual_consumption - self_consumed
    annual_cost = remaining_consumption * electricity_price
    
    return {
        "electricity_price": electricity_price,
        "feed_in_tariff": feed_in_tariff,
        "annual_savings": annual_savings,
        "annual_cost": annual_cost,
        "net_benefit": annual_savings - annual_cost,
        "total_savings_20y": annual_savings * 20
    }


# ==================== API Endpoints ====================

@router.post("/pv-comparison")
async def compare_pv_scenarios(input_data: PVComparisonInput):
    """Compare with/without PV scenarios."""
    
    without_pv = calculate_pv_scenario(
        with_pv=False,
        annual_consumption=input_data.annual_consumption_kwh,
        electricity_price=input_data.electricity_price_eur
    )
    
    with_pv = calculate_pv_scenario(
        with_pv=True,
        annual_consumption=input_data.annual_consumption_kwh,
        electricity_price=input_data.electricity_price_eur,
        annual_yield=input_data.annual_yield_kwh,
        investment=input_data.investment_eur,
        feed_in_tariff=input_data.feed_in_tariff_eur
    )
    
    scenarios = [
        ScenarioResult(
            scenario_id="without_pv",
            scenario_name="Ohne PV-Anlage",
            description="Aktueller Zustand ohne Photovoltaik",
            metrics=without_pv,
            highlight_color="#EF4444"
        ),
        ScenarioResult(
            scenario_id="with_pv",
            scenario_name="Mit PV-Anlage",
            description=f"{input_data.system_power_kwp} kWp Photovoltaikanlage",
            metrics=with_pv,
            is_recommended=True,
            highlight_color="#10B981"
        )
    ]
    
    return ScenarioComparison(
        comparison_type=ScenarioType.PV_COMPARISON,
        title="PV-Anlage Vergleich",
        description="Vergleich der Kosten und Einsparungen mit und ohne PV-Anlage",
        scenarios=scenarios,
        best_scenario_id="with_pv",
        comparison_metrics=[
            ComparisonMetric.ANNUAL_SAVINGS,
            ComparisonMetric.PAYBACK_YEARS,
            ComparisonMetric.AUTARKY,
            ComparisonMetric.CO2_SAVINGS
        ],
        chart_data=[
            {"scenario": "Ohne PV", "annual_cost": without_pv["annual_cost"], "savings": 0},
            {"scenario": "Mit PV", "annual_cost": with_pv["annual_cost"], "savings": with_pv["annual_savings"]}
        ]
    )


@router.post("/storage-comparison")
async def compare_storage_scenarios(input_data: StorageComparisonInput):
    """Compare different storage sizes."""
    
    scenarios = []
    best_roi = -999
    best_scenario_id = ""
    
    for storage_size in input_data.storage_sizes_kwh:
        result = calculate_storage_scenario(
            storage_kwh=storage_size,
            annual_consumption=input_data.annual_consumption_kwh,
            annual_yield=input_data.annual_yield_kwh,
            electricity_price=input_data.electricity_price_eur,
            base_self_consumption=input_data.base_self_consumption_rate,
            storage_price_per_kwh=input_data.storage_price_per_kwh
        )
        
        scenario_id = f"storage_{int(storage_size)}kwh"
        scenario_name = f"{int(storage_size)} kWh Speicher" if storage_size > 0 else "Ohne Speicher"
        
        # Calculate ROI for comparison
        roi = result["total_savings_20y"] / result["investment"] if result["investment"] > 0 else 0
        
        if roi > best_roi:
            best_roi = roi
            best_scenario_id = scenario_id
        
        scenarios.append(ScenarioResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            description=f"Eigenverbrauch: {result['self_consumption']:.0f}%, Autarkie: {result['autarky']:.0f}%",
            metrics=result,
            is_recommended=(storage_size == 10),  # 10kWh often optimal
            highlight_color="#3B82F6" if storage_size == 10 else None
        ))
    
    return ScenarioComparison(
        comparison_type=ScenarioType.STORAGE_COMPARISON,
        title="Speichergrößen Vergleich",
        description="Vergleich verschiedener Batteriespeichergrößen",
        scenarios=scenarios,
        best_scenario_id=best_scenario_id,
        comparison_metrics=[
            ComparisonMetric.INVESTMENT,
            ComparisonMetric.SELF_CONSUMPTION,
            ComparisonMetric.AUTARKY,
            ComparisonMetric.PAYBACK_YEARS
        ],
        chart_data=[
            {
                "storage": s.scenario_name,
                "self_consumption": s.metrics["self_consumption"],
                "autarky": s.metrics["autarky"],
                "investment": s.metrics["investment"]
            }
            for s in scenarios
        ]
    )


@router.post("/financing-comparison")
async def compare_financing_scenarios(input_data: FinancingComparisonInput):
    """Compare different financing options."""
    
    scenarios = []
    
    for rate in input_data.loan_interest_rates:
        result = calculate_financing_scenario(
            total_investment=input_data.total_investment_eur,
            annual_savings=input_data.annual_savings_eur,
            interest_rate=rate,
            loan_term_years=input_data.loan_term_years,
            down_payment_percent=input_data.down_payment_percent
        )
        
        scenario_id = f"financing_{rate}pct"
        if rate == 0:
            scenario_name = "Barzahlung"
            description = "Sofortige Zahlung ohne Finanzierung"
        else:
            scenario_name = f"{rate}% Zinsen"
            description = f"Kredit über {input_data.loan_term_years} Jahre"
        
        scenarios.append(ScenarioResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            description=description,
            metrics=result,
            is_recommended=(rate == 0),
            highlight_color="#10B981" if rate == 0 else None
        ))
    
    return ScenarioComparison(
        comparison_type=ScenarioType.FINANCING_COMPARISON,
        title="Finanzierungsvergleich",
        description="Vergleich verschiedener Finanzierungsoptionen",
        scenarios=scenarios,
        best_scenario_id="financing_0pct",
        comparison_metrics=[
            ComparisonMetric.INVESTMENT,
            ComparisonMetric.PAYBACK_YEARS,
            ComparisonMetric.TOTAL_SAVINGS_20Y
        ],
        chart_data=[
            {
                "option": s.scenario_name,
                "total_cost": s.metrics["total_cost"],
                "total_interest": s.metrics["total_interest"],
                "monthly_payment": s.metrics["monthly_payment"]
            }
            for s in scenarios
        ]
    )


@router.post("/tariff-comparison")
async def compare_tariff_scenarios(input_data: TariffComparisonInput):
    """Compare different tariff scenarios."""
    
    scenarios = []
    
    for tariff in input_data.tariff_scenarios:
        result = calculate_tariff_scenario(
            annual_consumption=input_data.annual_consumption_kwh,
            annual_yield=input_data.annual_yield_kwh,
            self_consumption_rate=input_data.self_consumption_rate,
            electricity_price=tariff["price"],
            feed_in_tariff=tariff["feed_in"]
        )
        
        scenario_id = f"tariff_{tariff['name'].lower().replace(' ', '_')}"
        
        scenarios.append(ScenarioResult(
            scenario_id=scenario_id,
            scenario_name=tariff["name"],
            description=f"Strompreis: {tariff['price']:.2f} €/kWh",
            metrics=result,
            is_recommended=(tariff["name"] == "Aktuell")
        ))
    
    return ScenarioComparison(
        comparison_type=ScenarioType.TARIFF_COMPARISON,
        title="Tarifvergleich",
        description="Auswirkungen verschiedener Strompreise auf die Wirtschaftlichkeit",
        scenarios=scenarios,
        best_scenario_id=scenarios[0].scenario_id if scenarios else "",
        comparison_metrics=[
            ComparisonMetric.ANNUAL_SAVINGS,
            ComparisonMetric.TOTAL_SAVINGS_20Y
        ],
        chart_data=[
            {
                "tariff": s.scenario_name,
                "annual_savings": s.metrics["annual_savings"],
                "total_savings_20y": s.metrics["total_savings_20y"]
            }
            for s in scenarios
        ]
    )


@router.get("/types")
async def get_scenario_types():
    """Get available scenario comparison types."""
    return {
        "types": [
            {
                "id": ScenarioType.PV_COMPARISON,
                "name": "PV-Anlage Vergleich",
                "description": "Mit vs. ohne Photovoltaik"
            },
            {
                "id": ScenarioType.STORAGE_COMPARISON,
                "name": "Speichervergleich",
                "description": "Verschiedene Batteriespeichergrößen"
            },
            {
                "id": ScenarioType.FINANCING_COMPARISON,
                "name": "Finanzierungsvergleich",
                "description": "Verschiedene Finanzierungsoptionen"
            },
            {
                "id": ScenarioType.TARIFF_COMPARISON,
                "name": "Tarifvergleich",
                "description": "Verschiedene Stromtarife"
            },
            {
                "id": ScenarioType.HEATPUMP_COMPARISON,
                "name": "Wärmepumpenvergleich",
                "description": "Verschiedene Wärmepumpentypen"
            },
            {
                "id": ScenarioType.COMBINED_COMPARISON,
                "name": "Kombinierter Vergleich",
                "description": "PV + Wärmepumpe Szenarien"
            }
        ]
    }


@router.get("/metrics")
async def get_comparison_metrics():
    """Get available comparison metrics."""
    return {
        "metrics": [
            {"id": ComparisonMetric.INVESTMENT, "name": "Investition", "unit": "€"},
            {"id": ComparisonMetric.ANNUAL_SAVINGS, "name": "Jährliche Ersparnis", "unit": "€"},
            {"id": ComparisonMetric.PAYBACK_YEARS, "name": "Amortisation", "unit": "Jahre"},
            {"id": ComparisonMetric.ROI, "name": "ROI", "unit": "%"},
            {"id": ComparisonMetric.AUTARKY, "name": "Autarkiegrad", "unit": "%"},
            {"id": ComparisonMetric.SELF_CONSUMPTION, "name": "Eigenverbrauch", "unit": "%"},
            {"id": ComparisonMetric.CO2_SAVINGS, "name": "CO₂-Einsparung", "unit": "kg"},
            {"id": ComparisonMetric.TOTAL_SAVINGS_20Y, "name": "Ersparnis 20 Jahre", "unit": "€"},
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for scenario comparison service."""
    return {
        "status": "healthy",
        "service": "scenario-comparison",
        "scenario_types": len(ScenarioType),
        "comparison_metrics": len(ComparisonMetric),
        "timestamp": datetime.now().isoformat()
    }
