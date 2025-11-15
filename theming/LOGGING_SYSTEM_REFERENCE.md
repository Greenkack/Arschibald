# Theme Logging System - Vollständige Referenz

## Übersicht

Das Theme Logging System bietet umfassendes Logging und Monitoring für das shadcn/ui Theme-System. Es loggt alle wichtigen Ereignisse, Performance-Metriken und Fehler.

## ThemeLogger Klasse

### Initialisierung

```python
from theming.theme_logger import ThemeLogger, get_theme_logger

# Neue Instanz erstellen
logger = ThemeLogger(log_level="INFO", log_dir="logs")

# Oder Singleton-Instanz verwenden (empfohlen)
logger = get_theme_logger()
```

### Log-Level

- `DEBUG`: Detaillierte Informationen für Debugging
- `INFO`: Allgemeine Informationen über normale Operationen
- `WARNING`: Warnungen über potenzielle Probleme
- `ERROR`: Fehler, die behandelt wurden
- `CRITICAL`: Kritische Fehler, die sofortige Aufmerksamkeit erfordern

### Methoden

#### log_theme_switch()

Loggt Theme-Wechsel mit Timestamp und optionaler User-ID.

```python
logger.log_theme_switch(
    from_theme="shadcn-default",
    to_theme="shadcn-dark",
    user_id="user123",  # optional
    duration_ms=45.2    # optional
)
```

**Parameter:**
- `from_theme` (str): Vorheriges Theme
- `to_theme` (str): Neues Theme
- `user_id` (str, optional): Benutzer-ID
- `duration_ms` (float, optional): Dauer des Wechsels in Millisekunden

#### log_css_generation()

Loggt CSS-Generierungs-Ereignisse mit Performance-Metriken.

```python
logger.log_css_generation(
    theme_name="shadcn-dark",
    duration_ms=78.5,
    css_size_bytes=45000  # optional
)
```

**Parameter:**
- `theme_name` (str): Name des Themes
- `duration_ms` (float): Dauer der Generierung in Millisekunden
- `css_size_bytes` (int, optional): Größe des generierten CSS in Bytes

#### log_css_injection()

Loggt CSS-Injection-Ereignisse.

```python
logger.log_css_injection(
    theme_name="shadcn-dark",
    success=True,
    duration_ms=12.3,  # optional
    error=None         # optional
)
```

**Parameter:**
- `theme_name` (str): Name des Themes
- `success` (bool): Ob Injection erfolgreich war
- `duration_ms` (float, optional): Dauer der Injection
- `error` (str, optional): Fehlermeldung falls nicht erfolgreich

#### log_component_render()

Loggt Komponenten-Rendering mit Performance-Daten.

```python
logger.log_component_render(
    component_name="Card",
    duration_ms=23.4,
    success=True,
    error=None,        # optional
    user_id="user123"  # optional
)
```

**Parameter:**
- `component_name` (str): Name der Komponente
- `duration_ms` (float): Dauer des Renderings
- `success` (bool): Ob Rendering erfolgreich war
- `error` (str, optional): Fehlermeldung
- `user_id` (str, optional): Benutzer-ID

#### log_performance_metric()

Loggt allgemeine Performance-Metriken.

```python
logger.log_performance_metric(
    metric_name="css_size",
    value=45.2,
    unit="KB",
    theme_name="shadcn-dark",  # optional
    metadata={"compressed": True}  # optional
)
```

**Parameter:**
- `metric_name` (str): Name der Metrik
- `value` (float): Wert der Metrik
- `unit` (str): Einheit (z.B. "ms", "bytes", "count")
- `theme_name` (str, optional): Name des Themes
- `metadata` (dict, optional): Zusätzliche Metadaten

#### log_cache_event()

Loggt Cache-Ereignisse (Hits und Misses).

```python
logger.log_cache_event(
    event_type="theme_cache",
    cache_key="shadcn-dark",
    hit=True,
    metadata={"source": "memory"}  # optional
)
```

**Parameter:**
- `event_type` (str): Typ des Events
- `cache_key` (str): Cache-Schlüssel
- `hit` (bool): Ob Cache-Hit oder Miss
- `metadata` (dict, optional): Zusätzliche Metadaten

#### log_error()

Loggt Fehler mit Stack-Trace.

```python
try:
    # Code der fehlschlagen könnte
    pass
except Exception as e:
    logger.log_error(
        error_message="Theme konnte nicht geladen werden",
        exception=e,
        category=logger.CATEGORY_ERROR,
        user_id="user123",  # optional
        metadata={"theme": "custom-theme"}  # optional
    )
```

