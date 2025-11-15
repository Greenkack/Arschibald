# shadcn/ui Migration Guide

## Overview

This guide explains how to migrate existing Streamlit modules to use shadcn/ui components for a modern, consistent design system.

## Migration Status

### ✅ Completed Migrations

1. **solar_calculator.py** → `solar_calculator_shadcn.py`
2. **crm.py** → `crm_shadcn.py`
3. **admin_panel.py** → `admin_panel_shadcn.py`

### 🎨 Applied Enhancements

- ✅ Replaced `st.container()` with shadcn/ui `Card` components
- ✅ Replaced `st.info/warning/error/success()` with shadcn/ui `Alert` components
- ✅ Replaced `st.metric()` with shadcn/ui `MetricCard` components
- ✅ Applied `apply_chart_theme()` to all Plotly charts
- ✅ Added modern navigation with `ShadcnSidebar`
- ✅ Enhanced forms with shadcn/ui styling

## Migration Helpers

The `utils/shadcn_migration_helpers.py` module provides convenient wrapper functions for easy migration:

### Available Functions

```python
from utils.shadcn_migration_helpers import (
    inject_shadcn_styles,      # Inject CSS once per page
    shadcn_card,                # Replacement for st.container()
    shadcn_alert,               # Replacement for st.info/warning/error/success()
    shadcn_metric,              # Replacement for st.metric()
    shadcn_badge,               # Create badges
    apply_shadcn_chart_theme,   # Apply theme to Plotly charts
    shadcn_section,             # Create styled sections
)
```

## Migration Patterns

### 1. Basic Page Setup

**Before:**
```python
import streamlit as st

def render_my_page():
    st.header("My Page")
    # ... content
```

**After:**
```python
import streamlit as st
from utils.shadcn_migration_helpers import inject_shadcn_styles

def render_my_page():
    # Inject styles once at the beginning
    inject_shadcn_styles()
    
    st.header("My Page")
    # ... content
```

### 2. Replacing Containers with Cards

**Before:**
```python
with st.container():
    st.subheader("Section Title")
    st.write("Content here")
```

**After:**
```python
from utils.shadcn_migration_helpers import shadcn_card

shadcn_card(
    title="Section Title",
    content="Content here",
    variant="default",  # or "outlined", "elevated"
    icon="📊"
)
```

### 3. Replacing Alerts

**Before:**
```python
st.info("Information message")
st.success("Success message")
st.warning("Warning message")
st.error("Error message")
```

**After:**
```python
from utils.shadcn_migration_helpers import shadcn_alert

shadcn_alert("Information message", alert_type="info")
shadcn_alert("Success message", alert_type="success")
shadcn_alert("Warning message", alert_type="warning")
shadcn_alert("Error message", alert_type="error")
```

### 4. Replacing Metrics

**Before:**
```python
st.metric(
    label="Total Users",
    value="1,234",
    delta="+12%"
)
```

**After:**
```python
from utils.shadcn_migration_helpers import shadcn_metric

shadcn_metric(
    label="Total Users",
    value="1,234",
    delta="+12%",
    icon="👥",
    size="medium"
)
```

### 5. Applying Chart Themes

**Before:**
```python
import plotly.graph_objects as go

fig = go.Figure(data=[...])
st.plotly_chart(fig)
```

**After:**
```python
import plotly.graph_objects as go
from utils.shadcn_migration_helpers import apply_shadcn_chart_theme

fig = go.Figure(data=[...])
fig = apply_shadcn_chart_theme(fig)
st.plotly_chart(fig)
```

### 6. Creating Sections

**Before:**
```python
st.subheader("My Section")
st.write("Content")
```

**After:**
```python
from utils.shadcn_migration_helpers import shadcn_section

with shadcn_section(
    title="My Section",
    icon="📊",
    description="Optional description",
    collapsible=False
):
    st.write("Content")
```

## Module-Specific Migration

### Solar Calculator Migration

The `solar_calculator_shadcn.py` module provides:

```python
from solar_calculator_shadcn import (
    render_solar_calculator_with_shadcn,
    display_pricing_with_shadcn,
    apply_chart_theme_to_all_figures,
)

# Use in gui.py
render_solar_calculator_with_shadcn(texts, module_name)
```

**Key Enhancements:**
- Pricing display uses modern cards and metrics
- All charts automatically themed
- Form sections use cards
- Alerts use shadcn/ui styling

### CRM Migration

The `crm_shadcn.py` module provides:

```python
from crm_shadcn import (
    render_crm_with_shadcn,
    render_customer_list_with_cards,
    render_crm_dashboard_with_metrics,
)

# Use in gui.py
render_crm_with_shadcn(texts, get_db_connection_func)
```

**Key Enhancements:**
- Customer list displays as modern card grid
- Dashboard shows metrics with icons
- Forms use shadcn/ui styling
- Action buttons styled consistently

### Admin Panel Migration

