"""Example Usage of Background Job Processing System"""

import time
from datetime import datetime, timedelta

from core.jobs import Job, JobPriority, cancel, enqueue, get_job_manager, poll


# Example 1: Simple Job
def simple_calculation(x: int, y: int, progress_callback=None) -> int:
    """Simple calculation with progress tracking"""
    if progress_callback:
        progress_callback(0.0, "Starting calculation")

    time.sleep(1)

    if progress_callback:
        progress_callback(0.5, "Halfway done")

    result = x + y

    time.sleep(1)

    if progress_callback:
        progress_callback(1.0, "Complete")

    return result


def example_simple_job():
    """Example: Simple job execution"""
    print("\n=== Example 1: Simple Job ===")

    job = Job(
        name="Simple Addition",
        function=simple_calculation,
        args=(10, 20),
        priority=JobPriority.NORMAL
    )

    job_id = enqueue(job)
    print(f"Job enqueued: {job_id}")

    # Poll for results
    while True:
        result = poll(job_id)
        if result:
            print(f"Status: {result.status.value}")
            print(f"Progress: {result.progress * 100:.0f}%")
            print(f"Message: {result.progress_message}")

            if result.status.value in ['completed', 'failed', 'cancelled']:
                break

        time.sleep(0.5)

    if result.result:
        print(f"Result: {result.result}")


# Example 2: Long Running Task with Progress
def long_running_task(items: list, progress_callback=None) -> dict:
    """Process multiple items with progress tracking"""
    total = len(items)
    processed = []

    for i, item in enumerate(items):
        # Simulate processing
        time.sleep(0.5)
        processed.append(item * 2)

        # Update progress
        if progress_callback:
            progress = (i + 1) / total
            progress_callback(
                progress,
                f"Processing item {i + 1}/{total}",
                current_item=item,
                processed_count=i + 1
            )

    return {"processed": processed, "total": total}


def example_long_running_job():
    """Example: Long running job with detailed progress"""
    print("\n=== Example 2: Long Running Job ===")

    items = list(range(10))

    job = Job(
        name="Process Items",
        function=long_running_task,
        args=(items,),
        priority=JobPriority.HIGH
    )

    job_id = enqueue(job)
    print(f"Job enqueued: {job_id}")

    # Poll with progress details
    while True:
        result = poll(job_id)
        if result:
            print(f"\rProgress: {result.progress *
                                 100:.0f}% - {result.progress_message}", end='')

            if result.status.value in ['completed', 'failed', 'cancelled']:
                print()  # New line
                break

        time.sleep(0.3)

    if result.result:
        print(f"Result: {result.result}")


# Example 3: Job with Retry
def unreliable_task(fail_count: int = 2, progress_callback=None) -> str:
    """Task that fails a few times before succeeding"""
    import random

    if progress_callback:
        progress_callback(0.5, "Attempting operation")

    # Simulate transient failure
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("Temporary connection issue")

    if progress_callback:
        progress_callback(1.0, "Success")

    return "Operation completed successfully"


def example_retry_job():
    """Example: Job with automatic retry"""
    print("\n=== Example 3: Job with Retry ===")

    job = Job(
        name="Unreliable Operation",
        function=unreliable_task,
        priority=JobPriority.NORMAL,
        max_retries=5,
        retry_delay=1,
        retry_backoff=2.0,
        retry_jitter=True
    )

    job_id = enqueue(job)
    print(f"Job enqueued: {job_id}")

    # Monitor retries
    last_status = None
    while True:
        result = poll(job_id)
        if result:
            if result.status.value != last_status:
                print(f"Status: {result.status.value}")
                if result.error:
                    print(f"Error: {result.error}")
                last_status = result.status.value

            if result.status.value in ['completed', 'failed', 'cancelled']:
                break

        time.sleep(0.5)

    print(f"Final status: {result.status.value}")
    if result.result:
        print(f"Result: {result.result}")


# Example 4: Scheduled Job
def scheduled_task(message: str, progress_callback=None) -> str:
    """Task scheduled for future execution"""
    if progress_callback:
        progress_callback(0.5, "Executing scheduled task")

    time.sleep(1)

    if progress_callback:
        progress_callback(1.0, "Scheduled task complete")

    return f"Scheduled task executed: {message}"


def example_scheduled_job():
    """Example: Schedule job for future execution"""
    print("\n=== Example 4: Scheduled Job ===")

    # Schedule for 5 seconds from now
    scheduled_time = datetime.now() + timedelta(seconds=5)

    job = Job(
        name="Scheduled Task",
        function=scheduled_task,
        args=("Hello from the future!",),
        scheduled_at=scheduled_time
    )

    job_id = enqueue(job)
    print(f"Job scheduled for: {scheduled_time.strftime('%H:%M:%S')}")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    print("Waiting for scheduled time...")

    # Poll until complete
    while True:
        result = poll(job_id)
        if result:
            if result.status.value == 'queued':
                print(".", end='', flush=True)
            elif result.status.value == 'running':
                print(
                    f"\nJob started at: {datetime.now().strftime('%H:%M:%S')}")
            elif result.status.value in ['completed', 'failed', 'cancelled']:
                break

        time.sleep(0.5)

    print(f"\nResult: {result.result}")


