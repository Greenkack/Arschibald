# Third-Party Integrations - Quick Reference

Quick reference for all third-party service integrations.

## Status & Health

```bash
# Check all integration status
GET /api/v1/integrations/status

# Test all connections
GET /api/v1/integrations/test
```

## Weather API

```bash
# Current weather
POST /api/v1/integrations/weather/current
{
  "lat": 52.52,
  "lon": 13.405
}

# 7-day forecast
POST /api/v1/integrations/weather/forecast
{
  "lat": 52.52,
  "lon": 13.405,
  "days": 7
}

# Historical data
POST /api/v1/integrations/weather/historical
{
  "lat": 52.52,
  "lon": 13.405,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

## Mapping API

```bash
# Geocode address
POST /api/v1/integrations/mapping/geocode
{
  "address": "Berlin, Germany"
}

# Reverse geocode
POST /api/v1/integrations/mapping/reverse-geocode
{
  "lat": 52.52,
  "lon": 13.405
}

# Calculate distance
POST /api/v1/integrations/mapping/distance
{
  "origin": {"lat": 52.52, "lon": 13.405},
  "destination": {"lat": 48.137, "lon": 11.576}
}
```

## Payment Gateway

```bash
# Create payment intent
POST /api/v1/integrations/payment/create-intent
{
  "amount": 16999.00,
  "currency": "EUR",
  "metadata": {"project_id": "proj_123"}
}

# Confirm payment
POST /api/v1/integrations/payment/confirm
{
  "payment_intent_id": "pi_123"
}

# Refund payment
POST /api/v1/integrations/payment/refund
{
  "payment_intent_id": "pi_123",
  "amount": 5000.00
}
```

## Email Service

```bash
# Send email
POST /api/v1/integrations/email/send
{
  "to_email": "customer@example.com",
  "subject": "Your Solar Quote",
  "html_content": "<h1>Quote</h1>",
  "attachments": [...]
}

# Send template email
POST /api/v1/integrations/email/send-template
{
  "to_email": "customer@example.com",
  "template_id": "quote_template",
  "template_data": {"name": "John", "amount": "16.999,00 €"}
}
```

## Cloud Storage

```bash
# Upload file
POST /api/v1/integrations/storage/upload
{
  "file_path": "projects/proj_123/quote.pdf",
  "file_data": "base64_encoded_data",
  "content_type": "application/pdf"
}

# Download file
POST /api/v1/integrations/storage/download
{
  "file_path": "projects/proj_123/quote.pdf"
}

# Delete file
POST /api/v1/integrations/storage/delete
{
  "file_path": "projects/proj_123/quote.pdf"
}

# List files
POST /api/v1/integrations/storage/list
{
  "prefix": "projects/proj_123/"
}
```

## Analytics

```bash
# Track event
POST /api/v1/integrations/analytics/event
{
  "category": "Solar Calculator",
  "action": "Calculate",
  "label": "10kWp System",
  "value": 16999
}

# Track page view
POST /api/v1/integrations/analytics/page-view
{
  "page_path": "/solar-calculator",
  "page_title": "Solar Calculator"
}

# Track user
POST /api/v1/integrations/analytics/user
{
  "user_id": "user_123",
  "properties": {"plan": "premium"}
}
```

## Configuration

### Environment Variables

```bash
# Weather
WEATHER_PROVIDER=openweathermap
WEATHER_API_KEY=your_api_key

# Mapping
MAPPING_PROVIDER=google_maps
MAPPING_API_KEY=your_api_key

# Payment
PAYMENT_PROVIDER=stripe
PAYMENT_SECRET_KEY=sk_test_...
PAYMENT_PUBLISHABLE_KEY=pk_test_...

# Email
EMAIL_PROVIDER=sendgrid
EMAIL_API_KEY=your_api_key
EMAIL_FROM=noreply@example.com

# Storage
STORAGE_PROVIDER=s3
STORAGE_BUCKET=solar-calculator-files
STORAGE_REGION=eu-central-1

# Analytics
ANALYTICS_PROVIDER=google_analytics
ANALYTICS_TRACKING_ID=UA-XXXXXXXXX-X
```

### Python Configuration

```python
config = {
    "weather": {
        "enabled": True,
        "provider": "openweathermap",
        "api_key": "your_api_key"
    },
    "mapping": {
        "enabled": True,
        "provider": "google_maps",
        "api_key": "your_api_key"
    },
    "payment": {
        "enabled": True,
        "provider": "stripe",
        "secret_key": "sk_test_...",
        "test_mode": True
    },
    "email": {
        "enabled": True,
        "provider": "sendgrid",
        "api_key": "your_api_key",
        "from_email": "noreply@example.com"
    },
    "cloud_storage": {
        "enabled": True,
        "provider": "s3",
        "bucket": "solar-calculator-files"
    },
    "analytics": {
        "enabled": True,
        "provider": "google_analytics",
        "tracking_id": "UA-XXXXXXXXX-X"
    }
}
```

## Error Codes

- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Internal server error
- `502` - Bad gateway (integration error)
- `503` - Service unavailable (integration disabled)

## Common Patterns

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_integration():
    return await service.weather.get_current_weather(lat, lon)
```

### Caching

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=100)
async def get_cached_weather(lat: float, lon: float):
    return await service.weather.get_current_weather(lat, lon)
```

### Error Handling

```python
try:
    result = await service.weather.get_current_weather(lat, lon)
except IntegrationError as e:
    logger.error(f"Integration error: {e}")
    # Use fallback or cached data
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle general error
```

## Testing

### Mock Integration

```python
from unittest.mock import AsyncMock

# Mock weather service
service.weather.get_current_weather = AsyncMock(
    return_value={"temperature": 20.5, "cloud_cover": 30}
)

# Test
result = await service.weather.get_current_weather(52.52, 13.405)
assert result["temperature"] == 20.5
```

### Integration Tests

```python
import pytest

@pytest.mark.asyncio
async def test_weather_integration():
    service = ThirdPartyIntegrationService(config)
    result = await service.weather.get_current_weather(52.52, 13.405)
    assert result is not None
    assert "temperature" in result
```

## Monitoring

### Metrics to Track

- API response times
- Error rates
- Rate limit usage
- Cache hit rates
- Integration availability

### Logging

```python
import logging

logger = logging.getLogger("integrations")
logger.setLevel(logging.INFO)

# Log all integration calls
logger.info(f"Weather API call: lat={lat}, lon={lon}")
logger.error(f"Weather API error: {error}")
```

## Support

- **Documentation**: `/docs/THIRD_PARTY_INTEGRATIONS_GUIDE.md`
- **API Docs**: `/api/v1/docs`
- **Issues**: GitHub Issues
- **Email**: support@example.com
