# Solar Grid Integration Guide

## Overview

The Grid Integration module provides comprehensive analysis and calculations for connecting solar PV systems to the electrical grid. It covers financial analysis, technical requirements, power quality, grid stability, and smart grid integration.

## Features

### 1. Feed-in Tariff Calculations

Calculate financial benefits from feed-in tariffs over the system lifetime.

**Key Metrics:**
- Annual and lifetime feed-in revenue
- Self-consumption savings
- Total benefits with degradation
- Payback period analysis

**Example:**
```python
from backend.services.grid_integration_service import GridIntegrationService
from backend.models.grid_schemas import FeedInTariffRequest

service = GridIntegrationService()

request = FeedInTariffRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    self_consumption_rate=0.3,
    feed_in_tariff_per_kwh=0.10,
    electricity_price_per_kwh=0.30,
    contract_duration_years=20,
    degradation_rate=0.005
)

result = service.calculate_feed_in_tariff(request)
print(f"Annual benefit: €{result.total_annual_benefit}")
print(f"Lifetime benefit: €{result.total_lifetime_benefit}")
print(f"Payback period: {result.payback_period_years} years")
```

### 2. Net Metering Analysis

Analyze net metering benefits with monthly credit flow tracking.

**Key Features:**
- Monthly production vs consumption analysis
- Credit accumulation and rollover
- Self-sufficiency rate calculation
- Grid independence metrics
- Optimal system sizing

**Example:**
```python
from backend.models.grid_schemas import NetMeteringRequest

# Monthly data (12 months)
monthly_production = [800, 900, 1100, 1200, 1300, 1400, 
                      1400, 1300, 1100, 900, 800, 700]
monthly_consumption = [1000, 950, 900, 850, 800, 750,
                       750, 800, 850, 900, 950, 1000]

request = NetMeteringRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    annual_consumption_kwh=10200,
    electricity_price_per_kwh=0.30,
    net_metering_credit_per_kwh=0.27,
    monthly_production=monthly_production,
    monthly_consumption=monthly_consumption,
    rollover_allowed=True,
    max_rollover_months=12
)

result = service.analyze_net_metering(request)
print(f"Self-sufficiency: {result.self_sufficiency_rate * 100:.1f}%")
print(f"Grid independence: {result.grid_independence_rate * 100:.1f}%")
print(f"Annual savings: €{result.annual_net_savings}")
```

### 3. Grid Connection Requirements

Calculate technical requirements and costs for grid connection.

**Calculations Include:**
- Cable sizing based on current and distance
- Voltage drop analysis
- Protection device requirements
- Connection cost estimation
- Approval timeline

**Example:**
```python
from backend.models.grid_schemas import GridConnectionRequest, GridConnectionType

request = GridConnectionRequest(
    system_size_kwp=15.0,
    connection_type=GridConnectionType.THREE_PHASE,
    voltage_level=400,
    distance_to_grid_m=100,
    inverter_power_kw=15.0,
    location="Commercial Area",
    building_type="commercial"
)

result = service.calculate_grid_connection_requirements(request)
print(f"Cable size required: {result.required_cable_size_mm2} mm²")
print(f"Estimated cost: €{result.estimated_connection_cost}")
print(f"Voltage drop: {result.voltage_drop_percent}%")
print(f"Approval time: {result.estimated_approval_time_days} days")
```

### 4. Power Quality Analysis

Assess compliance with power quality standards.

**Standards Supported:**
- IEEE 1547
- EN 50160
- VDE-AR-N 4105
- IEC 61727

**Metrics Analyzed:**
- Voltage regulation
- Frequency deviation
- Power factor
- Total Harmonic Distortion (THD)
- Individual harmonics
- Flicker severity
- DC injection

**Example:**
```python
from backend.models.grid_schemas import PowerQualityRequest, PowerQualityStandard

request = PowerQualityRequest(
    system_size_kwp=10.0,
    inverter_specs={
        "rated_power_kw": 10.0,
        "efficiency": 0.97,
        "power_factor": 0.99,
        "thd": 0.03
    },
    grid_voltage=400,
    grid_frequency=50.0,
    standard=PowerQualityStandard.VDE_AR_N_4105
)

result = service.analyze_power_quality(request)
print(f"Compliant: {result.compliant}")
print(f"Power factor: {result.power_factor}")
print(f"THD: {result.total_harmonic_distortion_percent}%")
if result.compliance_issues:
    print("Issues:", result.compliance_issues)
```

### 5. Grid Stability Calculations

Analyze impact on grid stability and available support services.

**Key Metrics:**
- Short Circuit Ratio (SCR)
- Voltage stability margin
- Frequency stability margin
- Reactive power capability
- Overall stability index

**Grid Support Services:**
- Reactive power support (Q/V control)
- Voltage regulation
- Frequency response
- Fast fault ride-through

