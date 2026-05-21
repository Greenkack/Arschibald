# API Integration Framework - Quick Reference

## Installation

```bash
pip install aiohttp pydantic sqlalchemy
```

## Create Integration

```python
from backend.models.api_integration_schemas import APIIntegrationCreate, IntegrationType, AuthType

integration = APIIntegrationCreate(
    name="My API",
    integration_type=IntegrationType.REST,
    base_url="https://api.example.com",
    auth_type=AuthType.API_KEY,
    api_key="your_key_here"
)

response = await service.create_integration(integration)
```

## Make API Calls

```python
# GET request
data = await client.get("/endpoint", params={"key": "value"})

# POST request
data = await client.post("/endpoint", data={"key": "value"})

# PUT request
data = await client.put("/endpoint", data={"key": "value"})

# DELETE request
data = await client.delete("/endpoint")
```

## OAuth Flow

```python
# 1. Get authorization URL
url = await service.get_oauth_authorization_url(integration_id=1)

# 2. Handle callback
tokens = await service.handle_oauth_callback(integration_id=1, code="auth_code")

# 3. Refresh token (automatic, but can be manual)
tokens = await service.refresh_oauth_token(integration_id=1)
```

## Webhooks

```python
# Send webhook
success = await client.send_webhook("event.name", {"data": "value"})

# Verify webhook signature
is_valid = webhook_manager.verify_signature(payload, signature)

# List webhook history
history = await service.list_webhook_history(integration_id=1)

# Retry failed webhook
success = await service.retry_webhook(integration_id=1, webhook_id=123)
```

## Rate Limiting

```python
rate_limit_config = {
    "calls": 100,    # Max calls
    "period": 60     # Per 60 seconds
}
```

## Caching

```python
cache_config = {
    "enabled": True,
    "ttl": 300  # 5 minutes
}

# Clear cache
await client.clear_cache()
```

## Monitoring

```python
# Get metrics
metrics = await service.get_metrics(integration_id=1)

print(f"Total: {metrics.total_calls}")
print(f"Success: {metrics.successful_calls}")
print(f"Failed: {metrics.failed_calls}")
print(f"Success Rate: {metrics.success_rate * 100}%")
print(f"Avg Duration: {metrics.average_duration}s")
```

## Testing

```python
# Test connection
result = await service.test_integration(integration_id=1)

# Test webhook
success = await service.test_webhook(
    integration_id=1,
    event="test",
    data={"test": True}
)
```

## Auth Types

### API Key
```python
auth_type=AuthType.API_KEY,
api_key="your_key"
```

### Basic Auth
```python
auth_type=AuthType.BASIC,
username="user",
password="pass"
```

### Bearer Token
```python
auth_type=AuthType.BEARER,
bearer_token="token"
```

### OAuth 2.0
```python
auth_type=AuthType.OAUTH2,
oauth_config=OAuthConfigSchema(...)
```

## Error Handling

```python
try:
    data = await client.get("/endpoint")
except Exception as e:
    logger.error(f"API call failed: {e}")
```

## Common Patterns

### Retry Logic
```python
config = APIClientConfig(
    max_retries=3,
    retry_delay=1  # Exponential backoff: 1s, 2s, 4s
)
```

### Custom Headers
```python
custom_headers = {
    "X-Custom-Header": "value",
    "X-API-Version": "v1"
}
```

### Bypass Cache
```python
data = await client.get("/endpoint", use_cache=False)
```

### Bypass Rate Limit
```python
data = await client.get("/endpoint", bypass_rate_limit=True)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/api-integration/` | Create integration |
| GET | `/api/v1/api-integration/` | List integrations |
| GET | `/api/v1/api-integration/{id}` | Get integration |
| PUT | `/api/v1/api-integration/{id}` | Update integration |
| DELETE | `/api/v1/api-integration/{id}` | Delete integration |
| POST | `/api/v1/api-integration/{id}/oauth/authorize` | Get OAuth URL |
| POST | `/api/v1/api-integration/{id}/oauth/callback` | Handle OAuth callback |
| POST | `/api/v1/api-integration/{id}/oauth/refresh` | Refresh token |
| POST | `/api/v1/api-integration/{id}/test` | Test connection |
| POST | `/api/v1/api-integration/{id}/webhook/test` | Test webhook |
| GET | `/api/v1/api-integration/{id}/metrics` | Get metrics |
| POST | `/api/v1/api-integration/{id}/cache/clear` | Clear cache |
| GET | `/api/v1/api-integration/{id}/webhooks` | List webhooks |
| POST | `/api/v1/api-integration/{id}/webhooks/{wid}/retry` | Retry webhook |

## Configuration Examples

### Weather API
```python
APIIntegrationCreate(
    name="Weather API",
    integration_type=IntegrationType.REST,
    base_url="https://api.weather.com",
    auth_type=AuthType.API_KEY,
    api_key="key",
    rate_limit_config={"calls": 1000, "period": 3600},
    cache_config={"enabled": True, "ttl": 600}
)
```

### Payment Gateway
```python
APIIntegrationCreate(
    name="Payment Gateway",
    integration_type=IntegrationType.REST,
    base_url="https://api.payment.com",
    auth_type=AuthType.OAUTH2,
    oauth_config=OAuthConfigSchema(...),
    rate_limit_config={"calls": 100, "period": 60},
    cache_config={"enabled": False}
)
```

### Notification Service
```python
APIIntegrationCreate(
    name="Notifications",
    integration_type=IntegrationType.WEBHOOK,
    base_url="https://api.notify.com",
    auth_type=AuthType.BEARER,
    bearer_token="token",
    webhook_config=WebhookConfigSchema(
        url="https://your-app.com/webhooks",
        secret="secret",
        events=["notification.sent", "notification.failed"]
    )
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Token expired | `await service.refresh_oauth_token(id)` |
| Rate limit hit | `await service.reset_rate_limit(id)` |
| Stale cache | `await service.clear_cache(id)` |
| Webhook failed | `await service.retry_webhook(id, wid)` |
| Connection error | `await service.test_integration(id)` |

## Best Practices

1. ✅ Use appropriate cache TTL for data freshness
2. ✅ Set rate limits matching API provider limits
3. ✅ Monitor success rates regularly
4. ✅ Secure credentials with environment variables
5. ✅ Handle errors gracefully with try/except
6. ✅ Test integrations before production use
7. ✅ Use webhooks for real-time updates
8. ✅ Clear cache when data changes externally
9. ✅ Log all API interactions for debugging
10. ✅ Implement retry logic for transient failures
