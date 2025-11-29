# Task 253 Complete - PVGIS API Integration

## Overview
PVGIS (Photovoltaic Geographical Information System) API integration for accurate yield calculations.

## File Created

### `backend/api/v1/pvgis_integration.py`
**Complete PVGIS Integration Module**

## Features Implemented

### 1. PVGIS API Connection
- Connection to PVGIS 5.2 API (EU Joint Research Centre)
- Async HTTP requests with timeout handling
- Automatic parameter conversion
- Error handling and fallback

### 2. Static Yield Fallback
- Latitude-based yield factors for Germany (47°-56°N)
- Orientation correction factors (N, NE, E, SE, S, SW, W, NW)
- Tilt angle correction (optimal ~32° for Germany)
- System loss calculation

### 3. Location-Based Optimization
- Optimal tilt angle calculation
- Optimal azimuth determination
- Location-specific yield factors
- Regional irradiance data

### 4. Roof Configuration Correction
- Tilt angle correction factors
- Orientation correction factors
- Combined correction calculation
- System loss integration

### 5. Yield Comparison
- PVGIS vs. static calculation comparison
- Difference calculation (kWh and %)
- Recommendation engine
- Explanation notes

## API Endpoints

### POST `/api/v1/pvgis/calculate`
Calculate PV yield using PVGIS API with fallback.

**Request:**
```json
{
  "latitude": 51.0,
  "longitude": 7.0,
  "peak_power_kwp": 10.0,
  "roof_tilt": 30,
  "roof_orientation": "south",
  "system_loss": 14,
  "mounting_type": "building",
  "use_horizon": true
}
```

**Response:**
```json
{
  "annual_yield_kwh": 9500,
  "monthly_yields_kwh": [475, 570, 760, ...],
  "specific_yield_kwh_kwp": 950,
  "optimal_tilt": 32,
  "optimal_azimuth": 180,
  "data_source": "PVGIS 5.2",
  "location": {"latitude": 51.0, "longitude": 7.0},
  "system_info": {...}
}
```

### POST `/api/v1/pvgis/static-yield`
Calculate yield using static factors only.

### POST `/api/v1/pvgis/compare`
Compare PVGIS and static yield calculations.

**Response:**
```json
{
  "pvgis_yield_kwh": 9500,
  "static_yield_kwh": 9200,
  "difference_kwh": 300,
  "difference_percent": 3.26,
  "recommended_source": "either",
  "notes": "Both calculations are within 5%..."
}
```

### GET `/api/v1/pvgis/optimal-configuration`
Get optimal roof configuration for location.

### GET `/api/v1/pvgis/monthly-profile`
Get monthly yield profile for the year.

## Static Yield Factors

### Base Yield by Latitude (Germany)
| Latitude Range | Base Yield (kWh/kWp) |
|----------------|---------------------|
| 47-48° (South) | 1050 |
| 48-49° | 1020 |
| 49-50° | 1000 |
| 50-51° | 980 |
| 51-52° | 960 |
| 52-53° | 940 |
| 53-54° | 920 |
| 54-55° (North) | 900 |

### Orientation Correction Factors
| Orientation | Factor |
|-------------|--------|
| South | 1.00 |
| Southeast/Southwest | 0.95 |
| East/West | 0.85 |
| Northeast/Northwest | 0.75 |
| North | 0.60 |

### Tilt Correction Factors
| Deviation from Optimal | Factor |
|------------------------|--------|
| 0-5° | 1.00 |
| 5-10° | 0.98 |
| 10-15° | 0.95 |
| 15-20° | 0.92 |
| 20-30° | 0.87 |
| >30° | 0.80 |

## Monthly Distribution (Static)
| Month | Factor |
|-------|--------|
| January | 5% |
| February | 6% |
| March | 8% |
| April | 10% |
| May | 11% |
| June | 12% |
| July | 12% |
| August | 11% |
| September | 9% |
| October | 8% |
| November | 5% |
| December | 3% |

## Usage Examples

### Basic Yield Calculation
```python
import httpx

response = await httpx.post(
    "http://localhost:8000/api/v1/pvgis/calculate",
    json={
        "latitude": 51.0,
        "longitude": 7.0,
        "peak_power_kwp": 10.0,
        "roof_tilt": 30,
        "roof_orientation": "south"
    }
)
result = response.json()
print(f"Annual yield: {result['annual_yield_kwh']} kWh")
```

### Compare Calculations
```python
response = await httpx.post(
    "http://localhost:8000/api/v1/pvgis/compare",
    json={
        "latitude": 51.0,
        "longitude": 7.0,
        "peak_power_kwp": 10.0,
        "roof_tilt": 30,
        "roof_orientation": "south"
    }
)
comparison = response.json()
print(f"PVGIS: {comparison['pvgis_yield_kwh']} kWh")
print(f"Static: {comparison['static_yield_kwh']} kWh")
print(f"Difference: {comparison['difference_percent']:.1f}%")
```

### Get Optimal Configuration
```python
response = await httpx.get(
    "http://localhost:8000/api/v1/pvgis/optimal-configuration",
    params={
        "latitude": 51.0,
        "longitude": 7.0,
        "peak_power_kwp": 10.0
    }
)
optimal = response.json()
print(f"Optimal tilt: {optimal['optimal_tilt_degrees']}°")
print(f"Optimal orientation: {optimal['optimal_orientation']}")
```

## Error Handling

### PVGIS Unavailable
- Automatic fallback to static calculation
- Data source indicated in response
- No user intervention required

### Invalid Parameters
- Latitude/longitude validation
- Power validation (must be > 0)
- Tilt angle validation (0-90°)
- System loss validation (0-100%)

## Integration Notes

### PVGIS API Details
- Base URL: https://re.jrc.ec.europa.eu/api/v5_2
- Endpoint: /PVcalc
- Timeout: 30 seconds
- Technology: Crystalline Silicon

### Azimuth Convention
- PVGIS: -180 to 180 (0 = South)
- Internal: 0 to 360 (0 = North, 180 = South)
- Automatic conversion handled

## Status: ✅ COMPLETE

Task 253 - PVGIS API Integration is fully implemented with API connection, fallback system, and yield comparison features.
