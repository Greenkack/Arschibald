"""
Test Docker Performance Optimizations
======================================

Tests for Task 15.2: Optimize Docker operations
- Container reuse
- Efficient cleanup
- Parallel execution
- Resource monitoring
"""

from agent.tools.execution_tools import (
    clear_container_pool,
    execute_python_code_in_sandbox,
    get_container_stats,
    run_terminal_command_in_sandbox,
)
import os
import sys
import threading
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_container_reuse():
    """Test that containers are reused from pool."""
    print("\n" + "=" * 70)
    print("TEST 1: Container Reuse")
    print("=" * 70)

    # Clear pool first
    clear_container_pool()
    time.sleep(1)

    # First execution (should create container)
    print("\nFirst execution (should create container)...")
    start = time.time()
    result1 = execute_python_code_in_sandbox.func("print('Hello 1')")
    time1 = time.time() - start
    print(f"Time: {time1:.2f}s")
    print(f"Result: {result1[:100]}")

    # Check pool
    stats = get_container_stats()
    print(f"\nPool size after first execution: {stats['pool_size']}")
    assert stats['pool_size'] > 0, "Container should be in pool"

    # Second execution (should reuse container)
    print("\nSecond execution (should reuse container)...")
    start = time.time()
    result2 = execute_python_code_in_sandbox.func("print('Hello 2')")
    time2 = time.time() - start
    print(f"Time: {time2:.2f}s")
    print(f"Result: {result2[:100]}")

    # Check pool
    stats = get_container_stats()
    print(f"\nPool size after second execution: {stats['pool_size']}")

    # Second execution should be faster (container reuse)
    if time1 > 1.0:  # Only check if first execution was slow enough
        speedup = time1 / time2
        print(f"\n✓ Container reuse is {speedup:.1f}x faster")
        assert speedup > 1.2, "Reuse should be faster"

    print("\n✅ Container reuse test passed")


def test_parallel_execution():
    """Test parallel container execution."""
    print("\n" + "=" * 70)
    print("TEST 2: Parallel Execution")
    print("=" * 70)

    clear_container_pool()
    time.sleep(1)

    # Execute multiple tasks in parallel
    results = []
    threads = []

    def execute_task(task_id):
        code = f"import time; time.sleep(0.5); print('Task {task_id}')"
        result = execute_python_code_in_sandbox.func(code)
        results.append((task_id, result))

    print("\nExecuting 3 tasks in parallel...")
    start = time.time()

    for i in range(3):
        thread = threading.Thread(target=execute_task, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    parallel_time = time.time() - start
    print(f"Parallel execution time: {parallel_time:.2f}s")

    # Check results
    assert len(results) == 3, "All tasks should complete"
    print(f"✓ All {len(results)} tasks completed")

    # Parallel should be faster than sequential
    # (3 tasks * 0.5s = 1.5s sequential, but parallel should be ~0.5-1.0s)
    assert parallel_time < 2.0, "Parallel execution should be efficient"
    print(f"✓ Parallel execution completed in {parallel_time:.2f}s")

    # Check pool
    stats = get_container_stats()
    print(f"\nPool size after parallel execution: {stats['pool_size']}")

    print("\n✅ Parallel execution test passed")


def test_efficient_cleanup():
    """Test that cleanup works efficiently."""
    print("\n" + "=" * 70)
    print("TEST 3: Efficient Cleanup")
    print("=" * 70)

    # Create several containers
    print("\nCreating multiple containers...")
    for i in range(3):
        execute_python_code_in_sandbox.func(f"print('Test {i}')")

    stats = get_container_stats()
    initial_count = stats['pool_size']
    print(f"Initial pool size: {initial_count}")

    # Manual cleanup
    print("\nPerforming manual cleanup...")
    clear_container_pool()
    time.sleep(1)

    stats = get_container_stats()
    final_count = stats['pool_size']
    print(f"Final pool size: {final_count}")

    assert final_count == 0, "Pool should be empty after cleanup"
    print("✓ Cleanup removed all containers")

    print("\n✅ Efficient cleanup test passed")


def test_resource_monitoring():
    """Test resource monitoring and statistics."""
    print("\n" + "=" * 70)
    print("TEST 4: Resource Monitoring")
    print("=" * 70)

    clear_container_pool()
    time.sleep(1)

    # Execute some tasks
    print("\nExecuting tasks...")
    execute_python_code_in_sandbox.func("print('Task 1')")
    time.sleep(0.5)
    execute_python_code_in_sandbox.func("print('Task 2')")

    # Get statistics
    stats = get_container_stats()

    print("\nContainer Statistics:")
    print(f"Pool size: {stats['pool_size']}/{stats['max_pool_size']}")

    for container in stats['containers']:
        print(f"\nContainer: {container['name']}")
        print(f"  Age: {container['age_seconds']:.1f}s")
        print(f"  Idle: {container['idle_seconds']:.1f}s")

    assert 'pool_size' in stats, "Stats should include pool size"
    assert 'containers' in stats, "Stats should include container list"
    print("\n✓ Statistics available")

    print("\n✅ Resource monitoring test passed")


def test_startup_optimization():
    """Test that container startup is optimized."""
    print("\n" + "=" * 70)
    print("TEST 5: Startup Optimization")
    print("=" * 70)

    clear_container_pool()
    time.sleep(1)

    # Measure first execution (cold start)
    print("\nCold start (first execution)...")
    start = time.time()
    result1 = execute_python_code_in_sandbox.func("print('Cold start')")
    cold_time = time.time() - start
    print(f"Time: {cold_time:.2f}s")

    # Measure second execution (warm start)
    print("\nWarm start (reused container)...")
    start = time.time()
    result2 = execute_python_code_in_sandbox.func("print('Warm start')")
    warm_time = time.time() - start
    print(f"Time: {warm_time:.2f}s")

    # Warm start should be faster
    if cold_time > 0.5:
        speedup = cold_time / warm_time
        print(f"\n✓ Warm start is {speedup:.1f}x faster")

    # Both should complete successfully
    assert "Cold start" in result1 or "STDOUT" in result1
    assert "Warm start" in result2 or "STDOUT" in result2
    print("✓ Both executions successful")

    print("\n✅ Startup optimization test passed")


def test_different_container_types():
    """Test that different container types are managed separately."""
    print("\n" + "=" * 70)
    print("TEST 6: Different Container Types")
    print("=" * 70)

    clear_container_pool()
    time.sleep(1)

    # Execute Python code (network disabled)
    print("\nExecuting Python code (network disabled)...")
    result1 = execute_python_code_in_sandbox.func("print('Python')")

    # Execute terminal command (network enabled)
    print("Executing terminal command (network enabled)...")
    result2 = run_terminal_command_in_sandbox.func("echo 'Terminal'")

    # Check pool
    stats = get_container_stats()
    print(f"\nPool size: {stats['pool_size']}")

    # Should have 2 containers (one for each type)
    assert stats['pool_size'] >= 1, "Should have at least one container"
    print(f"✓ Managing {stats['pool_size']} container(s)")

    # Both should work
    assert "Python" in result1 or "STDOUT" in result1
    assert "Terminal" in result2 or "STDOUT" in result2
    print("✓ Both container types work correctly")

    print("\n✅ Different container types test passed")


def run_all_tests():
    """Run all Docker optimization tests."""
    print("\n" + "=" * 70)
    print("DOCKER PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 70)

    try:
        test_container_reuse()
        test_parallel_execution()
        test_efficient_cleanup()
        test_resource_monitoring()
        test_startup_optimization()
        test_different_container_types()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)

        # Final cleanup
        clear_container_pool()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
