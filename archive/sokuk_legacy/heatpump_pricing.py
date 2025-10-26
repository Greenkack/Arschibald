# heatpump_pricing.py
"""Enhanced Heat Pump Pricing Engine

Zentrale Preis- und Förderlogik für Wärmepumpen-Angebote mit Integration
des Enhanced Pricing Systems. Unterstützt Profit Margins, dynamische Keys
und erweiterte Preisberechnungen.

Funktionen in diesem Modul werden sowohl von UI (heatpump_ui.py) als auch
von PDF-/Placeholder-Befüllung genutzt. Ziel ist eine einheitliche Berechnung
für Komponentenpreise, Rabatte/Aufpreise, Förderung (BEG) und Finanzierung.

Alle Funktionen liefern klar strukturierte Dicts, damit sie leicht
serialisiert oder in Session-State abgelegt werden können.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

try:
    from product_db import (
        calculate_price_by_method,
        calculate_selling_price,
        get_product_by_id,
        get_product_by_model_name,
        list_products,
    )
except Exception:  # pragma: no cover – Fallback im Testkontext ohne DB
    def list_products(category: str | None = None, company_id: int | None = None):  # type: ignore
        return []

    def get_product_by_model_name(model_name: str):  # type: ignore
        return None

    # type: ignore
    def get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return None

    def calculate_price_by_method(base_price: float, quantity: float, calculate_per: str,
                                  product_specs: dict[str, Any] | None = None) -> float:  # type: ignore
        return base_price * quantity

    # type: ignore
    def calculate_selling_price(
            product_id: int | float) -> dict[str, Any] | None:
        return None

try:
    from pricing.dynamic_key_manager import DynamicKeyManager
    from pricing.enhanced_pricing_engine import (
        FinalPricingResult,
        PriceComponent,
        PricingEngine,
        PricingResult,
    )
    from pricing.profit_margin_manager import ProfitMarginManager
except ImportError:
    # Fallback classes for standalone operation
    class PricingEngine:
        def __init__(self, system_type: str = "heatpump"):
            self.system_type = system_type

    class PriceComponent:
        pass

    class PricingResult:
        def __init__(
                self,
                base_price: float,
                components: list,
                dynamic_keys: dict,
                metadata: dict):
            self.base_price = base_price
            self.components = components
            self.dynamic_keys = dynamic_keys
            self.metadata = metadata

    class FinalPricingResult(PricingResult):
        pass

    class DynamicKeyManager:
        def generate_keys(self, data: dict, prefix: str = "") -> dict:
            return {f"{prefix}{k}": v for k, v in data.items()}

    class ProfitMarginManager:
        def calculate_selling_price(
                self,
                purchase_price: float,
                product_id: int = None) -> float:
            return purchase_price

logger = logging.getLogger(__name__)

# Kann später via Admin-Einstellung überschrieben werden
LABOR_RATE_EUR_PER_HOUR_DEFAULT = 75.0

# Heat pump specific component categories
HEATPUMP_CATEGORIES = {
    "heatpump": ["waermepumpe", "wärmepumpe", "heatpump", "vitocal"],
    "storage": ["speicher", "pufferspeicher", "warmwasserspeicher", "boiler"],
    "services": ["dienstleistung", "service", "installation", "montage", "planung"],
    "accessories": ["zubehoer", "zubehör", "accessory", "kleinteile", "rohre", "ventile"],
    "controls": ["regelung", "steuerung", "thermostat", "control", "sensor"]
}

# ----------------------------- Enhanced Datenstrukturen ----------------------------- #


@dataclass
class ComponentCost:
    name: str
    category: str
    material_net: float
    labor_hours: float = 0.0
    labor_rate: float = LABOR_RATE_EUR_PER_HOUR_DEFAULT
    description: str = ""

    # Enhanced pricing fields
    product_id: int | None = None
    calculate_per: str | None = None
    quantity: float = 1.0
    purchase_price_net: float | None = None
    margin_applied: float | None = None

    # Heat pump specific fields
    power_kw: float | None = None
    efficiency_cop: float | None = None
    refrigerant_type: str | None = None
    installation_complexity: str | None = None

    @property
    def labor_cost_net(self) -> float:
        return self.labor_hours * self.labor_rate

    @property
    def total_net(self) -> float:
        base_cost = self.material_net + self.labor_cost_net

        # Apply installation complexity multiplier
        if self.installation_complexity == "complex":
            base_cost *= 1.3
        elif self.installation_complexity == "medium":
            base_cost *= 1.15

        return base_cost

    @property
    def final_price(self) -> float:
        """Calculate final price including quantity and calculation method"""
        if not self.calculate_per:
            return self.total_net * self.quantity

        # Use enhanced calculation method
        return calculate_price_by_method(
            self.total_net, self.quantity, self.calculate_per,
            {"power_kw": self.power_kw}
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update({
            "labor_cost_net": round(self.labor_cost_net, 2),
            "total_net": round(self.total_net, 2),
            "final_price": round(self.final_price, 2),
        })
        return d


@dataclass
class HeatPumpPriceComponent(PriceComponent):
    """Heat pump specific price component extending base PriceComponent"""

    # Heat pump specific fields
    power_kw: float | None = None
    efficiency_cop: float | None = None
    refrigerant_type: str | None = None
    installation_complexity: str | None = None
    beg_eligible: bool = True

    def __post_init__(self):
        """Enhanced post-init for heat pump specific calculations"""
        super().__post_init__()
        self._calculate_heatpump_specific_pricing()

    def _calculate_heatpump_specific_pricing(self):
        """Apply heat pump specific pricing logic"""
        # Adjust pricing based on installation complexity
        if self.installation_complexity == "complex":
            complexity_multiplier = 1.3
        elif self.installation_complexity == "medium":
            complexity_multiplier = 1.15
        else:
            complexity_multiplier = 1.0

        # Apply complexity adjustment
        self.total_price *= complexity_multiplier

        # Apply efficiency bonus/penalty
        if self.efficiency_cop and self.efficiency_cop >= 4.5:
            self.total_price *= 1.05  # 5% premium for high efficiency

        # Update dynamic keys with heat pump specific information
        self._add_heatpump_keys()

    def _add_heatpump_keys(self):
        """Add heat pump specific dynamic keys"""
        key_manager = DynamicKeyManager()
        safe_name = key_manager._create_safe_key_name(self.model_name)

        hp_keys = {}

        if self.power_kw:
            hp_keys[f"{safe_name}_POWER_KW"] = self.power_kw

        if self.efficiency_cop:
            hp_keys[f"{safe_name}_COP"] = self.efficiency_cop

        if self.refrigerant_type:
            hp_keys[f"{safe_name}_REFRIGERANT"] = self.refrigerant_type

        if self.installation_complexity:
            hp_keys[f"{safe_name}_COMPLEXITY"] = self.installation_complexity

        hp_keys[f"{safe_name}_BEG_ELIGIBLE"] = "Yes" if self.beg_eligible else "No"

        self.dynamic_keys.update(hp_keys)

# ----------------------------- Enhanced Heat Pump Pricing Engine ----------------------------- #


class HeatPumpPricingEngine(PricingEngine):
    """Enhanced heat pump pricing engine with profit margins and dynamic keys"""

    def __init__(self):
        """Initialize heat pump pricing engine"""
        super().__init__(system_type="heatpump")
        self.logger = logging.getLogger(f"{__name__}.HeatPumpPricingEngine")
        self.margin_manager = ProfitMarginManager()

    def calculate_heatpump_system_price(
            self, system_config: dict[str, Any]) -> PricingResult:
        """Calculate complete heat pump system pricing

        Args:
            system_config: Heat pump system configuration

        Returns:
            PricingResult with heat pump system pricing
        """
        try:
            components = system_config.get("components", [])
            system_specs = system_config.get("system_specs", {})

            # Calculate base price with heat pump specific logic
            base_result = self._calculate_heatpump_base_price(
                components, system_specs)

            # Add heat pump specific validations
            self._validate_heatpump_configuration(components, system_specs)

            # Generate heat pump specific system keys
            hp_system_keys = self._generate_heatpump_system_keys(
                base_result, system_specs)
            base_result.dynamic_keys.update(hp_system_keys)

            return base_result

        except Exception as e:
            self.logger.error(f"Error calculating heat pump system price: {e}")
            raise

    def _calculate_heatpump_base_price(self, components: list[dict[str, Any]],
                                       system_specs: dict[str, Any]) -> PricingResult:
        """Calculate base price with heat pump specific logic"""
        hp_components = []
        total_base_price = 0.0
        all_dynamic_keys = {}

        # Extract system-level specifications
        heating_capacity_kw = system_specs.get("heating_capacity_kw", 0.0)
        installation_type = system_specs.get("installation_type", "indoor")

        for comp_data in components:
            # Get product information
            product = self._get_product_info(comp_data)
            if not product:
                self.logger.warning(
                    f"Heat pump product not found: {comp_data}")
                continue

            # Determine component category
            category = self._classify_heatpump_component(product)

            # Create heat pump specific price component
            hp_comp = self._create_heatpump_price_component(
                product, comp_data, system_specs, category
            )
            hp_components.append(hp_comp)

            # Calculate price using heat pump specific logic
            component_price = self._calculate_heatpump_component_price(
                hp_comp, system_specs
            )
            total_base_price += component_price

            # Merge dynamic keys
            all_dynamic_keys.update(hp_comp.dynamic_keys)

        # Generate system-level keys
        system_keys = self._generate_heatpump_system_keys_base(
            total_base_price, hp_components, system_specs
        )
        all_dynamic_keys.update(system_keys)

        return PricingResult(
            base_price=total_base_price,
            components=hp_components,
            dynamic_keys=all_dynamic_keys,
            metadata={
                "system_type": "heatpump",
                "component_count": len(hp_components),
                "heating_capacity_kw": heating_capacity_kw,
                "installation_type": installation_type,
                "calculation_method": "heatpump_specific"
            }
        )

    def _classify_heatpump_component(self, product: dict[str, Any]) -> str:
        """Classify heat pump component based on product data"""
        category = product.get("category", "").lower()
        model_name = product.get("model_name", "").lower()

        # Check each heat pump category
        for hp_cat, keywords in HEATPUMP_CATEGORIES.items():
            if any(keyword in category for keyword in keywords):
                return hp_cat
            if any(keyword in model_name for keyword in keywords):
                return hp_cat

        # Default classification based on power and capacity
        if product.get("power_kw"):
            return "heatpump"
        if product.get("max_kwh_capacity"):
            return "storage"
        if product.get("labor_hours"):
            return "services"
        return "accessories"

    def _create_heatpump_price_component(self,
                                         product: dict[str,
                                                       Any],
                                         comp_data: dict[str,
                                                         Any],
                                         system_specs: dict[str,
                                                            Any],
                                         category: str) -> HeatPumpPriceComponent:
        """Create heat pump specific price component"""
        # Determine installation complexity
        installation_complexity = self._determine_heatpump_complexity(
            product, system_specs
        )

        # Check BEG eligibility
        beg_eligible = self._check_beg_eligibility(product, system_specs)

        return HeatPumpPriceComponent(
            product_id=product.get("id", 0),
            model_name=product.get("model_name", ""),
            category=category,
            brand=product.get("brand"),
            quantity=comp_data.get("quantity", 1),

            # Core pricing
            price_euro=float(product.get("price_euro", 0.0)),
            calculate_per=product.get("calculate_per"),

            # Technical specs
            capacity_w=product.get("capacity_w"),
            storage_power_kw=product.get("storage_power_kw"),
            power_kw=product.get("power_kw"),
            max_cycles=product.get("max_cycles"),
            warranty_years=product.get("warranty_years"),

            # Enhanced attributes
            technology=product.get("technology"),
            feature=product.get("feature"),
            design=product.get("design"),
            upgrade=product.get("upgrade"),
            max_kwh_capacity=product.get("max_kwh_capacity"),

            # Physical dimensions
            length_m=product.get("length_m"),
            width_m=product.get("width_m"),
            weight_kg=product.get("weight_kg"),
            efficiency_percent=product.get("efficiency_percent"),

            # Additional info
            origin_country=product.get("origin_country"),
            description=product.get("description"),
            pros=product.get("pros"),
            cons=product.get("cons"),
            rating=product.get("rating"),

            # Heat pump specific fields
            efficiency_cop=product.get("efficiency_cop"),
            refrigerant_type=product.get("refrigerant_type"),
            installation_complexity=installation_complexity,
            beg_eligible=beg_eligible
        )

    def _determine_heatpump_complexity(self, product: dict[str, Any],
                                       system_specs: dict[str, Any]) -> str:
        """Determine installation complexity for heat pump components"""
        installation_type = system_specs.get("installation_type", "indoor")
        building_type = system_specs.get("building_type", "existing")

        # Complex installations
        if installation_type == "outdoor" and building_type == "renovation":
            return "complex"

        # Medium complexity
        if installation_type == "outdoor" or building_type == "renovation":
            return "medium"

        # Simple installations
        return "simple"

    def _check_beg_eligibility(self, product: dict[str, Any],
                               system_specs: dict[str, Any]) -> bool:
        """Check if component is eligible for BEG subsidy"""
        # Heat pumps are generally BEG eligible
        category = product.get("category", "").lower()

        if any(
                keyword in category for keyword in HEATPUMP_CATEGORIES["heatpump"]):
            return True

        # Storage and services are also eligible
        if any(
                keyword in category for keyword in HEATPUMP_CATEGORIES["storage"]):
            return True

        if any(
                keyword in category for keyword in HEATPUMP_CATEGORIES["services"]):
            return True

        return False

    def _calculate_heatpump_component_price(self, component: HeatPumpPriceComponent,
                                            system_specs: dict[str, Any]) -> float:
        """Calculate component price using heat pump specific logic"""
        base_price = component.price_euro
        quantity = component.quantity
        calculate_per = component.calculate_per or "Stück"

        # Apply profit margins if available
        if component.product_id:
            margin_result = calculate_selling_price(component.product_id)
            if margin_result and margin_result.get("selling_price_net"):
                base_price = margin_result["selling_price_net"]

        # Use enhanced calculation method
        product_specs = {
            "power_kw": component.power_kw,
            "max_kwh_capacity": component.max_kwh_capacity,
            "labor_hours": getattr(component, "labor_hours", 0)
        }

        total_price = calculate_price_by_method(
            base_price, quantity, calculate_per, product_specs
        )

        # Apply heat pump specific adjustments
        total_price = self._apply_heatpump_adjustments(component, total_price)

        return total_price

    def _apply_heatpump_adjustments(self, component: HeatPumpPriceComponent,
                                    base_price: float) -> float:
        """Apply heat pump specific pricing adjustments"""
        adjusted_price = base_price

        # Efficiency-based adjustments
        if component.efficiency_cop:
            if component.efficiency_cop >= 4.5:
                adjusted_price *= 1.05  # 5% premium for high COP
            elif component.efficiency_cop >= 4.0:
                adjusted_price *= 1.02  # 2% premium for good COP

        # Refrigerant type adjustments
        if component.refrigerant_type:
            refrigerant = component.refrigerant_type.lower()
            if "r290" in refrigerant or "propan" in refrigerant:
                adjusted_price *= 1.03  # 3% premium for natural refrigerant

        return adjusted_price

    def _generate_heatpump_system_keys_base(self,
                                            total_price: float,
                                            components: list[HeatPumpPriceComponent],
                                            system_specs: dict[str,
                                                               Any]) -> dict[str,
                                                                             Any]:
        """Generate heat pump system-level dynamic keys"""
        system_keys = self.key_manager.generate_keys({
            "HP_BASE_PRICE_NET": total_price,
            "HP_COMPONENT_COUNT": len(components),
            "HP_SYSTEM_TYPE": "heatpump"
        }, prefix="HP_")

        # Calculate category totals
        category_totals = {}
        total_power_kw = 0
        beg_eligible_count = 0

        for comp in components:
            cat = comp.category
            if cat not in category_totals:
                category_totals[cat] = 0.0
            category_totals[cat] += comp.total_price

            # Track power and BEG eligibility
            if comp.power_kw:
                total_power_kw += comp.power_kw

            if comp.beg_eligible:
                beg_eligible_count += 1

        # Add category totals
        for category, total in category_totals.items():
            safe_cat = self.key_manager._create_safe_key_name(category)
            system_keys[f"HP_{safe_cat.upper()}_TOTAL"] = total

        # Add system specifications
        system_keys.update({
            "HP_TOTAL_POWER_KW": total_power_kw,
            "HP_BEG_ELIGIBLE_COMPONENTS": beg_eligible_count,
            "HP_INSTALLATION_TYPE": system_specs.get("installation_type", "indoor"),
            "HP_BUILDING_TYPE": system_specs.get("building_type", "existing")
        })

        return system_keys

    def _generate_heatpump_system_keys(self,
                                       base_result: PricingResult,
                                       system_specs: dict[str,
                                                          Any]) -> dict[str,
                                                                        Any]:
        """Generate additional heat pump system keys"""
        hp_keys = {}

        # Performance calculations
        total_power_kw = system_specs.get("heating_capacity_kw", 0.0)
        if total_power_kw > 0:
            # Price per kW heating capacity
            price_per_kw = base_result.base_price / total_power_kw
            hp_keys["HP_PRICE_PER_KW"] = round(price_per_kw, 2)

        # System efficiency indicators
        avg_cop = self._calculate_average_cop(base_result.components)
        if avg_cop:
            hp_keys["HP_AVERAGE_COP"] = round(avg_cop, 2)

        # BEG eligibility summary
        beg_eligible_price = self._calculate_beg_eligible_price(
            base_result.components)
        hp_keys["HP_BEG_ELIGIBLE_PRICE"] = beg_eligible_price

        return hp_keys

    def _calculate_average_cop(
            self,
            components: list[PriceComponent]) -> float | None:
        """Calculate weighted average COP of heat pump components"""
        total_power = 0.0
        weighted_cop = 0.0

        for comp in components:
            if (hasattr(comp, "efficiency_cop") and comp.efficiency_cop and
                    hasattr(comp, "power_kw") and comp.power_kw):

                power = comp.power_kw
                total_power += power
                weighted_cop += comp.efficiency_cop * power

        if total_power > 0:
            return weighted_cop / total_power

        return None

    def _calculate_beg_eligible_price(
            self, components: list[PriceComponent]) -> float:
        """Calculate total price of BEG eligible components"""
        beg_price = 0.0

        for comp in components:
            if hasattr(comp, "beg_eligible") and comp.beg_eligible:
                beg_price += comp.total_price

        return beg_price

    def _validate_heatpump_configuration(
            self, components: list[dict[str, Any]], system_specs: dict[str, Any]):
        """Validate heat pump system configuration"""
        # Check for required components
        has_heatpump = any(
            self._classify_heatpump_component(self._get_product_info(comp) or {}) == "heatpump"
            for comp in components
        )

        if not has_heatpump:
            self.logger.warning(
                "Heat pump system configuration missing main heat pump unit")

# ----------------------------- Komponenten Laden -------------------------- #


HEATPUMP_CATEGORY_ALIASES = {"waermepumpe", "wärmepumpe", "heatpump"}
STORAGE_CATEGORY_ALIASES = {"speicher", "pufferspeicher", "warmwasserspeicher"}
SERVICE_CATEGORY_ALIASES = {
    "dienstleistung",
    "service",
    "installation",
    "montage"}
ACCESSORY_CATEGORY_ALIASES = {"zubehoer", "zubehör", "accessory"}

MAIN_COMPONENT_KEYWORDS = ["vitocal", "warmwasser", "puffer"]  # heuristisch


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def load_heatpump_components() -> dict[str, list[ComponentCost]]:
    """Lädt Produkte aus der DB und klassifiziert sie in Haupt- / Zubehörgruppen.
    Erwartet, dass in der products Tabelle Preise in `price_euro` und Arbeitsstunden
    in `labor_hours` gepflegt sind.
    """
    prods = list_products() or []
    main: list[ComponentCost] = []
    accessories: list[ComponentCost] = []

    for p in prods:
        cat = _norm(p.get("category", ""))
        model = p.get("model_name", "")
        price = float(p.get("price_euro") or 0.0)
        labor_h = float(p.get("labor_hours") or 0.0)
        desc = p.get("description") or ""
        cc = ComponentCost(
            name=model,
            category=cat,
            material_net=price,
            labor_hours=labor_h,
            description=desc)
        # Einfache Heuristik: Hauptkomponenten falls Keyword matcht oder
        # Kategorie klar
        if any(k in _norm(model) for k in MAIN_COMPONENT_KEYWORDS):
            main.append(cc)
        else:
            accessories.append(cc)
    return {"main": main, "accessories": accessories}

# ----------------------------- Preislogik --------------------------------- #


def calculate_base_price(
        components: dict[str, list[ComponentCost]]) -> dict[str, Any]:
    all_components = components.get(
        "main", []) + components.get("accessories", [])
    material_sum = sum(c.material_net for c in all_components)
    labor_sum = sum(c.labor_cost_net for c in all_components)
    total = material_sum + labor_sum
    return {
        "material_sum_net": round(material_sum, 2),
        "labor_sum_net": round(labor_sum, 2),
        "base_total_net": round(total, 2),
    }


def apply_discounts_and_surcharges(base_total_net: float,
                                   rabatt_pct: float = 0.0,
                                   rabatt_abs: float = 0.0,
                                   zuschlag_pct: float = 0.0,
                                   zuschlag_abs: float = 0.0) -> dict[str,
                                                                      Any]:
    rabatt_wert_pct = base_total_net * (rabatt_pct / 100.0)
    zwischen = base_total_net - rabatt_wert_pct - rabatt_abs
    zuschlag_wert_pct = zwischen * (zuschlag_pct / 100.0)
    final_net = zwischen + zuschlag_wert_pct + zuschlag_abs
    return {
        "rabatt_pct": rabatt_pct,
        "rabatt_pct_amount": round(rabatt_wert_pct, 2),
        "rabatt_abs": round(rabatt_abs, 2),
        "zuschlag_pct": zuschlag_pct,
        "zuschlag_pct_amount": round(zuschlag_wert_pct, 2),
        "zuschlag_abs": round(zuschlag_abs, 2),
        "final_price_net": round(final_net, 2),
    }

# ----------------------------- Förderung (BEG) ---------------------------- #


@dataclass
class BegConfig:
    base_pct: float = 30.0
    refrigerant_bonus_pct: float = 5.0
    heating_replacement_bonus_pct: float = 20.0
    # Aufgabenstellung (auch wenn teils 30 % aktuell)
    low_income_bonus_pct: float = 20.0
    max_total_pct: float = 70.0
    eligible_cost_cap_eur: float = 30000.0  # Optionale Deckelung


def calculate_beg_subsidy(total_cost_net: float,
                          use_natural_refrigerant: bool,
                          replace_old_heating: bool,
                          low_income: bool,
                          cfg: BegConfig | None = None) -> dict[str,
                                                                Any]:
    cfg = cfg or BegConfig()
    pct = cfg.base_pct
    details = {"base_pct": cfg.base_pct}
    if use_natural_refrigerant:
        pct += cfg.refrigerant_bonus_pct
        details["refrigerant_bonus_pct"] = cfg.refrigerant_bonus_pct
    if replace_old_heating:
        pct += cfg.heating_replacement_bonus_pct
        details["heating_replacement_bonus_pct"] = cfg.heating_replacement_bonus_pct
    if low_income:
        pct += cfg.low_income_bonus_pct
        details["low_income_bonus_pct"] = cfg.low_income_bonus_pct
    capped_pct = min(pct, cfg.max_total_pct)
    eligible_costs = min(total_cost_net, cfg.eligible_cost_cap_eur)
    subsidy_amount = eligible_costs * (capped_pct / 100.0)
    return {
        "requested_pct": pct, "applied_pct": capped_pct, "eligible_costs_net": round(
            eligible_costs, 2), "subsidy_amount_net": round(
            subsidy_amount, 2), "effective_total_after_subsidy_net": round(
                total_cost_net - subsidy_amount, 2), "detail": details, }

# ----------------------------- Finanzierung ------------------------------ #


def calculate_annuity_loan(principal: float,
                           annual_interest_rate_pct: float,
                           years: int) -> dict[str,
                                               Any]:
    if principal <= 0 or years <= 0 or annual_interest_rate_pct < 0:
        return {"error": "invalid parameters"}
    r = annual_interest_rate_pct / 100.0 / 12.0
    n = years * 12
    if r == 0:
        rate = principal / n
    else:
        rate = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    remaining = principal
    plan = []
    total_interest = 0.0
    for m in range(1, n + 1):
        interest = remaining * r
        principal_pay = rate - interest
        remaining -= principal_pay
        total_interest += interest
        plan.append({
            "month": m,
            "rate": round(rate, 2),
            "interest": round(interest, 2),
            "principal": round(principal_pay, 2),
            "remaining": round(max(0.0, remaining), 2)
        })
    return {
        "monthly_rate": round(rate, 2),
        "total_interest": round(total_interest, 2),
        "total_paid": round(principal + total_interest, 2),
        "months": n,
        "plan": plan,
    }

# ----------------------------- Orchestrierung ---------------------------- #


def build_enhanced_heatpump_offer(system_config: dict[str, Any],
                                  rabatt_pct: float = 0.0, rabatt_abs: float = 0.0,
                                  zuschlag_pct: float = 0.0, zuschlag_abs: float = 0.0,
                                  beg_flags: dict[str, bool] | None = None,
                                  financing: dict[str, float] | None = None) -> dict[str, Any]:
    """Build enhanced heat pump offer using new pricing system"""
    try:
        # Use enhanced pricing engine
        hp_engine = HeatPumpPricingEngine()
        base_result = hp_engine.calculate_heatpump_system_price(system_config)

        # Apply modifications using enhanced pricing engine
        modifications = {
            "discount_percent": rabatt_pct,
            "discount_fixed": rabatt_abs,
            "surcharge_percent": zuschlag_pct,
            "surcharge_fixed": zuschlag_abs
        }

        mod_result = hp_engine.apply_modifications(
            base_result.base_price, modifications)

        # Calculate BEG subsidy
        beg_flags = beg_flags or {}
        subsidy = calculate_beg_subsidy(
            mod_result["final_price"],
            use_natural_refrigerant=beg_flags.get("natural_refrigerant", True),
            replace_old_heating=beg_flags.get("replace_old", False),
            low_income=beg_flags.get("low_income", False)
        )

        # Calculate financing
        financing_result = None
        if financing:
            principal = subsidy["effective_total_after_subsidy_net"] - \
                float(financing.get("equity_amount", 0.0))
            if principal < 0:
                principal = 0.0
            financing_result = calculate_annuity_loan(
                principal,
                financing.get("interest_pct", 3.0),
                int(financing.get("years", 15))
            )

        # Combine all dynamic keys
        all_keys = base_result.dynamic_keys.copy()
        all_keys.update(mod_result.get("dynamic_keys", {}))

        return {
            "components": [
                comp.to_dict() if hasattr(
                    comp,
                    'to_dict') else comp for comp in base_result.components],
            "base": {
                "base_total_net": base_result.base_price,
                "component_count": len(
                    base_result.components)},
            "pricing_modifiers": mod_result,
            "beg_subsidy": subsidy,
            "financing": financing_result,
            "dynamic_keys": all_keys,
            "metadata": base_result.metadata}

    except Exception as e:
        logger.error(f"Error building enhanced heat pump offer: {e}")
        # Fallback to legacy system
        return build_full_heatpump_offer(
            rabatt_pct,
            rabatt_abs,
            zuschlag_pct,
            zuschlag_abs,
            beg_flags,
            financing)


def build_full_heatpump_offer(rabatt_pct: float = 0.0,
                              rabatt_abs: float = 0.0,
                              zuschlag_pct: float = 0.0,
                              zuschlag_abs: float = 0.0,
                              beg_flags: dict[str,
                                              bool] | None = None,
                              financing: dict[str,
                                              float] | None = None) -> dict[str,
                                                                            Any]:
    """Legacy heat pump offer builder - maintained for backward compatibility"""
    comps = load_heatpump_components()
    base = calculate_base_price(comps)
    mods = apply_discounts_and_surcharges(
        base["base_total_net"],
        rabatt_pct,
        rabatt_abs,
        zuschlag_pct,
        zuschlag_abs)
    beg_flags = beg_flags or {}
    subsidy = calculate_beg_subsidy(
        mods["final_price_net"], use_natural_refrigerant=beg_flags.get(
            "natural_refrigerant", True), replace_old_heating=beg_flags.get(
            "replace_old", False), low_income=beg_flags.get(
                "low_income", False))
    financing_result = None
    if financing:
        principal = subsidy["effective_total_after_subsidy_net"] - \
            float(financing.get("equity_amount", 0.0))
        if principal < 0:
            principal = 0.0
        financing_result = calculate_annuity_loan(
            principal, financing.get(
                "interest_pct", 3.0), int(
                financing.get(
                    "years", 15)))
    return {
        "components": {
            "main": [c.to_dict() for c in comps["main"]],
            "accessories": [c.to_dict() for c in comps["accessories"]],
        },
        "base": base,
        "pricing_modifiers": mods,
        "beg_subsidy": subsidy,
        "financing": financing_result,
    }

# ----------------------------- Placeholder Helper ------------------------ #


def extract_placeholders_from_offer(offer: dict[str, Any]) -> dict[str, Any]:
    """Erzeugt flache Placeholder-Struktur für PDF/Template.
    Unterstützt sowohl legacy als auch enhanced pricing system.
    Nutzung: dyn.update(extract_placeholders_from_offer(offer))
    """
    out: dict[str, Any] = {}

    # Check if this is an enhanced offer with dynamic keys
    if "dynamic_keys" in offer:
        # Use dynamic keys from enhanced pricing system
        out.update(offer["dynamic_keys"])

    # Legacy compatibility
    base = offer.get("base", {})
    mods = offer.get("pricing_modifiers", {})
    subsidy = offer.get("beg_subsidy", {})
    financing = offer.get("financing") or {}

    # Add legacy keys (will be overridden by dynamic keys if present)
    legacy_keys = {
        "HP_MATERIAL_NET": base.get("material_sum_net"),
        "HP_LABOR_NET": base.get("labor_sum_net"),
        "HP_BASE_TOTAL_NET": base.get("base_total_net"),
        "HP_RABATT_PCT": mods.get("rabatt_pct"),
        "HP_RABATT_PCT_AMOUNT": mods.get("rabatt_pct_amount"),
        "HP_RABATT_ABS": mods.get("rabatt_abs"),
        "HP_ZUSCHLAG_PCT": mods.get("zuschlag_pct"),
        "HP_ZUSCHLAG_PCT_AMOUNT": mods.get("zuschlag_pct_amount"),
        "HP_ZUSCHLAG_ABS": mods.get("zuschlag_abs"),
        "HP_FINAL_PRICE_NET": mods.get("final_price_net") or mods.get("final_price"),
        "HP_SUBSIDY_PCT": subsidy.get("applied_pct"),
        "HP_SUBSIDY_AMOUNT": subsidy.get("subsidy_amount_net"),
        "HP_AFTER_SUBSIDY_NET": subsidy.get("effective_total_after_subsidy_net"),
        "HP_MONTHLY_RATE": financing.get("monthly_rate"),
        "HP_TOTAL_INTEREST": financing.get("total_interest"),
    }

    # Add legacy keys only if not already present from dynamic keys
    for key, value in legacy_keys.items():
        if key not in out and value is not None:
            out[key] = value

    # Komponentenliste konsolidieren (handle both legacy and enhanced formats)
    items: list[str] = []
    components = offer.get("components", [])

    if isinstance(components, dict):
        # Legacy format
        for c in components.get("main", []):
            items.append(
                f"{c['name']} ({c.get('total_net', c.get('final_price', 0)):.0f} €)")
        for c in components.get("accessories", []):
            items.append(
                f"{c['name']} ({c.get('total_net', c.get('final_price', 0)):.0f} €)")
    elif isinstance(components, list):
        # Enhanced format
        for c in components:
            if hasattr(c, 'model_name') and hasattr(c, 'total_price'):
                items.append(f"{c.model_name} ({c.total_price:.0f} €)")
            elif isinstance(c, dict):
                name = c.get('name') or c.get('model_name', 'Unknown')
                price = c.get('total_net') or c.get(
                    'final_price') or c.get('total_price', 0)
                items.append(f"{name} ({price:.0f} €)")

    out["HP_COMPONENTS_TEXT"] = ", ".join(items)

    # Nummerierte Items (begrenze auf 15 damit Template nicht explodiert)
    all_components = []
    if isinstance(components, dict):
        all_components = components.get(
            "main", []) + components.get("accessories", [])
    elif isinstance(components, list):
        all_components = components

    for idx, c in enumerate(all_components, start=1):
        if idx > 15:
            break

        if hasattr(c, 'model_name') and hasattr(c, 'total_price'):
            out[f"HP_ITEM{idx}_NAME"] = c.model_name
            out[f"HP_ITEM{idx}_PRICE_NET"] = c.total_price
        elif isinstance(c, dict):
            name = c.get('name') or c.get('model_name', f'Item {idx}')
            price = c.get('total_net') or c.get(
                'final_price') or c.get('total_price', 0)
            out[f"HP_ITEM{idx}_NAME"] = name
            out[f"HP_ITEM{idx}_PRICE_NET"] = price

    return out


def extract_enhanced_placeholders(offer: dict[str, Any]) -> dict[str, Any]:
    """Extract placeholders specifically from enhanced pricing system offers"""
    if "dynamic_keys" not in offer:
        return extract_placeholders_from_offer(offer)

    placeholders = offer["dynamic_keys"].copy()

    # Add metadata placeholders
    metadata = offer.get("metadata", {})
    for key, value in metadata.items():
        placeholder_key = f"HP_META_{key.upper()}"
        placeholders[placeholder_key] = value

    return placeholders

# ----------------------------- Convenience Functions ----------------------------- #


def create_heatpump_pricing_engine() -> HeatPumpPricingEngine:
    """Create a new heat pump pricing engine instance"""
    return HeatPumpPricingEngine()


def calculate_heatpump_system_pricing(
        system_config: dict[str, Any]) -> PricingResult:
    """Calculate heat pump system pricing using the enhanced pricing engine

    Args:
        system_config: Heat pump system configuration

    Returns:
        PricingResult with complete heat pump system pricing
    """
    engine = create_heatpump_pricing_engine()
    return engine.calculate_heatpump_system_price(system_config)


__all__ = [
    # Legacy components
    "ComponentCost",
    "load_heatpump_components",
    "calculate_base_price",
    "apply_discounts_and_surcharges",
    "BegConfig",
    "calculate_beg_subsidy",
    "calculate_annuity_loan",
    "build_full_heatpump_offer",
    "extract_placeholders_from_offer",

    # Enhanced pricing system
    "HeatPumpPriceComponent",
    "HeatPumpPricingEngine",
    "build_enhanced_heatpump_offer",
    "extract_enhanced_placeholders",
    "create_heatpump_pricing_engine",
    "calculate_heatpump_system_pricing",
    "HEATPUMP_CATEGORIES",
]
