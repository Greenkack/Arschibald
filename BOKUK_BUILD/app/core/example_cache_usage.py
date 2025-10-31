"""Example Usage of Intelligent Caching System"""

import time
from datetime import datetime

from .cache import CacheKeys, get_cache, get_or_compute, invalidate_cache
from .cache_invalidation import (
    InvalidationRule,
    add_cache_dependency,
    invalidate_by_write,
    register_invalidation_rule,
)
from .cache_monitoring import get_cache_performance_report, start_cache_monitoring
from .cache_warming import (
    WarmingTask,
    register_warming_task,
    warm_user_data,
)


def example_basic_caching():
    """Example: Basic cache usage"""
    print("\n=== Basic Caching ===")

    # Simple get/set
    cache = get_cache()
    cache.set("user_name", "John Doe", ttl=3600)
    name = cache.get("user_name")
    print(f"Cached name: {name}")

    # Using CacheKeys for namespacing
    user_key = CacheKeys.user_session("user123")
    cache.set(user_key, {"session_id": "abc", "logged_in": True})
    session = cache.get(user_key)
    print(f"Cached session: {session}")


def example_get_or_compute():
    """Example: get_or_compute pattern"""
    print("\n=== Get or Compute Pattern ===")

    def expensive_calculation(x, y):
        """Simulate expensive computation"""
        print(f"Computing {x} + {y}...")
        time.sleep(0.1)  # Simulate work
        return x + y

    # First call - will compute
    key = CacheKeys.computed("add", 10, 20)
    result1 = get_or_compute(
        key=key,
        fn=lambda: expensive_calculation(10, 20),
        ttl=60,
        tags={"math", "computation"}
    )
    print(f"Result 1: {result1}")

    # Second call - will use cache
    result2 = get_or_compute(
        key=key,
        fn=lambda: expensive_calculation(10, 20),
        ttl=60
    )
    print(f"Result 2 (cached): {result2}")


def example_tagged_invalidation():
    """Example: Tagged cache invalidation"""
    print("\n=== Tagged Invalidation ===")

    cache = get_cache()

    # Set multiple entries with tags
    cache.set("user1_data", {"name": "Alice"}, tags={"user", "user:1"})
    cache.set("user1_prefs", {"theme": "dark"}, tags={"user", "user:1"})
    cache.set("user2_data", {"name": "Bob"}, tags={"user", "user:2"})

    print("Before invalidation:")
    print(f"  User 1 data: {cache.get('user1_data')}")
    print(f"  User 2 data: {cache.get('user2_data')}")

    # Invalidate all user:1 caches
    count = invalidate_cache(tags={"user:1"})
    print(f"\nInvalidated {count} entries with tag 'user:1'")

    print("\nAfter invalidation:")
    print(f"  User 1 data: {cache.get('user1_data')}")
    print(f"  User 2 data: {cache.get('user2_data')}")


def example_cache_dependencies():
    """Example: Cache dependencies"""
    print("\n=== Cache Dependencies ===")

    cache = get_cache()

    # Set up source data
    cache.set("product_price", 100.0)
    cache.set("tax_rate", 0.2)

    # Compute derived value
    def calculate_total():
        price = cache.get("product_price")
        tax = cache.get("tax_rate")
        return price * (1 + tax)

    total_key = "product_total"
    total = get_or_compute(total_key, calculate_total)
    print(f"Total price: ${total}")

    # Register dependency
    add_cache_dependency(total_key, {"product_price", "tax_rate"})

    # When source changes, derived value is invalidated
    cache.set("product_price", 120.0)
    invalidate_by_write("product", "price_update")


def example_invalidation_rules():
    """Example: Custom invalidation rules"""
    print("\n=== Invalidation Rules ===")

    # Define rule: when user data changes, invalidate user caches
    rule = InvalidationRule(
        name="user_update_rule",
        trigger_tags={"user_update"},
        invalidate_tags={"user_session", "user_preferences", "user_forms"},
        description="Invalidate user caches when user data is updated"
    )

    register_invalidation_rule(rule)

    # Simulate user update
    cache = get_cache()
    cache.set("user_session_123", {"active": True}, tags={"user_session"})

    # Trigger invalidation
    count = invalidate_by_write("user", "user123")
    print(f"Invalidated {count} entries after user update")


