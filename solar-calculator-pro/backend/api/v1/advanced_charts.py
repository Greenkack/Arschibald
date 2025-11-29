"""
Advanced Chart Types and Dashboard Switcher Components API

Provides REST API for advanced charts:
- Break-even detailed chart
- Lifecycle cost chart
- Monthly production/consumption chart
- Electricity cost projection chart
- Cumulative cashflow chart
- Consumption coverage pie chart
- PV usage pie chart
- Dashboard switcher components

Requirements: funktionen.txt - "advanced_charts.py", "render_*_switcher"
Tasks: 291. Advanced Chart Types, 292. Dashboard Switcher Components
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/charts", tags=["Advanced Charts"])


# ==================== Enums ====================

class ChartType(str, Enum):
    BREAK_EVEN = "break_even"
    LIFECYCLE_COST = "lifecycle_cost"
    MONTHLY_PRODUCTION = "monthly_production"
    ELECTRICITY_PROJECTION = "electricity_projection"
    CUMULATIVE_CASHFLOW = "cumulative_cashflow"
    CONSUMPTION_COVERAGE = "consumption_coverage"
    PV_USAGE = "pv_usage"
    ROI_MATRIX = "roi_matrix"
    TARIFF_CUBE = "tariff_cube"
    STORAGE_EFFECT = "storage_effect"
    SCENARIO_COMPARISON = "scenario_comparison"


class TimeRange(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


# ==================== Pydantic Models ====================

class ChartDataPoint(BaseModel):
    """Chart data point"""
    x: Any
    y: float
    label: Optional[str] = None
    color: Optional[str] = None


class ChartSeries(BaseModel):
    """Chart series"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None
    type: str = "line"


class ChartConfig(BaseModel):
    """Chart configuration"""
    chart_type: ChartType
    title: str
    subtitle: Optional[str] = None
    x_axis_label: str
    y_axis_label: str
    series: List[ChartSeries]
    show_legend: bool = True
    show_grid: bool = True
    annotations: Optional[List[Dict[str, Any]]] = None


class SwitcherOption(BaseModel):
    """Switcher option"""
    id: str
    label: str
    value: Any
    description: Optional[str] = None
    is_default: bool = False


class SwitcherConfig(BaseModel):
    """Switcher configuration"""
    id: str
    title: str
    options: List[SwitcherOption]
    current_value: Any
    chart_type: ChartType


# ==================== Chart Data Generators ====================

def generate_break_even_chart(
    investment: float,
    annual_savings: float,
    years: int = 25,
    price_increase: float = 3.0
) -> ChartConfig:
    """Generate break-even chart data."""
    cumulative_savings = []
    investment_line = []
    current_savings = annual_savings
    total = 0
    
    for year in range(years + 1):
        cumulative_savings.append(ChartDataPoint(x=year, y=round(total, 0)))
        investment_line.append(ChartDataPoint(x=year, y=investment))
        total += current_savings
        current_savings *= (1 + price_increase / 100)
    
    # Find break-even point
    break_even_year = None
    for i, point in enumerate(cumulative_savings):
        if point.y >= investment:
            break_even_year = i
            break
    
    return ChartConfig(
        chart_type=ChartType.BREAK_EVEN,
        title="Break-Even Analyse",
        subtitle=f"Amortisation nach ca. {break_even_year} Jahren" if break_even_year else None,
        x_axis_label="Jahre",
        y_axis_label="Euro (€)",
        series=[
            ChartSeries(name="Kumulative Ersparnis", data=cumulative_savings, color="#10B981", type="area"),
            ChartSeries(name="Investition", data=investment_line, color="#EF4444", type="line")
        ],
        annotations=[{"x": break_even_year, "label": "Break-Even"}] if break_even_year else None
    )


def generate_lifecycle_cost_chart(
    pv_investment: float,
    annual_pv_savings: float,
    no_pv_annual_cost: float,
    years: int = 25
) -> ChartConfig:
    """Generate lifecycle cost comparison chart."""
    with_pv = []
    without_pv = []
    
    pv_cumulative = pv_investment
    no_pv_cumulative = 0
    
    for year in range(years + 1):
        with_pv.append(ChartDataPoint(x=year, y=round(pv_cumulative, 0)))
        without_pv.append(ChartDataPoint(x=year, y=round(no_pv_cumulative, 0)))
        
        pv_cumulative -= annual_pv_savings * 0.7  # Net cost reduction
        no_pv_cumulative += no_pv_annual_cost
    
    return ChartConfig(
        chart_type=ChartType.LIFECYCLE_COST,
        title="Lebenszyklus-Kostenvergleich",
        x_axis_label="Jahre",
        y_axis_label="Kumulative Kosten (€)",
        series=[
            ChartSeries(name="Mit PV-Anlage", data=with_pv, color="#10B981"),
            ChartSeries(name="Ohne PV-Anlage", data=without_pv, color="#EF4444")
        ]
    )


