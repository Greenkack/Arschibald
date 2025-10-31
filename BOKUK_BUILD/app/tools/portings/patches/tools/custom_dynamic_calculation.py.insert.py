# === AUTO-GENERATED INSERT PATCH ===
# target_module: tools/custom_dynamic_calculation.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from __future__ import annotations

from dataclasses import dataclass


# --- DEF BLOCK START: func calculate_savings ---
def calculate_savings(
    annual_consumption_kwh: float,
    pv_production_kwh: float,
    direct_consumption_kwh: float,
    battery_capacity_kwh: float,
    price_eur_per_kwh: float,
    eeg_eur_per_kwh: float,
    days_per_year: int = 300,
) -> SavingsResult:
    """Calculate annual savings for a PV system with battery storage.

    Args:
        annual_consumption_kwh: Total annual electricity consumption of the household.
        pv_production_kwh: Annual PV production of the solar array.
        direct_consumption_kwh: Electricity directly consumed during the day from PV.
        battery_capacity_kwh: Usable storage capacity of the battery (kWh).
        price_eur_per_kwh: Customer electricity price in EUR/kWh.
        eeg_eur_per_kwh: Feed‑in tariff in EUR/kWh.
        days_per_year: Number of days the battery charges each year (default 300).

    Returns:
        A SavingsResult dataclass instance containing all intermediate values and
        the total savings for the year.
    """
    # Energy stored in the battery over the year
    battery_charge = battery_capacity_kwh * float(days_per_year)
    # Remaining consumption after direct daytime PV usage
    remaining_consumption = max(
        0.0,
        annual_consumption_kwh -
        direct_consumption_kwh)
    # Discharged energy is limited by both the remaining consumption and the
    # stored energy
    battery_discharge = min(remaining_consumption, battery_charge)
    # Any energy left in the battery that cannot be used is fed into the grid
    battery_surplus = max(0.0, battery_charge - battery_discharge)
    # Feed‑in from PV after subtracting direct consumption and battery charge
    grid_feedin = max(
        0.0,
        pv_production_kwh -
        direct_consumption_kwh -
        battery_charge)

    # Calculate monetary values
    savings_direct = direct_consumption_kwh * price_eur_per_kwh
    revenue_grid = grid_feedin * eeg_eur_per_kwh
    savings_battery_usage = battery_discharge * price_eur_per_kwh
    savings_battery_surplus = battery_surplus * eeg_eur_per_kwh
    total = (
        savings_direct +
        revenue_grid +
        savings_battery_usage +
        savings_battery_surplus)

    return SavingsResult(
        battery_charge=battery_charge,
        battery_discharge=battery_discharge,
        battery_surplus=battery_surplus,
        grid_feedin=grid_feedin,
        savings_direct=savings_direct,
        revenue_grid=revenue_grid,
        savings_battery_usage=savings_battery_usage,
        savings_battery_surplus=savings_battery_surplus,
        total=total,
    )
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: class SavingsResult ---
@dataclass
class SavingsResult:
    """Structured result for photovoltaic savings calculations."""

    battery_charge: float
    battery_discharge: float
    battery_surplus: float
    grid_feedin: float
    savings_direct: float
    revenue_grid: float
    savings_battery_usage: float
    savings_battery_surplus: float
    total: float
# --- DEF BLOCK END ---
