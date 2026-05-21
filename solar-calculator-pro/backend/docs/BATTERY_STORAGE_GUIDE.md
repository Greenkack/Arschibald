# Battery Storage Service Guide

## Overview

The Battery Storage Service provides comprehensive calculations and analysis for solar battery storage systems, including sizing, ROI analysis, discharge strategies, grid independence metrics, lifecycle analysis, and monitoring integration.

## Features

### 1. Battery Sizing Calculations
- Optimal battery capacity based on consumption patterns
- Backup power requirements
- Self-sufficiency targets
- Performance predictions

### 2. ROI Analysis
- Payback period calculation
- Net Present Value (NPV)
- Lifetime savings projections
- Cash flow analysis with degradation
- Savings breakdown

### 3. Discharge Strategies
- **Self-Consumption**: Maximize use of stored solar energy
- **Peak Shaving**: Reduce grid import during peak hours
- **Time-of-Use**: Optimize for variable electricity pricing
- **Backup**: Maintain high charge for emergency backup

### 4. Grid Independence
- Self-sufficiency rate calculation
- Grid dependency metrics
- Monthly and annual analysis
- Battery contribution tracking

### 5. Lifecycle Analysis
- Capacity degradation over time
- Replacement schedule
- Total cost of ownership
- Warranty tracking

### 6. Monitoring Integration
- Real-time data points
- Historical metrics
- Alert thresholds
- System-specific configurations

## API Endpoints

### Battery Sizing

```http
POST /api/v1/battery/sizing
```

**Request Body:**
```json
{
  "daily_consumption_kwh": 15.0,
  "pv_system_size_kwp": 10.0,
  "annual_production_kwh": 10000.0,
  "self_consumption_rate": 0.35,
  "grid_feed_in_tariff": 0.08,
  "electricity_price": 0.30,
  "backup_hours": 8,
  "target_self_sufficiency": 0.8
}
```

**Response:**
```json
{
  "recommended_capacity_kwh": 10.5,
  "selected_battery": "medium",
  "battery_specs": {
    "capacity_kwh": 10.0,
    "usable_capacity_kwh": 9.0,
    "max_charge_rate_kw": 5.0,
    "max_discharge_rate_kw": 5.0,
    "efficiency": 0.95,
    "depth_of_discharge": 0.9,
    "warranty_years": 10,
    "warranty_cycles": 6000,
    "cost_per_kwh": 750.0,
    "degradation_rate_per_year": 0.02
  },
  "performance": {
    "storable_energy_per_day_kwh": 8.5,
    "usable_energy_per_day_kwh": 8.08,
    "additional_self_consumption_kwh": 7.5,
    "new_self_consumption_rate_percent": 62.3,
    "improvement_percent": 27.3,
    "cycles_per_day": 0.94,
    "annual_cycles": 343
  },
  "sizing_rationale": {
    "daily_production_kwh": 27.4,
    "daily_consumption_kwh": 15.0,
    "daily_surplus_kwh": 17.8,
    "daily_deficit_kwh": 9.75,
    "backup_hours": 8,
    "target_self_sufficiency": 0.8
  }
}
```

### ROI Analysis

```http
POST /api/v1/battery/roi
```

**Request Body:**
```json
{
  "battery_capacity_kwh": 10.0,
  "daily_consumption_kwh": 15.0,
  "pv_system_size_kwp": 10.0,
  "annual_production_kwh": 10000.0,
  "self_consumption_rate": 0.35,
  "grid_feed_in_tariff": 0.08,
  "electricity_price": 0.30,
  "analysis_years": 20
}
```

**Response:**
```json
{
  "initial_investment": 7500.00,
  "annual_savings_year_1": 650.00,
  "lifetime_savings": 11234.56,
  "simple_payback_years": 11.5,
  "payback_year": 12,
  "npv": 2345.67,
  "roi_percent": 49.8,
  "cash_flow_analysis": [
    {
      "year": 1,
      "annual_savings": 650.00,
      "cumulative_savings": 650.00,
      "capacity_remaining": 98.0
    }
  ],
  "savings_breakdown": {
    "grid_purchase_savings": 550.00,
    "arbitrage_savings": 100.00,
    "total_annual": 650.00
  }
}
```

### Discharge Strategy

```http
POST /api/v1/battery/discharge-strategy
```

