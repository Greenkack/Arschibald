# Theme Logging & Monitoring - Quick Reference

## 🚀 Schnellstart

```python
from theming.theme_logger import get_theme_logger
from theming.monitoring_dashboard import render_monitoring_dashboard

# Logger initialisieren
logger = get_theme_logger()

# Theme-Wechsel loggen
logger.log_theme_switch("default", "dark", user_id="user123")

# Monitoring Dashboard anzeigen
render_monitoring_dashboard()
```

## 📝 Häufige Logging-Operationen

### Theme-Wechsel

```python
logger.log_theme_switch(
    from_theme="shadcn-default",
    to_theme="shadcn-dark",
    user_id="user123",
    duration_ms=45.2
)
```

### CSS-Generierung

```python
logger.log_css_generation(
    theme_name="shadcn-dark",
    duration_ms=78.5,
    css_size_bytes=45000
)
```

### CSS-Injection

```python
logger.log_css_injection(
    theme_name="shadcn-dark",
    success=True,
    duration_ms=12.3
)
```

### Komponenten-Rendering

```python
logger.log_component_render(
    component_name="Card",
    duration_ms=23.4,
    success=True
)
```

### Performance-Metriken

```python
logger.log_performance_metric(
    metric_name="css_size",
    value=45.2,
    unit="KB",
    theme_name="shadcn-dark"
)
```

### Cache-Ereignisse

```python
logger.log_cache_event(
    event_type="theme_cache",
    cache_key="shadcn-dark",
    hit=True
)
```

### Fehler

```python
try:
    # Riskante Operation
    pass
except Exception as e:
    logger.log_error(
        "Operation fehlgeschlagen",
        exception=e
    )
```

## 📊 Statistiken abrufen

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

## 📋 Log-Einträge abrufen

```python
# Letzte 50 Einträge
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

## 💾 Logs exportieren

```python
# Als JSON
filepath = logger.export_logs(format="json")

# Als CSV
filepath = logger.export_logs(format="csv")
```

## 🎛️ Log-Level

```python
# Log-Level setzen
logger.set_log_level("DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Logs löschen
logger.clear_logs()
```

## 📊 Monitoring Dashboard

### Vollständiges Dashboard

```python
from theming.monitoring_dashboard import render_monitoring_dashboard

render_monitoring_dashboard()
```

### Kompakte Sidebar-Ansicht

```python
from theming.monitoring_dashboard import render_compact_monitoring

render_compact_monitoring()
```

## 🏷️ Log-Kategorien

```python
logger.CATEGORY_THEME_SWITCH      # Theme-Wechsel
logger.CATEGORY_CSS_INJECTION     # CSS-Injection
logger.CATEGORY_COMPONENT_RENDER  # Komponenten-Rendering
logger.CATEGORY_PERFORMANCE       # Performance-Metriken
logger.CATEGORY_ERROR             # Fehler
logger.CATEGORY_CACHE             # Cache-Ereignisse
```

## ⚡ Performance-Messung

```python
import time

start = time.perf_counter()
# Operation ausführen
duration_ms = (time.perf_counter() - start) * 1000

logger.log_performance_metric("operation", duration_ms, "ms")
```

## 🔍 Monitoring in Streamlit

```python
import streamlit as st
from theming.theme_logger import get_theme_logger
from theming.monitoring_dashboard import render_compact_monitoring

# In Sidebar
with st.sidebar:
    render_compact_monitoring()

# Oder vollständiges Dashboard in Tab
tab1, tab2 = st.tabs(["App", "Monitoring"])

with tab2:
    render_monitoring_dashboard()
```

## 💡 Best Practices

1. **Singleton verwenden**: `logger = get_theme_logger()`
2. **Performance messen**: Immer `time.perf_counter()` verwenden
3. **Fehler loggen**: Immer mit `exception=e` Parameter
4. **Metadaten hinzufügen**: Für bessere Nachvollziehbarkeit
5. **Log-Level anpassen**: DEBUG in Dev, WARNING in Prod

## 🐛 Troubleshooting

### Logs werden nicht geschrieben

```python
# Prüfe Log-Verzeichnis
print(f"Log-Dir: {logger.log_dir}")
print(f"Existiert: {logger.log_dir.exists()}")
```

### Zu viele Logs

```python
# Erhöhe Log-Level
logger.set_log_level("WARNING")

# Oder lösche alte Logs
logger.clear_logs()
```

## 📚 Weitere Ressourcen

- [Vollständige Referenz](../theming/LOGGING_SYSTEM_REFERENCE.md)
- [Error Handling Guide](ERROR_HANDLING_QUICK_REFERENCE.md)
- [Performance Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
