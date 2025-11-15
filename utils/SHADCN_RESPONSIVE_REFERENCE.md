# shadcn/ui Responsive Design System - Reference

## Overview

Das Responsive Design System bietet vollständige Mobile-, Tablet- und Desktop-Unterstützung für Streamlit-Apps mit shadcn/ui-Styling.

## Features

- ✅ Media Queries für Breakpoints (mobile, tablet, desktop)
- ✅ Kollabierbare Sidebar für Mobile
- ✅ Gestapelte Layouts für Mobile
- ✅ Touch-freundliche Button-Größen (min. 44px)
- ✅ Verhindert horizontales Scrollen
- ✅ Mobile-First Approach
- ✅ Touch-optimierte Komponenten
- ✅ Responsive Grid & Flexbox Layouts
- ✅ Utility Classes

## Breakpoints

```python
BREAKPOINTS = {
    'mobile': 0-767px,
    'tablet': 768-1023px,
    'desktop': 1024px+
}
```

## Quick Start

### 1. Basis-Integration

```python
import streamlit as st
from utils.shadcn_responsive import inject_responsive_design

# CSS injizieren
inject_responsive_design()

# App Content
st.title("Responsive App")
```

### 2. Mit Sidebar Toggle

```python
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle
)

# CSS injizieren
inject_responsive_design()

# Sidebar Toggle für Mobile
render_mobile_sidebar_toggle()

# Sidebar Content
with st.sidebar:
    st.write("Sidebar Content")
```

### 3. Responsive Columns

```python
from utils.shadcn_responsive import responsive_columns

# Erstellt 3 Spalten auf Desktop, stackt auf Mobile
cols = responsive_columns(3)

with cols[0]:
    st.write("Column 1")
with cols[1]:
    st.write("Column 2")
with cols[2]:
    st.write("Column 3")
```

### 4. Responsive Container

```python
from utils.shadcn_responsive import responsive_container

# Container mit max-width
with responsive_container('tablet'):
    st.write("Zentrierter Content mit max-width: 768px")
```

## API Reference

### ResponsiveDesignSystem

Hauptklasse für Responsive Design Management.

```python
from utils.shadcn_responsive import ResponsiveDesignSystem

system = ResponsiveDesignSystem()
```

#### Methods

##### `generate_responsive_css() -> str`

Generiert vollständiges Responsive CSS.

```python
css = system.generate_responsive_css()
```

##### `inject_responsive_css()`

Injiziert Responsive CSS in die App.

```python
system.inject_responsive_css()
```

##### `render_sidebar_toggle()`

Rendert Sidebar Toggle Button für Mobile.

```python
system.render_sidebar_toggle()
```

##### `get_current_breakpoint() -> str`

Ermittelt aktuellen Breakpoint.

```python
breakpoint = system.get_current_breakpoint()
# Returns: 'mobile', 'tablet', oder 'desktop'
```

##### `is_mobile() -> bool`

Prüft ob Mobile Viewport.

```python
if system.is_mobile():
    st.write("Mobile View")
```

##### `is_tablet() -> bool`

Prüft ob Tablet Viewport.

```python
if system.is_tablet():
    st.write("Tablet View")
```

##### `is_desktop() -> bool`

Prüft ob Desktop Viewport.

```python
if system.is_desktop():
    st.write("Desktop View")
```

### Convenience Functions

#### `inject_responsive_design()`

Schnelle Integration ohne Klassen-Instanz.

```python
from utils.shadcn_responsive import inject_responsive_design

inject_responsive_design()
```

#### `render_mobile_sidebar_toggle()`

Rendert Sidebar Toggle ohne Klassen-Instanz.

```python
from utils.shadcn_responsive import render_mobile_sidebar_toggle

render_mobile_sidebar_toggle()
```

#### `responsive_columns(num_columns, mobile_stack=True)`

Erstellt responsive Columns.

**Parameters:**
- `num_columns` (int): Anzahl Spalten auf Desktop
- `mobile_stack` (bool): Stacken auf Mobile (default: True)

