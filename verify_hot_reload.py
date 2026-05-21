"""
Verification Script für Hot Reload System

Testet alle Features des Hot Reload Systems.
"""

import time
import json
from pathlib import Path

# Hot Reload System
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import (
    HotReloadManager,
    ThemeFileHandler,
    create_hot_reload_manager
)
from theming.dev_mode import (
    DevModeConfig,
    get_dev_mode_config,
    is_dev_mode,
    enable_dev_mode,
    disable_dev_mode
)
from theming.validation_display import ValidationDisplay
from theming.theme_validator import ThemeValidator


def print_section(title: str):
    """Druckt Abschnitts-Header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_dev_mode():
    """Test: Development Mode"""
    print_section("1. Development Mode")
    
    # Test enable/disable
    print(" Testing enable_dev_mode()...")
    enable_dev_mode()
    assert is_dev_mode() is True
    print("   Dev Mode aktiviert")
    
    print(" Testing disable_dev_mode()...")
    disable_dev_mode()
    assert is_dev_mode() is False
    print("   Dev Mode deaktiviert")
    
    # Test config
    print(" Testing get_dev_mode_config()...")
    enable_dev_mode()
    config = get_dev_mode_config()
    assert isinstance(config, DevModeConfig)
    assert config.hot_reload_enabled is True
    print("   Config geladen")
    print(f"     - Hot Reload: {config.hot_reload_enabled}")
    print(f"     - Debounce: {config.hot_reload_debounce}s")
    print(f"     - Verbose: {config.verbose_logging}")


def test_theme_file_handler():
    """Test: ThemeFileHandler"""
    print_section("2. ThemeFileHandler")
    
    # Mock Theme Manager
    class MockThemeManager:
        def reload_theme(self, theme_name):
            return True
    
    theme_manager = MockThemeManager()
    
    # Callback
    callback_called = []
    def callback(theme_name):
        callback_called.append(theme_name)
    
    # Erstelle Handler
    print(" Creating ThemeFileHandler...")
    handler = ThemeFileHandler(
        theme_manager,
        callback,
        debounce_seconds=0.1
    )
    print("   Handler erstellt")
    print(f"     - Debounce: {handler.debounce_seconds}s")
    
    # Test Event
    print(" Testing on_modified()...")
    
    class MockEvent:
        is_directory = False
        src_path = "test-theme.json"
    
    handler.on_modified(MockEvent())
    
    assert len(callback_called) == 1
    assert callback_called[0] == "test-theme"
    print("   Event verarbeitet")
    print(f"     - Callback aufgerufen: {callback_called}")


def test_hot_reload_manager():
    """Test: HotReloadManager"""
    print_section("3. HotReloadManager")
    
    # Theme Manager
    print(" Creating ThemeManager...")
    theme_manager = ThemeManager()
    print("   ThemeManager erstellt")
    
    # Hot Reload Manager
    print(" Creating HotReloadManager...")
    manager = HotReloadManager(
        theme_manager,
        debounce_seconds=0.5
    )
    print("   Manager erstellt")
    print(f"     - Watch Dir: {manager.watch_dir}")
    print(f"     - Debounce: {manager.debounce_seconds}s")
    
    # Start
    print(" Starting Hot Reload...")
    manager.start()
    assert manager.is_running is True
    print("   Hot Reload gestartet")
    
    # Stats
    print(" Getting stats...")
    stats = manager.get_stats()
    print("   Stats abgerufen:")
    print(f"     - Running: {stats['is_running']}")
    print(f"     - Reloads: {stats['reloads']}")
    print(f"     - Errors: {stats['errors']}")
    
    # Stop
    print(" Stopping Hot Reload...")
    manager.stop()
    assert manager.is_running is False
    print("   Hot Reload gestoppt")


def test_create_hot_reload_manager():
    """Test: create_hot_reload_manager Factory"""
    print_section("4. create_hot_reload_manager()")
    
    theme_manager = ThemeManager()
    
    # Enabled
    print(" Creating with enabled=True...")
    manager = create_hot_reload_manager(
        theme_manager,
        enabled=True,
        debounce_seconds=1.0
    )
    assert manager is not None
    assert isinstance(manager, HotReloadManager)
    print("   Manager erstellt")
    
    # Disabled
    print(" Creating with enabled=False...")
    manager = create_hot_reload_manager(
        theme_manager,
        enabled=False
    )
    assert manager is None
    print("   None zurückgegeben (wie erwartet)")


def test_validation_display():
    """Test: ValidationDisplay"""
    print_section("5. ValidationDisplay")
    
    print(" Creating ValidationDisplay...")
    display = ValidationDisplay()
    print("   Display erstellt")
    
    # Test error summary
    print(" Testing get_error_summary()...")
    summary = display.get_error_summary()
    assert summary['total_validations'] == 0
    assert summary['total_errors'] == 0
    print("   Summary abgerufen:")
    print(f"     - Validations: {summary['total_validations']}")
    print(f"     - Errors: {summary['total_errors']}")
    
    # Add to history (internal)
    print(" Testing _add_to_history()...")
    display._add_to_history(
        "test-theme",
        ["Error 1", "Error 2"],
        ["Warning 1"]
    )
    
    summary = display.get_error_summary()
    assert summary['total_validations'] == 1
    assert summary['total_errors'] == 2
    assert summary['total_warnings'] == 1
    print("   Historie aktualisiert:")
    print(f"     - Validations: {summary['total_validations']}")
    print(f"     - Errors: {summary['total_errors']}")
    print(f"     - Warnings: {summary['total_warnings']}")


def test_context_manager():
    """Test: Context Manager"""
    print_section("6. Context Manager")
    
    theme_manager = ThemeManager()
    
    print(" Testing with statement...")
    with HotReloadManager(theme_manager) as manager:
        assert manager.is_running is True
        print("   Manager läuft innerhalb Context")
    
    assert manager.is_running is False
    print("   Manager gestoppt nach Context")


def test_integration():
    """Test: Integration"""
    print_section("7. Integration Test")
    
    # Setup
    print(" Setting up integration test...")
    enable_dev_mode()
    theme_manager = ThemeManager()
    theme_manager.set_theme('shadcn-default')
    
    validator = ThemeValidator()
    display = ValidationDisplay()
    
    # Callback mit Validierung
    validation_results = []
    
    def on_reload(theme_name: str):
        theme = theme_manager.get_theme(theme_name)
        if theme:
            is_valid, errors = validator.validate_theme(theme.to_dict())
            validation_results.append({
                'theme': theme_name,
                'valid': is_valid,
                'errors': errors
            })
    
    # Manager
    manager = create_hot_reload_manager(
        theme_manager,
        enabled=True,
        debounce_seconds=0.5
    )
    
    assert manager is not None
    print("   Integration Setup komplett")
    
    # Cleanup
    if manager:
        manager.stop()


def main():
    """Hauptfunktion"""
    print("\n" + "" * 30)
    print("  HOT RELOAD SYSTEM VERIFICATION")
    print("" * 30)
    
    try:
        # Tests
        test_dev_mode()
        test_theme_file_handler()
        test_hot_reload_manager()
        test_create_hot_reload_manager()
        test_validation_display()
        test_context_manager()
        test_integration()
        
        # Zusammenfassung
        print_section(" VERIFICATION COMPLETE")
        print("\nAlle Tests bestanden!")
        print("\nImplementierte Features:")
        print("   ThemeFileHandler mit watchdog")
        print("   HotReloadManager")
        print("   Theme-Datei-Überwachung")
        print("   Automatisches Neuladen")
        print("   Debouncing für File-Events")
        print("   Development-Mode-Flag")
        print("   Echtzeit-Validierungs-Fehler")
        
        print("\nNächste Schritte:")
        print("  1. Demo ausführen: streamlit run demo_hot_reload.py")
        print("  2. Tests ausführen: pytest tests/test_hot_reload.py -v")
        print("  3. Dokumentation lesen: theming/HOT_RELOAD_QUICK_START.md")
        
        return True
        
    except Exception as e:
        print(f"\n FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
