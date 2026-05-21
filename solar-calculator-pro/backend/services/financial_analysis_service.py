"""
Solar Financial Analysis Service
Implements comprehensive financial calculations for solar projects
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from datetime import datetime
import numpy_financial as npf

from ..models.financial_schemas import (
    FinancialAnalysisRequest,
    FinancialAnalysisResponse,
    YearlyCashFlow,
    ROIAnalysis,
    NPVAnalysis,
    IRRAnalysis,
    FinancingComparison,
    SensitivityAnalysis,
    FinancingOption,
    FinancingType,
    TaxIncentive
)


class FinancialAnalysisService:
    """Service for solar financial analysis calculations"""
    
    # Constants
    CO2_PER_KWH_KG = 0.401  # kg CO2 per kWh (German grid average)
    CO2_PER_TREE_KG = 21.77  # kg CO2 absorbed by one tree per year
    
    def __init__(self):
        """Initialize the financial analysis service"""
        pass
    
    def calculate_comprehensive_analysis(
        self, 
        request: FinancialAnalysisRequest
    ) -> FinancialAnalysisResponse:
        """
        Calculate comprehensive financial analysis
        
        Args:
            request: Financial analysis request with all parameters
            
        Returns:
            Complete financial analysis response
        """
        # Calculate yearly cash flows
        cash_flows = self._calculate_yearly_cash_flows(request)
        
        # Calculate ROI metrics
        roi_analysis = self._calculate_roi(request, cash_flows)
        
        # Calculate NPV
        npv_analysis = self._calculate_npv(request, cash_flows)
        
        # Calculate IRR
        irr_analysis = self._calculate_irr(request, cash_flows)
        
        # Compare financing options
        financing_comparisons = self._compare_financing_options(request, cash_flows)
        
        # Perform sensitivity analysis
        sensitivity_analyses = self._perform_sensitivity_analysis(request)
        
        # Calculate summary metrics
        total_energy_produced = sum(cf.energy_production_kwh for cf in cash_flows)
        total_energy_savings = sum(cf.electricity_savings for cf in cash_flows)
        total_feed_in_revenue = sum(cf.feed_in_revenue for cf in cash_flows)
        total_maintenance = sum(cf.maintenance_cost for cf in cash_flows)
        total_insurance = sum(cf.insurance_cost for cf in cash_flows)
        net_lifetime_benefit = cash_flows[-1].cumulative_cash_flow
        
        # Calculate environmental impact
        co2_savings = total_energy_produced * self.CO2_PER_KWH_KG
        trees_equivalent = int(co2_savings / self.CO2_PER_TREE_KG)
        
        # Determine investment grade and recommendations
        investment_grade = self._determine_investment_grade(npv_analysis, irr_analysis, roi_analysis)
        key_insights = self._generate_key_insights(
            request, roi_analysis, npv_analysis, irr_analysis, financing_comparisons
        )
        
        # Determine recommended financing
        recommended_financing = None
        if financing_comparisons:
            best_option = min(financing_comparisons, key=lambda x: x.rank)
            recommended_financing = best_option.option_name
        
        return FinancialAnalysisResponse(
            system_size_kwp=request.system_size_kwp,
            total_system_cost=request.total_system_cost,
            analysis_period_years=request.analysis_period_years,
            roi_analysis=roi_analysis,
            npv_analysis=npv_analysis,
            irr_analysis=irr_analysis,
            yearly_cash_flows=cash_flows,
            financing_comparisons=financing_comparisons,
            sensitivity_analyses=sensitivity_analyses,
            total_energy_produced_kwh=total_energy_produced,
            total_energy_savings_eur=total_energy_savings,
            total_feed_in_revenue_eur=total_feed_in_revenue,
            total_maintenance_costs_eur=total_maintenance,
            total_insurance_costs_eur=total_insurance,
            net_lifetime_benefit_eur=net_lifetime_benefit,
            co2_savings_kg=co2_savings,
            trees_equivalent=trees_equivalent,
            recommended_financing=recommended_financing,
            investment_grade=investment_grade,
            key_insights=key_insights
        )
    
    def _calculate_yearly_cash_flows(
        self, 
        request: FinancialAnalysisRequest
    ) -> List[YearlyCashFlow]:
        """Calculate cash flows for each year"""
        cash_flows = []
        cumulative_cash_flow = -request.total_system_cost  # Initial investment
        
        # Get loan payment if financing
        loan_payment = 0.0
        if request.financing_options:
            # Use first financing option for base calculation
            loan_payment = request.financing_options[0].monthly_payment * 12 if request.financing_options[0].monthly_payment else 0
        
        for year in range(1, request.analysis_period_years + 1):
            # Calculate energy production with degradation
            degradation_factor = (1 - request.system_degradation / 100) ** (year - 1)
            energy_production = request.annual_production_kwh * degradation_factor
            
            # Calculate self-consumed and exported energy
            self_consumed = energy_production * (request.self_consumption_rate / 100)
            exported = energy_production - self_consumed
            
            # Calculate electricity price for this year
            electricity_price = request.current_electricity_price * (
                (1 + request.electricity_price_increase / 100) ** (year - 1)
            )
            
            # Calculate revenues
            electricity_savings = self_consumed * electricity_price
            feed_in_revenue = exported * request.feed_in_tariff
            total_revenue = electricity_savings + feed_in_revenue
            
            # Calculate costs
            maintenance_cost = request.maintenance_cost_annual * (
                (1 + request.maintenance_cost_increase / 100) ** (year - 1)
            )
            insurance_cost = request.insurance_cost_annual
            
            # Loan payment (only during loan term)
            loan_term_years = request.financing_options[0].term_years if request.financing_options else 0
            current_loan_payment = loan_payment if year <= loan_term_years else 0
            
            total_costs = maintenance_cost + insurance_cost + current_loan_payment
            
            # Calculate tax benefits
            tax_benefit = self._calculate_tax_benefit(request, year)
            
            # Net cash flow
            net_cash_flow = total_revenue - total_costs + tax_benefit
            cumulative_cash_flow += net_cash_flow
            
            cash_flows.append(YearlyCashFlow(
                year=year,
                energy_production_kwh=energy_production,
                self_consumed_kwh=self_consumed,
                exported_kwh=exported,
                electricity_savings=electricity_savings,
                feed_in_revenue=feed_in_revenue,
                total_revenue=total_revenue,
                maintenance_cost=maintenance_cost,
                insurance_cost=insurance_cost,
                loan_payment=current_loan_payment,
                total_costs=total_costs,
                net_cash_flow=net_cash_flow,
                cumulative_cash_flow=cumulative_cash_flow,
                tax_benefit=tax_benefit
            ))
        
        return cash_flows
    
    def _calculate_roi(
        self, 
        request: FinancialAnalysisRequest,
        cash_flows: List[YearlyCashFlow]
    ) -> ROIAnalysis:
        """Calculate Return on Investment metrics"""
        total_investment = request.total_system_cost
        total_lifetime_savings = cash_flows[-1].cumulative_cash_flow + total_investment
        
        # Simple ROI
        simple_roi_percent = (total_lifetime_savings / total_investment) * 100
        
        # Simple payback period
        simple_payback_years = self._calculate_payback_period(cash_flows, discounted=False)
        
        # Discounted payback period
        discounted_payback_years = self._calculate_payback_period(cash_flows, discounted=True, discount_rate=request.discount_rate)
        
        # Average annual return
        average_annual_return = total_lifetime_savings / request.analysis_period_years
        average_annual_return_percent = (average_annual_return / total_investment) * 100
        
        return ROIAnalysis(
            simple_roi_percent=round(simple_roi_percent, 2),
            simple_payback_years=round(simple_payback_years, 1),
            discounted_payback_years=round(discounted_payback_years, 1) if discounted_payback_years else None,
            total_lifetime_savings=round(total_lifetime_savings, 2),
            average_annual_return=round(average_annual_return, 2),
            average_annual_return_percent=round(average_annual_return_percent, 2)
        )
    
    def _calculate_npv(
        self, 
        request: FinancialAnalysisRequest,
        cash_flows: List[YearlyCashFlow]
    ) -> NPVAnalysis:
        """Calculate Net Present Value"""
        discount_rate = request.discount_rate / 100
        
        # Initial investment (negative cash flow at year 0)
        cash_flow_array = [-request.total_system_cost]
        
        # Add yearly cash flows
        cash_flow_array.extend([cf.net_cash_flow for cf in cash_flows])
        
        # Calculate NPV
        npv = npf.npv(discount_rate, cash_flow_array)
        
        # Calculate present value of benefits and costs
        pv_benefits = sum(
            cf.total_revenue / ((1 + discount_rate) ** cf.year)
            for cf in cash_flows
        )
        
        pv_costs = request.total_system_cost + sum(
            cf.total_costs / ((1 + discount_rate) ** cf.year)
            for cf in cash_flows
        )
        
        # Benefit-cost ratio
        benefit_cost_ratio = pv_benefits / pv_costs if pv_costs > 0 else 0
        
        return NPVAnalysis(
            npv=round(npv, 2),
            npv_positive=npv > 0,
            present_value_benefits=round(pv_benefits, 2),
            present_value_costs=round(pv_costs, 2),
            benefit_cost_ratio=round(benefit_cost_ratio, 2)
        )
    
    def _calculate_irr(
        self, 
        request: FinancialAnalysisRequest,
        cash_flows: List[YearlyCashFlow]
    ) -> IRRAnalysis:
        """Calculate Internal Rate of Return"""
        # Initial investment (negative cash flow at year 0)
        cash_flow_array = [-request.total_system_cost]
        
        # Add yearly cash flows
        cash_flow_array.extend([cf.net_cash_flow for cf in cash_flows])
        
        try:
            # Calculate IRR
            irr = npf.irr(cash_flow_array)
            irr_percent = irr * 100
            
            # Calculate Modified IRR (MIRR)
            finance_rate = request.discount_rate / 100
            reinvest_rate = request.discount_rate / 100
            mirr = npf.mirr(cash_flow_array, finance_rate, reinvest_rate)
            mirr_percent = mirr * 100
            
            irr_exceeds_discount_rate = irr_percent > request.discount_rate
            
            return IRRAnalysis(
                irr_percent=round(irr_percent, 2),
                irr_exceeds_discount_rate=irr_exceeds_discount_rate,
                modified_irr_percent=round(mirr_percent, 2)
            )
        except:
            # If IRR calculation fails, return default values
            return IRRAnalysis(
                irr_percent=0.0,
                irr_exceeds_discount_rate=False,
                modified_irr_percent=None
            )
    
    def _compare_financing_options(
        self, 
        request: FinancialAnalysisRequest,
        base_cash_flows: List[YearlyCashFlow]
    ) -> List[FinancingComparison]:
        """Compare different financing options"""
        if not request.financing_options:
            return []
        
        comparisons = []
        
        for option in request.financing_options:
            # Calculate financing-specific metrics
            monthly_payment = self._calculate_monthly_payment(
                option.loan_amount,
                option.interest_rate,
                option.term_years
            )
            
            total_interest = (monthly_payment * 12 * option.term_years) - option.loan_amount
            total_cost = option.down_payment + option.loan_amount + total_interest
            
            # Recalculate cash flows with this financing option
            modified_request = request.copy()
            modified_request.financing_options = [option]
            financing_cash_flows = self._calculate_yearly_cash_flows(modified_request)
            
            # Calculate NPV and IRR for this option
            npv_analysis = self._calculate_npv(modified_request, financing_cash_flows)
            irr_analysis = self._calculate_irr(modified_request, financing_cash_flows)
            roi_analysis = self._calculate_roi(modified_request, financing_cash_flows)
            
            comparisons.append(FinancingComparison(
                option_name=option.name,
                financing_type=option.type,
                total_cost=round(total_cost, 2),
                monthly_payment=round(monthly_payment, 2),
                total_interest=round(total_interest, 2),
                npv=npv_analysis.npv,
                irr_percent=irr_analysis.irr_percent,
                payback_years=roi_analysis.simple_payback_years,
                lifetime_savings=roi_analysis.total_lifetime_savings,
                rank=0  # Will be set after sorting
            ))
        
        # Rank by NPV (highest NPV = rank 1)
        comparisons.sort(key=lambda x: x.npv, reverse=True)
        for i, comp in enumerate(comparisons, 1):
            comp.rank = i
        
        return comparisons
    
    def _perform_sensitivity_analysis(
        self, 
        request: FinancialAnalysisRequest
    ) -> List[SensitivityAnalysis]:
        """Perform sensitivity analysis on key parameters"""
        analyses = []
        
        # Parameters to analyze
        parameters = [
            ("electricity_price", request.current_electricity_price, 0.20, 0.50),
            ("system_cost", request.total_system_cost, request.total_system_cost * 0.8, request.total_system_cost * 1.2),
            ("self_consumption_rate", request.self_consumption_rate, 20.0, 50.0),
            ("discount_rate", request.discount_rate, 2.0, 8.0),
        ]
        
        for param_name, base_value, low_value, high_value in parameters:
            # Calculate NPV at base value
            base_cash_flows = self._calculate_yearly_cash_flows(request)
            base_npv = self._calculate_npv(request, base_cash_flows).npv
            
            # Calculate NPV at low value
            low_request = request.copy()
            setattr(low_request, param_name, low_value)
            low_cash_flows = self._calculate_yearly_cash_flows(low_request)
            low_npv = self._calculate_npv(low_request, low_cash_flows).npv
            
            # Calculate NPV at high value
            high_request = request.copy()
            setattr(high_request, param_name, high_value)
            high_cash_flows = self._calculate_yearly_cash_flows(high_request)
            high_npv = self._calculate_npv(high_request, high_cash_flows).npv
            
            # Calculate sensitivity
            param_change_percent = ((high_value - low_value) / base_value) * 100
            npv_change_percent = ((high_npv - low_npv) / base_npv) * 100 if base_npv != 0 else 0
            sensitivity = npv_change_percent / param_change_percent if param_change_percent != 0 else 0
            
            analyses.append(SensitivityAnalysis(
                parameter=param_name,
                base_value=round(base_value, 2),
                low_value=round(low_value, 2),
                high_value=round(high_value, 2),
                npv_at_low=round(low_npv, 2),
                npv_at_base=round(base_npv, 2),
                npv_at_high=round(high_npv, 2),
                sensitivity_percent=round(sensitivity, 2)
            ))
        
        return analyses
    
    def _calculate_payback_period(
        self, 
        cash_flows: List[YearlyCashFlow],
        discounted: bool = False,
        discount_rate: float = 0.0
    ) -> float:
        """Calculate payback period (simple or discounted)"""
        cumulative = 0.0
        discount_factor = 1.0
        
        for cf in cash_flows:
            if discounted:
                discount_factor = 1 / ((1 + discount_rate / 100) ** cf.year)
                cumulative += cf.net_cash_flow * discount_factor
            else:
                cumulative += cf.net_cash_flow
            
            if cumulative >= 0:
                # Interpolate to get fractional year
                if cf.year == 1:
                    return cf.year
                
                prev_cf = cash_flows[cf.year - 2]
                prev_cumulative = cumulative - (cf.net_cash_flow * discount_factor if discounted else cf.net_cash_flow)
                
                fraction = abs(prev_cumulative) / abs(cf.net_cash_flow * discount_factor if discounted else cf.net_cash_flow)
                return cf.year - 1 + fraction
        
        # If never positive, return analysis period
        return float(len(cash_flows))
    
    def _calculate_monthly_payment(
        self, 
        loan_amount: float,
        annual_rate: float,
        term_years: int
    ) -> float:
        """Calculate monthly loan payment"""
        if annual_rate == 0:
            return loan_amount / (term_years * 12)
        
        monthly_rate = annual_rate / 100 / 12
        num_payments = term_years * 12
        
        payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / (
            ((1 + monthly_rate) ** num_payments) - 1
        )
        
        return payment
    
    def _calculate_tax_benefit(
        self, 
        request: FinancialAnalysisRequest,
        year: int
    ) -> float:
        """Calculate tax benefits for a given year"""
        total_benefit = 0.0
        
        for incentive in request.tax_incentives:
            if incentive.year_received == year:
                total_benefit += incentive.amount
        
        return total_benefit
    
    def _determine_investment_grade(
        self, 
        npv: NPVAnalysis,
        irr: IRRAnalysis,
        roi: ROIAnalysis
    ) -> str:
        """Determine investment grade based on metrics"""
        score = 0
        
        # NPV criteria
        if npv.npv > 20000:
            score += 3
        elif npv.npv > 10000:
            score += 2
        elif npv.npv > 0:
            score += 1
        
        # IRR criteria
        if irr.irr_percent > 15:
            score += 3
        elif irr.irr_percent > 10:
            score += 2
        elif irr.irr_percent > 5:
            score += 1
        
        # Payback criteria
        if roi.simple_payback_years < 8:
            score += 3
        elif roi.simple_payback_years < 12:
            score += 2
        elif roi.simple_payback_years < 15:
            score += 1
        
        # Determine grade
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair"
        else:
            return "Poor"
    
    def _generate_key_insights(
        self,
        request: FinancialAnalysisRequest,
        roi: ROIAnalysis,
        npv: NPVAnalysis,
        irr: IRRAnalysis,
        financing: List[FinancingComparison]
    ) -> List[str]:
        """Generate key insights and recommendations"""
        insights = []
        
        # NPV insight
        if npv.npv_positive:
            insights.append(
                f"The investment has a positive NPV of €{npv.npv:,.2f}, "
                f"indicating it will create value over {request.analysis_period_years} years."
            )
        else:
            insights.append(
                f"The investment has a negative NPV of €{npv.npv:,.2f}, "
                "suggesting it may not be financially attractive at the current discount rate."
            )
        
        # IRR insight
        if irr.irr_exceeds_discount_rate:
            insights.append(
                f"The IRR of {irr.irr_percent:.1f}% exceeds the discount rate of {request.discount_rate:.1f}%, "
                "indicating a good return on investment."
            )
        else:
            insights.append(
                f"The IRR of {irr.irr_percent:.1f}% is below the discount rate of {request.discount_rate:.1f}%, "
                "suggesting the investment may not meet return expectations."
            )
        
        # Payback insight
        if roi.simple_payback_years < 10:
            insights.append(
                f"The system will pay for itself in approximately {roi.simple_payback_years:.1f} years, "
                "which is considered a good payback period for solar investments."
            )
        elif roi.simple_payback_years < 15:
            insights.append(
                f"The system will pay for itself in approximately {roi.simple_payback_years:.1f} years, "
                "which is a reasonable payback period."
            )
        else:
            insights.append(
                f"The payback period of {roi.simple_payback_years:.1f} years is relatively long. "
                "Consider ways to improve self-consumption or reduce system costs."
            )
        
        # Lifetime savings insight
        insights.append(
            f"Over {request.analysis_period_years} years, the system is projected to save "
            f"€{roi.total_lifetime_savings:,.2f} in electricity costs."
        )
        
        # Financing insight
        if financing:
            best_option = min(financing, key=lambda x: x.rank)
            insights.append(
                f"The recommended financing option is '{best_option.option_name}' "
                f"with an NPV of €{best_option.npv:,.2f} and monthly payments of €{best_option.monthly_payment:,.2f}."
            )
        
        # Self-consumption insight
        if request.self_consumption_rate < 30:
            insights.append(
                "Consider adding battery storage to increase self-consumption rate and improve financial returns."
            )
        elif request.self_consumption_rate > 50:
            insights.append(
                "Your high self-consumption rate maximizes the financial benefits of the solar system."
            )
        
        return insights
