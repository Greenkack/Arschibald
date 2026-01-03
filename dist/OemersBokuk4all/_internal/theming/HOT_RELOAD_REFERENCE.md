## Hot Reload System - Referenz

Vollständige API-Referenz für das Hot Reload System.

### ThemeFileHandler

Handler für Theme-Datei-Änderungen mit Debouncing.

```python
from theming.hot_reload_manager import ThemeFileHandler

handler = ThemeFileHandler(
    theme_manager=theme_manager,
    callback=my_callback,
    debounce_seconds=1.0
)
```

**Parameter:**
- `theme_manager`: ThemeManager-Instanz
- `callback`: Callback-Funktion die bei Theme-Änderung aufgerufen wird
- `debounce_seconds`: Debounce-Zeit in Sekunden (Standard: 1.0)

**Methoden:**

#### `on_modified(event)`

Wird aufgerufen wenn eine Datei geändert wird.

```python
# Wird automatisch von watchdog aufgerufen
handler.on_modified(event)
```

**Verhalten:**
- Ignoriert Verzeichnis-Events
- Verarbeitet nur `.json` Dateien
- Wendet Debouncing an
- Lädt Theme neu via `theme_manager.reload_theme()`
- Ruft Callback auf bei Erfolg
- Zeigt Streamlit-Benachrichtigungen (falls verfügbar)

---

### HotReloadManager

Verwaltet Hot Reload für Theme-Dateien.

```python
from theming.hot_reload_manager import HotReloadManager

manager = HotReloadManager(
    theme_manager=theme_manager,
    watch_dir="/path/to/themes",
    debounce_seconds=1.0
)
```

**Parameter:**
- `theme_manager`: ThemeManager-Instanz
- `watch_dir`: Verzeichnis das überwacht werden soll (optional, Standard: theme_manager.themes_dir)
- `debounce_seconds`: Debounce-Zeit für File-Events (Standard: 1.0)

**Attribute:**
- `is_running`: Ob Hot Reload aktiv ist
- `observer`: watchdog Observer-Instanz
- `stats`: Statistiken (reloads, errors, uptime, etc.)

**Methoden:**

#### `start(callback=None)`

Startet File Watcher.

```python
def on_reload(theme_name: str):
    print(f"Theme {theme_name} wurde neu geladen")

manager.start(callback=on_reload)
```

**Parameter:**
- `callback`: Optional callback function die bei Theme-Änderung aufgerufen wird

**Raises:**
- `FileNotFoundError`: Wenn watch_dir nicht existiert

#### `stop()`

Stoppt File Watcher.

```python
manager.stop()
```

#### `restart(callback=None)`

Startet Hot Reload neu.

```python
manager.restart(callback=my_callback)
```

#### `get_stats()`

Gibt Statistiken zurück.

```python
stats = manager.get_stats()

# stats = {
#     'started_at': '2024-01-15T10:30:00',
#     'reloads': 5,
#     'errors': 0,
#     'last_reload': '2024-01-15T10:35:00',
#     'uptime_seconds': 300.5,
#     'uptime_formatted': '0:05:00',
#     'is_running': True,
#     'watch_dir': '/path/to/themes',
#     'debounce_seconds': 1.0
# }
```

**Returns:**
- Dictionary mit Statistiken

#### Context Manager

HotReloadManager kann als Context Manager verwendet werden:

```python
with HotReloadManager(theme_manager) as manager:
    # Hot Reload ist aktiv
    time.sleep(60)
# Hot Reload wird automatisch gestoppt
```

---

### create_hot_reload_manager()

Factory function zum Erstellen eines HotReloadManagers.

```python
from theming.hot_reload_manager import create_hot_reload_manager

manager = create_hot_reload_manager(
    theme_manager=theme_manager,
    enabled=True,
    debounce_seconds=1.0
)
```

**Parameter:**
- `theme_manager`: ThemeManager-Instanz
- `enabled`: Ob Hot Reload aktiviert sein soll (Standard: True)
- `debounce_seconds`: Debounce-Zeit für File-Events (Standard: 1.0)

**Returns:**
- HotReloadManager-Instanz oder None wenn deaktiviert

---

### DevModeConfig

Konfiguration für Development Mode.

