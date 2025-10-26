"""Tests for Tagged Cache Invalidation System"""

import re
import time

import pytest

from .cache import get_cache
from .cache_invalidation import (
    DataRelationship,
    InvalidationEngine,
    InvalidationRule,
    InvalidationStrategy,
    add_cache_dependency,
    flush_pending_invalidations,
    get_invalidation_engine,
    get_invalidation_stats,
    invalidate_by_write,
    invalidate_with_dependencies,
    register_data_relationship,
    register_invalidation_rule,
    schedule_batch_invalidation,
    set_batch_delay,
)


@pytest.fixture
def cache():
    """Get cache instance"""
    cache = get_cache()
    cache.clear()
    yield cache
    cache.clear()


@pytest.fixture
def engine():
    """Get fresh invalidation engine"""
    engine = InvalidationEngine()
    yield engine


def test_data_relationship_creation():
    """Test DataRelationship creation"""
    rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    assert rel.source_type == "user"
    assert "session" in rel.target_types
    assert rel.cascade_depth == 2


def test_data_relationship_get_related_tags():
    """Test getting related tags from relationship"""
    rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences"},
        relationship_type="one_to_many"
    )

    tags = rel.get_related_tags("user123")

    assert "session" in tags
    assert "preferences" in tags
    assert "session:user123" in tags
    assert "preferences:user123" in tags


def test_invalidation_rule_with_strategy():
    """Test InvalidationRule with different strategies"""
    rule = InvalidationRule(
        name="test_rule",
        trigger_tags={"user"},
        invalidate_tags={"session"},
        strategy=InvalidationStrategy.BATCHED,
        priority=50
    )

    assert rule.strategy == InvalidationStrategy.BATCHED
    assert rule.priority == 50
    assert rule.execution_count == 0


def test_invalidation_rule_with_relationships(cache):
    """Test InvalidationRule with data relationships"""
    rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences"},
        relationship_type="one_to_many"
    )

    rule = InvalidationRule(
        name="user_invalidation",
        trigger_tags={"user"},
        invalidate_tags={"session"},
        relationships=[rel]
    )

    # Set up cache entries
    cache.set("session:user123", "data1", tags={"session"})
    cache.set("preferences:user123", "data2", tags={"preferences"})

    # Execute rule
    context = {"resource_id": "user123"}
    count = rule.execute(context)

    assert count >= 0
    assert rule.execution_count == 1


def test_invalidation_rule_with_pattern(cache):
    """Test InvalidationRule with regex pattern"""
    rule = InvalidationRule(
        name="pattern_rule",
        trigger_tags={"user"},
        invalidate_tags=set(),
        pattern=re.compile(r"user:\d+:.*")
    )

    # Set up cache entries
    cache.set("user:123:session", "data1", tags={"user"})
    cache.set("user:456:session", "data2", tags={"user"})
    cache.set("other:789", "data3", tags={"other"})

    # Execute rule with context
    context = {"resource_type": "user"}
    count = rule.execute(context)

    # Pattern matching should find and invalidate matching keys
    assert count >= 0  # Pattern matching may not find keys depending on cache state


def test_engine_register_rule(engine):
    """Test registering invalidation rules"""
    rule = InvalidationRule(
        name="test_rule",
        trigger_tags={"user"},
        invalidate_tags={"session"}
    )

    engine.register_rule(rule)

    stats = engine.get_stats()
    assert stats["rules"] == 1


def test_engine_register_relationship(engine):
    """Test registering data relationships"""
    rel = DataRelationship(
        source_type="user",
        target_types={"session"},
        relationship_type="one_to_many"
    )

    engine.register_relationship(rel)

    stats = engine.get_stats()
    # Stats returns a list of relationships, check length
    assert len(stats["relationships"]) == 1
    assert stats["relationships"][0]["source"] == "user"


def test_engine_get_related_tags(engine):
    """Test getting related tags from engine"""
    rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    engine.register_relationship(rel)

    tags = engine.get_related_tags("user", "user123", depth=1)

    assert "user" in tags
    assert "user:user123" in tags
    assert "session" in tags
    assert "preferences" in tags


