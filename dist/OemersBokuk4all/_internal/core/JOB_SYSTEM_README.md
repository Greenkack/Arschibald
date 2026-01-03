# Background Job Processing System

## Overview

The Background Job Processing System provides a robust, production-ready solution for executing long-running tasks asynchronously without blocking the UI. It includes priority queues, job scheduling, progress tracking, automatic retry with exponential backoff, and comprehensive error handling.

## Key Features

- **Priority Queue System**: Jobs are executed based on priority (LOW, NORMAL, HIGH, CRITICAL)
- **Job Scheduling**: Schedule jobs for future execution or use cron expressions
- **Progress Tracking**: Real-time progress updates with progress bars (no spinners)
- **Automatic Retry**: Exponential backoff with jitter for transient errors
- **Job Persistence**: Jobs survive application restarts
- **Dead Letter Queue**: Failed jobs are moved to DLQ for manual inspection
- **Job Dependencies**: Jobs can depend on other jobs
- **Graceful Shutdown**: Workers complete running jobs before shutdown
- **Notification System**: Configurable notifications for job failures

## Architecture

```
┌─────────────────┐
│   Application   │
└────────┬────────┘
         │ enqueue(job)
         ▼
┌─────────────────┐
│   JobManager    │
│  - Priority Q   │
│  - Workers      │
│  - Registry     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Worker 1│ │Worker N│
└────┬───┘ └───┬────┘
     │         │
     ▼         ▼
┌─────────────────┐
│   JobRepository │
│   (Database)    │
└─────────────────┘
```

## Quick Start

### 1. Basic Job Execution

```python
from core import Job, enqueue, poll

# Define a simple job function
def calculate_report(user_id: str, progress_callback=None):
    # Simulate work
    for i in range(10):
        time.sleep(1)
        if progress_callback:
            progress_callback(i / 10, f"Processing step {i+1}/10")
    
    return {"status": "completed", "user_id": user_id}

# Create and enqueue job
job = Job(
    name="Calculate Report",
    function=calculate_report,
    args=("user123",),
    priority=JobPriority.HIGH
)

job_id = enqueue(job)

# Poll for results
result = poll(job_id)
print(f"Status: {result.status}")
print(f"Progress: {result.progress * 100}%")
```

### 2. Job with Retry Configuration

```python
from core import Job, JobPriority, enqueue

def unreliable_api_call(endpoint: str):
    # This might fail with transient errors
    response = requests.get(endpoint)
    return response.json()

job = Job(
    name="API Call",
    function=unreliable_api_call,
    args=("https://api.example.com/data",),
    priority=JobPriority.NORMAL,
    max_retries=5,
    retry_delay=2,  # Start with 2 seconds
    retry_backoff=2.0,  # Double each time
    retry_jitter=True  # Add random jitter
)

job_id = enqueue(job)
```

### 3. Scheduled Job

```python
from datetime import datetime, timedelta
from core import Job, enqueue

# Schedule job for future execution
scheduled_time = datetime.now() + timedelta(hours=1)

job = Job(
    name="Scheduled Report",
    function=generate_daily_report,
    scheduled_at=scheduled_time
)

job_id = enqueue(job)
```

### 4. Job with Dependencies

```python
from core import Job, enqueue

# Job 1: Fetch data
job1 = Job(
    name="Fetch Data",
    function=fetch_data_from_api
)
job1_id = enqueue(job1)

# Job 2: Process data (depends on job1)
job2 = Job(
    name="Process Data",
    function=process_data,
    depends_on=[job1_id]
)
job2_id = enqueue(job2)

# Job 2 will only run after job1 completes successfully
```

## UI Integration

### Progress Bar Widget

```python
import streamlit as st
from core import Job, enqueue
from core.job_ui import render_job_progress

# Enqueue job
job = Job(name="Long Calculation", function=long_calculation)
job_id = enqueue(job)

# Render progress (no spinners!)
result = render_job_progress(
    job_id=job_id,
    poll_interval=0.5,
    show_details=True
)

if result.status == JobStatus.COMPLETED:
    st.success("Job completed!")
    st.json(result.result)
```

### Job Status Dashboard

```python
import streamlit as st
from core.job_ui import render_job_status_dashboard

st.title("Job Management")

# Render unified dashboard
render_job_status_dashboard()
```

