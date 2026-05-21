# Design Document

## Overview

Dieses Design beschreibt die Architektur und Implementierung eines vollständigen shadcn/ui-Design-Systems für die Streamlit-Anwendung. Das System basiert auf drei Säulen:

1. **Theme System**: Zentrale Verwaltung von Design-Tokens und Themes
2. **Component Library**: Wiederverwendbare, gestylete Komponenten
3. **CSS Injection Layer**: Globales Styling für native Streamlit-Komponenten

Die Implementierung erfolgt nicht-invasiv, sodass bestehende Funktionalität erhalten bleibt und das neue Design optional aktiviert werden kann.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit App                         │
│                          (gui.py)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─────────────────────────────────────┐
                         │                                     │
                ┌────────▼────────┐                  ┌────────▼────────┐
                │  Theme System   │                  │  Component Lib  │
                │                 │                  │                 │
                │ - Theme Manager │                  │ - Card          │
                │ - Token Store   │                  │ - Alert         │
                │ - CSS Generator │                  │ - Badge         │
                └────────┬────────┘                  │ - Table         │
                         │                           │ - Metric        │
                         │                           │ - ...           │
                         │                           └────────┬────────┘
                         │                                    │
                ┌────────▼────────────────────────────────────▼────────┐
                │              CSS Injection Layer                     │
                │                                                      │
                │  - Global Styles                                    │
                │  - Component Overrides                              │
                │  - Theme Variables                                  │
                └──────────────────────────────────────────────────────┘
```

### Module Structure

```
theming/
├── __init__.py
├── theme_manager.py          # Zentrale Theme-Verwaltung
├── theme_tokens.py           # Design-Token-Definitionen
├── css_generator.py          # CSS-Generierung aus Tokens
├── theme_selector_ui.py      # UI für Theme-Auswahl
└── themes/
    ├── shadcn_default.json
    ├── shadcn_dark.json
    ├── shadcn_ocean.json
    ├── shadcn_forest.json
    └── shadcn_sunset.json

components/
├── __init__.py
├── shadcn_base.py           # Basis-Klasse für alle Komponenten
├── card.py                  # Card-Komponente
├── alert.py                 # Alert/AlertDialog
├── badge.py                 # Badge-Komponente
├── table.py                 # Erweiterte Tabelle
├── metric_card.py           # KPI-Metriken
├── accordion.py             # Accordion
├── breadcrumb.py            # Breadcrumb-Navigation
├── dropdown.py              # Dropdown-Menu
├── popover.py               # Popover
├── progress.py              # Progress-Bar
├── skeleton.py              # Skeleton-Loader
├── pagination.py            # Pagination
└── form_components.py       # Erweiterte Form-Inputs

utils/
├── shadcn_chart_theme.py    # Chart-Styling für Plotly
├── shadcn_sidebar.py        # Sidebar-Styling
└── shadcn_animations.py     # Animation-Utilities

