"""
Financial Calculation Functions API

Provides REST API for financial calculations:
- FinancialCalculator class
- Compound interest calculations
- Loan payment calculations
- Investment value calculations
- Break-even point analysis
- Mortgage payment calculations
- Annuity factor calculations

Requirements: funktionen.txt - "financial_calculations.py"
Task: 290. Financial Calculation Functions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import math

router = APIRouter(prefix="/financial", tags=["Financial Calculations"])


# ==================== Enums ====================

class PaymentFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class LoanType(str, Enum):
    ANNUITY = "annuity"
    LINEAR = "linear"
    BULLET = "bullet"


# ==================== Pydantic Models ====================

class CompoundInterestInput(BaseModel):
    """Compound interest input"""
    principal: float = Field(..., ge=0)
    annual_rate_percent: float = Field(..., ge=0, le=100)
    years: int = Field(..., ge=1, le=50)
    compounds_per_year: int = Field(12, ge=1, le=365)
    monthly_contribution: float = Field(0, ge=0)


class LoanInput(BaseModel):
    """Loan calculation input"""
    principal: float = Field(..., ge=0)
    annual_rate_percent: float = Field(..., ge=0, le=30)
    term_years: int = Field(..., ge=1, le=40)
    loan_type: LoanType = LoanType.ANNUITY
    down_payment_percent: float = Field(0, ge=0, le=100)


class InvestmentInput(BaseModel):
    """Investment calculation input"""
    initial_investment: float = Field(..., ge=0)
    annual_return_percent: float = Field(7, ge=-50, le=100)
    years: int = Field(20, ge=1, le=50)
    annual_contribution: float = Field(0, ge=0)
    inflation_rate_percent: float = Field(2, ge=0, le=20)


class BreakEvenInput(BaseModel):
    """Break-even analysis input"""
    fixed_costs: float = Field(..., ge=0)
    variable_cost_per_unit: float = Field(..., ge=0)
    price_per_unit: float = Field(..., ge=0)
    target_profit: float = Field(0, ge=0)


class MortgageInput(BaseModel):
    """Mortgage calculation input"""
    property_value: float = Field(..., ge=0)
    down_payment_percent: float = Field(20, ge=0, le=100)
    annual_rate_percent: float = Field(3.5, ge=0, le=20)
    term_years: int = Field(25, ge=5, le=40)
    include_insurance: bool = False
    annual_insurance_rate_percent: float = Field(0.5, ge=0, le=5)


class CashFlowInput(BaseModel):
    """Cash flow analysis input"""
    initial_investment: float
    annual_cash_flows: List[float]
    discount_rate_percent: float = Field(8, ge=0, le=50)


# ==================== Financial Calculator Class ====================

class FinancialCalculator:
    """Financial calculation utilities."""
    
    @staticmethod
    def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12,
        monthly_contribution: float = 0
    ) -> Dict[str, Any]:
        """Calculate compound interest with optional contributions."""
        rate_per_period = annual_rate / 100 / compounds_per_year
        total_periods = years * compounds_per_year
        
        # Future value of principal
        fv_principal = principal * ((1 + rate_per_period) ** total_periods)
        
        # Future value of contributions (if any)
        if monthly_contribution > 0 and rate_per_period > 0:
            contribution_per_period = monthly_contribution * (12 / compounds_per_year)
            fv_contributions = contribution_per_period * (((1 + rate_per_period) ** total_periods - 1) / rate_per_period)
        else:
            fv_contributions = monthly_contribution * 12 * years
        
        total_value = fv_principal + fv_contributions
        total_contributions = principal + (monthly_contribution * 12 * years)
        total_interest = total_value - total_contributions
        
        return {
            "future_value": round(total_value, 2),
            "total_contributions": round(total_contributions, 2),
            "total_interest_earned": round(total_interest, 2),
            "effective_annual_rate": round((1 + rate_per_period) ** compounds_per_year - 1, 4) * 100
        }
    
    @staticmethod
    def calculate_loan_payment(
        principal: float,
        annual_rate: float,
        term_years: int,
        loan_type: LoanType = LoanType.ANNUITY
    ) -> Dict[str, Any]:
        """Calculate loan payment details."""
        monthly_rate = annual_rate / 100 / 12
        total_payments = term_years * 12
        
        if loan_type == LoanType.ANNUITY:
            if monthly_rate > 0:
                monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
            else:
                monthly_payment = principal / total_payments
            
            total_paid = monthly_payment * total_payments
            total_interest = total_paid - principal
            
        elif loan_type == LoanType.LINEAR:
            principal_payment = principal / total_payments
            # Average interest (first + last payment) / 2
            first_interest = principal * monthly_rate
            last_interest = principal_payment * monthly_rate
            avg_interest = (first_interest + last_interest) / 2
            monthly_payment = principal_payment + avg_interest  # Average
            total_interest = (principal * monthly_rate * (total_payments + 1)) / 2
            total_paid = principal + total_interest
            
        else:  # Bullet
            monthly_payment = principal * monthly_rate
            total_interest = monthly_payment * total_payments
            total_paid = principal + total_interest
        
        return {
            "monthly_payment": round(monthly_payment, 2),
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_interest, 2),
            "interest_to_principal_ratio": round(total_interest / principal * 100, 1) if principal > 0 else 0
        }
    
    @staticmethod
    def calculate_investment_value(
        initial_investment: float,
        annual_return: float,
        years: int,
        annual_contribution: float = 0,
        inflation_rate: float = 2
    ) -> Dict[str, Any]:
        """Calculate investment value over time."""
        nominal_value = initial_investment
        real_value = initial_investment
        
        yearly_data = []
        
        for year in range(1, years + 1):
            # Nominal growth
            nominal_value = nominal_value * (1 + annual_return / 100) + annual_contribution
            
            # Real value (inflation adjusted)
            inflation_factor = (1 + inflation_rate / 100) ** year
            real_value = nominal_value / inflation_factor
            
            yearly_data.append({
                "year": year,
                "nominal_value": round(nominal_value, 2),
                "real_value": round(real_value, 2)
            })
        
        total_contributions = initial_investment + (annual_contribution * years)
        
        return {
            "final_nominal_value": round(nominal_value, 2),
            "final_real_value": round(real_value, 2),
            "total_contributions": round(total_contributions, 2),
            "nominal_gain": round(nominal_value - total_contributions, 2),
            "real_gain": round(real_value - total_contributions, 2),
            "yearly_data": yearly_data
        }
    
    @staticmethod
    def calculate_break_even_point(
        fixed_costs: float,
        variable_cost_per_unit: float,
        price_per_unit: float,
        target_profit: float = 0
    ) -> Dict[str, Any]:
        """Calculate break-even point."""
        contribution_margin = price_per_unit - variable_cost_per_unit
        
        if contribution_margin <= 0:
            return {
                "break_even_units": None,
                "break_even_revenue": None,
                "contribution_margin": contribution_margin,
                "error": "Contribution margin must be positive"
            }
        
        break_even_units = (fixed_costs + target_profit) / contribution_margin
        break_even_revenue = break_even_units * price_per_unit
        
        return {
            "break_even_units": round(break_even_units, 0),
            "break_even_revenue": round(break_even_revenue, 2),
            "contribution_margin": round(contribution_margin, 2),
            "contribution_margin_ratio": round(contribution_margin / price_per_unit * 100, 1)
        }
    
    @staticmethod
    def calculate_mortgage_payment(
        property_value: float,
        down_payment_percent: float,
        annual_rate: float,
        term_years: int,
        include_insurance: bool = False,
        insurance_rate: float = 0.5
    ) -> Dict[str, Any]:
        """Calculate mortgage payment details."""
        down_payment = property_value * (down_payment_percent / 100)
        loan_amount = property_value - down_payment
        
        monthly_rate = annual_rate / 100 / 12
        total_payments = term_years * 12
        
        if monthly_rate > 0:
            monthly_principal_interest = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
        else:
            monthly_principal_interest = loan_amount / total_payments
        
        monthly_insurance = (property_value * insurance_rate / 100 / 12) if include_insurance else 0
        total_monthly = monthly_principal_interest + monthly_insurance
        
        total_paid = total_monthly * total_payments
        total_interest = (monthly_principal_interest * total_payments) - loan_amount
        
        return {
            "property_value": property_value,
            "down_payment": round(down_payment, 2),
            "loan_amount": round(loan_amount, 2),
            "monthly_principal_interest": round(monthly_principal_interest, 2),
            "monthly_insurance": round(monthly_insurance, 2),
            "total_monthly_payment": round(total_monthly, 2),
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_interest, 2)
        }
    
    @staticmethod
    def calculate_annuity_factor(
        annual_rate: float,
        years: int,
        payments_per_year: int = 12
    ) -> float:
        """Calculate annuity factor."""
        rate_per_period = annual_rate / 100 / payments_per_year
        total_periods = years * payments_per_year
        
        if rate_per_period == 0:
            return total_periods
        
        annuity_factor = ((1 + rate_per_period) ** total_periods - 1) / (rate_per_period * (1 + rate_per_period) ** total_periods)
        return round(annuity_factor, 4)
    
    @staticmethod
    def calculate_npv(
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: float
    ) -> float:
        """Calculate Net Present Value."""
        npv = -initial_investment
        for i, cf in enumerate(cash_flows, 1):
            npv += cf / ((1 + discount_rate / 100) ** i)
        return round(npv, 2)
    
    @staticmethod
    def calculate_irr(
        initial_investment: float,
        cash_flows: List[float]
    ) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson."""
        all_flows = [-initial_investment] + cash_flows
        
        irr = 0.10  # Initial guess
        for _ in range(100):
            npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(all_flows))
            npv_derivative = sum(-i * cf / (1 + irr) ** (i + 1) for i, cf in enumerate(all_flows))
            
            if abs(npv_derivative) < 1e-10:
                break
            
            irr = irr - npv / npv_derivative
            
            if abs(npv) < 1e-6:
                break
        
        return round(irr * 100, 2)


