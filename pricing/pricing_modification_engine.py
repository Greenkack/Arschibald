"""Pricing Modification Engine

Handles discounts, surcharges, and pricing adjustments with transparent
calculation formulas. Implements the pricing formula:
(Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) -
Fixed Discounts + Fixed Surcharges
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

from .dynamic_key_manager import DynamicKeyManager

logger = logging.getLogger(__name__)


class ModificationType(Enum):
    """Types of pricing modifications"""
    DISCOUNT_PERCENTAGE = "discount_percentage"
    DISCOUNT_FIXED = "discount_fixed"
    SURCHARGE_PERCENTAGE = "surcharge_percentage"
    SURCHARGE_FIXED = "surcharge_fixed"
    ACCESSORY = "accessory"


@dataclass
class DiscountConfig:
    """Configuration for discount application"""
    discount_type: str  # 'percentage', 'fixed', 'tiered'
    discount_value: float
    conditions: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    dynamic_key: str = ""
    applies_to: str = "total"  # 'total', 'category', 'product'
    target_id: int | None = None  # For category or product-specific
    minimum_amount: float = 0.0  # Minimum order amount for discount
    maximum_discount: float | None = None  # Maximum discount amount
    is_active: bool = True
    priority: int = 0  # Higher priority discounts are applied first

    def __post_init__(self):
        """Generate dynamic key if not provided"""
        if not self.dynamic_key and self.description:
            # Create safe key from description
            safe_desc = self.description.upper().replace(" ", "_")
            safe_desc = safe_desc.replace("-", "_")
            safe_desc = "".join(
                c for c in safe_desc if c.isalnum() or c == "_")
            self.dynamic_key = f"DISCOUNT_{safe_desc}"


@dataclass
class SurchargeConfig:
    """Configuration for surcharge application"""
    surcharge_type: str  # 'percentage', 'fixed', 'tiered'
    surcharge_value: float
    conditions: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    dynamic_key: str = ""
    applies_to: str = "total"  # 'total', 'category', 'product'
    target_id: int | None = None  # For category or product-specific
    minimum_amount: float = 0.0  # Minimum order amount for surcharge
    maximum_surcharge: float | None = None  # Maximum surcharge amount
    is_active: bool = True
    priority: int = 0  # Higher priority surcharges are applied first

    def __post_init__(self):
        """Generate dynamic key if not provided"""
        if not self.dynamic_key and self.description:
            # Create safe key from description
            safe_desc = self.description.upper().replace(" ", "_")
            safe_desc = safe_desc.replace("-", "_")
            safe_desc = "".join(
                c for c in safe_desc if c.isalnum() or c == "_")
            self.dynamic_key = f"SURCHARGE_{safe_desc}"


@dataclass
class AccessoryConfig:
    """Configuration for accessory pricing"""
    accessory_id: int
    name: str
    price: float
    quantity: int = 1
    category: str = "accessory"
    description: str = ""
    dynamic_key: str = ""
    is_optional: bool = True
    vat_rate: float | None = None  # Override VAT rate if different

    def __post_init__(self):
        """Generate dynamic key if not provided"""
        if not self.dynamic_key:
            safe_name = self.name.upper().replace(" ", "_").replace("-", "_")
            safe_name = "".join(
                c for c in safe_name if c.isalnum() or c == "_")
            self.dynamic_key = f"ACCESSORY_{safe_name}"


@dataclass
class ModificationApplication:
    """Record of an applied modification"""
    modification_type: ModificationType
    config: DiscountConfig | SurchargeConfig | AccessoryConfig
    applied_amount: float
    base_amount: float  # Amount this modification was calculated on
    calculation_details: dict[str, Any] = field(default_factory=dict)
    applied_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModificationResult:
    """Result of pricing modifications"""
    original_amount: float
    accessories_cost: float
    total_discounts: float
    total_surcharges: float
    final_amount: float
    applied_modifications: list[ModificationApplication] = field(
        default_factory=list
    )
    dynamic_keys: dict[str, Any] = field(default_factory=dict)
    calculation_breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate breakdown after initialization"""
        self.calculation_breakdown = {
            "original_amount": self.original_amount,
            "accessories_cost": self.accessories_cost,
            "amount_with_accessories": self.original_amount +
            self.accessories_cost,
            "total_discounts": self.total_discounts,
            "total_surcharges": self.total_surcharges,
            "final_amount": self.final_amount,
            "net_modification": self.total_surcharges -
            self.total_discounts}


