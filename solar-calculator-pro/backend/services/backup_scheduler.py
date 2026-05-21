"""
Backup Scheduler Service

Provides automatic backup scheduling with configurable intervals
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional
import logging

from .database_backup_service import DatabaseBackupService

logger = logging.getLogger(__name__)


class BackupScheduler:
    """Scheduler for automatic database backups"""
    
    def __init__(self, backup_service: DatabaseBackupService):
        self.backup_service = backup_service
        self.scheduler = schedule.Scheduler()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Backup configuration
        self.daily_backup_time = "02:00"  # 2 AM
        self.weekly_backup_day = "sunday"
        self.monthly_backup_day = 1  # First day of month
        
        # Retention policy
        self.retention_policy = {
            'keep_daily': 7,
            'keep_weekly': 4,
            'keep_monthly': 12,
            'keep_yearly': 5
        }
        
        # Last backup tracking
        self.last_full_backup: Optional[datetime] = None
        self.last_incremental_backup: Optional[datetime] = None
    
    def schedule_daily_backup(
        self,
        time: str = "02:00",
        backup_type: str = "incremental",
        encrypt: bool = True,
        compress: bool = True
    ):
        """
        Schedule daily backups
        
        Args:
            time: Time to run backup (HH:MM format)
            backup_type: Type of backup ('full' or 'incremental')
            encrypt: Whether to encrypt backups
            compress: Whether to compress backups
        """
        self.daily_backup_time = time
        
        def daily_backup_job():
            try:
                logger.info(f"Running scheduled daily {backup_type} backup")
                
                if backup_type == "full":
                    metadata = self.backup_service.create_full_backup(
                        encrypt=encrypt,
                        compress=compress
                    )
                    self.last_full_backup = datetime.now()
                else:
                    # Find most recent full backup
                    full_backups = self.backup_service.list_backups(backup_type='full')
                    if not full_backups:
                        logger.warning("No full backup found, creating one")
                        metadata = self.backup_service.create_full_backup(
                            encrypt=encrypt,
                            compress=compress
                        )
                        self.last_full_backup = datetime.now()
                    else:
                        parent_backup_id = full_backups[0].backup_id
                        metadata = self.backup_service.create_incremental_backup(
                            parent_backup_id=parent_backup_id,
                            encrypt=encrypt,
                            compress=compress
                        )
                        self.last_incremental_backup = datetime.now()
                
                logger.info(f"Daily backup completed: {metadata.backup_id}")
                
                # Apply retention policy after backup
                self.backup_service.apply_retention_policy(**self.retention_policy)
                
            except Exception as e:
                logger.error(f"Daily backup failed: {e}")
        
        self.scheduler.every().day.at(time).do(daily_backup_job)
        logger.info(f"Scheduled daily {backup_type} backup at {time}")
    
    def schedule_weekly_backup(
        self,
        day: str = "sunday",
        time: str = "03:00",
        encrypt: bool = True,
        compress: bool = True
    ):
        """
        Schedule weekly full backups
        
        Args:
            day: Day of week (monday, tuesday, etc.)
            time: Time to run backup (HH:MM format)
            encrypt: Whether to encrypt backups
            compress: Whether to compress backups
        """
        self.weekly_backup_day = day
        
        def weekly_backup_job():
            try:
                logger.info("Running scheduled weekly full backup")
                
                metadata = self.backup_service.create_full_backup(
                    encrypt=encrypt,
                    compress=compress
                )
                self.last_full_backup = datetime.now()
                
                logger.info(f"Weekly backup completed: {metadata.backup_id}")
                
                # Apply retention policy after backup
                self.backup_service.apply_retention_policy(**self.retention_policy)
                
            except Exception as e:
                logger.error(f"Weekly backup failed: {e}")
        
        # Schedule based on day
        day_schedule = getattr(self.scheduler.every(), day.lower())
        day_schedule.at(time).do(weekly_backup_job)
        
        logger.info(f"Scheduled weekly full backup on {day} at {time}")
    
    def schedule_monthly_backup(
        self,
        day: int = 1,
        time: str = "04:00",
        encrypt: bool = True,
        compress: bool = True
    ):
        """
        Schedule monthly full backups
        
        Args:
            day: Day of month (1-31)
            time: Time to run backup (HH:MM format)
            encrypt: Whether to encrypt backups
            compress: Whether to compress backups
        """
        self.monthly_backup_day = day
        
        def monthly_backup_job():
            # Check if today is the scheduled day
            if datetime.now().day != day:
                return
            
            try:
                logger.info("Running scheduled monthly full backup")
                
                metadata = self.backup_service.create_full_backup(
                    encrypt=encrypt,
                    compress=compress
                )
                self.last_full_backup = datetime.now()
                
                logger.info(f"Monthly backup completed: {metadata.backup_id}")
                
                # Apply retention policy after backup
                self.backup_service.apply_retention_policy(**self.retention_policy)
                
            except Exception as e:
                logger.error(f"Monthly backup failed: {e}")
        
        # Check daily at specified time
        self.scheduler.every().day.at(time).do(monthly_backup_job)
        
        logger.info(f"Scheduled monthly full backup on day {day} at {time}")
    
    def schedule_retention_cleanup(self, time: str = "05:00"):
        """
        Schedule regular retention policy cleanup
        
        Args:
            time: Time to run cleanup (HH:MM format)
        """
        def cleanup_job():
            try:
                logger.info("Running scheduled retention policy cleanup")
                self.backup_service.apply_retention_policy(**self.retention_policy)
                logger.info("Retention policy cleanup completed")
            except Exception as e:
                logger.error(f"Retention cleanup failed: {e}")
        
        self.scheduler.every().day.at(time).do(cleanup_job)
        logger.info(f"Scheduled retention cleanup at {time}")
    
    def set_retention_policy(
        self,
        keep_daily: int = 7,
        keep_weekly: int = 4,
        keep_monthly: int = 12,
        keep_yearly: int = 5
    ):
        """
        Set backup retention policy
        
        Args:
            keep_daily: Number of daily backups to keep
            keep_weekly: Number of weekly backups to keep
            keep_monthly: Number of monthly backups to keep
            keep_yearly: Number of yearly backups to keep
        """
        self.retention_policy = {
            'keep_daily': keep_daily,
            'keep_weekly': keep_weekly,
            'keep_monthly': keep_monthly,
            'keep_yearly': keep_yearly
        }
        logger.info(f"Retention policy updated: {self.retention_policy}")
    
    def start(self):
        """Start the backup scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        def run_scheduler():
            logger.info("Backup scheduler started")
            while self.running:
                self.scheduler.run_pending()
                time.sleep(60)  # Check every minute
            logger.info("Backup scheduler stopped")
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the backup scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Backup scheduler stopped")
    
    def run_immediate_backup(
        self,
        backup_type: str = "full",
        encrypt: bool = True,
        compress: bool = True
    ):
        """
        Run an immediate backup outside of schedule
        
        Args:
            backup_type: Type of backup ('full' or 'incremental')
            encrypt: Whether to encrypt backup
            compress: Whether to compress backup
            
        Returns:
            BackupMetadata object
        """
        logger.info(f"Running immediate {backup_type} backup")
        
        if backup_type == "full":
            metadata = self.backup_service.create_full_backup(
                encrypt=encrypt,
                compress=compress
            )
            self.last_full_backup = datetime.now()
        else:
            # Find most recent full backup
            full_backups = self.backup_service.list_backups(backup_type='full')
            if not full_backups:
                logger.warning("No full backup found, creating one")
                metadata = self.backup_service.create_full_backup(
                    encrypt=encrypt,
                    compress=compress
                )
                self.last_full_backup = datetime.now()
            else:
                parent_backup_id = full_backups[0].backup_id
                metadata = self.backup_service.create_incremental_backup(
                    parent_backup_id=parent_backup_id,
                    encrypt=encrypt,
                    compress=compress
                )
                self.last_incremental_backup = datetime.now()
        
        logger.info(f"Immediate backup completed: {metadata.backup_id}")
        return metadata
    
    def get_schedule_info(self) -> dict:
        """Get information about scheduled backups"""
        return {
            'running': self.running,
            'daily_backup_time': self.daily_backup_time,
            'weekly_backup_day': self.weekly_backup_day,
            'monthly_backup_day': self.monthly_backup_day,
            'retention_policy': self.retention_policy,
            'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
            'last_incremental_backup': self.last_incremental_backup.isoformat() if self.last_incremental_backup else None,
            'scheduled_jobs': len(self.scheduler.jobs)
        }
