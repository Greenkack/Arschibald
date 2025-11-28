"""
Synchronization Scheduler
Manages automatic synchronization scheduling
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from backend.models.sync_models import SyncSchedule, SyncStatus
from backend.services.sync_service import SyncService

logger = logging.getLogger(__name__)


class SyncScheduler:
    """Scheduler for automatic data synchronization"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Sync scheduler started")
    
    def create_schedule(
        self,
        db: Session,
        user_id: int,
        device_id: str,
        sync_interval: int = 300,
        auto_sync: bool = True,
        sync_on_startup: bool = True,
        sync_on_shutdown: bool = True,
        entity_types: Optional[list] = None
    ) -> SyncSchedule:
        """Create synchronization schedule"""
        # Check if schedule exists
        existing = db.query(SyncSchedule).filter(
            and_(
                SyncSchedule.user_id == user_id,
                SyncSchedule.device_id == device_id
            )
        ).first()
        
        if existing:
            # Update existing schedule
            existing.sync_interval = sync_interval
            existing.auto_sync = auto_sync
            existing.sync_on_startup = sync_on_startup
            existing.sync_on_shutdown = sync_on_shutdown
            existing.entity_types = entity_types
            existing.next_sync_at = datetime.now() + timedelta(seconds=sync_interval)
            db.commit()
            db.refresh(existing)
            
            # Update scheduler job
            self._update_scheduler_job(db, existing)
            
            return existing
        
        # Create new schedule
        schedule = SyncSchedule(
            user_id=user_id,
            device_id=device_id,
            sync_interval=sync_interval,
            auto_sync=auto_sync,
            sync_on_startup=sync_on_startup,
            sync_on_shutdown=sync_on_shutdown,
            entity_types=entity_types,
            next_sync_at=datetime.now() + timedelta(seconds=sync_interval)
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        # Add to scheduler
        if auto_sync:
            self._add_scheduler_job(db, schedule)
        
        logger.info(f"Created sync schedule for user {user_id}, device {device_id}")
        return schedule
    
    def _add_scheduler_job(self, db: Session, schedule: SyncSchedule):
        """Add job to scheduler"""
        job_id = f"sync_{schedule.user_id}_{schedule.device_id}"
        
        # Remove existing job if any
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Add new job
        self.scheduler.add_job(
            func=self._execute_scheduled_sync,
            trigger=IntervalTrigger(seconds=schedule.sync_interval),
            id=job_id,
            args=[schedule.user_id, schedule.device_id],
            replace_existing=True
        )
        
        logger.info(f"Added scheduler job {job_id} with interval {schedule.sync_interval}s")
    
    def _update_scheduler_job(self, db: Session, schedule: SyncSchedule):
        """Update scheduler job"""
        job_id = f"sync_{schedule.user_id}_{schedule.device_id}"
        
        if schedule.auto_sync and schedule.enabled:
            self._add_scheduler_job(db, schedule)
        else:
            # Remove job if auto_sync disabled
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed scheduler job {job_id}")
    
    def _execute_scheduled_sync(self, user_id: int, device_id: str):
        """Execute scheduled synchronization"""
        from backend.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            logger.info(f"Executing scheduled sync for user {user_id}, device {device_id}")
            
            # Get schedule
            schedule = db.query(SyncSchedule).filter(
                and_(
                    SyncSchedule.user_id == user_id,
                    SyncSchedule.device_id == device_id
                )
            ).first()
            
            if not schedule or not schedule.enabled:
                logger.warning(f"Schedule not found or disabled for user {user_id}, device {device_id}")
                return
            
            # Process offline queue
            sync_service = SyncService(db)
            operations = sync_service.process_offline_queue(user_id, device_id)
            
            # Update schedule
            schedule.last_sync_at = datetime.now()
            schedule.last_sync_status = SyncStatus.COMPLETED if operations else SyncStatus.PENDING
            schedule.next_sync_at = datetime.now() + timedelta(seconds=schedule.sync_interval)
            db.commit()
            
            logger.info(f"Scheduled sync completed: {len(operations)} operations processed")
            
        except Exception as e:
            logger.error(f"Error in scheduled sync: {str(e)}")
            
            # Update schedule with error status
            schedule = db.query(SyncSchedule).filter(
                and_(
                    SyncSchedule.user_id == user_id,
                    SyncSchedule.device_id == device_id
                )
            ).first()
            
            if schedule:
                schedule.last_sync_status = SyncStatus.FAILED
                schedule.next_sync_at = datetime.now() + timedelta(seconds=schedule.sync_interval)
                db.commit()
        
        finally:
            db.close()
    
    def enable_schedule(self, db: Session, user_id: int, device_id: str):
        """Enable synchronization schedule"""
        schedule = db.query(SyncSchedule).filter(
            and_(
                SyncSchedule.user_id == user_id,
                SyncSchedule.device_id == device_id
            )
        ).first()
        
        if not schedule:
            raise ValueError("Schedule not found")
        
        schedule.enabled = True
        db.commit()
        
        if schedule.auto_sync:
            self._add_scheduler_job(db, schedule)
        
        logger.info(f"Enabled sync schedule for user {user_id}, device {device_id}")
    
    def disable_schedule(self, db: Session, user_id: int, device_id: str):
        """Disable synchronization schedule"""
        schedule = db.query(SyncSchedule).filter(
            and_(
                SyncSchedule.user_id == user_id,
                SyncSchedule.device_id == device_id
            )
        ).first()
        
        if not schedule:
            raise ValueError("Schedule not found")
        
        schedule.enabled = False
        db.commit()
        
        # Remove from scheduler
        job_id = f"sync_{user_id}_{device_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        logger.info(f"Disabled sync schedule for user {user_id}, device {device_id}")
    
    def trigger_manual_sync(self, user_id: int, device_id: str):
        """Trigger manual synchronization"""
        logger.info(f"Triggering manual sync for user {user_id}, device {device_id}")
        self._execute_scheduled_sync(user_id, device_id)
    
    def shutdown(self):
        """Shutdown scheduler"""
        self.scheduler.shutdown()
        logger.info("Sync scheduler shutdown")


# Global scheduler instance
sync_scheduler = SyncScheduler()
