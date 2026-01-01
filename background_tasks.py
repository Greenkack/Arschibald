"""background_tasks.py - Background Task Management"""
import threading
import queue
import logging
from typing import Callable, Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Background Task"""
    task_id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = datetime.now()

class BackgroundTaskManager:
    """Manager für Background Tasks"""
    
    def __init__(self, num_workers: int = 4):
        self.task_queue = queue.PriorityQueue()
        self.results = {}
        self.workers = []
        self.num_workers = num_workers
        self.running = False
    
    def start(self):
        """Starte Worker-Threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"Worker-{i}")
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Background Task Manager gestartet mit {self.num_workers} Workers")
    
    def stop(self):
        """Stoppe Worker-Threads"""
        self.running = False
        # Signal Workers to stop
        for _ in range(self.num_workers):
            self.task_queue.put((float('inf'), None))
        
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers = []
        logger.info("Background Task Manager gestoppt")
    
    def _worker(self):
        """Worker-Thread-Funktion"""
        while self.running:
            try:
                priority, task = self.task_queue.get(timeout=1)
                
                if task is None:  # Stop signal
                    break
                
                try:
                    logger.info(f"Führe Task '{task.task_id}' aus")
                    result = task.func(*task.args, **task.kwargs)
                    self.results[task.task_id] = {
                        'status': 'completed',
                        'result': result,
                        'completed_at': datetime.now()
                    }
                    logger.info(f"Task '{task.task_id}' erfolgreich")
                except Exception as e:
                    logger.error(f"Task '{task.task_id}' fehlgeschlagen: {e}")
                    self.results[task.task_id] = {
                        'status': 'failed',
                        'error': str(e),
                        'completed_at': datetime.now()
                    }
                finally:
                    self.task_queue.task_done()
            
            except queue.Empty:
                continue
    
    def submit_task(self, task_id: str, func: Callable, *args, priority: int = 0, **kwargs):
        """Reiche Task ein"""
        task = Task(task_id, func, args, kwargs, priority)
        self.task_queue.put((priority, task))
        logger.info(f"Task '{task_id}' eingereicht (Priorität: {priority})")
        return task_id
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Hole Task-Ergebnis"""
        return self.results.get(task_id)
    
    def get_queue_size(self) -> int:
        """Hole Anzahl wartender Tasks"""
        return self.task_queue.qsize()
    
    def clear_results(self):
        """Lösche alle Ergebnisse"""
        self.results = {}

# Globale Task-Manager-Instanz
_task_manager = None

def get_task_manager() -> BackgroundTaskManager:
    """Hole oder erstelle Task-Manager-Instanz"""
    global _task_manager
    if _task_manager is None:
        _task_manager = BackgroundTaskManager()
        _task_manager.start()
    return _task_manager