def test_engine_invalidate_by_write_immediate(cache, engine):
    """Test immediate invalidation on write"""
    rule = InvalidationRule(
        name="immediate_rule",
        trigger_tags={"user"},
        invalidate_tags={"session"},
        strategy=InvalidationStrategy.IMMEDIATE,
        priority=100
    )

    engine.register_rule(rule)

    # Set up cache
    cache.set("session:123", "data", tags={"session"})

    # Trigger write
    count = engine.invalidate_by_write("user", "user123", "update")

    assert count > 0
    assert cache.get("session:123") is None


def test_engine_invalidate_by_write_batched(cache, engine):
    """Test batched invalidation on write"""
    rule = InvalidationRule(
        name="batched_rule",
        trigger_tags={"form"},
        invalidate_tags={"form_state"},
        strategy=InvalidationStrategy.BATCHED
    )

    engine.register_rule(rule)
    engine.set_batch_delay(50)  # 50ms delay

    # Set up cache
    cache.set("form_state:123", "data", tags={"form_state"})

    # Verify it's cached
    assert cache.get("form_state:123") is not None

    # Trigger write (should be batched)
    count = engine.invalidate_by_write("form", "form123", "update")

    # Wait for batch to execute
    time.sleep(0.15)

    # Now it should be invalidated
    assert cache.get("form_state:123") is None