**Request Body:**
```json
{
  "strategy_type": "self_consumption",
  "battery_capacity_kwh": 10.0,
  "hourly_production": [0, 0, 0, 0, 0, 0.5, 2, 4, 6, 8, 9, 10, 9, 8, 6, 4, 2, 0.5, 0, 0, 0, 0, 0, 0],
  "hourly_consumption": [1, 1, 1, 1, 1, 2, 3, 2, 1.5, 1, 1, 1.5, 2, 1.5, 1, 1.5, 2, 3, 4, 3, 2, 1.5, 1, 1],
  "peak_hours": [17, 18, 19, 20],
  "min_soc": 0.2,
  "max_soc": 1.0,
  "priority": "self_consumption"
}
```

**Response:**
```json
{
  "strategy_type": "self_consumption",
  "schedule": [
    {
      "hour": 0,
      "production_kw": 0,
      "consumption_kw": 1,
      "action": "discharge",
      "amount_kw": 1.0,
      "soc_percent": 49.0,
      "grid_import_kw": 0,
      "grid_export_kw": 0
    }
  ],
  "performance": {
    "total_charged_kwh": 45.5,
    "total_discharged_kwh": 28.0,
    "effective_discharged_kwh": 26.6,
    "round_trip_efficiency_percent": 95.0,
    "grid_import_kwh": 5.5,
    "grid_export_kwh": 12.0,
    "self_consumption_from_battery_kwh": 26.6,
    "final_soc_percent": 65.5
  }
}
```

### Grid Independence

```http
POST /api/v1/battery/grid-independence
```

**Request Body:**
```json
{
  "battery_capacity_kwh": 10.0,
  "daily_consumption_kwh": 15.0,
  "pv_system_size_kwp": 10.0,
  "annual_production_kwh": 10000.0,
  "self_consumption_rate": 0.35,
  "monthly_production": [600, 700, 850, 950, 1100, 1150, 1200, 1150, 1000, 800, 650, 550],
  "monthly_consumption": [450, 450, 450, 450, 450, 450, 450, 450, 450, 450, 450, 450]
}
```

**Response:**
```json
{
  "monthly_analysis": [
    {
      "month": 1,
      "production_kwh": 600,
      "consumption_kwh": 450,
      "direct_self_consumption_kwh": 450,
      "battery_contribution_kwh": 0,
      "grid_import_kwh": 0,
      "self_sufficiency_percent": 100.0
    }
  ],
  "annual_metrics": {
    "self_sufficiency_percent": 85.5,
    "grid_dependency_percent": 14.5,
    "battery_contribution_percent": 25.3,
    "total_self_consumption_kwh": 4617.5,
    "total_grid_import_kwh": 782.5,
    "total_battery_contribution_kwh": 1367.5
  },
  "comparison": {
    "without_battery_self_sufficiency_percent": 60.2,
    "with_battery_self_sufficiency_percent": 85.5,
    "improvement_percent": 25.3
  }
}
```

### Lifecycle Analysis

```http
POST /api/v1/battery/lifecycle
```

**Request Body:**
```json
{
  "battery_capacity_kwh": 10.0,
  "daily_cycles": 1.0,
  "analysis_years": 20
}
```

**Response:**
```json
{
  "battery_specs": { },
  "lifecycle_parameters": {
    "daily_cycles": 1.0,
    "cycles_per_year": 365,
    "total_cycles": 7300,
    "warranty_cycles": 6000,
    "warranty_years": 10
  },
  "capacity_timeline": [
    {
      "year": 0,
      "capacity_kwh": 10.0,
      "capacity_percent": 100.0,
      "cycles_completed": 0,
      "usable_capacity_kwh": 9.0
    }
  ],
  "replacement_schedule": [
    {
      "year": 16,
      "cycles_completed": 6000,
      "replacement_cost": 7500.00
    }
  ],
  "cost_analysis": {
    "initial_cost": 7500.00,
    "replacement_costs": 7500.00,
    "maintenance_costs": 1500.00,
    "total_cost_of_ownership": 16500.00,
    "cost_per_year": 825.00
  },
  "end_of_life": {
    "final_capacity_percent": 67.3,
    "total_cycles_completed": 7300,
    "years_of_service": 20
  }
}
```

### Monitoring Integration

```http
POST /api/v1/battery/monitoring-integration
```

**Request Body:**
```json
{
  "battery_capacity_kwh": 10.0,
  "monitoring_system": "generic"
}
```

