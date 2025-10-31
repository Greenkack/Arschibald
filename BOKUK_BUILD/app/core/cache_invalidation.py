"""Tagged Cache Invalidation System with Smart Rules and Dependency Tracking"""

import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from re import Pattern
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .cache import get_cache, invalidate_cache


class InvalidationStrategy(Enum):
    """Cache invalidation strategies"""
    IMMEDIATE = "immediate"  # Invalidate immediately
    BATCHED = "batched"  # Batch invalidations for performance
    LAZY = "lazy"  # Mark as stale, invalidate on next access
    CASCADE = "cascade"  # Invalidate with all dependencies


@dataclass
class DataRelationship:
    """Define relationship between data entities for smart invalidation"""
    source_type: str  # e.g., "user", "product", "form"
    target_types: set[str]  # Related types to invalidate
    relationship_type: str  # "one_to_many", "many_to_many", "parent_child"
    bidirectional: bool = False  # If True, invalidate both directions
    cascade_depth: int = 1  # How many levels deep to cascade

    def get_related_tags(self, source_id: str = None) -> set[str]:
        """Get tags to invalidate based on relationship"""
        tags = set()

        # Add target type tags
        for target_type in self.target_types:
            tags.add(target_type)
            if source_id:
                tags.add(f"{target_type}:{source_id}")

        return tags


@dataclass
class InvalidationRule:
    """Enhanced cache invalidation rule with smart conditions"""
    name: str
    trigger_tags: set[str]
    invalidate_tags: set[str]
    condition: Callable[[dict[str, Any]], bool] | None = None
    strategy: InvalidationStrategy = InvalidationStrategy.IMMEDIATE
    priority: int = 0  # Higher priority rules execute first
    description: str = ""
    pattern: Pattern | None = None  # Regex pattern for key matching
    relationships: list[DataRelationship] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    last_executed: datetime | None = None
    total_invalidated: int = 0

    def should_execute(self, context: dict[str, Any] = None) -> bool:
        """Check if rule should execute"""
        if self.condition is None:
            return True
        return self.condition(context or {})

    def execute(self, context: dict[str, Any] = None) -> int:
        """Execute invalidation rule"""
        if not self.should_execute(context):
            return 0

        tags_to_invalidate = self.invalidate_tags.copy()

        # Add relationship-based tags
        if self.relationships and context:
            resource_id = context.get("resource_id")
            for relationship in self.relationships:
                related_tags = relationship.get_related_tags(resource_id)
                tags_to_invalidate.update(related_tags)

        # Apply pattern matching if specified
        if self.pattern and context:
            cache = get_cache()
            all_keys = cache.memory_cache.get_all_keys()
            matching_keys = [k for k in all_keys if self.pattern.match(k)]

            if matching_keys:
                count = invalidate_cache(keys=matching_keys)
                self._update_stats(count)
                return count

        # Standard tag-based invalidation
        count = invalidate_cache(tags=tags_to_invalidate)
        self._update_stats(count)

        logger.info(
            "Invalidation rule executed",
            rule=self.name,
            strategy=self.strategy.value,
            invalidated=count,
            trigger_tags=list(self.trigger_tags),
            invalidate_tags=list(tags_to_invalidate)
        )

        return count

    def _update_stats(self, count: int) -> None:
        """Update rule execution statistics"""
        self.execution_count += 1
        self.total_invalidated += count
        self.last_executed = datetime.now()