tools/
└── theme_generator.py       # Theme-Generator-Tool
```

## Components and Interfaces

### 1. Theme Manager

**Verantwortlichkeit**: Zentrale Verwaltung von Themes und Design-Tokens

```python
class ThemeManager:
    """Verwaltet Themes und Design-Tokens"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.load_themes()
    
    def load_themes(self) -> None:
        """Lädt alle verfügbaren Themes aus dem themes/ Verzeichnis"""
        pass
    
    def get_theme(self, theme_name: str) -> Theme:
        """Gibt ein Theme nach Namen zurück"""
        pass
    
    def set_theme(self, theme_name: str) -> None:
        """Setzt das aktuelle Theme"""
        pass
    
    def get_token(self, token_path: str) -> str:
        """Gibt einen Design-Token-Wert zurück (z.B. 'colors.primary')"""
        pass
    
    def generate_css(self) -> str:
        """Generiert CSS aus dem aktuellen Theme"""
        pass
```

### 2. Theme Data Structure

```python
@dataclass
class Theme:
    """Repräsentiert ein vollständiges Theme"""
    name: str
    display_name: str
    colors: ColorTokens
    typography: TypographyTokens
    spacing: SpacingTokens
    shadows: ShadowTokens
    borders: BorderTokens
    animations: AnimationTokens

@dataclass
class ColorTokens:
    """Farb-Tokens"""
    # Base colors
    background: str
    foreground: str
    
    # Component colors
    primary: str
    primary_foreground: str
    secondary: str
    secondary_foreground: str
    accent: str
    accent_foreground: str
    
    # Semantic colors
    success: str
    warning: str
    error: str
    info: str
    
    # UI colors
    muted: str
    muted_foreground: str
    border: str
    input: str
    ring: str
    
    # Chart colors
    chart_1: str
    chart_2: str
    chart_3: str
    chart_4: str
    chart_5: str

@dataclass
class TypographyTokens:
    """Typografie-Tokens"""
    font_family: str
    font_family_mono: str
    
    # Font sizes
    font_size_xs: str
    font_size_sm: str
    font_size_base: str
    font_size_lg: str
    font_size_xl: str
    font_size_2xl: str
    
    # Font weights
    font_weight_normal: int
    font_weight_medium: int
    font_weight_semibold: int
    font_weight_bold: int
    
    # Line heights
    line_height_tight: float
    line_height_normal: float
    line_height_relaxed: float

@dataclass
class SpacingTokens:
    """Abstands-Tokens"""
    spacing_0: str
    spacing_1: str  # 0.25rem
    spacing_2: str  # 0.5rem
    spacing_3: str  # 0.75rem
    spacing_4: str  # 1rem
    spacing_6: str  # 1.5rem
    spacing_8: str  # 2rem
    spacing_12: str # 3rem
    spacing_16: str # 4rem

@dataclass
class ShadowTokens:
    """Schatten-Tokens"""
    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    shadow_xl: str

@dataclass
class BorderTokens:
    """Border-Tokens"""
    border_width: str
    border_radius_sm: str
    border_radius_md: str
    border_radius_lg: str
    border_radius_full: str

@dataclass
class AnimationTokens:
    """Animations-Tokens"""
    transition_fast: str    # 150ms
    transition_base: str    # 200ms
    transition_slow: str    # 300ms
    easing_default: str     # cubic-bezier(0.4, 0, 0.2, 1)
```

### 3. CSS Generator

**Verantwortlichkeit**: Generiert CSS aus Theme-Tokens

```python
class CSSGenerator:
    """Generiert CSS aus Theme-Tokens"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
    
    def generate_css_variables(self) -> str:
        """Generiert CSS Custom Properties (Variablen)"""
        pass
    
    def generate_component_styles(self) -> str:
        """Generiert Styles für Streamlit-Komponenten"""
        pass
    
    def generate_utility_classes(self) -> str:
        """Generiert Utility-Klassen (ähnlich Tailwind)"""
        pass
    
    def generate_full_css(self) -> str:
        """Generiert vollständiges CSS"""
        pass
```

### 4. Component Base Class

**Verantwortlichkeit**: Basis-Klasse für alle shadcn-Komponenten

```python
class ShadcnComponent:
    """Basis-Klasse für alle shadcn-Komponenten"""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme = theme_manager
    
    def get_token(self, path: str) -> str:
        """Shortcut für Theme-Token-Zugriff"""
        return self.theme.get_token(path)
    
    def render(self, **kwargs) -> None:
        """Rendert die Komponente (muss überschrieben werden)"""
        raise NotImplementedError
```

### 5. Card Component

```python
class Card(ShadcnComponent):
    """shadcn/ui Card-Komponente"""
    
    def render(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        footer: Optional[str] = None,
        variant: Literal["default", "outlined", "elevated"] = "default",
        icon: Optional[str] = None,
        badge: Optional[str] = None
    ) -> None:
        """Rendert eine Card"""
        
        # CSS für Card
        card_css = f"""
        <style>
        .shadcn-card {{
            background: {self.get_token('colors.background')};
            border: 1px solid {self.get_token('colors.border')};
            border-radius: {self.get_token('borders.border_radius_lg')};
            padding: {self.get_token('spacing.spacing_6')};
            transition: all {self.get_token('animations.transition_base')};
        }}
        .shadcn-card:hover {{
            box-shadow: {self.get_token('shadows.shadow_md')};
        }}
        </style>
        """
        
        st.markdown(card_css, unsafe_allow_html=True)
        
        # HTML für Card
        # ... Implementation
