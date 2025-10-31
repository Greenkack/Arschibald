# Tagged Cache Invalidation System

## Overview

The Tagged Cache Invalidation System provides smart, efficient cache invalidation with support for:

- **Tagged Invalidation**: Invalidate cache entries by tags
- **Data Relationships**: Define relationships between data types for smart cascade invalidation
- **Dependency Tracking**: Track cache dependencies and invalidate transitively
- **Batched Invalidation**: Batch multiple invalidations for performance optimization
- **Multiple Strategies**: Immediate, batched, lazy, and cascade invalidation strategies
- **Pattern Matching**: Invalidate cache entries matching regex patterns
- **Conditional Rules**: Execute invalidation rules based on custom conditions
- **Priority-Based Execution**: Control rule execution order with priorities
- **Database Write Triggers**: Automatically invalidate caches on database writes

## Core Concepts

### Invalidation Strategies

```python
class InvalidationStrategy(Enum):
    IMMEDIATE = "immediate"  # Invalidate immediately
    BATCHED = "batched"      # Batch invalidations for performance
    LAZY = "lazy"            # Mark as stale, invalidate on next access
    CASCADE = "cascade"      # Invalidate with all dependencies
```

### Data Relationships

Define relationships between data types to enable smart cascade invalidation:

```python
from core.cache_invalidation import DataRelationship

# When user changes, invalidate related session and preferences
user_relationship = DataRelationship(
    source_type="user",
    target_types={"session", "preferences", "navigation"},
    relationship_type="one_to_many",
    cascade_depth=2  # How many levels to cascade
)
```

### Invalidation Rules

Rules define when and how to invalidate caches:

```python
from core.cache_invalidation import InvalidationRule, InvalidationStrategy

rule = InvalidationRule(
    name="user_data_invalidation",
    trigger_tags={"user", "user_profile"},
    invalidate_tags={"session", "preferences"},
    strategy=InvalidationStrategy.IMMEDIATE,
    priority=100,  # Higher priority executes first
    relationships=[user_relationship],
    description="Invalidate user caches when user data changes"
)
```

## Quick Start

### Basic Invalidation on Database Write

```python
from core.cache_invalidation import invalidate_by_write

# After updating user in database
invalidate_by_write("user", "user123", "update")

# After deleting product
invalidate_by_write("product", "prod456", "delete")
```

### Register Custom Rules

```python
from core.cache_invalidation import (
    InvalidationRule,
    InvalidationStrategy,
    register_invalidation_rule
)

# Create custom rule
rule = InvalidationRule(
    name="custom_invalidation",
    trigger_tags={"custom_resource"},
    invalidate_tags={"related_cache"},
    strategy=InvalidationStrategy.BATCHED,
    priority=50
)

# Register it
register_invalidation_rule(rule)
```

### Define Data Relationships

```python
from core.cache_invalidation import (
    DataRelationship,
    register_data_relationship
)

# Define relationship
relationship = DataRelationship(
    source_type="order",
    target_types={"order_items", "inventory", "pricing"},
    relationship_type="one_to_many",
    cascade_depth=2
)

# Register it
register_data_relationship(relationship)
```

### Add Cache Dependencies

```python
from core.cache_invalidation import add_cache_dependency

# Define that computed_result depends on base_data
add_cache_dependency("computed_result", {"base_data", "config"})

# When base_data is invalidated, computed_result will also be invalidated
```

### Batch Invalidation for Performance

```python
from core.cache_invalidation import (
    schedule_batch_invalidation,
    flush_pending_invalidations,
    set_batch_delay
)

# Set batch delay (default 100ms)
set_batch_delay(200)  # 200ms

# Schedule batched invalidation
schedule_batch_invalidation(tags={"form_state", "widget_state"})

# Or flush immediately if needed
count = flush_pending_invalidations()
```

## Advanced Usage

### Pattern-Based Invalidation

Invalidate cache entries matching a regex pattern:

```python
import re
from core.cache_invalidation import InvalidationRule

rule = InvalidationRule(
    name="session_pattern",
    trigger_tags={"user"},
    invalidate_tags=set(),
    pattern=re.compile(r"user:\d+:session:.*"),
    strategy=InvalidationStrategy.IMMEDIATE
)

register_invalidation_rule(rule)
```

### Conditional Invalidation

Execute rules only when conditions are met:

