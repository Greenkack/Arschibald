"""
Background Jobs System
Task 189: Job queue, scheduling, monitoring, and retry logic
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import hashlib
import traceback
from collections import deque


router = APIRouter(prefix="/jobs", tags=["Background Jobs"])


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobType(str, Enum):
    PDF_GENERATION = "pdf_generation"
    EMAIL_SEND = "email_send"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    CALCULATION = "calculation"
    REPORT_GENERATION = "report_generation"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    NOTIFICATION = "notification"
    SYNC = "sync"


class Job(BaseModel):
    """Job model"""
    id: str
    type: JobType
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    payload: Dict[str, Any] = {}
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 300
    progress: int = 0
    created_by: Optional[str] = None
    tags: List[str] = []


class ScheduledJob(BaseModel):
    """Scheduled job model"""
    id: str
    job_type: JobType
    schedule: str  # cron expression or interval
    payload: Dict[str, Any] = {}
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0


class JobQueue:
    """Job queue implementation"""
    
    def __init__(self):
        self.queues: Dict[JobPriority, deque] = {
            JobPriority.CRITICAL: deque(),
            JobPriority.HIGH: deque(),
            JobPriority.NORMAL: deque(),
            JobPriority.LOW: deque()
        }
        self.jobs: Dict[str, Job] = {}
        self.scheduled_jobs: Dict[str, ScheduledJob] = {}
        self.job_history: List[Job] = []
        self.max_history = 1000
        self.handlers: Dict[JobType, Callable] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.max_concurrent = 5
        
    def register_handler(self, job_type: JobType, handler: Callable):
        """Register a job handler"""
        self.handlers[job_type] = handler
        
    def generate_job_id(self) -> str:
        """Generate unique job ID"""
        return hashlib.sha256(f"job_{datetime.now().isoformat()}_{len(self.jobs)}".encode()).hexdigest()[:16]
        
    async def enqueue(
        self,
        job_type: JobType,
        payload: Dict[str, Any] = {},
        priority: JobPriority = JobPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        created_by: Optional[str] = None,
        tags: List[str] = []
    ) -> Job:
        """Add a job to the queue"""
        job = Job(
            id=self.generate_job_id(),
            type=job_type,
            status=JobStatus.QUEUED if not scheduled_at else JobStatus.PENDING,
            priority=priority,
            payload=payload,
            created_at=datetime.now(),
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            created_by=created_by,
            tags=tags
        )
        
        self.jobs[job.id] = job
        
        if not scheduled_at or scheduled_at <= datetime.now():
            self.queues[priority].append(job.id)
            
        return job
        
    async def process_next(self) -> Optional[Job]:
        """Process the next job in queue"""
        # Check concurrent limit
        if len(self.running_jobs) >= self.max_concurrent:
            return None
            
        # Get next job by priority
        for priority in [JobPriority.CRITICAL, JobPriority.HIGH, JobPriority.NORMAL, JobPriority.LOW]:
            if self.queues[priority]:
                job_id = self.queues[priority].popleft()
                job = self.jobs.get(job_id)
                
                if job and job.status == JobStatus.QUEUED:
                    await self._execute_job(job)
                    return job
                    
        return None
        
    async def _execute_job(self, job: Job):
        """Execute a job"""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        handler = self.handlers.get(job.type)
        
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"No handler registered for job type: {job.type}"
            job.completed_at = datetime.now()
            self._add_to_history(job)
            return
            
        try:
            # Create task with timeout
            task = asyncio.create_task(self._run_handler(handler, job))
            self.running_jobs[job.id] = task
            
            result = await asyncio.wait_for(task, timeout=job.timeout_seconds)
            
            job.result = result
            job.status = JobStatus.COMPLETED
            job.progress = 100
            
        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error = f"Job timed out after {job.timeout_seconds} seconds"
            await self._handle_failure(job)
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            await self._handle_failure(job)
            
        finally:
            job.completed_at = datetime.now()
            self.running_jobs.pop(job.id, None)
            self._add_to_history(job)
            
    async def _run_handler(self, handler: Callable, job: Job) -> Any:
        """Run job handler"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(job.payload, job)
        else:
            return handler(job.payload, job)
            
    async def _handle_failure(self, job: Job):
        """Handle job failure with retry logic"""
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.RETRYING
            
            # Schedule retry
            retry_at = datetime.now() + timedelta(seconds=job.retry_delay_seconds * job.retry_count)
            job.scheduled_at = retry_at
            
            # Re-queue after delay
            await asyncio.sleep(job.retry_delay_seconds * job.retry_count)
            job.status = JobStatus.QUEUED
            self.queues[job.priority].append(job.id)
            
    def _add_to_history(self, job: Job):
        """Add job to history"""
        self.job_history.append(job)
        
        # Trim history
        if len(self.job_history) > self.max_history:
            self.job_history = self.job_history[-self.max_history:]
            
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
        
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        job = self.jobs.get(job_id)
        if not job:
            return False
            
        if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            return True
            
        if job.status == JobStatus.RUNNING and job_id in self.running_jobs:
            self.running_jobs[job_id].cancel()
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            return True
            
        return False
        
    def update_progress(self, job_id: str, progress: int):
        """Update job progress"""
        job = self.jobs.get(job_id)
        if job:
            job.progress = min(100, max(0, progress))
            
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queued": {
                priority.value: len(queue)
                for priority, queue in self.queues.items()
            },
            "running": len(self.running_jobs),
            "total_jobs": len(self.jobs),
            "history_size": len(self.job_history),
            "by_status": {
                status.value: sum(1 for j in self.jobs.values() if j.status == status)
                for status in JobStatus
            }
        }