```

### 6. Chart Theme

```python
def apply_chart_theme(fig, theme_manager: ThemeManager) -> go.Figure:
    """Wendet shadcn/ui-Theme auf Plotly-Chart an"""
    
    theme = theme_manager.current_theme
    
    fig.update_layout(
        font=dict(
            family=theme.typography.font_family,
            size=14,
            color=theme.colors.foreground
        ),
        plot_bgcolor=theme.colors.background,
        paper_bgcolor=theme.colors.background,
        margin=dict(l=70, r=40, t=60, b=60),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=theme.colors.muted,
            font_size=13,
            font_family=theme.typography.font_family
        )
    )
    
    # Update traces mit Theme-Farben
    colors = [
        theme.colors.chart_1,
        theme.colors.chart_2,
        theme.colors.chart_3,
        theme.colors.chart_4,
        theme.colors.chart_5
    ]
    
    for i, trace in enumerate(fig.data):
        color = colors[i % len(colors)]
        
        if trace.type == 'scatter':
            trace.update(
                line=dict(color=color, width=3, shape='spline'),
                fillcolor=f"rgba({color}, 0.1)" if trace.fill else None
            )
        elif trace.type == 'bar':
            trace.update(marker=dict(color=color))
    
    return fig
```

## Data Models

### Theme JSON Structure

```json
{
  "name": "shadcn-default",
  "display_name": "shadcn/ui Default",
  "colors": {
    "background": "#ffffff",
    "foreground": "#0a0a0a",
    "primary": "#18181b",
    "primary_foreground": "#fafafa",
    "secondary": "#f4f4f5",
    "secondary_foreground": "#18181b",
    "accent": "#f4f4f5",
    "accent_foreground": "#18181b",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "muted": "#f4f4f5",
    "muted_foreground": "#71717a",
    "border": "#e4e4e7",
    "input": "#e4e4e7",
    "ring": "#18181b",
    "chart_1": "#38bdf8",
    "chart_2": "#34d399",
    "chart_3": "#f87171",
    "chart_4": "#fbbf24",
    "chart_5": "#a78bfa"
  },
  "typography": {
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "font_family_mono": "'Fira Code', 'Courier New', monospace",
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
    "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
  },
  "borders": {
    "border_width": "1px",
    "border_radius_sm": "0.25rem",
    "border_radius_md": "0.375rem",
    "border_radius_lg": "0.5rem",
    "border_radius_full": "9999px"
  },
  "animations": {
    "transition_fast": "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    "transition_base": "200ms cubic-bezier(0.4, 0, 0.2, 1)",
    "transition_slow": "300ms cubic-bezier(0.4, 0, 0.2, 1)",
    "easing_default": "cubic-bezier(0.4, 0, 0.2, 1)"
  }
}
```

## Error Handling

### Theme Loading Errors

```python
try:
    theme_manager.load_themes()
except FileNotFoundError:
    st.warning("Theme-Dateien nicht gefunden. Verwende Fallback-Theme.")
    theme_manager.use_fallback_theme()
except json.JSONDecodeError as e:
    st.error(f"Fehler beim Parsen der Theme-Datei: {e}")
    theme_manager.use_fallback_theme()
```

### CSS Injection Errors

```python
try:
    css = css_generator.generate_full_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Fehler beim Injizieren von CSS: {e}")
    # App läuft weiter mit Standard-Streamlit-Styling
```

### Component Rendering Errors

```python
try:
    card.render(title="Test", content="Content")
except Exception as e:
    st.error(f"Fehler beim Rendern der Komponente: {e}")
    # Fallback auf native Streamlit-Komponente
    st.container()
