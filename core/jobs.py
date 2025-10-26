"""Background Job Processing System"""

import json
import random
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(int, Enum):
    """Job priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class ErrorType(str, Enum):
    """Error categorization"""
    TRANSIENT = "transient"  # Temporary errors that can be retried
    PERMANENT = "permanent"  # Permanent errors that should not be retried


@dataclass
class Job:
    """Enhanced job definition for background processing"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function: Callable | None = None
    function_name: str = ""  # For serialization
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)

    # Scheduling
    priority: int = JobPriority.NORMAL
    scheduled_at: datetime | None = None
    timeout: int | None = None  # seconds

    # Retry configuration
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 1  # Base delay in seconds
    retry_backoff: float = 2.0  # Exponential backoff multiplier
    retry_jitter: bool = True  # Add random jitter to retry delay

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)

    # Metadata
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Cron scheduling (optional)
    cron_expression: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'function_name': self.function_name,
            'args': list(self.args),
            'kwargs': self.kwargs,
            'priority': self.priority,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'retry_backoff': self.retry_backoff,
            'retry_jitter': self.retry_jitter,
            'depends_on': self.depends_on,
            'tags': list(self.tags),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'cron_expression': self.cron_expression
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Job':
        """Create from dictionary"""
        scheduled_at = None
        if data.get('scheduled_at'):
            scheduled_at = datetime.fromisoformat(data['scheduled_at'])

        return cls(
            id=data['id'],
            name=data.get('name', ''),
            function_name=data.get('function_name', ''),
            args=tuple(data.get('args', [])),
            kwargs=data.get('kwargs', {}),
            priority=data.get('priority', JobPriority.NORMAL),
            scheduled_at=scheduled_at,
            timeout=data.get('timeout'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 1),
            retry_backoff=data.get('retry_backoff', 2.0),
            retry_jitter=data.get('retry_jitter', True),
            depends_on=data.get('depends_on', []),
            tags=set(data.get('tags', [])),
            created_by=data.get('created_by', ''),
            created_at=datetime.fromisoformat(data['created_at']),
            metadata=data.get('metadata', {}),
            cron_expression=data.get('cron_expression')
        )


