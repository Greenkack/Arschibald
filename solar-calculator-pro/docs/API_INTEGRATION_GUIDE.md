# API Integration Framework Guide

## Overview

The API Integration Framework provides a unified system for connecting to external APIs with built-in support for:

- **OAuth 2.0 Authentication**: Full OAuth flow with automatic token refresh
- **Webhook Management**: Send and receive webhooks with retry logic
- **Rate Limiting**: Token bucket algorithm to respect API limits
- **Caching**: Intelligent response caching with TTL
- **Monitoring**: Track API performance and errors
- **Multiple Auth Types**: API Key, Basic, Bearer, OAuth2

## Quick Start

### 1. Create an API Integration

```python
from backend.models.api_integration_schemas import (
    APIIntegrationCreate,
    IntegrationType,
    AuthType,
    OAuthConfigSchema
)

# Create integration with OAuth
integration = APIIntegrationCreate(
    name="Weather API",
    description="External weather data provider",
    integration_type=IntegrationType.REST,
    base_url="https://api.weather.com/v1",
    auth_type=AuthType.OAUTH2,
    oauth_config=OAuthConfigSchema(
        client_id="your_client_id",
        client_secret="your_client_secret",
        authorization_url="https://api.weather.com/oauth/authorize",
        token_url="https://api.weather.com/oauth/token",
        redirect_uri="http://localhost:8000/callback",
        scope=["read:weather", "read:forecast"]
    ),
    rate_limit_config={
        "calls": 100,
        "period": 60  # 100 calls per minute
    },
    cache_config={
        "enabled": True,
        "ttl": 300  # Cache for 5 minutes
    }
)

# Save to database
response = await api_integration_service.create_integration(integration)
```

### 2. OAuth Authorization Flow

```python
# Step 1: Get authorization URL
auth_url = await api_integration_service.get_oauth_authorization_url(
    integration_id=1,
    state="random_state_string"
)

# Redirect user to auth_url

# Step 2: Handle callback
tokens = await api_integration_service.handle_oauth_callback(
    integration_id=1,
    code="authorization_code_from_callback"
)

# Tokens are automatically stored and managed
```

### 3. Make API Calls

```python
from backend.core.api_client import APIClient, APIClientConfig

# Get client for integration
client = api_integration_service._get_client(integration)

# Make requests (rate limiting and caching applied automatically)
weather_data = await client.get("/weather", params={"city": "Berlin"})

forecast_data = await client.post("/forecast", data={
    "location": "Berlin",
    "days": 7
})
```

### 4. Send Webhooks

```python
# Configure webhook
webhook_config = WebhookConfigSchema(
    url="https://your-app.com/webhooks/weather",
    secret="your_webhook_secret",
    events=["weather.updated", "forecast.ready"],
    retry_attempts=3,
    timeout=10
)

# Send webhook
success = await client.send_webhook(
    event="weather.updated",
    data={"city": "Berlin", "temperature": 22}
)
```

## Authentication Types

### API Key Authentication

```python
integration = APIIntegrationCreate(
    name="Simple API",
    auth_type=AuthType.API_KEY,
    api_key="your_api_key_here",
    custom_headers={"X-API-Key": "your_api_key_here"}
)
```

### Basic Authentication

```python
integration = APIIntegrationCreate(
    name="Basic Auth API",
    auth_type=AuthType.BASIC,
    username="your_username",
    password="your_password"
)
```

### Bearer Token

```python
integration = APIIntegrationCreate(
    name="Bearer Token API",
    auth_type=AuthType.BEARER,
    bearer_token="your_bearer_token"
)
```

### OAuth 2.0

```python
integration = APIIntegrationCreate(
    name="OAuth API",
    auth_type=AuthType.OAUTH2,
    oauth_config=OAuthConfigSchema(
        client_id="client_id",
        client_secret="client_secret",
        authorization_url="https://api.example.com/oauth/authorize",
        token_url="https://api.example.com/oauth/token",
        redirect_uri="http://localhost:8000/callback",
        scope=["read", "write"]
    )
)
```

## Rate Limiting

The framework uses a token bucket algorithm for rate limiting:

```python
rate_limit_config = {
    "calls": 100,      # Maximum calls
    "period": 60       # Time period in seconds
}

# This allows 100 calls per 60 seconds
# Tokens refill gradually over time
```

## Caching

Intelligent caching for GET requests:

```python
cache_config = {
    "enabled": True,
    "ttl": 300  # Cache for 5 minutes
}

# First call - hits API
data1 = await client.get("/data")

# Second call within 5 minutes - returns cached data
data2 = await client.get("/data")

# Clear cache manually if needed
await client.clear_cache()
```

## Monitoring

Track API performance and errors:

```python
# Get metrics for an integration
metrics = await api_integration_service.get_metrics(integration_id=1)

print(f"Total calls: {metrics.total_calls}")
print(f"Success rate: {metrics.success_rate * 100}%")
print(f"Average duration: {metrics.average_duration}s")
print(f"Failed calls: {metrics.failed_calls}")
print(f"Recent errors: {metrics.errors}")
```