```

## Testing Strategy

### Unit Tests

1. **Theme Manager Tests**
   - Test: Theme laden und abrufen
   - Test: Token-Zugriff
   - Test: Theme-Wechsel
   - Test: Fallback bei fehlenden Themes

2. **CSS Generator Tests**
   - Test: CSS-Variablen-Generierung
   - Test: Component-Styles-Generierung
   - Test: Vollständiges CSS

3. **Component Tests**
   - Test: Card-Rendering mit verschiedenen Varianten
   - Test: Alert-Rendering
   - Test: Badge-Rendering
   - Test: Alle Komponenten mit verschiedenen Props

### Integration Tests

1. **Theme System Integration**
   - Test: Theme-Wechsel in laufender App
   - Test: CSS-Injection beim App-Start
   - Test: Persistierung der Theme-Auswahl

2. **Component Integration**
   - Test: Komponenten mit Theme-Manager
   - Test: Komponenten in verschiedenen Themes
   - Test: Komponenten-Interaktion

### Visual Regression Tests

1. **Screenshot-Tests**
   - Test: Alle Komponenten in allen Themes
   - Test: Responsive Layouts
   - Test: Dark Mode vs. Light Mode

### Performance Tests

1. **CSS Injection Performance**
   - Test: Zeit für CSS-Generierung
   - Test: Zeit für CSS-Injection
   - Ziel: < 100ms

2. **Component Rendering Performance**
   - Test: Zeit für Component-Rendering
   - Ziel: < 50ms pro Komponente

## Implementation Notes

### CSS Injection Strategy

```python
def inject_shadcn_css(theme_manager: ThemeManager):
    """Injiziert shadcn/ui CSS in die App"""
    
    # Nur einmal beim App-Start injizieren
    if 'shadcn_css_injected' not in st.session_state:
        css = theme_manager.generate_css()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.session_state.shadcn_css_injected = True
```

### Theme Switching

```python
def switch_theme(theme_name: str, theme_manager: ThemeManager):
    """Wechselt das Theme"""
    
    theme_manager.set_theme(theme_name)
    
    # CSS neu generieren und injizieren
    css = theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Session State aktualisieren
    st.session_state.current_theme = theme_name
    
    # Optional: In Local Storage speichern
    st.components.v1.html(f"""
        <script>
        localStorage.setItem('shadcn_theme', '{theme_name}');
        </script>
    """, height=0)
```

### Backward Compatibility

```python
# Feature Flag in config oder Session State
if st.session_state.get('enable_shadcn_ui', True):
    # Neues shadcn/ui Design
    inject_shadcn_css(theme_manager)
    card = Card(theme_manager)
    card.render(title="Test")
else:
    # Original Streamlit Design
    st.container()
```

### Integration mit bestehender App

```python
# In gui.py
from theming import ThemeManager, inject_shadcn_css

# Theme System initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')
    inject_shadcn_css(st.session_state.theme_manager)

# Theme Selector in Sidebar
with st.sidebar:
    from theming import render_theme_selector
    render_theme_selector(st.session_state.theme_manager)
```

## Migration Strategy

### Phase 1: Infrastruktur (Woche 1)

- Theme System implementieren
- CSS Generator implementieren
- Basis-CSS für Streamlit-Komponenten

### Phase 2: Basis-Komponenten (Woche 2)

- Card, Alert, Badge
- Button-Styling
- Input-Styling

### Phase 3: Erweiterte Komponenten (Woche 3)

- Table, Accordion, Dropdown
- Chart-Styling
- Sidebar-Styling

### Phase 4: Integration (Woche 4)

- Integration in gui.py
- Migration bestehender Module
- Testing und Bugfixes

### Phase 5: Polish (Woche 5)

- Animations und Transitions
- Dark Mode
- Performance-Optimierung
- Dokumentation

## Advanced Features Design

### Error Handling System

```python
class ThemeError(Exception):
    """Basis-Exception für Theme-Fehler"""
    pass

class ThemeLoadError(ThemeError):
    """Theme konnte nicht geladen werden"""
    pass

class ThemeValidationError(ThemeError):
    """Theme-Validierung fehlgeschlagen"""
    pass