```python
from utils.shadcn_responsive import responsive_columns

# 4 Spalten auf Desktop, 2 auf Tablet, 1 auf Mobile
cols = responsive_columns(4)
```

#### `responsive_container(max_width='desktop')`

Erstellt Container mit max-width.

**Parameters:**
- `max_width` (str): 'mobile', 'tablet', oder 'desktop'

```python
from utils.shadcn_responsive import responsive_container

with responsive_container('tablet'):
    st.write("Content")
```

## CSS Classes

### Layout Classes

```css
/* Grid Layouts */
.responsive-grid          /* Basis Grid */
.responsive-grid-2        /* 2-Spalten Grid */
.responsive-grid-3        /* 3-Spalten Grid */
.responsive-grid-4        /* 4-Spalten Grid */

/* Flexbox Layouts */
.responsive-flex          /* Flex Container */
.flex-container           /* Flex mit Wrap */
.flex-item                /* Flex Item */
```

### Visibility Classes

```css
/* Verstecken auf Breakpoints */
.hide-mobile              /* Versteckt auf Mobile */
.hide-tablet              /* Versteckt auf Tablet */
.hide-desktop             /* Versteckt auf Desktop */

/* Zeigen auf Breakpoints */
.show-mobile              /* Nur auf Mobile */
.show-tablet              /* Nur auf Tablet */
.show-desktop             /* Nur auf Desktop */
```

### Spacing Classes

```css
.spacing-mobile-sm        /* Kleines Padding (responsive) */
.spacing-mobile-md        /* Mittleres Padding (responsive) */
.spacing-mobile-lg        /* Großes Padding (responsive) */
```

### Width Classes

```css
.w-full                   /* width: 100% */
.w-auto                   /* width: auto */
.max-w-mobile             /* max-width: 100% */
.max-w-tablet             /* max-width: 768px */
.max-w-desktop            /* max-width: 1400px */
```

### Utility Classes

```css
.mx-auto                  /* Horizontal zentriert */
.my-auto                  /* Vertikal zentriert */
.text-center-mobile       /* Text zentriert auf Mobile */
.overflow-hidden          /* Overflow versteckt */
.overflow-x-hidden        /* Horizontal Overflow versteckt */
.scroll-smooth            /* Smooth Scrolling */
```

## Responsive Patterns

### Pattern 1: Responsive Grid

```python
import streamlit as st
from utils.shadcn_responsive import inject_responsive_design

inject_responsive_design()

st.markdown('<div class="responsive-grid-3">', unsafe_allow_html=True)

for i in range(6):
    st.markdown(f'<div class="shadcn-card">Card {i+1}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
```

### Pattern 2: Conditional Content

```python
from utils.shadcn_responsive import ResponsiveDesignSystem

system = ResponsiveDesignSystem()

if system.is_mobile():
    # Mobile Layout
    st.write("Simplified Mobile View")
else:
    # Desktop Layout
    cols = st.columns(3)
    with cols[0]:
        st.write("Column 1")
```

### Pattern 3: Responsive Sidebar

```python
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle
)

inject_responsive_design()
render_mobile_sidebar_toggle()

with st.sidebar:
    st.title("Navigation")
    st.button("Home")
    st.button("About")
```

### Pattern 4: Touch-Optimized Buttons

```python
# Buttons sind automatisch touch-optimiert (min. 44px)
st.button("Touch-Friendly Button")
```

### Pattern 5: Responsive Tables

```python
import pandas as pd

df = pd.DataFrame({
    'A': range(10),
    'B': range(10, 20),
    'C': range(20, 30)
})

# Tabelle ist automatisch horizontal scrollbar auf Mobile
st.dataframe(df)
```

## Mobile-Specific Features

### Sidebar Toggle

Auf Mobile wird automatisch ein Toggle-Button angezeigt:

```python
render_mobile_sidebar_toggle()
```

