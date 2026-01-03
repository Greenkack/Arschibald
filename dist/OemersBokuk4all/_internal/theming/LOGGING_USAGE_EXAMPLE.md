# Theme Logging System - Verwendungsbeispiele

## Grundlegende Verwendung

### 1. Logger initialisieren

```python
from theming.theme_logger import get_theme_logger

# Singleton-Instanz verwenden (empfohlen)
logger = get_theme_logger()

# Oder mit spezifischen Einstellungen
logger = get_theme_logger(log_level="DEBUG", log_dir="logs")
```

### 2. Theme-Wechsel loggen

```python
import time

def switch_theme(from_theme: str, to_theme: str, user_id: str):
    """Theme wechseln und loggen"""
    start = time.perf_counter()
    
    # Theme-Wechsel durchführen
    # ... Theme-Wechsel-Logik ...
    
    duration_ms = (time.perf_counter() - start) * 1000
    
    logger.log_theme_switch(
        from_theme=from_theme,
        to_theme=to_theme,
        user_id=user_id,
        duration_ms=duration_ms
    )
```

### 3. CSS-Generierung loggen

```python
def generate_css(theme_name: str) -> str:
    """CSS generieren und loggen"""
    start = time.perf_counter()
    
    # CSS generieren
    css = "/* Generated CSS */"
    
    duration_ms = (time.perf_counter() - start) * 1000
    css_size = len(css.encode('utf-8'))
    
    logger.log_css_generation(
        theme_name=theme_name,
        duration_ms=duration_ms,
        css_size_bytes=css_size
    )
    
    return css
```

### 4. Komponenten-Rendering loggen

```python
def render_card(title: str, content: str):
    """Card rendern und loggen"""
    start = time.perf_counter()
    
    try:
        # Rendering-Logik
        st.markdown(f"### {title}")
        st.write(content)
        
        duration_ms = (time.perf_counter() - start) * 1000
        
        logger.log_component_render(
            component_name="Card",
            duration_ms=duration_ms,
            success=True
        )
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        
        logger.log_component_render(
            component_name="Card",
            duration_ms=duration_ms,
            success=False,
            error=str(e)
        )
        raise
```

## Integration mit Theme-System

### ThemeManager mit Logging

```python
from theming.theme_logger import get_theme_logger
import time

class ThemeManager:
    def __init__(self):
        self.logger = get_theme_logger()
        self.current_theme = None
        self.themes = {}
    
    def load_themes(self):
        """Themes laden mit Logging"""
        start = time.perf_counter()
        
        try:
            # Themes laden...
            self.themes = self._load_theme_files()
            
            duration_ms = (time.perf_counter() - start) * 1000
            
            self.logger.log_performance_metric(
                metric_name="theme_loading",
                value=duration_ms,
                unit="ms",
                metadata={"theme_count": len(self.themes)}
            )
        except Exception as e:
            self.logger.log_error(
                "Failed to load themes",
                exception=e,
                category=self.logger.CATEGORY_ERROR
            )
            raise
    
    def set_theme(self, theme_name: str, user_id: str = None):
        """Theme setzen mit Logging"""
        old_theme = self.current_theme.name if self.current_theme else None
        
        start = time.perf_counter()
        
        try:
            self.current_theme = self.themes[theme_name]
            
            duration_ms = (time.perf_counter() - start) * 1000
            
            self.logger.log_theme_switch(
                from_theme=old_theme,
                to_theme=theme_name,
                user_id=user_id,
                duration_ms=duration_ms
            )
        except KeyError:
            self.logger.log_error(
                f"Theme '{theme_name}' not found",
                category=self.logger.CATEGORY_ERROR,
                metadata={"available_themes": list(self.themes.keys())}
            )
            raise
```

### CSSGenerator mit Logging

