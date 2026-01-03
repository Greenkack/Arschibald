"""
Tests für Hot Reload System

Testet ThemeFileHandler, HotReloadManager und Dev Mode.
"""

import pytest
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from theming.hot_reload_manager import (
    ThemeFileHandler,
    HotReloadManager,
    create_hot_reload_manager
)
from theming.dev_mode import (
    DevModeConfig,
    get_dev_mode_config,
    is_dev_mode,
    enable_dev_mode,
    disable_dev_mode
)
from theming.theme_manager import ThemeManager


class TestThemeFileHandler:
    """Tests für ThemeFileHandler"""
    
    def test_init(self):
        """Test: Initialisierung"""
        theme_manager = Mock()
        callback = Mock()
        
        handler = ThemeFileHandler(
            theme_manager,
            callback,
            debounce_seconds=0.5
        )
        
        assert handler.theme_manager == theme_manager
        assert handler.callback == callback
        assert handler.debounce_seconds == 0.5
        assert handler.last_modified == {}
    
    def test_on_modified_json_file(self, tmp_path):
        """Test: JSON-Datei wurde geändert"""
        theme_manager = Mock()
        theme_manager.reload_theme.return_value = True
        
        callback = Mock()
        
        handler = ThemeFileHandler(
            theme_manager,
            callback,
            debounce_seconds=0.1
        )
        
        # Erstelle Mock Event
        event = Mock()
        event.is_directory = False
        event.src_path = str(tmp_path / "test-theme.json")
        
        # Trigger Event
        handler.on_modified(event)
        
        # Assertions
        theme_manager.reload_theme.assert_called_once_with("test-theme")
        callback.assert_called_once_with("test-theme")
    
    def test_on_modified_non_json_file(self, tmp_path):
        """Test: Nicht-JSON-Datei wird ignoriert"""
        theme_manager = Mock()
        callback = Mock()
        
        handler = ThemeFileHandler(theme_manager, callback)
        
        # Erstelle Mock Event für .txt Datei
        event = Mock()
        event.is_directory = False
        event.src_path = str(tmp_path / "test.txt")
        
        # Trigger Event
        handler.on_modified(event)
        
        # Assertions: Nichts sollte passieren
        theme_manager.reload_theme.assert_not_called()
        callback.assert_not_called()
    
    def test_on_modified_directory(self, tmp_path):
        """Test: Verzeichnis-Events werden ignoriert"""
        theme_manager = Mock()
        callback = Mock()
        
        handler = ThemeFileHandler(theme_manager, callback)
        
        # Erstelle Mock Event für Verzeichnis
        event = Mock()
        event.is_directory = True
        event.src_path = str(tmp_path)
        
        # Trigger Event
        handler.on_modified(event)
        
        # Assertions: Nichts sollte passieren
        theme_manager.reload_theme.assert_not_called()
        callback.assert_not_called()
    
    def test_debouncing(self, tmp_path):
        """Test: Debouncing verhindert mehrfache Events"""
        theme_manager = Mock()
        theme_manager.reload_theme.return_value = True
        
        callback = Mock()
        
        handler = ThemeFileHandler(
            theme_manager,
            callback,
            debounce_seconds=0.5
        )
        
        # Erstelle Mock Event
        event = Mock()
        event.is_directory = False
        event.src_path = str(tmp_path / "test-theme.json")
        
        # Erstes Event
        handler.on_modified(event)
        
        # Zweites Event sofort danach (sollte ignoriert werden)
        handler.on_modified(event)
        
        # Assertions: Nur einmal aufgerufen
        assert theme_manager.reload_theme.call_count == 1
        assert callback.call_count == 1
        
        # Warte länger als Debounce-Zeit
        time.sleep(0.6)
        
        # Drittes Event (sollte durchkommen)
        handler.on_modified(event)
        
        # Assertions: Jetzt zweimal aufgerufen
        assert theme_manager.reload_theme.call_count == 2
        assert callback.call_count == 2
    
    def test_reload_failure(self, tmp_path):
        """Test: Fehler beim Reload wird behandelt"""
        theme_manager = Mock()
        theme_manager.reload_theme.return_value = False
        
        callback = Mock()
        
        handler = ThemeFileHandler(theme_manager, callback)
        
        # Erstelle Mock Event
        event = Mock()
        event.is_directory = False
        event.src_path = str(tmp_path / "test-theme.json")
        
        # Trigger Event
        handler.on_modified(event)
        
        # Assertions: reload_theme wurde aufgerufen, aber callback nicht
        theme_manager.reload_theme.assert_called_once()
        callback.assert_not_called()


