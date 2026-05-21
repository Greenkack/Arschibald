# Heat Pump Product Database - Complete Guide

## Overview

The Heat Pump Product Database system provides comprehensive management of heat pump products with advanced filtering, comparison, and intelligent recommendation capabilities.

## Features

### 1. Product Data Management
- **Complete Specifications**: Technical specs, efficiency ratings, power ranges
- **Manufacturer Information**: All major heat pump manufacturers
- **Product Types**: Air-water, water-water, brine-water, air-air, hybrid
- **Pricing Data**: Base prices and installation costs
- **Availability Tracking**: Real-time stock levels and lead times

### 2. Advanced Filtering
Filter products by:
- Manufacturers and types
- Power range (heating/cooling)
- Efficiency ratings (COP, SCOP, EER, SEER)
- Temperature requirements
- Features (smart grid, internet, inverter)
- Price range
- Availability and lead time

### 3. Product Comparison
Compare up to 5 products across:
- Efficiency metrics
- Power capabilities
- Total cost of ownership
- Features and capabilities
- Temperature operating ranges

### 4. Intelligent Recommendations
Get personalized recommendations based on:
- Building characteristics (size, insulation, age)
- Climate and temperature requirements
- Heating/cooling needs
- Budget constraints
- Feature preferences
- Energy efficiency goals

### 5. Availability Management
- Real-time availability tracking
- Stock level monitoring
- Lead time information
- Alternative product suggestions
- Bulk availability checks

## API Endpoints

### Get All Products
```http
GET /api/v1/heatpump-products/
```

Returns all heat pump products in the database.

**Response:**
```json
[
  {
    "model": "Vitocal 200-S",
    "manufacturer": "Viessmann",
    "heatpump_type": "Luft-Wasser-Wärmepumpe",
    "heating_power_kw": [6.0, 8.0, 10.0],
    "scop": 4.5,
    "base_price": 12000.00,
    "available": true
  }
]
```

### Get Product by ID
```http
GET /api/v1/heatpump-products/{product_id}
```

### Filter Products
```http
POST /api/v1/heatpump-products/filter
```

**Request Body:**
```json
{
  "manufacturers": ["Viessmann", "Vaillant"],
  "heatpump_types": ["Luft-Wasser-Wärmepumpe"],
  "min_heating_power": 8.0,
  "max_heating_power": 15.0,
  "min_scop": 4.0,
  "smart_grid_required": true,
  "max_price": 15000.00,
  "available_only": true,
  "sort_by": "scop",
  "sort_order": "desc",
  "page": 1,
  "page_size": 20
}
```

**Response:**
```json
{
  "products": [...],
  "total_count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "filters_applied": {...}
}
```

### Compare Products
```http
POST /api/v1/heatpump-products/compare
```

**Request Body:**
```json
{
  "product_ids": [
    "Viessmann_Vitocal_200-S",
    "Vaillant_aroTHERM_plus",
    "Daikin_Altherma_3"
  ],
  "comparison_criteria": ["efficiency", "power", "cost", "features"]
}
```

**Response:**
```json
{
  "products": [...],
  "comparison_matrix": {
    "efficiency": {
      "Viessmann_Vitocal_200-S": {"cop": 4.2, "scop": 4.5},
      "Vaillant_aroTHERM_plus": {"cop": 4.3, "scop": 4.6}
    },
    "power": {...},
    "cost": {...},
    "features": {...}
  },
  "best_in_category": {
    "efficiency": "Vaillant aroTHERM plus",
    "power": "Daikin Altherma 3",
    "value": "Viessmann Vitocal 200-S",
    "features": "Daikin Altherma 3"
  },
  "summary": {...}
}
```

### Get Recommendations
```http
POST /api/v1/heatpump-products/recommend
```

**Request Body:**
```json
{
  "building_area_sqm": 150.0,
  "building_insulation": "good",
  "building_age": 15,
  "desired_indoor_temp": 21.0,
  "climate_zone": "Central Europe",
  "lowest_outdoor_temp": -15.0,
  "existing_heating_system": "gas",
  "radiator_type": "low-temp",
  "hot_water_required": true,
  "cooling_required": false,
  "max_budget": 18000.00,
  "prefer_quiet": true,
  "prefer_smart_features": true,
  "target_scop": 4.5
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "product": {...},
      "suitability_score": 92.5,
      "recommendation_reasons": [
        "Optimal power match for your heating needs",
        "Exceeds target SCOP of 4.5",
        "Smart grid ready for energy optimization",
        "Very quiet operation (45 dB)"
      ],
      "estimated_annual_cost": 850.00,
      "estimated_savings": 450.00,
      "payback_period_years": 12.5,
      "environmental_impact": {
        "annual_co2_kg": 1200,
        "co2_savings_vs_gas_kg": 800
      }
    }
  ],
  "building_analysis": {...},
  "estimated_heat_load_kw": 10.5,
  "recommended_power_range": {
    "min": 9.5,
    "max": 12.6
  }
}
```