class CSSInjectionError(ThemeError):
    """CSS-Injection fehlgeschlagen"""
    pass

class ErrorHandler:
    """Zentraler Error Handler für Theme-System"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_count = 0
        self.last_errors = []
    
    def handle_theme_load_error(self, theme_name: str, error: Exception) -> Theme:
        """Behandelt Theme-Load-Fehler und gibt Fallback zurück"""
        self.logger.error(f"Failed to load theme '{theme_name}': {error}")
        self.error_count += 1
        self.last_errors.append({
            'type': 'theme_load',
            'theme': theme_name,
            'error': str(error),
            'timestamp': datetime.now()
        })
        
        st.warning(f"⚠️ Theme '{theme_name}' konnte nicht geladen werden. Verwende Fallback-Theme.")
        
        return self.get_fallback_theme()
    
    def handle_css_injection_error(self, error: Exception) -> None:
        """Behandelt CSS-Injection-Fehler"""
        self.logger.error(f"CSS injection failed: {error}")
        st.error("❌ CSS konnte nicht geladen werden. App läuft mit Standard-Styling.")
    
    def handle_component_error(self, component_name: str, error: Exception) -> None:
        """Behandelt Komponenten-Rendering-Fehler"""
        self.logger.error(f"Component '{component_name}' failed: {error}")
        st.warning(f"⚠️ Komponente '{component_name}' konnte nicht gerendert werden.")
    
    def get_error_report(self) -> Dict[str, Any]:
        """Gibt Error-Report zurück"""
        return {
            'total_errors': self.error_count,
            'recent_errors': self.last_errors[-10:],
            'error_types': self._count_error_types()
        }
```

### Logging System

```python
class ThemeLogger:
    """Spezialisierter Logger für Theme-System"""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger("shadcn_theme")
        self.logger.setLevel(getattr(logging, log_level))
        
        # File Handler
        fh = logging.FileHandler('logs/theme_system.log')
        fh.setLevel(logging.DEBUG)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_theme_switch(self, from_theme: str, to_theme: str, user_id: Optional[str] = None):
        """Loggt Theme-Wechsel"""
        self.logger.info(f"Theme switch: {from_theme} -> {to_theme} (user: {user_id})")
    
    def log_css_generation(self, theme_name: str, duration_ms: float):
        """Loggt CSS-Generierung"""
        self.logger.debug(f"CSS generated for '{theme_name}' in {duration_ms:.2f}ms")
    
    def log_component_render(self, component_name: str, duration_ms: float):
        """Loggt Komponenten-Rendering"""
        self.logger.debug(f"Component '{component_name}' rendered in {duration_ms:.2f}ms")
```

### Caching System

```python
class ThemeCache:
    """Cache für Theme-Daten und generiertes CSS"""
    
    def __init__(self):
        self.theme_cache: Dict[str, Theme] = {}
        self.css_cache: Dict[str, str] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Holt Theme aus Cache"""
        if theme_name in self.theme_cache:
            self.cache_hits += 1
            return self.theme_cache[theme_name]
        self.cache_misses += 1
        return None
    
    def set_theme(self, theme_name: str, theme: Theme) -> None:
        """Speichert Theme im Cache"""
        self.theme_cache[theme_name] = theme
    
    def get_css(self, theme_name: str) -> Optional[str]:
        """Holt CSS aus Cache"""
        if theme_name in self.css_cache:
            self.cache_hits += 1
            return self.css_cache[theme_name]
        self.cache_misses += 1
        return None
    
    def set_css(self, theme_name: str, css: str) -> None:
        """Speichert CSS im Cache"""
        self.css_cache[theme_name] = css
    
    def invalidate(self, theme_name: Optional[str] = None) -> None:
        """Invalidiert Cache"""
        if theme_name:
            self.theme_cache.pop(theme_name, None)
            self.css_cache.pop(theme_name, None)
        else:
            self.theme_cache.clear()
            self.css_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_themes': len(self.theme_cache),
            'cached_css': len(self.css_cache)
        }
```

### Theme Validation

```python
from jsonschema import validate, ValidationError