## Webhook Management

### Sending Webhooks

```python
# Send webhook with automatic retry
success = await client.send_webhook(
    event="data.updated",
    data={"id": 123, "status": "completed"}
)
```

### Receiving Webhooks

```python
from backend.core.api_client import WebhookManager

# Verify webhook signature
webhook_manager = WebhookManager(webhook_config)
is_valid = webhook_manager.verify_signature(
    payload=request_body,
    signature=request.headers.get("X-Webhook-Signature")
)

if is_valid:
    # Process webhook
    pass
```

### Webhook History

```python
# List webhook deliveries
history = await api_integration_service.list_webhook_history(
    integration_id=1,
    skip=0,
    limit=50
)

# Retry failed webhook
success = await api_integration_service.retry_webhook(
    integration_id=1,
    webhook_id=123
)
```

## Error Handling

The framework includes automatic retry logic with exponential backoff:

```python
config = APIClientConfig(
    base_url="https://api.example.com",
    max_retries=3,      # Retry up to 3 times
    retry_delay=1       # Start with 1 second delay
)

# Retry delays: 1s, 2s, 4s (exponential backoff)
```

## Testing Integrations

```python
# Test connection
result = await api_integration_service.test_integration(integration_id=1)

if result.success:
    print(f"Connection successful! Response time: {result.response_time}s")
else:
    print(f"Connection failed: {result.error}")

# Test webhook
success = await api_integration_service.test_webhook(
    integration_id=1,
    event="test.event",
    data={"test": True}
)
```

## Best Practices

### 1. Use Appropriate Cache TTL

```python
# Short TTL for frequently changing data
cache_config={"enabled": True, "ttl": 60}

# Long TTL for static data
cache_config={"enabled": True, "ttl": 3600}

# Disable cache for real-time data
cache_config={"enabled": False}
```

### 2. Set Reasonable Rate Limits

```python
# Match the API provider's limits
rate_limit_config={
    "calls": 1000,
    "period": 3600  # 1000 calls per hour
}
```

### 3. Handle Token Refresh

```python
# Tokens are automatically refreshed when needed
# But you can manually refresh if required
tokens = await api_integration_service.refresh_oauth_token(integration_id=1)
```

### 4. Monitor API Health

```python
# Regularly check metrics
metrics = await api_integration_service.get_metrics(integration_id=1)

if metrics.success_rate < 0.95:  # Less than 95% success
    # Alert or investigate
    logger.warning(f"Low success rate: {metrics.success_rate}")
```

### 5. Secure Credentials

```python
# In production, encrypt sensitive data
# Use environment variables for secrets
import os

integration = APIIntegrationCreate(
    name="Secure API",
    api_key=os.getenv("API_KEY"),
    # Never hardcode credentials
)
```

## API Endpoints

### Create Integration
```
POST /api/v1/api-integration/
```

### List Integrations
```
GET /api/v1/api-integration/
```

### Get Integration
```
GET /api/v1/api-integration/{integration_id}
```

### Update Integration
```
PUT /api/v1/api-integration/{integration_id}
```

### Delete Integration
```
DELETE /api/v1/api-integration/{integration_id}
```

### OAuth Authorization
```
POST /api/v1/api-integration/{integration_id}/oauth/authorize
POST /api/v1/api-integration/{integration_id}/oauth/callback
POST /api/v1/api-integration/{integration_id}/oauth/refresh
```

### Testing
```
POST /api/v1/api-integration/{integration_id}/test
POST /api/v1/api-integration/{integration_id}/webhook/test
```

### Monitoring
```
GET /api/v1/api-integration/{integration_id}/metrics
POST /api/v1/api-integration/{integration_id}/cache/clear
POST /api/v1/api-integration/{integration_id}/rate-limit/reset
```

### Webhooks
```
GET /api/v1/api-integration/{integration_id}/webhooks
POST /api/v1/api-integration/{integration_id}/webhooks/{webhook_id}/retry
```

## Troubleshooting

### OAuth Token Expired

```python
# Tokens are automatically refreshed
# If manual refresh needed:
tokens = await api_integration_service.refresh_oauth_token(integration_id=1)
```

### Rate Limit Exceeded

```python
# Wait for rate limit to reset or increase limits
await api_integration_service.reset_rate_limit(integration_id=1)
```

### Webhook Delivery Failed

```python
# Check webhook history
history = await api_integration_service.list_webhook_history(integration_id=1)

# Retry failed deliveries
for delivery in history:
    if delivery.status == "FAILED":
        await api_integration_service.retry_webhook(
            integration_id=1,
            webhook_id=delivery.id
        )
```

### Cache Issues

```python
# Clear cache if stale data is returned
await api_integration_service.clear_cache(integration_id=1)
```

## Examples

See `backend/demo_api_integration.py` for complete working examples.