**Parameter:**
- `error_message` (str): Fehlermeldung
- `exception` (Exception, optional): Exception-Objekt
- `category` (str): Fehler-Kategorie
- `user_id` (str, optional): Benutzer-ID
- `metadata` (dict, optional): Zusätzliche Metadaten

#### get_stats()

Gibt Logging-Statistiken zurück.

```python
stats = logger.get_stats()
# {
#     'total_entries': 150,
#     'theme_switches': 12,
#     'css_injections': 8,
#     'component_renders': 95,
#     'errors': 2,
#     'cache_hits': 45,
#     'cache_misses': 10,
#     'cache_hit_rate': '81.8%'
# }
```

#### get_recent_entries()

Gibt die letzten Log-Einträge zurück.

```python
# Alle letzten 50 Einträge
entries = logger.get_recent_entries(count=50)

# Nur Theme-Wechsel
entries = logger.get_recent_entries(
    count=20,
    category=logger.CATEGORY_THEME_SWITCH
)

# Nur Fehler
entries = logger.get_recent_entries(
    count=10,
    level="ERROR"
)
```

**Parameter:**
- `count` (int): Anzahl der Einträge (default: 50)
- `category` (str, optional): Filter nach Kategorie
- `level` (str, optional): Filter nach Level

#### export_logs()

Exportiert Logs in Datei.

```python
# Als JSON exportieren
filepath = logger.export_logs(format="json")

# Als CSV exportieren
filepath = logger.export_logs(format="csv")

# Mit spezifischem Pfad
filepath = logger.export_logs(
    filepath="exports/my_logs.json",
    format="json"
)
```

**Parameter:**
- `filepath` (str, optional): Pfad zur Ausgabedatei
- `format` (str): Format ("json" oder "csv")

**Returns:** Pfad zur exportierten Datei

#### clear_logs()

Löscht alle Log-Einträge aus dem Speicher.

```python
logger.clear_logs()
```

#### set_log_level()

Setzt das Log-Level dynamisch.

```python
logger.set_log_level("DEBUG")
```

## Log-Kategorien

```python
# Verfügbare Kategorien
logger.CATEGORY_THEME_SWITCH      # Theme-Wechsel
logger.CATEGORY_CSS_INJECTION     # CSS-Injection
logger.CATEGORY_COMPONENT_RENDER  # Komponenten-Rendering
logger.CATEGORY_PERFORMANCE       # Performance-Metriken
logger.CATEGORY_ERROR             # Fehler
logger.CATEGORY_CACHE             # Cache-Ereignisse
```

## LogEntry Klasse

Jeder Log-Eintrag ist ein `LogEntry`-Objekt mit folgenden Attributen:

```python
@dataclass
class LogEntry:
    timestamp: datetime      # Zeitstempel
    level: str              # Log-Level
    category: str           # Kategorie
    message: str            # Nachricht
    user_id: Optional[str]  # Benutzer-ID
    metadata: Dict[str, Any]  # Zusätzliche Metadaten
```

## Integration mit Theme-System

### In ThemeManager

```python
from theming.theme_logger import get_theme_logger

class ThemeManager:
    def __init__(self):
        self.logger = get_theme_logger()
        # ...
    
    def set_theme(self, theme_name: str) -> None:
        old_theme = self.current_theme.name if self.current_theme else None
        
        start_time = time.perf_counter()
        # Theme wechseln...
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        self.logger.log_theme_switch(
            from_theme=old_theme,
            to_theme=theme_name,
            duration_ms=duration_ms
        )
```

### In CSSGenerator

```python
from theming.theme_logger import get_theme_logger

class CSSGenerator:
    def __init__(self, theme):
        self.theme = theme
        self.logger = get_theme_logger()
    
    def generate_full_css(self) -> str:
        start_time = time.perf_counter()
        
        css = self._generate_css()
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        css_size = len(css.encode('utf-8'))
        
        self.logger.log_css_generation(
            theme_name=self.theme.name,
            duration_ms=duration_ms,
            css_size_bytes=css_size
        )
        
        return css
```

### In Komponenten

```python
from theming.theme_logger import get_theme_logger

class Card(ShadcnComponent):
    def __init__(self, theme_manager):
        super().__init__(theme_manager)
        self.logger = get_theme_logger()
    
    def render(self, **kwargs):
        start_time = time.perf_counter()
        
        try:
            # Rendering-Logik...
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            self.logger.log_component_render(
                component_name="Card",
                duration_ms=duration_ms,
                success=True
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            self.logger.log_component_render(
                component_name="Card",
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            raise
```