```python
from theming.theme_logger import get_theme_logger
import time

class CSSGenerator:
    def __init__(self, theme):
        self.theme = theme
        self.logger = get_theme_logger()
    
    def generate_full_css(self) -> str:
        """CSS generieren mit Logging"""
        start = time.perf_counter()
        
        try:
            css = self._generate_css_variables()
            css += self._generate_component_styles()
            css += self._generate_utility_classes()
            
            duration_ms = (time.perf_counter() - start) * 1000
            css_size = len(css.encode('utf-8'))
            
            self.logger.log_css_generation(
                theme_name=self.theme.name,
                duration_ms=duration_ms,
                css_size_bytes=css_size
            )
            
            # Performance-Warnung bei langsamer Generierung
            if duration_ms > 100:
                self.logger.logger.warning(
                    f"CSS generation took {duration_ms:.2f}ms (target: <100ms)"
                )
            
            return css
        except Exception as e:
            self.logger.log_error(
                "CSS generation failed",
                exception=e,
                category=self.logger.CATEGORY_PERFORMANCE
            )
            raise
    
    def inject_css(self, css: str) -> bool:
        """CSS injizieren mit Logging"""
        start = time.perf_counter()
        
        try:
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            
            duration_ms = (time.perf_counter() - start) * 1000
            
            self.logger.log_css_injection(
                theme_name=self.theme.name,
                success=True,
                duration_ms=duration_ms
            )
            
            return True
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            
            self.logger.log_css_injection(
                theme_name=self.theme.name,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            
            return False
```

### Cache mit Logging

```python
from theming.theme_logger import get_theme_logger

class ThemeCache:
    def __init__(self):
        self.cache = {}
        self.logger = get_theme_logger()
    
    def get(self, key: str):
        """Wert aus Cache holen mit Logging"""
        if key in self.cache:
            self.logger.log_cache_event(
                event_type="theme_cache",
                cache_key=key,
                hit=True
            )
            return self.cache[key]
        else:
            self.logger.log_cache_event(
                event_type="theme_cache",
                cache_key=key,
                hit=False
            )
            return None
    
    def set(self, key: str, value):
        """Wert in Cache speichern"""
        self.cache[key] = value
        
        self.logger.log_performance_metric(
            metric_name="cache_size",
            value=len(self.cache),
            unit="items"
        )
```

## Streamlit-Integration

### Vollständige App mit Logging

```python
import streamlit as st
from theming.theme_logger import get_theme_logger
from theming.monitoring_dashboard import render_compact_monitoring

# Logger initialisieren
if 'logger' not in st.session_state:
    st.session_state.logger = get_theme_logger(log_level="INFO")

logger = st.session_state.logger

# Sidebar mit Monitoring
with st.sidebar:
    st.header("Theme Settings")
    
    # Theme-Selector
    theme = st.selectbox(
        "Theme",
        ["shadcn-default", "shadcn-dark", "shadcn-ocean"]
    )
    
    if theme != st.session_state.get('current_theme'):
        old_theme = st.session_state.get('current_theme', 'shadcn-default')
        st.session_state.current_theme = theme
        
        logger.log_theme_switch(
            from_theme=old_theme,
            to_theme=theme,
            user_id=st.session_state.get('user_id', 'anonymous')
        )
    
    # Kompaktes Monitoring
    st.markdown("---")
    render_compact_monitoring(logger)

# Hauptbereich
st.title("My App")

# Komponenten mit Logging
import time

start = time.perf_counter()
st.metric("Revenue", "$1,234", "+12%")
duration_ms = (time.perf_counter() - start) * 1000

logger.log_component_render(
    component_name="MetricCard",
    duration_ms=duration_ms,
    success=True
)
```

### Monitoring-Dashboard als Tab

```python
import streamlit as st
from theming.monitoring_dashboard import render_monitoring_dashboard

tab1, tab2, tab3 = st.tabs(["App", "Monitoring", "Settings"])

with tab1:
    st.write("Main app content")

with tab2:
    render_monitoring_dashboard()

with tab3:
    st.write("Settings")
```

## Performance-Monitoring

### Performance-Metriken sammeln

