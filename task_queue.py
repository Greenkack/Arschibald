"""task_queue.py - Task Queue System"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

class TaskQueue:
    """Persistente Task Queue mit SQLite"""
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialisiere Queue-Tabelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                task_data TEXT,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_status ON task_queue(status, priority DESC)
        """)
        conn.commit()
        conn.close()
    
    def enqueue(self, task_type: str, task_data: str, priority: int = 0) -> int:
        """Füge Task zur Queue hinzu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO task_queue (task_type, task_data, priority) VALUES (?, ?, ?)",
            (task_type, task_data, priority)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Hole nächsten Task aus Queue"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Hole Task mit höchster Priorität
        cursor.execute("""
            SELECT * FROM task_queue 
            WHERE status = 'pending' 
            ORDER BY priority DESC, id ASC 
            LIMIT 1
        """)
        task = cursor.fetchone()
        
        if task:
            # Markiere als "processing"
            cursor.execute(
                "UPDATE task_queue SET status = 'processing', started_at = ? WHERE id = ?",
                (datetime.now(), task['id'])
            )
            conn.commit()
        
        conn.close()
        return dict(task) if task else None
    
    def complete_task(self, task_id: int, error: Optional[str] = None):
        """Markiere Task als abgeschlossen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if error:
            cursor.execute(
                "UPDATE task_queue SET status = 'failed', completed_at = ?, error_message = ? WHERE id = ?",
                (datetime.now(), error, task_id)
            )
        else:
            cursor.execute(
                "UPDATE task_queue SET status = 'completed', completed_at = ? WHERE id = ?",
                (datetime.now(), task_id)
            )
        
        conn.commit()
        conn.close()
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Hole Queue-Statistiken"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT status, COUNT(*) as count FROM task_queue GROUP BY status")
        stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return stats
    
    def clear_completed(self, older_than_days: int = 7):
        """Lösche alte abgeschlossene Tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM task_queue WHERE status IN ('completed', 'failed') AND completed_at < datetime('now', '-' || ? || ' days')",
            (older_than_days,)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