### Cancel Job Button

```python
from core.job_ui import cancel_job_button

if cancel_job_button(job_id, label="Cancel This Job"):
    st.success("Job cancelled")
```

## Function Registry

For jobs that need to survive application restarts, register functions:

```python
from core import get_job_manager, Job, enqueue

manager = get_job_manager()

# Register function
manager.register_function("calculate_report", calculate_report)

# Create job with function name
job = Job(
    name="Report",
    function_name="calculate_report",  # Use name instead of function
    args=("user123",)
)

job_id = enqueue(job)
```

## Progress Tracking

### In Job Function

```python
def long_running_task(data, progress_callback=None):
    total_steps = len(data)
    
    for i, item in enumerate(data):
        # Do work
        process_item(item)
        
        # Update progress
        if progress_callback:
            progress = (i + 1) / total_steps
            progress_callback(
                progress,
                f"Processing item {i+1}/{total_steps}",
                current_item=item,
                items_processed=i+1
            )
    
    return {"processed": total_steps}
```

### Multi-Step Progress

```python
def complex_task(progress_callback=None):
    # Step 1: Fetch data (0-30%)
    if progress_callback:
        progress_callback(0.0, "Fetching data...")
    
    data = fetch_data()
    
    if progress_callback:
        progress_callback(0.3, "Data fetched")
    
    # Step 2: Process data (30-70%)
    if progress_callback:
        progress_callback(0.3, "Processing data...")
    
    result = process_data(data)
    
    if progress_callback:
        progress_callback(0.7, "Data processed")
    
    # Step 3: Save results (70-100%)
    if progress_callback:
        progress_callback(0.7, "Saving results...")
    
    save_results(result)
    
    if progress_callback:
        progress_callback(1.0, "Complete!")
    
    return result
```

## Error Handling

### Error Types

The system automatically categorizes errors:

- **Transient Errors**: Temporary failures that can be retried
  - `TimeoutError`
  - `ConnectionError`
  - `OSError`
  - Errors with keywords: "timeout", "connection", "temporary", "unavailable"

- **Permanent Errors**: Failures that should not be retried
  - `ValueError`
  - `TypeError`
  - `KeyError`
  - All other exceptions

### Custom Error Handling

```python
def robust_task():
    try:
        # Risky operation
        result = risky_operation()
        return result
    except SpecificError as e:
        # Handle specific error
        logger.error("Specific error occurred", error=str(e))
        raise  # Re-raise to let job system handle retry
    except Exception as e:
        # Handle unexpected errors
        logger.error("Unexpected error", error=str(e))
        raise
```

## Notifications

### Add Email Notifications

```python
from core.job_notifications import EmailNotificationChannel, add_notification_channel

# Configure email channel
email_channel = EmailNotificationChannel(
    smtp_host="smtp.example.com",
    smtp_port=587,
    from_addr="jobs@example.com",
    to_addrs=["admin@example.com"]
)

add_notification_channel(email_channel)
```

### Add Webhook Notifications

```python
from core.job_notifications import WebhookNotificationChannel, add_notification_channel

# Configure webhook
webhook_channel = WebhookNotificationChannel(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)

add_notification_channel(webhook_channel)
```

## Job Cleanup

### Automatic Cleanup

```python
from core import get_job_manager

manager = get_job_manager()

# Clean up completed jobs older than 7 days
deleted_count = manager.cleanup_old_results(retention_days=7)
print(f"Cleaned up {deleted_count} old job results")
```

### Manual Cleanup via CLI

```bash
# Clean up old jobs
python -m core.cli jobs cleanup --retention-days 7
```

## Dead Letter Queue

### Inspect Failed Jobs

```python
from core import get_job_manager

manager = get_job_manager()

# Get failed jobs
dead_letter = manager.get_dead_letter_queue()

for job, result in dead_letter:
    print(f"Job: {job.name}")
    print(f"Error: {result.error}")
    print(f"Traceback: {result.traceback}")
```

### Retry Failed Jobs

```python
# Retry a failed job
for job, result in dead_letter:
    if should_retry(job):
        # Reset retry count
        job.retry_count = 0
        # Re-enqueue
        enqueue(job)
```

