"""Common financial and pricing helper functions used across the Bokuk codebase.

The goal of this module is to provide a single source of truth for recurring
business calculations (VAT, net/gross totals, discounts, surcharges,
amortisation/payback, and subtotal aggregation).  All legacy duplicates should
migrate to these helpers to guarantee identical results across the application
suite including archived compatibility layers under ``KOPIE``.

Each helper is intentionally minimal and side-effect free so that it can be used
both in production code and in tests for expected value construction without
violating test semantics.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

# Central VAT reference used across the project
VAT_RATE_DEFAULT = 0.19


def _safe_float(value: float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        if value != value:  # NaN check
            return 0.0
        if value == float("inf") or value == float("-inf"):
            return 0.0
        return float(value)
    raise TypeError(f"Unsupported numeric type: {type(value)!r}")


def calculate_payback_years(
    investment_amount: float | None,
    annual_benefit: float | None,
    *,
    allow_infinite: bool = True,
    default_zero: bool = False,
) -> float:
    """Return the amortisation/payback period in years.

    ``allow_infinite`` mirrors historical logic where division by zero yielded
    ``float('inf')`` to highlight missing profitability.  ``default_zero`` is an
    additional guard for UI widgets that expect ``0`` instead of ``inf``.
    """

    investment = _safe_float(investment_amount)
    benefit = _safe_float(annual_benefit)

    if benefit <= 0:
        if default_zero:
            return 0.0
        return float("inf") if allow_infinite else 0.0

    return investment / benefit


def calculate_discount_amount(
        base_amount: float | None,
        percent: float | None) -> float:
    base = _safe_float(base_amount)
    pct = _safe_float(percent)
    return base * pct / 100.0


def calculate_surcharge_amount(
        base_amount: float | None,
        percent: float | None) -> float:
    base = _safe_float(base_amount)
    pct = _safe_float(percent)
    return base * pct / 100.0


def apply_discount(
        base_amount: float | None,
        *,
        percent: float | None = None,
        amount: float | None = None) -> float:
    base = _safe_float(base_amount)
    discount_total = 0.0

    if percent is not None:
        discount_total += calculate_discount_amount(base, percent)

    if amount is not None:
        discount_total += _safe_float(amount)

    return max(base - discount_total, 0.0)


def apply_surcharge(
        base_amount: float | None,
        *,
        percent: float | None = None,
        amount: float | None = None) -> float:
    base = _safe_float(base_amount)
    surcharge_total = 0.0

    if percent is not None:
        surcharge_total += calculate_surcharge_amount(base, percent)

    if amount is not None:
        surcharge_total += _safe_float(amount)

    return max(base + surcharge_total, 0.0)


def calculate_vat_amount(net_amount: float | None,
                         vat_rate: float = VAT_RATE_DEFAULT) -> float:
    net = _safe_float(net_amount)
    return net * vat_rate


def calculate_gross_from_net(
        net_amount: float | None,
        vat_rate: float = VAT_RATE_DEFAULT) -> float:
    net = _safe_float(net_amount)
    return net + calculate_vat_amount(net, vat_rate)


def calculate_net_from_gross(
        gross_amount: float | None,
        vat_rate: float = VAT_RATE_DEFAULT) -> float:
    gross = _safe_float(gross_amount)
    divisor = 1 + vat_rate
    if divisor == 0:
        raise ZeroDivisionError("VAT divisor must not be zero")
    return gross / divisor


def aggregate_subtotal(
    *,
    base: float | None = 0.0,
    discounts: Iterable[float] | None = None,
    surcharges: Iterable[float] | None = None,
    additions: Iterable[float] | None = None,
) -> float:
    """Aggregate subtotal from base, surcharges, discounts and other add-ons."""

    subtotal = _safe_float(base)

    if additions:
        subtotal += sum(_safe_float(val) for val in additions)

    if discounts:
        subtotal -= sum(_safe_float(val) for val in discounts)

    if surcharges:
        subtotal += sum(_safe_float(val) for val in surcharges)

    return max(subtotal, 0.0)


@dataclass(frozen=True)
class FinalPriceBreakdown:
    net_price: float
    total_discounts: float
    total_surcharges: float
    additional_costs: float
    net_after_modifications: float
    gross_total: float


def calculate_final_price(
    *,
    base_net_price: float | None,
    discount_percent: float | None = None,
    surcharge_percent: float | None = None,
    discount_amount: float | None = None,
    surcharge_amount: float | None = None,
    additional_costs: float | None = None,
    vat_rate: float = VAT_RATE_DEFAULT,
) -> FinalPriceBreakdown:
    """Return a structured summary of a final price including VAT."""

    base = _safe_float(base_net_price)
    discount_pct_amount = calculate_discount_amount(base, discount_percent)
    surcharge_base = max(base - discount_pct_amount, 0.0)
    surcharge_pct_amount = calculate_surcharge_amount(
        surcharge_base, surcharge_percent)

    discount_fixed = _safe_float(
        discount_amount) if discount_amount is not None else 0.0
    surcharge_fixed = _safe_float(
        surcharge_amount) if surcharge_amount is not None else 0.0
    additionals = _safe_float(additional_costs)

    net_after = (
        surcharge_base
        - discount_fixed
        + surcharge_pct_amount
        + surcharge_fixed
        + additionals
    )
    net_after = max(net_after, 0.0)

    total_discounts = discount_pct_amount + discount_fixed
    total_surcharges = surcharge_pct_amount + surcharge_fixed

    gross_total = calculate_gross_from_net(net_after, vat_rate)

    return FinalPriceBreakdown(
        net_price=base,
        total_discounts=total_discounts,
        total_surcharges=total_surcharges,
        additional_costs=additionals,
        net_after_modifications=net_after,
        gross_total=gross_total,
    )
