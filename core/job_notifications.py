"""Job Failure Notification System"""

from abc import ABC, abstractmethod

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .jobs import Job, JobResult, JobStatus


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""

    @abstractmethod
    def send(self, job: Job, result: JobResult, message: str) -> bool:
        """Send notification"""


class LogNotificationChannel(NotificationChannel):
    """Log-based notification channel"""

    def send(self, job: Job, result: JobResult, message: str) -> bool:
        """Send notification via logging"""
        logger.error(
            "Job failure notification",
            job_id=job.id,
            job_name=job.name,
            error=result.error,
            message=message
        )
        return True


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel (placeholder)"""

    def __init__(
            self,
            smtp_host: str,
            smtp_port: int,
            from_addr: str,
            to_addrs: list[str]):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    def send(self, job: Job, result: JobResult, message: str) -> bool:
        """Send notification via email"""
        # Placeholder for email implementation
        logger.info(
            "Email notification would be sent",
            job_id=job.id,
            to=self.to_addrs,
            message=message
        )
        return True


class WebhookNotificationChannel(NotificationChannel):
    """Webhook notification channel"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, job: Job, result: JobResult, message: str) -> bool:
        """Send notification via webhook"""
        try:
            import requests

            payload = {
                'job_id': job.id,
                'job_name': job.name,
                'status': result.status.value,
                'error': result.error,
                'message': message,
                'traceback': result.traceback
            }

            response = requests.post(
                self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Webhook notification sent", job_id=job.id)
            return True

        except Exception as e:
            logger.error("Failed to send webhook notification", error=str(e))
            return False


class JobNotificationManager:
    """Manage job failure notifications"""

    def __init__(self):
        self.channels: list[NotificationChannel] = []

        # Add default log channel
        self.add_channel(LogNotificationChannel())

    def add_channel(self, channel: NotificationChannel) -> None:
        """Add notification channel"""
        self.channels.append(channel)
        logger.debug(
            "Notification channel added",
            channel=type(channel).__name__)

    def notify_failure(self, job: Job, result: JobResult) -> None:
        """Notify about job failure"""
        if result.status != JobStatus.FAILED:
            return

        message = self._format_failure_message(job, result)

        for channel in self.channels:
            try:
                channel.send(job, result, message)
            except Exception as e:
                logger.error(
                    "Failed to send notification",
                    channel=type(channel).__name__,
                    error=str(e)
                )

    def notify_retry(self, job: Job, result: JobResult) -> None:
        """Notify about job retry"""
        message = self._format_retry_message(job, result)

        # Only log retries, don't send to all channels
        logger.warning(
            "Job retry notification",
            job_id=job.id,
            retry_count=job.retry_count,
            message=message
        )

    def _format_failure_message(self, job: Job, result: JobResult) -> str:
        """Format failure notification message"""
        duration_str = f"{
            result.duration_seconds:.2f}s" if result.duration_seconds else "N/A"
        return (
            f"Job '{job.name}' (ID: {job.id}) failed\n"
            f"Error: {result.error}\n"
            f"Error Type: {result.error_type.value if result.error_type else 'unknown'}\n"
            f"Retry Count: {job.retry_count}/{job.max_retries}\n"
            f"Duration: {duration_str}"
        )

    def _format_retry_message(self, job: Job, result: JobResult) -> str:
        """Format retry notification message"""
        return (
            f"Job '{job.name}' (ID: {job.id}) will be retried\n"
            f"Error: {result.error}\n"
            f"Retry Count: {job.retry_count}/{job.max_retries}"
        )


# Global notification manager
_notification_manager: JobNotificationManager | None = None


def get_notification_manager() -> JobNotificationManager:
    """Get global notification manager"""
    global _notification_manager

    if _notification_manager is None:
        _notification_manager = JobNotificationManager()

    return _notification_manager


def add_notification_channel(channel: NotificationChannel) -> None:
    """Add notification channel to global manager"""
    manager = get_notification_manager()
    manager.add_channel(channel)


def notify_job_failure(job: Job, result: JobResult) -> None:
    """Notify about job failure"""
    manager = get_notification_manager()
    manager.notify_failure(job, result)


def notify_job_retry(job: Job, result: JobResult) -> None:
    """Notify about job retry"""
    manager = get_notification_manager()
    manager.notify_retry(job, result)