Features:
- Fixed Position (top-left)
- Touch-freundlich (44px min)
- Overlay beim Öffnen
- Smooth Transitions

### Touch Optimization

Alle interaktiven Elemente haben automatisch:
- Mindestgröße: 44px × 44px
- Größeres Padding
- Touch-Feedback (scale on tap)
- Verhindert iOS Zoom (font-size: 16px)

### Stack Layouts

Columns stacken automatisch auf Mobile:

```python
# Desktop: 3 Spalten nebeneinander
# Mobile: 3 Spalten untereinander
cols = st.columns(3)
```

## Best Practices

### 1. Mobile-First Development

Entwickle zuerst für Mobile, dann erweitere für größere Screens:

```python
# Basis (Mobile)
st.write("Content")

# Erweitert für Desktop
if not system.is_mobile():
    st.write("Additional Desktop Content")
```

### 2. Touch-Targets

Stelle sicher, dass alle interaktiven Elemente mindestens 44px groß sind:

```python
# ✅ Gut
st.button("Click Me")  # Automatisch 44px

# ❌ Vermeiden
st.markdown('<button style="height: 20px">Too Small</button>')
```

### 3. Horizontal Scrolling vermeiden

Nutze responsive Layouts statt fixer Breiten:

```python
# ✅ Gut
with responsive_container():
    st.write("Content")

# ❌ Vermeiden
st.markdown('<div style="width: 2000px">Wide Content</div>')
```

### 4. Conditional Rendering

Zeige unterschiedlichen Content basierend auf Viewport:

```python
if system.is_mobile():
    # Vereinfachte Mobile-Ansicht
    st.metric("Revenue", "$1.2M")
else:
    # Detaillierte Desktop-Ansicht
    cols = st.columns(4)
    with cols[0]:
        st.metric("Revenue", "$1.2M", "+12%")
```

### 5. Performance

Injiziere CSS nur einmal:

```python
if 'responsive_css_injected' not in st.session_state:
    inject_responsive_design()
    st.session_state.responsive_css_injected = True
```

## Testing

### Test auf verschiedenen Viewports

```python
# Browser DevTools:
# - Mobile: 375px (iPhone)
# - Tablet: 768px (iPad)
# - Desktop: 1920px
```

### Test Touch-Interaktionen

- Alle Buttons mindestens 44px
- Keine Hover-only Interaktionen
- Touch-Feedback vorhanden

### Test Sidebar

- Toggle funktioniert auf Mobile
- Overlay schließt Sidebar
- Smooth Transitions

## Troubleshooting

### Problem: Horizontales Scrollen

**Lösung:**
```python
# Stelle sicher, dass CSS injiziert ist
inject_responsive_design()

# Nutze responsive Container
with responsive_container():
    st.write("Content")
```

### Problem: Sidebar nicht kollabierbar

**Lösung:**
```python
# Stelle sicher, dass Toggle gerendert wird
render_mobile_sidebar_toggle()
```

### Problem: Buttons zu klein auf Mobile

**Lösung:**
```python
# CSS ist automatisch touch-optimiert
# Stelle sicher, dass inject_responsive_design() aufgerufen wurde
inject_responsive_design()
```

### Problem: Columns stacken nicht

**Lösung:**
```python
# Nutze responsive_columns() statt st.columns()
from utils.shadcn_responsive import responsive_columns

cols = responsive_columns(3)
```

## Examples

Siehe:
- `demo_shadcn_responsive.py` - Vollständige Demo
- `tests/test_shadcn_responsive.py` - Unit Tests

## Requirements

Erfüllt folgende Requirements:
- 12.1: Media Queries für Breakpoints ✅
- 12.2: Kollabierbare Sidebar für Mobile ✅
- 12.3: Gestapelte Layouts für Mobile ✅
- 12.4: Touch-freundliche Button-Größen ✅
- 12.5: Verhindert horizontales Scrollen ✅

## Version

Version: 1.0.0
Author: shadcn/ui Theme System
