# Hot Reload - Usage Example

Praktisches Beispiel für Hot Reload in einer Streamlit-App.

## Einfaches Beispiel

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import enable_dev_mode

# Aktiviere Development Mode
enable_dev_mode()

# Initialisiere Theme Manager
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# Erstelle Hot Reload Manager
if 'hot_reload_manager' not in st.session_state:
    manager = create_hot_reload_manager(
        theme_manager,
        enabled=True,
        debounce_seconds=1.0
    )
    
    if manager:
        manager.start()
        st.session_state.hot_reload_manager = manager

# Deine App
st.title("Meine App mit Hot Reload")
st.write("Ändere Theme-Dateien und sieh die Änderungen sofort!")

# Zeige aktuelles Theme
current_theme = theme_manager.get_current_theme()
st.info(f"Aktuelles Theme: {current_theme}")
```

---

## Mit Validierung

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.theme_validator import ThemeValidator
from theming.validation_display import ValidationDisplay
from theming.dev_mode import enable_dev_mode

# Setup
enable_dev_mode()

# Initialisierung
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

if 'validation_display' not in st.session_state:
    st.session_state.validation_display = ValidationDisplay()

theme_manager = st.session_state.theme_manager
validation_display = st.session_state.validation_display

# Callback mit Validierung
def on_theme_reload(theme_name: str):
    """Wird aufgerufen wenn Theme neu geladen wurde"""
    
    # Validiere Theme
    validator = ThemeValidator()
    theme = theme_manager.get_theme(theme_name)
    
    if theme:
        is_valid, errors = validator.validate_theme(theme.to_dict())
        
        # Zeige Ergebnis
        if is_valid:
            validation_display.show_validation_success(theme_name)
            st.toast(f"✅ Theme '{theme_name}' erfolgreich geladen!", icon="🎨")
        else:
            validation_display.show_validation_errors(theme_name, errors)
            st.toast(f"❌ Theme '{theme_name}' hat Fehler!", icon="⚠️")

# Hot Reload Manager
if 'hot_reload_manager' not in st.session_state:
    manager = create_hot_reload_manager(theme_manager, enabled=True)
    
    if manager:
        manager.start(callback=on_theme_reload)
        st.session_state.hot_reload_manager = manager

# App
st.title("Theme-Entwicklung mit Validierung")

# Zeige Validierungs-Historie
validation_display.show_validation_history(limit=5)
```

---

## Mit Sidebar-Steuerung

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import is_dev_mode, enable_dev_mode, disable_dev_mode

# Initialisierung
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

if 'hot_reload_manager' not in st.session_state:
    st.session_state.hot_reload_manager = None

theme_manager = st.session_state.theme_manager

# Sidebar: Steuerung
with st.sidebar:
    st.header("⚙️ Hot Reload")
    
    # Development Mode Toggle
    dev_mode = st.checkbox(
        "Development Mode",
        value=is_dev_mode()
    )
    
    if dev_mode:
        enable_dev_mode()
    else:
        disable_dev_mode()
    
    # Hot Reload Toggle
    hot_reload_enabled = st.checkbox(
        "Hot Reload aktivieren",
        value=st.session_state.hot_reload_manager is not None,
        disabled=not dev_mode
    )
    
    # Debounce Slider
    debounce = st.slider(
        "Debounce (Sekunden)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        disabled=not dev_mode
    )
    
    # Status
    st.markdown("---")
    
    if st.session_state.hot_reload_manager:
        st.success("🟢 Hot Reload aktiv")
        
        stats = st.session_state.hot_reload_manager.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Reloads", stats['reloads'])
        with col2:
            st.metric("Fehler", stats['errors'])
        
        st.text(f"Uptime: {stats['uptime_formatted']}")
        
        if st.button("🔄 Restart", use_container_width=True):
            st.session_state.hot_reload_manager.restart()
            st.rerun()
    else:
        st.warning("🔴 Hot Reload inaktiv")

# Hot Reload starten/stoppen
if hot_reload_enabled and not st.session_state.hot_reload_manager:
    manager = create_hot_reload_manager(
        theme_manager,
        enabled=True,
        debounce_seconds=debounce
    )
    
    if manager:
        manager.start()
        st.session_state.hot_reload_manager = manager
        st.rerun()

elif not hot_reload_enabled and st.session_state.hot_reload_manager:
    st.session_state.hot_reload_manager.stop()
    st.session_state.hot_reload_manager = None
    st.rerun()

# Main App
st.title("Meine App")
st.write("Nutze die Sidebar um Hot Reload zu steuern")
```

---

## Mit Performance-Monitoring

```python
import streamlit as st
import time
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import enable_dev_mode

# Setup
enable_dev_mode()

# Initialisierung
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

if 'reload_times' not in st.session_state:
    st.session_state.reload_times = []

theme_manager = st.session_state.theme_manager

