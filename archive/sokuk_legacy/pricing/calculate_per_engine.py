"""Calculate Per Calculation Engine

Comprehensive calculation method handler for different pricing calculation methods.
Supports "per piece" (Stück), "per meter" (Meter), "lump sum" (pauschal),
"per kWp" pricing, and integration with product features.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .pricing_errors import (
    CalculationError,
    ValidationError,
    safe_pricing_operation,
)
from .pricing_validation import get_pricing_validator

logger = logging.getLogger(__name__)


class CalculationMethod(Enum):
    """Supported calculation methods"""
    PER_PIECE = "Stück"
    PER_METER = "Meter"
    LUMP_SUM = "pauschal"
    PER_KWP = "kWp"
    PER_SQUARE_METER = "m²"
    PER_HOUR = "Stunde"

    @classmethod
    def from_string(cls, value: str) -> CalculationMethod:
        """Convert string to CalculationMethod enum"""
        if not value:
            return cls.PER_PIECE

        value_lower = value.lower().strip()

        # Map various string representations to enum values
        mapping = {
            "stück": cls.PER_PIECE,
            "piece": cls.PER_PIECE,
            "unit": cls.PER_PIECE,
            "pcs": cls.PER_PIECE,
            "meter": cls.PER_METER,
            "m": cls.PER_METER,
            "metre": cls.PER_METER,
            "pauschal": cls.LUMP_SUM,
            "lump_sum": cls.LUMP_SUM,
            "flat": cls.LUMP_SUM,
            "fixed": cls.LUMP_SUM,
            "kwp": cls.PER_KWP,
            "kw_peak": cls.PER_KWP,
            "kilowatt_peak": cls.PER_KWP,
            "m²": cls.PER_SQUARE_METER,
            "sqm": cls.PER_SQUARE_METER,
            "square_meter": cls.PER_SQUARE_METER,
            "stunde": cls.PER_HOUR,
            "hour": cls.PER_HOUR,
            "hr": cls.PER_HOUR
        }

        return mapping.get(value_lower, cls.PER_PIECE)


@dataclass
class CalculationContext:
    """Context information for price calculations"""
    # Product specifications
    capacity_w: float | None = None
    power_kw: float | None = None
    efficiency_percent: float | None = None
    length_m: float | None = None
    width_m: float | None = None
    area_m2: float | None = None

    # Technology and feature specifications
    technology: str | None = None
    feature: str | None = None
    design: str | None = None
    upgrade: str | None = None

    # System context
    system_capacity_kwp: float | None = None
    installation_area_m2: float | None = None
    labor_hours: float | None = None

    # Additional context
    category: str | None = None
    brand: str | None = None

    def __post_init__(self):
        """Calculate derived fields"""
        # Calculate area from dimensions if not provided
        if not self.area_m2 and self.length_m and self.width_m:
            self.area_m2 = self.length_m * self.width_m

        # Calculate system capacity from power if not provided
        if not self.system_capacity_kwp and self.power_kw:
            self.system_capacity_kwp = self.power_kw
        elif not self.system_capacity_kwp and self.capacity_w:
            self.system_capacity_kwp = self.capacity_w / 1000.0


@dataclass
class CalculationResult:
    """Result of a calculate_per calculation"""
    base_price: float
    quantity: float
    calculation_method: CalculationMethod
    unit_price: float
    total_price: float

    # Calculation details
    calculation_factor: float = 1.0
    adjusted_quantity: float = field(init=False)
    price_adjustments: dict[str, float] = field(default_factory=dict)

    # Metadata
    context_used: CalculationContext | None = None
    validation_warnings: list[str] = field(default_factory=list)
    calculation_notes: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate derived fields"""
        self.adjusted_quantity = self.quantity * self.calculation_factor


