"""
Tests für Theme Logging & Monitoring System
"""

import pytest
import time
from datetime import datetime
from pathlib import Path
import json
import tempfile
import shutil

try:
    from theming.theme_logger import ThemeLogger, LogEntry, get_theme_logger
except ImportError:
    pytest.skip("Theme-System nicht verfügbar", allow_module_level=True)


@pytest.fixture
def temp_log_dir():
    """Erstellt temporäres Log-Verzeichnis"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def logger(temp_log_dir):
    """Erstellt Logger-Instanz für Tests"""
    return ThemeLogger(log_level="DEBUG", log_dir=temp_log_dir)


class TestThemeLogger:
    """Tests für ThemeLogger-Klasse"""
    
    def test_initialization(self, logger, temp_log_dir):
        """Test: Logger-Initialisierung"""
        assert logger.log_level == "DEBUG"
        assert logger.log_dir == Path(temp_log_dir)
        assert logger.log_dir.exists()
        assert len(logger.log_entries) == 0
    
    def test_log_theme_switch(self, logger):
        """Test: Theme-Wechsel loggen"""
        logger.log_theme_switch(
            from_theme="default",
            to_theme="dark",
            user_id="user123",
            duration_ms=45.2
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_THEME_SWITCH
        assert entry.level == "INFO"
        assert entry.user_id == "user123"
        assert entry.metadata['from_theme'] == "default"
        assert entry.metadata['to_theme'] == "dark"
        assert entry.metadata['duration_ms'] == 45.2
        assert logger.stats['theme_switches'] == 1
    
    def test_log_css_generation(self, logger):
        """Test: CSS-Generierung loggen"""
        logger.log_css_generation(
            theme_name="dark",
            duration_ms=78.5,
            css_size_bytes=45000
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_PERFORMANCE
        assert entry.level == "DEBUG"
        assert entry.metadata['theme_name'] == "dark"
        assert entry.metadata['duration_ms'] == 78.5
        assert entry.metadata['css_size_bytes'] == 45000
        assert entry.metadata['css_size_kb'] == 45000 / 1024
    
    def test_log_css_injection_success(self, logger):
        """Test: Erfolgreiche CSS-Injection loggen"""
        logger.log_css_injection(
            theme_name="dark",
            success=True,
            duration_ms=12.3
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_CSS_INJECTION
        assert entry.level == "INFO"
        assert entry.metadata['success'] is True
        assert logger.stats['css_injections'] == 1
        assert logger.stats['errors'] == 0
    
    def test_log_css_injection_failure(self, logger):
        """Test: Fehlgeschlagene CSS-Injection loggen"""
        logger.log_css_injection(
            theme_name="dark",
            success=False,
            error="Injection failed"
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_CSS_INJECTION
        assert entry.level == "ERROR"
        assert entry.metadata['success'] is False
        assert entry.metadata['error'] == "Injection failed"
        assert logger.stats['errors'] == 1
    
    def test_log_component_render_success(self, logger):
        """Test: Erfolgreiches Komponenten-Rendering loggen"""
        logger.log_component_render(
            component_name="Card",
            duration_ms=23.4,
            success=True,
            user_id="user123"
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_COMPONENT_RENDER
        assert entry.level == "DEBUG"
        assert entry.metadata['component_name'] == "Card"
        assert entry.metadata['success'] is True
        assert logger.stats['component_renders'] == 1
    
    def test_log_component_render_failure(self, logger):
        """Test: Fehlgeschlagenes Komponenten-Rendering loggen"""
        logger.log_component_render(
            component_name="Card",
            duration_ms=15.0,
            success=False,
            error="Rendering failed"
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_COMPONENT_RENDER
        assert entry.level == "ERROR"
        assert entry.metadata['error'] == "Rendering failed"
        assert logger.stats['errors'] == 1
    
    def test_log_performance_metric(self, logger):
        """Test: Performance-Metrik loggen"""
        logger.log_performance_metric(
            metric_name="css_size",
            value=45.2,
            unit="KB",
            theme_name="dark",
            metadata={"compressed": True}
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_PERFORMANCE
        assert entry.metadata['metric_name'] == "css_size"
        assert entry.metadata['value'] == 45.2
        assert entry.metadata['unit'] == "KB"
        assert entry.metadata['theme_name'] == "dark"
        assert entry.metadata['compressed'] is True
    
    def test_log_cache_event_hit(self, logger):
        """Test: Cache-Hit loggen"""
        logger.log_cache_event(
            event_type="theme_cache",
            cache_key="dark",
            hit=True
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.category == logger.CATEGORY_CACHE
        assert entry.metadata['hit'] is True
        assert logger.stats['cache_hits'] == 1
        assert logger.stats['cache_misses'] == 0
    
    def test_log_cache_event_miss(self, logger):
        """Test: Cache-Miss loggen"""
        logger.log_cache_event(
            event_type="theme_cache",
            cache_key="custom",
            hit=False
        )
        
        assert logger.stats['cache_hits'] == 0
        assert logger.stats['cache_misses'] == 1
    
    def test_log_error(self, logger):
        """Test: Fehler loggen"""
        logger.log_error(
            error_message="Test error",
            category=logger.CATEGORY_ERROR,
            user_id="user123",
            metadata={"context": "test"}
        )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.level == "ERROR"
        assert entry.category == logger.CATEGORY_ERROR
        assert entry.message == "Test error"
        assert entry.user_id == "user123"
        assert logger.stats['errors'] == 1
    
    def test_log_error_with_exception(self, logger):
        """Test: Fehler mit Exception loggen"""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.log_error(
                error_message="Exception occurred",
                exception=e
            )
        
        assert len(logger.log_entries) == 1
        entry = logger.log_entries[0]
        
        assert entry.metadata['exception_type'] == "ValueError"
        assert entry.metadata['exception_message'] == "Test exception"
    
    def test_get_stats(self, logger):
        """Test: Statistiken abrufen"""
        # Füge verschiedene Events hinzu
        logger.log_theme_switch("default", "dark")
        logger.log_css_injection("dark", True)
        logger.log_component_render("Card", 20.0, True)
        logger.log_cache_event("theme_cache", "dark", True)
        logger.log_cache_event("theme_cache", "custom", False)
        logger.log_error("Test error")
        
        stats = logger.get_stats()
        
        assert stats['total_entries'] == 6
        assert stats['theme_switches'] == 1
        assert stats['css_injections'] == 1
        assert stats['component_renders'] == 1
        assert stats['errors'] == 1
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 1
        assert stats['cache_hit_rate'] == "50.0%"
    
    def test_get_recent_entries(self, logger):
        """Test: Letzte Einträge abrufen"""
        # Füge mehrere Einträge hinzu
        for i in range(10):
            logger.log_theme_switch(f"theme{i}", f"theme{i+1}")
        
        # Hole letzte 5 Einträge
        entries = logger.get_recent_entries(count=5)
        assert len(entries) == 5
        
        # Hole alle Einträge
        entries = logger.get_recent_entries(count=20)
        assert len(entries) == 10
    
    def test_get_recent_entries_filtered_by_category(self, logger):
        """Test: Gefilterte Einträge nach Kategorie"""
        logger.log_theme_switch("default", "dark")
        logger.log_css_injection("dark", True)
        logger.log_component_render("Card", 20.0, True)
        
        entries = logger.get_recent_entries(
            count=10,
            category=logger.CATEGORY_THEME_SWITCH
        )
        
        assert len(entries) == 1
        assert entries[0].category == logger.CATEGORY_THEME_SWITCH
    
    def test_get_recent_entries_filtered_by_level(self, logger):
        """Test: Gefilterte Einträge nach Level"""
        logger.log_theme_switch("default", "dark")  # INFO
        logger.log_error("Test error")  # ERROR
        logger.log_component_render("Card", 20.0, True)  # DEBUG
        
        entries = logger.get_recent_entries(count=10, level="ERROR")
        
        assert len(entries) == 1
        assert entries[0].level == "ERROR"
    
    def test_export_logs_json(self, logger, temp_log_dir):
        """Test: Logs als JSON exportieren"""
        logger.log_theme_switch("default", "dark")
        logger.log_css_injection("dark", True)
        
        filepath = logger.export_logs(format="json")
        
        assert Path(filepath).exists()
        assert filepath.endswith(".json")
        
        # Prüfe Inhalt
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]['category'] == logger.CATEGORY_THEME_SWITCH
        assert data[1]['category'] == logger.CATEGORY_CSS_INJECTION
    
    def test_export_logs_csv(self, logger, temp_log_dir):
        """Test: Logs als CSV exportieren"""
        logger.log_theme_switch("default", "dark")
        
        filepath = logger.export_logs(format="csv")
        
        assert Path(filepath).exists()
        assert filepath.endswith(".csv")
        
        # Prüfe Inhalt
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "timestamp" in content
        assert "level" in content
        assert "category" in content
    
    def test_clear_logs(self, logger):
        """Test: Logs löschen"""
        logger.log_theme_switch("default", "dark")
        logger.log_css_injection("dark", True)
        
        assert len(logger.log_entries) == 2
        
        logger.clear_logs()
        
        assert len(logger.log_entries) == 0
    
    def test_set_log_level(self, logger):
        """Test: Log-Level setzen"""
        assert logger.log_level == "DEBUG"
        
        logger.set_log_level("WARNING")
        
        assert logger.log_level == "WARNING"
    
    def test_log_entry_to_dict(self):
        """Test: LogEntry zu Dictionary konvertieren"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            category="test",
            message="Test message",
            user_id="user123",
            metadata={"key": "value"}
        )
        
        data = entry.to_dict()
        
        assert data['level'] == "INFO"
        assert data['category'] == "test"
        assert data['message'] == "Test message"
        assert data['user_id'] == "user123"
        assert data['metadata']['key'] == "value"
        assert 'timestamp' in data


