"""Example Usage of Tagged Cache Invalidation System"""

import re
import time

from .cache import get_cache
from .cache_invalidation import (
    DataRelationship,
    InvalidationRule,
    InvalidationStrategy,
    add_cache_dependency,
    flush_pending_invalidations,
    get_invalidation_stats,
    invalidate_by_write,
    invalidate_with_dependencies,
    register_data_relationship,
    register_invalidation_rule,
    schedule_batch_invalidation,
    set_batch_delay,
)


def example_basic_invalidation():
    """Example: Basic cache invalidation on database write"""
    print("\n=== Basic Cache Invalidation ===")

    cache = get_cache()

    # Cache some user data
    cache.set("user:123:profile", {"name": "John"}, tags={"user", "user:123"})
    cache.set(
        "user:123:session", {
            "active": True}, tags={
            "session", "user:123"})

    print(f"Cached user profile: {cache.get('user:123:profile')}")
    print(f"Cached user session: {cache.get('user:123:session')}")

    # Simulate database write - invalidate user caches
    count = invalidate_by_write("user", "123", "update")
    print(f"\nInvalidated {count} cache entries after user update")

    print(f"User profile after invalidation: {cache.get('user:123:profile')}")
    print(f"User session after invalidation: {cache.get('user:123:session')}")


