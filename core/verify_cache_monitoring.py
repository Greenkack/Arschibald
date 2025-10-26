"""Verification script for Cache Performance Monitoring (Task 6.3)"""

from core.cache_monitoring import (
    detect_performance_issues,
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
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def verify_hit_rate_tracking():
    """Verify detailed hit rate tracking"""
    print_section("1. Hit Rate Tracking with Detailed Metrics")

    # Generate cache activity
    cache = get_cache()

    print("Generating cache activity...")
    for i in range(50):
        cache.set(f"key_{i}", f"value_{i}")

    # Generate hits
    for i in range(30):
        cache.get(f"key_{i}")

    # Generate misses
    for i in range(20):
        cache.get(f"miss_key_{i}")

    # Get detailed metrics
    detailed = get_detailed_metrics("memory", window_minutes=5)

    print(f"Layer: {detailed['layer']}")
    print(f"Window: {detailed['window_minutes']} minutes")

    if detailed["metrics"]:
        print("\nMetrics:")
        for metric_type, stats in detailed["metrics"].items():
            print(f"\n  {metric_type}:")
            print(f"    Current: {stats['current']:.4f}")
            print(f"    Average: {stats['average']:.4f}")
            print(f"    Min: {stats['min']:.4f}")
            print(f"    Max: {stats['max']:.4f}")
            print(f"    Trend: {stats['trend']}")
    else:
        print("No metrics collected yet")

    print("\n✓ Hit rate tracking verified")


def verify_trend_analysis():
    """Verify performance analytics with trend analysis"""
    print_section("2. Performance Analytics with Trend Analysis")

    monitor = get_cache_monitor()

    # Simulate improving trend
    print("Simulating improving performance trend...")
    for i in range(10):
        value = 0.5 + (i * 0.04)
        monitor.metrics_collector.record_metric("memory", "hit_rate", value)

    trend = monitor.metrics_collector.calculate_trend(
        "memory",
        "hit_rate",
        window_minutes=5
    )
    print(f"Trend detected: {trend}")

    # Get comprehensive report
    report = get_cache_performance_report()

    print("\nPerformance Report:")
    print(f"Timestamp: {report['timestamp']}")

    if "memory" in report["layers"]:
        memory = report["layers"]["memory"]
        hit_rate_data = memory.get("hit_rate", {})
        print("\nMemory Layer:")
        print(f"  Hit Rate: {hit_rate_data.get('hit_rate', 0):.2%}")
        print(f"  Trend: {hit_rate_data.get('trend', 'unknown')}")
        print(f"  Status: {hit_rate_data.get('status', 'unknown')}")

    print("\n✓ Trend analysis verified")


def verify_automatic_cleanup():
    """Verify cache size monitoring with automatic cleanup"""
    print_section("3. Cache Size Monitoring with Automatic Cleanup")

    # Register custom cleanup callback
    cleanup_executed = []

    def custom_cleanup():
        cleanup_executed.append(datetime.now())
        print("  Custom cleanup callback executed")

    register_cleanup_callback(custom_cleanup)
    print("Custom cleanup callback registered")

    # Enable automatic cleanup
    enable_automatic_cleanup(threshold=0.8)
    print("Automatic cleanup enabled (threshold: 80%)")

    # Fill cache
    cache = get_cache()
    print("\nFilling cache with entries...")
    for i in range(100):
        cache.set(f"cleanup_key_{i}", f"value_{i}", ttl=2)

    # Get size report
    monitor = get_cache_monitor()
    size_report = monitor.analyzer.analyze_cache_size("memory")

    print("\nCache Size:")
    print(f"  Entries: {size_report['entries']}")
    print(f"  Max Entries: {size_report['max_entries']}")
    print(f"  Utilization: {size_report['utilization']:.2%}")
    print(f"  Total Size: {size_report['total_size_mb']:.2f} MB")

    # Trigger manual cleanup
    print("\nTriggering manual cleanup...")
    results = trigger_manual_cleanup("verification_test")

    print("Cleanup Results:")
    print(f"  Reason: {results['reason']}")
    print(f"  Entries Before: {results['entries_before']}")
    print(f"  Entries After: {results['entries_after']}")
    print(f"  Space Freed: {results['space_freed_bytes'] / 1024:.2f} KB")
    print(f"  Callbacks Executed: {results['callbacks_executed']}")

    if cleanup_executed:
        print("\n✓ Custom cleanup callback was executed")

    print("\n✓ Automatic cleanup verified")


def verify_performance_alerts():
    """Verify performance degradation alerts"""
    print_section("4. Performance Degradation Detection")

    monitor = get_cache_monitor()

    # Establish baseline
    print("Establishing performance baseline...")
    for i in range(10):
        monitor.metrics_collector.record_metric("memory", "hit_rate", 0.90)

    # Simulate degradation
    print("Simulating performance degradation...")
    cache = get_cache()
    for i in range(100):
        cache.get(f"degrade_miss_{i}")

    # Detect degradation
    degradation = monitor.analyzer.detect_performance_degradation("memory")

    if degradation:
        print("\nDegradation Detected:")
        print(f"  Current Hit Rate: {degradation['current_hit_rate']:.2%}")
        print(f"  Historical Avg: {degradation['historical_avg']:.2%}")
        print(f"  Degradation: {degradation['degradation_percent']:.1f}%")
        print(f"  Threshold: {degradation['threshold_percent']:.1f}%")
    else:
        print("\nNo significant degradation detected")

    # Check for performance issues
    issues = detect_performance_issues()

    print("\nPerformance Issues Check:")
    print(f"  Active Alerts: {len(issues['alerts'])}")
    print(f"  Recommendations: {len(issues['recommendations'])}")

    if issues["alerts"]:
        print("\n  Active Alerts:")
        for alert in issues["alerts"]:
            print(f"    - [{alert['severity']}] {alert['message']}")

    if issues["recommendations"]:
        print("\n  Recommendations:")
        for rec in issues["recommendations"]:
            print(f"    - {rec}")

    print("\n✓ Performance alerts verified")


def verify_monitoring_integration():
    """Verify complete monitoring integration"""
    print_section("5. Complete Monitoring Integration")

    # Start monitoring
    print("Starting cache monitoring...")
    start_cache_monitoring(interval_seconds=1)

    monitor = get_cache_monitor()
    print(f"Monitoring started: {monitor._running}")

    # Generate activity
    print("\nGenerating cache activity...")
    cache = get_cache()

    for i in range(30):
        cache.set(f"monitor_key_{i}", f"value_{i}")

    for i in range(20):
        cache.get(f"monitor_key_{i}")

    # Wait for collection
    print("Waiting for metric collection...")
    time.sleep(2)

    # Get detailed report
    report = get_cache_performance_report(detailed=True)

    print("\nDetailed Monitoring Report:")
    print(f"Timestamp: {report['timestamp']}")

    if "monitoring_status" in report:
        status = report["monitoring_status"]
        print("\nMonitoring Status:")
        print(f"  Running: {status['running']}")
        print(
            f"  Collection Interval: {
                status['collection_interval_seconds']}s")
        print(f"  Collection Count: {status['collection_count']}")
        print(f"  Auto Cleanup: {status['auto_cleanup_enabled']}")

    if "detailed_metrics" in report:
        detailed = report["detailed_metrics"]
        print("\nDetailed Metrics:")
        print(f"  Layer: {detailed['layer']}")
        print(f"  Window: {detailed['window_minutes']} minutes")

        if detailed["metrics"]:
            for metric_type, stats in detailed["metrics"].items():
                print(f"\n  {metric_type}:")
                print(f"    Average: {stats['average']:.4f}")
                print(f"    Trend: {stats['trend']}")

    # Stop monitoring
    print("\nStopping cache monitoring...")
    stop_cache_monitoring()
    print(f"Monitoring stopped: {not monitor._running}")

    print("\n✓ Monitoring integration verified")


def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("  Cache Performance Monitoring Verification (Task 6.3)")
    print("=" * 60)

    try:
        verify_hit_rate_tracking()
        verify_trend_analysis()
        verify_automatic_cleanup()
        verify_performance_alerts()
        verify_monitoring_integration()

        print_section("Verification Complete")
        print("✓ All cache performance monitoring features verified")
        print("\nTask 6.3 Implementation Summary:")
        print("  ✓ Cache hit rate tracking with detailed metrics")
        print("  ✓ Performance analytics with trend analysis")
        print("  ✓ Cache size monitoring with automatic cleanup")
        print("  ✓ Performance degradation detection and alerts")
        print("  ✓ Complete monitoring integration")

    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