@dataclass
class JobResult:
    """Job execution result stored in JobResult-Table"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str = ""
    status: JobStatus = JobStatus.PENDING
    result: Any | None = None
    error: str | None = None
    error_type: ErrorType | None = None
    traceback: str | None = None

    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    progress_message: str = ""
    progress_details: dict[str, Any] = field(default_factory=dict)

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    worker_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for database storage"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'status': self.status.value if isinstance(
                self.status,
                JobStatus) else self.status,
            'result': json.dumps(
                self.result) if self.result is not None else None,
            'error': self.error,
            'error_type': self.error_type.value if self.error_type else None,
            'traceback': self.traceback,
            'progress': self.progress,
            'progress_message': self.progress_message,
            'progress_details': self.progress_details,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'metadata': self.metadata,
            'worker_id': self.worker_id}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'JobResult':
        """Create from dictionary"""
        result = None
        if data.get('result'):
            try:
                result = json.loads(data['result'])
            except (json.JSONDecodeError, TypeError):
                result = data['result']

        started_at = None
        if data.get('started_at'):
            started_at = datetime.fromisoformat(data['started_at'])

        completed_at = None
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])

        status = data.get('status', JobStatus.PENDING)
        if isinstance(status, str):
            status = JobStatus(status)

        error_type = data.get('error_type')
        if error_type and isinstance(error_type, str):
            error_type = ErrorType(error_type)

        return cls(
            id=data['id'],
            job_id=data['job_id'],
            status=status,
            result=result,
            error=data.get('error'),
            error_type=error_type,
            traceback=data.get('traceback'),
            progress=data.get('progress', 0.0),
            progress_message=data.get('progress_message', ''),
            progress_details=data.get('progress_details', {}),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=data.get('duration_seconds'),
            metadata=data.get('metadata', {}),
            worker_id=data.get('worker_id')
        )

    def update_progress(
            self,
            progress: float,
            message: str = "",
            **details) -> None:
        """Update job progress"""
        self.progress = max(0.0, min(1.0, progress))
        self.progress_message = message
        if details:
            self.progress_details.update(details)


class ProgressCallback:
    """Progress callback for job functions"""

    def __init__(
            self,
            job_result: JobResult,
            update_fn: Callable | None = None):
        self.job_result = job_result
        self.update_fn = update_fn

    def update(self, progress: float, message: str = "", **details) -> None:
        """Update progress"""
        self.job_result.update_progress(progress, message, **details)
        if self.update_fn:
            self.update_fn(self.job_result)

        logger.debug(
            "Job progress updated",
            job_id=self.job_result.job_id,
            progress=progress,
            message=message
        )

    def __call__(self, progress: float, message: str = "", **details) -> None:
        """Allow callback to be called directly"""
        self.update(progress, message, **details)


class JobQueue:
    """Priority queue for jobs"""

    def __init__(self):
        self._queue: list[tuple[int, datetime, Job]] = []
        self._lock = threading.Lock()

    def enqueue(self, job: Job) -> None:
        """Add job to queue with priority"""
        with self._lock:
            # Priority queue: higher priority first, then FIFO
            priority = -job.priority  # Negative for max-heap behavior
            timestamp = job.scheduled_at or datetime.now()
            self._queue.append((priority, timestamp, job))
            self._queue.sort(key=lambda x: (x[0], x[1]))

    def dequeue(self) -> Job | None:
        """Get next job from queue"""
        with self._lock:
            if not self._queue:
                return None

            # Check for jobs ready to run
            now = datetime.now()
            for i, (priority, timestamp, job) in enumerate(self._queue):
                if timestamp <= now:
                    self._queue.pop(i)
                    return job

            return None

    def peek(self) -> Job | None:
        """Peek at next job without removing"""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][2]

    def remove(self, job_id: str) -> bool:
        """Remove job from queue"""
        with self._lock:
            for i, (_, _, job) in enumerate(self._queue):
                if job.id == job_id:
                    self._queue.pop(i)
                    return True
            return False

    def size(self) -> int:
        """Get queue size"""
        with self._lock:
            return len(self._queue)

    def clear(self) -> None:
        """Clear all jobs from queue"""
        with self._lock:
            self._queue.clear()


class JobManager:
    """Enhanced job manager with priority queues and scheduling"""

    def __init__(self, max_workers: int = 4, auto_recover: bool = True):
        self.max_workers = max_workers
        self.queue = JobQueue()
        self.running_jobs: dict[str, Job] = {}
        self.job_results: dict[str, JobResult] = {}
        self.workers: list[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
        self.worker_id = str(uuid.uuid4())[:8]

        # Function registry for serialization
        self.function_registry: dict[str, Callable] = {}

        # Dead letter queue for failed jobs
        self.dead_letter_queue: list[tuple[Job, JobResult]] = []

        # Auto-recover pending jobs on startup
        if auto_recover:
            self._recover_pending_jobs()

    def register_function(self, name: str, func: Callable) -> None:
        """Register function for job execution"""
        self.function_registry[name] = func
        logger.debug("Function registered", name=name)

    def start(self) -> None:
        """Start job workers"""
        if self.running:
            logger.warning("Job manager already running")
            return

        self.running = True

        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

        logger.info("Job manager started", workers=self.max_workers)

    def stop(self, graceful: bool = True, timeout: int = 30) -> None:
        """Stop job workers"""
        if not self.running:
            return

        logger.info("Stopping job manager", graceful=graceful)
        self.running = False

        if graceful:
            # Wait for running jobs to complete
            start_time = time.time()
            while self.running_jobs and (time.time() - start_time) < timeout:
                time.sleep(0.1)

        # Wait for workers to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=1)

        self.workers.clear()
        logger.info("Job manager stopped")

    def _worker_loop(self) -> None:
        """Worker thread main loop"""
        while self.running:
            try:
                job = self.queue.dequeue()

                if job is None:
                    time.sleep(0.1)
                    continue

                # Check dependencies
                if not self._check_dependencies(job):
                    # Re-queue if dependencies not met
                    self.queue.enqueue(job)
                    time.sleep(0.5)
                    continue

                # Execute job
                self._execute_job(job)

            except Exception as e:
                logger.error("Worker error", error=str(e))
                time.sleep(1)

    def _check_dependencies(self, job: Job) -> bool:
        """Check if job dependencies are satisfied"""
        if not job.depends_on:
            return True

        for dep_id in job.depends_on:
            result = self.job_results.get(dep_id)
            if not result or result.status != JobStatus.COMPLETED:
                return False

        return True

    def _execute_job(self, job: Job) -> None:
        """Execute a job"""
        job_result = JobResult(
            job_id=job.id,
            status=JobStatus.RUNNING,
            started_at=datetime.now(),
            worker_id=self.worker_id
        )

        with self.lock:
            self.running_jobs[job.id] = job
            self.job_results[job.id] = job_result

        logger.info("Job started", job_id=job.id, name=job.name)

        try:
            # Get function
            func = job.function
            if func is None and job.function_name:
                func = self.function_registry.get(job.function_name)

            if func is None:
                raise ValueError(f"Function not found: {job.function_name}")

            # Create progress callback
            def update_progress(result: JobResult):
                self._persist_job_result(result)

            progress_callback = ProgressCallback(job_result, update_progress)

            # Execute with timeout
            if job.timeout:
                result = self._execute_with_timeout(
                    func, job.args, job.kwargs, job.timeout, progress_callback
                )
            else:
                # Add progress callback to kwargs if function accepts it
                kwargs = job.kwargs.copy()
                if 'progress_callback' not in kwargs:
                    kwargs['progress_callback'] = progress_callback

                result = func(*job.args, **kwargs)

            # Job completed successfully
            job_result.status = JobStatus.COMPLETED
            job_result.result = result
            job_result.progress = 1.0
            job_result.completed_at = datetime.now()
            job_result.duration_seconds = (
                job_result.completed_at - job_result.started_at
            ).total_seconds()

            logger.info(
                "Job completed",
                job_id=job.id,
                duration=job_result.duration_seconds
            )

        except Exception as e:
            # Job failed
            import traceback

            job_result.status = JobStatus.FAILED
            job_result.error = str(e)
            job_result.traceback = traceback.format_exc()
            job_result.completed_at = datetime.now()
            job_result.duration_seconds = (
                job_result.completed_at - job_result.started_at
            ).total_seconds()

            # Categorize error
            job_result.error_type = self._categorize_error(e)

            logger.error(
                "Job failed",
                job_id=job.id,
                error=str(e),
                error_type=job_result.error_type
            )

            # Handle retry
            if self._should_retry(job, job_result):
                self._retry_job(job)
                # Notify about retry
                try:
                    from .job_notifications import notify_job_retry
                    notify_job_retry(job, job_result)
                except Exception as e:
                    logger.error(
                        "Failed to send retry notification",
                        error=str(e))
            else:
                # Move to dead letter queue
                self.dead_letter_queue.append((job, job_result))
                # Notify about failure
                try:
                    from .job_notifications import notify_job_failure
                    notify_job_failure(job, job_result)
                except Exception as e:
                    logger.error(
                        "Failed to send failure notification",
                        error=str(e))

        finally:
            with self.lock:
                self.running_jobs.pop(job.id, None)

            # Persist result
            self._persist_job_result(job_result)

    def _execute_with_timeout(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        timeout: int,
        progress_callback: ProgressCallback
    ) -> Any:
        """Execute function with timeout"""
        result = [None]
        exception = [None]

        def target():
            try:
                kwargs_with_progress = kwargs.copy()
                if 'progress_callback' not in kwargs_with_progress:
                    kwargs_with_progress['progress_callback'] = progress_callback
                result[0] = func(*args, **kwargs_with_progress)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(f"Job execution exceeded timeout of {timeout}s")

        if exception[0]:
            raise exception[0]

        return result[0]

    def _categorize_error(self, error: Exception) -> ErrorType:
        """Categorize error as transient or permanent"""
        # Transient errors that can be retried
        transient_errors = (
            TimeoutError,
            ConnectionError,
            OSError,
        )

        if isinstance(error, transient_errors):
            return ErrorType.TRANSIENT

        # Check error message for transient indicators
        error_msg = str(error).lower()
        transient_keywords = [
            'timeout',
            'connection',
            'temporary',
            'unavailable']
        if any(keyword in error_msg for keyword in transient_keywords):
            return ErrorType.TRANSIENT

        return ErrorType.PERMANENT

    def _should_retry(self, job: Job, result: JobResult) -> bool:
        """Determine if job should be retried"""
        if job.retry_count >= job.max_retries:
            return False

        # Only retry transient errors
        if result.error_type == ErrorType.PERMANENT:
            return False

        return True

    def _retry_job(self, job: Job) -> None:
        """Retry failed job with exponential backoff"""
        job.retry_count += 1

        # Calculate retry delay with exponential backoff
        delay = job.retry_delay * (job.retry_backoff ** (job.retry_count - 1))

        # Add jitter if enabled
        if job.retry_jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        # Schedule retry
        job.scheduled_at = datetime.now() + timedelta(seconds=delay)

        logger.info(
            "Job retry scheduled",
            job_id=job.id,
            retry_count=job.retry_count,
            delay_seconds=delay
        )

        # Update result status
        if job.id in self.job_results:
            self.job_results[job.id].status = JobStatus.RETRYING

        # Re-queue job
        self.queue.enqueue(job)

    def _persist_job_result(self, result: JobResult) -> None:
        """Persist job result to database"""
        try:
            from .job_repository import JobRepository
            repo = JobRepository()
            repo.save_job_result(result)
        except Exception as e:
            logger.error("Failed to persist job result", error=str(e))

    def enqueue(self, job: Job) -> str:
        """Enqueue job for execution"""
        # Set function name for serialization
        if job.function and not job.function_name:
            job.function_name = job.function.__name__

        # Create initial result
        result = JobResult(
            job_id=job.id,
            status=JobStatus.QUEUED
        )

        with self.lock:
            self.job_results[job.id] = result

        # Add to queue
        self.queue.enqueue(job)

        # Persist job
        try:
            from .job_repository import JobRepository
            repo = JobRepository()
            repo.save_job(job)
            repo.save_job_result(result)
        except Exception as e:
            logger.error("Failed to persist job", error=str(e))

        logger.info("Job enqueued", job_id=job.id, name=job.name)

        return job.id

    def poll(self, job_id: str) -> JobResult | None:
        """Poll job status and results"""
        # Check in-memory first
        result = self.job_results.get(job_id)

        if result:
            return result

        # Check database
        try:
            from .job_repository import JobRepository
            repo = JobRepository()
            return repo.get_job_result(job_id)
        except Exception as e:
            logger.error("Failed to poll job", job_id=job_id, error=str(e))
            return None

    def cancel(self, job_id: str) -> bool:
        """Cancel job"""
        # Remove from queue
        if self.queue.remove(job_id):
            # Update result
            if job_id in self.job_results:
                self.job_results[job_id].status = JobStatus.CANCELLED
                self.job_results[job_id].completed_at = datetime.now()
                self._persist_job_result(self.job_results[job_id])

            logger.info("Job cancelled (queued)", job_id=job_id)
            return True

        # Check if running
        if job_id in self.running_jobs:
            # Mark as cancelled (worker will check)
            if job_id in self.job_results:
                self.job_results[job_id].status = JobStatus.CANCELLED
                self._persist_job_result(self.job_results[job_id])

            logger.info("Job cancellation requested (running)", job_id=job_id)
            return True

        logger.warning("Job not found for cancellation", job_id=job_id)
        return False

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.size()

    def get_running_jobs(self) -> list[Job]:
        """Get currently running jobs"""
        with self.lock:
            return list(self.running_jobs.values())

    def get_dead_letter_queue(self) -> list[tuple[Job, JobResult]]:
        """Get failed jobs in dead letter queue"""
        return self.dead_letter_queue.copy()

    def clear_dead_letter_queue(self) -> None:
        """Clear dead letter queue"""
        self.dead_letter_queue.clear()

    def _recover_pending_jobs(self) -> None:
        """Recover pending jobs from database after restart"""
        try:
            from .job_repository import JobRepository
            repo = JobRepository()
            pending_jobs = repo.get_pending_jobs()

            for job in pending_jobs:
                # Re-queue the job
                self.queue.enqueue(job)

                # Update result status
                result = repo.get_job_result(job.id)
                if result:
                    self.job_results[job.id] = result

            if pending_jobs:
                logger.info("Pending jobs recovered", count=len(pending_jobs))
        except Exception as e:
            logger.error("Failed to recover pending jobs", error=str(e))

    def cleanup_old_results(self, retention_days: int = 7) -> int:
        """
        Clean up old completed job results

        Args:
            retention_days: Number of days to retain completed jobs

        Returns:
            Number of results cleaned up
        """
        try:
            from .job_repository import JobRepository
            repo = JobRepository()
            return repo.cleanup_completed_jobs(retention_days)
        except Exception as e:
            logger.error("Failed to cleanup old results", error=str(e))
            return 0


# Global job manager instance
_job_manager: JobManager | None = None
_job_manager_lock = threading.Lock()


def get_job_manager() -> JobManager:
    """Get global job manager instance"""
    global _job_manager

    with _job_manager_lock:
        if _job_manager is None:
            from .config import get_config
            config = get_config()
            _job_manager = JobManager(max_workers=config.jobs.max_workers)
            _job_manager.start()

    return _job_manager


def enqueue(job: Job) -> str:
    """Enqueue job for background processing"""
    manager = get_job_manager()
    return manager.enqueue(job)


def poll(job_id: str) -> JobResult | None:
    """Poll job status and results"""
    manager = get_job_manager()
    return manager.poll(job_id)


def cancel(job_id: str) -> bool:
    """Cancel running job"""
    manager = get_job_manager()
    return manager.cancel(job_id)


def register_job_function(name: str, func: Callable) -> None:
    """Register function for job execution"""
    manager = get_job_manager()
    manager.register_function(name, func)