class CacheDependencyTracker:
    """Track cache dependencies for smart invalidation"""

    def __init__(self):
        self._dependencies: dict[str, set[str]] = defaultdict(set)
        self._reverse_deps: dict[str, set[str]] = defaultdict(set)
        self._lock = threading.RLock()

    def add_dependency(self, key: str, depends_on: set[str]) -> None:
        """
        Add cache dependency

        Args:
            key: Cache key
            depends_on: Set of keys this key depends on
        """
        with self._lock:
            self._dependencies[key].update(depends_on)

            # Update reverse dependencies
            for dep in depends_on:
                self._reverse_deps[dep].add(key)

            logger.debug(
                "Cache dependency added",
                key=key,
                depends_on=list(depends_on)
            )

    def get_dependencies(self, key: str) -> set[str]:
        """Get dependencies for a key"""
        with self._lock:
            return self._dependencies.get(key, set()).copy()

    def get_dependents(self, key: str) -> set[str]:
        """Get keys that depend on this key"""
        with self._lock:
            return self._reverse_deps.get(key, set()).copy()

    def get_all_dependents(self, key: str, recursive: bool = True) -> set[str]:
        """
        Get all dependent keys (optionally recursive)

        Args:
            key: Cache key
            recursive: If True, get transitive dependencies

        Returns:
            Set of all dependent keys
        """
        with self._lock:
            if not recursive:
                return self.get_dependents(key)

            # BFS to find all transitive dependents
            visited = set()
            queue = [key]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                dependents = self.get_dependents(current)

                for dep in dependents:
                    if dep not in visited:
                        queue.append(dep)

            # Remove the original key
            visited.discard(key)
            return visited

    def remove_dependency(self, key: str) -> None:
        """Remove all dependencies for a key"""
        with self._lock:
            # Remove from dependencies
            depends_on = self._dependencies.pop(key, set())

            # Remove from reverse dependencies
            for dep in depends_on:
                self._reverse_deps[dep].discard(key)

            # Remove from reverse deps if this key is a dependency
            for dependent in self._reverse_deps.pop(key, set()):
                self._dependencies[dependent].discard(key)

            logger.debug("Cache dependency removed", key=key)

    def clear(self) -> None:
        """Clear all dependencies"""
        with self._lock:
            self._dependencies.clear()
            self._reverse_deps.clear()
            logger.info("Cache dependencies cleared")