## Monitoring Dashboard

### Vollständiges Dashboard

```python
from theming.monitoring_dashboard import render_monitoring_dashboard

# In Streamlit-App
render_monitoring_dashboard()
```

### Kompakte Sidebar-Ansicht

```python
from theming.monitoring_dashboard import render_compact_monitoring

# In Sidebar
render_compact_monitoring()
```

## Best Practices

### 1. Singleton-Pattern verwenden

```python
# ✅ Gut - Singleton verwenden
logger = get_theme_logger()

# ❌ Schlecht - Neue Instanz erstellen
logger = ThemeLogger()
```

### 2. Performance-Messungen

```python
import time

start = time.perf_counter()
# Operation ausführen
duration_ms = (time.perf_counter() - start) * 1000

logger.log_performance_metric("operation_name", duration_ms, "ms")
```

### 3. Fehlerbehandlung

```python
try:
    # Riskante Operation
    pass
except Exception as e:
    logger.log_error(
        "Operation fehlgeschlagen",
        exception=e,
        metadata={"context": "additional_info"}
    )
    # Fehler behandeln oder weiterwerfen
```

### 4. Kontextuelle Informationen

```python
# Füge relevante Metadaten hinzu
logger.log_theme_switch(
    from_theme="default",
    to_theme="dark",
    user_id=st.session_state.get('user_id'),
    duration_ms=duration
)
```

### 5. Log-Level angemessen wählen

```python
# DEBUG: Detaillierte Informationen
logger.logger.debug("Theme-Token abgerufen: colors.primary")

# INFO: Normale Operationen
logger.log_theme_switch("default", "dark")

# WARNING: Potenzielle Probleme
logger.logger.warning("Theme-Datei fehlt, verwende Fallback")

# ERROR: Behandelte Fehler
logger.log_error("CSS-Injection fehlgeschlagen")

# CRITICAL: Kritische Fehler
logger.logger.critical("Theme-System nicht initialisiert")
```

## Troubleshooting

### Problem: Logs werden nicht geschrieben

**Lösung:** Prüfe ob Log-Verzeichnis existiert und beschreibbar ist.

```python
import os
logger = get_theme_logger(log_dir="logs")
print(f"Log-Verzeichnis: {logger.log_dir}")
print(f"Existiert: {logger.log_dir.exists()}")
print(f"Beschreibbar: {os.access(logger.log_dir, os.W_OK)}")
```

### Problem: Zu viele Log-Einträge

**Lösung:** Erhöhe Log-Level oder lösche alte Einträge.

```python
# Log-Level erhöhen
logger.set_log_level("WARNING")

# Alte Einträge löschen
logger.clear_logs()
```

### Problem: Performance-Impact durch Logging

**Lösung:** Verwende höheres Log-Level in Produktion.

```python
# Development
logger = get_theme_logger(log_level="DEBUG")

# Production
logger = get_theme_logger(log_level="WARNING")
```

## Beispiele

### Vollständiges Beispiel

```python
import streamlit as st
from theming.theme_logger import get_theme_logger
from theming.monitoring_dashboard import render_monitoring_dashboard
import time

# Initialisiere Logger
logger = get_theme_logger(log_level="DEBUG")

# Theme-Wechsel
def switch_theme(new_theme):
    old_theme = st.session_state.get('current_theme', 'default')
    
    start = time.perf_counter()
    # Theme wechseln...
    st.session_state.current_theme = new_theme
    duration = (time.perf_counter() - start) * 1000
    
    logger.log_theme_switch(
        from_theme=old_theme,
        to_theme=new_theme,
        user_id=st.session_state.get('user_id'),
        duration_ms=duration
    )

# Komponente rendern
def render_card():
    start = time.perf_counter()
    
    try:
        st.markdown("### Card Content")
        duration = (time.perf_counter() - start) * 1000
        
        logger.log_component_render(
            component_name="Card",
            duration_ms=duration,
            success=True
        )
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        
        logger.log_component_render(
            component_name="Card",
            duration_ms=duration,
            success=False,
            error=str(e)
        )

# Monitoring Dashboard anzeigen
if st.sidebar.checkbox("Show Monitoring"):
    render_monitoring_dashboard()
```

## Siehe auch

- [Error Handling Reference](ERROR_HANDLING_REFERENCE.md)
- [Performance Optimization Guide](../docs/PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [Theme System Reference](THEME_MANAGER_REFERENCE.md)