**Example:**
```python
from backend.models.grid_schemas import GridStabilityRequest

request = GridStabilityRequest(
    system_size_kwp=10.0,
    grid_short_circuit_power_mva=50.0,
    grid_impedance_ohm=0.1,
    inverter_response_time_ms=50,
    enable_reactive_power_support=True,
    enable_voltage_regulation=True
)

result = service.calculate_grid_stability(request)
print(f"Stability index: {result.stability_index}")
print(f"SCR: {result.short_circuit_ratio}")
print(f"Grid services: {result.grid_support_services}")
if result.stability_concerns:
    print("Concerns:", result.stability_concerns)
```

### 6. Smart Grid Integration

Evaluate potential for smart grid services and revenue streams.

**Available Services:**
- Demand response
- Frequency regulation
- Voltage support
- Time-of-use optimization
- Peak shaving

**Revenue Streams:**
- Demand response payments
- Frequency regulation services
- Voltage support compensation
- TOU arbitrage
- Peak shaving benefits

**Example:**
```python
from backend.models.grid_schemas import SmartGridRequest

request = SmartGridRequest(
    system_size_kwp=10.0,
    battery_capacity_kwh=10.0,
    enable_demand_response=True,
    enable_frequency_regulation=True,
    enable_voltage_support=True,
    time_of_use_tariff={
        "peak": 0.40,
        "off_peak": 0.15,
        "shoulder": 0.25
    }
)

result = service.analyze_smart_grid_integration(request)
print(f"Smart grid ready: {result.smart_grid_ready}")
print(f"Annual revenue: €{result.annual_grid_services_revenue}")
print(f"Services: {result.available_services}")
print(f"Payback: {result.payback_period_years} years")
```

### 7. Comprehensive Grid Analysis

Perform complete analysis of all grid integration aspects.

**Includes:**
- Feed-in tariff analysis
- Net metering analysis (if applicable)
- Connection requirements
- Power quality assessment
- Grid stability analysis
- Smart grid potential (if enabled)

**Example:**
```python
from backend.models.grid_schemas import (
    GridIntegrationAnalysisRequest,
    GridConnectionType,
    MeteringType
)

request = GridIntegrationAnalysisRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    annual_consumption_kwh=10000,
    location="Berlin, Germany",
    connection_type=GridConnectionType.THREE_PHASE,
    metering_type=MeteringType.NET_METERING,
    feed_in_tariff_per_kwh=0.10,
    electricity_price_per_kwh=0.30,
    grid_voltage=400,
    distance_to_grid_m=50,
    battery_capacity_kwh=10.0,
    enable_smart_grid=True
)

result = service.comprehensive_grid_analysis(request)
print(f"Total annual benefit: €{result.total_annual_benefit}")
print(f"Lifetime benefit: €{result.total_lifetime_benefit}")
print(f"Compliance: {result.compliance_status}")
print(f"Feasibility score: {result.overall_feasibility_score}/100")
print(f"Recommended config: {result.recommended_configuration}")
```

## API Endpoints

### POST /api/v1/grid/feed-in-tariff
Calculate feed-in tariff benefits.

### POST /api/v1/grid/net-metering
Analyze net metering benefits.

### POST /api/v1/grid/connection-requirements
Calculate grid connection requirements.

### POST /api/v1/grid/power-quality
Analyze power quality compliance.

### POST /api/v1/grid/grid-stability
Calculate grid stability metrics.

### POST /api/v1/grid/smart-grid
Analyze smart grid integration potential.

### POST /api/v1/grid/comprehensive-analysis
Perform comprehensive grid integration analysis.

## German Number Formatting

All financial values are formatted according to German standards:
- Currency: 16.999,00 €
- Percentages: 85,5%
- Energy: 12.500 kWh

## Best Practices

1. **Feed-in Tariff Analysis:**
   - Always include system degradation (typically 0.5% per year)
   - Consider contract duration carefully
   - Compare with self-consumption savings

2. **Net Metering:**
   - Use actual monthly production/consumption data when available
   - Consider seasonal variations
   - Check rollover policies in your region

3. **Grid Connection:**
   - Verify local grid capacity before sizing
   - Consider future expansion needs
   - Factor in approval timelines

4. **Power Quality:**
   - Use inverter specifications from manufacturer
   - Check compliance with local standards
   - Consider harmonic filters if needed

5. **Grid Stability:**
   - Assess grid strength (SCR) before installation
   - Enable grid support services when possible
   - Monitor stability concerns

6. **Smart Grid:**
   - Evaluate battery storage benefits
   - Consider time-of-use tariffs
   - Calculate payback period for upgrades

## Troubleshooting

### High Voltage Drop
- Increase cable size
- Reduce distance to grid
- Consider three-phase connection

### Power Quality Issues
- Check inverter specifications
- Install harmonic filters
- Enable reactive power compensation

### Low Stability Index
- Assess grid strength
- Enable grid support services
- Consider battery storage

### Low Smart Grid Revenue
- Add battery storage
- Enable more services
- Switch to TOU tariff

## References

- IEEE 1547: Standard for Interconnecting Distributed Resources
- VDE-AR-N 4105: German grid connection standard
- EN 50160: Voltage characteristics of electricity supplied by public distribution networks
- IEC 61727: Photovoltaic (PV) systems - Characteristics of the utility interface
