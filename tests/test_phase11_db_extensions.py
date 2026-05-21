"""
Tests für Phase 11: Database Extensions
========================================

Test-Coverage für:
- DB Performance Monitor (core/db_performance.py)
- Query Tracker
- Slow Query Detection
- Connection Pool Monitoring

Ausführen:
    pytest tests/test_phase11_db_extensions.py -v
"""

import pytest
import time
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager
from typing import List, Dict, Any

# Import der zu testenden Module
try:
    from core.db_performance import (
        DBPerformanceMonitor,
        QueryTracker,
        QueryMetric,
        ConnectionPoolMetric,
        get_db_performance_monitor
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    pytest.skip(f"DB Extensions nicht verfügbar: {e}", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock-Datenbank-Connection."""
    conn = Mock(spec=sqlite3.Connection)
    cursor = Mock(spec=sqlite3.Cursor)
    
    cursor.execute = Mock(return_value=cursor)
    cursor.fetchall = Mock(return_value=[])
    cursor.fetchone = Mock(return_value=None)
    cursor.rowcount = 0
    
    conn.cursor = Mock(return_value=cursor)
    conn.execute = Mock(return_value=cursor)
    conn.commit = Mock()
    conn.rollback = Mock()
    conn.close = Mock()
    
    return conn


@pytest.fixture
def monitor():
    """DBPerformanceMonitor-Instanz."""
    return DBPerformanceMonitor()


@pytest.fixture
def sample_queries():
    """Sample SQL-Queries für Tests."""
    return {
        'select_users': "SELECT * FROM users WHERE active=1",
        'insert_user': "INSERT INTO users (name, email) VALUES (?, ?)",
        'update_user': "UPDATE users SET name=? WHERE id=?",
        'delete_user': "DELETE FROM users WHERE id=?",
        'join_query': "SELECT u.*, o.* FROM users u JOIN orders o ON u.id=o.user_id",
        'slow_query': "SELECT * FROM users u1 JOIN users u2 ON u1.id != u2.id",  # Cartesian
    }


# ============================================================================
# TEST CLASS: DB Performance Monitor
# ============================================================================

class TestDBPerformanceMonitor:
    """Tests für DB Performance Monitor."""
    
    def test_track_query_basic(self, monitor):
        """Test: Query tracken (Basis)."""
        sql = "SELECT * FROM users"
        
        with monitor.track_query(sql) as tracker:
            time.sleep(0.01)  # Simuliere Query-Ausführung
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 1
        assert stats['avg_duration_ms'] > 0
    
    def test_track_query_with_rows(self, monitor):
        """Test: Query mit Rows-Count tracken."""
        sql = "SELECT * FROM users"
        
        with monitor.track_query(sql) as tracker:
            time.sleep(0.005)
            tracker.record_rows(42)
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 1
        
        recent = monitor.get_recent_queries(limit=1)
        assert recent[0].rows_affected == 42
    
    def test_track_query_with_error(self, monitor):
        """Test: Query mit Error tracken."""
        sql = "SELECT * FROM nonexistent"
        
        with monitor.track_query(sql) as tracker:
            tracker.record_error("Table does not exist")
        
        stats = monitor.get_stats()
        assert stats['success_rate'] == 0.0
        assert stats['total_errors'] == 1
        
        recent = monitor.get_recent_queries(limit=1)
        assert recent[0].success is False
        assert recent[0].error == "Table does not exist"
    
    def test_track_multiple_queries(self, monitor):
        """Test: Mehrere Queries tracken."""
        queries = [
            "SELECT * FROM users",
            "SELECT * FROM orders",
            "SELECT * FROM products"
        ]
        
        for sql in queries:
            with monitor.track_query(sql):
                time.sleep(0.001)
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 3
    
    def test_success_rate_calculation(self, monitor):
        """Test: Success-Rate korrekt berechnen."""
        # 3 erfolgreiche, 2 fehlerhafte = 60%
        for i in range(3):
            with monitor.track_query(f"SELECT {i}"):
                pass
        
        for i in range(2):
            with monitor.track_query(f"SELECT {i}") as tracker:
                tracker.record_error("Error")
        
        stats = monitor.get_stats()
        assert stats['success_rate'] == 0.6
        assert stats['total_queries'] == 5
    
    def test_get_recent_queries(self, monitor):
        """Test: Letzte Queries abrufen."""
        for i in range(10):
            with monitor.track_query(f"SELECT {i}"):
                time.sleep(0.001)
        
        recent = monitor.get_recent_queries(limit=5)
        
        assert len(recent) == 5
        # Neueste zuerst
        assert "SELECT 9" in recent[0].sql
    
    def test_query_type_distribution(self, monitor, sample_queries):
        """Test: Query-Type-Distribution."""
        with monitor.track_query(sample_queries['select_users']):
            pass
        with monitor.track_query(sample_queries['insert_user']):
            pass
        with monitor.track_query(sample_queries['update_user']):
            pass
        with monitor.track_query(sample_queries['delete_user']):
            pass
        
        stats = monitor.get_stats()
        dist = stats['query_type_distribution']
        
        assert dist['SELECT'] == 1
        assert dist['INSERT'] == 1
        assert dist['UPDATE'] == 1
        assert dist['DELETE'] == 1
    
    def test_clear_metrics(self, monitor):
        """Test: Metriken zurücksetzen."""
        with monitor.track_query("SELECT 1"):
            pass
        
        monitor.clear_metrics()
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 0
        assert stats['avg_duration_ms'] == 0


# ============================================================================
# TEST CLASS: Query Tracker
# ============================================================================

class TestQueryTracker:
    """Tests für QueryTracker Context Manager."""
    
    def test_context_manager_success(self, monitor):
        """Test: Context Manager bei Erfolg."""
        with monitor.track_query("SELECT 1") as tracker:
            assert tracker.sql == "SELECT 1"
            assert tracker.start_time is not None
        
        # Nach Context: Query sollte getrackt sein
        stats = monitor.get_stats()
        assert stats['total_queries'] == 1
    
    def test_context_manager_exception(self, monitor):
        """Test: Context Manager bei Exception."""
        try:
            with monitor.track_query("SELECT 1") as tracker:
                raise ValueError("Test Error")
        except ValueError:
            pass
        
        # Query sollte trotzdem getrackt sein (mit Error)
        stats = monitor.get_stats()
        assert stats['total_queries'] == 1
        
        recent = monitor.get_recent_queries(limit=1)
        assert recent[0].success is False
    
    def test_manual_finish(self, monitor):
        """Test: Manuelle finish()-Call."""
        tracker = monitor.start_tracking("SELECT 1")
        time.sleep(0.01)
        tracker.finish()
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 1
        assert stats['avg_duration_ms'] > 0
    
    def test_record_success(self, monitor):
        """Test: Erfolg manuell tracken."""
        tracker = monitor.start_tracking("INSERT INTO users ...")
        tracker.record_success(rows_affected=5)
        tracker.finish()
        
        recent = monitor.get_recent_queries(limit=1)
        assert recent[0].success is True
        assert recent[0].rows_affected == 5
    
    def test_record_error(self, monitor):
        """Test: Fehler manuell tracken."""
        tracker = monitor.start_tracking("SELECT * FROM nonexistent")
        tracker.record_error("Table not found")
        tracker.finish()
        
        recent = monitor.get_recent_queries(limit=1)
        assert recent[0].success is False
        assert recent[0].error == "Table not found"
    
    def test_tracker_duration_calculation(self, monitor):
        """Test: Dauer korrekt berechnet."""
        with monitor.track_query("SELECT 1") as tracker:
            time.sleep(0.05)  # 50ms
        
        recent = monitor.get_recent_queries(limit=1)
        # Sollte ~50ms sein (±10ms Toleranz)
        assert 40 <= recent[0].duration_ms <= 60


# ============================================================================
# TEST CLASS: Slow Query Detection
# ============================================================================

class TestSlowQueryDetection:
    """Tests für Slow Query Detection."""
    
    def test_set_slow_query_threshold(self, monitor):
        """Test: Slow-Query-Threshold setzen."""
        monitor.set_slow_query_threshold(100)  # 100ms
        
        assert monitor.slow_query_threshold_ms == 100
    
    def test_detect_slow_query(self, monitor):
        """Test: Langsame Query erkennen."""
        monitor.set_slow_query_threshold(10)  # 10ms
        
        with monitor.track_query("SELECT * FROM big_table"):
            time.sleep(0.05)  # 50ms = langsam!
        
        slow_queries = monitor.get_slow_queries(limit=10)
        
        assert len(slow_queries) == 1
        assert slow_queries[0].duration_ms > 10
    
    def test_no_slow_queries_when_fast(self, monitor):
        """Test: Schnelle Queries nicht als slow markiert."""
        monitor.set_slow_query_threshold(100)  # 100ms
        
        with monitor.track_query("SELECT 1"):
            time.sleep(0.001)  # 1ms = schnell
        
        slow_queries = monitor.get_slow_queries(limit=10)
        
        assert len(slow_queries) == 0
    
    def test_get_slow_queries_limit(self, monitor):
        """Test: Limit für Slow Queries."""
        monitor.set_slow_query_threshold(1)  # Alle Queries sind "slow"
        
        for i in range(20):
            with monitor.track_query(f"SELECT {i}"):
                time.sleep(0.002)
        
        slow_queries = monitor.get_slow_queries(limit=5)
        
        assert len(slow_queries) == 5
    
    def test_slow_query_statistics(self, monitor):
        """Test: Slow-Query-Statistiken."""
        monitor.set_slow_query_threshold(10)
        
        # 2 langsame, 3 schnelle
        for i in range(2):
            with monitor.track_query(f"SLOW {i}"):
                time.sleep(0.05)  # 50ms
        
        for i in range(3):
            with monitor.track_query(f"FAST {i}"):
                time.sleep(0.001)  # 1ms
        
        stats = monitor.get_stats()
        
        assert stats['total_queries'] == 5
        assert stats['slow_queries'] == 2


# ============================================================================
# TEST CLASS: Connection Pool
# ============================================================================

class TestConnectionPool:
    """Tests für Connection Pool Monitoring."""
    
    def test_track_connection_acquired(self, monitor):
        """Test: Connection Acquire tracken."""
        monitor.track_connection_acquired(wait_time_ms=5.2)
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['active_connections'] == 1
        assert pool['avg_wait_time_ms'] == 5.2
    
    def test_track_connection_released(self, monitor):
        """Test: Connection Release tracken."""
        monitor.track_connection_acquired(wait_time_ms=1.0)
        monitor.track_connection_released()
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['active_connections'] == 0
        assert pool['idle_connections'] == 1
    
    def test_connection_pool_utilization(self, monitor):
        """Test: Pool-Auslastung berechnen."""
        monitor.set_max_connections(10)
        
        # 7 Connections aktiv = 70% Auslastung
        for _ in range(7):
            monitor.track_connection_acquired(wait_time_ms=1.0)
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['active_connections'] == 7
        assert pool['max_connections'] == 10
        utilization = pool['active_connections'] / pool['max_connections']
        assert utilization == 0.7
    
    def test_high_wait_time_alert(self, monitor):
        """Test: Alert bei hoher Wartezeit."""
        # Simuliere hohe Wartezeiten
        for _ in range(5):
            monitor.track_connection_acquired(wait_time_ms=200)  # 200ms = hoch!
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['avg_wait_time_ms'] == 200
        # Alert sollte getriggert werden (Implementation-abhängig)
    
    def test_connection_timeout_tracking(self, monitor):
        """Test: Connection-Timeouts tracken."""
        monitor.track_connection_timeout()
        monitor.track_connection_timeout()
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['connection_timeouts'] == 2
    
    def test_connection_error_tracking(self, monitor):
        """Test: Connection-Errors tracken."""
        monitor.track_connection_error("Connection refused")
        
        stats = monitor.get_stats()
        pool = stats['connection_pool']
        
        assert pool['connection_errors'] == 1


# ============================================================================
# TEST CLASS: Sampling Rate
# ============================================================================

class TestSamplingRate:
    """Tests für Query Sampling."""
    
    def test_set_sampling_rate(self, monitor):
        """Test: Sampling-Rate setzen."""
        monitor.set_sampling_rate(0.5)  # 50%
        
        assert monitor.sampling_rate == 0.5
    
    def test_sampling_reduces_tracking(self, monitor):
        """Test: Sampling reduziert getrackte Queries."""
        monitor.set_sampling_rate(0.1)  # 10% Sampling
        
        # 100 Queries, aber nur ~10 sollten getrackt werden
        for i in range(100):
            with monitor.track_query(f"SELECT {i}"):
                pass
        
        stats = monitor.get_stats()
        # Mit Sampling sollten weniger als 100 Queries getrackt sein
        assert stats['total_queries'] < 100
        # Aber mehr als 0 (statistisch)
        assert stats['total_queries'] > 0
    
    def test_sampling_rate_100_percent(self, monitor):
        """Test: 100% Sampling trackt alle Queries."""
        monitor.set_sampling_rate(1.0)  # 100%
        
        for i in range(50):
            with monitor.track_query(f"SELECT {i}"):
                pass
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 50
    
    def test_sampling_rate_0_percent(self, monitor):
        """Test: 0% Sampling trackt keine Queries."""
        monitor.set_sampling_rate(0.0)  # 0%
        
        for i in range(50):
            with monitor.track_query(f"SELECT {i}"):
                pass
        
        stats = monitor.get_stats()
        assert stats['total_queries'] == 0


# ============================================================================
# TEST CLASS: Metrics Collection
# ============================================================================

class TestMetricsCollection:
    """Tests für Metrics-Collection."""
    
    def test_get_stats_complete(self, monitor):
        """Test: Vollständige Stats abrufen."""
        with monitor.track_query("SELECT 1"):
            pass
        
        stats = monitor.get_stats()
        
        # Alle erwarteten Keys vorhanden
        assert 'total_queries' in stats
        assert 'avg_duration_ms' in stats
        assert 'max_duration_ms' in stats
        assert 'min_duration_ms' in stats
        assert 'slow_queries' in stats
        assert 'success_rate' in stats
        assert 'connection_pool' in stats
        assert 'query_type_distribution' in stats
    
    def test_metrics_aggregation(self, monitor):
        """Test: Metriken aggregieren."""
        durations = [10, 20, 30, 40, 50]  # ms
        
        for duration in durations:
            with monitor.track_query("SELECT 1"):
                time.sleep(duration / 1000)
        
        stats = monitor.get_stats()
        
        # Durchschnitt sollte ~30ms sein
        assert 20 <= stats['avg_duration_ms'] <= 40
        # Max sollte ~50ms sein
        assert stats['max_duration_ms'] >= 40
        # Min sollte ~10ms sein
        assert stats['min_duration_ms'] <= 20
    
    def test_query_type_detection(self, monitor, sample_queries):
        """Test: Query-Type automatisch erkennen."""
        with monitor.track_query(sample_queries['select_users']):
            pass
        
        with monitor.track_query(sample_queries['insert_user']):
            pass
        
        stats = monitor.get_stats()
        dist = stats['query_type_distribution']
        
        assert 'SELECT' in dist
        assert 'INSERT' in dist
        assert dist['SELECT'] == 1
        assert dist['INSERT'] == 1
    
    def test_export_metrics_json(self, monitor):
        """Test: Metriken als JSON exportieren."""
        with monitor.track_query("SELECT 1"):
            pass
        
        export = monitor.export_metrics(format='json')
        
        assert isinstance(export, dict)
        assert 'total_queries' in export
        assert 'timestamp' in export
    
    def test_metrics_retention_limit(self, monitor):
        """Test: Metriken-Limit (Ring-Buffer)."""
        # Fülle über Limit
        for i in range(20000):
            with monitor.track_query(f"SELECT {i}"):
                pass
        
        recent = monitor.get_recent_queries()
        
        # Sollte auf Max-Limit beschränkt sein
        assert len(recent) <= 10000  # Angenommenes Limit


# ============================================================================
# TEST CLASS: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration-Tests."""
    
    def test_full_workflow_with_db(self, mock_db):
        """Test: Kompletter Workflow mit Mock-DB."""
        monitor = DBPerformanceMonitor()
        
        # Simuliere DB-Operationen
        with monitor.track_query("SELECT * FROM users") as tracker:
            cursor = mock_db.execute("SELECT * FROM users")
            result = cursor.fetchall()
            tracker.record_rows(len(result))
        
        # Insert
        with monitor.track_query("INSERT INTO users (name) VALUES (?)") as tracker:
            mock_db.execute("INSERT INTO users (name) VALUES (?)", ["Alice"])
            mock_db.commit()
            tracker.record_success(rows_affected=1)
        
        # Stats prüfen
        stats = monitor.get_stats()
        
        assert stats['total_queries'] == 2
        assert stats['query_type_distribution']['SELECT'] == 1
        assert stats['query_type_distribution']['INSERT'] == 1
    
    def test_slow_query_with_alert(self, monitor):
        """Test: Slow Query triggert Alert."""
        monitor.set_slow_query_threshold(10)
        
        # Langsame Query
        with monitor.track_query("SELECT * FROM huge_table"):
            time.sleep(0.1)  # 100ms
        
        slow = monitor.get_slow_queries(limit=1)
        
        assert len(slow) == 1
        assert slow[0].duration_ms > 10
        
        # Alert-Check (Implementation-abhängig)
        stats = monitor.get_stats()
        assert stats['slow_queries'] == 1


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("sql,expected_type", [
    ("SELECT * FROM users", "SELECT"),
    ("INSERT INTO users VALUES (?)", "INSERT"),
    ("UPDATE users SET name=?", "UPDATE"),
    ("DELETE FROM users WHERE id=?", "DELETE"),
    ("CREATE TABLE test (id INT)", "CREATE"),
    ("DROP TABLE test", "DROP"),
])
def test_parametrized_query_type_detection(monitor, sql, expected_type):
    """Parametrized Test: Query-Type-Detection."""
    with monitor.track_query(sql):
        pass
    
    stats = monitor.get_stats()
    dist = stats['query_type_distribution']
    
    assert expected_type in dist
    assert dist[expected_type] == 1


@pytest.mark.parametrize("threshold,duration,is_slow", [
    (100, 50, False),   # 50ms < 100ms = nicht slow
    (100, 150, True),   # 150ms > 100ms = slow
    (10, 20, True),     # 20ms > 10ms = slow
    (1000, 500, False), # 500ms < 1000ms = nicht slow
])
def test_parametrized_slow_query_detection(monitor, threshold, duration, is_slow):
    """Parametrized Test: Slow Query Detection."""
    monitor.set_slow_query_threshold(threshold)
    
    with monitor.track_query("SELECT 1"):
        time.sleep(duration / 1000)
    
    slow = monitor.get_slow_queries(limit=10)
    
    if is_slow:
        assert len(slow) == 1
    else:
        assert len(slow) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
