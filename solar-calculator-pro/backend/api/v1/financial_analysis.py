"""
Financial Analysis API Endpoints
Provides REST API for solar financial analysis
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from ...models.financial_schemas import (
    FinancialAnalysisRequest,
    FinancialAnalysisResponse,
    FinancingOption,
    TaxIncentive
)
from ...services.financial_analysis_service import FinancialAnalysisService
from ...core.auth_dependencies import get_current_user

router = APIRouter(prefix="/financial-analysis", tags=["Financial Analysis"])


@router.post(
    "/calculate",
    response_model=FinancialAnalysisResponse,
    summary="Calculate comprehensive financial analysis",
    description="Performs complete financial analysis including ROI, NPV, IRR, cash flow projections, and financing comparisons"
)
async def calculate_financial_analysis(
    request: FinancialAnalysisRequest,
    current_user: str = Depends(get_current_user)
) -> FinancialAnalysisResponse:
    """
    Calculate comprehensive financial analysis for a solar project.
    
    This endpoint performs:
    - ROI (Return on Investment) calculations
    - NPV (Net Present Value) analysis
    - IRR (Internal Rate of Return) calculations
    - Payback period analysis (simple and discounted)
    - 25-year cash flow projections
    - Financing options comparison
    - Sensitivity analysis on key parameters
    - Environmental impact calculations
    
    Args:
        request: Financial analysis request with system and financial parameters
        current_user: Authenticated user (from JWT token)
        
    Returns:
        Complete financial analysis with all metrics and projections
        
    Raises:
        HTTPException: If calculation fails
    """
    try:
        service = FinancialAnalysisService()
        result = service.calculate_comprehensive_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Financial analysis calculation failed: {str(e)}"
        )


@router.post(
    "/quick-roi",
    summary="Calculate quick ROI estimate",
    description="Provides a quick ROI estimate without full analysis"
)
async def calculate_quick_roi(
    system_cost: float,
    annual_savings: float,
    analysis_years: int = 25,
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Calculate a quick ROI estimate.
    
    Args:
        system_cost: Total system cost in EUR
        annual_savings: Estimated annual savings in EUR
        analysis_years: Number of years for analysis
        current_user: Authenticated user
        
    Returns:
        Quick ROI metrics
    """
    try:
        total_savings = annual_savings * analysis_years
        roi_percent = (total_savings / system_cost) * 100
        payback_years = system_cost / annual_savings if annual_savings > 0 else 0
        
        return {
            "system_cost": system_cost,
            "annual_savings": annual_savings,
            "analysis_years": analysis_years,
            "total_savings": round(total_savings, 2),
            "roi_percent": round(roi_percent, 2),
            "simple_payback_years": round(payback_years, 1),
            "average_annual_return_percent": round(roi_percent / analysis_years, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick ROI calculation failed: {str(e)}"
        )


@router.post(
    "/calculate-loan-payment",
    summary="Calculate monthly loan payment",
    description="Calculates monthly payment for a loan"
)
async def calculate_loan_payment(
    loan_amount: float,
    interest_rate: float,
    term_years: int,
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Calculate monthly loan payment.
    
    Args:
        loan_amount: Loan amount in EUR
        interest_rate: Annual interest rate in %
        term_years: Loan term in years
        current_user: Authenticated user
        
    Returns:
        Loan payment details
    """
    try:
        service = FinancialAnalysisService()
        monthly_payment = service._calculate_monthly_payment(
            loan_amount, interest_rate, term_years
        )
        
        total_payments = monthly_payment * 12 * term_years
        total_interest = total_payments - loan_amount
        
        return {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "term_years": term_years,
            "monthly_payment": round(monthly_payment, 2),
            "total_payments": round(total_payments, 2),
            "total_interest": round(total_interest, 2),
            "total_cost": round(total_payments, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan payment calculation failed: {str(e)}"
        )


@router.post(
    "/compare-scenarios",
    summary="Compare multiple financial scenarios",
    description="Compares different system configurations or financing options"
)
async def compare_scenarios(
    scenarios: List[FinancialAnalysisRequest],
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Compare multiple financial scenarios.
    
    Args:
        scenarios: List of financial analysis requests to compare
        current_user: Authenticated user
        
    Returns:
        Comparison of all scenarios
    """
    try:
        if len(scenarios) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 scenarios can be compared at once"
            )
        
        service = FinancialAnalysisService()
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            analysis = service.calculate_comprehensive_analysis(scenario)
            results.append({
                "scenario_number": i,
                "system_size_kwp": scenario.system_size_kwp,
                "total_cost": scenario.total_system_cost,
                "npv": analysis.npv_analysis.npv,
                "irr_percent": analysis.irr_analysis.irr_percent,
                "payback_years": analysis.roi_analysis.simple_payback_years,
                "lifetime_savings": analysis.roi_analysis.total_lifetime_savings,
                "investment_grade": analysis.investment_grade
            })
        
        # Rank scenarios by NPV
        results.sort(key=lambda x: x["npv"], reverse=True)
        for i, result in enumerate(results, 1):
            result["rank"] = i
        
        return {
            "scenarios_compared": len(scenarios),
            "results": results,
            "best_scenario": results[0]["scenario_number"],
            "recommendation": f"Scenario {results[0]['scenario_number']} offers the best financial return with an NPV of €{results[0]['npv']:,.2f}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario comparison failed: {str(e)}"
        )


@router.get(
    "/financing-templates",
    summary="Get financing option templates",
    description="Returns common financing option templates"
)
async def get_financing_templates(
    current_user: str = Depends(get_current_user)
) -> List[dict]:
    """
    Get common financing option templates.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of financing templates
    """
    templates = [
        {
            "name": "Cash Purchase",
            "type": "cash",
            "description": "Pay full amount upfront",
            "down_payment_percent": 100,
            "interest_rate": 0,
            "term_years": 0
        },
        {
            "name": "Standard Loan (5 years)",
            "type": "loan",
            "description": "5-year loan with 20% down payment",
            "down_payment_percent": 20,
            "interest_rate": 4.5,
            "term_years": 5
        },
        {
            "name": "Standard Loan (10 years)",
            "type": "loan",
            "description": "10-year loan with 20% down payment",
            "down_payment_percent": 20,
            "interest_rate": 5.0,
            "term_years": 10
        },
        {
            "name": "Extended Loan (15 years)",
            "type": "loan",
            "description": "15-year loan with 10% down payment",
            "down_payment_percent": 10,
            "interest_rate": 5.5,
            "term_years": 15
        },
        {
            "name": "Zero Down Loan (10 years)",
            "type": "loan",
            "description": "10-year loan with no down payment",
            "down_payment_percent": 0,
            "interest_rate": 6.0,
            "term_years": 10
        }
    ]
    
    return templates


@router.get(
    "/tax-incentive-templates",
    summary="Get tax incentive templates",
    description="Returns common tax incentive templates for Germany"
)
async def get_tax_incentive_templates(
    current_user: str = Depends(get_current_user)
) -> List[dict]:
    """
    Get common tax incentive templates.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of tax incentive templates
    """
    templates = [
        {
            "name": "KfW Förderung 270",
            "type": "grant",
            "description": "KfW loan program for renewable energy",
            "typical_amount_percent": 10,
            "year_received": 1
        },
        {
            "name": "BAFA Förderung",
            "type": "grant",
            "description": "Federal Office for Economic Affairs grant",
            "typical_amount_percent": 15,
            "year_received": 1
        },
        {
            "name": "Degressive AfA",
            "type": "depreciation",
            "description": "Accelerated depreciation for tax purposes",
            "typical_amount_percent": 20,
            "year_received": 1
        },
        {
            "name": "Regional Subsidy",
            "type": "rebate",
            "description": "State or municipal subsidy programs",
            "typical_amount_percent": 5,
            "year_received": 1
        }
    ]
    
    return templates


@router.post(
    "/export-analysis",
    summary="Export financial analysis",
    description="Exports financial analysis to various formats"
)
async def export_analysis(
    analysis: FinancialAnalysisResponse,
    format: str = "json",
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Export financial analysis to various formats.
    
    Args:
        analysis: Financial analysis to export
        format: Export format (json, csv, pdf)
        current_user: Authenticated user
        
    Returns:
        Exported data or download link
    """
    try:
        if format == "json":
            return analysis.dict()
        elif format == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(["Year", "Energy Production (kWh)", "Savings (EUR)", "Cash Flow (EUR)", "Cumulative (EUR)"])
            
            # Write data
            for cf in analysis.yearly_cash_flows:
                writer.writerow([
                    cf.year,
                    round(cf.energy_production_kwh, 2),
                    round(cf.electricity_savings, 2),
                    round(cf.net_cash_flow, 2),
                    round(cf.cumulative_cash_flow, 2)
                ])
            
            return {
                "format": "csv",
                "data": output.getvalue()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )
