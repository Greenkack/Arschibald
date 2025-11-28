# Third-Party Integrations Guide

Complete guide for configuring and using third-party service integrations in Solar Calculator Pro.

## Overview

The application integrates with six major categories of third-party services:

1. **Weather API** - Real-time and historical weather data for solar calculations
2. **Mapping API** - Geocoding and location services
3. **Payment Gateway** - Payment processing for customer transactions
4. **Email Service** - Transactional and marketing emails
5. **Cloud Storage** - File storage and management
6. **Analytics** - User behavior and application analytics

## Architecture

### Service Layer

All integrations are managed through a unified service layer:

```
ThirdPartyIntegrationService
├── WeatherIntegration
├── MappingIntegration
├── PaymentIntegration
├── EmailIntegration
├── CloudStorageIntegration
└── AnalyticsIntegration
```

### Configuration

Integrations are configured through environment variables or database settings:

```python
{
    "weather": {
        "enabled": true,
        "provider": "openweathermap",
        "api_key": "your_api_key",
        "units": "metric",
        "language": "de"
    },
    "mapping": {
        "enabled": true,
        "provider": "google_maps",
        "api_key": "your_api_key"
    },
    // ... other integrations
}
```

## Weather API Integration

### Supported Providers

- OpenWeatherMap (default)
- WeatherAPI
- Visual Crossing
- Custom providers

### Features

1. **Current Weather**
   - Temperature
   - Cloud cover
   - Humidity
   - Wind speed
   - Solar radiation

2. **Weather Forecast**
   - Up to 14 days
   - Hourly and daily data
   - Solar radiation forecasts

3. **Historical Data**
   - Past weather data
   - Solar production analysis
   - Seasonal patterns

### API Endpoints

```
POST /api/v1/integrations/weather/current
POST /api/v1/integrations/weather/forecast
POST /api/v1/integrations/weather/historical
```

### Example Usage

```python
# Get current weather
response = await client.post(
    "/api/v1/integrations/weather/current",
    json={"lat": 52.52, "lon": 13.405}
)

# Get 7-day forecast
response = await client.post(
    "/api/v1/integrations/weather/forecast",
    json={"lat": 52.52, "lon": 13.405, "days": 7}
)
```

### Configuration

```python
weather_config = {
    "enabled": True,
    "provider": "openweathermap",
    "api_key": "your_api_key",
    "base_url": "https://api.openweathermap.org/data/2.5",
    "units": "metric",  # or "imperial"
    "language": "de",
    "cache_duration": 3600  # seconds
}
```

## Mapping API Integration

### Supported Providers

- Google Maps (default)
- Mapbox
- OpenStreetMap
- HERE Maps

### Features

1. **Geocoding**
   - Address to coordinates
   - Structured address parsing
   - Multiple result handling

2. **Reverse Geocoding**
   - Coordinates to address
   - Detailed location info

3. **Distance Calculation**
   - Route distance
   - Travel time
   - Multiple routing options

### API Endpoints

```
POST /api/v1/integrations/mapping/geocode
POST /api/v1/integrations/mapping/reverse-geocode
POST /api/v1/integrations/mapping/distance
```

### Example Usage

```python
# Geocode address
response = await client.post(
    "/api/v1/integrations/mapping/geocode",
    json={"address": "Berlin, Germany"}
)

# Reverse geocode
response = await client.post(
    "/api/v1/integrations/mapping/reverse-geocode",
    json={"lat": 52.52, "lon": 13.405}
)

# Calculate distance
response = await client.post(
    "/api/v1/integrations/mapping/distance",
    json={
        "origin": {"lat": 52.52, "lon": 13.405},
        "destination": {"lat": 48.137, "lon": 11.576}
    }
)
```

## Payment Gateway Integration

### Supported Providers

- Stripe (default)
- PayPal
- Square
- Braintree

### Features

1. **Payment Intents**
   - Create payment intents
   - Confirm payments
   - Handle 3D Secure

2. **Refunds**
   - Full refunds
   - Partial refunds
   - Refund tracking

3. **Webhooks**
   - Payment status updates
   - Dispute notifications
   - Subscription events

### API Endpoints

```
POST /api/v1/integrations/payment/create-intent
POST /api/v1/integrations/payment/confirm
POST /api/v1/integrations/payment/refund
```

### Example Usage

```python
# Create payment intent
response = await client.post(
    "/api/v1/integrations/payment/create-intent",
    json={
        "amount": 16999.00,
        "currency": "EUR",
        "metadata": {
            "project_id": "proj_123",
            "customer_id": "cust_456"
        }
    }
)

# Confirm payment
response = await client.post(
    "/api/v1/integrations/payment/confirm",
    json={"payment_intent_id": "pi_123"}
)

# Refund payment
response = await client.post(
    "/api/v1/integrations/payment/refund",
    json={
        "payment_intent_id": "pi_123",
        "amount": 5000.00  # Partial refund
    }
)
```

### Security

- All payment data is encrypted
- PCI DSS compliance
- Secure webhook verification
- Test mode for development

## Email Service Integration

### Supported Providers

- SendGrid (default)
- Mailgun
- Amazon SES
- SMTP

### Features

1. **Transactional Emails**
   - Order confirmations
   - Password resets
   - Notifications

2. **Template Emails**
   - Pre-designed templates
   - Dynamic content
   - Personalization

3. **Attachments**
   - PDF reports
   - Documents
   - Images

### API Endpoints

```
POST /api/v1/integrations/email/send
POST /api/v1/integrations/email/send-template
```

### Example Usage