```python
from theming.dev_mode import DevModeConfig

config = DevModeConfig(
    hot_reload_enabled=True,
    hot_reload_debounce=1.0,
    show_validation_errors=True,
    validate_on_reload=True,
    verbose_logging=True,
    log_theme_switches=True,
    log_css_generation=True,
    disable_css_cache=False,
    show_performance_metrics=True,
    show_dev_tools=True,
    show_theme_inspector=True
)
```

**Attribute:**
- `hot_reload_enabled`: Ob Hot Reload aktiviert ist
- `hot_reload_debounce`: Debounce-Zeit in Sekunden
- `show_validation_errors`: Validierungs-Fehler anzeigen
- `validate_on_reload`: Bei Reload validieren
- `verbose_logging`: Verbose Logging aktivieren
- `log_theme_switches`: Theme-Wechsel loggen
- `log_css_generation`: CSS-Generierung loggen
- `disable_css_cache`: CSS-Cache deaktivieren
- `show_performance_metrics`: Performance-Metriken anzeigen
- `show_dev_tools`: Dev-Tools anzeigen
- `show_theme_inspector`: Theme-Inspector anzeigen

---

### Development Mode Functions

#### `get_dev_mode_config()`

Lädt Development Mode Konfiguration aus Umgebungsvariablen.

```python
from theming.dev_mode import get_dev_mode_config

config = get_dev_mode_config()
```

**Environment Variables:**
- `SHADCN_DEV_MODE`: Aktiviert Development Mode (1, true, yes)
- `SHADCN_HOT_RELOAD`: Aktiviert Hot Reload (1, true, yes)
- `SHADCN_HOT_RELOAD_DEBOUNCE`: Debounce-Zeit in Sekunden
- `SHADCN_VERBOSE`: Aktiviert verbose logging (1, true, yes)
- `SHADCN_DISABLE_CACHE`: Deaktiviert CSS-Cache (1, true, yes)

**Returns:**
- DevModeConfig-Instanz

#### `is_dev_mode()`

Prüft ob Development Mode aktiviert ist.

```python
from theming.dev_mode import is_dev_mode

if is_dev_mode():
    print("Development Mode ist aktiv")
```

**Returns:**
- True wenn Dev Mode aktiv

#### `enable_dev_mode()`

Aktiviert Development Mode.

```python
from theming.dev_mode import enable_dev_mode

enable_dev_mode()
```

#### `disable_dev_mode()`

Deaktiviert Development Mode.

```python
from theming.dev_mode import disable_dev_mode

disable_dev_mode()
```

---

### ValidationDisplay

Zeigt Theme-Validierungs-Fehler in Echtzeit an.

```python
from theming.validation_display import ValidationDisplay

display = ValidationDisplay()
```

**Methoden:**

#### `show_validation_errors(theme_name, errors, warnings=None)`

Zeigt Validierungs-Fehler in der UI an.

```python
display.show_validation_errors(
    theme_name="my-theme",
    errors=["Invalid color: #gggggg", "Missing property: primary"],
    warnings=["Deprecated property: old_color"]
)
```

#### `show_validation_success(theme_name)`

Zeigt Erfolgs-Meldung bei erfolgreicher Validierung.

```python
display.show_validation_success("my-theme")
```

#### `show_realtime_validation(theme_name, is_valid, errors=None, warnings=None)`

Zeigt Echtzeit-Validierung während Theme-Entwicklung.

```python
display.show_realtime_validation(
    theme_name="my-theme",
    is_valid=False,
    errors=["Invalid color"],
    warnings=[]
)
```

#### `show_validation_history(limit=10)`

Zeigt Historie der Validierungs-Fehler.

```python
display.show_validation_history(limit=10)
```

#### `clear_history()`

Löscht Validierungs-Historie.

```python
display.clear_history()
```

#### `get_error_summary()`

Gibt Zusammenfassung der Fehler zurück.

```python
summary = display.get_error_summary()

# summary = {
#     'total_validations': 10,
#     'total_errors': 3,
#     'total_warnings': 5,
#     'themes_with_errors': ['theme1', 'theme2']
# }
```

---

## Vollständiges Beispiel

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import enable_dev_mode, get_dev_mode_config
from theming.validation_display import ValidationDisplay
from theming.theme_validator import ThemeValidator

# Aktiviere Development Mode
enable_dev_mode()

# Lade Config
config = get_dev_mode_config()

# Initialisiere Theme Manager
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# Initialisiere Validation Display
validation_display = ValidationDisplay()

