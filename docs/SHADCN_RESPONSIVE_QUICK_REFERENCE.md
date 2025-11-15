# shadcn/ui Responsive Design - Quick Reference

## 🚀 Quick Start

```python
from utils.shadcn_responsive import inject_responsive_design

# Injiziere Responsive CSS
inject_responsive_design()
```

## 📱 Breakpoints

| Breakpoint | Range | Description |
|------------|-------|-------------|
| Mobile | 0-767px | Smartphones |
| Tablet | 768-1023px | Tablets |
| Desktop | 1024px+ | Desktop/Laptop |

## 🎯 Common Use Cases

### 1. Basis-Setup

```python
import streamlit as st
from utils.shadcn_responsive import inject_responsive_design

inject_responsive_design()
st.title("My Responsive App")
```

### 2. Sidebar mit Mobile Toggle

```python
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle
)

inject_responsive_design()
render_mobile_sidebar_toggle()

with st.sidebar:
    st.write("Navigation")
```

### 3. Responsive Columns

```python
from utils.shadcn_responsive import responsive_columns

# 3 Spalten auf Desktop, 1 auf Mobile
cols = responsive_columns(3)
with cols[0]:
    st.write("Column 1")
```

### 4. Responsive Container

```python
from utils.shadcn_responsive import responsive_container

with responsive_container('tablet'):
    st.write("Zentrierter Content")
```

## 🎨 CSS Classes

### Visibility

```html
<div class="hide-mobile">Versteckt auf Mobile</div>
<div class="show-mobile">Nur auf Mobile</div>
<div class="hide-tablet">Versteckt auf Tablet</div>
<div class="show-desktop">Nur auf Desktop</div>
```

### Layouts

```html
<div class="responsive-grid-3">
    <!-- 3 Spalten auf Desktop, 2 auf Tablet, 1 auf Mobile -->
</div>

<div class="responsive-flex">
    <!-- Flex Layout mit automatischem Wrap -->
</div>
```

### Width

```html
<div class="w-full">Volle Breite</div>
<div class="max-w-tablet mx-auto">Max 768px, zentriert</div>
```

## 🔧 API Functions

### inject_responsive_design()
Injiziert Responsive CSS in die App.

### render_mobile_sidebar_toggle()
Zeigt Sidebar Toggle Button auf Mobile.

### responsive_columns(num_columns, mobile_stack=True)
Erstellt responsive Columns.

### responsive_container(max_width='desktop')
Erstellt Container mit max-width.

## 📐 Touch Optimization

Alle interaktiven Elemente haben automatisch:
- ✅ Min. 44px × 44px Größe
- ✅ Größeres Padding
- ✅ Touch-Feedback
- ✅ Verhindert iOS Zoom

## 🎯 Best Practices

### ✅ DO

```python
# Responsive Columns nutzen
cols = responsive_columns(3)

# Container mit max-width
with responsive_container():
    st.write("Content")

# Conditional Rendering
if system.is_mobile():
    st.write("Mobile View")
```

### ❌ DON'T

```python
# Fixe Breiten vermeiden
st.markdown('<div style="width: 2000px">Wide</div>')

# Zu kleine Touch-Targets
st.markdown('<button style="height: 20px">Small</button>')

# Horizontales Scrollen
st.markdown('<div style="overflow-x: scroll">...</div>')
```

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|--------|
| Horizontales Scrollen | `inject_responsive_design()` aufrufen |
| Sidebar nicht kollabierbar | `render_mobile_sidebar_toggle()` aufrufen |
| Columns stacken nicht | `responsive_columns()` statt `st.columns()` |
| Buttons zu klein | CSS ist automatisch touch-optimiert |

## 📚 Examples

```python
# Vollständiges Beispiel
import streamlit as st
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle,
    responsive_columns,
    responsive_container
)

# Setup
inject_responsive_design()
render_mobile_sidebar_toggle()

# Sidebar
with st.sidebar:
    st.title("Navigation")
    st.button("Home")

# Main Content
with responsive_container('desktop'):
    st.title("Responsive App")
    
    # Responsive Grid
    cols = responsive_columns(3)
    with cols[0]:
        st.metric("Users", "1.2K")
    with cols[1]:
        st.metric("Revenue", "$45K")
    with cols[2]:
        st.metric("Growth", "+12%")
```

## 🔗 Related

- Full Reference: `utils/SHADCN_RESPONSIVE_REFERENCE.md`
- Demo: `demo_shadcn_responsive.py`
- Tests: `tests/test_shadcn_responsive.py`
