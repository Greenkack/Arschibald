"""job_scheduler.py - Job Scheduling System"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JobScheduler:
    """Job-Scheduler für geplante Aufgaben"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
    
    def start(self):
        """Starte Scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Job Scheduler gestartet")
    
    def stop(self):
        """Stoppe Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Job Scheduler gestoppt")
    
    def add_interval_job(self, job_id: str, func: Callable, seconds: int = 60, **kwargs):
        """Füge Job mit Intervall hinzu"""
        job = self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=seconds),
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        self.jobs[job_id] = job
        logger.info(f"Interval Job '{job_id}' hinzugefügt (alle {seconds}s)")
        return job
    
    def add_cron_job(self, job_id: str, func: Callable, cron_expression: str, **kwargs):
        """Füge Job mit Cron-Schedule hinzu"""
        # Beispiel: "0 2 * * *" für täglich um 2:00 Uhr
        job = self.scheduler.add_job(
            func,
            trigger=CronTrigger.from_crontab(cron_expression),
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        self.jobs[job_id] = job
        logger.info(f"Cron Job '{job_id}' hinzugefügt (Cron: {cron_expression})")
        return job
    
    def remove_job(self, job_id: str):
        """Entferne Job"""
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            logger.info(f"Job '{job_id}' entfernt")
    
    def pause_job(self, job_id: str):
        """Pausiere Job"""
        if job_id in self.jobs:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job '{job_id}' pausiert")
    
    def resume_job(self, job_id: str):
        """Setze Job fort"""
        if job_id in self.jobs:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job '{job_id}' fortgesetzt")
    
    def get_jobs(self) -> Dict[str, Any]:
        """Hole alle Jobs"""
        return {
            job_id: {
                'next_run': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            for job_id, job in self.jobs.items()
        }

# Globaler Scheduler-Instanz
_scheduler = None

def get_scheduler() -> JobScheduler:
    """Hole oder erstelle Scheduler-Instanz"""
    global _scheduler
    if _scheduler is None:
        _scheduler = JobScheduler()
        _scheduler.start()
    return _scheduler