# Callback mit Performance-Messung
def on_theme_reload(theme_name: str):
    """Misst Reload-Zeit"""
    start = time.perf_counter()
    
    # Theme ist bereits geladen, messe nur CSS-Generierung
    css = theme_manager.generate_css(minified=False)
    
    duration = (time.perf_counter() - start) * 1000  # ms
    
    # Speichere Zeit
    st.session_state.reload_times.append({
        'theme': theme_name,
        'duration_ms': duration,
        'timestamp': time.time()
    })
    
    # Begrenze Historie
    if len(st.session_state.reload_times) > 50:
        st.session_state.reload_times = st.session_state.reload_times[-50:]
    
    st.toast(f"⚡ Reload in {duration:.1f}ms", icon="🔄")

# Hot Reload Manager
if 'hot_reload_manager' not in st.session_state:
    manager = create_hot_reload_manager(theme_manager, enabled=True)
    
    if manager:
        manager.start(callback=on_theme_reload)
        st.session_state.hot_reload_manager = manager

# App
st.title("Performance-Monitoring")

# Zeige Performance-Metriken
if st.session_state.reload_times:
    st.subheader("📊 Reload-Performance")
    
    times = [r['duration_ms'] for r in st.session_state.reload_times]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Durchschnitt", f"{sum(times)/len(times):.1f}ms")
    
    with col2:
        st.metric("Minimum", f"{min(times):.1f}ms")
    
    with col3:
        st.metric("Maximum", f"{max(times):.1f}ms")
    
    # Chart
    import pandas as pd
    df = pd.DataFrame(st.session_state.reload_times)
    st.line_chart(df.set_index('timestamp')['duration_ms'])
```

---

## Mit Context Manager

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import HotReloadManager
from theming.dev_mode import enable_dev_mode

enable_dev_mode()

# Theme Manager
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# Nutze Context Manager
with HotReloadManager(theme_manager, debounce_seconds=1.0) as manager:
    st.title("App mit Context Manager")
    st.write("Hot Reload ist aktiv während dieser Block läuft")
    
    # Zeige Stats
    stats = manager.get_stats()
    st.metric("Reloads", stats['reloads'])
    
    # Deine App-Logik
    st.write("Ändere Theme-Dateien und sieh die Änderungen!")

# Hot Reload wird automatisch gestoppt
st.info("Hot Reload wurde gestoppt")
```

---

## Production-Ready Beispiel

```python
import streamlit as st
import os
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import create_hot_reload_manager
from theming.dev_mode import get_dev_mode_config

# Lade Config aus Umgebungsvariablen
config = get_dev_mode_config()

# Initialisierung
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# Hot Reload nur in Development Mode
if config.hot_reload_enabled:
    if 'hot_reload_manager' not in st.session_state:
        manager = create_hot_reload_manager(
            theme_manager,
            enabled=True,
            debounce_seconds=config.hot_reload_debounce
        )
        
        if manager:
            manager.start()
            st.session_state.hot_reload_manager = manager
            
            # Cleanup registrieren
            import atexit
            atexit.register(manager.stop)

# App
st.title("Production-Ready App")

# Zeige Environment
env = os.getenv('ENVIRONMENT', 'production')
st.info(f"Environment: {env}")

if config.hot_reload_enabled:
    st.success("🟢 Development Mode - Hot Reload aktiv")
else:
    st.info("🔵 Production Mode - Hot Reload deaktiviert")
```

---

## Umgebungsvariablen setzen

### Linux/Mac

```bash
# Development
export SHADCN_DEV_MODE=1
export SHADCN_HOT_RELOAD=1
export SHADCN_HOT_RELOAD_DEBOUNCE=1.0
export SHADCN_VERBOSE=1

# App starten
streamlit run app.py
```

### Windows (PowerShell)

```powershell
# Development
$env:SHADCN_DEV_MODE="1"
$env:SHADCN_HOT_RELOAD="1"
$env:SHADCN_HOT_RELOAD_DEBOUNCE="1.0"
$env:SHADCN_VERBOSE="1"

# App starten
streamlit run app.py
```

### .env Datei

```env
# .env
SHADCN_DEV_MODE=1
SHADCN_HOT_RELOAD=1
SHADCN_HOT_RELOAD_DEBOUNCE=1.0
SHADCN_VERBOSE=1
SHADCN_DISABLE_CACHE=0
```

```python
# In App
from dotenv import load_dotenv
load_dotenv()

# Config wird automatisch aus .env geladen
config = get_dev_mode_config()
```

---

## Tipps

1. **Nutze Session State** für Manager-Instanzen
2. **Registriere Cleanup** mit `atexit`
3. **Validiere Themes** nach Reload
4. **Zeige Feedback** mit `st.toast()`
5. **Monitore Performance** mit Callbacks
6. **Nutze Context Manager** für automatisches Cleanup
7. **Setze Umgebungsvariablen** für einfache Konfiguration