class InvalidationEngine:
    """Smart cache invalidation engine with batching and relationships"""

    def __init__(self):
        self._rules: dict[str, InvalidationRule] = {}
        self._dependency_tracker = CacheDependencyTracker()
        self._relationships: dict[str,
                                  list[DataRelationship]] = defaultdict(list)
        self._pending_invalidations: set[str] = set()
        self._pending_keys: set[str] = set()
        self._batch_timer: threading.Timer | None = None
        self._batch_delay_ms = 100
        self._write_triggers: dict[str, set[str]] = defaultdict(
            set)  # resource_type -> rule_names
        self._lock = threading.RLock()
        self._stats = {
            "total_invalidations": 0,
            "batched_invalidations": 0,
            "immediate_invalidations": 0,
            "cascade_invalidations": 0
        }

    def register_rule(self, rule: InvalidationRule) -> None:
        """Register invalidation rule"""
        with self._lock:
            self._rules[rule.name] = rule

            # Index rule by trigger tags for fast lookup
            for tag in rule.trigger_tags:
                resource_type = tag.split(":")[0]  # Extract base type
                self._write_triggers[resource_type].add(rule.name)

            # Register relationships
            for relationship in rule.relationships:
                self._relationships[relationship.source_type].append(
                    relationship)

            logger.info(
                "Invalidation rule registered",
                rule=rule.name,
                strategy=rule.strategy.value,
                priority=rule.priority,
                trigger_tags=list(rule.trigger_tags),
                invalidate_tags=list(rule.invalidate_tags),
                relationships=len(rule.relationships)
            )

    def unregister_rule(self, rule_name: str) -> bool:
        """Unregister invalidation rule"""
        with self._lock:
            if rule_name in self._rules:
                del self._rules[rule_name]
                logger.info("Invalidation rule unregistered", rule=rule_name)
                return True
            return False

    def add_dependency(self, key: str, depends_on: set[str]) -> None:
        """Add cache dependency"""
        self._dependency_tracker.add_dependency(key, depends_on)

    def register_relationship(self, relationship: DataRelationship) -> None:
        """Register data relationship for smart invalidation"""
        with self._lock:
            self._relationships[relationship.source_type].append(relationship)

            logger.info(
                "Data relationship registered",
                source=relationship.source_type,
                targets=list(relationship.target_types),
                type=relationship.relationship_type
            )

    def get_related_tags(
        self,
        resource_type: str,
        resource_id: str = None,
        depth: int = 1
    ) -> set[str]:
        """
        Get all related tags based on registered relationships

        Args:
            resource_type: Type of resource (e.g., "user", "form")
            resource_id: Optional specific resource ID
            depth: How many relationship levels to traverse

        Returns:
            Set of related tags to invalidate
        """
        tags = {resource_type}
        if resource_id:
            tags.add(f"{resource_type}:{resource_id}")

        if depth <= 0:
            return tags

        with self._lock:
            relationships = self._relationships.get(resource_type, [])

            for relationship in relationships:
                if relationship.cascade_depth >= depth:
                    related = relationship.get_related_tags(resource_id)
                    tags.update(related)

                    # Recursively get related tags if cascade depth allows
                    if depth > 1:
                        for target_type in relationship.target_types:
                            nested_tags = self.get_related_tags(
                                target_type,
                                resource_id,
                                depth - 1
                            )
                            tags.update(nested_tags)

        return tags

    def invalidate_by_write(
        self,
        resource_type: str,
        resource_id: str = None,
        operation: str = "update",
        context: dict[str, Any] = None
    ) -> int:
        """
        Invalidate cache after database write with smart relationship handling

        Args:
            resource_type: Type of resource written (e.g., 'user', 'form')
            resource_id: Optional resource ID
            operation: Type of operation ('create', 'update', 'delete')
            context: Additional context for conditional rules

        Returns:
            Number of cache entries invalidated
        """
        # Build context
        full_context = context or {}
        full_context.update({
            "resource_type": resource_type,
            "resource_id": resource_id,
            "operation": operation
        })

        # Get all related tags based on relationships
        related_tags = self.get_related_tags(
            resource_type, resource_id, depth=2)

        # Find matching rules (indexed lookup for performance)
        matching_rules = []
        with self._lock:
            rule_names = self._write_triggers.get(resource_type, set())
            for rule_name in rule_names:
                rule = self._rules.get(rule_name)
                if rule and (rule.trigger_tags & related_tags):
                    matching_rules.append(rule)

        # Sort by priority (higher first)
        matching_rules.sort(key=lambda r: r.priority, reverse=True)

        # Execute rules based on strategy
        total_invalidated = 0
        immediate_rules = []
        batched_rules = []

        for rule in matching_rules:
            if rule.strategy == InvalidationStrategy.IMMEDIATE:
                immediate_rules.append(rule)
            elif rule.strategy == InvalidationStrategy.BATCHED:
                batched_rules.append(rule)
            elif rule.strategy == InvalidationStrategy.CASCADE:
                # Execute cascade immediately with dependencies
                count = self._execute_cascade_invalidation(rule, full_context)
                total_invalidated += count
                self._stats["cascade_invalidations"] += 1

        # Execute immediate rules
        for rule in immediate_rules:
            count = rule.execute(full_context)
            total_invalidated += count
            self._stats["immediate_invalidations"] += 1

        # Schedule batched rules
        for rule in batched_rules:
            self.schedule_batch_invalidation(rule.invalidate_tags)
            self._stats["batched_invalidations"] += 1

        # Also invalidate direct tags immediately
        count = invalidate_cache(tags=related_tags)
        total_invalidated += count

        self._stats["total_invalidations"] += total_invalidated

        logger.info(
            "Cache invalidated by write",
            resource_type=resource_type,
            resource_id=resource_id,
            operation=operation,
            rules_executed=len(matching_rules),
            immediate=len(immediate_rules),
            batched=len(batched_rules),
            total_invalidated=total_invalidated
        )

        return total_invalidated

    def _execute_cascade_invalidation(
        self,
        rule: InvalidationRule,
        context: dict[str, Any]
    ) -> int:
        """Execute cascade invalidation with dependencies"""
        total = 0

        # Execute the rule
        count = rule.execute(context)
        total += count

        # Get all keys that were invalidated
        cache = get_cache()

        # For each invalidated tag, also invalidate dependencies
        for tag in rule.invalidate_tags:
            # Find keys with this tag
            all_keys = cache.memory_cache.get_all_keys()
            for key in all_keys:
                entry = cache.memory_cache.get_entry(key)
                if entry and tag in entry.tags:
                    # Invalidate with dependencies
                    dep_count = self.invalidate_with_dependencies(
                        key, recursive=True)
                    total += dep_count

        return total

    def invalidate_with_dependencies(
        self,
        key: str,
        recursive: bool = True
    ) -> int:
        """
        Invalidate key and all its dependents

        Args:
            key: Cache key to invalidate
            recursive: If True, invalidate transitive dependencies

        Returns:
            Number of entries invalidated
        """
        # Get all dependent keys
        dependents = self._dependency_tracker.get_all_dependents(
            key,
            recursive=recursive
        )

        # Add the original key
        keys_to_invalidate = {key} | dependents

        # Invalidate all keys
        count = invalidate_cache(keys=list(keys_to_invalidate))

        logger.info(
            "Cache invalidated with dependencies",
            key=key,
            dependents=len(dependents),
            total_invalidated=count
        )

        return count

    def schedule_batch_invalidation(
        self,
        tags: set[str] = None,
        keys: list[str] = None
    ) -> None:
        """
        Schedule batched invalidation for performance optimization

        Args:
            tags: Tags to invalidate
            keys: Specific keys to invalidate
        """
        with self._lock:
            if tags:
                self._pending_invalidations.update(tags)
            if keys:
                self._pending_keys.update(keys)

            # Cancel existing timer
            if self._batch_timer:
                self._batch_timer.cancel()

            # Schedule new batch
            self._batch_timer = threading.Timer(
                self._batch_delay_ms / 1000.0,
                self._execute_batch_invalidation
            )
            self._batch_timer.start()

            logger.debug(
                "Batch invalidation scheduled",
                tags=list(tags) if tags else [],
                keys=len(keys) if keys else 0,
                pending_tags=len(self._pending_invalidations),
                pending_keys=len(self._pending_keys)
            )

    def _execute_batch_invalidation(self) -> None:
        """Execute batched invalidation with optimization"""
        with self._lock:
            if not self._pending_invalidations and not self._pending_keys:
                return

            tags = self._pending_invalidations.copy()
            keys = list(self._pending_keys)
            self._pending_invalidations.clear()
            self._pending_keys.clear()
            self._batch_timer = None

        # Execute invalidation in single operation
        count = invalidate_cache(tags=tags, keys=keys)

        self._stats["total_invalidations"] += count

        logger.info(
            "Batch invalidation executed",
            tags=list(tags),
            keys_count=len(keys),
            invalidated=count
        )

    def flush_pending(self) -> int:
        """Immediately execute pending invalidations"""
        with self._lock:
            if self._batch_timer:
                self._batch_timer.cancel()
                self._batch_timer = None

            if not self._pending_invalidations and not self._pending_keys:
                return 0

            tags = self._pending_invalidations.copy()
            keys = list(self._pending_keys)
            self._pending_invalidations.clear()
            self._pending_keys.clear()

        count = invalidate_cache(tags=tags, keys=keys)
        self._stats["total_invalidations"] += count
        logger.info("Pending invalidations flushed", count=count)
        return count

    def set_batch_delay(self, delay_ms: int) -> None:
        """Set batch delay for performance tuning"""
        with self._lock:
            self._batch_delay_ms = max(10, min(delay_ms, 5000))  # 10ms to 5s
            logger.info("Batch delay updated", delay_ms=self._batch_delay_ms)

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive invalidation engine statistics"""
        with self._lock:
            return {
                "rules": len(self._rules),
                "relationships": sum(len(rels) for rels in self._relationships.values()),
                "pending_tags": len(self._pending_invalidations),
                "pending_keys": len(self._pending_keys),
                "batch_delay_ms": self._batch_delay_ms,
                "total_invalidations": self._stats["total_invalidations"],
                "immediate_invalidations": self._stats["immediate_invalidations"],
                "batched_invalidations": self._stats["batched_invalidations"],
                "cascade_invalidations": self._stats["cascade_invalidations"],
                "rule_details": [
                    {
                        "name": rule.name,
                        "strategy": rule.strategy.value,
                        "priority": rule.priority,
                        "execution_count": rule.execution_count,
                        "total_invalidated": rule.total_invalidated,
                        "last_executed": (
                            rule.last_executed.isoformat()
                            if rule.last_executed
                            else None
                        ),
                        "trigger_tags": list(rule.trigger_tags),
                        "invalidate_tags": list(rule.invalidate_tags)
                    }
                    for rule in sorted(
                        self._rules.values(),
                        key=lambda r: r.priority,
                        reverse=True
                    )
                ],
                "relationships": [
                    {
                        "source": source_type,
                        "targets": [
                            {
                                "types": list(rel.target_types),
                                "relationship": rel.relationship_type,
                                "cascade_depth": rel.cascade_depth
                            }
                            for rel in rels
                        ]
                    }
                    for source_type, rels in self._relationships.items()
                ]
            }


# Global invalidation engine
_invalidation_engine: InvalidationEngine | None = None
_engine_lock = threading.Lock()


def get_invalidation_engine() -> InvalidationEngine:
    """Get global invalidation engine"""
    global _invalidation_engine
    with _engine_lock:
        if _invalidation_engine is None:
            _invalidation_engine = InvalidationEngine()
            _setup_default_rules()
    return _invalidation_engine


def _setup_default_rules() -> None:
    """Setup default invalidation rules with smart relationships"""
    engine = _invalidation_engine

    # Define data relationships
    user_relationships = [
        DataRelationship(
            source_type="user",
            target_types={
                "user_session",
                "user_preferences",
                "user_forms",
                "navigation"},
            relationship_type="one_to_many",
            cascade_depth=2)]

    form_relationships = [
        DataRelationship(
            source_type="form",
            target_types={"form_state", "form_snapshot", "widget_state"},
            relationship_type="one_to_many",
            cascade_depth=1
        )
    ]

    product_relationships = [
        DataRelationship(
            source_type="product",
            target_types={"pricing", "calculation", "computed", "query"},
            relationship_type="one_to_many",
            cascade_depth=2
        )
    ]

    # User data changes invalidate user-related caches (immediate)
    engine.register_rule(InvalidationRule(
        name="user_data_invalidation",
        trigger_tags={"user", "user_profile"},
        invalidate_tags={"user_session", "user_preferences", "user_forms"},
        strategy=InvalidationStrategy.IMMEDIATE,
        priority=100,
        relationships=user_relationships,
        description="Invalidate user caches when user data changes"
    ))

    # Form changes invalidate form caches (batched for performance)
    engine.register_rule(InvalidationRule(
        name="form_data_invalidation",
        trigger_tags={"form", "form_data"},
        invalidate_tags={"form_state", "form_snapshot"},
        strategy=InvalidationStrategy.BATCHED,
        priority=50,
        relationships=form_relationships,
        description="Invalidate form caches when form data changes"
    ))

    # Session changes invalidate session caches (immediate)
    engine.register_rule(InvalidationRule(
        name="session_invalidation",
        trigger_tags={"session"},
        invalidate_tags={"user_session", "navigation"},
        strategy=InvalidationStrategy.IMMEDIATE,
        priority=90,
        description="Invalidate session caches when session changes"
    ))

    # Product/data changes invalidate computed results (cascade)
    engine.register_rule(InvalidationRule(
        name="data_change_invalidation",
        trigger_tags={"product", "pricing", "calculation"},
        invalidate_tags={"computed", "query"},
        strategy=InvalidationStrategy.CASCADE,
        priority=70,
        relationships=product_relationships,
        description="Invalidate computed caches when source data changes"
    ))

    # Widget state changes (batched for performance)
    engine.register_rule(InvalidationRule(
        name="widget_state_invalidation",
        trigger_tags={"widget", "widget_state"},
        invalidate_tags={"form_state"},
        strategy=InvalidationStrategy.BATCHED,
        priority=30,
        description="Invalidate form state when widget changes"
    ))

    # Job result changes (immediate)
    engine.register_rule(InvalidationRule(
        name="job_result_invalidation",
        trigger_tags={"job", "job_result"},
        invalidate_tags={"computed"},
        strategy=InvalidationStrategy.IMMEDIATE,
        priority=60,
        description="Invalidate computed caches when job completes"
    ))

    logger.info("Default invalidation rules setup complete", rules=6)


# Convenience functions
def invalidate_by_write(
    resource_type: str,
    resource_id: str = None,
    operation: str = "update",
    context: dict[str, Any] = None
) -> int:
    """
    Invalidate cache after database write

    Args:
        resource_type: Type of resource (e.g., 'user', 'form', 'product')
        resource_id: Optional specific resource ID
        operation: Type of operation ('create', 'update', 'delete')
        context: Additional context for conditional rules

    Returns:
        Number of cache entries invalidated
    """
    engine = get_invalidation_engine()
    return engine.invalidate_by_write(
        resource_type, resource_id, operation, context)


def add_cache_dependency(key: str, depends_on: set[str]) -> None:
    """
    Add cache dependency for smart invalidation

    Args:
        key: Cache key
        depends_on: Set of keys this key depends on
    """
    engine = get_invalidation_engine()
    engine.add_dependency(key, depends_on)


def invalidate_with_dependencies(key: str, recursive: bool = True) -> int:
    """
    Invalidate key and all its dependents

    Args:
        key: Cache key to invalidate
        recursive: If True, invalidate transitive dependencies

    Returns:
        Number of entries invalidated
    """
    engine = get_invalidation_engine()
    return engine.invalidate_with_dependencies(key, recursive)


def register_invalidation_rule(rule: InvalidationRule) -> None:
    """
    Register custom invalidation rule

    Args:
        rule: InvalidationRule to register
    """
    engine = get_invalidation_engine()
    engine.register_rule(rule)


def register_data_relationship(relationship: DataRelationship) -> None:
    """
    Register data relationship for smart invalidation

    Args:
        relationship: DataRelationship to register
    """
    engine = get_invalidation_engine()
    engine.register_relationship(relationship)


def schedule_batch_invalidation(
        tags: set[str] = None,
        keys: list[str] = None) -> None:
    """
    Schedule batched invalidation for performance

    Args:
        tags: Tags to invalidate
        keys: Specific keys to invalidate
    """
    engine = get_invalidation_engine()
    engine.schedule_batch_invalidation(tags, keys)


def flush_pending_invalidations() -> int:
    """
    Immediately execute pending invalidations

    Returns:
        Number of entries invalidated
    """
    engine = get_invalidation_engine()
    return engine.flush_pending()


def get_invalidation_stats() -> dict[str, Any]:
    """
    Get invalidation engine statistics

    Returns:
        Dictionary with statistics
    """
    engine = get_invalidation_engine()
    return engine.get_stats()


def set_batch_delay(delay_ms: int) -> None:
    """
    Set batch delay for performance tuning

    Args:
        delay_ms: Delay in milliseconds (10-5000)
    """
    engine = get_invalidation_engine()
    engine.set_batch_delay(delay_ms)