```python
def only_on_delete(context):
    return context.get("operation") == "delete"

rule = InvalidationRule(
    name="delete_only",
    trigger_tags={"resource"},
    invalidate_tags={"cache"},
    condition=only_on_delete,
    strategy=InvalidationStrategy.IMMEDIATE
)
```

### Cascade Invalidation with Dependencies

```python
from core.cache_invalidation import invalidate_with_dependencies

# Invalidate key and all its dependents recursively
count = invalidate_with_dependencies("base_data", recursive=True)
```

### Multi-Level Relationships

```python
# Define cascading relationships
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

register_data_relationship(user_rel)
register_data_relationship(session_rel)

# When user changes, it cascades through session to navigation and form_state
```

## Default Rules

The system comes with pre-configured rules:

1. **user_data_invalidation** (Priority: 100, Immediate)
   - Triggers: `user`, `user_profile`
   - Invalidates: `user_session`, `user_preferences`, `user_forms`

2. **form_data_invalidation** (Priority: 50, Batched)
   - Triggers: `form`, `form_data`
   - Invalidates: `form_state`, `form_snapshot`

3. **session_invalidation** (Priority: 90, Immediate)
   - Triggers: `session`
   - Invalidates: `user_session`, `navigation`

4. **data_change_invalidation** (Priority: 70, Cascade)
   - Triggers: `product`, `pricing`, `calculation`
   - Invalidates: `computed`, `query`

5. **widget_state_invalidation** (Priority: 30, Batched)
   - Triggers: `widget`, `widget_state`
   - Invalidates: `form_state`

6. **job_result_invalidation** (Priority: 60, Immediate)
   - Triggers: `job`, `job_result`
   - Invalidates: `computed`

## Monitoring and Statistics

### Get Invalidation Statistics

```python
from core.cache_invalidation import get_invalidation_stats

stats = get_invalidation_stats()

print(f"Total rules: {stats['rules']}")
print(f"Total relationships: {stats['relationships']}")
print(f"Total invalidations: {stats['total_invalidations']}")
print(f"Immediate: {stats['immediate_invalidations']}")
print(f"Batched: {stats['batched_invalidations']}")
print(f"Cascade: {stats['cascade_invalidations']}")

# Rule details
for rule in stats['rule_details']:
    print(f"{rule['name']}: {rule['execution_count']} executions")
```

### Performance Tuning

```python
from core.cache_invalidation import set_batch_delay

# Adjust batch delay based on your needs
# Lower = more responsive, higher = better batching
set_batch_delay(50)   # 50ms for responsive apps
set_batch_delay(200)  # 200ms for better batching
```

## Integration with Database Operations

### Repository Pattern Integration

```python
class UserRepository:
    def update(self, user_id: str, data: dict):
        # Update database
        result = self.db.update("users", user_id, data)
        
        # Invalidate caches
        invalidate_by_write("user", user_id, "update", context={
            "fields_changed": list(data.keys())
        })
        
        return result
    
    def delete(self, user_id: str):
        # Delete from database
        result = self.db.delete("users", user_id)
        
        # Invalidate caches
        invalidate_by_write("user", user_id, "delete")
        
        return result
```

### Transaction Integration

```python
from core.database import run_tx
from core.cache_invalidation import invalidate_by_write

def update_user_with_cache_invalidation(user_id: str, data: dict):
    def transaction():
        # Update in transaction
        db.update("users", user_id, data)
        
        # Invalidate after successful commit
        invalidate_by_write("user", user_id, "update")
    
    return run_tx(transaction)
```

## Best Practices

### 1. Use Appropriate Strategies

- **Immediate**: For critical data (user sessions, authentication)
- **Batched**: For frequent updates (form auto-save, widget state)
- **Cascade**: For related data (product pricing, calculations)
- **Lazy**: For rarely accessed data

### 2. Set Proper Priorities

- High priority (90-100): Security, authentication, critical data
- Medium priority (50-80): Business logic, computed data
- Low priority (10-40): UI state, preferences

### 3. Define Clear Relationships

```python
# Good: Clear, specific relationships
DataRelationship(
    source_type="order",
    target_types={"order_items", "inventory"},
    relationship_type="one_to_many",
    cascade_depth=1
)

# Avoid: Too broad, may invalidate too much
DataRelationship(
    source_type="order",
    target_types={"*"},  # Don't do this
    cascade_depth=10     # Too deep
)
```