The `admin_panel_shadcn.py` module provides:

```python
from admin_panel_shadcn import (
    render_admin_panel_with_shadcn,
    render_admin_navigation_with_shadcn,
    render_admin_dashboard_with_metrics,
)

# Use in gui.py
render_admin_panel_with_shadcn(
    texts,
    get_db_connection_func,
    load_admin_setting_func,
    save_admin_setting_func
)
```

**Key Enhancements:**
- Navigation uses modern sidebar with grouped menus
- Settings forms use cards
- Dashboard shows metrics
- All sections use consistent styling

## Integration with gui.py

To integrate the migrated modules into your main application:

```python
# In gui.py

# Import migrated modules
from solar_calculator_shadcn import render_solar_calculator_with_shadcn
from crm_shadcn import render_crm_with_shadcn
from admin_panel_shadcn import render_admin_panel_with_shadcn

# Use feature flag to enable/disable shadcn/ui
USE_SHADCN_UI = st.session_state.get('enable_shadcn_ui', True)

# In your page routing logic
if current_page == "solar_calculator":
    if USE_SHADCN_UI:
        render_solar_calculator_with_shadcn(texts, module_name)
    else:
        render_solar_calculator(texts, module_name)  # Original

elif current_page == "crm":
    if USE_SHADCN_UI:
        render_crm_with_shadcn(texts, get_db_connection)
    else:
        render_crm(texts, get_db_connection)  # Original

elif current_page == "admin":
    if USE_SHADCN_UI:
        render_admin_panel_with_shadcn(
            texts,
            get_db_connection,
            load_admin_setting,
            save_admin_setting
        )
    else:
        render_admin_panel(
            texts,
            get_db_connection,
            load_admin_setting,
            save_admin_setting
        )  # Original
```

## Fallback Behavior

All migration helpers include automatic fallback to standard Streamlit components if shadcn/ui is not available:

```python
# This will work even if shadcn/ui is not installed
shadcn_alert("Message", alert_type="info")
# Falls back to: st.info("Message")
```

## Theme Management

The migration automatically initializes the theme manager:

```python
# Theme manager is automatically initialized in session state
theme_manager = st.session_state.theme_manager

# You can change themes programmatically
theme_manager.set_theme('shadcn-dark')
theme_manager.set_theme('shadcn-ocean')
theme_manager.set_theme('shadcn-forest')
```

## Best Practices

1. **Always inject styles once per page:**
   ```python
   inject_shadcn_styles()  # At the beginning of your render function
   ```

2. **Use cards for logical groupings:**
   ```python
   # Group related content in cards
   shadcn_card(title="User Information", content="...")
   shadcn_card(title="Settings", content="...")
   ```

3. **Apply chart themes consistently:**
   ```python
   # Apply to all Plotly figures
   fig = apply_shadcn_chart_theme(fig)
   ```

4. **Use appropriate alert types:**
   ```python
   shadcn_alert("Info", alert_type="info")      # Blue
   shadcn_alert("Success", alert_type="success") # Green
   shadcn_alert("Warning", alert_type="warning") # Yellow
   shadcn_alert("Error", alert_type="error")     # Red
   ```

5. **Leverage metrics for KPIs:**
   ```python
   # Use metrics for important numbers
   shadcn_metric(
       label="Revenue",
       value="$1.2M",
       delta="+15%",
       icon="💰"
   )
   ```

## Testing

Test your migrated modules with both shadcn/ui enabled and disabled:

```python
# Test with shadcn/ui
st.session_state.enable_shadcn_ui = True
render_my_page()

# Test without shadcn/ui (fallback)
st.session_state.enable_shadcn_ui = False
render_my_page()
```

## Troubleshooting

### Issue: Styles not applying

**Solution:** Make sure you call `inject_shadcn_styles()` at the beginning of your page.

### Issue: Theme manager not found

**Solution:** The theme manager is automatically initialized. If you see errors, check that the theming module is properly installed.

### Issue: Components not rendering

**Solution:** Check that all required imports are available. The migration helpers will fall back to standard Streamlit components if shadcn/ui is not available.

### Issue: Charts not themed

**Solution:** Make sure you call `apply_shadcn_chart_theme(fig)` on your Plotly figures before displaying them.

## Next Steps

1. Test the migrated modules in your application
2. Gradually migrate additional modules using the same patterns
3. Customize themes to match your brand
4. Create custom components as needed

## Support

For questions or issues with the migration:

1. Check the component documentation in `docs/SHADCN_UI_GUIDE.md`
2. Review the component reference files in `components/`
3. Check the demo files for examples: `demo_*.py`

## Changelog

### 2025-01-15
- ✅ Migrated solar_calculator.py
- ✅ Migrated crm.py
- ✅ Migrated admin_panel.py
- ✅ Created migration helper utilities
- ✅ Applied chart themes to all Plotly figures
- ✅ Replaced containers with cards
- ✅ Created comprehensive migration guide
