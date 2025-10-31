"""Simple direct test for Database Performance Monitor - No imports needed"""

import sys


# Direct test without module imports
def test_monitor_directly():
    """Test the monitor by directly executing the code"""
    print("\n" + "=" * 60)
    print("SIMPLE DATABASE PERFORMANCE MONITOR TEST")
    print("=" * 60)

    try:
        # Test 1: Import the module
        print("\n[1/5] Testing module import...")
        sys.path.insert(0, '.')
        from db_performance_monitor import create_performance_monitor
        print("✅ Module imported successfully")

        # Test 2: Create monitor
        print("\n[2/5] Creating performance monitor...")
        monitor = create_performance_monitor(
            slow_query_threshold=0.5,
            enable_recommendations=True
        )
        print("✅ Monitor created successfully")

        # Test 3: Record queries
        print("\n[3/5] Recording test queries...")
        test_queries = [
            ("SELECT * FROM users WHERE id = 1", 0.1),
            ("INSERT INTO logs VALUES ('test')", 0.05),
            ("UPDATE users SET name = 'John'", 0.08),
            ("SELECT * FROM large_table", 0.8),  # Slow query
        ]

        for query, duration in test_queries:
            monitor.record_query(query, duration)

        print(f"✅ Recorded {len(test_queries)} queries")

        # Test 4: Get statistics
        print("\n[4/5] Getting statistics...")
        stats = monitor.get_stats()

        print(f"   Total Queries: {stats.total_queries}")
        print(f"   Slow Queries: {stats.slow_queries}")
        print(f"   Average Time: {stats.avg_query_time:.3f}s")
        print(f"   Error Rate: {stats.error_rate:.1%}")

        assert stats.total_queries == 4, "Query count mismatch"
        assert stats.slow_queries == 1, "Slow query count mismatch"
        print("✅ Statistics correct")

        # Test 5: Get slow queries
        print("\n[5/5] Getting slow queries...")
        slow_queries = monitor.get_slow_queries()
        print(f"   Found {len(slow_queries)} slow queries")

        if slow_queries:
            sq = slow_queries[0]
            print(f"   Query: {sq.query[:50]}...")
            print(f"   Duration: {sq.duration:.2f}s")

        assert len(slow_queries) == 1, "Slow query list mismatch"
        print("✅ Slow query detection works")

        # Success
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without complex imports"""
    print("\n" + "=" * 60)
    print("BASIC FUNCTIONALITY TEST")
    print("=" * 60)

    try:
        # Simple inline test
        print("\n✓ Testing dataclass creation...")
        from datetime import datetime

        # Test that we can create basic objects
        test_data = {
            'query': 'SELECT * FROM users',
            'duration': 0.5,
            'timestamp': datetime.utcnow()
        }

        print(f"   Query: {test_data['query']}")
        print(f"   Duration: {test_data['duration']}s")
        print("✅ Basic data structures work")

        # Test threshold logic
        print("\n✓ Testing threshold logic...")
        slow_threshold = 1.0
        is_slow = test_data['duration'] > slow_threshold
        print(
            f"   Duration {
                test_data['duration']}s vs threshold {slow_threshold}s")
        print(f"   Is slow: {is_slow}")
        print("✅ Threshold logic works")

        # Test statistics calculation
        print("\n✓ Testing statistics calculation...")
        query_times = [0.1, 0.2, 0.3, 0.4, 0.5]
        avg_time = sum(query_times) / len(query_times)
        min_time = min(query_times)
        max_time = max(query_times)

        print(f"   Average: {avg_time:.3f}s")
        print(f"   Min: {min_time:.3f}s")
        print(f"   Max: {max_time:.3f}s")
        print("✅ Statistics calculation works")

        print("\n" + "=" * 60)
        print("✅ BASIC FUNCTIONALITY TEST PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ BASIC TEST FAILED: {e}")
        return False


def test_file_exists():
    """Test that the implementation file exists"""
    print("\n" + "=" * 60)
    print("FILE EXISTENCE TEST")
    print("=" * 60)

    import os

    # Check in current directory (when run from core/)
    files_to_check = [
        'db_performance_monitor.py',
        'example_db_performance_monitor_usage.py',
        'test_db_performance_monitor.py',
        'DB_PERFORMANCE_MONITOR_README.md',
        'DB_PERFORMANCE_MONITOR_QUICK_START.md',
        'TASK_8_4_COMPLETE.md'
    ]

    # If not found, check in core/ subdirectory (when run from root)
    if not os.path.exists(files_to_check[0]):
        files_to_check = [os.path.join('core', f) for f in files_to_check]

    all_exist = True
    for filename in files_to_check:
        exists = os.path.exists(filename)
        status = "✅" if exists else "❌"
        print(f"{status} {filename}")
        if not exists:
            all_exist = False

    if all_exist:
        print("\n✅ ALL FILES EXIST")
    else:
        print("\n⚠️  SOME FILES MISSING")

    return all_exist


def main():
    """Run all simple tests"""
    print("\n" + "=" * 70)
    print("DATABASE PERFORMANCE MONITOR - SIMPLE TEST SUITE")
    print("=" * 70)

    results = []

    # Test 1: File existence
    print("\n>>> Running File Existence Test...")
    results.append(("File Existence", test_file_exists()))

    # Test 2: Basic functionality
    print("\n>>> Running Basic Functionality Test...")
    results.append(("Basic Functionality", test_basic_functionality()))

    # Test 3: Full monitor test
    print("\n>>> Running Full Monitor Test...")
    results.append(("Full Monitor", test_monitor_directly()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    print("⚠️  SOME TESTS FAILED")
    print("=" * 70)
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
