"""
Async Operations Module

This module provides async operation utilities including:
- Background task management
- Async database operations
- Task queue management
- Progress tracking
"""

from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import asyncio
import logging
import uuid
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Background task representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }


class BackgroundTaskManager:
    """Manage background tasks"""
    
    def __init__(self, max_workers: int = 4):
        self.tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
    
    def create_task(
        self,
        func: Callable,
        *args,
        name: str = "",
        **kwargs
    ) -> Task:
        """
        Create and start a background task
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            name: Task name
            **kwargs: Keyword arguments for function
            
        Returns:
            Task object
        """
        task = Task(name=name or func.__name__)
        self.tasks[task.id] = task
        
        # Submit to executor
        future = self.executor.submit(self._execute_task, task, func, *args, **kwargs)
        
        logger.info(f"Created background task: {task.id} ({task.name})")
        return task
    
    def _execute_task(
        self,
        task: Task,
        func: Callable,
        *args,
        **kwargs
    ):
        """Execute task and update status"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 100.0
            task.completed_at = datetime.now()
            
            logger.info(f"Task completed: {task.id} ({task.name})")
            
        except Exception as e:
            # Handle error
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Task failed: {task.id} ({task.name}) - {e}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_active_tasks(self) -> List[Task]:
        """Get active (pending or running) tasks"""
        return [
            task for task in self.tasks.values()
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
        ]
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled, False otherwise
        """
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            logger.info(f"Task cancelled: {task_id}")
            return True
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        Remove old completed tasks
        
        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds() / 3600
                    if age > max_age_hours:
                        to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")
    
    def shutdown(self):
        """Shutdown task manager"""
        self.executor.shutdown(wait=True)
        logger.info("Background task manager shut down")


class AsyncDatabaseOperations:
    """Async database operation helpers"""
    
    @staticmethod
    async def execute_in_thread(func: Callable, *args, **kwargs) -> Any:
        """
        Execute blocking database operation in thread pool
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    @staticmethod
    async def bulk_insert(session, model, data: List[Dict[str, Any]]):
        """
        Bulk insert records asynchronously
        
        Args:
            session: Database session
            model: SQLAlchemy model
            data: List of record dictionaries
        """
        def _insert():
            objects = [model(**item) for item in data]
            session.bulk_save_objects(objects)
            session.commit()
        
        await AsyncDatabaseOperations.execute_in_thread(_insert)
    
    @staticmethod
    async def bulk_update(session, model, data: List[Dict[str, Any]]):
        """
        Bulk update records asynchronously
        
        Args:
            session: Database session
            model: SQLAlchemy model
            data: List of record dictionaries with 'id' field
        """
        def _update():
            session.bulk_update_mappings(model, data)
            session.commit()
        
        await AsyncDatabaseOperations.execute_in_thread(_update)


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total: int, task: Optional[Task] = None):
        self.total = total
        self.current = 0
        self.task = task
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        """
        Update progress
        
        Args:
            increment: Amount to increment
        """
        self.current += increment
        progress = (self.current / self.total) * 100 if self.total > 0 else 0
        
        if self.task:
            self.task.progress = progress
        
        # Log progress at intervals
        if self.current % max(1, self.total // 10) == 0:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0
            eta = (self.total - self.current) / rate if rate > 0 else 0
            
            logger.info(
                f"Progress: {self.current}/{self.total} ({progress:.1f}%) "
                f"- Rate: {rate:.1f}/s - ETA: {eta:.1f}s"
            )
    
    def complete(self):
        """Mark as complete"""
        self.current = self.total
        if self.task:
            self.task.progress = 100.0
        
        elapsed = time.time() - self.start_time
        logger.info(f"Completed in {elapsed:.2f}s")


class TaskQueue:
    """Simple task queue for sequential processing"""
    
    def __init__(self):
        self.queue: List[Task] = []
        self.processing = False
    
    def add_task(self, task: Task):
        """Add task to queue"""
        self.queue.append(task)
        logger.info(f"Added task to queue: {task.id} ({task.name})")
    
    async def process_queue(self, task_manager: BackgroundTaskManager):
        """
        Process all tasks in queue
        
        Args:
            task_manager: Background task manager
        """
        if self.processing:
            logger.warning("Queue is already being processed")
            return
        
        self.processing = True
        logger.info(f"Processing queue with {len(self.queue)} tasks")
        
        try:
            while self.queue:
                task = self.queue.pop(0)
                
                # Wait for task to complete
                while task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    await asyncio.sleep(0.1)
                
                logger.info(f"Task {task.id} finished with status: {task.status}")
        
        finally:
            self.processing = False
            logger.info("Queue processing complete")
    
    def get_queue_size(self) -> int:
        """Get number of tasks in queue"""
        return len(self.queue)
    
    def clear_queue(self):
        """Clear all tasks from queue"""
        self.queue.clear()
        logger.info("Queue cleared")


# Global task manager instance
_task_manager: Optional[BackgroundTaskManager] = None


def get_task_manager() -> BackgroundTaskManager:
    """Get global task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = BackgroundTaskManager()
    return _task_manager


def background_task(name: str = ""):
    """
    Decorator to run function as background task
    
    Args:
        name: Task name
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            manager = get_task_manager()
            return manager.create_task(func, *args, name=name, **kwargs)
        return wrapper
    return decorator