THEME_SCHEMA = {
    "type": "object",
    "required": ["name", "display_name", "colors", "typography"],
    "properties": {
        "name": {"type": "string", "pattern": "^[a-z0-9-]+$"},
        "display_name": {"type": "string"},
        "colors": {
            "type": "object",
            "required": ["background", "foreground", "primary"],
            "properties": {
                "background": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                "foreground": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                "primary": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                # ... weitere Farben
            }
        },
        "typography": {
            "type": "object",
            "required": ["font_family", "font_size_base"],
            "properties": {
                "font_family": {"type": "string"},
                "font_size_base": {"type": "string"},
                # ... weitere Typography-Properties
            }
        }
    }
}

class ThemeValidator:
    """Validiert Theme-Dateien"""
    
    def __init__(self, schema: Dict = THEME_SCHEMA):
        self.schema = schema
    
    def validate_theme(self, theme_data: Dict) -> Tuple[bool, List[str]]:
        """Validiert Theme-Daten gegen Schema"""
        errors = []
        
        try:
            validate(instance=theme_data, schema=self.schema)
        except ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, errors
        
        # Zusätzliche Validierungen
        errors.extend(self._validate_colors(theme_data.get('colors', {})))
        errors.extend(self._validate_typography(theme_data.get('typography', {})))
        
        return len(errors) == 0, errors
    
    def _validate_colors(self, colors: Dict) -> List[str]:
        """Validiert Farb-Werte"""
        errors = []
        
        for key, value in colors.items():
            if not self._is_valid_color(value):
                errors.append(f"Invalid color value for '{key}': {value}")
        
        return errors
    
    def _is_valid_color(self, color: str) -> bool:
        """Prüft ob Farbe gültig ist (Hex, RGB, RGBA)"""
        import re
        
        hex_pattern = r'^#[0-9A-Fa-f]{6}$'
        rgb_pattern = r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
        rgba_pattern = r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$'
        
        return bool(
            re.match(hex_pattern, color) or
            re.match(rgb_pattern, color) or
            re.match(rgba_pattern, color)
        )
    
    def _validate_typography(self, typography: Dict) -> List[str]:
        """Validiert Typography-Werte"""
        errors = []
        
        # Prüfe Font-Sizes
        for key, value in typography.items():
            if 'font_size' in key:
                if not value.endswith('rem') and not value.endswith('px'):
                    errors.append(f"Invalid font size unit for '{key}': {value}")
        
        return errors
```

### Hot Reload System

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ThemeFileHandler(FileSystemEventHandler):
    """Handler für Theme-Datei-Änderungen"""
    
    def __init__(self, theme_manager: ThemeManager, callback: Callable):
        self.theme_manager = theme_manager
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        """Wird aufgerufen wenn Datei geändert wird"""
        if event.src_path.endswith('.json'):
            # Debounce: Ignoriere mehrfache Events innerhalb 1 Sekunde
            now = time.time()
            if event.src_path in self.last_modified:
                if now - self.last_modified[event.src_path] < 1.0:
                    return
            
            self.last_modified[event.src_path] = now
            
            # Lade Theme neu
            theme_name = Path(event.src_path).stem
            try:
                self.theme_manager.reload_theme(theme_name)
                self.callback(theme_name)
                st.toast(f"✅ Theme '{theme_name}' neu geladen", icon="🔄")
            except Exception as e:
                st.error(f"❌ Fehler beim Laden von '{theme_name}': {e}")

class HotReloadManager:
    """Verwaltet Hot Reload für Theme-Dateien"""
    
    def __init__(self, theme_manager: ThemeManager, watch_dir: str):
        self.theme_manager = theme_manager
        self.watch_dir = watch_dir
        self.observer = None
    
    def start(self, callback: Callable) -> None:
        """Startet File Watcher"""
        event_handler = ThemeFileHandler(self.theme_manager, callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_dir, recursive=False)
        self.observer.start()
    
    def stop(self) -> None:
        """Stoppt File Watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
```

### State Management