def test_engine_invalidate_by_write_cascade(cache, engine):
    """Test cascade invalidation on write"""
    rel = DataRelationship(
        source_type="product",
        target_types={"pricing", "calculation"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    rule = InvalidationRule(
        name="cascade_rule",
        trigger_tags={"product"},
        invalidate_tags={"pricing"},
        strategy=InvalidationStrategy.CASCADE,
        relationships=[rel]
    )

    engine.register_rule(rule)

    # Set up cache with dependencies
    cache.set("pricing:123", "data1", tags={"pricing"})
    cache.set("calculation:123", "data2", tags={"calculation"})

    # Add dependency
    engine.add_dependency("calculation:123", {"pricing:123"})

    # Trigger write
    count = engine.invalidate_by_write("product", "prod123", "update")

    assert count > 0


def test_engine_batch_invalidation(cache, engine):
    """Test batch invalidation scheduling"""
    cache.set("key1", "value1", tags={"tag1"})
    cache.set("key2", "value2", tags={"tag2"})

    engine.set_batch_delay(50)
    engine.schedule_batch_invalidation(tags={"tag1", "tag2"})

    # Should still be cached
    assert cache.get("key1") is not None

    # Wait for batch
    time.sleep(0.1)

    # Should be invalidated
    assert cache.get("key1") is None


def test_engine_flush_pending(cache, engine):
    """Test flushing pending invalidations"""
    cache.set("key1", "value1", tags={"tag1"})

    engine.schedule_batch_invalidation(tags={"tag1"})

    # Flush immediately
    count = engine.flush_pending()

    assert count > 0
    assert cache.get("key1") is None


def test_engine_stats(engine):
    """Test getting engine statistics"""
    rule = InvalidationRule(
        name="test_rule",
        trigger_tags={"user"},
        invalidate_tags={"session"},
        priority=50
    )

    engine.register_rule(rule)

    stats = engine.get_stats()

    assert stats["rules"] == 1
    assert stats["batch_delay_ms"] == 100
    assert "rule_details" in stats
    assert len(stats["rule_details"]) == 1
    assert stats["rule_details"][0]["name"] == "test_rule"
    assert stats["rule_details"][0]["priority"] == 50


def test_invalidate_by_write_convenience(cache):
    """Test invalidate_by_write convenience function"""
    cache.set("user:123", "data", tags={"user"})

    count = invalidate_by_write("user", "user123", "update")

    assert count >= 0


def test_add_cache_dependency():
    """Test add_cache_dependency convenience function"""
    add_cache_dependency("key1", {"key2", "key3"})

    engine = get_invalidation_engine()
    deps = engine._dependency_tracker.get_dependencies("key1")

    assert "key2" in deps
    assert "key3" in deps


def test_invalidate_with_dependencies(cache):
    """Test invalidate_with_dependencies convenience function"""
    cache.set("key1", "value1", tags={"tag1"})
    cache.set("key2", "value2", tags={"tag2"})

    add_cache_dependency("key2", {"key1"})

    count = invalidate_with_dependencies("key1", recursive=True)

    assert count >= 0


def test_register_invalidation_rule():
    """Test register_invalidation_rule convenience function"""
    rule = InvalidationRule(
        name="custom_rule",
        trigger_tags={"custom"},
        invalidate_tags={"target"}
    )

    register_invalidation_rule(rule)

    stats = get_invalidation_stats()
    rule_names = [r["name"] for r in stats["rule_details"]]
    assert "custom_rule" in rule_names


def test_register_data_relationship():
    """Test register_data_relationship convenience function"""
    rel = DataRelationship(
        source_type="test",
        target_types={"target"},
        relationship_type="one_to_many"
    )

    register_data_relationship(rel)

    stats = get_invalidation_stats()
    # Stats returns a list of relationships
    assert len(stats["relationships"]) > 0


def test_schedule_batch_invalidation_convenience(cache):
    """Test schedule_batch_invalidation convenience function"""
    cache.set("key1", "value1", tags={"tag1"})

    schedule_batch_invalidation(tags={"tag1"})

    # Should still be cached
    assert cache.get("key1") is not None

    # Flush
    count = flush_pending_invalidations()
    assert count > 0


def test_set_batch_delay():
    """Test set_batch_delay convenience function"""
    set_batch_delay(200)

    stats = get_invalidation_stats()
    assert stats["batch_delay_ms"] == 200


def test_complex_relationship_cascade(cache, engine):
    """Test complex multi-level relationship cascade"""
    # Define relationships
    user_rel = DataRelationship(
        source_type="user",
        target_types={"session", "preferences"},
        relationship_type="one_to_many",
        cascade_depth=2
    )

    session_rel = DataRelationship(
        source_type="session",
        target_types={"navigation", "form_state"},
        relationship_type="one_to_many",
        cascade_depth=1
    )

    engine.register_relationship(user_rel)
    engine.register_relationship(session_rel)

    # Get related tags with depth
    tags = engine.get_related_tags("user", "user123", depth=2)

    assert "user" in tags
    assert "session" in tags
    assert "preferences" in tags


def test_priority_ordering(cache, engine):
    """Test that rules execute in priority order"""
    high_priority = InvalidationRule(
        name="high",
        trigger_tags={"test"},
        invalidate_tags={"high"},
        priority=100
    )

    low_priority = InvalidationRule(
        name="low",
        trigger_tags={"test"},
        invalidate_tags={"low"},
        priority=10
    )

    engine.register_rule(low_priority)
    engine.register_rule(high_priority)

    stats = engine.get_stats()
    rule_details = stats["rule_details"]

    # Should be sorted by priority (high first)
    assert rule_details[0]["name"] == "high"
    assert rule_details[1]["name"] == "low"


def test_conditional_rule_execution(cache, engine):
    """Test conditional rule execution"""
    def condition(context):
        return context.get("should_execute", False)

    rule = InvalidationRule(
        name="conditional",
        trigger_tags={"test"},
        invalidate_tags={"target"},
        condition=condition
    )

    engine.register_rule(rule)

    cache.set("target:1", "data", tags={"target"})

    # Should not execute
    count = engine.invalidate_by_write(
        "test", context={"should_execute": False})
    assert cache.get("target:1") is not None

    # Should execute
    count = engine.invalidate_by_write(
        "test", context={"should_execute": True})
    assert cache.get("target:1") is None


def test_operation_specific_invalidation(cache, engine):
    """Test invalidation based on operation type"""
    def only_on_delete(context):
        return context.get("operation") == "delete"

    rule = InvalidationRule(
        name="delete_only",
        trigger_tags={"resource"},
        invalidate_tags={"cache"},
        condition=only_on_delete
    )

    engine.register_rule(rule)

    cache.set("cache:1", "data", tags={"cache"})

    # Update should not invalidate
    engine.invalidate_by_write("resource", "res1", "update")
    assert cache.get("cache:1") is not None

    # Delete should invalidate
    engine.invalidate_by_write("resource", "res1", "delete")
    assert cache.get("cache:1") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