# Create calculator instance
calculator = FinancialCalculator()


# ==================== API Endpoints ====================

@router.post("/compound-interest")
async def calculate_compound_interest(input_data: CompoundInterestInput):
    """Calculate compound interest."""
    result = calculator.calculate_compound_interest(
        input_data.principal,
        input_data.annual_rate_percent,
        input_data.years,
        input_data.compounds_per_year,
        input_data.monthly_contribution
    )
    return {"input": input_data.dict(), "result": result}


@router.post("/loan-payment")
async def calculate_loan_payment(input_data: LoanInput):
    """Calculate loan payment."""
    actual_principal = input_data.principal * (1 - input_data.down_payment_percent / 100)
    
    result = calculator.calculate_loan_payment(
        actual_principal,
        input_data.annual_rate_percent,
        input_data.term_years,
        input_data.loan_type
    )
    
    result["down_payment"] = round(input_data.principal * input_data.down_payment_percent / 100, 2)
    result["loan_amount"] = round(actual_principal, 2)
    
    return {"input": input_data.dict(), "result": result}


@router.post("/investment-value")
async def calculate_investment_value(input_data: InvestmentInput):
    """Calculate investment value over time."""
    result = calculator.calculate_investment_value(
        input_data.initial_investment,
        input_data.annual_return_percent,
        input_data.years,
        input_data.annual_contribution,
        input_data.inflation_rate_percent
    )
    return {"input": input_data.dict(), "result": result}