class CalculatePerEngine:
    """Engine for handling different calculation methods with product feature integration"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CalculatePerEngine")
        self.validator = get_pricing_validator()

    @safe_pricing_operation("calculate_price", "calculate_per_engine")
    def calculate_price(
            self,
            base_price: float,
            quantity: float,
            calculate_per: str,
            context: CalculationContext | None = None) -> CalculationResult:
        """
        Calculate total price based on calculation method and context.

        Args:
            base_price: Base unit price
            quantity: Quantity to calculate for
            calculate_per: Calculation method string
            context: Additional context for calculations

        Returns:
            CalculationResult with detailed calculation information
        """
        try:
            # Validate inputs
            self._validate_calculation_inputs(
                base_price, quantity, calculate_per)

            # Convert calculation method and check if it was unknown
            original_method = calculate_per.lower().strip()
            method = CalculationMethod.from_string(calculate_per)
            is_unknown_method = (
                method == CalculationMethod.PER_PIECE and original_method not in [
                    "stück", "piece", "unit", "pcs", ""])

            # Initialize context if not provided
            if context is None:
                context = CalculationContext()

            # Perform calculation based on method
            if method == CalculationMethod.PER_PIECE:
                result = self._calculate_per_piece(
                    base_price, quantity, context)
                if is_unknown_method:
                    result.validation_warnings.append(
                        f"Unknown method '{calculate_per}', used per piece instead")
                    self.logger.warning(
                        f"Unknown calculation method '{calculate_per}', falling back to per piece")
            elif method == CalculationMethod.PER_METER:
                result = self._calculate_per_meter(
                    base_price, quantity, context)
            elif method == CalculationMethod.LUMP_SUM:
                result = self._calculate_lump_sum(
                    base_price, quantity, context)
            elif method == CalculationMethod.PER_KWP:
                result = self._calculate_per_kwp(base_price, quantity, context)
            elif method == CalculationMethod.PER_SQUARE_METER:
                result = self._calculate_per_square_meter(
                    base_price, quantity, context)
            elif method == CalculationMethod.PER_HOUR:
                result = self._calculate_per_hour(
                    base_price, quantity, context)
            else:
                # This should not happen with current implementation, but keep
                # as safety
                self.logger.warning(
                    f"Unexpected calculation method '{calculate_per}', falling back to per piece")
                result = self._calculate_per_piece(
                    base_price, quantity, context)
                result.validation_warnings.append(
                    f"Unexpected method '{calculate_per}', used per piece instead")

            # Apply feature-based adjustments
            result = self._apply_feature_adjustments(result, context)

            # Validate result
            self._validate_calculation_result(result)

            return result

        except Exception as e:
            self.logger.error(f"Error in calculate_price: {e}")
            raise CalculationError(
                f"Failed to calculate price using method '{calculate_per}': {
                    str(e)}",
                context={
                    "base_price": base_price,
                    "quantity": quantity,
                    "calculate_per": calculate_per,
                    "context": context.__dict__ if context else None})

    def _calculate_per_piece(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for per piece method"""
        unit_price = base_price
        total_price = unit_price * quantity

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.PER_PIECE,
            unit_price=unit_price,
            total_price=total_price,
            context_used=context
        )

        result.calculation_notes.append(
            f"Per piece calculation: {quantity} × {
                unit_price:.2f} = {
                total_price:.2f}")

        return result

    def _calculate_per_meter(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for per meter method (cables, mounting systems)"""
        unit_price = base_price
        total_price = unit_price * quantity

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.PER_METER,
            unit_price=unit_price,
            total_price=total_price,
            context_used=context
        )

        result.calculation_notes.append(
            f"Per meter calculation: {quantity}m × {unit_price:.2f}/m = {total_price:.2f}")

        # Add validation for reasonable cable lengths
        if quantity > 1000:
            result.validation_warnings.append(
                f"Very long cable length: {quantity}m - please verify")

        return result

    def _calculate_lump_sum(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for lump sum method (services, packages)"""
        unit_price = base_price
        total_price = base_price  # Ignore quantity for lump sum

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.LUMP_SUM,
            unit_price=unit_price,
            total_price=total_price,
            calculation_factor=0.0,  # Quantity doesn't affect price
            context_used=context
        )

        result.calculation_notes.append(
            f"Lump sum calculation: {
                base_price:.2f} (quantity {quantity} ignored)")

        if quantity != 1:
            result.validation_warnings.append(
                f"Lump sum pricing ignores quantity ({quantity})")

        return result

    def _calculate_per_kwp(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for per kWp method (system-dependent components)"""
        # Determine kWp capacity from context
        kwp_capacity = self._determine_kwp_capacity(context, quantity)

        if kwp_capacity is None or kwp_capacity <= 0:
            # Fallback to per piece if no capacity information
            result = self._calculate_per_piece(base_price, quantity, context)
            result.validation_warnings.append(
                "No kWp capacity found, used per piece calculation")
            return result

        unit_price = base_price
        total_price = unit_price * kwp_capacity

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.PER_KWP,
            unit_price=unit_price,
            total_price=total_price,
            calculation_factor=kwp_capacity /
            quantity if quantity > 0 else 1.0,
            context_used=context)

        result.calculation_notes.append(
            f"Per kWp calculation: {
                kwp_capacity:.2f}kWp × {
                unit_price:.2f}/kWp = {
                total_price:.2f}")

        return result

    def _calculate_per_square_meter(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for per square meter method"""
        # Use area from context or calculate from dimensions
        area_m2 = context.area_m2 or context.installation_area_m2

        if area_m2 is None or area_m2 <= 0:
            # Fallback to quantity as area
            area_m2 = quantity
            result_notes = f"Per m² calculation using quantity as area: {area_m2}m²"
        else:
            result_notes = f"Per m² calculation using context area: {area_m2}m²"

        unit_price = base_price
        total_price = unit_price * area_m2

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.PER_SQUARE_METER,
            unit_price=unit_price,
            total_price=total_price,
            calculation_factor=area_m2 / quantity if quantity > 0 else 1.0,
            context_used=context
        )

        result.calculation_notes.append(
            f"{result_notes} × {unit_price:.2f}/m² = {total_price:.2f}")

        return result

    def _calculate_per_hour(
            self,
            base_price: float,
            quantity: float,
            context: CalculationContext) -> CalculationResult:
        """Calculate pricing for per hour method (labor, services)"""
        # Use labor hours from context or quantity as hours
        hours = context.labor_hours if context.labor_hours is not None else quantity

        unit_price = base_price
        total_price = unit_price * hours

        result = CalculationResult(
            base_price=base_price,
            quantity=quantity,
            calculation_method=CalculationMethod.PER_HOUR,
            unit_price=unit_price,
            total_price=total_price,
            calculation_factor=hours / quantity if quantity > 0 else 1.0,
            context_used=context
        )

        result.calculation_notes.append(
            f"Per hour calculation: {hours}h × {unit_price:.2f}/h = {total_price:.2f}")

        return result

    def _determine_kwp_capacity(
            self,
            context: CalculationContext,
            quantity: float) -> float | None:
        """Determine kWp capacity from context and quantity"""
        # Priority order for determining kWp capacity:
        # 1. Individual component capacity × quantity (for modules)
        # 2. System capacity from context (for system-level components)
        # 3. Power rating × quantity (for inverters)

        if context.capacity_w is not None and context.capacity_w > 0:
            return (context.capacity_w / 1000.0) * quantity

        if context.system_capacity_kwp is not None and context.system_capacity_kwp > 0:
            return context.system_capacity_kwp

        if context.power_kw is not None and context.power_kw > 0:
            return context.power_kw * quantity

        return None

    def _apply_feature_adjustments(
            self,
            result: CalculationResult,
            context: CalculationContext) -> CalculationResult:
        """Apply feature-based pricing adjustments"""
        adjustments = {}

        # Technology-based adjustments
        if context.technology:
            tech_adjustment = self._get_technology_adjustment(
                context.technology, context.category)
            if tech_adjustment != 0:
                adjustments[f"technology_{context.technology}"] = tech_adjustment

        # Feature-based adjustments
        if context.feature:
            feature_adjustment = self._get_feature_adjustment(
                context.feature, context.category)
            if feature_adjustment != 0:
                adjustments[f"feature_{context.feature}"] = feature_adjustment

        # Design-based adjustments
        if context.design:
            design_adjustment = self._get_design_adjustment(
                context.design, context.category)
            if design_adjustment != 0:
                adjustments[f"design_{context.design}"] = design_adjustment

        # Upgrade-based adjustments
        if context.upgrade:
            upgrade_adjustment = self._get_upgrade_adjustment(
                context.upgrade, context.category)
            if upgrade_adjustment != 0:
                adjustments[f"upgrade_{context.upgrade}"] = upgrade_adjustment

        # Efficiency-based adjustments
        if context.efficiency_percent:
            efficiency_adjustment = self._get_efficiency_adjustment(
                context.efficiency_percent, context.category)
            if efficiency_adjustment != 0:
                adjustments[f"efficiency_{context.efficiency_percent}%"] = efficiency_adjustment

        # Apply adjustments to result
        if adjustments:
            # For per-piece calculations, multiply adjustments by quantity
            if result.calculation_method == CalculationMethod.PER_PIECE:
                total_adjustment = sum(adjustments.values()) * result.quantity
            else:
                total_adjustment = sum(adjustments.values())

            result.total_price += total_adjustment
            result.price_adjustments = adjustments

            adjustment_notes = [
                f"{key}: {
                    value:+.2f}" for key,
                value in adjustments.items()]
            result.calculation_notes.append(
                f"Feature adjustments: {
                    ', '.join(adjustment_notes)}")

        return result

    def _get_technology_adjustment(
            self,
            technology: str,
            category: str | None) -> float:
        """Get pricing adjustment based on technology"""
        if not technology or not category:
            return 0.0

        # Technology adjustment rules (can be made configurable)
        tech_adjustments = {
            "Modul": {
                "Monokristallin": 0.0,  # Base technology
                "Polykristallin": -10.0,  # Cheaper technology
                "Dünnschicht": -20.0,  # Cheapest technology
                "HJT": 50.0,  # Premium technology
                "TOPCon": 30.0,  # Advanced technology
                "PERC": 10.0,  # Standard advanced technology
            },
            "Wechselrichter": {
                "String": 0.0,  # Base technology
                "Zentral": 100.0,  # More expensive
                "Mikro": -50.0,  # Cheaper per unit
                "Leistungsoptimierer": 25.0,  # Premium feature
            },
            "Batteriespeicher": {
                "Lithium-Ion": 0.0,  # Base technology
                "LiFePO4": 200.0,  # Premium technology
                "Blei-Säure": -500.0,  # Older, cheaper technology
            }
        }

        category_adjustments = tech_adjustments.get(category, {})
        return category_adjustments.get(technology, 0.0)

    def _get_feature_adjustment(
            self,
            feature: str,
            category: str | None) -> float:
        """Get pricing adjustment based on features"""
        if not feature or not category:
            return 0.0

        # Feature adjustment rules
        feature_adjustments = {
            "Modul": {
                "Bifazial": 50.0,  # Bifacial modules cost more
                "Glas-Glas": 30.0,  # Glass-glass construction
                "Halbzellen": 20.0,  # Half-cell technology
                "MPPT": 15.0,  # Maximum power point tracking
            },
            "Wechselrichter": {
                "WiFi": 25.0,  # WiFi connectivity
                "Bluetooth": 15.0,  # Bluetooth connectivity
                "Display": 20.0,  # Built-in display
                "Notstrom": 150.0,  # Emergency power capability
            },
            "Batteriespeicher": {
                "Notstrom": 300.0,  # Emergency power capability
                "Inselfähig": 500.0,  # Island capability
                "Fernüberwachung": 100.0,  # Remote monitoring
            }
        }

        category_adjustments = feature_adjustments.get(category, {})
        return category_adjustments.get(feature, 0.0)

    def _get_design_adjustment(
            self,
            design: str,
            category: str | None) -> float:
        """Get pricing adjustment based on design"""
        if not design or not category:
            return 0.0

        # Design adjustment rules
        design_adjustments = {
            "Modul": {
                "All-Black": 25.0,  # Premium aesthetic
                "Black Frame": 15.0,  # Black frame design
                "Silver Frame": 0.0,  # Standard design
                "Transparent": 100.0,  # Special transparent modules
            },
            "Wechselrichter": {
                "Kompakt": 50.0,  # Compact design
                "Outdoor": 75.0,  # Outdoor-rated design
                "Indoor": 0.0,  # Standard indoor design
            }
        }

        category_adjustments = design_adjustments.get(category, {})
        return category_adjustments.get(design, 0.0)

    def _get_upgrade_adjustment(
            self,
            upgrade: str,
            category: str | None) -> float:
        """Get pricing adjustment based on upgrades"""
        if not upgrade or not category:
            return 0.0

        # Upgrade adjustment rules
        upgrade_adjustments = {
            "Modul": {
                "Leistungsgarantie": 40.0,  # Extended power warranty
                "Produktgarantie": 30.0,  # Extended product warranty
                "Premium": 100.0,  # Premium upgrade package
            },
            "Wechselrichter": {
                "Erweiterte Garantie": 150.0,  # Extended warranty
                "Service Plus": 200.0,  # Premium service package
                "Monitoring": 75.0,  # Monitoring upgrade
            },
            "Batteriespeicher": {
                "Kapazitätserweiterung": 500.0,  # Capacity expansion
                "Schnellladung": 300.0,  # Fast charging capability
                "Premium Garantie": 400.0,  # Premium warranty
            }
        }

        category_adjustments = upgrade_adjustments.get(category, {})
        return category_adjustments.get(upgrade, 0.0)

    def _get_efficiency_adjustment(
            self,
            efficiency_percent: float,
            category: str | None) -> float:
        """Get pricing adjustment based on efficiency"""
        if not efficiency_percent or not category:
            return 0.0

        # Efficiency-based adjustments (only for modules)
        if category == "Modul":
            # Premium for high-efficiency modules
            if efficiency_percent >= 22.0:
                return 50.0  # Very high efficiency
            if efficiency_percent >= 20.0:
                return 25.0  # High efficiency
            if efficiency_percent >= 18.0:
                return 0.0   # Standard efficiency
            return -25.0  # Lower efficiency discount

        return 0.0

    def _validate_calculation_inputs(
            self,
            base_price: float,
            quantity: float,
            calculate_per: str):
        """Validate calculation inputs"""
        if base_price < 0:
            raise ValidationError(
                f"Base price cannot be negative: {base_price}")

        if quantity < 0:
            raise ValidationError(f"Quantity cannot be negative: {quantity}")

        if not calculate_per:
            raise ValidationError(
                "Calculation method (calculate_per) cannot be empty")

    def _validate_calculation_result(self, result: CalculationResult):
        """Validate calculation result"""
        if result.total_price < 0:
            raise ValidationError(
                f"Total price cannot be negative: {
                    result.total_price}")

        if result.unit_price < 0:
            raise ValidationError(
                f"Unit price cannot be negative: {
                    result.unit_price}")

        # Check for reasonable price ranges
        if result.total_price > 1000000:  # 1 million euros
            result.validation_warnings.append(
                f"Very high total price: {
                    result.total_price:.2f}€")

        if result.unit_price > 100000:  # 100k euros per unit
            result.validation_warnings.append(
                f"Very high unit price: {
                    result.unit_price:.2f}€")

