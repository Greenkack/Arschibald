"""
Results Dashboard API

Provides REST API for results dashboard:
- Results overview page
- Price breakdown display
- Cost savings comparison
- Autarky rate and amortization
- Modern tile-based dashboard
- Interactive diagram toggles

Requirements: funktionen.txt - "Ergebnis-Dashboard"
Task: 283. Results Dashboard
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/results-dashboard", tags=["Results Dashboard"])


# ==================== Enums ====================

class CalculationType(str, Enum):
    PV_ONLY = "pv_only"
    HEATPUMP_ONLY = "heatpump_only"
    COMBINED = "combined"


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    WATERFALL = "waterfall"


class TileSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    FULL = "full"


# ==================== Pydantic Models ====================

class PriceBreakdown(BaseModel):
    """Price breakdown item"""
    category: str
    label: str
    amount: float
    percentage: float
    is_discount: bool = False


class SavingsComparison(BaseModel):
    """Savings comparison data"""
    category: str
    current_cost: float
    future_cost: float
    savings: float
    savings_percentage: float


class DashboardTile(BaseModel):
    """Dashboard tile configuration"""
    id: str
    title: str
    value: str
    unit: Optional[str] = None
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    color: str = "primary"
    size: TileSize = TileSize.MEDIUM
    trend: Optional[float] = None
    trend_label: Optional[str] = None
    chart_type: Optional[ChartType] = None
    chart_data: Optional[List[Dict[str, Any]]] = None


class ChartConfig(BaseModel):
    """Chart configuration"""
    id: str
    title: str
    chart_type: ChartType
    data: List[Dict[str, Any]]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    colors: Optional[List[str]] = None
    show_legend: bool = True
    show_grid: bool = True
    interactive: bool = True


class ResultsSummary(BaseModel):
    """Results summary"""
    calculation_type: CalculationType
    system_power_kwp: Optional[float] = None
    annual_yield_kwh: Optional[float] = None
    self_consumption_rate: Optional[float] = None
    autarky_rate: Optional[float] = None
    total_investment: float
    annual_savings: float
    payback_years: float
    co2_savings_kg: Optional[float] = None
    roi_percent: Optional[float] = None


class DashboardConfig(BaseModel):
    """Complete dashboard configuration"""
    calculation_type: CalculationType
    tiles: List[DashboardTile]
    charts: List[ChartConfig]
    price_breakdown: List[PriceBreakdown]
    savings_comparison: List[SavingsComparison]
    summary: ResultsSummary


# ==================== Helper Functions ====================

def format_currency(value: float) -> str:
    """Format value as German currency."""
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.1f}%".replace(".", ",")


def format_kwh(value: float) -> str:
    """Format value as kWh."""
    return f"{value:,.0f} kWh".replace(",", ".")


def create_pv_dashboard(calculation_data: Dict[str, Any]) -> DashboardConfig:
    """Create PV results dashboard."""
    
    # Extract data with defaults
    system_power = calculation_data.get("system_power_kwp", 10.0)
    annual_yield = calculation_data.get("annual_yield_kwh", 9500)
    self_consumption = calculation_data.get("self_consumption_rate", 35)
    autarky = calculation_data.get("autarky_rate", 45)
    total_investment = calculation_data.get("total_investment", 18500)
    annual_savings = calculation_data.get("annual_savings", 1850)
    payback_years = calculation_data.get("payback_years", 10)
    co2_savings = calculation_data.get("co2_savings_kg", 4500)
    
    # Create tiles
    tiles = [
        DashboardTile(
            id="system_power",
            title="Anlagenleistung",
            value=f"{system_power:.1f}".replace(".", ","),
            unit="kWp",
            icon="solar_power",
            color="primary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="annual_yield",
            title="Jahresertrag",
            value=f"{annual_yield:,.0f}".replace(",", "."),
            unit="kWh",
            icon="bolt",
            color="success",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="self_consumption",
            title="Eigenverbrauch",
            value=f"{self_consumption:.0f}",
            unit="%",
            icon="home",
            color="info",
            size=TileSize.MEDIUM,
            subtitle="des erzeugten Stroms"
        ),
        DashboardTile(
            id="autarky",
            title="Autarkiegrad",
            value=f"{autarky:.0f}",
            unit="%",
            icon="offline_bolt",
            color="warning",
            size=TileSize.MEDIUM,
            subtitle="Unabhängigkeit vom Netz"
        ),
        DashboardTile(
            id="investment",
            title="Investition",
            value=format_currency(total_investment),
            icon="euro",
            color="secondary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="annual_savings",
            title="Jährliche Ersparnis",
            value=format_currency(annual_savings),
            icon="savings",
            color="success",
            size=TileSize.MEDIUM,
            trend=12.5,
            trend_label="vs. Vorjahr"
        ),
        DashboardTile(
            id="payback",
            title="Amortisation",
            value=f"{payback_years:.1f}".replace(".", ","),
            unit="Jahre",
            icon="schedule",
            color="primary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="co2_savings",
            title="CO₂-Einsparung",
            value=f"{co2_savings:,.0f}".replace(",", "."),
            unit="kg/Jahr",
            icon="eco",
            color="success",
            size=TileSize.MEDIUM
        ),
    ]
    
    # Create charts
    charts = [
        ChartConfig(
            id="monthly_yield",
            title="Monatlicher Ertrag",
            chart_type=ChartType.BAR,
            data=[
                {"month": "Jan", "yield": 450},
                {"month": "Feb", "yield": 580},
                {"month": "Mar", "yield": 850},
                {"month": "Apr", "yield": 1050},
                {"month": "Mai", "yield": 1200},
                {"month": "Jun", "yield": 1250},
                {"month": "Jul", "yield": 1300},
                {"month": "Aug", "yield": 1150},
                {"month": "Sep", "yield": 950},
                {"month": "Okt", "yield": 650},
                {"month": "Nov", "yield": 480},
                {"month": "Dez", "yield": 390},
            ],
            x_axis="month",
            y_axis="yield",
            colors=["#3B82F6"]
        ),
        ChartConfig(
            id="energy_flow",
            title="Energiefluss",
            chart_type=ChartType.PIE,
            data=[
                {"name": "Eigenverbrauch", "value": self_consumption},
                {"name": "Netzeinspeisung", "value": 100 - self_consumption},
            ],
            colors=["#10B981", "#F59E0B"]
        ),
        ChartConfig(
            id="savings_over_time",
            title="Kumulative Ersparnis",
            chart_type=ChartType.AREA,
            data=[
                {"year": 1, "savings": annual_savings, "investment": total_investment},
                {"year": 5, "savings": annual_savings * 5, "investment": total_investment},
                {"year": 10, "savings": annual_savings * 10, "investment": total_investment},
                {"year": 15, "savings": annual_savings * 15, "investment": total_investment},
                {"year": 20, "savings": annual_savings * 20, "investment": total_investment},
            ],
            x_axis="year",
            colors=["#10B981", "#EF4444"]
        ),
    ]
    
    # Price breakdown
    price_breakdown = [
        PriceBreakdown(category="modules", label="PV-Module", amount=8500, percentage=46),
        PriceBreakdown(category="inverter", label="Wechselrichter", amount=2500, percentage=14),
        PriceBreakdown(category="mounting", label="Montagesystem", amount=2000, percentage=11),
        PriceBreakdown(category="installation", label="Installation", amount=3500, percentage=19),
        PriceBreakdown(category="electrical", label="Elektroinstallation", amount=1500, percentage=8),
        PriceBreakdown(category="other", label="Sonstiges", amount=500, percentage=2),
    ]
    
    # Savings comparison
    savings_comparison = [
        SavingsComparison(
            category="electricity",
            current_cost=1800,
            future_cost=650,
            savings=1150,
            savings_percentage=64
        ),
        SavingsComparison(
            category="feed_in",
            current_cost=0,
            future_cost=-700,
            savings=700,
            savings_percentage=100
        ),
    ]
    
    # Summary
    summary = ResultsSummary(
        calculation_type=CalculationType.PV_ONLY,
        system_power_kwp=system_power,
        annual_yield_kwh=annual_yield,
        self_consumption_rate=self_consumption,
        autarky_rate=autarky,
        total_investment=total_investment,
        annual_savings=annual_savings,
        payback_years=payback_years,
        co2_savings_kg=co2_savings,
        roi_percent=(annual_savings / total_investment) * 100
    )
    
    return DashboardConfig(
        calculation_type=CalculationType.PV_ONLY,
        tiles=tiles,
        charts=charts,
        price_breakdown=price_breakdown,
        savings_comparison=savings_comparison,
        summary=summary
    )


def create_heatpump_dashboard(calculation_data: Dict[str, Any]) -> DashboardConfig:
    """Create heat pump results dashboard."""
    
    # Extract data with defaults
    heating_power = calculation_data.get("heating_power_kw", 12)
    annual_cop = calculation_data.get("annual_cop", 3.8)
    heating_demand = calculation_data.get("heating_demand_kwh", 18000)
    electricity_consumption = calculation_data.get("electricity_consumption_kwh", 4700)
    total_investment = calculation_data.get("total_investment", 28000)
    annual_savings = calculation_data.get("annual_savings", 1200)
    payback_years = calculation_data.get("payback_years", 12)
    co2_savings = calculation_data.get("co2_savings_kg", 3500)
    
    # Create tiles
    tiles = [
        DashboardTile(
            id="heating_power",
            title="Heizleistung",
            value=f"{heating_power:.1f}".replace(".", ","),
            unit="kW",
            icon="whatshot",
            color="warning",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="cop",
            title="Jahresarbeitszahl",
            value=f"{annual_cop:.1f}".replace(".", ","),
            icon="speed",
            color="success",
            size=TileSize.MEDIUM,
            subtitle="COP Durchschnitt"
        ),
        DashboardTile(
            id="heating_demand",
            title="Wärmebedarf",
            value=f"{heating_demand:,.0f}".replace(",", "."),
            unit="kWh/Jahr",
            icon="thermostat",
            color="info",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="electricity",
            title="Stromverbrauch WP",
            value=f"{electricity_consumption:,.0f}".replace(",", "."),
            unit="kWh/Jahr",
            icon="bolt",
            color="primary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="investment",
            title="Investition",
            value=format_currency(total_investment),
            icon="euro",
            color="secondary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="annual_savings",
            title="Jährliche Ersparnis",
            value=format_currency(annual_savings),
            icon="savings",
            color="success",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="payback",
            title="Amortisation",
            value=f"{payback_years:.1f}".replace(".", ","),
            unit="Jahre",
            icon="schedule",
            color="primary",
            size=TileSize.MEDIUM
        ),
        DashboardTile(
            id="co2_savings",
            title="CO₂-Einsparung",
            value=f"{co2_savings:,.0f}".replace(",", "."),
            unit="kg/Jahr",
            icon="eco",
            color="success",
            size=TileSize.MEDIUM
        ),
    ]
    
    # Create charts
    charts = [
        ChartConfig(
            id="heating_cost_comparison",
            title="Heizkostenvergleich",
            chart_type=ChartType.BAR,
            data=[
                {"system": "Gas (alt)", "cost": 2400},
                {"system": "Öl (alt)", "cost": 2800},
                {"system": "Wärmepumpe", "cost": 1200},
            ],
            x_axis="system",
            y_axis="cost",
            colors=["#EF4444", "#F59E0B", "#10B981"]
        ),
        ChartConfig(
            id="cop_monthly",
            title="COP im Jahresverlauf",
            chart_type=ChartType.LINE,
            data=[
                {"month": "Jan", "cop": 2.8},
                {"month": "Feb", "cop": 3.0},
                {"month": "Mar", "cop": 3.5},
                {"month": "Apr", "cop": 4.2},
                {"month": "Mai", "cop": 4.8},
                {"month": "Jun", "cop": 5.2},
                {"month": "Jul", "cop": 5.5},
                {"month": "Aug", "cop": 5.3},
                {"month": "Sep", "cop": 4.5},
                {"month": "Okt", "cop": 3.8},
                {"month": "Nov", "cop": 3.2},
                {"month": "Dez", "cop": 2.9},
            ],
            x_axis="month",
            y_axis="cop",
            colors=["#3B82F6"]
        ),
    ]
    
    # Price breakdown
    price_breakdown = [
        PriceBreakdown(category="heatpump", label="Wärmepumpe", amount=14000, percentage=50),
        PriceBreakdown(category="installation", label="Installation", amount=6000, percentage=21),
        PriceBreakdown(category="hydraulics", label="Hydraulik", amount=4000, percentage=14),
        PriceBreakdown(category="electrical", label="Elektroinstallation", amount=2500, percentage=9),
        PriceBreakdown(category="other", label="Sonstiges", amount=1500, percentage=6),
    ]
    
    # Savings comparison
    savings_comparison = [
        SavingsComparison(
            category="heating",
            current_cost=2400,
            future_cost=1200,
            savings=1200,
            savings_percentage=50
        ),
    ]
    
    # Summary
    summary = ResultsSummary(
        calculation_type=CalculationType.HEATPUMP_ONLY,
        total_investment=total_investment,
        annual_savings=annual_savings,
        payback_years=payback_years,
        co2_savings_kg=co2_savings,
        roi_percent=(annual_savings / total_investment) * 100
    )
    
    return DashboardConfig(
        calculation_type=CalculationType.HEATPUMP_ONLY,
        tiles=tiles,
        charts=charts,
        price_breakdown=price_breakdown,
        savings_comparison=savings_comparison,
        summary=summary
    )


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_dashboard(
    calculation_type: CalculationType,
    calculation_data: Dict[str, Any]
):
    """Generate results dashboard from calculation data."""
    if calculation_type == CalculationType.PV_ONLY:
        dashboard = create_pv_dashboard(calculation_data)
    elif calculation_type == CalculationType.HEATPUMP_ONLY:
        dashboard = create_heatpump_dashboard(calculation_data)
    else:
        # Combined - merge both dashboards
        pv_dashboard = create_pv_dashboard(calculation_data)
        hp_dashboard = create_heatpump_dashboard(calculation_data)
        
        dashboard = DashboardConfig(
            calculation_type=CalculationType.COMBINED,
            tiles=pv_dashboard.tiles + hp_dashboard.tiles,
            charts=pv_dashboard.charts + hp_dashboard.charts,
            price_breakdown=pv_dashboard.price_breakdown + hp_dashboard.price_breakdown,
            savings_comparison=pv_dashboard.savings_comparison + hp_dashboard.savings_comparison,
            summary=ResultsSummary(
                calculation_type=CalculationType.COMBINED,
                system_power_kwp=pv_dashboard.summary.system_power_kwp,
                annual_yield_kwh=pv_dashboard.summary.annual_yield_kwh,
                self_consumption_rate=pv_dashboard.summary.self_consumption_rate,
                autarky_rate=pv_dashboard.summary.autarky_rate,
                total_investment=pv_dashboard.summary.total_investment + hp_dashboard.summary.total_investment,
                annual_savings=pv_dashboard.summary.annual_savings + hp_dashboard.summary.annual_savings,
                payback_years=(pv_dashboard.summary.total_investment + hp_dashboard.summary.total_investment) / 
                             (pv_dashboard.summary.annual_savings + hp_dashboard.summary.annual_savings),
                co2_savings_kg=(pv_dashboard.summary.co2_savings_kg or 0) + (hp_dashboard.summary.co2_savings_kg or 0)
            )
        )
    
    return {"dashboard": dashboard}


@router.get("/tiles/{calculation_type}")
async def get_dashboard_tiles(calculation_type: CalculationType):
    """Get dashboard tiles for calculation type."""
    if calculation_type == CalculationType.PV_ONLY:
        dashboard = create_pv_dashboard({})
    elif calculation_type == CalculationType.HEATPUMP_ONLY:
        dashboard = create_heatpump_dashboard({})
    else:
        pv = create_pv_dashboard({})
        hp = create_heatpump_dashboard({})
        return {"tiles": pv.tiles + hp.tiles}
    
    return {"tiles": dashboard.tiles}


@router.get("/charts/{calculation_type}")
async def get_dashboard_charts(calculation_type: CalculationType):
    """Get dashboard charts for calculation type."""
    if calculation_type == CalculationType.PV_ONLY:
        dashboard = create_pv_dashboard({})
    elif calculation_type == CalculationType.HEATPUMP_ONLY:
        dashboard = create_heatpump_dashboard({})
    else:
        pv = create_pv_dashboard({})
        hp = create_heatpump_dashboard({})
        return {"charts": pv.charts + hp.charts}
    
    return {"charts": dashboard.charts}


@router.get("/price-breakdown/{calculation_type}")
async def get_price_breakdown(calculation_type: CalculationType):
    """Get price breakdown for calculation type."""
    if calculation_type == CalculationType.PV_ONLY:
        dashboard = create_pv_dashboard({})
    elif calculation_type == CalculationType.HEATPUMP_ONLY:
        dashboard = create_heatpump_dashboard({})
    else:
        pv = create_pv_dashboard({})
        hp = create_heatpump_dashboard({})
        return {"price_breakdown": pv.price_breakdown + hp.price_breakdown}
    
    return {"price_breakdown": dashboard.price_breakdown}


@router.post("/chart-toggle")
async def toggle_chart_visibility(chart_id: str, visible: bool):
    """Toggle chart visibility."""
    return {
        "chart_id": chart_id,
        "visible": visible,
        "message": f"Chart {chart_id} {'angezeigt' if visible else 'ausgeblendet'}"
    }


@router.get("/export/{calculation_type}")
async def export_dashboard_data(calculation_type: CalculationType, format: str = "json"):
    """Export dashboard data."""
    if calculation_type == CalculationType.PV_ONLY:
        dashboard = create_pv_dashboard({})
    elif calculation_type == CalculationType.HEATPUMP_ONLY:
        dashboard = create_heatpump_dashboard({})
    else:
        pv = create_pv_dashboard({})
        hp = create_heatpump_dashboard({})
        dashboard = DashboardConfig(
            calculation_type=CalculationType.COMBINED,
            tiles=pv.tiles + hp.tiles,
            charts=pv.charts + hp.charts,
            price_breakdown=pv.price_breakdown + hp.price_breakdown,
            savings_comparison=pv.savings_comparison + hp.savings_comparison,
            summary=pv.summary
        )
    
    return {
        "format": format,
        "data": dashboard.dict(),
        "exported_at": datetime.now().isoformat()
    }


@router.get("/health/check")
async def health_check():
    """Health check for results dashboard service."""
    return {
        "status": "healthy",
        "service": "results-dashboard",
        "calculation_types": [ct.value for ct in CalculationType],
        "chart_types": [ct.value for ct in ChartType],
        "timestamp": datetime.now().isoformat()
    }
