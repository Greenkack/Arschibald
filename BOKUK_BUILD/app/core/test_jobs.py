"""Tests for Background Job Processing System"""

import time
from datetime import datetime, timedelta

import pytest

from core.jobs import (
    ErrorType,
    Job,
    JobManager,
    JobPriority,
    JobQueue,
    JobResult,
    JobStatus,
    ProgressCallback,
    enqueue,
    poll,
)


# Test fixtures
def simple_task(x: int, y: int, progress_callback=None) -> int:
    """Simple test task"""
    if progress_callback:
        progress_callback(0.5, "Computing")
    time.sleep(0.1)
    if progress_callback:
        progress_callback(1.0, "Done")
    return x + y


def failing_task(progress_callback=None):
    """Task that always fails"""
    raise ValueError("This task always fails")


def transient_error_task(progress_callback=None):
    """Task that fails with transient error"""
    raise ConnectionError("Temporary connection issue")


def slow_task(duration: float, progress_callback=None) -> str:
    """Slow task for testing cancellation"""
    steps = 10
    for i in range(steps):
        time.sleep(duration / steps)
        if progress_callback:
            progress_callback((i + 1) / steps, f"Step {i + 1}/{steps}")
    return "completed"


# Test Job class
def test_job_creation():
    """Test Job creation and serialization"""
    job = Job(
        name="Test Job",
        function=simple_task,
        args=(1, 2),
        priority=JobPriority.HIGH,
        max_retries=5
    )

    assert job.name == "Test Job"
    assert job.args == (1, 2)
    assert job.priority == JobPriority.HIGH
    assert job.max_retries == 5

    # Test serialization
    job_dict = job.to_dict()
    assert job_dict['name'] == "Test Job"
    assert job_dict['args'] == [1, 2]

    # Test deserialization
    job2 = Job.from_dict(job_dict)
    assert job2.name == job.name
    assert job2.args == job.args


def test_job_result_creation():
    """Test JobResult creation and serialization"""
    result = JobResult(
        job_id="test-123",
        status=JobStatus.COMPLETED,
        result={"value": 42},
        progress=1.0
    )

    assert result.job_id == "test-123"
    assert result.status == JobStatus.COMPLETED
    assert result.result == {"value": 42}
    assert result.progress == 1.0

    # Test serialization
    result_dict = result.to_dict()
    assert result_dict['job_id'] == "test-123"
    assert result_dict['status'] == "completed"

    # Test deserialization
    result2 = JobResult.from_dict(result_dict)
    assert result2.job_id == result.job_id
    assert result2.status == result.status


def test_progress_callback():
    """Test ProgressCallback"""
    result = JobResult(job_id="test-123")

    updates = []

    def update_fn(r):
        updates.append((r.progress, r.progress_message))

    callback = ProgressCallback(result, update_fn)

    callback.update(0.5, "Halfway")
    assert result.progress == 0.5
    assert result.progress_message == "Halfway"
    assert len(updates) == 1

    callback(1.0, "Done")  # Test __call__
    assert result.progress == 1.0
    assert len(updates) == 2


def test_job_queue():
    """Test JobQueue priority ordering"""
    queue = JobQueue()

    # Add jobs with different priorities
    job_low = Job(name="Low", function=simple_task, priority=JobPriority.LOW)
    job_normal = Job(
        name="Normal",
        function=simple_task,
        priority=JobPriority.NORMAL)
    job_high = Job(
        name="High",
        function=simple_task,
        priority=JobPriority.HIGH)

    queue.enqueue(job_low)
    queue.enqueue(job_normal)
    queue.enqueue(job_high)

    assert queue.size() == 3

    # Should dequeue in priority order (high first)
    first = queue.dequeue()
    assert first.name == "High"

    second = queue.dequeue()
    assert second.name == "Normal"

    third = queue.dequeue()
    assert third.name == "Low"

    assert queue.size() == 0


def test_job_queue_scheduled():
    """Test JobQueue with scheduled jobs"""
    queue = JobQueue()

    # Schedule job for future
    future_time = datetime.now() + timedelta(seconds=1)
    job = Job(name="Future", function=simple_task, scheduled_at=future_time)

    queue.enqueue(job)

    # Should not dequeue yet
    result = queue.dequeue()
    assert result is None

    # Wait for scheduled time
    time.sleep(1.1)

    # Should dequeue now
    result = queue.dequeue()
    assert result is not None
    assert result.name == "Future"