class TestHotReloadManager:
    """Tests für HotReloadManager"""
    
    def test_init(self, tmp_path):
        """Test: Initialisierung"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(
            theme_manager,
            watch_dir=str(tmp_path),
            debounce_seconds=0.5
        )
        
        assert manager.theme_manager == theme_manager
        assert manager.watch_dir == tmp_path
        assert manager.debounce_seconds == 0.5
        assert manager.observer is None
        assert manager.is_running is False
    
    def test_start_stop(self, tmp_path):
        """Test: Start und Stop"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        # Start
        manager.start()
        
        assert manager.is_running is True
        assert manager.observer is not None
        assert manager.stats['started_at'] is not None
        
        # Stop
        manager.stop()
        
        assert manager.is_running is False
    
    def test_start_with_callback(self, tmp_path):
        """Test: Start mit Callback"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        callback = Mock()
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        manager.start(callback=callback)
        
        assert manager.is_running is True
        
        manager.stop()
    
    def test_start_already_running(self, tmp_path):
        """Test: Start wenn bereits läuft"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        manager.start()
        
        # Versuche nochmal zu starten
        manager.start()  # Sollte Warnung loggen
        
        assert manager.is_running is True
        
        manager.stop()
    
    def test_stop_not_running(self, tmp_path):
        """Test: Stop wenn nicht läuft"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        # Stop ohne Start
        manager.stop()  # Sollte Warnung loggen
        
        assert manager.is_running is False
    
    def test_restart(self, tmp_path):
        """Test: Restart"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        manager.start()
        assert manager.is_running is True
        
        manager.restart()
        assert manager.is_running is True
        
        manager.stop()
    
    def test_get_stats(self, tmp_path):
        """Test: Statistiken abrufen"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        # Stats vor Start
        stats = manager.get_stats()
        assert stats['is_running'] is False
        assert stats['reloads'] == 0
        
        # Start
        manager.start()
        
        # Stats nach Start
        stats = manager.get_stats()
        assert stats['is_running'] is True
        assert 'uptime_seconds' in stats
        assert 'uptime_formatted' in stats
        
        manager.stop()
    
    def test_context_manager(self, tmp_path):
        """Test: Context Manager"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = HotReloadManager(theme_manager, watch_dir=str(tmp_path))
        
        with manager:
            assert manager.is_running is True
        
        assert manager.is_running is False
    
    def test_watch_dir_not_exists(self):
        """Test: Watch-Verzeichnis existiert nicht"""
        theme_manager = Mock()
        theme_manager.themes_dir = Path("/nonexistent")
        
        manager = HotReloadManager(
            theme_manager,
            watch_dir="/nonexistent"
        )
        
        with pytest.raises(FileNotFoundError):
            manager.start()


