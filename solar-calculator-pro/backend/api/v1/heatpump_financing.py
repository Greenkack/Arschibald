"""
Heat Pump Financing Options API

Provides REST API for heat pump financing calculations:
- Financing input fields (loan amount, interest, term)
- Monthly payment calculation
- Integration into amortization calculation
- Financing comparison scenarios
- Financing impact on ROI

Requirements: funktionen.txt - "Optionale Finanzierung"
Task: 256. Heat Pump Financing Options
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import math

router = APIRouter(prefix="/heatpump/financing", tags=["Heat Pump Financing"])


# ==================== Enums ====================

class FinancingType(str, Enum):
    """Financing type"""
    ANNUITY = "annuity"              # Annuitätendarlehen
    LINEAR = "linear"                # Lineares Darlehen
    BALLOON = "balloon"              # Ballonfinanzierung
    LEASING = "leasing"              # Leasing


class SubsidyProgram(str, Enum):
    """Available subsidy programs"""
    BAFA = "bafa"                    # BAFA Förderung
    KFW = "kfw"                      # KfW Förderung
    REGIONAL = "regional"            # Regionale Förderung
    NONE = "none"                    # Keine Förderung


# ==================== Pydantic Models ====================

class FinancingRequest(BaseModel):
    """Request for financing calculation"""
    total_investment_eur: float = Field(..., gt=0, description="Gesamtinvestition in EUR")
    loan_amount_eur: Optional[float] = Field(None, description="Darlehensbetrag (default: Gesamtinvestition)")
    interest_rate_percent: float = Field(default=4.5, ge=0, le=20, description="Zinssatz in %")
    term_years: int = Field(default=15, ge=1, le=30, description="Laufzeit in Jahren")
    financing_type: FinancingType = Field(default=FinancingType.ANNUITY)
    down_payment_eur: float = Field(default=0, ge=0, description="Anzahlung in EUR")
    subsidy_program: SubsidyProgram = Field(default=SubsidyProgram.BAFA)
    subsidy_percent: Optional[float] = Field(None, ge=0, le=70, description="Fördersatz in %")


class MonthlyPayment(BaseModel):
    """Monthly payment details"""
    month: int
    payment_eur: float
    principal_eur: float
    interest_eur: float
    remaining_balance_eur: float


class FinancingResult(BaseModel):
    """Result of financing calculation"""
    loan_amount_eur: float
    monthly_payment_eur: float
    total_payments_eur: float
    total_interest_eur: float
    effective_interest_rate_percent: float
    subsidy_amount_eur: float
    net_investment_eur: float
    payment_schedule: List[MonthlyPayment]
    summary: Dict[str, Any]


class AmortizationIntegration(BaseModel):
    """Amortization calculation with financing"""
    annual_savings_eur: float = Field(..., gt=0, description="Jährliche Einsparung")
    financing: FinancingRequest
    energy_price_increase_percent: float = Field(default=3.0, ge=0, le=20)


class AmortizationResult(BaseModel):
    """Result of amortization with financing"""
    payback_period_years: float
    payback_period_with_financing_years: float
    total_savings_20_years_eur: float
    total_cost_20_years_eur: float
    net_benefit_20_years_eur: float
    roi_percent: float
    yearly_cashflow: List[Dict[str, float]]


class FinancingComparison(BaseModel):
    """Comparison of financing scenarios"""
    scenarios: List[Dict[str, Any]]
    best_scenario: str
    recommendation: str


# ==================== Constants ====================

# Default subsidy rates by program
SUBSIDY_RATES = {
    SubsidyProgram.BAFA: 30,      # 30% BAFA Förderung
    SubsidyProgram.KFW: 25,       # 25% KfW Förderung
    SubsidyProgram.REGIONAL: 15,  # 15% Regional
    SubsidyProgram.NONE: 0
}

# Additional bonus for replacing old oil heating
OIL_REPLACEMENT_BONUS = 10  # 10% extra


# ==================== Helper Functions ====================

def calculate_annuity_payment(
    principal: float,
    annual_rate: float,
    term_years: int
) -> float:
    """Calculate monthly annuity payment"""
    if annual_rate == 0:
        return principal / (term_years * 12)
    
    monthly_rate = annual_rate / 100 / 12
    num_payments = term_years * 12
    
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    
    return round(payment, 2)


def calculate_linear_payment(
    principal: float,
    annual_rate: float,
    term_years: int,
    month: int
) -> tuple:
    """Calculate linear payment for a specific month"""
    monthly_principal = principal / (term_years * 12)
    remaining = principal - (month - 1) * monthly_principal
    monthly_interest = remaining * (annual_rate / 100 / 12)
    
    return round(monthly_principal + monthly_interest, 2), round(monthly_principal, 2), round(monthly_interest, 2)


def generate_payment_schedule(
    principal: float,
    annual_rate: float,
    term_years: int,
    financing_type: FinancingType
) -> List[MonthlyPayment]:
    """Generate complete payment schedule"""
    schedule = []
    remaining = principal
    monthly_rate = annual_rate / 100 / 12
    num_payments = term_years * 12
    
    if financing_type == FinancingType.ANNUITY:
        monthly_payment = calculate_annuity_payment(principal, annual_rate, term_years)
        
        for month in range(1, num_payments + 1):
            interest = remaining * monthly_rate
            principal_payment = monthly_payment - interest
            remaining -= principal_payment
            
            schedule.append(MonthlyPayment(
                month=month,
                payment_eur=round(monthly_payment, 2),
                principal_eur=round(principal_payment, 2),
                interest_eur=round(interest, 2),
                remaining_balance_eur=round(max(0, remaining), 2)
            ))
    
    elif financing_type == FinancingType.LINEAR:
        monthly_principal = principal / num_payments
        
        for month in range(1, num_payments + 1):
            interest = remaining * monthly_rate
            payment = monthly_principal + interest
            remaining -= monthly_principal
            
            schedule.append(MonthlyPayment(
                month=month,
                payment_eur=round(payment, 2),
                principal_eur=round(monthly_principal, 2),
                interest_eur=round(interest, 2),
                remaining_balance_eur=round(max(0, remaining), 2)
            ))
    
    return schedule


def calculate_subsidy(
    investment: float,
    program: SubsidyProgram,
    custom_rate: Optional[float] = None
) -> float:
    """Calculate subsidy amount"""
    rate = custom_rate if custom_rate is not None else SUBSIDY_RATES.get(program, 0)
    return round(investment * rate / 100, 2)


def calculate_effective_rate(
    principal: float,
    monthly_payment: float,
    term_years: int
) -> float:
    """Calculate effective annual interest rate"""
    total_paid = monthly_payment * term_years * 12
    total_interest = total_paid - principal
    
    if principal <= 0:
        return 0
    
    # Simple approximation
    avg_balance = principal / 2
    annual_interest = total_interest / term_years
    effective_rate = (annual_interest / avg_balance) * 100
    
    return round(effective_rate, 2)


# ==================== API Endpoints ====================

@router.post("/calculate", response_model=FinancingResult)
async def calculate_financing(request: FinancingRequest):
    """
    Calculate financing details including monthly payments and total costs.
    """
    # Calculate subsidy
    subsidy = calculate_subsidy(
        request.total_investment_eur,
        request.subsidy_program,
        request.subsidy_percent
    )
    
    # Calculate net investment
    net_investment = request.total_investment_eur - subsidy - request.down_payment_eur
    
    # Loan amount (default to net investment if not specified)
    loan_amount = request.loan_amount_eur if request.loan_amount_eur else net_investment
    loan_amount = min(loan_amount, net_investment)  # Can't borrow more than needed
    
    # Calculate monthly payment
    monthly_payment = calculate_annuity_payment(
        loan_amount,
        request.interest_rate_percent,
        request.term_years
    )
    
    # Generate payment schedule
    schedule = generate_payment_schedule(
        loan_amount,
        request.interest_rate_percent,
        request.term_years,
        request.financing_type
    )
    
    # Calculate totals
    total_payments = monthly_payment * request.term_years * 12
    total_interest = total_payments - loan_amount
    
    # Effective rate
    effective_rate = calculate_effective_rate(loan_amount, monthly_payment, request.term_years)
    
    return FinancingResult(
        loan_amount_eur=loan_amount,
        monthly_payment_eur=monthly_payment,
        total_payments_eur=round(total_payments, 2),
        total_interest_eur=round(total_interest, 2),
        effective_interest_rate_percent=effective_rate,
        subsidy_amount_eur=subsidy,
        net_investment_eur=net_investment,
        payment_schedule=schedule[:24],  # First 24 months only
        summary={
            "total_investment": request.total_investment_eur,
            "subsidy": subsidy,
            "down_payment": request.down_payment_eur,
            "loan_amount": loan_amount,
            "term_years": request.term_years,
            "interest_rate": request.interest_rate_percent,
            "financing_type": request.financing_type.value
        }
    )


@router.post("/amortization", response_model=AmortizationResult)
async def calculate_amortization_with_financing(request: AmortizationIntegration):
    """
    Calculate amortization period including financing costs.
    """
    # Calculate financing
    financing = request.financing
    subsidy = calculate_subsidy(
        financing.total_investment_eur,
        financing.subsidy_program,
        financing.subsidy_percent
    )
    
    net_investment = financing.total_investment_eur - subsidy - financing.down_payment_eur
    loan_amount = financing.loan_amount_eur if financing.loan_amount_eur else net_investment
    
    monthly_payment = calculate_annuity_payment(
        loan_amount,
        financing.interest_rate_percent,
        financing.term_years
    )
    
    annual_financing_cost = monthly_payment * 12
    
    # Calculate payback periods
    # Simple payback (without financing)
    simple_payback = financing.total_investment_eur / request.annual_savings_eur
    
    # Payback with financing
    yearly_cashflow = []
    cumulative_savings = 0
    cumulative_costs = financing.down_payment_eur
    payback_with_financing = None
    
    for year in range(1, 21):
        # Savings with energy price increase
        savings = request.annual_savings_eur * ((1 + request.energy_price_increase_percent / 100) ** (year - 1))
        
        # Financing cost (only during loan term)
        financing_cost = annual_financing_cost if year <= financing.term_years else 0
        
        # Net cashflow
        net_cashflow = savings - financing_cost
        cumulative_savings += savings
        cumulative_costs += financing_cost
        
        # Check payback
        if payback_with_financing is None and cumulative_savings >= cumulative_costs + net_investment:
            payback_with_financing = year
        
        yearly_cashflow.append({
            "year": year,
            "savings_eur": round(savings, 2),
            "financing_cost_eur": round(financing_cost, 2),
            "net_cashflow_eur": round(net_cashflow, 2),
            "cumulative_savings_eur": round(cumulative_savings, 2),
            "cumulative_costs_eur": round(cumulative_costs, 2)
        })
    
    # Calculate totals
    total_savings_20y = cumulative_savings
    total_costs_20y = cumulative_costs + net_investment
    net_benefit = total_savings_20y - total_costs_20y
    roi = (net_benefit / financing.total_investment_eur) * 100
    
    return AmortizationResult(
        payback_period_years=round(simple_payback, 1),
        payback_period_with_financing_years=payback_with_financing or 20,
        total_savings_20_years_eur=round(total_savings_20y, 2),
        total_cost_20_years_eur=round(total_costs_20y, 2),
        net_benefit_20_years_eur=round(net_benefit, 2),
        roi_percent=round(roi, 1),
        yearly_cashflow=yearly_cashflow
    )


@router.post("/compare")
async def compare_financing_scenarios(
    total_investment_eur: float = Query(..., gt=0),
    annual_savings_eur: float = Query(..., gt=0),
    scenarios: str = Query("5,10,15,20", description="Comma-separated loan terms in years")
):
    """
    Compare different financing scenarios.
    """
    terms = [int(t.strip()) for t in scenarios.split(",")]
    results = []
    
    for term in terms:
        monthly = calculate_annuity_payment(total_investment_eur, 4.5, term)
        total_paid = monthly * term * 12
        total_interest = total_paid - total_investment_eur
        
        # Simple ROI calculation
        total_savings = annual_savings_eur * 20
        net_benefit = total_savings - total_paid
        
        results.append({
            "term_years": term,
            "monthly_payment_eur": monthly,
            "total_payments_eur": round(total_paid, 2),
            "total_interest_eur": round(total_interest, 2),
            "net_benefit_20y_eur": round(net_benefit, 2),
            "monthly_net_cashflow_eur": round(annual_savings_eur / 12 - monthly, 2)
        })
    
    # Find best scenario (highest net benefit with positive monthly cashflow)
    positive_cashflow = [r for r in results if r["monthly_net_cashflow_eur"] >= 0]
    if positive_cashflow:
        best = max(positive_cashflow, key=lambda x: x["net_benefit_20y_eur"])
        best_scenario = f"{best['term_years']} Jahre"
        recommendation = f"Empfehlung: {best['term_years']} Jahre Laufzeit mit {best['monthly_payment_eur']:.2f} €/Monat"
    else:
        best = min(results, key=lambda x: x["monthly_payment_eur"])
        best_scenario = f"{best['term_years']} Jahre"
        recommendation = f"Längste Laufzeit ({best['term_years']} Jahre) für niedrigste Rate empfohlen"
    
    return FinancingComparison(
        scenarios=results,
        best_scenario=best_scenario,
        recommendation=recommendation
    )


@router.get("/subsidies")
async def get_subsidy_programs():
    """
    Get available subsidy programs and rates.
    """
    return {
        "programs": [
            {
                "program": SubsidyProgram.BAFA.value,
                "name": "BAFA Förderung",
                "description": "Bundesförderung für effiziente Gebäude (BEG)",
                "base_rate_percent": 30,
                "oil_bonus_percent": 10,
                "max_rate_percent": 40,
                "max_amount_eur": 21000,
                "requirements": ["Energieeffizienz-Experte", "Antrag vor Maßnahmenbeginn"]
            },
            {
                "program": SubsidyProgram.KFW.value,
                "name": "KfW Förderung",
                "description": "KfW-Kredit mit Tilgungszuschuss",
                "base_rate_percent": 25,
                "max_loan_eur": 150000,
                "interest_rate_percent": 2.5,
                "requirements": ["Energieberater", "Antrag über Hausbank"]
            },
            {
                "program": SubsidyProgram.REGIONAL.value,
                "name": "Regionale Förderung",
                "description": "Landesspezifische Förderprogramme",
                "base_rate_percent": 15,
                "note": "Variiert je nach Bundesland"
            }
        ],
        "combination_note": "BAFA und regionale Förderung können kombiniert werden (max. 60%)"
    }


@router.get("/quick-calculation")
async def quick_financing_calculation(
    investment_eur: float = Query(..., gt=0),
    term_years: int = Query(15, ge=1, le=30),
    interest_rate_percent: float = Query(4.5, ge=0, le=20),
    subsidy_percent: float = Query(30, ge=0, le=70)
):
    """
    Quick financing calculation with minimal input.
    """
    subsidy = investment_eur * subsidy_percent / 100
    loan_amount = investment_eur - subsidy
    monthly = calculate_annuity_payment(loan_amount, interest_rate_percent, term_years)
    total_paid = monthly * term_years * 12
    total_interest = total_paid - loan_amount
    
    return {
        "investment_eur": investment_eur,
        "subsidy_eur": round(subsidy, 2),
        "loan_amount_eur": round(loan_amount, 2),
        "monthly_payment_eur": monthly,
        "total_payments_eur": round(total_paid, 2),
        "total_interest_eur": round(total_interest, 2),
        "term_years": term_years,
        "interest_rate_percent": interest_rate_percent
    }


@router.get("/roi-impact")
async def calculate_roi_impact(
    investment_eur: float = Query(..., gt=0),
    annual_savings_eur: float = Query(..., gt=0),
    interest_rate_percent: float = Query(4.5, ge=0, le=20),
    term_years: int = Query(15, ge=1, le=30),
    subsidy_percent: float = Query(30, ge=0, le=70)
):
    """
    Calculate financing impact on ROI.
    """
    # Without financing
    simple_payback = investment_eur / annual_savings_eur
    simple_roi_20y = ((annual_savings_eur * 20) - investment_eur) / investment_eur * 100
    
    # With financing
    subsidy = investment_eur * subsidy_percent / 100
    loan_amount = investment_eur - subsidy
    monthly = calculate_annuity_payment(loan_amount, interest_rate_percent, term_years)
    total_financing_cost = monthly * term_years * 12
    
    total_savings_20y = annual_savings_eur * 20
    net_cost = total_financing_cost  # Already paid subsidy
    financed_roi_20y = (total_savings_20y - net_cost) / investment_eur * 100
    
    return {
        "without_financing": {
            "payback_years": round(simple_payback, 1),
            "roi_20_years_percent": round(simple_roi_20y, 1),
            "total_savings_20y_eur": round(annual_savings_eur * 20, 2)
        },
        "with_financing": {
            "monthly_payment_eur": monthly,
            "total_financing_cost_eur": round(total_financing_cost, 2),
            "subsidy_eur": round(subsidy, 2),
            "roi_20_years_percent": round(financed_roi_20y, 1),
            "net_benefit_20y_eur": round(total_savings_20y - net_cost, 2)
        },
        "comparison": {
            "roi_difference_percent": round(financed_roi_20y - simple_roi_20y, 1),
            "financing_recommended": financed_roi_20y > 0
        }
    }


@router.get("/health/check")
async def health_check():
    """
    Health check for financing service.
    """
    return {
        "status": "healthy",
        "service": "heatpump-financing",
        "subsidy_programs": len(SubsidyProgram),
        "financing_types": len(FinancingType),
        "timestamp": datetime.now().isoformat()
    }