```python
class ThemeStateManager:
    """Verwaltet Theme-State über verschiedene Speicher-Backends"""
    
    def __init__(self):
        self.backends = {
            'session': SessionStateBackend(),
            'local_storage': LocalStorageBackend(),
            'database': DatabaseBackend()
        }
    
    def save_theme_preference(
        self,
        user_id: str,
        theme_name: str,
        backends: List[str] = ['session', 'local_storage']
    ) -> None:
        """Speichert Theme-Präferenz in mehreren Backends"""
        for backend_name in backends:
            backend = self.backends.get(backend_name)
            if backend:
                backend.save(user_id, theme_name)
    
    def load_theme_preference(
        self,
        user_id: str,
        backends: List[str] = ['session', 'local_storage', 'database']
    ) -> Optional[str]:
        """Lädt Theme-Präferenz aus Backends (in Reihenfolge)"""
        for backend_name in backends:
            backend = self.backends.get(backend_name)
            if backend:
                theme_name = backend.load(user_id)
                if theme_name:
                    return theme_name
        return None

class SessionStateBackend:
    """Session State Backend"""
    
    def save(self, user_id: str, theme_name: str) -> None:
        st.session_state[f'theme_{user_id}'] = theme_name
    
    def load(self, user_id: str) -> Optional[str]:
        return st.session_state.get(f'theme_{user_id}')

class LocalStorageBackend:
    """Browser Local Storage Backend"""
    
    def save(self, user_id: str, theme_name: str) -> None:
        st.components.v1.html(f"""
            <script>
            localStorage.setItem('shadcn_theme_{user_id}', '{theme_name}');
            </script>
        """, height=0)
    
    def load(self, user_id: str) -> Optional[str]:
        # Wird via JavaScript beim App-Start geladen
        return st.session_state.get(f'ls_theme_{user_id}')

class DatabaseBackend:
    """Datenbank Backend"""
    
    def __init__(self):
        self.db = database.get_connection()
    
    def save(self, user_id: str, theme_name: str) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO user_preferences (user_id, theme_name) VALUES (?, ?)",
            (user_id, theme_name)
        )
        self.db.commit()
    
    def load(self, user_id: str) -> Optional[str]:
        result = self.db.execute(
            "SELECT theme_name FROM user_preferences WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return result[0] if result else None
```

### Analytics System

```python
class ThemeAnalytics:
    """Sammelt Analytics-Daten für Theme-System"""
    
    def __init__(self):
        self.events = []
    
    def track_theme_switch(self, user_id: str, from_theme: str, to_theme: str):
        """Trackt Theme-Wechsel"""
        self.events.append({
            'type': 'theme_switch',
            'user_id': user_id,
            'from_theme': from_theme,
            'to_theme': to_theme,
            'timestamp': datetime.now()
        })
    
    def track_component_usage(self, component_name: str, user_id: str):
        """Trackt Komponenten-Nutzung"""
        self.events.append({
            'type': 'component_usage',
            'component': component_name,
            'user_id': user_id,
            'timestamp': datetime.now()
        })
    
    def track_performance(self, metric_name: str, value: float, theme_name: str):
        """Trackt Performance-Metriken"""
        self.events.append({
            'type': 'performance',
            'metric': metric_name,
            'value': value,
            'theme': theme_name,
            'timestamp': datetime.now()
        })
    
    def get_theme_usage_stats(self) -> Dict[str, int]:
        """Gibt Theme-Nutzungs-Statistiken zurück"""
        theme_counts = {}
        for event in self.events:
            if event['type'] == 'theme_switch':
                theme = event['to_theme']
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        return theme_counts
    
    def get_component_usage_stats(self) -> Dict[str, int]:
        """Gibt Komponenten-Nutzungs-Statistiken zurück"""
        component_counts = {}
        for event in self.events:
            if event['type'] == 'component_usage':
                component = event['component']
                component_counts[component] = component_counts.get(component, 0) + 1
        return component_counts
    
    def export_to_csv(self, filepath: str) -> None:
        """Exportiert Analytics-Daten als CSV"""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            if not self.events:
                return
            
            writer = csv.DictWriter(f, fieldnames=self.events[0].keys())
            writer.writeheader()
            writer.writerows(self.events)
```