# Callback für Theme-Reload
def on_theme_reload(theme_name: str):
    st.toast(f"Theme {theme_name} neu geladen!", icon="🔄")
    
    # Validiere Theme
    if config.validate_on_reload:
        validator = ThemeValidator()
        theme = theme_manager.get_theme(theme_name)
        
        if theme:
            is_valid, errors = validator.validate_theme(theme.to_dict())
            
            if config.show_validation_errors:
                if is_valid:
                    validation_display.show_validation_success(theme_name)
                else:
                    validation_display.show_validation_errors(theme_name, errors)

# Erstelle und starte Hot Reload Manager
if config.hot_reload_enabled:
    hot_reload_manager = create_hot_reload_manager(
        theme_manager,
        enabled=True,
        debounce_seconds=config.hot_reload_debounce
    )
    
    if hot_reload_manager:
        hot_reload_manager.start(callback=on_theme_reload)
        
        # Zeige Status
        st.sidebar.success("🟢 Hot Reload aktiv")
        
        # Zeige Statistiken
        stats = hot_reload_manager.get_stats()
        st.sidebar.metric("Reloads", stats['reloads'])
        st.sidebar.text(f"Uptime: {stats['uptime_formatted']}")

# Deine App-Logik hier...
st.title("Meine App")

# Cleanup beim Beenden
if 'hot_reload_manager' in locals():
    import atexit
    atexit.register(hot_reload_manager.stop)
```

---

## Best Practices

### 1. Development vs. Production

Aktiviere Hot Reload nur im Development Mode:

```python
from theming.dev_mode import is_dev_mode

if is_dev_mode():
    # Hot Reload aktivieren
    manager.start()
else:
    # Production: Kein Hot Reload
    pass
```

### 2. Debounce-Zeit anpassen

Passe die Debounce-Zeit an deine Bedürfnisse an:

```python
# Schnelle Reaktion (für schnelle Iterationen)
manager = HotReloadManager(theme_manager, debounce_seconds=0.5)

# Langsame Reaktion (für große Theme-Dateien)
manager = HotReloadManager(theme_manager, debounce_seconds=2.0)
```

### 3. Validierung aktivieren

Validiere Themes automatisch nach Reload:

```python
def on_reload(theme_name: str):
    validator = ThemeValidator()
    theme = theme_manager.get_theme(theme_name)
    
    if theme:
        is_valid, errors = validator.validate_theme(theme.to_dict())
        
        if not is_valid:
            st.error(f"Theme {theme_name} hat Fehler:")
            for error in errors:
                st.text(f"  - {error}")

manager.start(callback=on_reload)
```

### 4. Cleanup

Stoppe Hot Reload beim Beenden der App:

```python
import atexit

manager = HotReloadManager(theme_manager)
manager.start()

# Registriere Cleanup
atexit.register(manager.stop)
```

### 5. Context Manager verwenden

Nutze Context Manager für automatisches Cleanup:

```python
with HotReloadManager(theme_manager) as manager:
    # Hot Reload ist aktiv
    run_app()
# Hot Reload wird automatisch gestoppt
```

---

## Troubleshooting

### Hot Reload funktioniert nicht

**Problem:** Theme-Änderungen werden nicht erkannt.

**Lösung:**
1. Prüfe ob Development Mode aktiviert ist: `is_dev_mode()`
2. Prüfe ob Hot Reload läuft: `manager.is_running`
3. Prüfe Logs für Fehler
4. Erhöhe Debounce-Zeit

### Zu viele Reloads

**Problem:** Theme wird mehrfach neu geladen.

**Lösung:**
1. Erhöhe Debounce-Zeit: `debounce_seconds=2.0`
2. Prüfe ob Editor mehrere Save-Events auslöst

### Validierungs-Fehler werden nicht angezeigt

**Problem:** Fehler werden nicht in UI angezeigt.

**Lösung:**
1. Aktiviere `show_validation_errors` in Config
2. Aktiviere `validate_on_reload` in Config
3. Prüfe ob ValidationDisplay initialisiert ist

---

## Performance-Tipps

1. **Debouncing:** Nutze angemessene Debounce-Zeit (1-2 Sekunden)
2. **Validierung:** Validiere nur wenn nötig
3. **Logging:** Deaktiviere verbose Logging in Production
4. **Cache:** Aktiviere CSS-Cache in Production
5. **Cleanup:** Stoppe Hot Reload wenn nicht benötigt
