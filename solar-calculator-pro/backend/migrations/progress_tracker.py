"""
Migration Progress Tracker
Real-time progress tracking for long-running migrations.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class ProgressState:
    """Current progress state"""
    total_steps: int
    completed_steps: int
    current_step: str
    current_step_progress: float  # 0.0 to 1.0
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, paused
    
    @property
    def overall_progress(self) -> float:
        """Calculate overall progress (0.0 to 1.0)"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps + self.current_step_progress) / self.total_steps
    
    @property
    def percentage(self) -> float:
        """Get progress as percentage"""
        return self.overall_progress * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Get elapsed time"""
        return datetime.now() - self.started_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['overall_progress'] = self.overall_progress
        result['percentage'] = self.percentage
        result['elapsed_time'] = str(self.elapsed_time)
        result['started_at'] = self.started_at.isoformat()
        if self.estimated_completion:
            result['estimated_completion'] = self.estimated_completion.isoformat()
        return result


class ProgressTracker:
    """
    Progress tracker for migrations
    
    Features:
    - Real-time progress updates
    - Time estimation
    - Step tracking
    - Callback notifications
    - Thread-safe operations
    """
    
    def __init__(self, total_steps: int):
        """
        Initialize progress tracker
        
        Args:
            total_steps: Total number of steps in migration
        """
        self.state = ProgressState(
            total_steps=total_steps,
            completed_steps=0,
            current_step="Initializing",
            current_step_progress=0.0,
            started_at=datetime.now()
        )
        
        self.callbacks: list[Callable[[ProgressState], None]] = []
        self.lock = threading.Lock()
        
        # Performance tracking
        self.step_times: list[float] = []
        self.last_update = datetime.now()
    
    def add_callback(self, callback: Callable[[ProgressState], None]):
        """
        Add progress callback
        
        Args:
            callback: Function to call on progress update
        """
        self.callbacks.append(callback)
    
    def start_step(self, step_name: str):
        """
        Start a new step
        
        Args:
            step_name: Name of the step
        """
        with self.lock:
            self.state.current_step = step_name
            self.state.current_step_progress = 0.0
            self.last_update = datetime.now()
            
            logger.info(f"Starting step: {step_name} ({self.state.completed_steps + 1}/{self.state.total_steps})")
            
            self._notify_callbacks()
    
    def update_step_progress(self, progress: float):
        """
        Update current step progress
        
        Args:
            progress: Progress value (0.0 to 1.0)
        """
        with self.lock:
            self.state.current_step_progress = max(0.0, min(1.0, progress))
            self._update_time_estimate()
            self._notify_callbacks()
    
    def complete_step(self):
        """Mark current step as complete"""
        with self.lock:
            # Record step time
            step_time = (datetime.now() - self.last_update).total_seconds()
            self.step_times.append(step_time)
            
            self.state.completed_steps += 1
            self.state.current_step_progress = 1.0
            
            logger.info(f"Completed step: {self.state.current_step} (took {step_time:.2f}s)")
            
            # Check if all steps complete
            if self.state.completed_steps >= self.state.total_steps:
                self.state.status = "completed"
                self.state.estimated_completion = datetime.now()
                logger.info("All migration steps completed")
            
            self._notify_callbacks()
    
    def fail_step(self, error_message: str):
        """
        Mark current step as failed
        
        Args:
            error_message: Error description
        """
        with self.lock:
            self.state.status = "failed"
            logger.error(f"Step failed: {self.state.current_step} - {error_message}")
            self._notify_callbacks()
    
    def pause(self):
        """Pause migration"""
        with self.lock:
            self.state.status = "paused"
            logger.info("Migration paused")
            self._notify_callbacks()
    
    def resume(self):
        """Resume migration"""
        with self.lock:
            self.state.status = "running"
            logger.info("Migration resumed")
            self._notify_callbacks()
    
    def _update_time_estimate(self):
        """Update estimated completion time"""
        if not self.step_times:
            return
        
        # Calculate average step time
        avg_step_time = sum(self.step_times) / len(self.step_times)
        
        # Estimate remaining time
        remaining_steps = self.state.total_steps - self.state.completed_steps - self.state.current_step_progress
        estimated_seconds = remaining_steps * avg_step_time
        
        self.state.estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
    
    def _notify_callbacks(self):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(self.state)
            except Exception as e:
                logger.error(f"Callback error: {str(e)}")
    
    def get_state(self) -> ProgressState:
        """Get current progress state"""
        with self.lock:
            return self.state
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        with self.lock:
            return {
                'progress': self.state.to_dict(),
                'performance': {
                    'average_step_time': sum(self.step_times) / len(self.step_times) if self.step_times else 0,
                    'fastest_step': min(self.step_times) if self.step_times else 0,
                    'slowest_step': max(self.step_times) if self.step_times else 0,
                    'total_steps_completed': len(self.step_times)
                }
            }


class ProgressLogger:
    """Log progress to console with formatting"""
    
    def __init__(self, tracker: ProgressTracker):
        """
        Initialize progress logger
        
        Args:
            tracker: Progress tracker to monitor
        """
        self.tracker = tracker
        self.tracker.add_callback(self.log_progress)
        self.last_log_time = datetime.now()
        self.log_interval = 1.0  # Log every second
    
    def log_progress(self, state: ProgressState):
        """
        Log progress update
        
        Args:
            state: Current progress state
        """
        # Throttle logging
        now = datetime.now()
        if (now - self.last_log_time).total_seconds() < self.log_interval:
            return
        
        self.last_log_time = now
        
        # Format progress bar
        bar_length = 40
        filled_length = int(bar_length * state.overall_progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Format time estimate
        time_str = ""
        if state.estimated_completion:
            remaining = state.estimated_completion - now
            time_str = f" | ETA: {self._format_timedelta(remaining)}"
        
        # Log formatted progress
        logger.info(
            f"[{bar}] {state.percentage:.1f}% | "
            f"Step {state.completed_steps + 1}/{state.total_steps}: {state.current_step}"
            f"{time_str}"
        )
    
    @staticmethod
    def _format_timedelta(td: timedelta) -> str:
        """Format timedelta as human-readable string"""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class ProgressWebSocket:
    """Send progress updates via WebSocket"""
    
    def __init__(self, tracker: ProgressTracker, websocket_manager):
        """
        Initialize WebSocket progress sender
        
        Args:
            tracker: Progress tracker to monitor
            websocket_manager: WebSocket manager instance
        """
        self.tracker = tracker
        self.websocket_manager = websocket_manager
        self.tracker.add_callback(self.send_progress)
    
    def send_progress(self, state: ProgressState):
        """
        Send progress update via WebSocket
        
        Args:
            state: Current progress state
        """
        try:
            self.websocket_manager.broadcast({
                'type': 'migration_progress',
                'data': state.to_dict()
            })
        except Exception as e:
            logger.error(f"WebSocket send error: {str(e)}")


class ProgressFile:
    """Write progress to file for monitoring"""
    
    def __init__(self, tracker: ProgressTracker, file_path: str):
        """
        Initialize file progress writer
        
        Args:
            tracker: Progress tracker to monitor
            file_path: Path to progress file
        """
        self.tracker = tracker
        self.file_path = file_path
        self.tracker.add_callback(self.write_progress)
    
    def write_progress(self, state: ProgressState):
        """
        Write progress to file
        
        Args:
            state: Current progress state
        """
        import json
        
        try:
            with open(self.file_path, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"File write error: {str(e)}")