def generate_monthly_production_chart(
    annual_yield: float,
    annual_consumption: float
) -> ChartConfig:
    """Generate monthly production vs consumption chart."""
    # Monthly factors
    production_factors = [0.045, 0.055, 0.085, 0.105, 0.120, 0.125, 0.130, 0.115, 0.095, 0.065, 0.040, 0.020]
    consumption_factors = [0.10, 0.09, 0.085, 0.08, 0.075, 0.07, 0.07, 0.075, 0.08, 0.085, 0.09, 0.10]
    months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    production = [ChartDataPoint(x=m, y=round(annual_yield * f, 0)) for m, f in zip(months, production_factors)]
    consumption = [ChartDataPoint(x=m, y=round(annual_consumption * f, 0)) for m, f in zip(months, consumption_factors)]
    
    return ChartConfig(
        chart_type=ChartType.MONTHLY_PRODUCTION,
        title="Monatliche Produktion vs. Verbrauch",
        x_axis_label="Monat",
        y_axis_label="kWh",
        series=[
            ChartSeries(name="PV-Produktion", data=production, color="#F59E0B", type="bar"),
            ChartSeries(name="Verbrauch", data=consumption, color="#3B82F6", type="bar")
        ]
    )


def generate_electricity_projection_chart(
    current_price: float,
    annual_increase: float = 5.0,
    years: int = 20
) -> ChartConfig:
    """Generate electricity price projection chart."""
    prices = []
    price = current_price
    
    for year in range(years + 1):
        prices.append(ChartDataPoint(x=2024 + year, y=round(price, 3)))
        price *= (1 + annual_increase / 100)
    
    return ChartConfig(
        chart_type=ChartType.ELECTRICITY_PROJECTION,
        title="Strompreis-Prognose",
        subtitle=f"Annahme: {annual_increase}% jährliche Steigerung",
        x_axis_label="Jahr",
        y_axis_label="€/kWh",
        series=[
            ChartSeries(name="Strompreis", data=prices, color="#EF4444", type="area")
        ]
    )


def generate_cumulative_cashflow_chart(
    investment: float,
    annual_savings: float,
    years: int = 25
) -> ChartConfig:
    """Generate cumulative cashflow chart."""
    cashflow = []
    cumulative = -investment
    
    for year in range(years + 1):
        cashflow.append(ChartDataPoint(
            x=year,
            y=round(cumulative, 0),
            color="#10B981" if cumulative >= 0 else "#EF4444"
        ))
        cumulative += annual_savings
    
    return ChartConfig(
        chart_type=ChartType.CUMULATIVE_CASHFLOW,
        title="Kumulativer Cashflow",
        x_axis_label="Jahre",
        y_axis_label="Euro (€)",
        series=[
            ChartSeries(name="Cashflow", data=cashflow, type="area")
        ]
    )


def generate_consumption_coverage_chart(
    self_consumption_kwh: float,
    grid_consumption_kwh: float
) -> ChartConfig:
    """Generate consumption coverage pie chart."""
    total = self_consumption_kwh + grid_consumption_kwh
    
    return ChartConfig(
        chart_type=ChartType.CONSUMPTION_COVERAGE,
        title="Stromverbrauch Deckung",
        x_axis_label="",
        y_axis_label="",
        series=[
            ChartSeries(
                name="Deckung",
                data=[
                    ChartDataPoint(x="Eigenverbrauch", y=round(self_consumption_kwh / total * 100, 1), color="#10B981"),
                    ChartDataPoint(x="Netzbezug", y=round(grid_consumption_kwh / total * 100, 1), color="#6B7280")
                ],
                type="pie"
            )
        ]
    )


def generate_pv_usage_chart(
    self_consumption_kwh: float,
    feed_in_kwh: float
) -> ChartConfig:
    """Generate PV usage pie chart."""
    total = self_consumption_kwh + feed_in_kwh
    
    return ChartConfig(
        chart_type=ChartType.PV_USAGE,
        title="PV-Strom Verwendung",
        x_axis_label="",
        y_axis_label="",
        series=[
            ChartSeries(
                name="Verwendung",
                data=[
                    ChartDataPoint(x="Eigenverbrauch", y=round(self_consumption_kwh / total * 100, 1), color="#10B981"),
                    ChartDataPoint(x="Einspeisung", y=round(feed_in_kwh / total * 100, 1), color="#F59E0B")
                ],
                type="pie"
            )
        ]
    )


