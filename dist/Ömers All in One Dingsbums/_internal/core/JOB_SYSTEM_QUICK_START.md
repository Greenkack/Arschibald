# Background Job Processing System - Quick Start

## 5-Minute Quick Start

### 1. Basic Setup

```python
# Import the job system
from core import Job, JobPriority, enqueue, poll

# Define a job function
def my_task(data, progress_callback=None):
    """Your task function"""
    # Do work
    result = process_data(data)
    
    # Update progress (optional)
    if progress_callback:
        progress_callback(1.0, "Complete!")
    
    return result

# Create and enqueue a job
job = Job(
    name="My Task",
    function=my_task,
    args=({"key": "value"},),
    priority=JobPriority.NORMAL
)

job_id = enqueue(job)
print(f"Job enqueued: {job_id}")

# Poll for results
result = poll(job_id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### 2. With Progress Tracking

```python
def long_task(items, progress_callback=None):
    """Task with progress updates"""
    total = len(items)
    
    for i, item in enumerate(items):
        # Process item
        process(item)
        
        # Update progress
        if progress_callback:
            progress = (i + 1) / total
            progress_callback(
                progress,
                f"Processing {i+1}/{total}",
                current_item=item
            )
    
    return {"processed": total}

# Enqueue
job = Job(name="Process Items", function=long_task, args=([1,2,3,4,5],))
job_id = enqueue(job)

# Monitor progress
import time
while True:
    result = poll(job_id)
    print(f"Progress: {result.progress * 100:.0f}% - {result.progress_message}")
    
    if result.status.value in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(0.5)
```

### 3. Streamlit Integration

```python
import streamlit as st
from core import Job, enqueue
from core.job_ui import render_job_progress

st.title("Job Processing Demo")

# Button to start job
if st.button("Start Long Calculation"):
    job = Job(
        name="Long Calculation",
        function=long_calculation,
        args=(1000,)
    )
    job_id = enqueue(job)
    st.session_state.job_id = job_id

# Show progress if job is running
if 'job_id' in st.session_state:
    result = render_job_progress(
        st.session_state.job_id,
        poll_interval=0.5,
        show_details=True
    )
    
    if result.status.value == 'completed':
        st.success("Job completed!")
        st.json(result.result)
        del st.session_state.job_id
```

### 4. With Automatic Retry

```python
from core import Job, enqueue

def unreliable_api_call(endpoint):
    """API call that might fail"""
    response = requests.get(endpoint)
    return response.json()

# Job with retry configuration
job = Job(
    name="API Call",
    function=unreliable_api_call,
    args=("https://api.example.com/data",),
    max_retries=5,          # Retry up to 5 times
    retry_delay=2,          # Start with 2 second delay
    retry_backoff=2.0,      # Double delay each time
    retry_jitter=True       # Add random jitter
)

job_id = enqueue(job)
```

### 5. Scheduled Jobs

```python
from datetime import datetime, timedelta
from core import Job, enqueue

# Schedule for 1 hour from now
scheduled_time = datetime.now() + timedelta(hours=1)

job = Job(
    name="Scheduled Report",
    function=generate_daily_report,
    scheduled_at=scheduled_time
)

job_id = enqueue(job)
print(f"Job scheduled for {scheduled_time}")
```

## Common Patterns

### Pattern 1: Fire and Forget

```python
# Just enqueue and don't wait
job_id = enqueue(Job(name="Cleanup", function=cleanup_old_data))
```

### Pattern 2: Wait for Completion

```python
job_id = enqueue(job)

# Wait for completion
while True:
    result = poll(job_id)
    if result.status.value in ['completed', 'failed', 'cancelled']:
        break
    time.sleep(0.5)

if result.status.value == 'completed':
    print(f"Success: {result.result}")
else:
    print(f"Failed: {result.error}")
```

### Pattern 3: Job Chain (Dependencies)

```python
# Job 1: Fetch data
job1 = Job(name="Fetch", function=fetch_data)
job1_id = enqueue(job1)

# Job 2: Process (depends on job1)
job2 = Job(
    name="Process",
    function=process_data,
    depends_on=[job1_id]
)
job2_id = enqueue(job2)

# Job 3: Save (depends on job2)
job3 = Job(
    name="Save",
    function=save_results,
    depends_on=[job2_id]
)
job3_id = enqueue(job3)
```

### Pattern 4: Batch Processing

```python
# Enqueue multiple jobs
job_ids = []
for item in items:
    job = Job(
        name=f"Process {item}",
        function=process_item,
        args=(item,),
        priority=JobPriority.HIGH
    )
    job_ids.append(enqueue(job))

# Wait for all to complete
while True:
    results = [poll(jid) for jid in job_ids]
    if all(r.status.value in ['completed', 'failed'] for r in results):
        break
    time.sleep(1)
```

### Pattern 5: Progress Dashboard

```python
import streamlit as st
from core.job_ui import render_job_status_dashboard

st.title("Job Management Dashboard")

# Show all jobs
render_job_status_dashboard()

# Refresh every 2 seconds
time.sleep(2)
st.rerun()
```

## Configuration

### Environment Variables

```bash
# Job system configuration
JOB_BACKEND=memory          # or 'redis', 'rq'
JOB_MAX_WORKERS=4           # Number of worker threads
JOB_TIMEOUT=3600            # Default timeout in seconds
```

### In Code

```python
from core import get_job_manager

manager = get_job_manager()

# Register functions for persistence
manager.register_function("my_task", my_task)

# Get statistics
print(f"Queue size: {manager.get_queue_size()}")
print(f"Running jobs: {len(manager.get_running_jobs())}")
```

## Troubleshooting

### Job Not Starting

```python
from core import get_job_manager

manager = get_job_manager()
print(f"Manager running: {manager.running}")
print(f"Workers: {len(manager.workers)}")
print(f"Queue size: {manager.get_queue_size()}")
```

### Cancel Stuck Job

```python
from core import cancel

if cancel(job_id):
    print("Job cancelled")
else:
    print("Job not found or already completed")
```

### Check Failed Jobs

```python
from core import get_job_manager

manager = get_job_manager()
dead_letter = manager.get_dead_letter_queue()

for job, result in dead_letter:
    print(f"Failed: {job.name}")
    print(f"Error: {result.error}")
```

## Next Steps

1. **Read full documentation**: `core/JOB_SYSTEM_README.md`
2. **Run examples**: `python core/example_job_usage.py`
3. **Run tests**: `pytest core/test_jobs.py`
4. **Initialize database**: 
   ```python
   from core import init_job_tables
   init_job_tables()
   ```

## Key Points

✓ Jobs run in background threads - UI stays responsive
✓ Progress bars instead of spinners - better UX
✓ Automatic retry with exponential backoff - handles transient errors
✓ Jobs survive application restarts - persistent storage
✓ Priority queue - important jobs run first
✓ Job dependencies - build complex workflows
✓ Graceful shutdown - no data loss
✓ Dead letter queue - inspect and retry failed jobs

## Support

- Documentation: `core/JOB_SYSTEM_README.md`
- Examples: `core/example_job_usage.py`
- Tests: `core/test_jobs.py`
- Verification: `python core/verify_job_system.py`