def example_data_relationships():
    """Example: Smart invalidation with data relationships"""
    print("\n=== Data Relationships ===")

    # Define relationship: when user changes, invalidate related data
    user_relationship = DataRelationship(
        source_type="user",
        target_types={"session", "preferences", "navigation"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    register_data_relationship(user_relationship)

    # Create rule that uses the relationship
    rule = InvalidationRule(
        name="user_cascade_invalidation",
        trigger_tags={"user"},
        invalidate_tags={"session"},
        strategy=InvalidationStrategy.CASCADE,
        priority=100,
        relationships=[user_relationship],
        description="Cascade invalidate all user-related data"
    )

    register_invalidation_rule(rule)

    cache = get_cache()

    # Cache related data
    cache.set("session:user123", "session_data", tags={"session"})
    cache.set("preferences:user123", "pref_data", tags={"preferences"})
    cache.set("navigation:user123", "nav_data", tags={"navigation"})

    print("Cached session, preferences, and navigation")

    # Update user - should cascade to all related data
    count = invalidate_by_write("user", "user123", "update")
    print(f"\nCascade invalidated {count} entries")

    print(f"Session after cascade: {cache.get('session:user123')}")
    print(f"Preferences after cascade: {cache.get('preferences:user123')}")


def example_batched_invalidation():
    """Example: Batched invalidation for performance"""
    print("\n=== Batched Invalidation ===")

    # Set batch delay to 100ms
    set_batch_delay(100)

    # Create batched rule for form updates
    rule = InvalidationRule(
        name="form_batch_invalidation",
        trigger_tags={"form", "widget"},
        invalidate_tags={"form_state", "widget_state"},
        strategy=InvalidationStrategy.BATCHED,
        priority=50,
        description="Batch invalidate form state for performance"
    )

    register_invalidation_rule(rule)

    cache = get_cache()

    # Cache form data
    for i in range(5):
        cache.set(f"form_state:{i}", f"data_{i}", tags={"form_state"})

    print("Cached 5 form states")

    # Trigger multiple writes (will be batched)
    for i in range(3):
        invalidate_by_write("form", f"form{i}", "update")
        print(f"Triggered write {i + 1} (batched)")

    # Check immediately - should still be cached
    print(f"\nForm state 0 (immediate): {cache.get('form_state:0')}")

    # Wait for batch to execute
    time.sleep(0.15)

    # Now should be invalidated
    print(f"Form state 0 (after batch): {cache.get('form_state:0')}")

    # Or flush immediately
    schedule_batch_invalidation(tags={"form_state"})
    count = flush_pending_invalidations()
    print(f"\nFlushed {count} pending invalidations")


def example_cache_dependencies():
    """Example: Cache dependencies and cascade invalidation"""
    print("\n=== Cache Dependencies ===")

    cache = get_cache()

    # Cache computed data with dependencies
    cache.set("base_data", {"value": 100}, tags={"base"})
    cache.set("computed_1", {"result": 200}, tags={"computed"})
    cache.set("computed_2", {"result": 300}, tags={"computed"})

    # Define dependencies
    add_cache_dependency("computed_1", {"base_data"})
    add_cache_dependency("computed_2", {"base_data", "computed_1"})

    print("Set up cache with dependencies:")
    print("  base_data -> computed_1 -> computed_2")

    # Invalidate base data with dependencies
    count = invalidate_with_dependencies("base_data", recursive=True)
    print(f"\nInvalidated {count} entries (including dependencies)")

    print(f"Base data: {cache.get('base_data')}")
    print(f"Computed 1: {cache.get('computed_1')}")
    print(f"Computed 2: {cache.get('computed_2')}")


def example_pattern_based_invalidation():
    """Example: Pattern-based cache invalidation"""
    print("\n=== Pattern-Based Invalidation ===")

    # Create rule with regex pattern
    rule = InvalidationRule(
        name="user_session_pattern",
        trigger_tags={"user"},
        invalidate_tags=set(),
        pattern=re.compile(r"user:\d+:session:.*"),
        strategy=InvalidationStrategy.IMMEDIATE,
        description="Invalidate all user session keys matching pattern"
    )

    register_invalidation_rule(rule)

    cache = get_cache()

    # Cache multiple session keys
    cache.set("user:123:session:active", True, tags={"user"})
    cache.set("user:123:session:last_seen", "2024-01-01", tags={"user"})
    cache.set("user:456:session:active", True, tags={"user"})
    cache.set("other:data", "value", tags={"other"})

    print("Cached user sessions and other data")

    # Trigger invalidation - pattern will match user sessions
    count = invalidate_by_write("user", "123", "update")
    print(f"\nPattern matched and invalidated {count} entries")

    print(f"User 123 session: {cache.get('user:123:session:active')}")
    print(f"Other data: {cache.get('other:data')}")


def example_conditional_invalidation():
    """Example: Conditional invalidation rules"""
    print("\n=== Conditional Invalidation ===")

    # Create rule that only executes on delete operations
    def only_on_delete(context):
        return context.get("operation") == "delete"

    rule = InvalidationRule(
        name="delete_only_invalidation",
        trigger_tags={"product"},
        invalidate_tags={"product_cache", "pricing_cache"},
        condition=only_on_delete,
        strategy=InvalidationStrategy.IMMEDIATE,
        description="Only invalidate on delete operations"
    )

    register_invalidation_rule(rule)

    cache = get_cache()

    # Cache product data
    cache.set("product_cache:123", "data", tags={"product_cache"})
    cache.set("pricing_cache:123", "price", tags={"pricing_cache"})

    print("Cached product and pricing data")

    # Update operation - should NOT invalidate
    count = invalidate_by_write("product", "123", "update")
    print(f"\nUpdate operation: invalidated {count} entries")
    print(f"Product cache: {cache.get('product_cache:123')}")

    # Delete operation - SHOULD invalidate
    count = invalidate_by_write("product", "123", "delete")
    print(f"\nDelete operation: invalidated {count} entries")
    print(f"Product cache: {cache.get('product_cache:123')}")


def example_priority_rules():
    """Example: Rule priority and execution order"""
    print("\n=== Rule Priority ===")

    # Create rules with different priorities
    high_priority = InvalidationRule(
        name="critical_invalidation",
        trigger_tags={"critical"},
        invalidate_tags={"critical_cache"},
        priority=100,
        strategy=InvalidationStrategy.IMMEDIATE,
        description="High priority - execute first"
    )

    medium_priority = InvalidationRule(
        name="normal_invalidation",
        trigger_tags={"critical"},
        invalidate_tags={"normal_cache"},
        priority=50,
        strategy=InvalidationStrategy.IMMEDIATE,
        description="Medium priority"
    )

    low_priority = InvalidationRule(
        name="background_invalidation",
        trigger_tags={"critical"},
        invalidate_tags={"background_cache"},
        priority=10,
        strategy=InvalidationStrategy.BATCHED,
        description="Low priority - can be batched"
    )

    register_invalidation_rule(high_priority)
    register_invalidation_rule(medium_priority)
    register_invalidation_rule(low_priority)

    # Get stats to see priority ordering
    stats = get_invalidation_stats()

    print("Registered rules (sorted by priority):")
    for rule in stats["rule_details"]:
        print(f"  {rule['name']}: priority={rule['priority']}, "
              f"strategy={rule['strategy']}")


def example_statistics():
    """Example: Monitoring invalidation statistics"""
    print("\n=== Invalidation Statistics ===")

    cache = get_cache()

    # Perform some operations
    cache.set("key1", "value1", tags={"tag1"})
    cache.set("key2", "value2", tags={"tag2"})

    invalidate_by_write("tag1", "id1", "update")
    invalidate_by_write("tag2", "id2", "update")

    # Get comprehensive stats
    stats = get_invalidation_stats()

    print(f"Total rules: {stats['rules']}")
    print(f"Total relationships: {stats['relationships']}")
    print(f"Pending tags: {stats['pending_tags']}")
    print(f"Pending keys: {stats['pending_keys']}")
    print(f"Batch delay: {stats['batch_delay_ms']}ms")
    print("\nInvalidation counts:")
    print(f"  Total: {stats['total_invalidations']}")
    print(f"  Immediate: {stats['immediate_invalidations']}")
    print(f"  Batched: {stats['batched_invalidations']}")
    print(f"  Cascade: {stats['cascade_invalidations']}")

    print("\nRule details:")
    for rule in stats["rule_details"][:3]:  # Show first 3
        print(f"  {rule['name']}:")
        print(f"    Executions: {rule['execution_count']}")
        print(f"    Total invalidated: {rule['total_invalidated']}")
        print(f"    Strategy: {rule['strategy']}")


def example_real_world_scenario():
    """Example: Real-world scenario with user, forms, and products"""
    print("\n=== Real-World Scenario ===")

    # Setup relationships
    user_rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences", "forms"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    form_rel = DataRelationship(
        source_type="form",
        target_types={"form_state", "widget_state"},
        relationship_type="one_to_many",
        cascade_depth=1
    )

    product_rel = DataRelationship(
        source_type="product",
        target_types={"pricing", "inventory", "calculations"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    register_data_relationship(user_rel)
    register_data_relationship(form_rel)
    register_data_relationship(product_rel)

    # Setup rules
    user_rule = InvalidationRule(
        name="user_updates",
        trigger_tags={"user"},
        invalidate_tags={"session", "preferences"},
        strategy=InvalidationStrategy.IMMEDIATE,
        priority=100,
        relationships=[user_rel]
    )

    form_rule = InvalidationRule(
        name="form_updates",
        trigger_tags={"form"},
        invalidate_tags={"form_state"},
        strategy=InvalidationStrategy.BATCHED,
        priority=50,
        relationships=[form_rel]
    )

    product_rule = InvalidationRule(
        name="product_updates",
        trigger_tags={"product"},
        invalidate_tags={"pricing", "calculations"},
        strategy=InvalidationStrategy.CASCADE,
        priority=80,
        relationships=[product_rel]
    )

    register_invalidation_rule(user_rule)
    register_invalidation_rule(form_rule)
    register_invalidation_rule(product_rule)

    cache = get_cache()

    # Simulate application usage
    print("Simulating application usage...")

    # User logs in
    cache.set("session:user123", {"active": True}, tags={"session"})
    cache.set("preferences:user123", {"theme": "dark"}, tags={"preferences"})
    print("✓ User logged in, session cached")

    # User fills form
    cache.set("form_state:form1", {"field1": "value"}, tags={"form_state"})
    print("✓ Form state cached")

    # Product data loaded
    cache.set("pricing:prod1", {"price": 99.99}, tags={"pricing"})
    cache.set("calculations:prod1", {"total": 119.99}, tags={"calculations"})
    print("✓ Product data cached")

    # User updates profile (immediate invalidation)
    print("\n→ User updates profile...")
    count = invalidate_by_write("user", "user123", "update")
    print(f"  Invalidated {count} entries immediately")

    # Form auto-save (batched invalidation)
    print("\n→ Form auto-save...")
    invalidate_by_write("form", "form1", "update")
    print("  Scheduled batch invalidation")

    # Product price changes (cascade invalidation)
    print("\n→ Product price updated...")
    count = invalidate_by_write("product", "prod1", "update")
    print(f"  Cascade invalidated {count} entries")

    # Show final stats
    stats = get_invalidation_stats()
    print("\nFinal statistics:")
    print(f"  Total invalidations: {stats['total_invalidations']}")
    print(f"  Immediate: {stats['immediate_invalidations']}")
    print(f"  Batched: {stats['batched_invalidations']}")
    print(f"  Cascade: {stats['cascade_invalidations']}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Tagged Cache Invalidation System - Examples")
    print("=" * 60)

    example_basic_invalidation()
    example_data_relationships()
    example_batched_invalidation()
    example_cache_dependencies()
    example_pattern_based_invalidation()
    example_conditional_invalidation()
    example_priority_rules()
    example_statistics()
    example_real_world_scenario()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