# Global job queue
job_queue = JobQueue()


# Register default handlers
async def pdf_generation_handler(payload: Dict, job: Job) -> Dict:
    """PDF generation job handler"""
    await asyncio.sleep(2)  # Simulate work
    job_queue.update_progress(job.id, 50)
    await asyncio.sleep(2)
    return {"pdf_url": f"/downloads/pdf_{job.id}.pdf"}


async def email_send_handler(payload: Dict, job: Job) -> Dict:
    """Email send job handler"""
    await asyncio.sleep(1)
    return {"sent": True, "recipient": payload.get("to")}


async def data_export_handler(payload: Dict, job: Job) -> Dict:
    """Data export job handler"""
    await asyncio.sleep(3)
    return {"export_url": f"/downloads/export_{job.id}.zip"}


async def calculation_handler(payload: Dict, job: Job) -> Dict:
    """Calculation job handler"""
    await asyncio.sleep(1)
    return {"result": "calculation_complete"}


job_queue.register_handler(JobType.PDF_GENERATION, pdf_generation_handler)
job_queue.register_handler(JobType.EMAIL_SEND, email_send_handler)
job_queue.register_handler(JobType.DATA_EXPORT, data_export_handler)
job_queue.register_handler(JobType.CALCULATION, calculation_handler)


# API Endpoints

@router.post("/enqueue", response_model=Job)
async def enqueue_job(
    job_type: JobType,
    payload: Dict[str, Any] = {},
    priority: JobPriority = JobPriority.NORMAL,
    scheduled_at: Optional[datetime] = None,
    max_retries: int = 3,
    timeout_seconds: int = 300,
    tags: List[str] = [],
    background_tasks: BackgroundTasks = None
):
    """Enqueue a new job"""
    job = await job_queue.enqueue(
        job_type=job_type,
        payload=payload,
        priority=priority,
        scheduled_at=scheduled_at,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        tags=tags
    )
    
    # Start processing in background
    if background_tasks:
        background_tasks.add_task(job_queue.process_next)
        
    return job


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job by ID"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a job"""
    success = job_queue.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    return {"status": "cancelled", "job_id": job_id}


@router.get("/", response_model=List[Job])
async def list_jobs(
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    priority: Optional[JobPriority] = None,
    limit: int = 50
):
    """List jobs with filtering"""
    jobs = list(job_queue.jobs.values())
    
    if status:
        jobs = [j for j in jobs if j.status == status]
    if job_type:
        jobs = [j for j in jobs if j.type == job_type]
    if priority:
        jobs = [j for j in jobs if j.priority == priority]
        
    return sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]


@router.get("/stats/queue")
async def get_queue_stats():
    """Get queue statistics"""
    return job_queue.get_queue_stats()


@router.get("/history/recent")
async def get_recent_history(limit: int = 50):
    """Get recent job history"""
    return job_queue.job_history[-limit:]


@router.post("/process")
async def trigger_processing(background_tasks: BackgroundTasks):
    """Trigger job processing"""
    background_tasks.add_task(job_queue.process_next)
    return {"status": "processing_triggered"}


@router.post("/scheduled", response_model=ScheduledJob)
async def create_scheduled_job(
    job_type: JobType,
    schedule: str,
    payload: Dict[str, Any] = {}
):
    """Create a scheduled job"""
    scheduled = ScheduledJob(
        id=hashlib.sha256(f"sched_{datetime.now().isoformat()}".encode()).hexdigest()[:16],
        job_type=job_type,
        schedule=schedule,
        payload=payload,
        next_run=datetime.now() + timedelta(hours=1)  # Simplified
    )
    job_queue.scheduled_jobs[scheduled.id] = scheduled
    return scheduled


@router.get("/scheduled/list", response_model=List[ScheduledJob])
async def list_scheduled_jobs():
    """List scheduled jobs"""
    return list(job_queue.scheduled_jobs.values())


@router.delete("/scheduled/{schedule_id}")
async def delete_scheduled_job(schedule_id: str):
    """Delete a scheduled job"""
    if schedule_id in job_queue.scheduled_jobs:
        del job_queue.scheduled_jobs[schedule_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Scheduled job not found")
