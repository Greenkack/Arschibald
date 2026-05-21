"""
Tests für Phase 10: Cache Extensions
======================================

Test-Coverage für:
- Cache Invalidation Engine (core/cache_invalidation.py)
- Cache Monitoring (core/cache_monitoring.py)
- Cache Warming (core/cache_warming.py)

Ausführen:
    pytest tests/test_phase10_cache_extensions.py -v
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import der zu testenden Module
try:
    from core.cache_invalidation import (
        InvalidationEngine,
        InvalidationRule,
        CacheRelationship,
        invalidate_by_tag,
        invalidate_by_pattern,
        add_invalidation_rule,
        get_invalidation_stats
    )
    from core.cache_monitoring import (
        CacheMonitor,
        CacheMetrics,
        get_cache_monitor,
        PerformanceAnalyzer,
        AlertManager
    )
    from core.cache_warming import (
        CacheWarmer,
        WarmingTask,
        WarmingStrategy,
        get_cache_warmer
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    pytest.skip(f"Cache Extensions nicht verfügbar: {e}", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_cache():
    """Mock-Cache mit dict-basiertem Storage."""
    cache = Mock()
    cache.storage = {}
    cache.tags = {}  # Tag -> Keys mapping
    
    def get(key, default=None):
        return cache.storage.get(key, default)
    
    def set(key, value, tags=None):
        cache.storage[key] = value
        if tags:
            for tag in tags:
                if tag not in cache.tags:
                    cache.tags[tag] = []
                cache.tags[tag].append(key)
        return True
    
    def delete(key):
        if key in cache.storage:
            del cache.storage[key]
            # Remove from tags
            for tag, keys in cache.tags.items():
                if key in keys:
                    keys.remove(key)
            return True
        return False
    
    def keys():
        return list(cache.storage.keys())
    
    cache.get = Mock(side_effect=get)
    cache.set = Mock(side_effect=set)
    cache.delete = Mock(side_effect=delete)
    cache.keys = Mock(side_effect=keys)
    
    return cache


@pytest.fixture
def invalidation_engine(mock_cache):
    """InvalidationEngine-Instanz mit Mock-Cache."""
    engine = InvalidationEngine(cache=mock_cache)
    return engine


@pytest.fixture
def cache_monitor(mock_cache):
    """CacheMonitor-Instanz mit Mock-Cache."""
    monitor = CacheMonitor(cache=mock_cache)
    return monitor


@pytest.fixture
def cache_warmer(mock_cache):
    """CacheWarmer-Instanz mit Mock-Cache."""
    warmer = CacheWarmer(cache=mock_cache)
    return warmer


@pytest.fixture
def sample_data():
    """Sample-Daten für Tests."""
    return {
        'user:1': {'id': 1, 'name': 'Alice'},
        'user:2': {'id': 2, 'name': 'Bob'},
        'session:abc': {'user_id': 1, 'token': 'abc'},
        'session:xyz': {'user_id': 2, 'token': 'xyz'},
        'product:100': {'id': 100, 'name': 'Widget'},
    }


# ============================================================================
# TEST CLASS: Invalidation Engine
# ============================================================================

class TestInvalidationEngine:
    """Tests für Cache Invalidation Engine."""
    
    def test_invalidate_single_tag(self, invalidation_engine, mock_cache, sample_data):
        """Test: Tag-basierte Invalidierung einzelner Key."""
        # Setup
        mock_cache.set('user:1', sample_data['user:1'], tags=['user:1'])
        mock_cache.set('user:2', sample_data['user:2'], tags=['user:2'])
        
        # Execute
        result = invalidation_engine.invalidate_by_tag('user:1')
        
        # Verify
        assert result['invalidated_count'] == 1
        assert 'user:1' not in mock_cache.storage
        assert 'user:2' in mock_cache.storage
    
    def test_invalidate_wildcard_tag(self, invalidation_engine, mock_cache, sample_data):
        """Test: Wildcard-Pattern für Tags."""
        # Setup
        mock_cache.set('user:1', sample_data['user:1'], tags=['user:1'])
        mock_cache.set('user:2', sample_data['user:2'], tags=['user:2'])
        mock_cache.set('product:100', sample_data['product:100'], tags=['product:100'])
        
        # Execute
        result = invalidation_engine.invalidate_by_tag('user:*')
        
        # Verify
        assert result['invalidated_count'] == 2
        assert 'user:1' not in mock_cache.storage
        assert 'user:2' not in mock_cache.storage
        assert 'product:100' in mock_cache.storage
    
    def test_invalidate_multiple_tags(self, invalidation_engine, mock_cache, sample_data):
        """Test: Mehrere Tags gleichzeitig invalidieren."""
        # Setup
        for key, value in sample_data.items():
            tag = key.split(':')[0] + ':' + key.split(':')[1]
            mock_cache.set(key, value, tags=[tag])
        
        # Execute
        result = invalidation_engine.invalidate_by_tag(['user:1', 'session:abc'])
        
        # Verify
        assert result['invalidated_count'] == 2
        assert 'user:1' not in mock_cache.storage
        assert 'session:abc' not in mock_cache.storage
        assert 'user:2' in mock_cache.storage
    
    def test_invalidate_by_pattern(self, invalidation_engine, mock_cache, sample_data):
        """Test: Regex-Pattern-Invalidierung."""
        # Setup
        for key, value in sample_data.items():
            mock_cache.set(key, value)
        
        # Execute
        result = invalidation_engine.invalidate_by_pattern(r'^user:\d+$')
        
        # Verify
        assert result['invalidated_count'] == 2
        assert 'user:1' not in mock_cache.storage
        assert 'user:2' not in mock_cache.storage
        assert 'session:abc' in mock_cache.storage
    
    def test_cascade_invalidation(self, invalidation_engine, mock_cache):
        """Test: Kaskadierende Invalidierung mit Relationships."""
        # Setup: User -> Sessions Relationship
        mock_cache.set('user:1', {'id': 1}, tags=['user:1'])
        mock_cache.set('session:abc', {'user_id': 1}, tags=['session:abc', 'user:1:sessions'])
        mock_cache.set('session:xyz', {'user_id': 1}, tags=['session:xyz', 'user:1:sessions'])
        
        relationship = CacheRelationship(
            name='user_sessions',
            parent_pattern='user:*',
            child_pattern='user:{id}:sessions',
            relationship_type='one_to_many'
        )
        invalidation_engine.add_relationship(relationship)
        
        # Execute: Invalidiere User (sollte auch Sessions invalidieren)
        result = invalidation_engine.invalidate_by_tag('user:1', cascade=True)
        
        # Verify
        assert result['invalidated_count'] >= 3  # user:1 + 2 sessions
        assert 'user:1' not in mock_cache.storage
        assert 'session:abc' not in mock_cache.storage
        assert 'session:xyz' not in mock_cache.storage
    
    def test_invalidation_rule(self, invalidation_engine, mock_cache):
        """Test: Regel-basierte Invalidierung."""
        # Setup
        mock_cache.set('user:1', {'status': 'active'}, tags=['user:1'])
        
        rule = InvalidationRule(
            name='invalidate_active_users',
            condition=lambda key, value: value.get('status') == 'active',
            action='invalidate',
            priority=10
        )
        invalidation_engine.add_rule(rule)
        
        # Execute
        result = invalidation_engine.apply_rules()
        
        # Verify
        assert result['rules_applied'] >= 1
        assert 'user:1' not in mock_cache.storage
    
    def test_batch_invalidation(self, invalidation_engine, mock_cache):
        """Test: Batch-Invalidierung für Performance."""
        # Setup: Viele Keys
        keys = [f'key:{i}' for i in range(100)]
        for key in keys:
            mock_cache.set(key, {'value': key}, tags=[key])
        
        # Execute: Batch-Invalidierung
        start = time.time()
        result = invalidation_engine.invalidate_batch(keys[:50])
        duration = time.time() - start
        
        # Verify
        assert result['invalidated_count'] == 50
        assert duration < 0.1  # Sollte <100ms dauern
        assert len(mock_cache.storage) == 50
    
    def test_get_invalidation_stats(self, invalidation_engine, mock_cache, sample_data):
        """Test: Statistiken abrufen."""
        # Setup
        for key, value in sample_data.items():
            tag = key
            mock_cache.set(key, value, tags=[tag])
        
        # Execute einige Invalidierungen
        invalidation_engine.invalidate_by_tag('user:1')
        invalidation_engine.invalidate_by_tag('user:2')
        
        # Get Stats
        stats = invalidation_engine.get_stats()
        
        # Verify
        assert stats['total_invalidations'] >= 2
        assert stats['tags_invalidated'] >= 2
        assert 'avg_invalidation_time_ms' in stats
    
    def test_clear_all_cache(self, invalidation_engine, mock_cache, sample_data):
        """Test: Kompletten Cache leeren."""
        # Setup
        for key, value in sample_data.items():
            mock_cache.set(key, value)
        
        # Execute
        result = invalidation_engine.clear_all()
        
        # Verify
        assert result['invalidated_count'] == len(sample_data)
        assert len(mock_cache.storage) == 0


# ============================================================================
# TEST CLASS: Invalidation Rules
# ============================================================================

class TestInvalidationRules:
    """Tests für Invalidation Rules."""
    
    def test_rule_priority(self, invalidation_engine):
        """Test: Rules werden nach Priorität ausgeführt."""
        execution_order = []
        
        rule1 = InvalidationRule(
            name='low_priority',
            condition=lambda k, v: True,
            action=lambda: execution_order.append('low'),
            priority=1
        )
        
        rule2 = InvalidationRule(
            name='high_priority',
            condition=lambda k, v: True,
            action=lambda: execution_order.append('high'),
            priority=10
        )
        
        invalidation_engine.add_rule(rule1)
        invalidation_engine.add_rule(rule2)
        invalidation_engine.apply_rules()
        
        # High priority zuerst
        assert execution_order == ['high', 'low']
    
    def test_conditional_rule(self, invalidation_engine, mock_cache):
        """Test: Regel nur bei Condition."""
        mock_cache.set('user:1', {'age': 25}, tags=['user:1'])
        mock_cache.set('user:2', {'age': 17}, tags=['user:2'])
        
        rule = InvalidationRule(
            name='invalidate_adults',
            condition=lambda k, v: v.get('age', 0) >= 18,
            action='invalidate',
            priority=1
        )
        invalidation_engine.add_rule(rule)
        
        invalidation_engine.apply_rules()
        
        # Nur Erwachsene invalidiert
        assert 'user:1' not in mock_cache.storage
        assert 'user:2' in mock_cache.storage
    
    def test_rule_removal(self, invalidation_engine):
        """Test: Rules entfernen."""
        rule = InvalidationRule(
            name='test_rule',
            condition=lambda k, v: True,
            action='invalidate',
            priority=1
        )
        
        invalidation_engine.add_rule(rule)
        assert len(invalidation_engine.rules) == 1
        
        invalidation_engine.remove_rule('test_rule')
        assert len(invalidation_engine.rules) == 0
    
    def test_rule_update(self, invalidation_engine):
        """Test: Bestehende Rule updaten."""
        rule1 = InvalidationRule(name='test', condition=lambda k, v: False, action='invalidate', priority=1)
        rule2 = InvalidationRule(name='test', condition=lambda k, v: True, action='invalidate', priority=10)
        
        invalidation_engine.add_rule(rule1)
        assert invalidation_engine.rules[0].priority == 1
        
        invalidation_engine.add_rule(rule2)  # Update
        assert invalidation_engine.rules[0].priority == 10
    
    def test_rule_action_types(self, invalidation_engine, mock_cache):
        """Test: Verschiedene Action-Types."""
        mock_cache.set('key1', {'value': 1}, tags=['key1'])
        
        # Action als String
        rule1 = InvalidationRule(name='r1', condition=lambda k, v: True, action='invalidate', priority=1)
        
        # Action als Callable
        action_called = False
        def custom_action():
            nonlocal action_called
            action_called = True
        
        rule2 = InvalidationRule(name='r2', condition=lambda k, v: True, action=custom_action, priority=2)
        
        invalidation_engine.add_rule(rule1)
        invalidation_engine.add_rule(rule2)
        invalidation_engine.apply_rules()
        
        assert action_called


# ============================================================================
# TEST CLASS: Cache Monitor
# ============================================================================

class TestCacheMonitor:
    """Tests für Cache Monitoring."""
    
    def test_track_hit(self, cache_monitor):
        """Test: Cache Hit tracken."""
        cache_monitor.track_hit('user:1')
        
        metrics = cache_monitor.get_metrics()
        assert metrics['total_hits'] == 1
        assert metrics['total_accesses'] == 1
        assert metrics['hit_rate'] == 1.0
    
    def test_track_miss(self, cache_monitor):
        """Test: Cache Miss tracken."""
        cache_monitor.track_miss('user:999')
        
        metrics = cache_monitor.get_metrics()
        assert metrics['total_misses'] == 1
        assert metrics['total_accesses'] == 1
        assert metrics['hit_rate'] == 0.0
    
    def test_hit_rate_calculation(self, cache_monitor):
        """Test: Hit-Rate korrekt berechnen."""
        # 3 Hits, 2 Misses = 60% Hit-Rate
        for _ in range(3):
            cache_monitor.track_hit('key')
        for _ in range(2):
            cache_monitor.track_miss('key')
        
        metrics = cache_monitor.get_metrics()
        assert metrics['hit_rate'] == 0.6
        assert metrics['total_accesses'] == 5
    
    def test_track_operation_time(self, cache_monitor):
        """Test: Operation-Zeit tracken."""
        cache_monitor.track_operation('get', duration_ms=12.5)
        cache_monitor.track_operation('set', duration_ms=8.3)
        
        metrics = cache_monitor.get_metrics()
        assert metrics['avg_get_time_ms'] == 12.5
        assert metrics['avg_set_time_ms'] == 8.3
    
    def test_track_cache_size(self, cache_monitor, mock_cache):
        """Test: Cache-Size tracken."""
        mock_cache.storage = {'k1': 'v1', 'k2': 'v2'}
        
        cache_monitor.track_size()
        
        metrics = cache_monitor.get_metrics()
        assert metrics['current_size'] == 2
    
    def test_get_analytics(self, cache_monitor):
        """Test: Analytics-Daten abrufen."""
        # Simuliere Aktivität
        for i in range(10):
            if i % 2 == 0:
                cache_monitor.track_hit(f'key{i}')
            else:
                cache_monitor.track_miss(f'key{i}')
        
        analytics = cache_monitor.get_analytics()
        
        assert 'hit_rate_trend' in analytics
        assert 'hot_keys' in analytics
        assert 'cold_keys' in analytics
        assert analytics['hit_rate'] == 0.5
    
    def test_performance_alerts(self, cache_monitor):
        """Test: Performance-Alerts bei schlechter Hit-Rate."""
        # Hit-Rate unter Threshold
        for _ in range(10):
            cache_monitor.track_miss('key')
        
        alerts = cache_monitor.get_alerts()
        
        assert len(alerts) > 0
        assert any('hit rate' in alert.lower() for alert in alerts)
    
    def test_clear_metrics(self, cache_monitor):
        """Test: Metriken zurücksetzen."""
        cache_monitor.track_hit('key')
        cache_monitor.track_miss('key')
        
        cache_monitor.clear_metrics()
        
        metrics = cache_monitor.get_metrics()
        assert metrics['total_hits'] == 0
        assert metrics['total_misses'] == 0


# ============================================================================
# TEST CLASS: Metrics Collector
# ============================================================================

class TestMetricsCollector:
    """Tests für Metrics-Collection."""
    
    def test_collect_time_series(self, cache_monitor):
        """Test: Time-Series Metriken sammeln."""
        for i in range(5):
            cache_monitor.track_hit('key')
            time.sleep(0.01)
        
        time_series = cache_monitor.get_time_series(interval='1s', duration='10s')
        
        assert len(time_series) > 0
        assert all('timestamp' in point for point in time_series)
        assert all('hit_rate' in point for point in time_series)
    
    def test_aggregate_metrics(self, cache_monitor):
        """Test: Aggregierte Metriken."""
        # Verschiedene Keys tracken
        for i in range(100):
            key = f'key{i % 10}'  # 10 verschiedene Keys
            if i % 3 == 0:
                cache_monitor.track_hit(key)
            else:
                cache_monitor.track_miss(key)
        
        aggregates = cache_monitor.get_aggregates()
        
        assert 'avg_hit_rate' in aggregates
        assert 'max_hit_rate' in aggregates
        assert 'min_hit_rate' in aggregates
        assert aggregates['total_keys'] == 10
    
    def test_key_statistics(self, cache_monitor):
        """Test: Per-Key-Statistiken."""
        # Key A: 8 Hits, 2 Misses = 80%
        for _ in range(8):
            cache_monitor.track_hit('keyA')
        for _ in range(2):
            cache_monitor.track_miss('keyA')
        
        # Key B: 2 Hits, 8 Misses = 20%
        for _ in range(2):
            cache_monitor.track_hit('keyB')
        for _ in range(8):
            cache_monitor.track_miss('keyB')
        
        key_stats = cache_monitor.get_key_statistics()
        
        assert key_stats['keyA']['hit_rate'] == 0.8
        assert key_stats['keyB']['hit_rate'] == 0.2
    
    def test_export_metrics(self, cache_monitor):
        """Test: Metriken exportieren (JSON)."""
        cache_monitor.track_hit('key')
        
        export = cache_monitor.export_metrics(format='json')
        
        assert 'total_hits' in export
        assert 'timestamp' in export
    
    def test_metrics_retention(self, cache_monitor):
        """Test: Alte Metriken werden entfernt (Ring-Buffer)."""
        # Fülle Ring-Buffer über Limit
        for i in range(10000):
            cache_monitor.track_hit(f'key{i}')
        
        time_series = cache_monitor.get_time_series()
        
        # Sollte auf Max-Size limitiert sein
        assert len(time_series) <= 1000  # Angenommenes Limit


# ============================================================================
# TEST CLASS: Performance Analyzer
# ============================================================================

class TestPerformanceAnalyzer:
    """Tests für Performance-Analyse."""
    
    def test_identify_hot_keys(self, cache_monitor):
        """Test: Hot Keys identifizieren."""
        # Key1: Viele Accesses
        for _ in range(100):
            cache_monitor.track_hit('hot_key')
        
        # Key2: Wenige Accesses
        cache_monitor.track_hit('cold_key')
        
        hot_keys = cache_monitor.get_hot_keys(limit=1)
        
        assert len(hot_keys) == 1
        assert hot_keys[0]['key'] == 'hot_key'
        assert hot_keys[0]['access_count'] == 100
    
    def test_identify_cold_keys(self, cache_monitor):
        """Test: Cold Keys identifizieren."""
        cache_monitor.track_miss('cold_key1')
        cache_monitor.track_miss('cold_key2')
        
        for _ in range(50):
            cache_monitor.track_hit('hot_key')
        
        cold_keys = cache_monitor.get_cold_keys(limit=2)
        
        assert len(cold_keys) == 2
        assert all(key['key'] in ['cold_key1', 'cold_key2'] for key in cold_keys)
    
    def test_performance_recommendations(self, cache_monitor):
        """Test: Performance-Empfehlungen generieren."""
        # Schlechte Hit-Rate simulieren
        for _ in range(90):
            cache_monitor.track_miss('key')
        for _ in range(10):
            cache_monitor.track_hit('key')
        
        recommendations = cache_monitor.get_recommendations()
        
        assert len(recommendations) > 0
        assert any('hit rate' in rec.lower() for rec in recommendations)
    
    def test_bottleneck_detection(self, cache_monitor):
        """Test: Bottlenecks erkennen."""
        # Langsame Operations simulieren
        for _ in range(10):
            cache_monitor.track_operation('get', duration_ms=500)  # 500ms = langsam!
        
        bottlenecks = cache_monitor.get_bottlenecks()
        
        assert len(bottlenecks) > 0
        assert any('get' in bn['operation'] for bn in bottlenecks)


# ============================================================================
# TEST CLASS: Cache Warmer
# ============================================================================

class TestCacheWarmer:
    """Tests für Cache Warming."""
    
    def test_register_warming_task(self, cache_warmer):
        """Test: Warming-Task registrieren."""
        task = WarmingTask(
            name='warm_users',
            keys=['user:1', 'user:2'],
            loader=lambda key: {'id': key},
            schedule='0 6 * * *',
            priority='HIGH'
        )
        
        cache_warmer.register_task(task)
        
        tasks = cache_warmer.get_tasks()
        assert len(tasks) == 1
        assert tasks[0].name == 'warm_users'
    
    def test_execute_warming_task(self, cache_warmer, mock_cache):
        """Test: Warming-Task ausführen."""
        def loader(key):
            return {'id': key, 'loaded': True}
        
        task = WarmingTask(
            name='warm_test',
            keys=['key1', 'key2', 'key3'],
            loader=loader,
            priority='HIGH'
        )
        
        cache_warmer.register_task(task)
        result = cache_warmer.execute_task('warm_test')
        
        assert result['warmed_count'] == 3
        assert 'key1' in mock_cache.storage
        assert mock_cache.storage['key1']['loaded'] is True
    
    def test_warm_all_tasks(self, cache_warmer, mock_cache):
        """Test: Alle Tasks ausführen."""
        task1 = WarmingTask(name='t1', keys=['k1'], loader=lambda k: {'v': 1}, priority='HIGH')
        task2 = WarmingTask(name='t2', keys=['k2'], loader=lambda k: {'v': 2}, priority='HIGH')
        
        cache_warmer.register_task(task1)
        cache_warmer.register_task(task2)
        
        result = cache_warmer.warm_all()
        
        assert result['tasks_executed'] == 2
        assert result['total_warmed'] == 2
        assert 'k1' in mock_cache.storage
        assert 'k2' in mock_cache.storage
    
    def test_warming_strategy_eager(self, cache_warmer, mock_cache):
        """Test: EAGER Warming-Strategie."""
        task = WarmingTask(
            name='eager_task',
            keys=['k1', 'k2'],
            loader=lambda k: {'value': k},
            strategy=WarmingStrategy.EAGER,
            priority='HIGH'
        )
        
        cache_warmer.register_task(task)
        cache_warmer.execute_task('eager_task')
        
        # EAGER: Alle Keys sofort laden
        assert len(mock_cache.storage) == 2
    
    def test_warming_strategy_lazy(self, cache_warmer, mock_cache):
        """Test: LAZY Warming-Strategie."""
        task = WarmingTask(
            name='lazy_task',
            keys=['k1', 'k2', 'k3'],
            loader=lambda k: {'value': k},
            strategy=WarmingStrategy.LAZY,
            priority='LOW'
        )
        
        cache_warmer.register_task(task)
        # LAZY: Keys werden erst bei Bedarf geladen
        # (Im Mock nicht testbar, da kein Request-Context)
    
    def test_task_priority(self, cache_warmer):
        """Test: Tasks nach Priorität sortiert."""
        task_high = WarmingTask(name='high', keys=[], loader=lambda k: {}, priority='HIGH')
        task_low = WarmingTask(name='low', keys=[], loader=lambda k: {}, priority='LOW')
        task_medium = WarmingTask(name='medium', keys=[], loader=lambda k: {}, priority='MEDIUM')
        
        cache_warmer.register_task(task_low)
        cache_warmer.register_task(task_high)
        cache_warmer.register_task(task_medium)
        
        tasks = cache_warmer.get_tasks(sorted_by_priority=True)
        
        # HIGH -> MEDIUM -> LOW
        assert tasks[0].name == 'high'
        assert tasks[1].name == 'medium'
        assert tasks[2].name == 'low'
    
    def test_scheduled_warming(self, cache_warmer):
        """Test: Geplante Warming-Ausführung (Cron-Pattern)."""
        task = WarmingTask(
            name='scheduled',
            keys=['key1'],
            loader=lambda k: {},
            schedule='0 6 * * *',  # Täglich 6 Uhr
            priority='MEDIUM'
        )
        
        cache_warmer.register_task(task)
        
        # Check ob Schedule korrekt gespeichert
        tasks = cache_warmer.get_tasks()
        assert tasks[0].schedule == '0 6 * * *'
    
    def test_auto_warming(self, cache_warmer, cache_monitor):
        """Test: Auto-Warming bei niedriger Hit-Rate."""
        # Simuliere niedrige Hit-Rate
        for _ in range(90):
            cache_monitor.track_miss('key')
        for _ in range(10):
            cache_monitor.track_hit('key')
        
        # Enable Auto-Warming
        cache_warmer.enable_auto_warming(min_hit_rate=0.50, monitor=cache_monitor)
        
        # Auto-Warming sollte triggern
        result = cache_warmer.check_auto_warming()
        
        assert result['triggered'] is True
        assert result['reason'] == 'low_hit_rate'


# ============================================================================
# TEST CLASS: Warming Tasks
# ============================================================================

class TestWarmingTasks:
    """Tests für Warming-Task-Verwaltung."""
    
    def test_remove_task(self, cache_warmer):
        """Test: Task entfernen."""
        task = WarmingTask(name='test', keys=[], loader=lambda k: {}, priority='LOW')
        
        cache_warmer.register_task(task)
        assert len(cache_warmer.get_tasks()) == 1
        
        cache_warmer.remove_task('test')
        assert len(cache_warmer.get_tasks()) == 0
    
    def test_update_task(self, cache_warmer):
        """Test: Task updaten."""
        task1 = WarmingTask(name='test', keys=['k1'], loader=lambda k: {}, priority='LOW')
        task2 = WarmingTask(name='test', keys=['k1', 'k2'], loader=lambda k: {}, priority='HIGH')
        
        cache_warmer.register_task(task1)
        assert len(cache_warmer.get_tasks()[0].keys) == 1
        
        cache_warmer.register_task(task2)  # Update
        assert len(cache_warmer.get_tasks()[0].keys) == 2
        assert cache_warmer.get_tasks()[0].priority == 'HIGH'
    
    def test_get_task_stats(self, cache_warmer, mock_cache):
        """Test: Task-Statistiken abrufen."""
        task = WarmingTask(name='test', keys=['k1', 'k2'], loader=lambda k: {'v': k}, priority='HIGH')
        
        cache_warmer.register_task(task)
        cache_warmer.execute_task('test')
        
        stats = cache_warmer.get_task_stats('test')
        
        assert stats['executions'] >= 1
        assert stats['warmed_count'] == 2
        assert 'avg_duration_ms' in stats


# ============================================================================
# TEST CLASS: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration-Tests für alle Module zusammen."""
    
    def test_full_workflow(self, mock_cache):
        """Test: Kompletter Workflow (Invalidate → Monitor → Warm)."""
        # Setup
        invalidation_engine = InvalidationEngine(cache=mock_cache)
        cache_monitor = CacheMonitor(cache=mock_cache)
        cache_warmer = CacheWarmer(cache=mock_cache)
        
        # 1. Cache mit Daten füllen
        mock_cache.set('user:1', {'name': 'Alice'}, tags=['user:1'])
        mock_cache.set('user:2', {'name': 'Bob'}, tags=['user:2'])
        
        # 2. Monitoring
        cache_monitor.track_hit('user:1')
        cache_monitor.track_miss('user:3')
        
        metrics = cache_monitor.get_metrics()
        assert metrics['hit_rate'] == 0.5
        
        # 3. Invalidierung
        result = invalidation_engine.invalidate_by_tag('user:1')
        assert result['invalidated_count'] == 1
        assert 'user:1' not in mock_cache.storage
        
        # 4. Warming
        task = WarmingTask(
            name='rewarm_users',
            keys=['user:1', 'user:3'],
            loader=lambda k: {'name': f'User {k}'},
            priority='HIGH'
        )
        cache_warmer.register_task(task)
        warm_result = cache_warmer.execute_task('rewarm_users')
        
        assert warm_result['warmed_count'] == 2
        assert 'user:1' in mock_cache.storage
        assert 'user:3' in mock_cache.storage
    
    def test_end_to_end_with_relationships(self, mock_cache):
        """Test: End-to-End mit Relationships."""
        invalidation_engine = InvalidationEngine(cache=mock_cache)
        
        # Setup: User mit Sessions
        mock_cache.set('user:1', {'name': 'Alice'}, tags=['user:1'])
        mock_cache.set('session:abc', {'user_id': 1}, tags=['user:1:sessions'])
        
        # Relationship
        rel = CacheRelationship(
            name='user_sessions',
            parent_pattern='user:*',
            child_pattern='user:{id}:sessions',
            relationship_type='one_to_many'
        )
        invalidation_engine.add_relationship(rel)
        
        # Invalidate User (cascade zu Sessions)
        result = invalidation_engine.invalidate_by_tag('user:1', cascade=True)
        
        assert 'user:1' not in mock_cache.storage
        assert 'session:abc' not in mock_cache.storage


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("tag,expected_count", [
    ("user:1", 1),
    ("user:*", 3),
    ("session:*", 2),
    ("product:*", 1),
])
def test_parametrized_invalidation(invalidation_engine, mock_cache, tag, expected_count):
    """Parametrized Test: Verschiedene Tag-Patterns."""
    # Setup
    data = {
        'user:1': {}, 'user:2': {}, 'user:3': {},
        'session:a': {}, 'session:b': {},
        'product:100': {}
    }
    for key, value in data.items():
        mock_cache.set(key, value, tags=[key])
    
    # Execute
    result = invalidation_engine.invalidate_by_tag(tag)
    
    # Verify
    assert result['invalidated_count'] == expected_count


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
