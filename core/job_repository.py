"""Job Repository for Database Persistence"""

import json
from datetime import datetime, timedelta

try:
    from sqlalchemy import (
        Column,
        DateTime,
        Float,
        Integer,
        String,
        Text,
        create_engine,
    )
    from sqlalchemy.orm import Session

    from .database import Base, get_db_manager

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = object
    Column = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .jobs import Job, JobResult, JobStatus

if SQLALCHEMY_AVAILABLE:

    class JobModel(Base):
        """SQLAlchemy model for Job"""
        __tablename__ = 'jobs'

        id = Column(String(36), primary_key=True)
        name = Column(String(255), nullable=False)
        function_name = Column(String(255), nullable=False)
        args = Column(Text)  # JSON
        kwargs = Column(Text)  # JSON
        priority = Column(Integer, default=1)
        scheduled_at = Column(DateTime, nullable=True)
        timeout = Column(Integer, nullable=True)
        retry_count = Column(Integer, default=0)
        max_retries = Column(Integer, default=3)
        retry_delay = Column(Integer, default=1)
        retry_backoff = Column(Float, default=2.0)
        retry_jitter = Column(Integer, default=1)  # Boolean as int
        depends_on = Column(Text)  # JSON list
        tags = Column(Text)  # JSON list
        created_by = Column(String(255))
        created_at = Column(DateTime, default=datetime.now)
        metadata_json = Column('metadata', Text)  # JSON
        cron_expression = Column(String(255), nullable=True)

    class JobResultModel(Base):
        """SQLAlchemy model for JobResult"""
        __tablename__ = 'job_results'

        id = Column(String(36), primary_key=True)
        job_id = Column(String(36), nullable=False, index=True)
        status = Column(String(20), nullable=False, index=True)
        result = Column(Text, nullable=True)  # JSON
        error = Column(Text, nullable=True)
        error_type = Column(String(20), nullable=True)
        traceback = Column(Text, nullable=True)
        progress = Column(Float, default=0.0)
        progress_message = Column(String(500))
        progress_details = Column(Text)  # JSON
        started_at = Column(DateTime, nullable=True)
        completed_at = Column(DateTime, nullable=True)
        duration_seconds = Column(Float, nullable=True)
        metadata_json = Column('metadata', Text)  # JSON
        worker_id = Column(String(50), nullable=True)
        created_at = Column(DateTime, default=datetime.now)
        updated_at = Column(
            DateTime,
            default=datetime.now,
            onupdate=datetime.now)