### Check Availability
```http
GET /api/v1/heatpump-products/availability/{product_id}
```

**Response:**
```json
{
  "product_id": "Viessmann_Vitocal_200-S",
  "manufacturer": "Viessmann",
  "model": "Vitocal 200-S",
  "available": true,
  "stock_level": "in_stock",
  "lead_time_days": 14,
  "next_delivery_date": "2024-02-15T00:00:00",
  "last_updated": "2024-02-01T10:30:00"
}
```

### Update Availability
```http
PUT /api/v1/heatpump-products/availability
```

**Request Body:**
```json
{
  "product_id": "Viessmann_Vitocal_200-S",
  "available": true,
  "stock_level": "low_stock",
  "lead_time_days": 21,
  "next_delivery_date": "2024-02-20T00:00:00"
}
```

### Get Alternative Products
```http
GET /api/v1/heatpump-products/alternatives/{product_id}?max_alternatives=3
```

Returns similar products when the requested product is unavailable.

### Get Statistics
```http
GET /api/v1/heatpump-products/statistics
```

Returns comprehensive statistics about the product database.

## Usage Examples

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get all products
response = requests.get(f"{BASE_URL}/heatpump-products/")
products = response.json()

# Filter products
filter_request = {
    "min_heating_power": 8.0,
    "min_scop": 4.0,
    "smart_grid_required": True,
    "available_only": True,
    "sort_by": "scop",
    "sort_order": "desc"
}
response = requests.post(
    f"{BASE_URL}/heatpump-products/filter",
    json=filter_request
)
filtered = response.json()

# Get recommendations
recommendation_request = {
    "building_area_sqm": 150.0,
    "building_insulation": "good",
    "climate_zone": "Central Europe",
    "lowest_outdoor_temp": -15.0,
    "hot_water_required": True,
    "max_budget": 18000.00,
    "prefer_smart_features": True
}
response = requests.post(
    f"{BASE_URL}/heatpump-products/recommend",
    json=recommendation_request
)
recommendations = response.json()

# Compare products
comparison_request = {
    "product_ids": [
        "Viessmann_Vitocal_200-S",
        "Vaillant_aroTHERM_plus"
    ]
}
response = requests.post(
    f"{BASE_URL}/heatpump-products/compare",
    json=comparison_request
)
comparison = response.json()
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';

// Get recommendations
async function getRecommendations() {
  const response = await fetch(`${BASE_URL}/heatpump-products/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      building_area_sqm: 150.0,
      building_insulation: 'good',
      climate_zone: 'Central Europe',
      lowest_outdoor_temp: -15.0,
      hot_water_required: true,
      max_budget: 18000.00,
      prefer_smart_features: true,
    }),
  });
  
  const recommendations = await response.json();
  return recommendations;
}

// Filter products
async function filterProducts(filters) {
  const response = await fetch(`${BASE_URL}/heatpump-products/filter`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(filters),
  });
  
  return await response.json();
}
```

## Data Models

### HeatPumpSpecification
Complete product specification including:
- Model and manufacturer
- Heat pump type
- Power specifications (heating/cooling)
- Efficiency ratings (COP, SCOP, EER, SEER)
- Temperature ranges
- Physical specifications
- Features and capabilities
- Pricing and availability

### HeatPumpFilterRequest
Comprehensive filtering options for product search.

### HeatPumpRecommendationRequest
Building and requirement specifications for intelligent recommendations.

### HeatPumpAvailability
Real-time availability and stock information.

## Best Practices

1. **Filtering**: Use specific filters to narrow down results efficiently
2. **Recommendations**: Provide accurate building data for best results
3. **Comparison**: Compare similar products (same type, similar power range)
4. **Availability**: Check availability before finalizing product selection
5. **Alternatives**: Always have backup options for unavailable products

## Integration with Solar Calculator

The heat pump product database integrates seamlessly with the solar calculator for combined PV + heat pump systems:

```python
# Get solar calculation
solar_result = solar_service.calculate(solar_request)

# Get heat pump recommendations based on solar system
hp_request = HeatPumpRecommendationRequest(
    building_area_sqm=solar_request.building_area,
    # ... other parameters
)
hp_recommendations = heatpump_product_service.recommend_products(hp_request)

# Calculate combined system benefits
combined_savings = solar_result.annual_savings + hp_recommendations.recommendations[0].estimated_savings
```

## Performance Considerations

- Product data is loaded once at service initialization
- Filtering operations are optimized for large datasets
- Availability cache reduces database queries
- Recommendation engine uses efficient scoring algorithms

## Future Enhancements

- Machine learning-based recommendations
- Historical performance data integration
- Real-time pricing updates
- Integration with supplier APIs
- Advanced energy modeling
- Seasonal performance predictions