```python
import time
from theming.theme_logger import get_theme_logger

logger = get_theme_logger()

# CSS-Größe messen
css = generate_css()
css_size_kb = len(css.encode('utf-8')) / 1024

logger.log_performance_metric(
    metric_name="css_size",
    value=css_size_kb,
    unit="KB",
    theme_name="shadcn-dark"
)

# Rendering-Zeit messen
start = time.perf_counter()
render_component()
duration_ms = (time.perf_counter() - start) * 1000

logger.log_performance_metric(
    metric_name="component_render_time",
    value=duration_ms,
    unit="ms",
    metadata={"component": "Card"}
)

# Memory-Usage (optional)
import psutil
memory_mb = psutil.Process().memory_info().rss / 1024 / 1024

logger.log_performance_metric(
    metric_name="memory_usage",
    value=memory_mb,
    unit="MB"
)
```

## Fehlerbehandlung

### Fehler mit Context loggen

```python
from theming.theme_logger import get_theme_logger

logger = get_theme_logger()

def load_theme(theme_name: str):
    """Theme laden mit Fehlerbehandlung"""
    try:
        # Theme laden
        theme = load_theme_file(theme_name)
        return theme
    except FileNotFoundError as e:
        logger.log_error(
            f"Theme file not found: {theme_name}",
            exception=e,
            category=logger.CATEGORY_ERROR,
            metadata={
                "theme_name": theme_name,
                "search_paths": ["/themes", "/custom_themes"]
            }
        )
        # Fallback verwenden
        return load_default_theme()
    except json.JSONDecodeError as e:
        logger.log_error(
            f"Invalid theme JSON: {theme_name}",
            exception=e,
            category=logger.CATEGORY_ERROR,
            metadata={"theme_name": theme_name}
        )
        raise
```

## Statistiken und Export

### Statistiken abrufen

```python
from theming.theme_logger import get_theme_logger

logger = get_theme_logger()

# Statistiken abrufen
stats = logger.get_stats()

print(f"Total entries: {stats['total_entries']}")
print(f"Theme switches: {stats['theme_switches']}")
print(f"Errors: {stats['errors']}")
print(f"Cache hit rate: {stats['cache_hit_rate']}")
```

### Logs exportieren

```python
# Als JSON exportieren
json_file = logger.export_logs(format="json")
print(f"Logs exported to: {json_file}")

# Als CSV exportieren
csv_file = logger.export_logs(format="csv")
print(f"Logs exported to: {csv_file}")

# Mit spezifischem Pfad
custom_file = logger.export_logs(
    filepath="exports/theme_logs_2024.json",
    format="json"
)
```

### Log-Einträge filtern

```python
# Letzte 50 Einträge
entries = logger.get_recent_entries(count=50)

# Nur Theme-Wechsel
theme_switches = logger.get_recent_entries(
    count=100,
    category=logger.CATEGORY_THEME_SWITCH
)

# Nur Fehler
errors = logger.get_recent_entries(
    count=20,
    level="ERROR"
)

# Einträge durchgehen
for entry in errors:
    print(f"{entry.timestamp}: {entry.message}")
    if entry.metadata:
        print(f"  Metadata: {entry.metadata}")
```

## Best Practices

### 1. Singleton verwenden

```python
# ✅ Gut
logger = get_theme_logger()

# ❌ Schlecht
logger = ThemeLogger()
```

### 2. Performance immer messen

```python
import time

start = time.perf_counter()
# Operation
duration_ms = (time.perf_counter() - start) * 1000

logger.log_performance_metric("operation", duration_ms, "ms")
```

### 3. Fehler mit Exception loggen

```python
try:
    risky_operation()
except Exception as e:
    logger.log_error("Operation failed", exception=e)
```

### 4. Kontextuelle Metadaten hinzufügen

```python
logger.log_theme_switch(
    from_theme="default",
    to_theme="dark",
    user_id=user_id,
    duration_ms=duration
)
```

### 5. Log-Level in Produktion anpassen

```python
# Development
logger = get_theme_logger(log_level="DEBUG")

# Production
logger = get_theme_logger(log_level="WARNING")
```
