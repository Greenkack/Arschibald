"""
Financial Analysis Pydantic Schemas
Defines request/response models for financial calculations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class FinancingType(str, Enum):
    """Types of financing options"""
    CASH = "cash"
    LOAN = "loan"
    LEASE = "lease"
    PPA = "ppa"  # Power Purchase Agreement


class TaxIncentiveType(str, Enum):
    """Types of tax incentives"""
    ITC = "investment_tax_credit"  # Investment Tax Credit
    DEPRECIATION = "depreciation"  # Accelerated Depreciation
    GRANT = "grant"  # Direct Grant
    REBATE = "rebate"  # Utility Rebate


class FinancingOption(BaseModel):
    """Financing option details"""
    type: FinancingType
    name: str
    down_payment: float = Field(..., ge=0, description="Down payment amount in EUR")
    down_payment_percent: float = Field(..., ge=0, le=100, description="Down payment as percentage")
    loan_amount: float = Field(..., ge=0, description="Loan amount in EUR")
    interest_rate: float = Field(..., ge=0, le=100, description="Annual interest rate in %")
    term_years: int = Field(..., ge=1, le=30, description="Loan term in years")
    monthly_payment: Optional[float] = Field(None, description="Monthly payment in EUR")
    total_interest: Optional[float] = Field(None, description="Total interest paid in EUR")
    total_cost: Optional[float] = Field(None, description="Total cost including interest in EUR")


class TaxIncentive(BaseModel):
    """Tax incentive details"""
    type: TaxIncentiveType
    name: str
    amount: float = Field(..., description="Incentive amount in EUR")
    year_received: int = Field(..., ge=1, description="Year when incentive is received")
    description: Optional[str] = None


class FinancialAnalysisRequest(BaseModel):
    """Request for financial analysis"""
    # System details
    system_size_kwp: float = Field(..., gt=0, description="System size in kWp")
    total_system_cost: float = Field(..., gt=0, description="Total system cost in EUR")
    annual_production_kwh: float = Field(..., gt=0, description="Annual energy production in kWh")
    
    # Energy costs
    current_electricity_price: float = Field(..., gt=0, description="Current electricity price in EUR/kWh")
    electricity_price_increase: float = Field(default=3.0, ge=0, le=20, description="Annual electricity price increase in %")
    feed_in_tariff: float = Field(default=0.08, ge=0, description="Feed-in tariff in EUR/kWh")
    
    # Consumption
    annual_consumption_kwh: float = Field(..., gt=0, description="Annual electricity consumption in kWh")
    self_consumption_rate: float = Field(default=30.0, ge=0, le=100, description="Self-consumption rate in %")
    
    # System parameters
    system_degradation: float = Field(default=0.5, ge=0, le=5, description="Annual system degradation in %")
    maintenance_cost_annual: float = Field(default=200.0, ge=0, description="Annual maintenance cost in EUR")
    maintenance_cost_increase: float = Field(default=2.0, ge=0, le=10, description="Annual maintenance cost increase in %")
    insurance_cost_annual: float = Field(default=150.0, ge=0, description="Annual insurance cost in EUR")
    
    # Financial parameters
    discount_rate: float = Field(default=4.0, ge=0, le=20, description="Discount rate for NPV in %")
    analysis_period_years: int = Field(default=25, ge=1, le=50, description="Analysis period in years")
    
    # Financing options
    financing_options: List[FinancingOption] = Field(default_factory=list)
    
    # Tax incentives
    tax_incentives: List[TaxIncentive] = Field(default_factory=list)
    
    # Tax parameters
    income_tax_rate: float = Field(default=30.0, ge=0, le=100, description="Income tax rate in %")
    
    class Config:
        json_schema_extra = {
            "example": {
                "system_size_kwp": 10.5,
                "total_system_cost": 16999.00,
                "annual_production_kwh": 12000,
                "current_electricity_price": 0.35,
                "electricity_price_increase": 3.0,
                "feed_in_tariff": 0.08,
                "annual_consumption_kwh": 4000,
                "self_consumption_rate": 35.0,
                "system_degradation": 0.5,
                "maintenance_cost_annual": 200.0,
                "insurance_cost_annual": 150.0,
                "discount_rate": 4.0,
                "analysis_period_years": 25,
                "income_tax_rate": 30.0
            }
        }


class YearlyCashFlow(BaseModel):
    """Cash flow for a single year"""
    year: int
    energy_production_kwh: float
    self_consumed_kwh: float
    exported_kwh: float
    electricity_savings: float
    feed_in_revenue: float
    total_revenue: float
    maintenance_cost: float
    insurance_cost: float
    loan_payment: float
    total_costs: float
    net_cash_flow: float
    cumulative_cash_flow: float
    tax_benefit: float


class ROIAnalysis(BaseModel):
    """Return on Investment analysis"""
    simple_roi_percent: float = Field(..., description="Simple ROI in %")
    simple_payback_years: float = Field(..., description="Simple payback period in years")
    discounted_payback_years: Optional[float] = Field(None, description="Discounted payback period in years")
    total_lifetime_savings: float = Field(..., description="Total savings over analysis period in EUR")
    average_annual_return: float = Field(..., description="Average annual return in EUR")
    average_annual_return_percent: float = Field(..., description="Average annual return in %")


class NPVAnalysis(BaseModel):
    """Net Present Value analysis"""
    npv: float = Field(..., description="Net Present Value in EUR")
    npv_positive: bool = Field(..., description="Whether NPV is positive")
    present_value_benefits: float = Field(..., description="Present value of all benefits in EUR")
    present_value_costs: float = Field(..., description="Present value of all costs in EUR")
    benefit_cost_ratio: float = Field(..., description="Benefit-Cost Ratio")


class IRRAnalysis(BaseModel):
    """Internal Rate of Return analysis"""
    irr_percent: float = Field(..., description="Internal Rate of Return in %")
    irr_exceeds_discount_rate: bool = Field(..., description="Whether IRR exceeds discount rate")
    modified_irr_percent: Optional[float] = Field(None, description="Modified IRR in %")


class FinancingComparison(BaseModel):
    """Comparison of financing options"""
    option_name: str
    financing_type: FinancingType
    total_cost: float
    monthly_payment: float
    total_interest: float
    npv: float
    irr_percent: float
    payback_years: float
    lifetime_savings: float
    rank: int = Field(..., description="Rank based on NPV (1 = best)")


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis for key parameters"""
    parameter: str
    base_value: float
    low_value: float
    high_value: float
    npv_at_low: float
    npv_at_base: float
    npv_at_high: float
    sensitivity_percent: float = Field(..., description="% change in NPV per % change in parameter")


