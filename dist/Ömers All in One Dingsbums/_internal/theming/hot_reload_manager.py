"""
Hot Reload Manager

Überwacht Theme-Dateien auf Änderungen und lädt sie automatisch neu.
Für Theme-Entwicklung im Development-Mode.
"""

import time
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class ThemeFileHandler(FileSystemEventHandler):
    """Handler für Theme-Datei-Änderungen mit Debouncing"""
    
    def __init__(
        self,
        theme_manager,
        callback: Callable[[str], None],
        debounce_seconds: float = 1.0
    ):
        """
        Initialisiert ThemeFileHandler
        
        Args:
            theme_manager: ThemeManager-Instanz
            callback: Callback-Funktion die bei Theme-Änderung aufgerufen wird
            debounce_seconds: Debounce-Zeit in Sekunden (Standard: 1.0)
        """
        super().__init__()
        self.theme_manager = theme_manager
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.last_modified: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event):
        """
        Wird aufgerufen wenn eine Datei geändert wird
        
        Args:
            event: FileSystemEvent mit Informationen zur Änderung
        """
        # Ignoriere Verzeichnis-Events
        if event.is_directory:
            return
        
        # Nur JSON-Dateien verarbeiten
        if not event.src_path.endswith('.json'):
            return
        
        # Debouncing: Ignoriere mehrfache Events innerhalb der Debounce-Zeit
        now = time.time()
        if event.src_path in self.last_modified:
            time_since_last = now - self.last_modified[event.src_path]
            if time_since_last < self.debounce_seconds:
                self.logger.debug(
                    f"Debounced: {event.src_path} "
                    f"(last modified {time_since_last:.2f}s ago)"
                )
                return
        
        self.last_modified[event.src_path] = now
        
        # Extrahiere Theme-Namen aus Dateiname
        theme_name = Path(event.src_path).stem
        
        self.logger.info(f"Theme file modified: {theme_name}")
        
        # Lade Theme neu
        try:
            success = self.theme_manager.reload_theme(theme_name)
            
            if success:
                self.logger.info(f"Successfully reloaded theme: {theme_name}")
                
                # Rufe Callback auf
                self.callback(theme_name)
                
                # Zeige Benachrichtigung in Streamlit (falls verfügbar)
                if STREAMLIT_AVAILABLE:
                    try:
                        st.toast(
                            f" Theme '{theme_name}' neu geladen"
                        )
                    except Exception:
                        # Streamlit context nicht verfügbar
                        pass
            else:
                self.logger.error(f"Failed to reload theme: {theme_name}")
                
                if STREAMLIT_AVAILABLE:
                    try:
                        st.error(
                            f" Fehler beim Laden von Theme '{theme_name}'. "
                            "Siehe Logs für Details."
                        )
                    except Exception:
                        pass
                        
        except Exception as e:
            self.logger.error(
                f"Error reloading theme '{theme_name}': {e}",
                exc_info=True
            )
            
            if STREAMLIT_AVAILABLE:
                try:
                    st.error(f" Fehler beim Laden von '{theme_name}': {e}")
                except Exception:
                    pass


class HotReloadManager:
    """Verwaltet Hot Reload für Theme-Dateien"""
    
    def __init__(
        self,
        theme_manager,
        watch_dir: Optional[str] = None,
        debounce_seconds: float = 1.0
    ):
        """
        Initialisiert HotReloadManager
        
        Args:
            theme_manager: ThemeManager-Instanz
            watch_dir: Verzeichnis das überwacht werden soll (optional)
            debounce_seconds: Debounce-Zeit für File-Events (Standard: 1.0)
        """
        self.theme_manager = theme_manager
        
        if watch_dir is None:
            # Standard: themes/ Verzeichnis des ThemeManagers
            watch_dir = str(theme_manager.themes_dir)
        
        self.watch_dir = Path(watch_dir)
        self.debounce_seconds = debounce_seconds
        self.observer: Optional[Observer] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Statistiken
        self.stats = {
            'started_at': None,
            'reloads': 0,
            'errors': 0,
            'last_reload': None
        }
    
    def start(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Startet File Watcher
        
        Args:
            callback: Optional callback function die bei Theme-Änderung aufgerufen wird.
                     Erhält Theme-Namen als Parameter.
        """
        if self.is_running:
            self.logger.warning("Hot reload is already running")
            return
        
        if not self.watch_dir.exists():
            raise FileNotFoundError(
                f"Watch directory does not exist: {self.watch_dir}"
            )
        
        # Default callback: Nur loggen
        if callback is None:
            def default_callback(theme_name: str):
                self.stats['reloads'] += 1
                self.stats['last_reload'] = datetime.now()
                self.logger.info(f"Theme reloaded: {theme_name}")
            
            callback = default_callback
        else:
            # Wrap callback um Statistiken zu aktualisieren
            original_callback = callback
            def wrapped_callback(theme_name: str):
                self.stats['reloads'] += 1
                self.stats['last_reload'] = datetime.now()
                original_callback(theme_name)
            
            callback = wrapped_callback
        
        # Erstelle Event Handler
        event_handler = ThemeFileHandler(
            self.theme_manager,
            callback,
            self.debounce_seconds
        )
        
        # Erstelle und starte Observer
        self.observer = Observer()
        self.observer.schedule(
            event_handler,
            str(self.watch_dir),
            recursive=False
        )
        self.observer.start()
        
        self.is_running = True
        self.stats['started_at'] = datetime.now()
        
        self.logger.info(
            f"Hot reload started. Watching: {self.watch_dir} "
            f"(debounce: {self.debounce_seconds}s)"
        )
    
    def stop(self) -> None:
        """Stoppt File Watcher"""
        if not self.is_running:
            self.logger.warning("Hot reload is not running")
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.observer = None
        
        self.is_running = False
        self.logger.info("Hot reload stopped")
    
    def restart(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Startet Hot Reload neu
        
        Args:
            callback: Optional callback function
        """
        self.stop()
        time.sleep(0.5)  # Kurze Pause
        self.start(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        stats = self.stats.copy()
        
        # Berechne Uptime
        if stats['started_at']:
            uptime = datetime.now() - stats['started_at']
            stats['uptime_seconds'] = uptime.total_seconds()
            stats['uptime_formatted'] = str(uptime).split('.')[0]  # Ohne Mikrosekunden
        else:
            stats['uptime_seconds'] = 0
            stats['uptime_formatted'] = '0:00:00'
        
        # Formatiere Timestamps
        if stats['started_at']:
            stats['started_at'] = stats['started_at'].isoformat()
        if stats['last_reload']:
            stats['last_reload'] = stats['last_reload'].isoformat()
        
        stats['is_running'] = self.is_running
        stats['watch_dir'] = str(self.watch_dir)
        stats['debounce_seconds'] = self.debounce_seconds
        
        return stats
    
    def __enter__(self):
        """Context manager support"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.stop()
        return False


def create_hot_reload_manager(
    theme_manager,
    enabled: bool = True,
    debounce_seconds: float = 1.0
) -> Optional[HotReloadManager]:
    """
    Factory function zum Erstellen eines HotReloadManagers
    
    Args:
        theme_manager: ThemeManager-Instanz
        enabled: Ob Hot Reload aktiviert sein soll (Standard: True)
        debounce_seconds: Debounce-Zeit für File-Events (Standard: 1.0)
    
    Returns:
        HotReloadManager-Instanz oder None wenn deaktiviert
    """
    if not enabled:
        return None
    
    manager = HotReloadManager(
        theme_manager,
        debounce_seconds=debounce_seconds
    )
    
    return manager