**Response:**
```json
{
  "battery_specs": { },
  "monitoring_system": "generic",
  "configuration": {
    "api_endpoint": "/api/v1/battery/monitoring",
    "protocol": "REST",
    "authentication": "API_KEY",
    "data_format": "JSON"
  },
  "data_points": {
    "real_time": [
      {
        "name": "state_of_charge",
        "unit": "%",
        "update_interval_seconds": 5
      }
    ],
    "historical": [ ],
    "lifecycle": [ ]
  },
  "alert_thresholds": {
    "critical": [ ],
    "warning": [ ],
    "info": [ ]
  },
  "recommended_polling_intervals": {
    "real_time_data": "5 seconds",
    "historical_data": "15 minutes",
    "lifecycle_data": "1 day"
  },
  "integration_endpoints": {
    "get_status": "/api/v1/battery/status",
    "get_history": "/api/v1/battery/history",
    "get_lifecycle": "/api/v1/battery/lifecycle",
    "set_strategy": "/api/v1/battery/strategy",
    "get_alerts": "/api/v1/battery/alerts"
  }
}
```

## Usage Examples

### Python Client Example

```python
import requests

# Battery sizing
response = requests.post(
    'http://localhost:8000/api/v1/battery/sizing',
    json={
        'daily_consumption_kwh': 15.0,
        'pv_system_size_kwp': 10.0,
        'annual_production_kwh': 10000.0,
        'self_consumption_rate': 0.35,
        'grid_feed_in_tariff': 0.08,
        'electricity_price': 0.30,
        'target_self_sufficiency': 0.8
    }
)

sizing_result = response.json()
print(f"Recommended battery: {sizing_result['recommended_capacity_kwh']} kWh")
print(f"Self-consumption improvement: {sizing_result['performance']['improvement_percent']}%")

# ROI analysis
response = requests.post(
    'http://localhost:8000/api/v1/battery/roi',
    json={
        'battery_capacity_kwh': sizing_result['recommended_capacity_kwh'],
        'daily_consumption_kwh': 15.0,
        'pv_system_size_kwp': 10.0,
        'annual_production_kwh': 10000.0,
        'self_consumption_rate': 0.35,
        'grid_feed_in_tariff': 0.08,
        'electricity_price': 0.30,
        'analysis_years': 20
    }
)

roi_result = response.json()
print(f"Payback period: {roi_result['simple_payback_years']} years")
print(f"Lifetime savings: €{roi_result['lifetime_savings']}")
```

## Battery Specifications

### Small Battery (5 kWh)
- Capacity: 5.0 kWh
- Usable: 4.5 kWh (90% DoD)
- Max charge/discharge: 2.5 kW
- Efficiency: 95%
- Warranty: 10 years / 6000 cycles
- Cost: €800/kWh

### Medium Battery (10 kWh)
- Capacity: 10.0 kWh
- Usable: 9.0 kWh (90% DoD)
- Max charge/discharge: 5.0 kW
- Efficiency: 95%
- Warranty: 10 years / 6000 cycles
- Cost: €750/kWh

### Large Battery (15 kWh)
- Capacity: 15.0 kWh
- Usable: 13.5 kWh (90% DoD)
- Max charge/discharge: 7.5 kW
- Efficiency: 95%
- Warranty: 10 years / 6000 cycles
- Cost: €700/kWh

## Discharge Strategies Explained

### Self-Consumption
Maximizes the use of stored solar energy for household consumption. Charges battery when surplus solar is available, discharges when consumption exceeds production.

**Best for:** Maximizing solar energy utilization

### Peak Shaving
Reduces grid import during peak hours by discharging battery. Charges during off-peak hours or when solar surplus is available.

**Best for:** Reducing demand charges and peak-hour electricity costs

### Time-of-Use
Optimizes for variable electricity pricing. Charges during low-price periods, discharges during high-price periods.

**Best for:** Time-of-use tariffs with significant price differences

### Backup
Maintains high state of charge for emergency backup power. Only discharges when necessary and above target SOC.

**Best for:** Areas with unreliable grid or emergency preparedness

## Monitoring Systems Supported

- **Generic**: Standard REST API integration
- **Tesla Powerwall**: Native Tesla API integration
- **Sonnen Battery**: Sonnen API integration
- **LG RESU**: Modbus TCP integration

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input parameters
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Performance Considerations

- Battery sizing calculations: < 100ms
- ROI analysis (20 years): < 200ms
- Discharge strategy simulation (24 hours): < 150ms
- Grid independence (12 months): < 200ms
- Lifecycle analysis (20 years): < 250ms

## Requirements

- Python 3.10+
- FastAPI 0.100+
- Pydantic 2.0+

## Related Services

- Solar Calculator Service
- Heat Pump Service
- Price Matrix Service
- PDF Generation Service
