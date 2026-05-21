# shadcn/ui Migration Quick Reference

## Quick Start

```python
from utils.shadcn_migration_helpers import inject_shadcn_styles

def my_page():
    inject_shadcn_styles()  # Add this at the beginning
    # ... rest of your code
```

## Common Replacements

### Containers → Cards

```python
# Before
with st.container():
    st.subheader("Title")
    st.write("Content")

# After
from utils.shadcn_migration_helpers import shadcn_card
shadcn_card(title="Title", content="Content", icon="📊")
```

### Alerts

```python
# Before
st.info("Message")
st.success("Message")
st.warning("Message")
st.error("Message")

# After
from utils.shadcn_migration_helpers import shadcn_alert
shadcn_alert("Message", alert_type="info")
shadcn_alert("Message", alert_type="success")
shadcn_alert("Message", alert_type="warning")
shadcn_alert("Message", alert_type="error")
```

### Metrics

```python
# Before
st.metric("Label", "Value", "+10%")

# After
from utils.shadcn_migration_helpers import shadcn_metric
shadcn_metric("Label", "Value", delta="+10%", icon="📈")
```

### Charts

```python
# Before
fig = go.Figure(...)
st.plotly_chart(fig)

# After
from utils.shadcn_migration_helpers import apply_shadcn_chart_theme
fig = go.Figure(...)
fig = apply_shadcn_chart_theme(fig)
st.plotly_chart(fig)
```

## Module Imports

### Solar Calculator

```python
from solar_calculator_shadcn import render_solar_calculator_with_shadcn
render_solar_calculator_with_shadcn(texts, module_name)
```

### CRM

```python
from crm_shadcn import render_crm_with_shadcn
render_crm_with_shadcn(texts, get_db_connection_func)
```

### Admin Panel

```python
from admin_panel_shadcn import render_admin_panel_with_shadcn
render_admin_panel_with_shadcn(texts, get_db_connection_func, load_admin_setting_func, save_admin_setting_func)
```

## Card Variants

```python
shadcn_card(title="Title", variant="default")   # Standard
shadcn_card(title="Title", variant="outlined")  # With border
shadcn_card(title="Title", variant="elevated")  # With shadow
```

## Alert Types

```python
shadcn_alert("Message", alert_type="info")     # Blue
shadcn_alert("Message", alert_type="success")  # Green
shadcn_alert("Message", alert_type="warning")  # Yellow
shadcn_alert("Message", alert_type="error")    # Red
```

## Metric Sizes

```python
shadcn_metric("Label", "Value", size="small")   # Compact
shadcn_metric("Label", "Value", size="medium")  # Standard
shadcn_metric("Label", "Value", size="large")   # Prominent
```

## Common Icons

- 📊 Charts/Analytics
- 👥 Users/Customers
- 🏢 Company/Business
- ⚙️ Settings
- 📦 Products
- 💰 Money/Pricing
- 📧 Email
- 📞 Phone
- 📍 Location
- ✅ Success
- ⚠️ Warning
- ❌ Error
- ℹ️ Info

## Feature Flag

```python
# Enable/disable shadcn/ui globally
st.session_state.enable_shadcn_ui = True  # or False
```

## Fallback Behavior

All functions automatically fall back to standard Streamlit components if shadcn/ui is not available.

## Theme Selection

```python
# Available themes
themes = [
    'shadcn-default',  # Light theme
    'shadcn-dark',     # Dark theme
    'shadcn-ocean',    # Blue theme
    'shadcn-forest',   # Green theme
    'shadcn-sunset',   # Orange theme
]

# Change theme
st.session_state.theme_manager.set_theme('shadcn-dark')
```

## Complete Example

```python
import streamlit as st
from utils.shadcn_migration_helpers import (
    inject_shadcn_styles,
    shadcn_card,
    shadcn_alert,
    shadcn_metric,
    apply_shadcn_chart_theme,
)
import plotly.graph_objects as go

def my_dashboard():
    # 1. Inject styles
    inject_shadcn_styles()
    
    # 2. Show metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        shadcn_metric("Users", "1,234", delta="+12%", icon="👥")
    with col2:
        shadcn_metric("Revenue", "$45K", delta="+8%", icon="💰")
    with col3:
        shadcn_metric("Orders", "567", delta="-3%", icon="📦")
    
    # 3. Show content in cards
    shadcn_card(
        title="📊 Sales Overview",
        content="Your sales data for this month",
        variant="elevated"
    )
    
    # 4. Show alerts
    shadcn_alert("Data updated successfully!", alert_type="success")
    
    # 5. Show themed chart
    fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[4, 5, 6])])
    fig = apply_shadcn_chart_theme(fig)
    st.plotly_chart(fig)

if __name__ == "__main__":
    my_dashboard()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Styles not applying | Call `inject_shadcn_styles()` at page start |
| Components not rendering | Check imports and fallback behavior |
| Charts not themed | Call `apply_shadcn_chart_theme(fig)` |
| Theme not changing | Ensure theme_manager is initialized |

## More Information

- Full guide: `docs/SHADCN_MIGRATION_GUIDE.md`
- Component docs: `docs/SHADCN_UI_GUIDE.md`
- Demo files: `demo_*.py`