## Best Practices

### 1. Use Progress Callbacks

Always accept and use progress callbacks for long-running tasks:

```python
def good_task(data, progress_callback=None):
    for i, item in enumerate(data):
        process(item)
        if progress_callback:
            progress_callback(i / len(data), f"Processing {i}/{len(data)}")
```

### 2. Set Appropriate Timeouts

```python
job = Job(
    name="API Call",
    function=call_external_api,
    timeout=30  # 30 seconds max
)
```

### 3. Use Priority Wisely

```python
# User-facing tasks
job = Job(name="User Report", function=generate_report, priority=JobPriority.HIGH)

# Background maintenance
job = Job(name="Cleanup", function=cleanup_old_data, priority=JobPriority.LOW)
```

### 4. Tag Jobs for Organization

```python
job = Job(
    name="Process Order",
    function=process_order,
    tags={"order", "payment", "user:123"}
)
```

### 5. Add Metadata

```python
job = Job(
    name="Generate Report",
    function=generate_report,
    metadata={
        "user_id": "user123",
        "report_type": "monthly",
        "requested_at": datetime.now().isoformat()
    }
)
```

## Performance Considerations

### Worker Configuration

```python
# In config
jobs:
  max_workers: 8  # Adjust based on CPU cores and workload
  job_timeout: 3600  # 1 hour default timeout
```

### Queue Size Monitoring

```python
from core import get_job_manager

manager = get_job_manager()
queue_size = manager.get_queue_size()

if queue_size > 100:
    logger.warning("Job queue is large", size=queue_size)
```

### Memory Management

For jobs processing large datasets:

```python
def memory_efficient_task(data_source):
    # Process in chunks
    for chunk in read_chunks(data_source, chunk_size=1000):
        process_chunk(chunk)
        # Chunk is garbage collected after each iteration
```

## Troubleshooting

### Job Not Starting

1. Check if job manager is running:
   ```python
   manager = get_job_manager()
   print(f"Running: {manager.running}")
   print(f"Workers: {len(manager.workers)}")
   ```

2. Check dependencies:
   ```python
   job = manager.queue.peek()
   if job:
       print(f"Next job: {job.name}")
       print(f"Dependencies: {job.depends_on}")
   ```

### Job Stuck in Running State

1. Check for timeout:
   ```python
   result = poll(job_id)
   if result.started_at:
       duration = datetime.now() - result.started_at
       print(f"Running for: {duration}")
   ```

2. Cancel if needed:
   ```python
   cancel(job_id)
   ```

### High Failure Rate

1. Check error types:
   ```python
   from core.job_repository import JobRepository
   repo = JobRepository()
   stats = repo.get_job_statistics()
   print(f"Failed: {stats['failed']}")
   ```

2. Inspect dead letter queue:
   ```python
   dead_letter = manager.get_dead_letter_queue()
   for job, result in dead_letter:
       print(f"Error type: {result.error_type}")
       print(f"Error: {result.error}")
   ```

## API Reference

### Core Functions

- `enqueue(job: Job) -> str`: Enqueue job for execution
- `poll(job_id: str) -> Optional[JobResult]`: Get job status and results
- `cancel(job_id: str) -> bool`: Cancel job
- `register_job_function(name: str, func: Callable)`: Register function for serialization

### Classes

- `Job`: Job definition with configuration
- `JobResult`: Job execution result with progress
- `JobManager`: Core job management system
- `JobRepository`: Database persistence layer
- `ProgressCallback`: Progress tracking callback

### UI Components

- `render_job_progress()`: Render progress bar widget
- `render_job_status_dashboard()`: Render job dashboard
- `cancel_job_button()`: Render cancel button

## Requirements Satisfied

This implementation satisfies the following requirements:

- **3.1**: Job management with priority queues ✓
- **3.2**: Real-time progress tracking without UI blocking ✓
- **3.3**: Progress bars instead of spinners ✓
- **3.4**: Job cancellation with graceful shutdown ✓
- **3.5**: Exponential backoff retry with jitter ✓
- **3.6**: Job metadata and user attribution ✓
- **3.7**: Job persistence and recovery ✓
- **13.3**: Core classes (Job, JobResult, enqueue, poll, cancel) ✓
