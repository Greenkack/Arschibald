# Heat Pump System - Deep Analysis

## Document Overview

**Task:** 94. Heat Pump Deep Analysis  
**Date:** 2025-01-21  
**Status:** Complete  
**Requirements:** 1.3, 6.1

This document provides a comprehensive analysis of the heat pump calculation logic, heating cost calculations, dynamic tariff calculations, product database structure, configuration options, and efficiency calculation formulas extracted from the existing Streamlit codebase.

---

## Table of Contents

1. [Heat Pump Calculation Logic](#1-heat-pump-calculation-logic)
2. [Heating Cost Calculations](#2-heating-cost-calculations)
3. [Dynamic Tariff Calculations](#3-dynamic-tariff-calculations)
4. [Heat Pump Product Database Structure](#4-heat-pump-product-database-structure)
5. [Configuration Options](#5-configuration-options)
6. [Efficiency Calculation Formulas](#6-efficiency-calculation-formulas)
7. [Integration Points](#7-integration-points)
8. [Migration Recommendations](#8-migration-recommendations)

---

## 1. Heat Pump Calculation Logic

### 1.1 Core Calculation Functions

The heat pump system uses several core calculation functions located in `calculations_heatpump.py`:

#### Building Heat Load Calculation
```python
def calculate_building_heat_load(
    building_type: str, 
    living_area_m2: float, 
    insulation_quality: str
) -> float
```

**Purpose:** Calculates the maximum heating load of a building in kW.

**Parameters:**
- `building_type`: Building classification (e.g., "Neubau KFW40", "Altbau saniert")
- `living_area_m2`: Living area in square meters
- `insulation_quality`: Quality rating ("Gut", "Mittel", "Schlecht")

**Logic:**
- Uses base load values (W/m²) per building type:
  - Neubau KFW40: 40.0 W/m²
  - Neubau KFW55: 55.0 W/m²
  - Altbau saniert: 70.0 W/m²
  - Altbau unsaniert: 120.0 W/m²
- Applies insulation factor:
  - Gut: 0.9
  - Mittel: 1.0
  - Schlecht: 1.2
- Formula: `heat_load_kw = (living_area_m2 * base_w_m2 * factor) / 1000`


#### Heat Pump Recommendation
```python
def recommend_heat_pump(
    heat_load_kw: float,
    available_pumps: list[dict]
) -> dict
```

**Purpose:** Recommends the smallest suitable heat pump from available models.

**Logic:**
- Filters pumps where `heating_output_kw >= heat_load_kw`
- Sorts by heating output and selects the smallest suitable model
- Returns pump data or None if no suitable pump found

#### Annual Energy Consumption
```python
def calculate_annual_energy_consumption(
    heat_load_kw: float,
    scop: float,
    heating_hours: int = 1800
) -> float
```

**Purpose:** Calculates annual electricity consumption of the heat pump.

**Formula:**
```
annual_heat_demand_kwh = heat_load_kw * heating_hours
annual_electricity_consumption_kwh = annual_heat_demand_kwh / scop
```

**Default Values:**
- `heating_hours`: 1800 (typical full-load hours per year)
- `scop`: Seasonal Coefficient of Performance (typically 3.5-5.5)

### 1.2 Advanced Heat Load Calculations

#### Heat Load with Climate Zone
```python
def calculate_heat_load_with_climate_zone(
    building_type: str,
    living_area_m2: float,
    climate_zone: str = "Gemäßigt",
    insulation_quality: str = "Mittel",
    persons: int = None
) -> dict[str, Any]
```

**Climate Factors:**
- Kalt (Cold): 1.2 (e.g., mountain regions)
- Gemäßigt (Moderate): 1.0 (standard German climate)
- Mild: 0.8 (e.g., coastal regions)

**Returns:**
- `heating_load_kw`: Space heating load
- `dhw_load_kw`: Domestic hot water load
- `total_load_kw`: Combined load
- `annual_heating_demand_kwh`: Annual heating energy
- `annual_dhw_demand_kwh`: Annual DHW energy
- `annual_total_demand_kwh`: Total annual energy


#### Domestic Hot Water Demand
```python
def calculate_domestic_hot_water_demand(
    living_area_m2: float,
    persons: int = None,
    daily_usage_liters_per_person: float = 50.0
) -> dict[str, float]
```

**Calculation Logic:**
- Estimates persons if not provided: `persons = max(1, round(living_area_m2 / 37.5))`
- Annual water consumption: `persons * daily_usage_liters_per_person * 365`
- Energy demand: `annual_water_liters * 0.052 kWh/L`
  - Based on heating water from 10°C to 55°C (45K temperature rise)
  - Specific heat capacity: 1.16 Wh/(L·K)

**Returns:**
- `annual_dhw_demand_kwh`: Annual DHW energy requirement
- `persons`: Number of persons
- `daily_liters`: Daily water consumption
- `dhw_load_kw`: Peak DHW load
- `dhw_percentage`: Typical percentage of total heat demand (15%)

### 1.3 Consumption-Based Estimation

#### Estimate Heat Demand from Consumption
```python
def estimate_annual_heat_demand_kwh_from_consumption(
    consumption: dict[str, float],
    heating_system: str,
    wood_ster_additional: float = 0.0,
    custom_efficiency: float | None = None
) -> float
```

**Energy Content Values:**
- Oil: 10.0 kWh/liter
- Gas: 1.0 kWh/kWh (billing value)
- Wood: 1400.0 kWh/ster (air-dried hardwood)

**System Efficiency Defaults:**
- Gas-Brennwert: 0.92
- Öl-Brennwert: 0.90
- Pellets: 0.80
- Fernwärme: 0.95
- Strom-Direktheizung: 1.00
- Alte Gasheizung: 0.80
- Alte Ölheizung: 0.78

**Formula:**
```
heat_from_oil = oil_l * 10.0 * efficiency_main
heat_from_gas = gas_kwh * efficiency_main
heat_from_wood = wood_ster * 1400.0 * 0.75
total_heat_demand = heat_from_oil + heat_from_gas + heat_from_wood
```


### 1.4 Radiator Compatibility Check

#### Required Flow Temperature
```python
def calculate_required_flow_temperature(
    heat_load_kw: float,
    radiator_area_m2: float = None,
    room_temperature_c: float = 20.0,
    original_flow_temp_c: float = 70.0,
    original_return_temp_c: float = 55.0,
    radiator_exponent: float = 1.3
) -> dict[str, Any]
```

**Radiator Power Formula:**
```
Q ~ (ΔT)^n
where ΔT = (T_flow + T_return)/2 - T_room
n = radiator_exponent (typically 1.3)
```

**Logic:**
1. Calculate original mean temperature and delta T
2. Estimate radiator area if not provided (k ≈ 10 W/(m²·K^n))
3. Calculate required delta T for new heat load
4. Determine flow and return temperatures (10K spread)

**Returns:**
- `required_flow_temp_c`: Required flow temperature
- `required_return_temp_c`: Required return temperature
- `radiator_area_m2`: Estimated or provided radiator area

#### Radiator Compatibility Assessment
```python
def check_radiator_compatibility(
    required_flow_temp_c: float,
    heatpump_max_temp_c: float = 70.0,
    optimal_temp_c: float = 55.0
) -> dict[str, Any]
```

**Compatibility Ratings:**

| Flow Temp | Rating | COP Impact | Recommendation |
|-----------|--------|------------|----------------|
| ≤55°C | Optimal | 0% | Ideal for heat pump, high COP |
| 55-60°C | Gut | 5% | Suitable, slight COP reduction |
| 60-65°C | Grenzwertig | 12% | Borderline, upgrade recommended |
| 65-70°C | Kritisch | 25% | Critical, upgrade strongly recommended |
| >70°C | Ungeeignet | 40%+ | Unsuitable, upgrade required |

**Returns:**
- `compatible`: Boolean compatibility flag
- `compatibility`: Rating string
- `cop_impact_percent`: COP reduction percentage
- `upgrade_needed`: Whether upgrade is recommended
- `upgrade_cost_estimate`: Estimated upgrade cost (€3000-€7000)


---

## 2. Heating Cost Calculations

### 2.1 CO2 Costs for Fossil Heating

```python
def calculate_co2_costs_fossil_heating(
    fuel_type: str,
    annual_consumption_kwh: float,
    co2_price_per_ton: float = 85.0,
    green_fuel_share: float = 0.0,
    year: int = 2025
) -> dict[str, Any]
```

**CO2 Emission Factors:**
- Heizöl (Heating Oil): 0.266 kg CO2/kWh
- Erdgas (Natural Gas): 0.201 kg CO2/kWh
- Flüssiggas (LPG): 0.234 kg CO2/kWh
- Kohle (Coal): 0.350 kg CO2/kWh

**GEG (Gebäudeenergiegesetz) Green Fuel Requirements:**
- 2029: 15% minimum green fuel share
- 2035: 30% minimum green fuel share
- 2040: 60% minimum green fuel share
- 2045: 100% minimum green fuel share

**Calculation:**
```
fossil_share = 1.0 - max(green_fuel_share, geg_min_share)
annual_co2_tons = (annual_consumption_kwh * co2_factor * fossil_share) / 1000
annual_co2_cost = annual_co2_tons * co2_price_per_ton
```

**CO2 Price Trajectory:**
- 2025: €55/ton
- 2030: €65/ton
- 2035: €75/ton
- 2040: €80/ton
- 2045: €85/ton
- Average 2025-2045: €85/ton

### 2.2 Green Fuel Premium Calculation

```python
def calculate_green_fuel_premium(
    fuel_type: str,
    kwh_consumed: float,
    green_share: float
) -> float
```

**Green Fuel Production Costs:**
- Industrial electricity price: €0.17/kWh
- Bio-Heizöl efficiency: 60% (40% energy loss)
- Bio-Methan efficiency: 40% (60% energy loss)

**Fossil Fuel Base Costs:**
- Heizöl: €0.095/kWh (~9.5 ct/kWh)
- Erdgas: €0.10/kWh (~10 ct/kWh)
- Flüssiggas: €0.12/kWh

**Formula:**
```
green_fuel_cost = electricity_price / efficiency
premium_per_kwh = green_fuel_cost - fossil_base_cost
total_premium = premium_per_kwh * green_share * kwh_consumed
```


### 2.3 BEG Subsidy Calculation

```python
def calculate_beg_subsidy(
    investment_cost_eur: float,
    replaces_gas_oil: bool = True,
    household_income_below_threshold: bool = False,
    max_eligible_cost: float = 60000.0
) -> dict[str, Any]
```

**BEG (Bundesförderung für effiziente Gebäude) Structure:**

**Base Subsidy:** 30% (since 2024, was 35% until 2023)

**Bonus Programs:**
- **Climate Speed Bonus:** 20% (replacing functional heating before mandate)
- **Income Bonus:** 30% (household income < €40,000)
- **Maximum Total:** 70% (all bonuses combined)

**Eligible Costs:**
- Maximum: €60,000 for single-family homes (2024)
- Maximum: €30,000 per unit for multi-family homes

**Calculation:**
```
eligible_cost = min(investment_cost, max_eligible_cost)
total_subsidy_percent = min(
    base_subsidy + speed_bonus + income_bonus,
    70
)
subsidy_amount = eligible_cost * (total_subsidy_percent / 100)
net_investment = investment_cost - subsidy_amount
```

**Returns:**
- `subsidy_amount_eur`: Total subsidy amount
- `net_investment_eur`: Investment after subsidy
- `total_subsidy_percent`: Combined subsidy percentage
- Individual bonus percentages

### 2.4 NPV (Net Present Value) Calculation

```python
def calculate_npv_20_years(
    investment_eur: float,
    annual_operating_cost_eur: float,
    annual_cost_increase_percent: float = 2.0,
    discount_rate_percent: float = 3.0,
    residual_value_eur: float = 0.0,
    years: int = 20
) -> dict[str, Any]
```

**Financial Parameters:**
- **Discount Rate:** 3% (nominal interest rate)
- **Cost Increase:** 2% annual (inflation + energy price increase)
- **Time Horizon:** 20 years (typical heat pump lifespan)

**NPV Formula:**
```
NPV = -investment + Σ(operating_cost_year_i / (1 + discount_rate)^i) + residual_value / (1 + discount_rate)^years
```

**Annuity Factor:**
```
ANF = (q^n * (q-1)) / (q^n - 1)
where q = 1 + discount_rate
```

**Annual Equivalent Cost:**
```
annual_equivalent_cost = |NPV| * ANF
```


### 2.5 Heat Pump Economics Calculation

```python
def calculate_heatpump_economics(
    heatpump_data: dict[str, Any],
    building_data: dict[str, Any] = None
) -> dict[str, Any]
```

**Input Parameters:**
- `heating_demand`: Annual heating demand (kWh/year, default: 15000)
- `heatpump_power`: Heat pump power (kW, default: 10.0)
- `cop`: Coefficient of Performance (default: 3.5)
- `electricity_price`: Electricity price (€/kWh, default: 0.30)
- `investment_cost`: Total investment (€, default: 15000)
- `alternative_fuel_price`: Alternative fuel price (€/kWh, default: 0.08)
- `alternative_efficiency`: Alternative system efficiency (default: 0.9)

**Calculation Steps:**

1. **Electricity Consumption:**
   ```
   electricity_consumption = heating_demand / cop
   ```

2. **Annual Costs:**
   ```
   annual_electricity_cost = electricity_consumption * electricity_price
   alternative_fuel_consumption = heating_demand / alternative_efficiency
   annual_alternative_cost = alternative_fuel_consumption * alternative_fuel_price
   ```

3. **Savings:**
   ```
   annual_savings = annual_alternative_cost - annual_electricity_cost
   ```

4. **Payback Period:**
   ```
   payback_period_years = investment_cost / annual_savings
   ```

5. **20-Year Balance:**
   ```
   total_savings_20y = annual_savings * 20 - investment_cost
   ```

**Economic Assessment:**
- **Wirtschaftlich (Economic):** Payback ≤ 15 years
- **Bedingt wirtschaftlich (Conditionally Economic):** Payback 15-25 years
- **Nicht wirtschaftlich (Not Economic):** Payback > 25 years


---

## 3. Dynamic Tariff Calculations

### 3.1 Dynamic Tariff Overview

The system supports advanced dynamic electricity tariff calculations for optimizing heat pump operation costs. Key modules:
- `heatpump_dynamic_tariff.py`: Core calculation logic
- `heatpump_dynamic_tariff_charts.py`: Visualization components

### 3.2 Dynamic Tariff Comparison

```python
def calculate_dynamic_tariff_comparison(
    annual_consumption_kwh: float,
    base_price_ct_per_kwh: float = 32.0,
    dynamic_avg_price_ct_per_kwh: float = 28.0,
    dynamic_peak_price_ct_per_kwh: float = 45.0,
    dynamic_valley_price_ct_per_kwh: float = 15.0,
    load_shifting_potential_percent: float = 40.0
) -> dict[str, Any]
```

**Tariff Types:**
1. **Fixed Tariff:** Constant price per kWh
2. **Dynamic Tariff:** Hourly variable pricing based on market conditions
3. **Time-of-Use (TOU):** Different prices for peak/off-peak periods

**Calculation Logic:**
```
# Fixed tariff cost
fixed_annual_cost = annual_consumption_kwh * (base_price_ct_per_kwh / 100)

# Dynamic tariff with load shifting
shiftable_load = annual_consumption_kwh * (load_shifting_potential_percent / 100)
non_shiftable_load = annual_consumption_kwh - shiftable_load

# Assume 60% of shiftable load moved to valley, 40% to average
valley_consumption = shiftable_load * 0.6
average_consumption = shiftable_load * 0.4 + non_shiftable_load

dynamic_annual_cost = (
    valley_consumption * (dynamic_valley_price_ct_per_kwh / 100) +
    average_consumption * (dynamic_avg_price_ct_per_kwh / 100)
)

annual_savings = fixed_annual_cost - dynamic_annual_cost
```

**Returns:**
- `fixed_annual_cost`: Cost with fixed tariff
- `dynamic_annual_cost`: Cost with dynamic tariff
- `annual_savings`: Savings from dynamic tariff
- `savings_percent`: Percentage savings
- `load_shifting_benefit`: Benefit from load shifting

### 3.3 Stromcloud (Electricity Cloud) Economics

```python
def calculate_stromcloud_economics(
    annual_consumption_kwh: float,
    pv_annual_production_kwh: float,
    self_consumption_rate: float = 0.35,
    grid_price_ct_per_kwh: float = 32.0,
    feed_in_tariff_ct_per_kwh: float = 8.0,
    cloud_monthly_fee_eur: float = 19.90,
    cloud_coverage_percent: float = 80.0
) -> dict[str, Any]
```

**Stromcloud Concept:**
- Virtual storage of excess PV production
- Use stored energy when PV production is insufficient
- Monthly fee for cloud service
- Typically covers 80% of consumption

**Calculation:**
```
# PV self-consumption
pv_self_consumed = pv_annual_production_kwh * self_consumption_rate
pv_to_grid = pv_annual_production_kwh - pv_self_consumed

# Without cloud
grid_purchase_without_cloud = annual_consumption_kwh - pv_self_consumed
cost_without_cloud = (
    grid_purchase_without_cloud * (grid_price_ct_per_kwh / 100) -
    pv_to_grid * (feed_in_tariff_ct_per_kwh / 100)
)

# With cloud
cloud_coverage_kwh = annual_consumption_kwh * (cloud_coverage_percent / 100)
remaining_grid_purchase = max(0, annual_consumption_kwh - pv_self_consumed - cloud_coverage_kwh)
cloud_annual_fee = cloud_monthly_fee_eur * 12

cost_with_cloud = (
    remaining_grid_purchase * (grid_price_ct_per_kwh / 100) +
    cloud_annual_fee
)

annual_savings = cost_without_cloud - cost_with_cloud
```


### 3.4 Energy Management System Simulation

```python
def simulate_energy_management_system(
    heatpump_power_kw: float,
    buffer_tank_liters: float,
    pv_power_kwp: float,
    battery_capacity_kwh: float = 0.0,
    optimization_strategy: str = "cost"
) -> dict[str, Any]
```

**Optimization Strategies:**
1. **Cost Optimization:** Minimize electricity costs
2. **Self-Consumption:** Maximize PV self-consumption
3. **Grid Services:** Participate in demand response programs
4. **Comfort:** Prioritize temperature stability

**Simulation Components:**
- Heat pump operation scheduling
- Buffer tank thermal storage
- PV production forecasting
- Battery storage management
- Grid interaction optimization

**Key Metrics:**
- `self_consumption_rate`: Percentage of PV used directly
- `autarky_rate`: Energy independence percentage
- `grid_interaction`: Import/export balance
- `cost_savings`: Financial benefit
- `co2_reduction`: Environmental impact

### 3.5 Smart Home Benefits

```python
def calculate_smart_home_benefits(
    annual_consumption_kwh: float,
    automation_level: str = "basic",
    has_battery: bool = False,
    has_ev_charger: bool = False
) -> dict[str, Any]
```

**Automation Levels:**
- **Basic:** Simple scheduling (5-10% savings)
- **Advanced:** Weather forecasting, price optimization (10-20% savings)
- **AI-Powered:** Machine learning, predictive control (15-30% savings)

**Smart Home Features:**
- Automated heat pump scheduling
- Dynamic load management
- Weather-based optimization
- Grid signal response
- Battery integration
- EV charging coordination

**Benefit Categories:**
- Energy cost savings
- Comfort improvement
- Grid stability contribution
- CO2 reduction
- System longevity


---

## 4. Heat Pump Product Database Structure

### 4.1 Database Schema

The heat pump product database is stored in `heatpump_products_database.py` with the following structure:

```python
HEATPUMP_PRODUCTS = {
    "Manufacturer": {
        "Type": [
            {
                "model": str,
                "heating_power_kw": list[float],
                "scop": float,
                "max_flow_temp": int,
                "price_range": str,
                "features": list[str],
                "refrigerant": str,
                "rating": float,
                "awards": list[str]
            }
        ]
    }
}
```

### 4.2 Manufacturers

**Supported Manufacturers:**
1. **Viessmann**
   - Premium brand
   - Wide range of models
   - R290 (Propane) refrigerant focus
   - Models: Vitocal 250-A, 200-A, 222-A, 150-A

2. **Buderus**
   - Bosch Group brand
   - Reliable mid-range options
   - Various refrigerants
   - Models: Logatherm series

3. **Vaillant**
   - Innovation leader
   - Smart home integration
   - Efficient models
   - Models: aroTHERM series

### 4.3 Heat Pump Types

**1. Luft-Wasser-Wärmepumpe (Air-to-Water Heat Pump)**
- Most common type
- Extracts heat from outdoor air
- Suitable for most applications
- Power range: 4-16 kW typical

**2. Sole-Wasser-Wärmepumpe (Brine-to-Water Heat Pump)**
- Uses ground source heat
- Higher efficiency (SCOP 4.5-5.5)
- Higher installation cost
- Requires ground collectors or boreholes

**3. Wasser-Wasser-Wärmepumpe (Water-to-Water Heat Pump)**
- Uses groundwater as heat source
- Highest efficiency (SCOP 5.0-6.0)
- Requires water rights and wells
- Limited availability

**4. Hybrid-Wärmepumpe (Hybrid Heat Pump)**
- Combines heat pump with gas/oil boiler
- Optimal for partial renovations
- Flexible operation modes
- Lower investment than full heat pump


### 4.4 Product Attributes

**Core Technical Specifications:**
- `model`: Model name/number
- `heating_power_kw`: Heating capacity at various conditions (list)
- `scop`: Seasonal Coefficient of Performance
- `max_flow_temp`: Maximum flow temperature (°C)
- `refrigerant`: Refrigerant type (R290, R32, R410A, etc.)

**Commercial Information:**
- `price_range`: Price category (€, €€, €€€)
- `rating`: Customer rating (0-5 stars)
- `awards`: Industry awards and certifications
- `features`: Special features list

**Example Product Entry:**
```python
{
    "model": "Vitocal 250-A",
    "heating_power_kw": [6.0, 8.0, 10.0, 12.0, 15.0],
    "scop": 4.6,
    "max_flow_temp": 70,
    "price_range": "€€€",
    "features": [
        "Smart Grid Ready",
        "Active Cooling",
        "Internet Gateway"
    ],
    "refrigerant": "R290 (Propan)",
    "rating": 4.8,
    "awards": [
        "Testsieger Stiftung Warentest 2024",
        "Öko-Test SEHR GUT"
    ]
}
```

### 4.5 Database Access Functions

```python
def get_heatpump_models(
    manufacturer: str = None,
    heatpump_type: str = None,
    min_power_kw: float = None,
    max_power_kw: float = None
) -> list[dict]
```

**Purpose:** Retrieve heat pump models with optional filtering

**Filters:**
- Manufacturer name
- Heat pump type
- Power range
- SCOP minimum
- Refrigerant type
- Price range

```python
def find_suitable_model(
    required_power_kw: float,
    max_flow_temp_required: int = 55,
    preferred_refrigerant: str = None
) -> dict
```

**Purpose:** Find the most suitable heat pump model for given requirements

**Selection Criteria:**
1. Heating power ≥ required power
2. Max flow temperature ≥ required temperature
3. Highest SCOP among suitable models
4. Preferred refrigerant if specified
5. Best price-performance ratio


---

## 5. Configuration Options

### 5.1 Building Configuration

**Building Type Options:**
- Neubau KfW40 (New building KfW40 standard)
- Neubau KfW55 (New building KfW55 standard)
- Neubau Standard (New building standard)
- Altbau saniert (Renovated old building)
- Altbau teilsaniert (Partially renovated old building)
- Altbau unsaniert (Unrenovated old building)

**Insulation Quality:**
- Sehr gut (Very good)
- Gut (Good)
- Mittel (Medium)
- Schlecht (Poor)
- Sehr schlecht (Very poor)

**Building Year Categories:**
- Nach 2020 (After 2020)
- 2010-2020
- 2000-2010
- 1990-2000
- 1980-1990
- 1970-1980
- Vor 1970 (Before 1970)

### 5.2 Heating System Configuration

**Current Heating Systems:**
- Gas-Brennwert (Gas condensing boiler)
- Öl-Brennwert (Oil condensing boiler)
- Pellets (Pellet heating)
- Fernwärme (District heating)
- Strom-Direktheizung (Electric direct heating)
- Alte Gasheizung (Old gas heating)
- Alte Ölheizung (Old oil heating)

**Heating System Temperatures:**
- Fußbodenheizung (35°C) - Floor heating
- Wandheizung (40°C) - Wall heating
- Radiatoren (55°C) - Modern radiators
- Alte Radiatoren (70°C) - Old radiators

**Hot Water Demand:**
- Niedrig (1-2 Personen) - Low (1-2 persons)
- Mittel (3-4 Personen) - Medium (3-4 persons)
- Hoch (5+ Personen) - High (5+ persons)

### 5.3 Climate Configuration

**Climate Zones:**
- Kalt (Cold) - Mountain regions, harsh winters
- Gemäßigt (Moderate) - Standard German climate
- Mild - Coastal regions, mild winters

**Temperature Parameters:**
- Desired room temperature: 18-24°C (default: 21°C)
- Heating days per year: 150-300 (default: 220)
- Outside design temperature: -20°C to -5°C (default: -12°C)
- Heating hours per year: 1200-2600 (default: 1800)


### 5.4 Economic Configuration

**Fuel Prices (from heating_costs_config.json):**
```json
{
    "fuel_prices": {
        "gas_cent_per_kwh": 12.0,
        "oil_cent_per_liter": 90.0,
        "wood_euro_per_ster": 80.0,
        "pellets_euro_per_ton": 350.0,
        "electricity_cent_per_kwh": 32.0
    }
}
```

**CO2 Factors:**
```json
{
    "co2_factors": {
        "oil_kg_per_liter": 2.66,
        "gas_g_per_kwh": 428,
        "electricity_g_per_kwh": 420,
        "pellets_kg_per_ton": 26,
        "co2_price_euro_per_ton": 55
    }
}
```

**Operating Costs:**
```json
{
    "operating_costs": {
        "gas": {
            "chimney_sweep": 120,
            "maintenance": 150,
            "repair": 200,
            "pump_power_kwh": 300
        },
        "oil": {
            "chimney_sweep": 120,
            "maintenance": 200,
            "repair": 250,
            "pump_power_kwh": 400
        },
        "pellets": {
            "chimney_sweep": 120,
            "maintenance": 300,
            "repair": 300,
            "pump_power_kwh": 500
        },
        "heatpump": {
            "chimney_sweep": 0,
            "maintenance": 150,
            "repair": 100,
            "pump_power_kwh": 0
        }
    }
}
```

### 5.5 Subsidy Configuration

**BEG Subsidy Parameters:**
- Base subsidy: 30%
- Climate speed bonus: 20%
- Income bonus: 30%
- Maximum total: 70%
- Maximum eligible cost: €60,000 (single-family)
- Income threshold: €40,000

**Additional Subsidies:**
- Regional programs (varies by state)
- Municipal programs
- KfW loans with favorable interest rates
- Tax deductions for energy-efficient renovations


---

## 6. Efficiency Calculation Formulas

### 6.1 SCOP (Seasonal Coefficient of Performance)

**Definition:** SCOP represents the average efficiency of a heat pump over an entire heating season.

**Formula:**
```
SCOP = Total Heat Output (kWh) / Total Electrical Input (kWh)
```

**Typical SCOP Values:**
- Air-to-Water: 3.5 - 4.8
- Brine-to-Water: 4.5 - 5.5
- Water-to-Water: 5.0 - 6.0

**Factors Affecting SCOP:**
1. **Outside Temperature:** Lower temperatures reduce efficiency
2. **Flow Temperature:** Higher flow temps reduce efficiency
3. **System Design:** Proper sizing and hydraulics
4. **Control Strategy:** Smart operation optimization
5. **Building Insulation:** Better insulation = higher SCOP

### 6.2 COP (Coefficient of Performance)

**Definition:** COP is the instantaneous efficiency at specific operating conditions.

**Formula:**
```
COP = Heat Output (kW) / Electrical Input (kW)
```

**Standard Test Conditions:**
- A2/W35: Outside air 2°C, Water 35°C (floor heating)
- A7/W35: Outside air 7°C, Water 35°C (optimal conditions)
- A-7/W55: Outside air -7°C, Water 55°C (radiators, cold weather)

**COP vs. Temperature Relationship:**
```
COP ≈ COP_nominal * (1 - k * (T_flow - T_outside) / T_nominal)
where k ≈ 0.02 (temperature sensitivity factor)
```

### 6.3 JAZ (Jahresarbeitszahl) - Annual Performance Factor

**Definition:** JAZ is the actual measured annual efficiency including all system losses.

**Formula:**
```
JAZ = Annual Heat Delivered (kWh) / Annual Electricity Consumed (kWh)
```

**JAZ vs. SCOP:**
- JAZ: Real-world measurement including all losses
- SCOP: Laboratory value under standardized conditions
- Typical: JAZ ≈ 0.85 * SCOP (15% real-world penalty)

**System Losses Affecting JAZ:**
1. Circulation pump energy
2. Control system energy
3. Defrost cycles
4. Hydraulic losses
5. Thermal losses in distribution
6. Suboptimal control


### 6.4 Heat Pump Sizing Formula

**Optimal Sizing:**
```
Required Heat Pump Power = (Heat Load + DHW Load) * Safety Factor
where Safety Factor = 1.1 - 1.2
```

**Bivalent Point Calculation:**
For hybrid systems, determine the temperature at which backup heating activates:
```
Bivalent Temperature = T_design + (T_room - T_design) * (P_hp / P_total)
where:
  T_design = Design outside temperature
  T_room = Desired room temperature
  P_hp = Heat pump power
  P_total = Total heating power required
```

### 6.5 Buffer Tank Sizing

**Minimum Buffer Volume:**
```
V_buffer (liters) = P_hp (kW) * 15-20 liters/kW
```

**Optimal Buffer Volume:**
```
V_buffer (liters) = (P_hp * t_min_runtime * 60) / (ΔT * ρ * c_p)
where:
  t_min_runtime = Minimum runtime (minutes, typically 10-15)
  ΔT = Temperature difference (K, typically 5-10)
  ρ = Water density (kg/L, ≈ 1.0)
  c_p = Specific heat capacity (kWh/(kg·K), ≈ 0.00116)
```

### 6.6 Electricity Cost Calculation

**Annual Electricity Cost:**
```
Annual Cost = (Heating Demand / SCOP) * Electricity Price
```

**With Dynamic Tariff:**
```
Annual Cost = Σ(Hourly Consumption * Hourly Price)
where hourly consumption depends on:
  - Heat demand profile
  - Buffer tank capacity
  - Load shifting strategy
```

**Comparison with Fossil Fuel:**
```
Cost Ratio = (Electricity Price / SCOP) / (Fuel Price * Efficiency_fossil)

If Cost Ratio < 1: Heat pump is cheaper
If Cost Ratio > 1: Fossil fuel is cheaper
```

**Break-Even Electricity Price:**
```
P_elec_breakeven = Fuel Price * Efficiency_fossil * SCOP
```


---

## 7. Integration Points

### 7.1 UI Integration (heatpump_ui.py)

**Main Rendering Function:**
```python
def render_heatpump_analysis(
    texts: dict[str, str],
    project_data: dict[str, Any] = None
)
```

**Tab Structure:**
1. 🏠 Gebäudeanalyse (Building Analysis)
2. 🔥 Wärmepumpen-Auswahl (Heat Pump Selection)
3. 🌡️ Radiator-Check
4. 💰 Wirtschaftlichkeit (Economics)
5. ☀️ PV-Integration
6. 📊 Erweiterte Analyse (Advanced Analysis)
7. 🏗️ Renovierungs-Planer (Renovation Planner)
8. ⚙️ Optimierung (Optimization)
9. 💵 Förderung & CO2 (Subsidies & CO2)
10. 📈 ROI & Benchmarking
11. ⚡ Dynamischer Stromtarif (Dynamic Tariff)
12. 📋 Ergebnisse (Results)

**Session State Management:**
- `building_data`: Building analysis results
- `heatpump_data`: Selected heat pump information
- `radiator_data`: Radiator compatibility results
- `economics_data`: Economic analysis results
- `pv_integration_data`: PV integration results

### 7.2 Pricing Integration (heatpump_pricing.py)

**Enhanced Pricing Engine:**
```python
class HeatPumpPricingEngine(PricingEngine):
    def calculate_heatpump_system_price(
        self, 
        system_config: dict[str, Any]
    ) -> PricingResult
```

**Component Categories:**
- `heatpump`: Main heat pump unit
- `storage`: Buffer tanks, hot water storage
- `services`: Installation, planning, commissioning
- `accessories`: Pipes, valves, controls
- `controls`: Thermostats, sensors, smart controls

**Pricing Adjustments:**
- Installation complexity multiplier (1.0 - 1.3)
- Efficiency premium (COP ≥ 4.5: +5%)
- Natural refrigerant premium (R290: +3%)
- BEG eligibility tracking


### 7.3 Database Integration

**Product Database Connection:**
```python
from product_db import (
    get_product_by_id,
    get_product_by_model_name,
    list_products,
    calculate_selling_price
)
```

**Heat Pump Product Queries:**
```python
# Get all heat pumps
heatpumps = list_products(category="waermepumpe")

# Get specific model
model = get_product_by_model_name("Vitocal 250-A")

# Calculate price with margins
price_result = calculate_selling_price(product_id)
```

**Database Schema Integration:**
- Products table: Heat pump models
- Pricing table: Dynamic pricing rules
- Projects table: Heat pump projects
- Calculations table: Saved calculations

### 7.4 PV Integration

**Combined PV + Heat Pump Analysis:**
```python
def calculate_pv_self_consumption_heatpump(
    pv_annual_production_kwh: float,
    heatpump_annual_consumption_kwh: float,
    base_consumption_kwh: float,
    battery_capacity_kwh: float = 0.0
) -> dict[str, Any]
```

**Integration Benefits:**
- Increased PV self-consumption
- Reduced grid electricity purchase
- Lower operating costs
- Higher system autarky
- Better ROI for both systems

**Optimization Strategies:**
- Heat pump operation during PV production hours
- Buffer tank as thermal storage
- Battery storage for evening/night operation
- Smart grid integration

### 7.5 Chart Integration (heatpump_dynamic_tariff_charts.py)

**Shadcn UI Theme System:**
```python
def get_chart_theme() -> dict
```

**Chart Types:**
1. **Hourly Price Chart:** Dynamic tariff visualization
2. **Annual Cost Chart:** Cost comparison over time
3. **Stromcloud Waterfall:** Financial breakdown
4. **Load Shifting Heatmap:** Optimization potential

**Theme Features:**
- Dark/Light mode support
- Shadcn UI color palette
- Gradient fills
- Rounded corners
- Responsive design
- German number formatting


---

## 8. Migration Recommendations

### 8.1 Backend Service Architecture

**Recommended Service Structure:**
```
backend/services/
├── heatpump_service.py          # Main heat pump service
├── heatpump_calculation_service.py  # Calculation logic
├── heatpump_pricing_service.py      # Pricing engine
├── heatpump_product_service.py      # Product database
└── heatpump_tariff_service.py       # Dynamic tariff
```

**API Endpoint Structure:**
```
POST   /api/v1/heatpump/calculate-heat-load
POST   /api/v1/heatpump/recommend-model
POST   /api/v1/heatpump/check-radiator-compatibility
POST   /api/v1/heatpump/calculate-economics
POST   /api/v1/heatpump/calculate-subsidies
GET    /api/v1/heatpump/products
GET    /api/v1/heatpump/products/{id}
POST   /api/v1/heatpump/dynamic-tariff/compare
POST   /api/v1/heatpump/dynamic-tariff/simulate
```

### 8.2 Data Model Migration

**Core Data Models:**

```typescript
// Heat Pump Calculation Request
interface HeatPumpCalculationRequest {
  buildingType: string;
  livingAreaM2: number;
  insulationQuality: string;
  climateZone?: string;
  currentHeatingSystem: string;
  consumption?: {
    oilLiters?: number;
    gasKwh?: number;
    woodSter?: number;
  };
  heatingHours?: number;
  customEfficiency?: number;
}

// Heat Pump Calculation Result
interface HeatPumpCalculationResult {
  heatLoadKw: number;
  dhwLoadKw: number;
  totalLoadKw: number;
  annualHeatingDemandKwh: number;
  annualDhwDemandKwh: number;
  annualTotalDemandKwh: number;
  recommendedPowerKw: number;
  climateZone: string;
  persons: number;
}

// Heat Pump Product
interface HeatPumpProduct {
  id: number;
  manufacturer: string;
  model: string;
  type: string;
  heatingPowerKw: number[];
  scop: number;
  maxFlowTemp: number;
  refrigerant: string;
  priceRange: string;
  features: string[];
  rating: number;
  awards: string[];
}

// Economics Result
interface HeatPumpEconomics {
  heatingDemandKwh: number;
  electricityConsumptionKwh: number;
  annualElectricityCost: number;
  annualAlternativeCost: number;
  annualSavings: number;
  paybackPeriodYears: number;
  totalSavings20y: number;
  investmentCost: number;
  cop: number;
  recommendation: string;
}
```


### 8.3 Frontend Component Structure

**Recommended React Component Hierarchy:**

```
frontend/src/components/heatpump/
├── HeatPumpCalculator.tsx       # Main calculator component
├── BuildingAnalysis.tsx         # Building input form
├── HeatPumpSelection.tsx        # Product selection
├── RadiatorCheck.tsx            # Radiator compatibility
├── EconomicsAnalysis.tsx        # Economic calculations
├── PVIntegration.tsx            # PV + HP integration
├── DynamicTariff.tsx            # Dynamic tariff analysis
├── SubsidyCalculator.tsx        # BEG subsidy calculator
└── ResultsSummary.tsx           # Results display
```

**State Management (Zustand):**
```typescript
interface HeatPumpStore {
  // Building data
  buildingData: HeatPumpCalculationResult | null;
  setBuildingData: (data: HeatPumpCalculationResult) => void;
  
  // Selected heat pump
  selectedHeatPump: HeatPumpProduct | null;
  setSelectedHeatPump: (pump: HeatPumpProduct) => void;
  
  // Economics
  economicsData: HeatPumpEconomics | null;
  setEconomicsData: (data: HeatPumpEconomics) => void;
  
  // Radiator compatibility
  radiatorData: RadiatorCompatibility | null;
  setRadiatorData: (data: RadiatorCompatibility) => void;
  
  // Actions
  calculateHeatLoad: (request: HeatPumpCalculationRequest) => Promise<void>;
  recommendHeatPump: (heatLoadKw: number) => Promise<void>;
  calculateEconomics: () => Promise<void>;
}
```

### 8.4 Key Migration Challenges

**1. Complex Calculation Logic**
- **Challenge:** Multiple interdependent calculations
- **Solution:** Create calculation service with clear interfaces
- **Approach:** Wrap existing Python functions, maintain logic

**2. Product Database**
- **Challenge:** Large product database (25,000+ lines)
- **Solution:** Migrate to proper database with API
- **Approach:** Import to PostgreSQL/SQLite, create REST API

**3. Dynamic Tariff Simulation**
- **Challenge:** Time-series calculations and optimization
- **Solution:** Backend service with caching
- **Approach:** Pre-calculate common scenarios, cache results

**4. Chart Visualization**
- **Challenge:** Complex Plotly charts with Shadcn UI theme
- **Solution:** Use Recharts with custom theme
- **Approach:** Recreate chart logic in TypeScript

**5. German Number Formatting**
- **Challenge:** Consistent formatting across all components
- **Solution:** Global formatting utility
- **Approach:** Create `formatGermanNumber()` utility function


### 8.5 Testing Strategy

**Unit Tests:**
```python
# Backend calculation tests
def test_calculate_building_heat_load():
    result = calculate_building_heat_load(
        building_type="Neubau KFW40",
        living_area_m2=150,
        insulation_quality="Gut"
    )
    assert result > 0
    assert result < 10  # Reasonable range for KFW40

def test_calculate_domestic_hot_water_demand():
    result = calculate_domestic_hot_water_demand(
        living_area_m2=150,
        persons=4
    )
    assert result['annual_dhw_demand_kwh'] > 0
    assert result['persons'] == 4
```

**Integration Tests:**
```typescript
// Frontend integration tests
describe('HeatPumpCalculator', () => {
  it('should calculate heat load and recommend pump', async () => {
    const request: HeatPumpCalculationRequest = {
      buildingType: 'Neubau KFW40',
      livingAreaM2: 150,
      insulationQuality: 'Gut',
      currentHeatingSystem: 'Gas-Brennwert'
    };
    
    const result = await calculateHeatLoad(request);
    expect(result.heatLoadKw).toBeGreaterThan(0);
    
    const pump = await recommendHeatPump(result.totalLoadKw);
    expect(pump).toBeDefined();
    expect(pump.heatingPowerKw).toContain(
      expect.any(Number).toBeGreaterThanOrEqual(result.totalLoadKw)
    );
  });
});
```

**Property-Based Tests:**
```python
from hypothesis import given, strategies as st

@given(
    living_area=st.floats(min_value=30, max_value=1000),
    scop=st.floats(min_value=2.0, max_value=6.0)
)
def test_annual_energy_consumption_properties(living_area, scop):
    """Property: Electricity consumption should decrease as SCOP increases"""
    heat_load = calculate_building_heat_load(
        "Neubau KFW40", living_area, "Gut"
    )
    
    consumption_low_scop = calculate_annual_energy_consumption(
        heat_load, scop=3.0
    )
    consumption_high_scop = calculate_annual_energy_consumption(
        heat_load, scop=5.0
    )
    
    assert consumption_high_scop < consumption_low_scop
```


### 8.6 Performance Optimization

**Backend Optimization:**
1. **Caching Strategy:**
   - Cache product database queries
   - Cache common calculation results
   - Use Redis for distributed caching

2. **Database Optimization:**
   - Index heat pump products by power range
   - Denormalize frequently accessed data
   - Use database views for complex queries

3. **Calculation Optimization:**
   - Pre-calculate common scenarios
   - Use lookup tables for efficiency curves
   - Implement calculation result caching

**Frontend Optimization:**
1. **Code Splitting:**
   - Lazy load heat pump calculator
   - Split product database component
   - Separate chart libraries

2. **Data Management:**
   - Implement virtual scrolling for product lists
   - Paginate large result sets
   - Use React Query for data caching

3. **Chart Performance:**
   - Limit data points in charts
   - Use canvas rendering for large datasets
   - Implement chart data decimation

### 8.7 Security Considerations

**API Security:**
- Rate limiting on calculation endpoints
- Input validation for all parameters
- Sanitize user inputs
- Implement request throttling

**Data Protection:**
- Encrypt sensitive project data
- Implement GDPR-compliant data handling
- Secure storage of calculation results
- User data anonymization options

**Authentication:**
- JWT-based authentication
- Role-based access control
- Secure session management
- API key management for external integrations


---

## Summary

This deep analysis document provides a comprehensive overview of the heat pump calculation system, covering:

1. **Calculation Logic:** All core formulas and algorithms for heat load, efficiency, and economics
2. **Heating Costs:** CO2 costs, green fuel premiums, BEG subsidies, and NPV calculations
3. **Dynamic Tariffs:** Advanced tariff optimization and energy management
4. **Product Database:** Structure and access patterns for 25,000+ product entries
5. **Configuration:** All user-configurable options and parameters
6. **Efficiency Formulas:** SCOP, COP, JAZ calculations and relationships
7. **Integration Points:** UI, pricing, database, and PV integration
8. **Migration Strategy:** Recommended architecture, data models, and testing approach

### Key Takeaways for Migration:

1. **Preserve Calculation Logic:** The Python calculation functions are well-tested and should be wrapped, not rewritten
2. **Service-Oriented Architecture:** Create dedicated services for calculations, pricing, products, and tariffs
3. **Database Migration:** Move product database to proper RDBMS with API access
4. **Frontend Components:** Build modular React components matching the existing tab structure
5. **German Formatting:** Implement consistent number formatting across all components
6. **Testing:** Comprehensive unit, integration, and property-based tests
7. **Performance:** Implement caching, optimization, and lazy loading strategies
8. **Security:** Ensure proper authentication, validation, and data protection

### Next Steps:

1. Review this analysis with the development team
2. Create detailed API specifications based on existing functions
3. Design database schema for heat pump products
4. Implement backend services with calculation wrappers
5. Build frontend components with React + TypeScript
6. Develop comprehensive test suite
7. Perform migration validation and user acceptance testing

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-21  
**Author:** AI Analysis System  
**Status:** Complete
