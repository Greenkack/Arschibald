"""VAT Manager

Handles VAT and tax calculations for the enhanced pricing system.
Supports different VAT rates for different product categories and tax exemptions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .dynamic_key_manager import DynamicKeyManager
from .pricing_errors import CalculationError, ValidationError

logger = logging.getLogger(__name__)


class VATCategory(Enum):
    """VAT categories for different product types"""
    STANDARD = "standard"  # 19% in Germany
    REDUCED = "reduced"    # 7% in Germany
    ZERO = "zero"          # 0% for exemptions
    EXEMPT = "exempt"      # Tax exempt


@dataclass
class VATRate:
    """VAT rate configuration"""
    category: VATCategory
    rate_percent: float
    description: str
    country_code: str = "DE"
    effective_date: datetime | None = None

    def __post_init__(self):
        """Validate VAT rate configuration"""
        if self.rate_percent < 0 or self.rate_percent > 100:
            raise ValidationError(
                f"VAT rate must be between 0 and 100, got {
                    self.rate_percent}")

        if self.category == VATCategory.ZERO and self.rate_percent != 0:
            raise ValidationError("Zero VAT category must have 0% rate")

        if self.category == VATCategory.EXEMPT and self.rate_percent != 0:
            raise ValidationError("Exempt VAT category must have 0% rate")


@dataclass
class VATCalculation:
    """Result of VAT calculation"""
    net_amount: float
    vat_rate_percent: float
    vat_amount: float
    gross_amount: float
    vat_category: VATCategory
    breakdown: dict[str, Any] = field(default_factory=dict)
    dynamic_keys: dict[str, Any] = field(default_factory=dict)


@dataclass
class CategoryVATMapping:
    """Maps product categories to VAT rates"""
    product_category: str
    vat_category: VATCategory
    override_rate: float | None = None  # Override default rate for this category
    description: str | None = None


class VATManager:
    """Manages VAT calculations and tax handling"""

    def __init__(self, country_code: str = "DE"):
        """Initialize VAT manager for specific country

        Args:
            country_code: ISO country code (default: DE for Germany)
        """
        self.country_code = country_code.upper()
        self.key_manager = DynamicKeyManager()
        self.logger = logging.getLogger(f"{__name__}.{country_code}")

        # Default VAT rates for Germany
        self.vat_rates = self._initialize_default_vat_rates()

        # Category mappings
        self.category_mappings: dict[str, CategoryVATMapping] = {}
        self._initialize_default_category_mappings()

    def _initialize_default_vat_rates(self) -> dict[VATCategory, VATRate]:
        """Initialize default VAT rates based on country"""
        if self.country_code == "DE":
            return {
                VATCategory.STANDARD: VATRate(
                    category=VATCategory.STANDARD,
                    rate_percent=19.0,
                    description="Standard VAT rate Germany",
                    country_code="DE"
                ),
                VATCategory.REDUCED: VATRate(
                    category=VATCategory.REDUCED,
                    rate_percent=7.0,
                    description="Reduced VAT rate Germany",
                    country_code="DE"
                ),
                VATCategory.ZERO: VATRate(
                    category=VATCategory.ZERO,
                    rate_percent=0.0,
                    description="Zero VAT rate",
                    country_code="DE"
                ),
                VATCategory.EXEMPT: VATRate(
                    category=VATCategory.EXEMPT,
                    rate_percent=0.0,
                    description="VAT exempt",
                    country_code="DE"
                )
            }
        # Default rates for other countries
        return {
            VATCategory.STANDARD: VATRate(
                category=VATCategory.STANDARD,
                rate_percent=20.0,
                description=f"Standard VAT rate {self.country_code}",
                country_code=self.country_code
            ),
            VATCategory.REDUCED: VATRate(
                category=VATCategory.REDUCED,
                rate_percent=10.0,
                description=f"Reduced VAT rate {self.country_code}",
                country_code=self.country_code
            ),
            VATCategory.ZERO: VATRate(
                category=VATCategory.ZERO,
                rate_percent=0.0,
                description="Zero VAT rate",
                country_code=self.country_code
            ),
            VATCategory.EXEMPT: VATRate(
                category=VATCategory.EXEMPT,
                rate_percent=0.0,
                description="VAT exempt",
                country_code=self.country_code
            )
        }

    def _initialize_default_category_mappings(self):
        """Initialize default product category to VAT mappings"""
        # PV system components - standard VAT
        pv_categories = [
            "PV Module", "Inverter", "Battery Storage", "Mounting System",
            "Cables", "Monitoring", "Safety Equipment"
        ]

        for category in pv_categories:
            self.category_mappings[category] = CategoryVATMapping(
                product_category=category,
                vat_category=VATCategory.STANDARD,
                description=f"Standard VAT for {category}"
            )

        # Heat pump components - standard VAT
        hp_categories = [
            "Heat Pump", "Buffer Tank", "Installation", "Controls",
            "Piping", "Electrical"
        ]

        for category in hp_categories:
            self.category_mappings[category] = CategoryVATMapping(
                product_category=category,
                vat_category=VATCategory.STANDARD,
                description=f"Standard VAT for {category}"
            )

        # Services might have different VAT treatment
        service_categories = [
            "Installation Service",
            "Maintenance",
            "Consultation"]

        for category in service_categories:
            self.category_mappings[category] = CategoryVATMapping(
                product_category=category,
                vat_category=VATCategory.STANDARD,
                description=f"Standard VAT for {category}"
            )

    def set_vat_rate(
            self,
            category: VATCategory,
            rate_percent: float,
            description: str = ""):
        """Set VAT rate for a category

        Args:
            category: VAT category
            rate_percent: VAT rate as percentage (0-100)
            description: Optional description
        """
        try:
            vat_rate = VATRate(
                category=category,
                rate_percent=rate_percent,
                description=description or f"Custom rate for {category.value}",
                country_code=self.country_code,
                effective_date=datetime.now()
            )

            self.vat_rates[category] = vat_rate
            self.logger.info(
                f"Set VAT rate for {
                    category.value}: {rate_percent}%")

        except Exception as e:
            self.logger.error(f"Error setting VAT rate: {e}")
            raise

    def set_category_vat_mapping(
            self,
            product_category: str,
            vat_category: VATCategory,
            override_rate: float | None = None):
        """Map product category to VAT category

        Args:
            product_category: Product category name
            vat_category: VAT category to apply
            override_rate: Optional override rate for this specific category
        """
        try:
            if override_rate is not None and (
                    override_rate < 0 or override_rate > 100):
                raise ValidationError(
                    f"Override VAT rate must be between 0 and 100, got {override_rate}")

            self.category_mappings[product_category] = CategoryVATMapping(
                product_category=product_category,
                vat_category=vat_category,
                override_rate=override_rate,
                description=f"Custom mapping for {product_category}"
            )

            self.logger.info(
                f"Mapped category '{product_category}' to VAT category {
                    vat_category.value}")

        except Exception as e:
            self.logger.error(f"Error setting category VAT mapping: {e}")
            raise

    def get_vat_rate_for_category(self, product_category: str) -> float:
        """Get VAT rate for a product category

        Args:
            product_category: Product category name

        Returns:
            VAT rate as percentage
        """
        try:
            # Check if category has specific mapping
            if product_category in self.category_mappings:
                mapping = self.category_mappings[product_category]

                # Use override rate if specified
                if mapping.override_rate is not None:
                    return mapping.override_rate

                # Use rate from VAT category
                if mapping.vat_category in self.vat_rates:
                    return self.vat_rates[mapping.vat_category].rate_percent

            # Default to standard VAT rate
            return self.vat_rates[VATCategory.STANDARD].rate_percent

        except Exception as e:
            self.logger.error(
                f"Error getting VAT rate for category '{product_category}': {e}")
            # Return standard rate as fallback
            return self.vat_rates[VATCategory.STANDARD].rate_percent

    def calculate_vat(
            self,
            net_amount: float,
            product_category: str | None = None,
            vat_rate_override: float | None = None) -> VATCalculation:
        """Calculate VAT for a net amount

        Args:
            net_amount: Net amount before VAT
            product_category: Product category for VAT rate lookup
            vat_rate_override: Override VAT rate (percentage)

        Returns:
            VATCalculation with detailed breakdown
        """
        try:
            if net_amount < 0:
                raise ValidationError(
                    f"Net amount cannot be negative: {net_amount}")

            # Determine VAT rate
            if vat_rate_override is not None:
                if vat_rate_override < 0 or vat_rate_override > 100:
                    raise ValidationError(
                        f"VAT rate override must be between 0 and 100, got {vat_rate_override}")
                vat_rate = vat_rate_override
                vat_category = VATCategory.STANDARD  # Default category for overrides
            elif product_category:
                vat_rate = self.get_vat_rate_for_category(product_category)
                # Get VAT category for this product category
                if product_category in self.category_mappings:
                    vat_category = self.category_mappings[product_category].vat_category
                else:
                    vat_category = VATCategory.STANDARD
            else:
                vat_rate = self.vat_rates[VATCategory.STANDARD].rate_percent
                vat_category = VATCategory.STANDARD

            # Calculate VAT
            vat_amount = net_amount * (vat_rate / 100.0)
            gross_amount = net_amount + vat_amount

            # Generate dynamic keys
            category_key = self.key_manager._create_safe_key_name(
                product_category or "TOTAL")
            dynamic_keys = self.key_manager.generate_keys({
                f"{category_key}_NET_AMOUNT": net_amount,
                f"{category_key}_VAT_RATE": vat_rate,
                f"{category_key}_VAT_AMOUNT": vat_amount,
                f"{category_key}_GROSS_AMOUNT": gross_amount,
                f"{category_key}_VAT_CATEGORY": vat_category.value
            }, prefix="VAT")

            return VATCalculation(
                net_amount=net_amount,
                vat_rate_percent=vat_rate,
                vat_amount=vat_amount,
                gross_amount=gross_amount,
                vat_category=vat_category,
                breakdown={
                    "product_category": product_category,
                    "vat_rate_source": "override" if vat_rate_override else "category_mapping" if product_category else "default",
                    "calculation_timestamp": datetime.now().isoformat()},
                dynamic_keys=dynamic_keys)

        except Exception as e:
            self.logger.error(f"Error calculating VAT: {e}")
            raise CalculationError(f"VAT calculation failed: {e}")

    def calculate_mixed_vat(
            self, items: list[dict[str, Any]]) -> VATCalculation:
        """Calculate VAT for multiple items with different categories

        Args:
            items: List of items with 'net_amount' and 'category' keys

        Returns:
            VATCalculation with combined totals and detailed breakdown
        """
        try:
            if not items:
                return VATCalculation(
                    net_amount=0.0,
                    vat_rate_percent=0.0,
                    vat_amount=0.0,
                    gross_amount=0.0,
                    vat_category=VATCategory.STANDARD,
                    breakdown={"items": []},
                    dynamic_keys={}
                )

            total_net = 0.0
            total_vat = 0.0
            category_breakdowns = {}
            all_dynamic_keys = {}

            for i, item in enumerate(items):
                net_amount = item.get("net_amount", 0.0)
                category = item.get("category", "")

                if net_amount < 0:
                    raise ValidationError(
                        f"Item {i} net amount cannot be negative: {net_amount}")

                # Calculate VAT for this item
                item_vat = self.calculate_vat(net_amount, category)

                # Add to totals
                total_net += item_vat.net_amount
                total_vat += item_vat.vat_amount

                # Track by category
                if category not in category_breakdowns:
                    category_breakdowns[category] = {
                        "net_amount": 0.0,
                        "vat_amount": 0.0,
                        "vat_rate": item_vat.vat_rate_percent,
                        "items": []
                    }

                category_breakdowns[category]["net_amount"] += item_vat.net_amount
                category_breakdowns[category]["vat_amount"] += item_vat.vat_amount
                category_breakdowns[category]["items"].append({
                    "index": i,
                    "net_amount": net_amount,
                    "vat_amount": item_vat.vat_amount
                })

                # Merge dynamic keys
                all_dynamic_keys.update(item_vat.dynamic_keys)

            total_gross = total_net + total_vat

            # Calculate effective VAT rate
            effective_vat_rate = (
                total_vat /
                total_net *
                100.0) if total_net > 0 else 0.0

            # Generate summary keys
            summary_keys = self.key_manager.generate_keys({
                "MIXED_TOTAL_NET": total_net,
                "MIXED_TOTAL_VAT": total_vat,
                "MIXED_TOTAL_GROSS": total_gross,
                "MIXED_EFFECTIVE_VAT_RATE": effective_vat_rate,
                "MIXED_CATEGORY_COUNT": len(category_breakdowns)
            }, prefix="VAT")

            all_dynamic_keys.update(summary_keys)

            return VATCalculation(
                net_amount=total_net,
                vat_rate_percent=effective_vat_rate,
                vat_amount=total_vat,
                gross_amount=total_gross,
                vat_category=VATCategory.STANDARD,  # Mixed categories
                breakdown={
                    "item_count": len(items),
                    "category_breakdowns": category_breakdowns,
                    "calculation_timestamp": datetime.now().isoformat()
                },
                dynamic_keys=all_dynamic_keys
            )

        except Exception as e:
            self.logger.error(f"Error calculating mixed VAT: {e}")
            raise CalculationError(f"Mixed VAT calculation failed: {e}")

    def calculate_net_from_gross(
            self, gross_amount: float, vat_rate_percent: float) -> dict[str, float]:
        """Calculate net amount from gross amount

        Args:
            gross_amount: Gross amount including VAT
            vat_rate_percent: VAT rate as percentage

        Returns:
            Dictionary with net_amount, vat_amount, and gross_amount
        """
        try:
            if gross_amount < 0:
                raise ValidationError(
                    f"Gross amount cannot be negative: {gross_amount}")

            if vat_rate_percent < 0 or vat_rate_percent > 100:
                raise ValidationError(
                    f"VAT rate must be between 0 and 100, got {vat_rate_percent}")

            # Calculate net amount: net = gross / (1 + vat_rate/100)
            vat_multiplier = 1 + (vat_rate_percent / 100.0)
            net_amount = gross_amount / vat_multiplier
            vat_amount = gross_amount - net_amount

            return {
                "net_amount": net_amount,
                "vat_amount": vat_amount,
                "gross_amount": gross_amount,
                "vat_rate_percent": vat_rate_percent
            }

        except Exception as e:
            self.logger.error(f"Error calculating net from gross: {e}")
            raise CalculationError(f"Net from gross calculation failed: {e}")

    def get_vat_summary(self) -> dict[str, Any]:
        """Get summary of VAT configuration

        Returns:
            Dictionary with VAT rates and category mappings
        """
        return {
            "country_code": self.country_code,
            "vat_rates": {
                category.value: {
                    "rate_percent": rate.rate_percent,
                    "description": rate.description,
                    "effective_date": rate.effective_date.isoformat() if rate.effective_date else None
                }
                for category, rate in self.vat_rates.items()
            },
            "category_mappings": {
                category: {
                    "vat_category": mapping.vat_category.value,
                    "override_rate": mapping.override_rate,
                    "description": mapping.description
                }
                for category, mapping in self.category_mappings.items()
            }
        }

    def validate_vat_configuration(self) -> list[str]:
        """Validate VAT configuration and return any issues

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        try:
            # Check that all VAT categories have rates
            for category in VATCategory:
                if category not in self.vat_rates:
                    issues.append(
                        f"Missing VAT rate for category: {
                            category.value}")
                else:
                    rate = self.vat_rates[category]
                    if rate.rate_percent < 0 or rate.rate_percent > 100:
                        issues.append(
                            f"Invalid VAT rate for {
                                category.value}: {
                                rate.rate_percent}%")

            # Check category mappings
            for category, mapping in self.category_mappings.items():
                if mapping.vat_category not in self.vat_rates:
                    issues.append(
                        f"Category '{category}' mapped to undefined VAT category: {
                            mapping.vat_category.value}")

                if mapping.override_rate is not None:
                    if mapping.override_rate < 0 or mapping.override_rate > 100:
                        issues.append(
                            f"Invalid override rate for category '{category}': {
                                mapping.override_rate}%")

        except Exception as e:
            issues.append(f"Validation error: {e}")

        return issues


# Global VAT manager instance
_vat_manager = None


def get_vat_manager(country_code: str = "DE") -> VATManager:
    """Get global VAT manager instance

    Args:
        country_code: ISO country code

    Returns:
        VATManager instance
    """
    global _vat_manager
    if _vat_manager is None or _vat_manager.country_code != country_code.upper():
        _vat_manager = VATManager(country_code)
    return _vat_manager