```python
# Send email
response = await client.post(
    "/api/v1/integrations/email/send",
    json={
        "to_email": "customer@example.com",
        "subject": "Your Solar Quote",
        "html_content": "<h1>Quote Details</h1>...",
        "attachments": [
            {
                "filename": "quote.pdf",
                "content": "base64_encoded_pdf",
                "type": "application/pdf"
            }
        ]
    }
)

# Send template email
response = await client.post(
    "/api/v1/integrations/email/send-template",
    json={
        "to_email": "customer@example.com",
        "template_id": "quote_template",
        "template_data": {
            "customer_name": "John Doe",
            "quote_amount": "16.999,00 €",
            "system_size": "10 kWp"
        }
    }
)
```

## Cloud Storage Integration

### Supported Providers

- Amazon S3 (default)
- Google Cloud Storage
- Azure Blob Storage
- MinIO

### Features

1. **File Upload**
   - Direct uploads
   - Multipart uploads
   - Progress tracking

2. **File Management**
   - List files
   - Download files
   - Delete files
   - File metadata

3. **Access Control**
   - Public/private files
   - Signed URLs
   - Expiring links

### API Endpoints

```
POST /api/v1/integrations/storage/upload
POST /api/v1/integrations/storage/download
POST /api/v1/integrations/storage/delete
POST /api/v1/integrations/storage/list
```

### Example Usage

```python
# Upload file
import base64

with open("document.pdf", "rb") as f:
    file_data = base64.b64encode(f.read()).decode()

response = await client.post(
    "/api/v1/integrations/storage/upload",
    json={
        "file_path": "projects/proj_123/quote.pdf",
        "file_data": file_data,
        "content_type": "application/pdf",
        "metadata": {
            "project_id": "proj_123",
            "uploaded_by": "user_456"
        }
    }
)

# Download file
response = await client.post(
    "/api/v1/integrations/storage/download",
    json={"file_path": "projects/proj_123/quote.pdf"}
)

# List files
response = await client.post(
    "/api/v1/integrations/storage/list",
    json={"prefix": "projects/proj_123/"}
)
```

## Analytics Integration

### Supported Providers

- Google Analytics (default)
- Mixpanel
- Amplitude
- Custom analytics

### Features

1. **Event Tracking**
   - User actions
   - Feature usage
   - Conversions

2. **Page Views**
   - Navigation tracking
   - Time on page
   - User flow

3. **User Properties**
   - User segments
   - Custom dimensions
   - User lifecycle

### API Endpoints

```
POST /api/v1/integrations/analytics/event
POST /api/v1/integrations/analytics/page-view
POST /api/v1/integrations/analytics/user
```

### Example Usage

```python
# Track event
response = await client.post(
    "/api/v1/integrations/analytics/event",
    json={
        "category": "Solar Calculator",
        "action": "Calculate",
        "label": "10kWp System",
        "value": 16999,
        "user_id": "user_123"
    }
)

# Track page view
response = await client.post(
    "/api/v1/integrations/analytics/page-view",
    json={
        "page_path": "/solar-calculator",
        "page_title": "Solar Calculator",
        "user_id": "user_123"
    }
)

# Track user
response = await client.post(
    "/api/v1/integrations/analytics/user",
    json={
        "user_id": "user_123",
        "properties": {
            "plan": "premium",
            "signup_date": "2024-01-01",
            "projects_count": 5
        }
    }
)
```

## Health Monitoring

### Status Check

Check the status of all integrations:

```
GET /api/v1/integrations/status
```

Response:
```json
{
    "weather": {
        "provider": "openweathermap",
        "enabled": true,
        "connected": true,
        "last_check": "2024-01-15T10:30:00Z"
    },
    "mapping": {
        "provider": "google_maps",
        "enabled": true,
        "connected": true,
        "last_check": "2024-01-15T10:30:00Z"
    },
    // ... other integrations
}
```

### Connection Test

Test all integration connections:

```
GET /api/v1/integrations/test
```

Response:
```json
{
    "weather": true,
    "mapping": true,
    "payment": true,
    "email": true,
    "cloud_storage": true,
    "analytics": true
}
```

## Error Handling

All integration errors are handled consistently:

```python
try:
    result = await service.weather.get_current_weather(lat, lon)
except IntegrationError as e:
    # Handle integration-specific error
    logger.error(f"Weather API error: {e}")
except Exception as e:
    # Handle general error
    logger.error(f"Unexpected error: {e}")
```

### Error Codes

- `503` - Service unavailable (integration disabled)
- `502` - Bad gateway (integration error)
- `500` - Internal server error

## Best Practices

1. **Configuration Management**
   - Store API keys securely
   - Use environment variables
   - Separate test/production configs

2. **Error Handling**
   - Implement retry logic
   - Log all errors
   - Provide fallbacks

3. **Performance**
   - Cache responses
   - Use async operations
   - Implement rate limiting

4. **Security**
   - Validate all inputs
   - Encrypt sensitive data
   - Use HTTPS only

5. **Monitoring**
   - Track API usage
   - Monitor response times
   - Set up alerts

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check API keys
   - Verify network connectivity
   - Check rate limits

2. **Authentication Errors**
   - Verify credentials
   - Check token expiration
   - Review permissions

3. **Rate Limiting**
   - Implement backoff
   - Cache responses
   - Upgrade plan if needed

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('third_party_integration').setLevel(logging.DEBUG)
```

## Support

For integration support:
- Check provider documentation
- Review error logs
- Contact provider support
- Submit issue on GitHub

## Requirements

- Python 3.10+
- FastAPI 0.100+
- Pydantic 2.0+
- httpx or aiohttp for async requests

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Security Guide](./SECURITY_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