class JobRepository:
    """Repository for job persistence and recovery"""

    def __init__(self):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for JobRepository")

        self.db_manager = get_db_manager()

    def save_job(self, job: Job) -> None:
        """Save job to database"""
        with self.db_manager.get_session() as session:
            job_model = session.query(JobModel).filter_by(id=job.id).first()

            if job_model is None:
                job_model = JobModel(id=job.id)

            # Update fields
            job_model.name = job.name
            job_model.function_name = job.function_name
            job_model.args = json.dumps(list(job.args))
            job_model.kwargs = json.dumps(job.kwargs)
            job_model.priority = job.priority
            job_model.scheduled_at = job.scheduled_at
            job_model.timeout = job.timeout
            job_model.retry_count = job.retry_count
            job_model.max_retries = job.max_retries
            job_model.retry_delay = job.retry_delay
            job_model.retry_backoff = job.retry_backoff
            job_model.retry_jitter = 1 if job.retry_jitter else 0
            job_model.depends_on = json.dumps(job.depends_on)
            job_model.tags = json.dumps(list(job.tags))
            job_model.created_by = job.created_by
            job_model.created_at = job.created_at
            job_model.metadata_json = json.dumps(job.metadata)
            job_model.cron_expression = job.cron_expression

            session.add(job_model)
            session.commit()

            logger.debug("Job saved to database", job_id=job.id)

    def get_job(self, job_id: str) -> Job | None:
        """Get job from database"""
        with self.db_manager.get_session() as session:
            job_model = session.query(JobModel).filter_by(id=job_id).first()

            if job_model is None:
                return None

            return Job(
                id=job_model.id,
                name=job_model.name,
                function_name=job_model.function_name,
                args=tuple(json.loads(job_model.args)),
                kwargs=json.loads(job_model.kwargs),
                priority=job_model.priority,
                scheduled_at=job_model.scheduled_at,
                timeout=job_model.timeout,
                retry_count=job_model.retry_count,
                max_retries=job_model.max_retries,
                retry_delay=job_model.retry_delay,
                retry_backoff=job_model.retry_backoff,
                retry_jitter=bool(job_model.retry_jitter),
                depends_on=json.loads(job_model.depends_on),
                tags=set(json.loads(job_model.tags)),
                created_by=job_model.created_by,
                created_at=job_model.created_at,
                metadata=json.loads(job_model.metadata_json),
                cron_expression=job_model.cron_expression
            )

    def save_job_result(self, result: JobResult) -> None:
        """Save job result to database"""
        with self.db_manager.get_session() as session:
            result_model = session.query(
                JobResultModel).filter_by(id=result.id).first()

            if result_model is None:
                result_model = JobResultModel(id=result.id)

            # Update fields
            result_model.job_id = result.job_id
            result_model.status = result.status.value if isinstance(
                result.status, JobStatus) else result.status
            result_model.result = json.dumps(
                result.result) if result.result is not None else None
            result_model.error = result.error
            result_model.error_type = result.error_type.value if result.error_type else None
            result_model.traceback = result.traceback
            result_model.progress = result.progress
            result_model.progress_message = result.progress_message
            result_model.progress_details = json.dumps(result.progress_details)
            result_model.started_at = result.started_at
            result_model.completed_at = result.completed_at
            result_model.duration_seconds = result.duration_seconds
            result_model.metadata_json = json.dumps(result.metadata)
            result_model.worker_id = result.worker_id

            session.add(result_model)
            session.commit()

            logger.debug("Job result saved to database", job_id=result.job_id)

    def get_job_result(self, job_id: str) -> JobResult | None:
        """Get job result from database"""
        with self.db_manager.get_session() as session:
            result_model = session.query(
                JobResultModel).filter_by(job_id=job_id).first()

            if result_model is None:
                return None

            result_data = None
            if result_model.result:
                try:
                    result_data = json.loads(result_model.result)
                except (json.JSONDecodeError, TypeError):
                    result_data = result_model.result

            from .jobs import ErrorType
            error_type = None
            if result_model.error_type:
                error_type = ErrorType(result_model.error_type)

            return JobResult(
                id=result_model.id,
                job_id=result_model.job_id,
                status=JobStatus(
                    result_model.status),
                result=result_data,
                error=result_model.error,
                error_type=error_type,
                traceback=result_model.traceback,
                progress=result_model.progress,
                progress_message=result_model.progress_message,
                progress_details=json.loads(
                    result_model.progress_details) if result_model.progress_details else {},
                started_at=result_model.started_at,
                completed_at=result_model.completed_at,
                duration_seconds=result_model.duration_seconds,
                metadata=json.loads(
                    result_model.metadata_json) if result_model.metadata_json else {},
                worker_id=result_model.worker_id)

    def get_pending_jobs(self) -> list[Job]:
        """Get all pending jobs for recovery"""
        with self.db_manager.get_session() as session:
            job_models = session.query(JobModel).join(
                JobResultModel, JobModel.id == JobResultModel.job_id
            ).filter(
                JobResultModel.status.in_([
                    JobStatus.PENDING.value,
                    JobStatus.QUEUED.value,
                    JobStatus.RETRYING.value
                ])
            ).all()

            jobs = []
            for job_model in job_models:
                job = Job(
                    id=job_model.id,
                    name=job_model.name,
                    function_name=job_model.function_name,
                    args=tuple(json.loads(job_model.args)),
                    kwargs=json.loads(job_model.kwargs),
                    priority=job_model.priority,
                    scheduled_at=job_model.scheduled_at,
                    timeout=job_model.timeout,
                    retry_count=job_model.retry_count,
                    max_retries=job_model.max_retries,
                    retry_delay=job_model.retry_delay,
                    retry_backoff=job_model.retry_backoff,
                    retry_jitter=bool(job_model.retry_jitter),
                    depends_on=json.loads(job_model.depends_on),
                    tags=set(json.loads(job_model.tags)),
                    created_by=job_model.created_by,
                    created_at=job_model.created_at,
                    metadata=json.loads(job_model.metadata_json),
                    cron_expression=job_model.cron_expression
                )
                jobs.append(job)

            return jobs

    def cleanup_completed_jobs(self, retention_days: int = 7) -> int:
        """Clean up completed jobs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        with self.db_manager.get_session() as session:
            # Delete old completed job results
            deleted = session.query(JobResultModel).filter(
                JobResultModel.status == JobStatus.COMPLETED.value,
                JobResultModel.completed_at < cutoff_date
            ).delete()

            session.commit()

            logger.info("Completed jobs cleaned up", count=deleted)
            return deleted

    def get_job_statistics(self) -> dict:
        """Get job statistics"""
        with self.db_manager.get_session() as session:
            total = session.query(JobResultModel).count()
            pending = session.query(JobResultModel).filter_by(
                status=JobStatus.PENDING.value).count()
            queued = session.query(JobResultModel).filter_by(
                status=JobStatus.QUEUED.value).count()
            running = session.query(JobResultModel).filter_by(
                status=JobStatus.RUNNING.value).count()
            completed = session.query(JobResultModel).filter_by(
                status=JobStatus.COMPLETED.value).count()
            failed = session.query(JobResultModel).filter_by(
                status=JobStatus.FAILED.value).count()
            cancelled = session.query(JobResultModel).filter_by(
                status=JobStatus.CANCELLED.value).count()

            return {
                'total': total,
                'pending': pending,
                'queued': queued,
                'running': running,
                'completed': completed,
                'failed': failed,
                'cancelled': cancelled
            }


def init_job_tables() -> None:
    """Initialize job tables in database"""
    if not SQLALCHEMY_AVAILABLE:
        logger.warning(
            "SQLAlchemy not available, skipping job table initialization")
        return

    db_manager = get_db_manager()
    Base.metadata.create_all(db_manager.engine)
    logger.info("Job tables initialized")
