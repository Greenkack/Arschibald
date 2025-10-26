"""Example usage of Cache Performance Monitoring System"""

from core.cache_monitoring import (
    detect_performance_issues,
    disable_automatic_cleanup,
    enable_automatic_cleanup,
    get_cache_monitor,
    get_cache_performance_report,
    get_detailed_metrics,
    register_cleanup_callback,
    start_cache_monitoring,
    stop_cache_monitoring,
    trigger_manual_cleanup,
)
from core.cache import get_cache
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def example_basic_monitoring():
    """Example: Basic cache monitoring"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Cache Monitoring")
    print("=" * 60)

    # Start monitoring
    start_cache_monitoring(interval_seconds=5)
    print("✓ Monitoring started with 5-second intervals")

    # Generate some cache activity
    cache = get_cache()
    for i in range(20):
        cache.set(f"key_{i}", f"value_{i}")

    # Wait for collection
    time.sleep(6)

    # Get report
    report = get_cache_performance_report()

    print("\nPerformance Report:")
    print(f"Timestamp: {report['timestamp']}")

    if "memory" in report["layers"]:
        memory = report["layers"]["memory"]
        hit_rate_data = memory.get("hit_rate", {})
        size_data = memory.get("size", {})

        print("\nMemory Layer:")
        print(f"  Hit Rate: {hit_rate_data.get('hit_rate', 0):.2%}")
        print(f"  Status: {hit_rate_data.get('status', 'unknown')}")
        print(f"  Utilization: {size_data.get('utilization', 0):.2%}")
        print(f"  Entries: {size_data.get('entries', 0)}")

    # Stop monitoring
    stop_cache_monitoring()
    print("\n✓ Monitoring stopped")


def example_detailed_metrics():
    """Example: Get detailed metrics with historical data"""
    print("\n" + "=" * 60)
    print("Example 2: Detailed Metrics")
    print("=" * 60)

    monitor = get_cache_monitor()

    # Generate metrics over time
    print("Generating metrics...")
    for i in range(10):
        value = 0.7 + (i * 0.02)
        monitor.metrics_collector.record_metric("memory", "hit_rate", value)
        monitor.metrics_collector.record_metric(
            "memory", "utilization", 0.5 + (i * 0.03))

    # Get detailed metrics
    detailed = get_detailed_metrics("memory", window_minutes=5)

    print("\nDetailed Metrics (last 5 minutes):")
    print(f"Layer: {detailed['layer']}")

    for metric_type, stats in detailed["metrics"].items():
        print(f"\n{metric_type}:")
        print(f"  Current: {stats['current']:.4f}")
        print(f"  Average: {stats['average']:.4f}")
        print(f"  Min: {stats['min']:.4f}")
        print(f"  Max: {stats['max']:.4f}")
        print(f"  Count: {stats['count']}")
        print(f"  Trend: {stats['trend']}")


def example_trend_analysis():
    """Example: Analyze performance trends"""
    print("\n" + "=" * 60)
    print("Example 3: Trend Analysis")
    print("=" * 60)

    monitor = get_cache_monitor()

    # Simulate improving trend
    print("Simulating improving performance...")
    for i in range(10):
        value = 0.5 + (i * 0.04)
        monitor.metrics_collector.record_metric("memory", "hit_rate", value)

    trend = monitor.metrics_collector.calculate_trend(
        "memory",
        "hit_rate",
        window_minutes=5
    )
    print(f"Trend: {trend}")

    # Simulate degrading trend
    print("\nSimulating degrading performance...")
    for i in range(10):
        value = 0.9 - (i * 0.04)
        monitor.metrics_collector.record_metric(
            "memory", "response_time", value)

    trend = monitor.metrics_collector.calculate_trend(
        "memory",
        "response_time",
        window_minutes=5
    )
    print(f"Trend: {trend}")

    # Get comprehensive report
    report = get_cache_performance_report()

    if "memory" in report["layers"]:
        memory = report["layers"]["memory"]
        hit_rate_data = memory.get("hit_rate", {})
        print("\nCurrent Status:")
        print(f"  Hit Rate: {hit_rate_data.get('hit_rate', 0):.2%}")
        print(f"  Trend: {hit_rate_data.get('trend', 'unknown')}")
        print(f"  Status: {hit_rate_data.get('status', 'unknown')}")


def example_automatic_cleanup():
    """Example: Automatic cache cleanup"""
    print("\n" + "=" * 60)
    print("Example 4: Automatic Cleanup")
    print("=" * 60)

    # Register custom cleanup callback
    cleanup_count = [0]

    def custom_cleanup():
        cleanup_count[0] += 1
        print(f"  Custom cleanup executed (count: {cleanup_count[0]})")

    register_cleanup_callback(custom_cleanup)
    print("✓ Custom cleanup callback registered")

    # Enable automatic cleanup
    enable_automatic_cleanup(threshold=0.8)
    print("✓ Automatic cleanup enabled (threshold: 80%)")

    # Fill cache
    cache = get_cache()
    print("\nFilling cache...")
    for i in range(50):
        cache.set(f"cleanup_key_{i}", f"value_{i}", ttl=2)

    # Get size before cleanup
    monitor = get_cache_monitor()
    size_before = monitor.analyzer.analyze_cache_size("memory")
    print("\nBefore cleanup:")
    print(f"  Entries: {size_before['entries']}")
    print(f"  Utilization: {size_before['utilization']:.2%}")

    # Trigger manual cleanup
    print("\nTriggering manual cleanup...")
    results = trigger_manual_cleanup("example")

    print("\nCleanup Results:")
    print(f"  Entries Before: {results['entries_before']}")
    print(f"  Entries After: {results['entries_after']}")
    print(f"  Space Freed: {results['space_freed_bytes'] / 1024:.2f} KB")
    print(f"  Callbacks Executed: {results['callbacks_executed']}")

    # Disable cleanup
    disable_automatic_cleanup()
    print("\n✓ Automatic cleanup disabled")


def example_performance_alerts():
    """Example: Performance degradation alerts"""
    print("\n" + "=" * 60)
    print("Example 5: Performance Alerts")
    print("=" * 60)

    monitor = get_cache_monitor()

    # Establish baseline
    print("Establishing performance baseline...")
    for i in range(10):
        monitor.metrics_collector.record_metric("memory", "hit_rate", 0.90)

    # Simulate degradation
    print("Simulating performance degradation...")
    cache = get_cache()
    for i in range(100):
        cache.get(f"miss_key_{i}")

    # Detect degradation
    degradation = monitor.analyzer.detect_performance_degradation("memory")

    if degradation:
        print("\n⚠ Degradation Detected:")
        print(f"  Current Hit Rate: {degradation['current_hit_rate']:.2%}")
        print(f"  Historical Avg: {degradation['historical_avg']:.2%}")
        print(f"  Degradation: {degradation['degradation_percent']:.1f}%")
        print(f"  Threshold: {degradation['threshold_percent']:.1f}%")
    else:
        print("\n✓ No significant degradation detected")

    # Check for all performance issues
    issues = detect_performance_issues()

    print("\nPerformance Issues Summary:")
    print(f"  Active Alerts: {len(issues['alerts'])}")
    print(f"  Recommendations: {len(issues['recommendations'])}")

    if issues["alerts"]:
        print("\n  Active Alerts:")
        for alert in issues["alerts"]:
            print(f"    [{alert['severity']}] {alert['message']}")

    if issues["recommendations"]:
        print("\n  Recommendations:")
        for rec in issues["recommendations"]:
            print(f"    - {rec}")


def example_monitoring_dashboard():
    """Example: Create a monitoring dashboard"""
    print("\n" + "=" * 60)
    print("Example 6: Monitoring Dashboard")
    print("=" * 60)

    # Start monitoring
    start_cache_monitoring(interval_seconds=2)

    # Generate activity
    cache = get_cache()
    print("Generating cache activity...")

    for i in range(30):
        cache.set(f"dash_key_{i}", f"value_{i}")

    for i in range(20):
        cache.get(f"dash_key_{i}")  # Hits

    for i in range(10):
        cache.get(f"miss_key_{i}")  # Misses

    # Wait for collection
    time.sleep(3)

    # Get detailed report
    report = get_cache_performance_report(detailed=True)

    print("\n" + "=" * 60)
    print("Cache Performance Dashboard")
    print("=" * 60)

    # Memory layer stats
    if "memory" in report["layers"]:
        memory = report["layers"]["memory"]
        hit_rate = memory["hit_rate"]
        size = memory["size"]
        evictions = memory["evictions"]

        print(
            f"\n📊 Hit Rate: {
                hit_rate['hit_rate']:.2%} ({
                hit_rate['status']})")
        print(f"   Trend: {hit_rate['trend']}")
        print(f"   Hits: {hit_rate['hits']}, Misses: {hit_rate['misses']}")

        print(f"\n💾 Cache Size: {size['entries']}/{size['max_entries']}")
        print(f"   Utilization: {size['utilization']:.2%}")
        print(f"   Total Size: {size['total_size_mb']:.2f} MB")

        print(f"\n🔄 Evictions: {evictions['evictions']}")
        print(f"   Expirations: {evictions['expirations']}")

    # Monitoring status
    if "monitoring_status" in report:
        status = report["monitoring_status"]
        print("\n⚙️  Monitoring Status:")
        print(f"   Running: {status['running']}")
        print(f"   Interval: {status['collection_interval_seconds']}s")
        print(f"   Collections: {status['collection_count']}")
        print(f"   Auto Cleanup: {status['auto_cleanup_enabled']}")

    # Alerts
    if report["alerts"]:
        print(f"\n⚠️  Active Alerts: {len(report['alerts'])}")
        for alert in report["alerts"]:
            print(f"   [{alert['severity']}] {alert['message']}")

    # Recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")

    # Detailed metrics
    if "detailed_metrics" in report:
        detailed = report["detailed_metrics"]
        print(
            f"\n📈 Detailed Metrics (last {
                detailed['window_minutes']} minutes):")

        for metric_type, stats in detailed["metrics"].items():
            print(f"\n   {metric_type}:")
            print(f"     Current: {stats['current']:.4f}")
            print(f"     Average: {stats['average']:.4f}")
            print(f"     Range: {stats['min']:.4f} - {stats['max']:.4f}")
            print(f"     Trend: {stats['trend']}")

    print("\n" + "=" * 60)

    # Stop monitoring
    stop_cache_monitoring()


def example_custom_cleanup_logic():
    """Example: Custom cleanup logic"""
    print("\n" + "=" * 60)
    print("Example 7: Custom Cleanup Logic")
    print("=" * 60)

    def cleanup_old_sessions():
        """Remove session data older than 5 minutes"""
        cache = get_cache()
        cutoff = datetime.now() - timedelta(minutes=5)
        removed = 0

        for key in cache.memory_cache.get_all_keys():
            if key.startswith("user_session:"):
                entry = cache.memory_cache.get_entry(key)
                if entry and entry.created_at < cutoff:
                    cache.delete(key)
                    removed += 1

        print(f"  Removed {removed} old session entries")

    def cleanup_expired_forms():
        """Remove expired form data"""
        cache = get_cache()
        removed = 0

        for key in cache.memory_cache.get_all_keys():
            if key.startswith("form_data:"):
                entry = cache.memory_cache.get_entry(key)
                if entry and entry.is_expired():
                    cache.delete(key)
                    removed += 1

        print(f"  Removed {removed} expired form entries")

    # Register custom cleanup callbacks
    register_cleanup_callback(cleanup_old_sessions)
    register_cleanup_callback(cleanup_expired_forms)
    print("✓ Custom cleanup callbacks registered")

    # Add test data
    cache = get_cache()
    print("\nAdding test data...")

    for i in range(10):
        cache.set(f"user_session:user_{i}", {"data": i}, ttl=1)
        cache.set(f"form_data:form_{i}", {"data": i}, ttl=1)

    print("Added 20 test entries")

    # Wait for expiration
    time.sleep(2)

    # Trigger cleanup
    print("\nTriggering cleanup...")
    results = trigger_manual_cleanup("custom_cleanup_example")

    print("\nCleanup completed:")
    print(f"  Callbacks executed: {results['callbacks_executed']}")
    print(f"  Space freed: {results['space_freed_bytes'] / 1024:.2f} KB")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Cache Performance Monitoring Examples")
    print("=" * 60)

    try:
        example_basic_monitoring()
        example_detailed_metrics()
        example_trend_analysis()
        example_automatic_cleanup()
        example_performance_alerts()
        example_monitoring_dashboard()
        example_custom_cleanup_logic()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
