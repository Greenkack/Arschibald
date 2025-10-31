"""Verification Script for Background Job Processing System"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("Background Job Processing System - Verification")
print("=" * 70)

# Test 1: Import all components
print("\n[1/8] Testing imports...")
try:
    from core.job_notifications import (
        JobNotificationManager,
        LogNotificationChannel,
    )
    from core.jobs import (
        ErrorType,
        Job,
        JobManager,
        JobPriority,
        JobQueue,
        JobResult,
        JobStatus,
        ProgressCallback,
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test 2: Create Job
print("\n[2/8] Testing Job creation...")
try:
    def test_func(x, y, progress_callback=None):
        if progress_callback:
            progress_callback(0.5, "Computing")
        return x + y

    job = Job(
        name="Test Job",
        function=test_func,
        args=(10, 20),
        priority=JobPriority.HIGH,
        max_retries=3
    )

    assert job.name == "Test Job"
    assert job.priority == JobPriority.HIGH
    assert job.max_retries == 3

    # Test serialization
    job_dict = job.to_dict()
    job2 = Job.from_dict(job_dict)
    assert job2.name == job.name

    print("✓ Job creation and serialization working")
except Exception as e:
    print(f"✗ Job creation failed: {e}")
    exit(1)

# Test 3: JobResult
print("\n[3/8] Testing JobResult...")
try:
    result = JobResult(
        job_id="test-123",
        status=JobStatus.COMPLETED,
        result={"value": 42},
        progress=1.0
    )

    result.update_progress(0.75, "Almost done", step=3)
    assert result.progress == 0.75
    assert result.progress_message == "Almost done"
    assert result.progress_details['step'] == 3

    # Test serialization
    result_dict = result.to_dict()
    result2 = JobResult.from_dict(result_dict)
    assert result2.job_id == result.job_id

    print("✓ JobResult working correctly")
except Exception as e:
    print(f"✗ JobResult failed: {e}")
    exit(1)

# Test 4: ProgressCallback
print("\n[4/8] Testing ProgressCallback...")
try:
    result = JobResult(job_id="test-456")

    updates = []

    def update_fn(r):
        updates.append(r.progress)

    callback = ProgressCallback(result, update_fn)
    callback(0.25, "Step 1")
    callback(0.50, "Step 2")
    callback(0.75, "Step 3")

    assert len(updates) == 3
    assert result.progress == 0.75

    print("✓ ProgressCallback working correctly")
except Exception as e:
    print(f"✗ ProgressCallback failed: {e}")
    exit(1)

# Test 5: JobQueue
print("\n[5/8] Testing JobQueue...")
try:
    queue = JobQueue()

    job_low = Job(name="Low", function=test_func, priority=JobPriority.LOW)
    job_high = Job(name="High", function=test_func, priority=JobPriority.HIGH)
    job_normal = Job(
        name="Normal",
        function=test_func,
        priority=JobPriority.NORMAL)

    queue.enqueue(job_low)
    queue.enqueue(job_high)
    queue.enqueue(job_normal)

    assert queue.size() == 3

    # Should dequeue in priority order
    first = queue.dequeue()
    assert first.name == "High"

    second = queue.dequeue()
    assert second.name == "Normal"

    third = queue.dequeue()
    assert third.name == "Low"

    assert queue.size() == 0

    print("✓ JobQueue priority ordering working")
except Exception as e:
    print(f"✗ JobQueue failed: {e}")
    exit(1)

# Test 6: JobManager
print("\n[6/8] Testing JobManager...")
try:
    manager = JobManager(max_workers=2)
    manager.start()

    def quick_task(x, y, progress_callback=None):
        if progress_callback:
            progress_callback(0.5, "Working")
        time.sleep(0.1)
        if progress_callback:
            progress_callback(1.0, "Done")
        return x + y

    job = Job(name="Quick Task", function=quick_task, args=(5, 10))
    job_id = manager.enqueue(job)

    # Wait for completion
    max_wait = 3
    start_time = time.time()
    completed = False

    while time.time() - start_time < max_wait:
        result = manager.poll(job_id)
        if result and result.status == JobStatus.COMPLETED:
            completed = True
            break
        time.sleep(0.1)

    assert completed, "Job did not complete in time"

    result = manager.poll(job_id)
    assert result.result == 15

    manager.stop(graceful=True, timeout=5)

    print("✓ JobManager execution working")
except Exception as e:
    print(f"✗ JobManager failed: {e}")
    exit(1)

# Test 7: Error Categorization
print("\n[7/8] Testing error categorization...")
try:
    manager = JobManager(max_workers=1)

    # Test transient errors
    assert manager._categorize_error(TimeoutError()) == ErrorType.TRANSIENT
    assert manager._categorize_error(ConnectionError()) == ErrorType.TRANSIENT

    # Test permanent errors
    assert manager._categorize_error(ValueError()) == ErrorType.PERMANENT
    assert manager._categorize_error(TypeError()) == ErrorType.PERMANENT

    print("✓ Error categorization working")
except Exception as e:
    print(f"✗ Error categorization failed: {e}")
    exit(1)

# Test 8: Notification System
print("\n[8/8] Testing notification system...")
try:
    notification_manager = JobNotificationManager()

    # Add log channel
    log_channel = LogNotificationChannel()
    notification_manager.add_channel(log_channel)

    # Test notification
    job = Job(name="Failed Job", function=test_func)
    result = JobResult(
        job_id=job.id,
        status=JobStatus.FAILED,
        error="Test error",
        error_type=ErrorType.PERMANENT
    )

    notification_manager.notify_failure(job, result)

    print("✓ Notification system working")
except Exception as e:
    print(f"✗ Notification system failed: {e}")
    exit(1)

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n✓ All tests passed!")
print("\nBackground Job Processing System is ready to use.")
print("\nKey Features Verified:")
print("  • Job creation and serialization")
print("  • JobResult with progress tracking")
print("  • Progress callbacks")
print("  • Priority queue ordering")
print("  • Job execution with JobManager")
print("  • Error categorization (transient vs permanent)")
print("  • Notification system")
print("\nNext Steps:")
print("  1. Run: python core/example_job_usage.py")
print("  2. Run: pytest core/test_jobs.py")
print("  3. Initialize database: from core import init_job_tables; init_job_tables()")
print("  4. See core/JOB_SYSTEM_README.md for full documentation")
