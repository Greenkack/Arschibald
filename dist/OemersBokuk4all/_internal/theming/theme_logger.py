"""
Theme Logger - Spezialisiertes Logging-System für Theme-System

Dieses Modul implementiert ein umfassendes Logging-System für das shadcn/ui Theme-System.
Es loggt Theme-Wechsel, CSS-Injection, Komponenten-Rendering und Performance-Metriken.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import json


@dataclass
class LogEntry:
    """Repräsentiert einen Log-Eintrag"""
    timestamp: datetime
    level: str
    category: str
    message: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'category': self.category,
            'message': self.message,
            'user_id': self.user_id,
            'metadata': self.metadata
        }


class ThemeLogger:
    """Spezialisierter Logger für Theme-System"""
    
    # Log-Kategorien
    CATEGORY_THEME_SWITCH = "theme_switch"
    CATEGORY_CSS_INJECTION = "css_injection"
    CATEGORY_COMPONENT_RENDER = "component_render"
    CATEGORY_PERFORMANCE = "performance"
    CATEGORY_ERROR = "error"
    CATEGORY_CACHE = "cache"
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        """
        Initialisiert den Theme Logger
        
        Args:
            log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Verzeichnis für Log-Dateien
        """
        self.log_level = log_level
        self.log_dir = Path(log_dir)
        self.log_entries: List[LogEntry] = []
        
        # Erstelle Log-Verzeichnis
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialisiere Logger
        self.logger = logging.getLogger("shadcn_theme")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Entferne existierende Handler
        self.logger.handlers.clear()
        
        # File Handler
        log_file = self.log_dir / "theme_system.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        # Statistiken
        self.stats = {
            'theme_switches': 0,
            'css_injections': 0,
            'component_renders': 0,
            'errors': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.logger.info("Theme Logger initialized")
    
    def log_theme_switch(
        self,
        from_theme: str,
        to_theme: str,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """
        Loggt Theme-Wechsel
        
        Args:
            from_theme: Vorheriges Theme
            to_theme: Neues Theme
            user_id: Benutzer-ID (optional)
            duration_ms: Dauer des Wechsels in Millisekunden (optional)
        """
        metadata = {
            'from_theme': from_theme,
            'to_theme': to_theme
        }
        if duration_ms is not None:
            metadata['duration_ms'] = duration_ms
        
        message = f"Theme switch: {from_theme} -> {to_theme}"
        if user_id:
            message += f" (user: {user_id})"
        if duration_ms is not None:
            message += f" [{duration_ms:.2f}ms]"
        
        self.logger.info(message)
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level='INFO',
            category=self.CATEGORY_THEME_SWITCH,
            message=message,
            user_id=user_id,
            metadata=metadata
        )
        self.log_entries.append(entry)
        self.stats['theme_switches'] += 1
    
    def log_css_generation(
        self,
        theme_name: str,
        duration_ms: float,
        css_size_bytes: Optional[int] = None
    ) -> None:
        """
        Loggt CSS-Generierung
        
        Args:
            theme_name: Name des Themes
            duration_ms: Dauer der Generierung in Millisekunden
            css_size_bytes: Größe des generierten CSS in Bytes (optional)
        """
        metadata = {
            'theme_name': theme_name,
            'duration_ms': duration_ms
        }
        if css_size_bytes is not None:
            metadata['css_size_bytes'] = css_size_bytes
            metadata['css_size_kb'] = css_size_bytes / 1024
        
        message = f"CSS generated for '{theme_name}' in {duration_ms:.2f}ms"
        if css_size_bytes is not None:
            message += f" ({css_size_bytes / 1024:.2f}KB)"
        
        self.logger.debug(message)
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level='DEBUG',
            category=self.CATEGORY_PERFORMANCE,
            message=message,
            metadata=metadata
        )
        self.log_entries.append(entry)
    
    def log_css_injection(
        self,
        theme_name: str,
        success: bool,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Loggt CSS-Injection-Ereignisse
        
        Args:
            theme_name: Name des Themes
            success: Ob Injection erfolgreich war
            duration_ms: Dauer der Injection in Millisekunden (optional)
            error: Fehlermeldung falls nicht erfolgreich (optional)
        """
        metadata = {
            'theme_name': theme_name,
            'success': success
        }
        if duration_ms is not None:
            metadata['duration_ms'] = duration_ms
        if error:
            metadata['error'] = error
        
        if success:
            message = f"CSS injected for '{theme_name}'"
            if duration_ms is not None:
                message += f" in {duration_ms:.2f}ms"
            self.logger.info(message)
            level = 'INFO'
        else:
            message = f"CSS injection failed for '{theme_name}'"
            if error:
                message += f": {error}"
            self.logger.error(message)
            level = 'ERROR'
            self.stats['errors'] += 1
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=self.CATEGORY_CSS_INJECTION,
            message=message,
            metadata=metadata
        )
        self.log_entries.append(entry)
        self.stats['css_injections'] += 1
    
    def log_component_render(
        self,
        component_name: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Loggt Komponenten-Rendering
        
        Args:
            component_name: Name der Komponente
            duration_ms: Dauer des Renderings in Millisekunden
            success: Ob Rendering erfolgreich war
            error: Fehlermeldung falls nicht erfolgreich (optional)
            user_id: Benutzer-ID (optional)
        """
        metadata = {
            'component_name': component_name,
            'duration_ms': duration_ms,
            'success': success
        }
        if error:
            metadata['error'] = error
        
        if success:
            message = f"Component '{component_name}' rendered in {duration_ms:.2f}ms"
            self.logger.debug(message)
            level = 'DEBUG'
        else:
            message = f"Component '{component_name}' failed to render"
            if error:
                message += f": {error}"
            self.logger.error(message)
            level = 'ERROR'
            self.stats['errors'] += 1
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=self.CATEGORY_COMPONENT_RENDER,
            message=message,
            user_id=user_id,
            metadata=metadata
        )
        self.log_entries.append(entry)
        self.stats['component_renders'] += 1
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        theme_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Loggt Performance-Metriken
        
        Args:
            metric_name: Name der Metrik
            value: Wert der Metrik
            unit: Einheit (z.B. "ms", "bytes", "count")
            theme_name: Name des Themes (optional)
            metadata: Zusätzliche Metadaten (optional)
        """
        meta = metadata or {}
        meta.update({
            'metric_name': metric_name,
            'value': value,
            'unit': unit
        })
        if theme_name:
            meta['theme_name'] = theme_name
        
        message = f"Performance: {metric_name} = {value}{unit}"
        if theme_name:
            message += f" (theme: {theme_name})"
        
        self.logger.debug(message)
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level='DEBUG',
            category=self.CATEGORY_PERFORMANCE,
            message=message,
            metadata=meta
        )
        self.log_entries.append(entry)
    
    def log_cache_event(
        self,
        event_type: str,
        cache_key: str,
        hit: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Loggt Cache-Ereignisse
        
        Args:
            event_type: Typ des Events (z.B. "theme_cache", "css_cache")
            cache_key: Cache-Schlüssel
            hit: Ob Cache-Hit oder Miss
            metadata: Zusätzliche Metadaten (optional)
        """
        meta = metadata or {}
        meta.update({
            'event_type': event_type,
            'cache_key': cache_key,
            'hit': hit
        })
        
        status = "HIT" if hit else "MISS"
        message = f"Cache {status}: {event_type} - {cache_key}"
        
        self.logger.debug(message)
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level='DEBUG',
            category=self.CATEGORY_CACHE,
            message=message,
            metadata=meta
        )
        self.log_entries.append(entry)
        
        if hit:
            self.stats['cache_hits'] += 1
        else:
            self.stats['cache_misses'] += 1
    
    def log_error(
        self,
        error_message: str,
        exception: Optional[Exception] = None,
        category: str = CATEGORY_ERROR,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Loggt Fehler
        
        Args:
            error_message: Fehlermeldung
            exception: Exception-Objekt (optional)
            category: Fehler-Kategorie
            user_id: Benutzer-ID (optional)
            metadata: Zusätzliche Metadaten (optional)
        """
        meta = metadata or {}
        
        if exception:
            meta['exception_type'] = type(exception).__name__
            meta['exception_message'] = str(exception)
            self.logger.error(error_message, exc_info=True)
        else:
            self.logger.error(error_message)
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level='ERROR',
            category=category,
            message=error_message,
            user_id=user_id,
            metadata=meta
        )
        self.log_entries.append(entry)
        self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt Logging-Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        total_cache = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = (
            (self.stats['cache_hits'] / total_cache * 100)
            if total_cache > 0 else 0
        )
        
        return {
            'total_entries': len(self.log_entries),
            'theme_switches': self.stats['theme_switches'],
            'css_injections': self.stats['css_injections'],
            'component_renders': self.stats['component_renders'],
            'errors': self.stats['errors'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.1f}%"
        }
    
    def get_recent_entries(
        self,
        count: int = 50,
        category: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[LogEntry]:
        """
        Gibt die letzten Log-Einträge zurück
        
        Args:
            count: Anzahl der Einträge
            category: Filter nach Kategorie (optional)
            level: Filter nach Level (optional)
        
        Returns:
            Liste von Log-Einträgen
        """
        entries = self.log_entries
        
        if category:
            entries = [e for e in entries if e.category == category]
        
        if level:
            entries = [e for e in entries if e.level == level]
        
        return entries[-count:]
    
    def export_logs(
        self,
        filepath: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """
        Exportiert Logs in Datei
        
        Args:
            filepath: Pfad zur Ausgabedatei (optional)
            format: Format ("json" oder "csv")
        
        Returns:
            Pfad zur exportierten Datei
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = str(self.log_dir / f"theme_logs_{timestamp}.{format}")
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                data = [entry.to_dict() for entry in self.log_entries]
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.log_entries:
                    fieldnames = ['timestamp', 'level', 'category', 'message', 'user_id']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for entry in self.log_entries:
                        writer.writerow({
                            'timestamp': entry.timestamp.isoformat(),
                            'level': entry.level,
                            'category': entry.category,
                            'message': entry.message,
                            'user_id': entry.user_id or ''
                        })
        
        self.logger.info(f"Logs exported to {filepath}")
        return filepath
    
    def clear_logs(self) -> None:
        """Löscht alle Log-Einträge aus dem Speicher"""
        self.log_entries.clear()
        self.logger.info("Log entries cleared")
    
    def set_log_level(self, level: str) -> None:
        """
        Setzt das Log-Level
        
        Args:
            level: Neues Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level
        self.logger.setLevel(getattr(logging, level))
        self.logger.info(f"Log level set to {level}")


# Singleton-Instanz
_theme_logger_instance: Optional[ThemeLogger] = None


def get_theme_logger(
    log_level: str = "INFO",
    log_dir: str = "logs"
) -> ThemeLogger:
    """
    Gibt Singleton-Instanz des Theme Loggers zurück
    
    Args:
        log_level: Log-Level (nur beim ersten Aufruf verwendet)
        log_dir: Log-Verzeichnis (nur beim ersten Aufruf verwendet)
    
    Returns:
        ThemeLogger-Instanz
    """
    global _theme_logger_instance
    
    if _theme_logger_instance is None:
        _theme_logger_instance = ThemeLogger(log_level, log_dir)
    
    return _theme_logger_instance