@router.post("/break-even")
async def calculate_break_even(input_data: BreakEvenInput):
    """Calculate break-even point."""
    result = calculator.calculate_break_even_point(
        input_data.fixed_costs,
        input_data.variable_cost_per_unit,
        input_data.price_per_unit,
        input_data.target_profit
    )
    return {"input": input_data.dict(), "result": result}


@router.post("/mortgage")
async def calculate_mortgage(input_data: MortgageInput):
    """Calculate mortgage payment."""
    result = calculator.calculate_mortgage_payment(
        input_data.property_value,
        input_data.down_payment_percent,
        input_data.annual_rate_percent,
        input_data.term_years,
        input_data.include_insurance,
        input_data.annual_insurance_rate_percent
    )
    return {"input": input_data.dict(), "result": result}


@router.post("/cash-flow-analysis")
async def analyze_cash_flow(input_data: CashFlowInput):
    """Analyze cash flows (NPV, IRR)."""
    npv = calculator.calculate_npv(
        input_data.initial_investment,
        input_data.annual_cash_flows,
        input_data.discount_rate_percent
    )
    
    irr = calculator.calculate_irr(
        input_data.initial_investment,
        input_data.annual_cash_flows
    )
    
    total_cash_flow = sum(input_data.annual_cash_flows)
    payback_years = None
    cumulative = 0
    for i, cf in enumerate(input_data.annual_cash_flows, 1):
        cumulative += cf
        if cumulative >= input_data.initial_investment and payback_years is None:
            payback_years = i
    
    return {
        "input": input_data.dict(),
        "result": {
            "npv": npv,
            "irr_percent": irr,
            "total_cash_flow": round(total_cash_flow, 2),
            "payback_years": payback_years,
            "profitable": npv > 0
        }
    }


@router.get("/annuity-factor")
async def get_annuity_factor(
    annual_rate_percent: float,
    years: int,
    payments_per_year: int = 12
):
    """Calculate annuity factor."""
    factor = calculator.calculate_annuity_factor(annual_rate_percent, years, payments_per_year)
    return {
        "annual_rate_percent": annual_rate_percent,
        "years": years,
        "payments_per_year": payments_per_year,
        "annuity_factor": factor
    }


@router.post("/amortization-schedule")
async def generate_amortization_schedule(input_data: LoanInput):
    """Generate loan amortization schedule."""
    actual_principal = input_data.principal * (1 - input_data.down_payment_percent / 100)
    monthly_rate = input_data.annual_rate_percent / 100 / 12
    total_payments = input_data.term_years * 12
    
    if monthly_rate > 0:
        monthly_payment = actual_principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
    else:
        monthly_payment = actual_principal / total_payments
    
    schedule = []
    balance = actual_principal
    total_interest = 0
    total_principal = 0
    
    for month in range(1, min(total_payments + 1, 361)):  # Max 30 years
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        
        total_interest += interest_payment
        total_principal += principal_payment
        
        if month <= 12 or month % 12 == 0:  # First year monthly, then yearly
            schedule.append({
                "month": month,
                "payment": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(max(balance, 0), 2),
                "cumulative_interest": round(total_interest, 2)
            })
    
    return {
        "loan_amount": round(actual_principal, 2),
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "schedule": schedule
    }


@router.get("/health/check")
async def health_check():
    """Health check for financial calculations service."""
    return {
        "status": "healthy",
        "service": "financial-calculations",
        "functions_available": 8,
        "timestamp": datetime.now().isoformat()
    }