def test_job_manager_basic():
    """Test basic JobManager functionality"""
    manager = JobManager(max_workers=2)
    manager.start()

    try:
        # Enqueue simple job
        job = Job(name="Test", function=simple_task, args=(1, 2))
        job_id = manager.enqueue(job)

        assert job_id == job.id

        # Wait for completion
        max_wait = 5
        start_time = time.time()
        while time.time() - start_time < max_wait:
            result = manager.poll(job_id)
            if result and result.status == JobStatus.COMPLETED:
                break
            time.sleep(0.1)

        result = manager.poll(job_id)
        assert result is not None
        assert result.status == JobStatus.COMPLETED
        assert result.result == 3

    finally:
        manager.stop()


def test_job_manager_retry():
    """Test JobManager retry logic"""
    manager = JobManager(max_workers=1)
    manager.start()

    try:
        # Job with transient error
        job = Job(
            name="Transient Error",
            function=transient_error_task,
            max_retries=2,
            retry_delay=0.1
        )
        job_id = manager.enqueue(job)

        # Wait for retries
        time.sleep(2)

        result = manager.poll(job_id)
        assert result is not None
        assert result.status == JobStatus.FAILED
        assert result.error_type == ErrorType.TRANSIENT

        # Check that job was retried
        job_obj = manager.running_jobs.get(job_id) or None
        if job_obj is None:
            # Job completed, check retry count from dead letter queue
            for dead_job, dead_result in manager.dead_letter_queue:
                if dead_job.id == job_id:
                    assert dead_job.retry_count > 0
                    break

    finally:
        manager.stop()


def test_job_manager_cancellation():
    """Test job cancellation"""
    manager = JobManager(max_workers=1)
    manager.start()

    try:
        # Enqueue slow job
        job = Job(name="Slow", function=slow_task, args=(2.0,))
        job_id = manager.enqueue(job)

        # Wait a bit for job to start
        time.sleep(0.5)

        # Cancel job
        cancelled = manager.cancel(job_id)
        assert cancelled

        # Check status
        result = manager.poll(job_id)
        assert result is not None
        assert result.status == JobStatus.CANCELLED

    finally:
        manager.stop()


def test_job_manager_dependencies():
    """Test job dependencies"""
    manager = JobManager(max_workers=2)
    manager.start()

    try:
        # Job 1
        job1 = Job(name="Job1", function=simple_task, args=(1, 2))
        job1_id = manager.enqueue(job1)

        # Job 2 depends on Job 1
        job2 = Job(
            name="Job2",
            function=simple_task,
            args=(3, 4),
            depends_on=[job1_id]
        )
        job2_id = manager.enqueue(job2)

        # Wait for both to complete
        max_wait = 5
        start_time = time.time()
        while time.time() - start_time < max_wait:
            result1 = manager.poll(job1_id)
            result2 = manager.poll(job2_id)

            if (result1 and result1.status == JobStatus.COMPLETED and
                    result2 and result2.status == JobStatus.COMPLETED):
                break

            time.sleep(0.1)

        result1 = manager.poll(job1_id)
        result2 = manager.poll(job2_id)

        assert result1.status == JobStatus.COMPLETED
        assert result2.status == JobStatus.COMPLETED

        # Job 2 should complete after Job 1
        assert result2.started_at >= result1.completed_at

    finally:
        manager.stop()


def test_error_categorization():
    """Test error type categorization"""
    manager = JobManager(max_workers=1)

    # Transient errors
    assert manager._categorize_error(TimeoutError()) == ErrorType.TRANSIENT
    assert manager._categorize_error(ConnectionError()) == ErrorType.TRANSIENT
    assert manager._categorize_error(OSError()) == ErrorType.TRANSIENT

    # Permanent errors
    assert manager._categorize_error(ValueError()) == ErrorType.PERMANENT
    assert manager._categorize_error(TypeError()) == ErrorType.PERMANENT
    assert manager._categorize_error(KeyError()) == ErrorType.PERMANENT


def test_global_functions():
    """Test global enqueue, poll, cancel functions"""
    # These use the global job manager
    job = Job(name="Global Test", function=simple_task, args=(5, 10))

    job_id = enqueue(job)
    assert job_id is not None

    # Wait for completion
    max_wait = 5
    start_time = time.time()
    while time.time() - start_time < max_wait:
        result = poll(job_id)
        if result and result.status == JobStatus.COMPLETED:
            break
        time.sleep(0.1)

    result = poll(job_id)
    assert result is not None
    assert result.status == JobStatus.COMPLETED
    assert result.result == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
