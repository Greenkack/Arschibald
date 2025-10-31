"""Advanced Pricing Formula Implementation

Implements sophisticated pricing calculations with multiple formula modes,
validation, and detailed breakdown capabilities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from financial_calculations import (
    calculate_discount_amount,
    calculate_surcharge_amount,
)

logger = logging.getLogger(__name__)


class FormulaMode(Enum):
    """Different pricing formula calculation modes"""
    STANDARD = "standard"  # (Base + Accessories) × (1 - Disc%) × (1 + Surch%) - Fixed_Disc + Fixed_Surch
    SEQUENTIAL = "sequential"  # Apply modifications in strict sequence
    COMPOUND = "compound"  # Compound percentage calculations
    TIERED = "tiered"  # Tiered discount/surcharge application


@dataclass
class PricingStep:
    """Individual step in pricing calculation"""
    step_number: int
    step_name: str
    input_amount: float
    operation: str
    operation_value: float
    output_amount: float
    description: str
    formula_part: str


@dataclass
class FormulaResult:
    """Result of advanced pricing formula calculation"""
    formula_mode: FormulaMode
    base_price: float
    final_price: float
    total_savings: float
    total_additions: float
    calculation_steps: list[PricingStep] = field(default_factory=list)
    formula_string: str = ""
    validation_passed: bool = True
    validation_messages: list[str] = field(default_factory=list)
    calculation_time_ms: float = 0.0


class AdvancedPricingFormula:
    """Advanced pricing formula calculator with multiple modes"""

    def __init__(self, formula_mode: FormulaMode = FormulaMode.STANDARD):
        """Initialize the advanced pricing formula calculator

        Args:
            formula_mode: The calculation mode to use
        """
        self.formula_mode = formula_mode
        self.logger = logging.getLogger(__name__)

    def calculate_price(
        self,
        base_price: float,
        accessories_cost: float = 0.0,
        percentage_discounts: list[dict[str, Any]] = None,
        percentage_surcharges: list[dict[str, Any]] = None,
        fixed_discounts: list[dict[str, Any]] = None,
        fixed_surcharges: list[dict[str, Any]] = None,
        validation_enabled: bool = True
    ) -> FormulaResult:
        """Calculate final price using the selected formula mode

        Args:
            base_price: Base price before any modifications
            accessories_cost: Total cost of accessories
            percentage_discounts: List of percentage-based discounts
            percentage_surcharges: List of percentage-based surcharges
            fixed_discounts: List of fixed-amount discounts
            fixed_surcharges: List of fixed-amount surcharges
            validation_enabled: Whether to perform validation checks

        Returns:
            FormulaResult with detailed calculation breakdown
        """
        start_time = datetime.now()

        # Initialize defaults
        percentage_discounts = percentage_discounts or []
        percentage_surcharges = percentage_surcharges or []
        fixed_discounts = fixed_discounts or []
        fixed_surcharges = fixed_surcharges or []

        # Validate inputs if enabled
        validation_messages = []
        validation_passed = True

        if validation_enabled:
            validation_result = self._validate_inputs(
                base_price, accessories_cost, percentage_discounts,
                percentage_surcharges, fixed_discounts, fixed_surcharges
            )
            validation_passed = validation_result["is_valid"]
            validation_messages = validation_result["messages"]

        # Calculate based on formula mode
        if self.formula_mode == FormulaMode.STANDARD:
            result = self._calculate_standard_formula(
                base_price, accessories_cost, percentage_discounts,
                percentage_surcharges, fixed_discounts, fixed_surcharges
            )
        elif self.formula_mode == FormulaMode.SEQUENTIAL:
            result = self._calculate_sequential_formula(
                base_price, accessories_cost, percentage_discounts,
                percentage_surcharges, fixed_discounts, fixed_surcharges
            )
        elif self.formula_mode == FormulaMode.COMPOUND:
            result = self._calculate_compound_formula(
                base_price, accessories_cost, percentage_discounts,
                percentage_surcharges, fixed_discounts, fixed_surcharges
            )
        elif self.formula_mode == FormulaMode.TIERED:
            result = self._calculate_tiered_formula(
                base_price, accessories_cost, percentage_discounts,
                percentage_surcharges, fixed_discounts, fixed_surcharges
            )
        else:
            raise ValueError(f"Unsupported formula mode: {self.formula_mode}")

        # Calculate timing
        end_time = datetime.now()
        calculation_time_ms = (end_time - start_time).total_seconds() * 1000

        # Create final result
        final_result = FormulaResult(
            formula_mode=self.formula_mode,
            base_price=base_price,
            final_price=result["final_price"],
            total_savings=result["total_savings"],
            total_additions=result["total_additions"],
            calculation_steps=result["steps"],
            formula_string=result["formula_string"],
            validation_passed=validation_passed,
            validation_messages=validation_messages,
            calculation_time_ms=calculation_time_ms
        )

        return final_result

    def _calculate_standard_formula(
        self, base_price: float, accessories_cost: float,
        percentage_discounts: list[dict], percentage_surcharges: list[dict],
        fixed_discounts: list[dict], fixed_surcharges: list[dict]
    ) -> dict[str, Any]:
        """Calculate using standard formula:
        (Base + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed_Discounts + Fixed_Surcharges
        """
        steps = []
        current_amount = base_price

        # Step 1: Add accessories
        if accessories_cost > 0:
            current_amount += accessories_cost
            steps.append(PricingStep(
                step_number=1,
                step_name="Add Accessories",
                input_amount=base_price,
                operation="ADD",
                operation_value=accessories_cost,
                output_amount=current_amount,
                description=f"Base price + accessories: {base_price} + {accessories_cost}",
                formula_part=f"({base_price} + {accessories_cost})"
            ))

        base_with_accessories = current_amount

        # Step 2: Apply percentage discounts
        total_pct_discount = sum(d.get("value", 0)
                                 for d in percentage_discounts)
        if total_pct_discount > 0:
            discount_amount = calculate_discount_amount(
                current_amount, total_pct_discount)
            new_amount = max(current_amount - discount_amount, 0.0)
            steps.append(
                PricingStep(
                    step_number=len(steps) + 1,
                    step_name="Apply Percentage Discounts",
                    input_amount=current_amount,
                    operation="SUBTRACT",
                    operation_value=discount_amount,
                    output_amount=new_amount,
                    description=f"Apply {total_pct_discount}% discount: {current_amount} - {discount_amount}",
                    formula_part=f"− {total_pct_discount}%"))
            current_amount = new_amount

        # Step 3: Apply percentage surcharges
        total_pct_surcharge = sum(s.get("value", 0)
                                  for s in percentage_surcharges)
        if total_pct_surcharge > 0:
            surcharge_amount = calculate_surcharge_amount(
                current_amount, total_pct_surcharge)
            new_amount = current_amount + surcharge_amount
            steps.append(
                PricingStep(
                    step_number=len(steps) + 1,
                    step_name="Apply Percentage Surcharges",
                    input_amount=current_amount,
                    operation="ADD",
                    operation_value=surcharge_amount,
                    output_amount=new_amount,
                    description=f"Apply {total_pct_surcharge}% surcharge: {current_amount} + {surcharge_amount}",
                    formula_part=f"+ {total_pct_surcharge}%"))
            current_amount = new_amount

        # Step 4: Subtract fixed discounts
        total_fixed_discount = sum(d.get("value", 0) for d in fixed_discounts)
        if total_fixed_discount > 0:
            new_amount = current_amount - total_fixed_discount
            steps.append(
                PricingStep(
                    step_number=len(steps) + 1,
                    step_name="Subtract Fixed Discounts",
                    input_amount=current_amount,
                    operation="SUBTRACT",
                    operation_value=total_fixed_discount,
                    output_amount=new_amount,
                    description=f"Subtract fixed discounts: {current_amount} - {total_fixed_discount}",
                    formula_part=f"- {total_fixed_discount}"))
            current_amount = new_amount

        # Step 5: Add fixed surcharges
        total_fixed_surcharge = sum(s.get("value", 0)
                                    for s in fixed_surcharges)
        if total_fixed_surcharge > 0:
            new_amount = current_amount + total_fixed_surcharge
            steps.append(
                PricingStep(
                    step_number=len(steps) + 1,
                    step_name="Add Fixed Surcharges",
                    input_amount=current_amount,
                    operation="ADD",
                    operation_value=total_fixed_surcharge,
                    output_amount=new_amount,
                    description=f"Add fixed surcharges: {current_amount} + {total_fixed_surcharge}",
                    formula_part=f"+ {total_fixed_surcharge}"))
            current_amount = new_amount

        # Prevent negative final price
        final_price = max(0.0, current_amount)
        if final_price != current_amount:
            steps.append(PricingStep(
                step_number=len(steps) + 1,
                step_name="Prevent Negative Price",
                input_amount=current_amount,
                operation="MAX",
                operation_value=0.0,
                output_amount=final_price,
                description=f"Ensure non-negative: max(0, {current_amount})",
                formula_part="≥ 0"
            ))

        # Calculate totals
        percentage_savings = calculate_discount_amount(
            base_with_accessories, total_pct_discount)
        total_savings = percentage_savings + total_fixed_discount
        total_additions = accessories_cost + calculate_surcharge_amount(
            base_with_accessories - total_savings,
            total_pct_surcharge,
        ) + total_fixed_surcharge

        # Build formula string
        formula_parts = []
        if accessories_cost > 0:
            formula_parts.append(f"({base_price} + {accessories_cost})")
        else:
            formula_parts.append(str(base_price))

        if total_pct_discount > 0:
            formula_parts.append(f"× (1 - {total_pct_discount / 100})")

        if total_pct_surcharge > 0:
            formula_parts.append(f"× (1 + {total_pct_surcharge / 100})")

        if total_fixed_discount > 0:
            formula_parts.append(f"- {total_fixed_discount}")

        if total_fixed_surcharge > 0:
            formula_parts.append(f"+ {total_fixed_surcharge}")

        formula_string = " ".join(formula_parts) + f" = {final_price}"

        return {
            "final_price": final_price,
            "total_savings": total_savings,
            "total_additions": total_additions,
            "steps": steps,
            "formula_string": formula_string
        }

    def _calculate_sequential_formula(self,
                                      base_price: float,
                                      accessories_cost: float,
                                      percentage_discounts: list[dict],
                                      percentage_surcharges: list[dict],
                                      fixed_discounts: list[dict],
                                      fixed_surcharges: list[dict]) -> dict[str,
                                                                            Any]:
        """Calculate using sequential application of each modification"""
        # Implementation for sequential mode
        # For now, use standard formula as base
        return self._calculate_standard_formula(
            base_price, accessories_cost, percentage_discounts,
            percentage_surcharges, fixed_discounts, fixed_surcharges
        )

    def _calculate_compound_formula(self,
                                    base_price: float,
                                    accessories_cost: float,
                                    percentage_discounts: list[dict],
                                    percentage_surcharges: list[dict],
                                    fixed_discounts: list[dict],
                                    fixed_surcharges: list[dict]) -> dict[str,
                                                                          Any]:
        """Calculate using compound percentage calculations"""
        # Implementation for compound mode
        # For now, use standard formula as base
        return self._calculate_standard_formula(
            base_price, accessories_cost, percentage_discounts,
            percentage_surcharges, fixed_discounts, fixed_surcharges
        )

    def _calculate_tiered_formula(self,
                                  base_price: float,
                                  accessories_cost: float,
                                  percentage_discounts: list[dict],
                                  percentage_surcharges: list[dict],
                                  fixed_discounts: list[dict],
                                  fixed_surcharges: list[dict]) -> dict[str,
                                                                        Any]:
        """Calculate using tiered discount/surcharge application"""
        # Implementation for tiered mode
        # For now, use standard formula as base
        return self._calculate_standard_formula(
            base_price, accessories_cost, percentage_discounts,
            percentage_surcharges, fixed_discounts, fixed_surcharges
        )

    def _validate_inputs(
        self, base_price: float, accessories_cost: float,
        percentage_discounts: list[dict], percentage_surcharges: list[dict],
        fixed_discounts: list[dict], fixed_surcharges: list[dict]
    ) -> dict[str, Any]:
        """Validate all inputs for pricing calculation"""
        messages = []
        is_valid = True

        # Validate base price
        if base_price < 0:
            messages.append(f"Base price cannot be negative: {base_price}")
            is_valid = False

        # Validate accessories cost
        if accessories_cost < 0:
            messages.append(
                f"Accessories cost cannot be negative: {accessories_cost}")
            is_valid = False

        # Validate percentage discounts
        total_pct_discount = sum(d.get("value", 0)
                                 for d in percentage_discounts)
        if total_pct_discount > 100:
            messages.append(
                f"Total percentage discounts exceed 100%: {total_pct_discount}%")
            is_valid = False

        # Validate percentage surcharges
        for surcharge in percentage_surcharges:
            if surcharge.get("value", 0) < 0:
                messages.append(
                    f"Surcharge percentage cannot be negative: {surcharge}")
                is_valid = False

        # Validate fixed amounts
        for discount in fixed_discounts:
            if discount.get("value", 0) < 0:
                messages.append(
                    f"Fixed discount cannot be negative: {discount}")
                is_valid = False

        for surcharge in fixed_surcharges:
            if surcharge.get("value", 0) < 0:
                messages.append(
                    f"Fixed surcharge cannot be negative: {surcharge}")
                is_valid = False

        return {
            "is_valid": is_valid,
            "messages": messages
        }

    def get_formula_explanation(self) -> str:
        """Get explanation of the current formula mode"""
        explanations = {
            FormulaMode.STANDARD: (
                "Standard Formula: (Base Price + Accessories) × (1 - Discount%) × "
                "(1 + Surcharge%) - Fixed Discounts + Fixed Surcharges"),
            FormulaMode.SEQUENTIAL: (
                "Sequential Formula: Apply each modification in strict order, "
                "one after another"),
            FormulaMode.COMPOUND: (
                "Compound Formula: Apply percentage modifications with compounding "
                "effects"),
            FormulaMode.TIERED: (
                "Tiered Formula: Apply modifications based on price tiers and "
                "thresholds")}
        return explanations.get(self.formula_mode, "Unknown formula mode")