class TestGetThemeLogger:
    """Tests für get_theme_logger Singleton-Funktion"""
    
    def test_singleton_pattern(self):
        """Test: Singleton-Pattern"""
        logger1 = get_theme_logger()
        logger2 = get_theme_logger()
        
        assert logger1 is logger2


class TestIntegration:
    """Integrationstests"""
    
    def test_complete_workflow(self, logger):
        """Test: Vollständiger Workflow"""
        # Theme-Wechsel
        logger.log_theme_switch("default", "dark", user_id="user123", duration_ms=45.0)
        
        # CSS-Generierung und Injection
        logger.log_css_generation("dark", 78.5, 45000)
        logger.log_css_injection("dark", True, 12.3)
        
        # Komponenten rendern
        logger.log_component_render("Card", 23.4, True)
        logger.log_component_render("Alert", 18.2, True)
        
        # Cache-Events
        logger.log_cache_event("theme_cache", "dark", True)
        logger.log_cache_event("css_cache", "dark", True)
        
        # Performance-Metriken
        logger.log_performance_metric("render_time", 100.5, "ms")
        
        # Statistiken prüfen
        stats = logger.get_stats()
        assert stats['total_entries'] == 8
        assert stats['theme_switches'] == 1
        assert stats['css_injections'] == 1
        assert stats['component_renders'] == 2
        assert stats['cache_hits'] == 2
        
        # Export
        json_file = logger.export_logs(format="json")
        assert Path(json_file).exists()
        
        csv_file = logger.export_logs(format="csv")
        assert Path(csv_file).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