### Security Layer

```python
import bleach
from html import escape

class ThemeSecurityManager:
    """Sicherheits-Layer für Theme-System"""
    
    ALLOWED_CSS_PROPERTIES = [
        'color', 'background-color', 'font-family', 'font-size',
        'padding', 'margin', 'border', 'border-radius',
        'box-shadow', 'transition', 'transform'
    ]
    
    def sanitize_theme_data(self, theme_data: Dict) -> Dict:
        """Sanitized Theme-Daten"""
        sanitized = {}
        
        for key, value in theme_data.items():
            if isinstance(value, dict):
                sanitized[key] = self.sanitize_theme_data(value)
            elif isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def sanitize_string(self, value: str) -> str:
        """Sanitized String-Werte"""
        # Entferne potentiell gefährliche Zeichen
        return escape(value)
    
    def sanitize_css(self, css: str) -> str:
        """Sanitized CSS-Code"""
        # Entferne gefährliche CSS-Properties
        lines = css.split('\n')
        safe_lines = []
        
        for line in lines:
            if ':' in line:
                prop = line.split(':')[0].strip()
                if prop in self.ALLOWED_CSS_PROPERTIES:
                    safe_lines.append(line)
            else:
                safe_lines.append(line)
        
        return '\n'.join(safe_lines)
    
    def validate_file_upload(self, file) -> Tuple[bool, str]:
        """Validiert hochgeladene Theme-Datei"""
        # Prüfe Dateigröße
        if file.size > 1024 * 1024:  # 1MB
            return False, "Datei zu groß (max. 1MB)"
        
        # Prüfe Dateiendung
        if not file.name.endswith('.json'):
            return False, "Nur JSON-Dateien erlaubt"
        
        # Prüfe JSON-Inhalt
        try:
            data = json.loads(file.read())
            file.seek(0)  # Reset für weiteres Lesen
        except json.JSONDecodeError:
            return False, "Ungültiges JSON-Format"
        
        return True, "OK"
```

## Performance Optimization Strategies

### CSS Minification

```python
def minify_css(css: str) -> str:
    """Minified CSS für Produktion"""
    # Entferne Kommentare
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Entferne Whitespace
    css = re.sub(r'\s+', ' ', css)
    
    # Entferne Whitespace um Sonderzeichen
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    
    return css.strip()
```

### Lazy Loading

```python
def lazy_load_component(component_class: Type[ShadcnComponent], **kwargs):
    """Lädt Komponente nur wenn sichtbar"""
    
    # Placeholder während Komponente lädt
    placeholder = st.empty()
    
    # Intersection Observer via JavaScript
    is_visible = st.components.v1.html("""
        <script>
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    window.parent.postMessage({type: 'visible'}, '*');
                }
            });
        });
        observer.observe(document.body);
        </script>
    """, height=0)
    
    # Rendere Komponente nur wenn sichtbar
    if is_visible:
        with placeholder:
            component = component_class(**kwargs)
            component.render()
```

### Performance Monitoring

```python
class PerformanceMonitor:
    """Überwacht Performance-Metriken"""
    
    def __init__(self):
        self.metrics = []
    
    @contextmanager
    def measure(self, operation: str):
        """Context Manager für Performance-Messung"""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = (time.perf_counter() - start) * 1000  # ms
            self.metrics.append({
                'operation': operation,
                'duration_ms': duration,
                'timestamp': datetime.now()
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Performance-Statistiken zurück"""
        if not self.metrics:
            return {}
        
        durations = [m['duration_ms'] for m in self.metrics]
        
        return {
            'count': len(self.metrics),
            'avg_ms': sum(durations) / len(durations),
            'min_ms': min(durations),
            'max_ms': max(durations),
            'total_ms': sum(durations)
        }

# Usage
perf_monitor = PerformanceMonitor()

with perf_monitor.measure('css_generation'):
    css = css_generator.generate_full_css()

with perf_monitor.measure('component_render'):
    card.render(title="Test")

st.write(perf_monitor.get_stats())
```