### 4. Use Conditional Rules Wisely

```python
# Good: Specific conditions
def only_on_price_change(context):
    return "price" in context.get("fields_changed", [])

# Avoid: Complex conditions that slow down execution
def complex_condition(context):
    # Don't do expensive operations here
    result = expensive_database_query()
    return result > threshold
```

### 5. Monitor Performance

```python
# Regularly check stats
stats = get_invalidation_stats()

# Adjust batch delay if needed
if stats['batched_invalidations'] > 1000:
    set_batch_delay(200)  # Increase batching
```

### 6. Tag Consistently

```python
# Good: Consistent tagging scheme
cache.set("user:123:profile", data, tags={"user", "user:123", "profile"})
cache.set("user:123:session", data, tags={"user", "user:123", "session"})

# Avoid: Inconsistent tags
cache.set("user_123_profile", data, tags={"usr", "u123"})
```

## Performance Considerations

### Batch Delay Tuning

- **10-50ms**: Highly responsive, less batching
- **100-200ms**: Balanced (default: 100ms)
- **200-500ms**: Maximum batching, slight delay

### Cascade Depth

- **Depth 1**: Direct relationships only
- **Depth 2**: Two levels (recommended maximum)
- **Depth 3+**: Use with caution, may invalidate too much

### Rule Count

- Keep rules focused and specific
- Avoid overlapping rules that invalidate the same data
- Use priorities to control execution order

## Troubleshooting

### Cache Not Invalidating

1. Check if tags match:
   ```python
   # Cache entry
   cache.set("key", "value", tags={"user", "user:123"})
   
   # Invalidation must use matching tags
   invalidate_by_write("user", "123")  # ✓ Matches
   invalidate_by_write("usr", "123")   # ✗ Doesn't match
   ```

2. Check rule conditions:
   ```python
   # Rule may have condition that's not met
   stats = get_invalidation_stats()
   print(stats['rule_details'])  # Check execution_count
   ```

3. Check batch timing:
   ```python
   # Batched invalidations may not execute immediately
   flush_pending_invalidations()  # Force immediate execution
   ```

### Too Many Invalidations

1. Check cascade depth:
   ```python
   # Reduce cascade depth
   relationship.cascade_depth = 1  # Instead of 2+
   ```

2. Use more specific tags:
   ```python
   # Instead of broad tags
   cache.set("key", "value", tags={"data"})  # Too broad
   
   # Use specific tags
   cache.set("key", "value", tags={"user_data", "user:123"})  # Better
   ```

3. Use batched strategy:
   ```python
   # Change from immediate to batched
   rule.strategy = InvalidationStrategy.BATCHED
   ```

## API Reference

### Functions

- `invalidate_by_write(resource_type, resource_id, operation, context)` - Invalidate on DB write
- `add_cache_dependency(key, depends_on)` - Add cache dependency
- `invalidate_with_dependencies(key, recursive)` - Invalidate with dependencies
- `register_invalidation_rule(rule)` - Register custom rule
- `register_data_relationship(relationship)` - Register data relationship
- `schedule_batch_invalidation(tags, keys)` - Schedule batched invalidation
- `flush_pending_invalidations()` - Flush pending invalidations
- `get_invalidation_stats()` - Get statistics
- `set_batch_delay(delay_ms)` - Set batch delay

### Classes

- `InvalidationStrategy` - Enum of invalidation strategies
- `DataRelationship` - Define data relationships
- `InvalidationRule` - Define invalidation rules
- `InvalidationEngine` - Core invalidation engine

## Examples

See `example_cache_invalidation_usage.py` for comprehensive examples including:

- Basic invalidation
- Data relationships
- Batched invalidation
- Cache dependencies
- Pattern-based invalidation
- Conditional rules
- Priority ordering
- Real-world scenarios

## Testing

Run tests:

```bash
pytest core/test_cache_invalidation.py -v
```

## Requirements Met

This implementation satisfies:

- **Requirement 4.3**: Related cache entries are invalidated immediately via cache-bust on data modification
- **Requirement 4.7**: CacheKeys uses namespaced keys to prevent collisions

The system provides smart, efficient cache invalidation with multiple strategies, data relationships, dependency tracking, and performance optimization through batching.