# Example 5: Job Dependencies
def fetch_data(progress_callback=None) -> dict:
    """Fetch data (first job)"""
    if progress_callback:
        progress_callback(0.5, "Fetching data")

    time.sleep(1)
    data = {"values": [1, 2, 3, 4, 5]}

    if progress_callback:
        progress_callback(1.0, "Data fetched")

    return data


def process_data(progress_callback=None) -> dict:
    """Process data (second job, depends on first)"""
    if progress_callback:
        progress_callback(0.5, "Processing data")

    time.sleep(1)

    # In real scenario, would get data from first job's result
    result = {"processed": True, "count": 5}

    if progress_callback:
        progress_callback(1.0, "Data processed")

    return result


def example_job_dependencies():
    """Example: Jobs with dependencies"""
    print("\n=== Example 5: Job Dependencies ===")

    # Job 1: Fetch data
    job1 = Job(
        name="Fetch Data",
        function=fetch_data
    )
    job1_id = enqueue(job1)
    print(f"Job 1 (Fetch) enqueued: {job1_id}")

    # Job 2: Process data (depends on job1)
    job2 = Job(
        name="Process Data",
        function=process_data,
        depends_on=[job1_id]
    )
    job2_id = enqueue(job2)
    print(f"Job 2 (Process) enqueued: {job2_id}")
    print("Job 2 will wait for Job 1 to complete")

    # Monitor both jobs
    while True:
        result1 = poll(job1_id)
        result2 = poll(job2_id)

        print(
            f"\rJob 1: {
                result1.status.value if result1 else 'unknown'} | " f"Job 2: {
                result2.status.value if result2 else 'unknown'}",
            end='')

        if (result1 and result1.status.value in ['completed', 'failed'] and
                result2 and result2.status.value in ['completed', 'failed']):
            print()  # New line
            break

        time.sleep(0.5)

    print(f"Job 1 result: {result1.result}")
    print(f"Job 2 result: {result2.result}")


# Example 6: Job Cancellation
def cancellable_task(duration: int, progress_callback=None) -> str:
    """Long task that can be cancelled"""
    for i in range(duration):
        time.sleep(1)

        if progress_callback:
            progress = (i + 1) / duration
            progress_callback(progress, f"Step {i + 1}/{duration}")

    return "Task completed"


def example_job_cancellation():
    """Example: Cancel a running job"""
    print("\n=== Example 6: Job Cancellation ===")

    job = Job(
        name="Cancellable Task",
        function=cancellable_task,
        args=(10,)  # 10 second task
    )

    job_id = enqueue(job)
    print(f"Job enqueued: {job_id}")
    print("Job will be cancelled after 3 seconds...")

    # Let it run for 3 seconds
    for i in range(6):
        result = poll(job_id)
        if result:
            print(f"Progress: {result.progress * 100:.0f}%")
        time.sleep(0.5)

    # Cancel the job
    print("Cancelling job...")
    if cancel(job_id):
        print("Job cancelled successfully")

    # Check final status
    result = poll(job_id)
    print(f"Final status: {result.status.value}")


# Example 7: Job Manager Statistics
def example_job_statistics():
    """Example: Get job manager statistics"""
    print("\n=== Example 7: Job Statistics ===")

    manager = get_job_manager()

    print(f"Queue size: {manager.get_queue_size()}")
    print(f"Running jobs: {len(manager.get_running_jobs())}")
    print(f"Dead letter queue: {len(manager.get_dead_letter_queue())}")

    # Get database statistics
    try:
        from core.job_repository import JobRepository
        repo = JobRepository()
        stats = repo.get_job_statistics()

        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Could not get database statistics: {e}")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("Background Job Processing System - Examples")
    print("=" * 60)

    # Initialize job manager
    manager = get_job_manager()
    print(f"Job manager started with {manager.max_workers} workers\n")

    try:
        example_simple_job()
        time.sleep(1)

        example_long_running_job()
        time.sleep(1)

        example_retry_job()
        time.sleep(1)

        example_scheduled_job()
        time.sleep(1)

        example_job_dependencies()
        time.sleep(1)

        example_job_cancellation()
        time.sleep(1)

        example_job_statistics()

    finally:
        # Cleanup
        print("\n\nStopping job manager...")
        manager.stop(graceful=True, timeout=10)
        print("Job manager stopped")


if __name__ == "__main__":
    run_all_examples()