class PricingModificationEngine:
    """Engine for applying discounts, surcharges, and accessories to pricing"""

    def __init__(self):
        """Initialize the pricing modification engine"""
        self.key_manager = DynamicKeyManager()
        self.logger = logging.getLogger(__name__)

        # Storage for configurations
        self.discounts: list[DiscountConfig] = []
        self.surcharges: list[SurchargeConfig] = []
        self.accessories: list[AccessoryConfig] = []

    def add_discount(self, discount_config: DiscountConfig) -> None:
        """Add a discount configuration

        Args:
            discount_config: Discount configuration to add
        """
        try:
            # Validate discount configuration
            if not self._validate_discount_config(discount_config):
                raise ValueError(f"Invalid discount config: {discount_config}")

            # Add to discounts list (sorted by priority)
            self.discounts.append(discount_config)
            self.discounts.sort(key=lambda x: x.priority, reverse=True)

            self.logger.info(f"Added discount: {discount_config.description}")

        except Exception as e:
            self.logger.error(f"Error adding discount: {e}")
            raise

    def add_surcharge(self, surcharge_config: SurchargeConfig) -> None:
        """Add a surcharge configuration

        Args:
            surcharge_config: Surcharge configuration to add
        """
        try:
            # Validate surcharge configuration
            if not self._validate_surcharge_config(surcharge_config):
                raise ValueError(
                    f"Invalid surcharge config: {surcharge_config}")

            # Add to surcharges list (sorted by priority)
            self.surcharges.append(surcharge_config)
            self.surcharges.sort(key=lambda x: x.priority, reverse=True)

            self.logger.info(
                f"Added surcharge: {
                    surcharge_config.description}")

        except Exception as e:
            self.logger.error(f"Error adding surcharge: {e}")
            raise

    def add_accessory(self, accessory_config: AccessoryConfig) -> None:
        """Add an accessory configuration

        Args:
            accessory_config: Accessory configuration to add
        """
        try:
            # Validate accessory configuration
            if not self._validate_accessory_config(accessory_config):
                raise ValueError(
                    f"Invalid accessory config: {accessory_config}")

            self.accessories.append(accessory_config)

            self.logger.info(f"Added accessory: {accessory_config.name}")

        except Exception as e:
            self.logger.error(f"Error adding accessory: {e}")
            raise

    def calculate_modifications(
        self,
        base_price: float,
        selected_accessories: list[int] | None = None,
        context: dict[str, Any] | None = None
    ) -> ModificationResult:
        """Calculate all pricing modifications using the advanced pricing formula

        Advanced Formula Implementation:
        (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%)
        - Fixed Discounts + Fixed Surcharges

        Detailed Steps:
        1. Calculate accessories cost
        2. Add accessories to base price
        3. Apply percentage discounts to (base + accessories)
        4. Apply percentage surcharges to amount after percentage discounts
        5. Subtract fixed discounts
        6. Add fixed surcharges
        7. Ensure final amount ≥ 0

        Args:
            base_price: Base price before modifications
            selected_accessories: List of accessory IDs to include
            context: Additional context for conditional modifications

        Returns:
            ModificationResult with complete calculation breakdown and validation
        """
        try:
            context = context or {}
            selected_accessories = selected_accessories or []

            # Step 1: Calculate accessories cost
            accessories_cost = self._calculate_accessories_cost(
                selected_accessories
            )

            # Step 2: Calculate base amount with accessories
            amount_with_accessories = base_price + accessories_cost

            # Step 3: Apply percentage-based discounts
            percentage_discounts = self._calculate_percentage_discounts(
                amount_with_accessories, context
            )

            # Step 4: Apply percentage-based surcharges to amount after
            # percentage discounts
            amount_after_pct_discounts = (
                amount_with_accessories - percentage_discounts["total_amount"]
            )
            percentage_surcharges = self._calculate_percentage_surcharges(
                amount_after_pct_discounts, context
            )

            # Step 5: Apply fixed discounts and surcharges
            fixed_discounts = self._calculate_fixed_discounts(
                base_price, context
            )
            fixed_surcharges = self._calculate_fixed_surcharges(
                base_price, context
            )

            # Step 6: Calculate final amount
            amount_after_pct_surcharges = (
                amount_after_pct_discounts +
                percentage_surcharges["total_amount"])
            final_amount = (
                amount_after_pct_surcharges
                - fixed_discounts["total_amount"]
                + fixed_surcharges["total_amount"]
            )

            # Ensure final amount is not negative
            final_amount = max(0.0, final_amount)

            # Step 7: Compile all applied modifications
            applied_modifications = []
            applied_modifications.extend(percentage_discounts["applications"])
            applied_modifications.extend(percentage_surcharges["applications"])
            applied_modifications.extend(fixed_discounts["applications"])
            applied_modifications.extend(fixed_surcharges["applications"])

            # Add accessory applications
            for acc_id in selected_accessories:
                accessory = next(
                    (a for a in self.accessories if a.accessory_id == acc_id),
                    None
                )
                if accessory:
                    applied_modifications.append(ModificationApplication(
                        modification_type=ModificationType.ACCESSORY,
                        config=accessory,
                        applied_amount=accessory.price * accessory.quantity,
                        base_amount=base_price,
                        calculation_details={
                            "unit_price": accessory.price,
                            "quantity": accessory.quantity,
                            "total": accessory.price * accessory.quantity
                        }
                    ))

            # Step 8: Generate dynamic keys
            dynamic_keys = self._generate_modification_keys(
                base_price, accessories_cost,
                percentage_discounts["total_amount"] +
                fixed_discounts["total_amount"],
                percentage_surcharges["total_amount"] +
                fixed_surcharges["total_amount"],
                final_amount, applied_modifications
            )

            return ModificationResult(
                original_amount=base_price,
                accessories_cost=accessories_cost,
                total_discounts=(
                    percentage_discounts["total_amount"] +
                    fixed_discounts["total_amount"]
                ),
                total_surcharges=(
                    percentage_surcharges["total_amount"] +
                    fixed_surcharges["total_amount"]
                ),
                final_amount=final_amount,
                applied_modifications=applied_modifications,
                dynamic_keys=dynamic_keys
            )

        except Exception as e:
            self.logger.error(f"Error calculating modifications: {e}")
            raise

    def _calculate_accessories_cost(
            self, selected_accessories: list[int]) -> float:
        """Calculate total cost of selected accessories"""
        total_cost = 0.0

        for acc_id in selected_accessories:
            accessory = next(
                (a for a in self.accessories if a.accessory_id == acc_id),
                None
            )
            if accessory:
                total_cost += accessory.price * accessory.quantity

        return total_cost

    def _calculate_percentage_discounts(
        self, base_amount: float, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate percentage-based discounts"""
        total_discount = 0.0
        applications = []

        for discount in self.discounts:
            if not discount.is_active or discount.discount_type != "percentage":
                continue

            if not self._check_discount_conditions(
                discount, base_amount, context
            ):
                continue

            # Calculate discount amount
            discount_amount = calculate_discount_amount(
                base_amount,
                discount.discount_value,
            )

            # Apply maximum discount limit if set
            if (discount.maximum_discount and
                    discount_amount > discount.maximum_discount):
                discount_amount = discount.maximum_discount

            total_discount += discount_amount

            applications.append(ModificationApplication(
                modification_type=ModificationType.DISCOUNT_PERCENTAGE,
                config=discount,
                applied_amount=discount_amount,
                base_amount=base_amount,
                calculation_details={
                    "percentage": discount.discount_value,
                    "calculated_amount": calculate_discount_amount(
                        base_amount,
                        discount.discount_value,
                    ),
                    "applied_amount": discount_amount,
                    "capped": (
                        discount.maximum_discount and
                        discount_amount == discount.maximum_discount
                    )
                }
            ))

        return {"total_amount": total_discount, "applications": applications}

    def _calculate_percentage_surcharges(
        self, base_amount: float, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate percentage-based surcharges"""
        total_surcharge = 0.0
        applications = []

        for surcharge in self.surcharges:
            if not surcharge.is_active or surcharge.surcharge_type != "percentage":
                continue

            if not self._check_surcharge_conditions(
                surcharge, base_amount, context
            ):
                continue

            # Calculate surcharge amount
            surcharge_amount = calculate_surcharge_amount(
                base_amount,
                surcharge.surcharge_value,
            )

            # Apply maximum surcharge limit if set
            if (surcharge.maximum_surcharge and
                    surcharge_amount > surcharge.maximum_surcharge):
                surcharge_amount = surcharge.maximum_surcharge

            total_surcharge += surcharge_amount

            applications.append(ModificationApplication(
                modification_type=ModificationType.SURCHARGE_PERCENTAGE,
                config=surcharge,
                applied_amount=surcharge_amount,
                base_amount=base_amount,
                calculation_details={
                    "percentage": surcharge.surcharge_value,
                    "calculated_amount": calculate_surcharge_amount(
                        base_amount,
                        surcharge.surcharge_value,
                    ),
                    "applied_amount": surcharge_amount,
                    "capped": (
                        surcharge.maximum_surcharge and
                        surcharge_amount == surcharge.maximum_surcharge
                    )
                }
            ))

        return {"total_amount": total_surcharge, "applications": applications}

    def _calculate_fixed_discounts(
        self, base_amount: float, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate fixed-amount discounts"""
        total_discount = 0.0
        applications = []

        for discount in self.discounts:
            if not discount.is_active or discount.discount_type != "fixed":
                continue

            if not self._check_discount_conditions(
                discount, base_amount, context
            ):
                continue

            discount_amount = discount.discount_value
            total_discount += discount_amount

            applications.append(ModificationApplication(
                modification_type=ModificationType.DISCOUNT_FIXED,
                config=discount,
                applied_amount=discount_amount,
                base_amount=base_amount,
                calculation_details={
                    "fixed_amount": discount_amount
                }
            ))

        return {"total_amount": total_discount, "applications": applications}

    def _calculate_fixed_surcharges(
        self, base_amount: float, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate fixed-amount surcharges"""
        total_surcharge = 0.0
        applications = []

        for surcharge in self.surcharges:
            if not surcharge.is_active or surcharge.surcharge_type != "fixed":
                continue

            if not self._check_surcharge_conditions(
                surcharge, base_amount, context
            ):
                continue

            surcharge_amount = surcharge.surcharge_value
            total_surcharge += surcharge_amount

            applications.append(ModificationApplication(
                modification_type=ModificationType.SURCHARGE_FIXED,
                config=surcharge,
                applied_amount=surcharge_amount,
                base_amount=base_amount,
                calculation_details={
                    "fixed_amount": surcharge_amount
                }
            ))

        return {"total_amount": total_surcharge, "applications": applications}

    def _check_discount_conditions(
        self, discount: DiscountConfig, base_amount: float,
        context: dict[str, Any]
    ) -> bool:
        """Check if discount conditions are met"""
        # Check minimum amount
        if base_amount < discount.minimum_amount:
            return False

        # Check custom conditions
        for condition_key, condition_value in discount.conditions.items():
            if condition_key not in context:
                return False

            context_value = context[condition_key]

            # Simple equality check for now - can be extended for complex
            # conditions
            if context_value != condition_value:
                return False

        return True

    def _check_surcharge_conditions(
        self, surcharge: SurchargeConfig, base_amount: float,
        context: dict[str, Any]
    ) -> bool:
        """Check if surcharge conditions are met"""
        # Check minimum amount
        if base_amount < surcharge.minimum_amount:
            return False

        # Check custom conditions
        for condition_key, condition_value in surcharge.conditions.items():
            if condition_key not in context:
                return False

            context_value = context[condition_key]

            # Simple equality check for now - can be extended for complex
            # conditions
            if context_value != condition_value:
                return False

        return True

    def _generate_modification_keys(
        self, base_price: float, accessories_cost: float,
        total_discounts: float, total_surcharges: float,
        final_amount: float,
        applied_modifications: list[ModificationApplication]
    ) -> dict[str, Any]:
        """Generate dynamic keys for all modifications"""
        keys = {}

        # Base keys
        base_keys = self.key_manager.generate_keys({
            "BASE_PRICE": base_price,
            "ACCESSORIES_COST": accessories_cost,
            "PRICE_WITH_ACCESSORIES": base_price + accessories_cost,
            "TOTAL_DISCOUNTS": total_discounts,
            "TOTAL_SURCHARGES": total_surcharges,
            "NET_MODIFICATION": total_surcharges - total_discounts,
            "FINAL_AMOUNT": final_amount
        }, prefix="PRICING_")

        keys.update(base_keys)

        # Individual modification keys
        for modification in applied_modifications:
            config = modification.config
            if hasattr(config, 'dynamic_key') and config.dynamic_key:
                keys[config.dynamic_key] = modification.applied_amount

                # Add detailed keys for percentage modifications
                if modification.modification_type in [
                    ModificationType.DISCOUNT_PERCENTAGE,
                    ModificationType.SURCHARGE_PERCENTAGE
                ]:
                    details = modification.calculation_details
                    keys[f"{config.dynamic_key}_PERCENTAGE"] = details.get(
                        "percentage", 0
                    )
                    keys[f"{config.dynamic_key}_BASE_AMOUNT"] = (
                        modification.base_amount
                    )

        return keys

    def calculate_detailed_breakdown(
        self,
        base_price: float,
        selected_accessories: list[int] | None = None,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Calculate detailed pricing breakdown for transparency

        Returns step-by-step calculation details for audit and display purposes.

        Args:
            base_price: Base price before modifications
            selected_accessories: List of accessory IDs to include
            context: Additional context for conditional modifications

        Returns:
            Detailed breakdown dictionary with all calculation steps
        """
        context = context or {}
        selected_accessories = selected_accessories or []

        breakdown = {
            "step_1_base_price": base_price,
            "step_2_accessories": {},
            "step_3_base_with_accessories": 0.0,
            "step_4_percentage_discounts": {},
            "step_5_after_pct_discounts": 0.0,
            "step_6_percentage_surcharges": {},
            "step_7_after_pct_surcharges": 0.0,
            "step_8_fixed_discounts": {},
            "step_9_fixed_surcharges": {},
            "step_10_final_amount": 0.0,
            "validation_checks": {},
            "formula_verification": ""
        }

        # Step 1: Base price (already set)

        # Step 2: Calculate accessories
        accessories_cost = 0.0
        accessories_details = []
        for acc_id in selected_accessories:
            accessory = next(
                (a for a in self.accessories if a.accessory_id == acc_id),
                None
            )
            if accessory:
                acc_total = accessory.price * accessory.quantity
                accessories_cost += acc_total
                accessories_details.append({
                    "id": acc_id,
                    "name": accessory.name,
                    "unit_price": accessory.price,
                    "quantity": accessory.quantity,
                    "total": acc_total
                })

        breakdown["step_2_accessories"] = {
            "total_cost": accessories_cost,
            "details": accessories_details
        }

        # Step 3: Base with accessories
        base_with_accessories = base_price + accessories_cost
        breakdown["step_3_base_with_accessories"] = base_with_accessories

        # Step 4: Percentage discounts
        pct_discounts = self._calculate_percentage_discounts(
            base_with_accessories, context
        )
        breakdown["step_4_percentage_discounts"] = {
            "total_amount": pct_discounts["total_amount"],
            "details": [
                {
                    "description": app.config.description,
                    "percentage": app.calculation_details.get("percentage", 0),
                    "base_amount": app.base_amount,
                    "discount_amount": app.applied_amount
                }
                for app in pct_discounts["applications"]
            ]
        }

        # Step 5: After percentage discounts
        after_pct_discounts = base_with_accessories - \
            pct_discounts["total_amount"]
        breakdown["step_5_after_pct_discounts"] = after_pct_discounts

        # Step 6: Percentage surcharges
        pct_surcharges = self._calculate_percentage_surcharges(
            after_pct_discounts, context
        )
        breakdown["step_6_percentage_surcharges"] = {
            "total_amount": pct_surcharges["total_amount"],
            "details": [
                {
                    "description": app.config.description,
                    "percentage": app.calculation_details.get("percentage", 0),
                    "base_amount": app.base_amount,
                    "surcharge_amount": app.applied_amount
                }
                for app in pct_surcharges["applications"]
            ]
        }

        # Step 7: After percentage surcharges
        after_pct_surcharges = after_pct_discounts + \
            pct_surcharges["total_amount"]
        breakdown["step_7_after_pct_surcharges"] = after_pct_surcharges

        # Step 8: Fixed discounts
        fixed_discounts = self._calculate_fixed_discounts(base_price, context)
        breakdown["step_8_fixed_discounts"] = {
            "total_amount": fixed_discounts["total_amount"],
            "details": [
                {
                    "description": app.config.description,
                    "discount_amount": app.applied_amount
                }
                for app in fixed_discounts["applications"]
            ]
        }

        # Step 9: Fixed surcharges
        fixed_surcharges = self._calculate_fixed_surcharges(
            base_price, context)
        breakdown["step_9_fixed_surcharges"] = {
            "total_amount": fixed_surcharges["total_amount"],
            "details": [
                {
                    "description": app.config.description,
                    "surcharge_amount": app.applied_amount
                }
                for app in fixed_surcharges["applications"]
            ]
        }

        # Step 10: Final amount
        final_amount = (
            after_pct_surcharges
            - fixed_discounts["total_amount"]
            + fixed_surcharges["total_amount"]
        )

        # Validation: Prevent negative final amount
        original_final = final_amount
        final_amount = max(0.0, final_amount)

        breakdown["step_10_final_amount"] = final_amount

        # Validation checks
        breakdown["validation_checks"] = {
            "original_final_amount": original_final,
            "prevented_negative": original_final < 0,
            "final_amount_valid": final_amount >= 0,
            "total_discount_percentage": (
                (pct_discounts["total_amount"] / base_with_accessories * 100)
                if base_with_accessories > 0 else 0
            ),
            "total_surcharge_percentage": (
                (pct_surcharges["total_amount"] / after_pct_discounts * 100)
                if after_pct_discounts > 0 else 0
            )
        }

        # Formula verification string
        breakdown["formula_verification"] = (
            f"({base_price} + {accessories_cost}) × "
            f"(1 - {pct_discounts['total_amount']}/{base_with_accessories}) × "
            f"(1 + {pct_surcharges['total_amount']}/{after_pct_discounts}) "
            f"- {fixed_discounts['total_amount']} + {fixed_surcharges['total_amount']} "
            f"= {final_amount}"
        )

        return breakdown

    def validate_pricing_inputs(
        self,
        base_price: float,
        selected_accessories: list[int] | None = None
    ) -> dict[str, Any]:
        """Validate pricing calculation inputs

        Args:
            base_price: Base price to validate
            selected_accessories: Accessory IDs to validate

        Returns:
            Validation result with errors and warnings
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }

        # Validate base price
        if base_price < 0:
            validation_result["errors"].append(
                f"Base price cannot be negative: {base_price}"
            )
            validation_result["is_valid"] = False
        elif base_price == 0:
            validation_result["warnings"].append(
                "Base price is zero - this may result in unexpected calculations"
            )

        # Validate accessories
        selected_accessories = selected_accessories or []
        for acc_id in selected_accessories:
            accessory = next(
                (a for a in self.accessories if a.accessory_id == acc_id),
                None
            )
            if not accessory:
                validation_result["errors"].append(
                    f"Accessory with ID {acc_id} not found"
                )
                validation_result["is_valid"] = False

        # Check for excessive discounts
        total_pct_discount = sum(
            d.discount_value for d in self.discounts
            if d.is_active and d.discount_type == "percentage"
        )
        if total_pct_discount > 50:
            validation_result["warnings"].append(
                f"Total percentage discounts exceed 50%: {total_pct_discount}%"
            )

        # Check for conflicting modifications
        if len(self.discounts) > 5:
            validation_result["recommendations"].append(
                "Consider consolidating multiple discounts for clarity"
            )

        return validation_result

    def _validate_discount_config(self, config: DiscountConfig) -> bool:
        """Validate discount configuration"""
        if config.discount_type not in ["percentage", "fixed", "tiered"]:
            self.logger.error(f"Invalid discount type: {config.discount_type}")
            return False

        if config.discount_value < 0:
            self.logger.error(
                f"Discount value cannot be negative: {config.discount_value}"
            )
            return False

        if (config.discount_type == "percentage" and
                config.discount_value > 100):
            self.logger.warning(
                f"Discount percentage > 100%: {config.discount_value}"
            )

        return True

    def _validate_surcharge_config(self, config: SurchargeConfig) -> bool:
        """Validate surcharge configuration"""
        if config.surcharge_type not in ["percentage", "fixed", "tiered"]:
            self.logger.error(
                f"Invalid surcharge type: {
                    config.surcharge_type}")
            return False

        if config.surcharge_value < 0:
            self.logger.error(
                f"Surcharge value cannot be negative: {config.surcharge_value}"
            )
            return False

        return True

    def _validate_accessory_config(self, config: AccessoryConfig) -> bool:
        """Validate accessory configuration"""
        if config.price < 0:
            self.logger.error(
                f"Accessory price cannot be negative: {config.price}"
            )
            return False

        if config.quantity <= 0:
            self.logger.error(
                f"Accessory quantity must be positive: {config.quantity}"
            )
            return False

        return True

    def clear_discounts(self) -> None:
        """Clear all discount configurations"""
        self.discounts.clear()
        self.logger.info("Cleared all discounts")

    def clear_surcharges(self) -> None:
        """Clear all surcharge configurations"""
        self.surcharges.clear()
        self.logger.info("Cleared all surcharges")

    def clear_accessories(self) -> None:
        """Clear all accessory configurations"""
        self.accessories.clear()
        self.logger.info("Cleared all accessories")

    def get_active_discounts(self) -> list[DiscountConfig]:
        """Get list of active discount configurations"""
        return [d for d in self.discounts if d.is_active]

    def get_active_surcharges(self) -> list[SurchargeConfig]:
        """Get list of active surcharge configurations"""
        return [s for s in self.surcharges if s.is_active]

    def get_available_accessories(self) -> list[AccessoryConfig]:
        """Get list of available accessory configurations"""
        return self.accessories.copy()