class FinancialAnalysisResponse(BaseModel):
    """Complete financial analysis response"""
    # Input summary
    system_size_kwp: float
    total_system_cost: float
    analysis_period_years: int
    
    # ROI Analysis
    roi_analysis: ROIAnalysis
    
    # NPV Analysis
    npv_analysis: NPVAnalysis
    
    # IRR Analysis
    irr_analysis: IRRAnalysis
    
    # Cash flow projections
    yearly_cash_flows: List[YearlyCashFlow]
    
    # Financing comparisons
    financing_comparisons: List[FinancingComparison]
    
    # Sensitivity analysis
    sensitivity_analyses: List[SensitivityAnalysis]
    
    # Summary metrics
    total_energy_produced_kwh: float
    total_energy_savings_eur: float
    total_feed_in_revenue_eur: float
    total_maintenance_costs_eur: float
    total_insurance_costs_eur: float
    net_lifetime_benefit_eur: float
    
    # Environmental impact
    co2_savings_kg: float = Field(..., description="Total CO2 savings in kg")
    trees_equivalent: int = Field(..., description="Equivalent number of trees planted")
    
    # Recommendations
    recommended_financing: Optional[str] = Field(None, description="Recommended financing option")
    investment_grade: str = Field(..., description="Investment grade: Excellent/Good/Fair/Poor")
    key_insights: List[str] = Field(default_factory=list, description="Key insights and recommendations")
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.now)
    calculation_version: str = "1.0.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "system_size_kwp": 10.5,
                "total_system_cost": 16999.00,
                "analysis_period_years": 25,
                "roi_analysis": {
                    "simple_roi_percent": 285.5,
                    "simple_payback_years": 8.7,
                    "discounted_payback_years": 11.2,
                    "total_lifetime_savings": 48532.50,
                    "average_annual_return": 1941.30,
                    "average_annual_return_percent": 11.4
                },
                "npv_analysis": {
                    "npv": 25678.90,
                    "npv_positive": True,
                    "present_value_benefits": 42677.90,
                    "present_value_costs": 16999.00,
                    "benefit_cost_ratio": 2.51
                },
                "irr_analysis": {
                    "irr_percent": 12.8,
                    "irr_exceeds_discount_rate": True,
                    "modified_irr_percent": 11.5
                }
            }
        }