class TestCreateHotReloadManager:
    """Tests für create_hot_reload_manager Factory"""
    
    def test_create_enabled(self, tmp_path):
        """Test: Erstellen wenn aktiviert"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = create_hot_reload_manager(
            theme_manager,
            enabled=True,
            debounce_seconds=0.5
        )
        
        assert manager is not None
        assert isinstance(manager, HotReloadManager)
        assert manager.debounce_seconds == 0.5
    
    def test_create_disabled(self, tmp_path):
        """Test: Erstellen wenn deaktiviert"""
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        
        manager = create_hot_reload_manager(
            theme_manager,
            enabled=False
        )
        
        assert manager is None


class TestDevMode:
    """Tests für Development Mode"""
    
    def test_dev_mode_config_defaults(self):
        """Test: DevModeConfig Defaults"""
        config = DevModeConfig()
        
        assert config.hot_reload_enabled is False
        assert config.hot_reload_debounce == 1.0
        assert config.show_validation_errors is True
    
    def test_is_dev_mode(self):
        """Test: is_dev_mode()"""
        # Deaktiviert
        disable_dev_mode()
        assert is_dev_mode() is False
        
        # Aktiviert
        enable_dev_mode()
        assert is_dev_mode() is True
        
        # Cleanup
        disable_dev_mode()
    
    def test_enable_disable_dev_mode(self):
        """Test: enable_dev_mode() und disable_dev_mode()"""
        import os
        
        # Aktivieren
        enable_dev_mode()
        assert os.getenv('SHADCN_DEV_MODE') == '1'
        
        # Deaktivieren
        disable_dev_mode()
        assert os.getenv('SHADCN_DEV_MODE') is None
    
    @patch.dict('os.environ', {'SHADCN_DEV_MODE': '1'})
    def test_get_dev_mode_config_enabled(self):
        """Test: get_dev_mode_config() wenn aktiviert"""
        config = get_dev_mode_config()
        
        assert config.hot_reload_enabled is True
        assert config.verbose_logging is True
        assert config.show_dev_tools is True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_dev_mode_config_disabled(self):
        """Test: get_dev_mode_config() wenn deaktiviert"""
        config = get_dev_mode_config()
        
        assert config.hot_reload_enabled is False
        assert config.verbose_logging is False
        assert config.show_dev_tools is False
    
    @patch.dict('os.environ', {
        'SHADCN_DEV_MODE': '1',
        'SHADCN_HOT_RELOAD': '0',
        'SHADCN_HOT_RELOAD_DEBOUNCE': '2.5',
        'SHADCN_VERBOSE': '0',
        'SHADCN_DISABLE_CACHE': '1'
    })
    def test_get_dev_mode_config_custom(self):
        """Test: get_dev_mode_config() mit Custom-Werten"""
        config = get_dev_mode_config()
        
        assert config.hot_reload_enabled is False  # Explizit deaktiviert
        assert config.hot_reload_debounce == 2.5
        assert config.verbose_logging is False
        assert config.disable_css_cache is True


class TestIntegration:
    """Integrationstests"""
    
    def test_full_workflow(self, tmp_path):
        """Test: Vollständiger Workflow"""
        # Erstelle Test-Theme-Datei
        theme_file = tmp_path / "test-theme.json"
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {
                "background": "#ffffff",
                "foreground": "#000000",
                "primary": "#0000ff",
                "primary_foreground": "#ffffff",
                "secondary": "#cccccc",
                "secondary_foreground": "#000000",
                "accent": "#ff0000",
                "accent_foreground": "#ffffff",
                "success": "#00ff00",
                "warning": "#ffff00",
                "error": "#ff0000",
                "info": "#0000ff",
                "muted": "#cccccc",
                "muted_foreground": "#666666",
                "border": "#dddddd",
                "input": "#eeeeee",
                "ring": "#0000ff",
                "chart_1": "#ff0000",
                "chart_2": "#00ff00",
                "chart_3": "#0000ff",
                "chart_4": "#ffff00",
                "chart_5": "#ff00ff"
            },
            "typography": {
                "font_family": "Arial",
                "font_family_mono": "Courier",
                "font_size_xs": "0.75rem",
                "font_size_sm": "0.875rem",
                "font_size_base": "1rem",
                "font_size_lg": "1.125rem",
                "font_size_xl": "1.25rem",
                "font_size_2xl": "1.5rem",
                "font_weight_normal": 400,
                "font_weight_medium": 500,
                "font_weight_semibold": 600,
                "font_weight_bold": 700,
                "line_height_tight": 1.25,
                "line_height_normal": 1.5,
                "line_height_relaxed": 1.75
            },
            "spacing": {
                "spacing_0": "0",
                "spacing_1": "0.25rem",
                "spacing_2": "0.5rem",
                "spacing_3": "0.75rem",
                "spacing_4": "1rem",
                "spacing_6": "1.5rem",
                "spacing_8": "2rem",
                "spacing_12": "3rem",
                "spacing_16": "4rem"
            },
            "shadows": {
                "shadow_sm": "0 1px 2px rgba(0,0,0,0.05)",
                "shadow_md": "0 4px 6px rgba(0,0,0,0.1)",
                "shadow_lg": "0 10px 15px rgba(0,0,0,0.1)",
                "shadow_xl": "0 20px 25px rgba(0,0,0,0.1)"
            },
            "borders": {
                "border_width": "1px",
                "border_radius_sm": "0.25rem",
                "border_radius_md": "0.375rem",
                "border_radius_lg": "0.5rem",
                "border_radius_full": "9999px"
            },
            "animations": {
                "transition_fast": "150ms",
                "transition_base": "200ms",
                "transition_slow": "300ms",
                "easing_default": "ease"
            }
        }
        
        with open(theme_file, 'w') as f:
            json.dump(theme_data, f)
        
        # Erstelle ThemeManager
        theme_manager = Mock()
        theme_manager.themes_dir = tmp_path
        theme_manager.reload_theme.return_value = True
        
        # Erstelle Callback
        callback_called = []
        
        def callback(theme_name):
            callback_called.append(theme_name)
        
        # Erstelle und starte HotReloadManager
        manager = HotReloadManager(
            theme_manager,
            watch_dir=str(tmp_path),
            debounce_seconds=0.1
        )
        
        manager.start(callback=callback)
        
        # Warte kurz
        time.sleep(0.2)
        
        # Ändere Theme-Datei
        theme_data['colors']['primary'] = '#ff0000'
        with open(theme_file, 'w') as f:
            json.dump(theme_data, f)
        
        # Warte auf File-Event
        time.sleep(0.5)
        
        # Stop Manager
        manager.stop()
        
        # Assertions
        assert len(callback_called) > 0
        assert 'test-theme' in callback_called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