# ==================== Switcher Configurations ====================

SWITCHER_CONFIGS = {
    "daily_production": SwitcherConfig(
        id="daily_production",
        title="Tagesproduktion",
        options=[
            SwitcherOption(id="today", label="Heute", value="today", is_default=True),
            SwitcherOption(id="yesterday", label="Gestern", value="yesterday"),
            SwitcherOption(id="week", label="Diese Woche", value="week"),
        ],
        current_value="today",
        chart_type=ChartType.MONTHLY_PRODUCTION
    ),
    "weekly_production": SwitcherConfig(
        id="weekly_production",
        title="Wochenproduktion",
        options=[
            SwitcherOption(id="current", label="Aktuelle Woche", value="current", is_default=True),
            SwitcherOption(id="last", label="Letzte Woche", value="last"),
            SwitcherOption(id="month", label="Letzter Monat", value="month"),
        ],
        current_value="current",
        chart_type=ChartType.MONTHLY_PRODUCTION
    ),
    "yearly_production": SwitcherConfig(
        id="yearly_production",
        title="Jahresproduktion",
        options=[
            SwitcherOption(id="2024", label="2024", value="2024", is_default=True),
            SwitcherOption(id="2023", label="2023", value="2023"),
            SwitcherOption(id="all", label="Gesamt", value="all"),
        ],
        current_value="2024",
        chart_type=ChartType.MONTHLY_PRODUCTION
    ),
    "tariff_cube": SwitcherConfig(
        id="tariff_cube",
        title="Tarifvergleich",
        options=[
            SwitcherOption(id="current", label="Aktueller Tarif", value="current", is_default=True),
            SwitcherOption(id="increase_5", label="+5% Steigerung", value="increase_5"),
            SwitcherOption(id="increase_10", label="+10% Steigerung", value="increase_10"),
        ],
        current_value="current",
        chart_type=ChartType.TARIFF_CUBE
    ),
    "roi_matrix": SwitcherConfig(
        id="roi_matrix",
        title="ROI Szenarien",
        options=[
            SwitcherOption(id="conservative", label="Konservativ", value="conservative"),
            SwitcherOption(id="realistic", label="Realistisch", value="realistic", is_default=True),
            SwitcherOption(id="optimistic", label="Optimistisch", value="optimistic"),
        ],
        current_value="realistic",
        chart_type=ChartType.ROI_MATRIX
    ),
    "feed_in_revenue": SwitcherConfig(
        id="feed_in_revenue",
        title="Einspeisevergütung",
        options=[
            SwitcherOption(id="monthly", label="Monatlich", value="monthly", is_default=True),
            SwitcherOption(id="yearly", label="Jährlich", value="yearly"),
            SwitcherOption(id="cumulative", label="Kumulativ", value="cumulative"),
        ],
        current_value="monthly",
        chart_type=ChartType.CUMULATIVE_CASHFLOW
    ),
    "storage_effect": SwitcherConfig(
        id="storage_effect",
        title="Speicher-Effekt",
        options=[
            SwitcherOption(id="no_storage", label="Ohne Speicher", value="0"),
            SwitcherOption(id="5kwh", label="5 kWh", value="5"),
            SwitcherOption(id="10kwh", label="10 kWh", value="10", is_default=True),
            SwitcherOption(id="15kwh", label="15 kWh", value="15"),
        ],
        current_value="10",
        chart_type=ChartType.STORAGE_EFFECT
    ),
    "scenario_comparison": SwitcherConfig(
        id="scenario_comparison",
        title="Szenario-Vergleich",
        options=[
            SwitcherOption(id="pv_only", label="Nur PV", value="pv_only"),
            SwitcherOption(id="pv_storage", label="PV + Speicher", value="pv_storage", is_default=True),
            SwitcherOption(id="pv_hp", label="PV + Wärmepumpe", value="pv_hp"),
            SwitcherOption(id="all", label="Komplettsystem", value="all"),
        ],
        current_value="pv_storage",
        chart_type=ChartType.SCENARIO_COMPARISON
    ),
}


# ==================== API Endpoints ====================

@router.post("/break-even")
async def get_break_even_chart(
    investment: float,
    annual_savings: float,
    years: int = 25,
    price_increase: float = 3.0
):
    """Generate break-even chart."""
    chart = generate_break_even_chart(investment, annual_savings, years, price_increase)
    return {"chart": chart}


@router.post("/lifecycle-cost")
async def get_lifecycle_cost_chart(
    pv_investment: float,
    annual_pv_savings: float,
    no_pv_annual_cost: float,
    years: int = 25
):
    """Generate lifecycle cost chart."""
    chart = generate_lifecycle_cost_chart(pv_investment, annual_pv_savings, no_pv_annual_cost, years)
    return {"chart": chart}


