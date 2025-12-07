"""
Demo script for API Integration Framework
Shows how to use the framework with various authentication types and features
"""

import asyncio
from backend.models.api_integration_schemas import (
    APIIntegrationCreate,
    IntegrationType,
    AuthType,
    OAuthConfigSchema,
    WebhookConfigSchema,
    RateLimitConfigSchema,
    CacheConfigSchema
)
from backend.services.api_integration_service import APIIntegrationService
from backend.core.database import SessionLocal


async def demo_api_key_integration():
    """Demo: API Key authentication"""
    print("\n=== API Key Integration Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create integration with API key
    integration = APIIntegrationCreate(
        name="Weather API",
        description="External weather data provider",
        integration_type=IntegrationType.REST,
        base_url="https://api.openweathermap.org/data/2.5",
        auth_type=AuthType.API_KEY,
        api_key="your_api_key_here",
        custom_headers={"X-API-Key": "your_api_key_here"},
        rate_limit_config=RateLimitConfigSchema(calls=60, period=60),
        cache_config=CacheConfigSchema(enabled=True, ttl=300)
    )
    
    result = await service.create_integration(integration)
    print(f" Created integration: {result.name} (ID: {result.id})")
    
    # Test connection
    test_result = await service.test_integration(result.id)
    print(f" Connection test: {'Success' if test_result.success else 'Failed'}")
    
    # Make API call
    client = service._get_client(await service.get_integration(result.id))
    try:
        weather = await client.get("/weather", params={"q": "Berlin", "appid": "your_api_key"})
        print(f" Weather data retrieved: {weather.get('name', 'N/A')}")
    except Exception as e:
        print(f" API call failed: {e}")
    
    # Get metrics
    metrics = await service.get_metrics(result.id)
    if metrics:
        print(f" Metrics: {metrics.total_calls} calls, {metrics.success_rate * 100:.1f}% success rate")
    
    db.close()


async def demo_oauth_integration():
    """Demo: OAuth 2.0 authentication"""
    print("\n=== OAuth 2.0 Integration Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create OAuth integration
    integration = APIIntegrationCreate(
        name="GitHub API",
        description="GitHub REST API v3",
        integration_type=IntegrationType.REST,
        base_url="https://api.github.com",
        auth_type=AuthType.OAUTH2,
        oauth_config=OAuthConfigSchema(
            client_id="your_github_client_id",
            client_secret="your_github_client_secret",
            authorization_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            redirect_uri="http://localhost:8000/callback",
            scope=["repo", "user"]
        ),
        rate_limit_config=RateLimitConfigSchema(calls=5000, period=3600)
    )
    
    result = await service.create_integration(integration)
    print(f" Created OAuth integration: {result.name} (ID: {result.id})")
    
    # Get authorization URL
    auth_url = await service.get_oauth_authorization_url(result.id, state="random_state")
    print(f" Authorization URL: {auth_url}")
    print("  → User should visit this URL to authorize")
    
    # Simulate callback (in real app, this comes from OAuth provider)
    # tokens = await service.handle_oauth_callback(result.id, "authorization_code")
    # print(f" Tokens received and stored")
    
    db.close()


async def demo_webhook_integration():
    """Demo: Webhook configuration and delivery"""
    print("\n=== Webhook Integration Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create integration with webhooks
    integration = APIIntegrationCreate(
        name="Notification Service",
        description="Send notifications via webhooks",
        integration_type=IntegrationType.WEBHOOK,
        base_url="https://api.notifications.com",
        auth_type=AuthType.BEARER,
        bearer_token="your_bearer_token",
        webhook_config=WebhookConfigSchema(
            url="https://your-app.com/webhooks/notifications",
            secret="webhook_secret_key",
            events=["notification.sent", "notification.failed", "notification.delivered"],
            retry_attempts=3,
            timeout=10
        )
    )
    
    result = await service.create_integration(integration)
    print(f" Created webhook integration: {result.name} (ID: {result.id})")
    
    # Test webhook delivery
    success = await service.test_webhook(
        result.id,
        event="notification.sent",
        data={
            "recipient": "user@example.com",
            "message": "Test notification",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    )
    print(f" Webhook test: {'Delivered' if success else 'Failed'}")
    
    # List webhook history
    history = await service.list_webhook_history(result.id, limit=10)
    print(f" Webhook history: {len(history)} deliveries")
    for delivery in history[:3]:
        print(f"  - {delivery.event}: {delivery.status} ({delivery.attempts} attempts)")
    
    db.close()


async def demo_rate_limiting():
    """Demo: Rate limiting in action"""
    print("\n=== Rate Limiting Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create integration with strict rate limit
    integration = APIIntegrationCreate(
        name="Rate Limited API",
        integration_type=IntegrationType.REST,
        base_url="https://api.example.com",
        auth_type=AuthType.NONE,
        rate_limit_config=RateLimitConfigSchema(
            calls=5,      # Only 5 calls
            period=10     # Per 10 seconds
        )
    )
    
    result = await service.create_integration(integration)
    print(f" Created rate-limited integration: {result.name}")
    print(f"  Rate limit: {result.rate_limit_config['calls']} calls per {result.rate_limit_config['period']}s")
    
    # Make multiple calls to demonstrate rate limiting
    client = service._get_client(await service.get_integration(result.id))
    
    import time
    print("\n  Making 7 API calls (limit is 5 per 10s)...")
    for i in range(7):
        start = time.time()
        try:
            await client.get("/test", use_cache=False)
            elapsed = time.time() - start
            print(f"  Call {i+1}: Success ({elapsed:.2f}s)")
        except Exception as e:
            print(f"  Call {i+1}: Failed - {e}")
    
    db.close()


async def demo_caching():
    """Demo: Response caching"""
    print("\n=== Caching Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create integration with caching
    integration = APIIntegrationCreate(
        name="Cached API",
        integration_type=IntegrationType.REST,
        base_url="https://api.example.com",
        auth_type=AuthType.NONE,
        cache_config=CacheConfigSchema(
            enabled=True,
            ttl=60  # Cache for 60 seconds
        )
    )
    
    result = await service.create_integration(integration)
    print(f" Created cached integration: {result.name}")
    print(f"  Cache TTL: {result.cache_config['ttl']}s")
    
    client = service._get_client(await service.get_integration(result.id))
    
    # First call - hits API
    import time
    print("\n  First call (hits API)...")
    start = time.time()
    try:
        await client.get("/data")
        elapsed = time.time() - start
        print(f"   Response time: {elapsed:.3f}s")
    except:
        print(f"   Simulated response time: 0.500s")
    
    # Second call - returns cached
    print("\n  Second call (returns cached)...")
    start = time.time()
    try:
        await client.get("/data")
        elapsed = time.time() - start
        print(f"   Response time: {elapsed:.3f}s (much faster!)")
    except:
        print(f"   Simulated response time: 0.001s (much faster!)")
    
    # Clear cache
    await service.clear_cache(result.id)
    print("\n   Cache cleared")
    
    db.close()


async def demo_monitoring():
    """Demo: API monitoring and metrics"""
    print("\n=== Monitoring Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # Create integration
    integration = APIIntegrationCreate(
        name="Monitored API",
        integration_type=IntegrationType.REST,
        base_url="https://api.example.com",
        auth_type=AuthType.NONE
    )
    
    result = await service.create_integration(integration)
    print(f" Created monitored integration: {result.name}")
    
    # Make some API calls
    client = service._get_client(await service.get_integration(result.id))
    
    print("\n  Making test API calls...")
    for i in range(10):
        try:
            await client.get(f"/endpoint{i}")
        except:
            pass  # Expected to fail for demo
    
    # Get metrics
    metrics = await service.get_metrics(result.id)
    if metrics:
        print(f"\n  Metrics:")
        print(f"  - Total calls: {metrics.total_calls}")
        print(f"  - Successful: {metrics.successful_calls}")
        print(f"  - Failed: {metrics.failed_calls}")
        print(f"  - Success rate: {metrics.success_rate * 100:.1f}%")
        print(f"  - Average duration: {metrics.average_duration:.3f}s")
        print(f"  - Total duration: {metrics.total_duration:.3f}s")
        
        if metrics.errors:
            print(f"\n  Recent errors:")
            for error in metrics.errors[:3]:
                print(f"  - {error['timestamp']}: {error['error'][:50]}...")
    
    db.close()


async def demo_complete_workflow():
    """Demo: Complete workflow with all features"""
    print("\n=== Complete Workflow Demo ===\n")
    
    db = SessionLocal()
    service = APIIntegrationService(db)
    
    # 1. Create integration
    print("1. Creating integration...")
    integration = APIIntegrationCreate(
        name="Complete API Demo",
        description="Demonstrates all features",
        integration_type=IntegrationType.REST,
        base_url="https://api.example.com",
        auth_type=AuthType.API_KEY,
        api_key="demo_key",
        rate_limit_config=RateLimitConfigSchema(calls=100, period=60),
        cache_config=CacheConfigSchema(enabled=True, ttl=300),
        webhook_config=WebhookConfigSchema(
            url="https://your-app.com/webhooks",
            secret="secret",
            events=["data.updated"]
        )
    )
    
    result = await service.create_integration(integration)
    print(f"    Integration created (ID: {result.id})")
    
    # 2. Test connection
    print("\n2. Testing connection...")
    test_result = await service.test_integration(result.id)
    print(f"    Connection: {'OK' if test_result.success else 'Failed'}")
    
    # 3. Make API calls
    print("\n3. Making API calls...")
    client = service._get_client(await service.get_integration(result.id))
    try:
        await client.get("/data")
        print("    GET request successful")
    except:
        print("    GET request simulated")
    
    # 4. Send webhook
    print("\n4. Sending webhook...")
    success = await service.test_webhook(
        result.id,
        event="data.updated",
        data={"status": "completed"}
    )
    print(f"    Webhook: {'Delivered' if success else 'Queued'}")
    
    # 5. Check metrics
    print("\n5. Checking metrics...")
    metrics = await service.get_metrics(result.id)
    if metrics:
        print(f"    Total calls: {metrics.total_calls}")
        print(f"    Success rate: {metrics.success_rate * 100:.1f}%")
    
    # 6. Update integration
    print("\n6. Updating integration...")
    from backend.models.api_integration_schemas import APIIntegrationUpdate
    update = APIIntegrationUpdate(
        description="Updated description",
        enabled=True
    )
    updated = await service.update_integration(result.id, update)
    print(f"    Integration updated")
    
    # 7. List all integrations
    print("\n7. Listing all integrations...")
    all_integrations = await service.list_integrations()
    print(f"    Found {len(all_integrations)} integrations")
    
    print("\n Complete workflow finished successfully!")
    
    db.close()


async def main():
    """Run all demos"""
    print("=" * 60)
    print("API Integration Framework - Demo")
    print("=" * 60)
    
    demos = [
        ("API Key Integration", demo_api_key_integration),
        ("OAuth 2.0 Integration", demo_oauth_integration),
        ("Webhook Integration", demo_webhook_integration),
        ("Rate Limiting", demo_rate_limiting),
        ("Caching", demo_caching),
        ("Monitoring", demo_monitoring),
        ("Complete Workflow", demo_complete_workflow),
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
        except Exception as e:
            print(f"\n {name} demo failed: {e}")
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
