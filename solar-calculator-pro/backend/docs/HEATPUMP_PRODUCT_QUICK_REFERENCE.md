# Heat Pump Product Database - Quick Reference

## Quick Start

```python
from solar-calculator-pro.backend.services.heatpump_product_service import heatpump_product_service

# Get all products
products = heatpump_product_service.get_all_products()

# Get product by ID
product = heatpump_product_service.get_product_by_id("Viessmann_Vitocal_200-S")

# Filter products
from solar-calculator-pro.backend.models.heatpump_product_schemas import HeatPumpFilterRequest

filter_req = HeatPumpFilterRequest(
    min_heating_power=8.0,
    min_scop=4.0,
    available_only=True
)
filtered = heatpump_product_service.filter_products(filter_req)

# Get recommendations
from solar-calculator-pro.backend.models.heatpump_product_schemas import HeatPumpRecommendationRequest

rec_req = HeatPumpRecommendationRequest(
    building_area_sqm=150.0,
    building_insulation="good",
    climate_zone="Central Europe",
    lowest_outdoor_temp=-15.0,
    hot_water_required=True
)
recommendations = heatpump_product_service.recommend_products(rec_req)
```

## API Endpoints Cheat Sheet

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/heatpump-products/` | GET | Get all products |
| `/heatpump-products/{id}` | GET | Get specific product |
| `/heatpump-products/manufacturer/{name}` | GET | Get by manufacturer |
| `/heatpump-products/type/{type}` | GET | Get by type |
| `/heatpump-products/filter` | POST | Filter products |
| `/heatpump-products/compare` | POST | Compare products |
| `/heatpump-products/recommend` | POST | Get recommendations |
| `/heatpump-products/availability/{id}` | GET | Check availability |
| `/heatpump-products/availability` | PUT | Update availability |
| `/heatpump-products/alternatives/{id}` | GET | Get alternatives |
| `/heatpump-products/manufacturers` | GET | List manufacturers |
| `/heatpump-products/types` | GET | List types |
| `/heatpump-products/statistics` | GET | Get statistics |

## Filter Options

```python
HeatPumpFilterRequest(
    manufacturers=["Viessmann", "Vaillant"],  # Filter by manufacturers
    heatpump_types=["Luft-Wasser-Wärmepumpe"],  # Filter by types
    min_heating_power=8.0,  # Minimum heating power (kW)
    max_heating_power=15.0,  # Maximum heating power (kW)
    min_cop=4.0,  # Minimum COP
    min_scop=4.0,  # Minimum SCOP
    min_operating_temp_required=-20.0,  # Required min operating temp
    max_flow_temp_required=65.0,  # Required max flow temp
    smart_grid_required=True,  # Require smart grid capability
    internet_required=True,  # Require internet connectivity
    inverter_required=True,  # Require inverter technology
    max_price=15000.00,  # Maximum price (EUR)
    available_only=True,  # Show only available products
    max_lead_time_days=30,  # Maximum lead time
    sort_by="scop",  # Sort field (scop, cop, price, power)
    sort_order="desc",  # Sort order (asc, desc)
    page=1,  # Page number
    page_size=20  # Items per page
)
```

## Recommendation Parameters

```python
HeatPumpRecommendationRequest(
    # Building specs
    building_area_sqm=150.0,
    building_insulation="good",  # poor, average, good, excellent
    building_age=15,
    
    # Temperature requirements
    desired_indoor_temp=21.0,
    climate_zone="Central Europe",
    lowest_outdoor_temp=-15.0,
    
    # System requirements
    existing_heating_system="gas",
    radiator_type="low-temp",  # high-temp, low-temp, underfloor
    hot_water_required=True,
    cooling_required=False,
    
    # Budget and preferences
    max_budget=18000.00,
    prefer_quiet=True,
    prefer_smart_features=True,
    
    # Energy goals
    target_cop=4.0,
    target_scop=4.5
)
```

## Heat Pump Types

- `Luft-Wasser-Wärmepumpe` - Air-to-water heat pump
- `Wasser-Wasser-Wärmepumpe` - Water-to-water heat pump
- `Sole-Wasser-Wärmepumpe` - Brine-to-water heat pump (geothermal)
- `Luft-Luft-Wärmepumpe` - Air-to-air heat pump
- `Hybrid-Wärmepumpe` - Hybrid heat pump

## Efficiency Ratings

- **COP** (Coefficient of Performance): Instantaneous efficiency
- **SCOP** (Seasonal COP): Average efficiency over heating season
- **EER** (Energy Efficiency Ratio): Cooling efficiency
- **SEER** (Seasonal EER): Average cooling efficiency

## Response Examples

### Filter Response
```json
{
  "products": [...],
  "total_count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### Recommendation Response
```json
{
  "recommendations": [
    {
      "product": {...},
      "suitability_score": 92.5,
      "recommendation_reasons": ["..."],
      "estimated_annual_cost": 850.00,
      "estimated_savings": 450.00,
      "payback_period_years": 12.5
    }
  ],
  "estimated_heat_load_kw": 10.5,
  "recommended_power_range": {"min": 9.5, "max": 12.6}
}
```

### Comparison Response
```json
{
  "products": [...],
  "comparison_matrix": {...},
  "best_in_category": {
    "efficiency": "Product A",
    "power": "Product B",
    "value": "Product C"
  }
}
```

## Common Use Cases

### 1. Find Best Efficiency Products
```python
filter_req = HeatPumpFilterRequest(
    min_scop=4.5,
    available_only=True,
    sort_by="scop",
    sort_order="desc"
)
```

### 2. Find Budget-Friendly Options
```python
filter_req = HeatPumpFilterRequest(
    max_price=12000.00,
    min_scop=4.0,
    sort_by="price",
    sort_order="asc"
)
```

### 3. Find Smart Grid Ready Products
```python
filter_req = HeatPumpFilterRequest(
    smart_grid_required=True,
    internet_required=True,
    inverter_required=True
)
```

### 4. Get Personalized Recommendations
```python
rec_req = HeatPumpRecommendationRequest(
    building_area_sqm=150.0,
    building_insulation="good",
    lowest_outdoor_temp=-15.0,
    prefer_smart_features=True
)
recommendations = heatpump_product_service.recommend_products(rec_req)
```

## Error Handling

```python
from fastapi import HTTPException

try:
    product = heatpump_product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Performance Tips

1. Use pagination for large result sets
2. Apply specific filters to reduce result size
3. Cache frequently accessed products
4. Use bulk availability checks for multiple products
5. Limit comparison to 3-5 products for best performance

## Integration Points

- **Solar Calculator**: Combined PV + heat pump systems
- **CRM System**: Customer product recommendations
- **PDF Generator**: Product datasheets and comparisons
- **Pricing System**: Dynamic pricing and quotes
- **Inventory System**: Real-time availability tracking
