# Hot Reload - Quick Start

Starte in 5 Minuten mit Hot Reload für Theme-Entwicklung.

## 1. Installation

Hot Reload ist bereits installiert! Watchdog ist in `requirements.txt` enthalten.

```bash
# Falls noch nicht installiert
pip install watchdog
```

## 2. Aktiviere Development Mode

**Option A: In Python**

```python
from theming.dev_mode import enable_dev_mode

enable_dev_mode()
```

**Option B: Via Umgebungsvariable**

```bash
# Linux/Mac
export SHADCN_DEV_MODE=1

# Windows PowerShell
$env:SHADCN_DEV_MODE="1"
```

## 3. Starte Hot Reload

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager

# Theme Manager
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# Hot Reload Manager
manager = create_hot_reload_manager(theme_manager, enabled=True)
manager.start()

# Deine App
st.title("Meine App")
st.write("Hot Reload ist aktiv!")
```

## 4. Teste es!

1. **Starte deine App:**
   ```bash
   streamlit run app.py
   ```

2. **Öffne Theme-Datei:**
   ```
   theming/themes/shadcn-default.json
   ```

3. **Ändere eine Farbe:**
   ```json
   {
     "colors": {
       "primary": "#ff0000"  // Ändere zu Rot
     }
   }
   ```

4. **Speichere die Datei**

5. **Beobachte:** Theme wird automatisch neu geladen! 🎉

## 5. Mit Validierung (Optional)

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

## Demo ausführen

```bash
streamlit run demo_hot_reload.py
```

## Nächste Schritte

- 📖 Lies die [vollständige Referenz](HOT_RELOAD_REFERENCE.md)
- 📝 Sieh dir [Beispiele](HOT_RELOAD_USAGE_EXAMPLE.md) an
- 🚀 Lies die [Quick Reference](../docs/HOT_RELOAD_QUICK_REFERENCE.md)

## Troubleshooting

**Problem:** Hot Reload funktioniert nicht

**Lösung:**
```python
# Prüfe Status
from theming.dev_mode import is_dev_mode
print(f"Dev Mode: {is_dev_mode()}")
print(f"Manager läuft: {manager.is_running}")
```

**Problem:** Zu viele Reloads

**Lösung:**
```python
# Erhöhe Debounce-Zeit
manager = create_hot_reload_manager(
    theme_manager,
    debounce_seconds=2.0  # Statt 1.0
)
```

## Fertig! 🎉

Du kannst jetzt Theme-Dateien bearbeiten und Änderungen sofort sehen!