def example_cache_warming():
    """Example: Proactive cache warming"""
    print("\n=== Cache Warming ===")

    # Define warming task for critical data
    def load_critical_config():
        """Load critical configuration"""
        print("Loading critical config...")
        return {
            "api_endpoint": "https://api.example.com",
            "timeout": 30,
            "retry_count": 3
        }

    task = WarmingTask(
        task_id="critical_config",
        name="Critical Configuration",
        cache_key="app_config",
        compute_fn=load_critical_config,
        ttl=3600,
        priority=100,  # High priority
        tags={"config", "critical"}
    )

    register_warming_task(task)

    # Warm user-specific data
    results = warm_user_data("user123")
    print(f"Warmed {results['succeeded']} user cache entries")

    # Start background warming (runs periodically)
    # start_cache_warming(interval_minutes=60)


def example_cache_monitoring():
    """Example: Cache performance monitoring"""
    print("\n=== Cache Monitoring ===")

    # Start monitoring
    start_cache_monitoring(interval_seconds=60)

    # Perform some cache operations
    cache = get_cache()
    for i in range(10):
        cache.set(f"key_{i}", f"value_{i}")

    for i in range(15):
        cache.get(f"key_{i % 10}")  # Some hits, some misses

    # Get performance report
    report = get_cache_performance_report()

    print("\nCache Performance Report:")
    print(f"Timestamp: {report['timestamp']}")

    if "memory" in report["layers"]:
        memory = report["layers"]["memory"]
        hit_rate = memory["hit_rate"]
        print("\nMemory Layer:")
        print(f"  Hit Rate: {hit_rate['hit_rate']:.1%}")
        print(f"  Status: {hit_rate['status']}")
        print(f"  Trend: {hit_rate.get('trend', 'N/A')}")

    if report.get("recommendations"):
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")


def example_multi_layer_caching():
    """Example: Multi-layer cache usage"""
    print("\n=== Multi-Layer Caching ===")

    cache = get_cache()

    # Cache in memory only (fast, volatile)
    cache.set("temp_data", "temporary", layers={"memory"})

    # Cache in memory and database (persistent)
    cache.set(
        "important_data",
        {"value": "persistent"},
        layers={"memory", "database"}
    )

    # Get stats from all layers
    stats = cache.get_stats()
    print("\nCache Statistics:")
    for layer, layer_stats in stats.items():
        print(f"\n{layer.capitalize()} Layer:")
        if isinstance(layer_stats, dict):
            for key, value in layer_stats.items():
                print(f"  {key}: {value}")


def example_real_world_scenario():
    """Example: Real-world caching scenario"""
    print("\n=== Real-World Scenario: Product Pricing ===")

    def calculate_product_price(product_id: str, quantity: int):
        """Simulate expensive price calculation"""
        print(f"Calculating price for product {product_id}...")
        time.sleep(0.05)  # Simulate database query

        base_price = 100.0
        discount = 0.1 if quantity > 10 else 0.0
        tax = 0.2

        return {
            "product_id": product_id,
            "quantity": quantity,
            "base_price": base_price,
            "discount": discount,
            "tax": tax,
            "total": base_price * quantity * (1 - discount) * (1 + tax),
            "calculated_at": datetime.now().isoformat()
        }

    # First request - will compute
    start = time.time()
    key1 = CacheKeys.computed("product_price", "PROD123", 5)
    price1 = get_or_compute(
        key=key1,
        fn=lambda: calculate_product_price("PROD123", 5),
        ttl=300,  # Cache for 5 minutes
        tags={"pricing", "product:PROD123"}
    )
    time1 = (time.time() - start) * 1000
    print(f"First request: {time1:.1f}ms")
    print(f"Price: ${price1['total']:.2f}")

    # Second request - will use cache
    start = time.time()
    price2 = get_or_compute(
        key=key1,
        fn=lambda: calculate_product_price("PROD123", 5),
        ttl=300
    )
    time2 = (time.time() - start) * 1000
    print(f"\nSecond request (cached): {time2:.1f}ms")
    print(f"Price: ${price2['total']:.2f}")
    print(f"Speed improvement: {time1 / time2:.1f}x faster")

    # Simulate price update
    print("\n--- Price Update ---")
    invalidate_by_write("product", "PROD123", {"action": "price_update"})
    print("Cache invalidated after price update")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("Intelligent Caching System - Examples")
    print("=" * 60)

    example_basic_caching()
    example_get_or_compute()
    example_tagged_invalidation()
    example_cache_dependencies()
    example_invalidation_rules()
    example_cache_warming()
    example_cache_monitoring()
    example_multi_layer_caching()
    example_real_world_scenario()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
