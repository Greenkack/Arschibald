# Hot Reload - Quick Reference

Schnellreferenz für Hot Reload System.

## Setup (5 Minuten)

### 1. Development Mode aktivieren

```python
from theming.dev_mode import enable_dev_mode

enable_dev_mode()
```

Oder via Umgebungsvariable:

```bash
export SHADCN_DEV_MODE=1
export SHADCN_HOT_RELOAD=1
```

### 2. Hot Reload starten

```python
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager

# Theme Manager initialisieren
theme_manager = ThemeManager()

# Hot Reload Manager erstellen und starten
manager = create_hot_reload_manager(theme_manager, enabled=True)
manager.start()
```

### 3. Theme-Datei bearbeiten

1. Öffne Theme-Datei in Editor (z.B. `theming/themes/shadcn-default.json`)
2. Ändere Farben, Schriftarten, etc.
3. Speichere Datei
4. Theme wird automatisch neu geladen! 🎉

---

## Häufige Anwendungsfälle

### Mit Callback

```python
def on_reload(theme_name: str):
    print(f"Theme {theme_name} wurde neu geladen!")

manager.start(callback=on_reload)
```

### Mit Validierung

```python
from theming.theme_validator import ThemeValidator
from theming.validation_display import ValidationDisplay

validator = ThemeValidator()
display = ValidationDisplay()

def on_reload(theme_name: str):
    theme = theme_manager.get_theme(theme_name)
    is_valid, errors = validator.validate_theme(theme.to_dict())
    
    if is_valid:
        display.show_validation_success(theme_name)
    else:
        display.show_validation_errors(theme_name, errors)

manager.start(callback=on_reload)
```

### Context Manager

```python
with create_hot_reload_manager(theme_manager) as manager:
    # Hot Reload ist aktiv
    run_app()
# Automatisch gestoppt
```

---

## Konfiguration

### Debounce-Zeit anpassen

```python
# Schnell (0.5s)
manager = create_hot_reload_manager(
    theme_manager,
    debounce_seconds=0.5
)

# Langsam (2.0s)
manager = create_hot_reload_manager(
    theme_manager,
    debounce_seconds=2.0
)
```

### Via Umgebungsvariablen

```bash
# Development Mode
export SHADCN_DEV_MODE=1

# Hot Reload
export SHADCN_HOT_RELOAD=1
export SHADCN_HOT_RELOAD_DEBOUNCE=1.5

# Verbose Logging
export SHADCN_VERBOSE=1

# Cache deaktivieren
export SHADCN_DISABLE_CACHE=1
```

---

## Statistiken

```python
stats = manager.get_stats()

print(f"Reloads: {stats['reloads']}")
print(f"Fehler: {stats['errors']}")
print(f"Uptime: {stats['uptime_formatted']}")
print(f"Letzter Reload: {stats['last_reload']}")
```

---

## Streamlit Integration

```python
import streamlit as st

# In Sidebar
with st.sidebar:
    if manager.is_running:
        st.success("🟢 Hot Reload aktiv")
        
        stats = manager.get_stats()
        st.metric("Reloads", stats['reloads'])
        st.text(f"Uptime: {stats['uptime_formatted']}")
    else:
        st.warning("🔴 Hot Reload inaktiv")
```

---

## Troubleshooting

### Problem: Hot Reload funktioniert nicht

**Lösung:**
```python
# 1. Prüfe ob Dev Mode aktiv
from theming.dev_mode import is_dev_mode
print(f"Dev Mode: {is_dev_mode()}")

# 2. Prüfe ob Manager läuft
print(f"Running: {manager.is_running}")

# 3. Prüfe Watch-Verzeichnis
print(f"Watch Dir: {manager.watch_dir}")
print(f"Exists: {manager.watch_dir.exists()}")
```

### Problem: Zu viele Reloads

**Lösung:**
```python
# Erhöhe Debounce-Zeit
manager = create_hot_reload_manager(
    theme_manager,
    debounce_seconds=2.0  # Statt 1.0
)
```

### Problem: Fehler werden nicht angezeigt

**Lösung:**
```python
# Aktiviere Validierung im Callback
def on_reload(theme_name: str):
    validator = ThemeValidator()
    theme = theme_manager.get_theme(theme_name)
    is_valid, errors = validator.validate_theme(theme.to_dict())
    
    if not is_valid:
        for error in errors:
            st.error(error)

manager.start(callback=on_reload)
```

---

## Best Practices

### ✅ DO

- Aktiviere Hot Reload nur im Development Mode
- Nutze angemessene Debounce-Zeit (1-2 Sekunden)
- Validiere Themes nach Reload
- Stoppe Hot Reload beim Beenden
- Nutze Context Manager für automatisches Cleanup

### ❌ DON'T

- Hot Reload in Production aktivieren
- Zu kurze Debounce-Zeit (<0.5s)
- Hot Reload ohne Validierung
- Manager nicht stoppen
- Mehrere Manager gleichzeitig starten

---

## Cheat Sheet

```python
# Setup
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import enable_dev_mode

enable_dev_mode()
theme_manager = ThemeManager()
manager = create_hot_reload_manager(theme_manager)

# Start
manager.start()

# Mit Callback
manager.start(callback=lambda name: print(f"Reloaded: {name}"))

# Stop
manager.stop()

# Restart
manager.restart()

# Stats
stats = manager.get_stats()

# Context Manager
with manager:
    # Aktiv
    pass
# Gestoppt
```

---

## Demo ausführen

```bash
streamlit run demo_hot_reload.py
```

Dann:
1. Aktiviere "Development Mode" in Sidebar
2. Aktiviere "Hot Reload aktivieren"
3. Öffne Theme-Datei in Editor
4. Ändere Farben
5. Speichere
6. Beobachte automatischen Reload! 🎉

---

## Weitere Ressourcen

- **Vollständige Referenz:** `theming/HOT_RELOAD_REFERENCE.md`
- **Tests:** `tests/test_hot_reload.py`
- **Demo:** `demo_hot_reload.py`
- **Source Code:** `theming/hot_reload_manager.py`
