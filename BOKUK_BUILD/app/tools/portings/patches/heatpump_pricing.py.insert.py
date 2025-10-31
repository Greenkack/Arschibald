# === AUTO-GENERATED INSERT PATCH ===
# target_module: heatpump_pricing.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import math

# --- DEF BLOCK START: func _norm ---


def _norm(s: str) -> str:
    return (s or "").strip().lower()
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func load_heatpump_components ---

def load_heatpump_components() -> Dict[str, List[ComponentCost]]:
    """Lädt Produkte aus der DB und klassifiziert sie in Haupt- / Zubehörgruppen.
    Erwartet, dass in der products Tabelle Preise in `price_euro` und Arbeitsstunden
    in `labor_hours` gepflegt sind.
    """
    prods = list_products() or []
    main: List[ComponentCost] = []
    accessories: List[ComponentCost] = []

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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func calculate_base_price ---

def calculate_base_price(
    components: Dict[str, List[ComponentCost]]) -> Dict[str, Any]:
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func apply_discounts_and_surcharges ---

def apply_discounts_and_surcharges(base_total_net: float, rabatt_pct: float = 0.0, rabatt_abs: float = 0.0,
                                   zuschlag_pct: float = 0.0, zuschlag_abs: float = 0.0) -> Dict[str, Any]:
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func calculate_beg_subsidy ---

def calculate_beg_subsidy(total_cost_net: float, use_natural_refrigerant: bool, replace_old_heating: bool,
                          low_income: bool, cfg: Optional[BegConfig] = None) -> Dict[str, Any]:
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
        "requested_pct": pct,
        "applied_pct": capped_pct,
        "eligible_costs_net": round(eligible_costs, 2),
        "subsidy_amount_net": round(subsidy_amount, 2),
        "effective_total_after_subsidy_net": round(total_cost_net - subsidy_amount, 2),
        "detail": details,
    }
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func calculate_annuity_loan ---

def calculate_annuity_loan(principal: float,
    annual_interest_rate_pct: float,
    years: int) -> Dict[str,
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func build_full_heatpump_offer ---

def build_full_heatpump_offer(rabatt_pct: float = 0.0, rabatt_abs: float = 0.0, zuschlag_pct: float = 0.0,
                              zuschlag_abs: float = 0.0, beg_flags: Optional[Dict[str, bool]] = None,
                              financing: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    comps = load_heatpump_components()
    base = calculate_base_price(comps)
    mods = apply_discounts_and_surcharges(
    base["base_total_net"],
    rabatt_pct,
    rabatt_abs,
    zuschlag_pct,
     zuschlag_abs)
    beg_flags = beg_flags or {}
    subsidy = calculate_beg_subsidy(mods["final_price_net"],
                                    use_natural_refrigerant=beg_flags.get(
                                        "natural_refrigerant", True),
                                    replace_old_heating=beg_flags.get(
                                        "replace_old", False),
                                    low_income=beg_flags.get("low_income", False))
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func extract_placeholders_from_offer ---

def extract_placeholders_from_offer(offer: Dict[str, Any]) -> Dict[str, Any]:
    """Erzeugt flache Placeholder-Struktur für PDF/Template.
    Nutzung: dyn.update(extract_placeholders_from_offer(offer))
    """
    out: Dict[str, Any] = {}
    base = offer.get("base", {})
    mods = offer.get("pricing_modifiers", {})
    subsidy = offer.get("beg_subsidy", {})
    financing = offer.get("financing") or {}

    out.update({
        "HP_MATERIAL_NET": base.get("material_sum_net"),
        "HP_LABOR_NET": base.get("labor_sum_net"),
        "HP_BASE_TOTAL_NET": base.get("base_total_net"),
        "HP_RABATT_PCT": mods.get("rabatt_pct"),
        "HP_RABATT_PCT_AMOUNT": mods.get("rabatt_pct_amount"),
        "HP_RABATT_ABS": mods.get("rabatt_abs"),
        "HP_ZUSCHLAG_PCT": mods.get("zuschlag_pct"),
        "HP_ZUSCHLAG_PCT_AMOUNT": mods.get("zuschlag_pct_amount"),
        "HP_ZUSCHLAG_ABS": mods.get("zuschlag_abs"),
        "HP_FINAL_PRICE_NET": mods.get("final_price_net"),
        "HP_SUBSIDY_PCT": subsidy.get("applied_pct"),
        "HP_SUBSIDY_AMOUNT": subsidy.get("subsidy_amount_net"),
        "HP_AFTER_SUBSIDY_NET": subsidy.get("effective_total_after_subsidy_net"),
        "HP_MONTHLY_RATE": financing.get("monthly_rate"),
        "HP_TOTAL_INTEREST": financing.get("total_interest"),
    })

    # Komponentenliste konsolidieren
    items: List[str] = []
    for c in offer.get("components", {}).get("main", []):
        items.append(f"{c['name']} ({c['total_net']:.0f} €)")
    for c in offer.get("components", {}).get("accessories", []):
        items.append(f"{c['name']} ({c['total_net']:.0f} €)")
    out["HP_COMPONENTS_TEXT"] = ", ".join(items)

    # Nummerierte Items (begrenze auf 15 damit Template nicht explodiert)
    for idx, c in enumerate(offer.get("components", {}).get(
        "main", []) + offer.get("components", {}).get("accessories", []), start=1):
        if idx > 15:
            break
        out[f"HP_ITEM{idx}_NAME"] = c["name"]
        out[f"HP_ITEM{idx}_PRICE_NET"] = c["total_net"]
    return out
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: class ComponentCost ---

@dataclass
class ComponentCost:
    name: str
    category: str
    material_net: float
    labor_hours: float = 0.0
    labor_rate: float = LABOR_RATE_EUR_PER_HOUR_DEFAULT
    description: str = ""

    @property
    def labor_cost_net(self) -> float:
        return self.labor_hours * self.labor_rate

    @property
    def total_net(self) -> float:
        return self.material_net + self.labor_cost_net

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.update({
            "labor_cost_net": round(self.labor_cost_net, 2),
            "total_net": round(self.total_net, 2),
        })
        return d
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: class BegConfig ---

@dataclass
class BegConfig:
    base_pct: float = 30.0
    refrigerant_bonus_pct: float = 5.0
    heating_replacement_bonus_pct: float = 20.0
    # Aufgabenstellung (auch wenn teils 30 % aktuell)
    low_income_bonus_pct: float = 20.0
    max_total_pct: float = 70.0
    eligible_cost_cap_eur: float = 30000.0  # Optionale Deckelung
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: method ComponentCost.labor_cost_net ---
   @property
    def labor_cost_net(self) -> float:
        return self.labor_hours * self.labor_rate
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: method ComponentCost.total_net ---
   @property
    def total_net(self) -> float:
        return self.material_net + self.labor_cost_net
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: method ComponentCost.to_dict ---
   def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.update({
            "labor_cost_net": round(self.labor_cost_net, 2),
            "total_net": round(self.total_net, 2),
        })
        return d
# --- DEF BLOCK END ---