# Convenience functions for backward compatibility


def calculate_price_by_method(base_price: float,
                              quantity: float,
                              calculate_per: str,
                              product_specs: dict[str,
                                                  Any] | None = None) -> float:
    """
    Legacy function for backward compatibility.
    Calculate total price based on calculate_per method.

    Args:
        base_price: Base unit price
        quantity: Quantity to calculate for
        calculate_per: Calculation method ("Stück", "Meter", "pauschal", "kWp", etc.)
        product_specs: Additional product specifications

    Returns:
        Total calculated price
    """
    engine = CalculatePerEngine()

    # Convert product_specs to CalculationContext
    context = None
    if product_specs:
        context = CalculationContext(
            capacity_w=product_specs.get('capacity_w'),
            power_kw=product_specs.get('power_kw'),
            efficiency_percent=product_specs.get('efficiency_percent'),
            length_m=product_specs.get('length_m'),
            width_m=product_specs.get('width_m'),
            technology=product_specs.get('technology'),
            feature=product_specs.get('feature'),
            design=product_specs.get('design'),
            upgrade=product_specs.get('upgrade'),
            category=product_specs.get('category'),
            brand=product_specs.get('brand'),
            labor_hours=product_specs.get('labor_hours')
        )

    result = engine.calculate_price(
        base_price, quantity, calculate_per, context)
    return result.total_price


def get_supported_calculation_methods() -> list[str]:
    """Get list of supported calculation methods"""
    return [method.value for method in CalculationMethod]


def validate_calculation_method(calculate_per: str) -> bool:
    """Validate if calculation method is supported"""
    try:
        CalculationMethod.from_string(calculate_per)
        return True
    except BaseException:
        return False