@router.post("/monthly-production")
async def get_monthly_production_chart(
    annual_yield: float,
    annual_consumption: float
):
    """Generate monthly production chart."""
    chart = generate_monthly_production_chart(annual_yield, annual_consumption)
    return {"chart": chart}


@router.post("/electricity-projection")
async def get_electricity_projection_chart(
    current_price: float = 0.30,
    annual_increase: float = 5.0,
    years: int = 20
):
    """Generate electricity price projection chart."""
    chart = generate_electricity_projection_chart(current_price, annual_increase, years)
    return {"chart": chart}


@router.post("/cumulative-cashflow")
async def get_cumulative_cashflow_chart(
    investment: float,
    annual_savings: float,
    years: int = 25
):
    """Generate cumulative cashflow chart."""
    chart = generate_cumulative_cashflow_chart(investment, annual_savings, years)
    return {"chart": chart}


@router.post("/consumption-coverage")
async def get_consumption_coverage_chart(
    self_consumption_kwh: float,
    grid_consumption_kwh: float
):
    """Generate consumption coverage pie chart."""
    chart = generate_consumption_coverage_chart(self_consumption_kwh, grid_consumption_kwh)
    return {"chart": chart}


@router.post("/pv-usage")
async def get_pv_usage_chart(
    self_consumption_kwh: float,
    feed_in_kwh: float
):
    """Generate PV usage pie chart."""
    chart = generate_pv_usage_chart(self_consumption_kwh, feed_in_kwh)
    return {"chart": chart}


@router.get("/types")
async def get_chart_types():
    """Get available chart types."""
    return {
        "chart_types": [
            {"id": ct.value, "name": ct.value.replace("_", " ").title()}
            for ct in ChartType
        ]
    }


# ==================== Switcher Endpoints ====================

@router.get("/switchers")
async def get_all_switchers():
    """Get all switcher configurations."""
    return {"switchers": SWITCHER_CONFIGS}


@router.get("/switchers/{switcher_id}")
async def get_switcher(switcher_id: str):
    """Get specific switcher configuration."""
    if switcher_id not in SWITCHER_CONFIGS:
        raise HTTPException(status_code=404, detail="Switcher nicht gefunden")
    return {"switcher": SWITCHER_CONFIGS[switcher_id]}


@router.post("/switchers/{switcher_id}/select")
async def select_switcher_option(switcher_id: str, option_id: str):
    """Select switcher option and get updated chart data."""
    if switcher_id not in SWITCHER_CONFIGS:
        raise HTTPException(status_code=404, detail="Switcher nicht gefunden")
    
    switcher = SWITCHER_CONFIGS[switcher_id]
    option = next((o for o in switcher.options if o.id == option_id), None)
    
    if not option:
        raise HTTPException(status_code=404, detail="Option nicht gefunden")
    
    # Update current value
    switcher.current_value = option.value
    
    return {
        "switcher": switcher,
        "selected_option": option,
        "message": f"Option '{option.label}' ausgewählt"
    }


@router.get("/dashboard/complete")
async def get_complete_dashboard_charts(
    annual_yield: float = 9500,
    annual_consumption: float = 4000,
    investment: float = 18500,
    annual_savings: float = 1850,
    electricity_price: float = 0.30
):
    """Get all dashboard charts with default values."""
    self_consumption_rate = 35
    self_consumption_kwh = annual_yield * (self_consumption_rate / 100)
    feed_in_kwh = annual_yield - self_consumption_kwh
    grid_consumption_kwh = annual_consumption - self_consumption_kwh
    
    return {
        "charts": {
            "break_even": generate_break_even_chart(investment, annual_savings),
            "monthly_production": generate_monthly_production_chart(annual_yield, annual_consumption),
            "electricity_projection": generate_electricity_projection_chart(electricity_price),
            "cumulative_cashflow": generate_cumulative_cashflow_chart(investment, annual_savings),
            "consumption_coverage": generate_consumption_coverage_chart(self_consumption_kwh, grid_consumption_kwh),
            "pv_usage": generate_pv_usage_chart(self_consumption_kwh, feed_in_kwh)
        },
        "switchers": SWITCHER_CONFIGS
    }


@router.get("/health/check")
async def health_check():
    """Health check for charts service."""
    return {
        "status": "healthy",
        "service": "advanced-charts",
        "chart_types": len(ChartType),
        "switchers": len(SWITCHER_CONFIGS),
        "timestamp": datetime.now().isoformat()
    }
