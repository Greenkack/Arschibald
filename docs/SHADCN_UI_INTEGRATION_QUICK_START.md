# streamlit-shadcn-ui Integration - Quick Start Guide

## Installation

```bash
pip install streamlit-shadcn-ui
```

## Import

```python
from components import shadcn_ui_integration as sui
```

## Check Status

```python
# Show library availability
sui.show_availability_status()

# Check programmatically
if sui.is_available():
    print(f"Version: {sui.get_version()}")
```

## 5-Minute Tutorial

### 1. Simple Button

```python
import streamlit as st
from components import shadcn_ui_integration as sui

if sui.button("Click Me", variant="default"):
    st.success("Button clicked!")
```

### 2. Form Input

```python
name = sui.input("Your Name", placeholder="John Doe")
email = sui.input("Email", type="email")

if sui.button("Submit"):
    st.write(f"Hello {name}!")
```

### 3. Card Display

```python
sui.card(
    title="Welcome",
    description="Get started with shadcn/ui",
    content="This is a beautiful card component."
)
```

### 4. Alert Message

```python
sui.alert(
    title="Success",
    description="Your changes have been saved.",
    variant="default"
)
```

### 5. Metrics Dashboard

```python
col1, col2, col3 = st.columns(3)

with col1:
    sui.metric("Revenue", "$45,231", delta="+20.1%")

with col2:
    sui.metric("Users", "2,350", delta="+180")

with col3:
    sui.metric("Rate", "3.2%", delta="-0.5%")
```

## Component Cheat Sheet

### Buttons
```python
sui.button("Text", variant="default|destructive|outline|secondary|ghost|link")
sui.button("Text", size="sm|default|lg|icon")
```

### Badges
```python
sui.badge("Text", variant="default|secondary|destructive|outline")
```

### Inputs
```python
sui.input("Label", type="text|password|email|number")
sui.textarea("Label", rows=4)
sui.select("Label", options=["A", "B", "C"])
sui.checkbox("Label")
sui.switch("Label")
sui.radio_group("Label", options=["A", "B"])
sui.slider("Label", min_value=0, max_value=100)
sui.date_picker("Label")
```

### Display
```python
sui.card(title="Title", description="Desc", content="Content")
sui.alert(title="Title", description="Desc", variant="default|destructive")
sui.metric(label="Label", value="Value", delta="Delta")
sui.table(data=dataframe)
sui.link("Text", href="url")
```

### Navigation
```python
selected = sui.tabs(options=["Tab1", "Tab2", "Tab3"])
```

## Complete Example

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("My App")

# Show status
sui.show_availability_status()

# Form
with st.form("my_form"):
    name = sui.input("Name", placeholder="Enter name")
    email = sui.input("Email", type="email")
    message = sui.textarea("Message", rows=4)
    
    submitted = sui.button("Submit", variant="default")
    
    if submitted:
        if name and email and message:
            sui.alert(
                title="Success",
                description=f"Thank you {name}!",
                variant="default"
            )
        else:
            sui.alert(
                title="Error",
                description="Please fill all fields",
                variant="destructive"
            )

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    sui.metric("Total", "1,234", delta="+12%")

with col2:
    sui.metric("Active", "567", delta="+5%")

with col3:
    sui.metric("Rate", "45%", delta="-3%")
```

## Fallback Behavior

If `streamlit-shadcn-ui` is not installed, all components automatically fall back to native Streamlit widgets. Your app will still work!

## Run Demo

```bash
streamlit run demo_shadcn_ui_integration.py
```

## Run Tests

```bash
pytest tests/test_shadcn_ui_integration.py -v
```

## Documentation

- **Full Reference**: `components/SHADCN_UI_INTEGRATION_REFERENCE.md`
- **Quick Reference**: `components/SHADCN_UI_INTEGRATION_QUICK_REFERENCE.md`
- **Usage Examples**: `components/SHADCN_UI_INTEGRATION_USAGE_EXAMPLE.md`

## Common Patterns

### Login Form
```python
username = sui.input("Username")
password = sui.input("Password", type="password")
remember = sui.checkbox("Remember me")

if sui.button("Login", variant="default"):
    # Handle login
    pass
```

### Settings Panel
```python
notifications = sui.switch("Enable notifications", default=True)
theme = sui.radio_group("Theme", options=["Light", "Dark", "Auto"])
language = sui.select("Language", options=["English", "German", "French"])

if sui.button("Save", variant="default"):
    sui.alert(title="Success", description="Settings saved!")
```

### Data Table
```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob"],
    "Age": [25, 30]
})

sui.table(data=df)
```

## Tips

1. Always use unique `key` parameters for interactive components
2. Check availability with `sui.is_available()` at startup
3. Use appropriate variants for different contexts
4. Combine with native Streamlit components as needed
5. Test with and without the library installed

## Troubleshooting

### Library not found
```bash
pip install streamlit-shadcn-ui
```

### Components not rendering
```python
if not sui.is_available():
    st.warning("Please install: pip install streamlit-shadcn-ui")
```

### Import errors
```python
# Use the wrapper, not direct import
from components import shadcn_ui_integration as sui  # ✅ Correct
# import streamlit_shadcn_ui as ui  # ❌ Don't do this
```

## Resources

- **Demo Site**: https://shadcn.streamlit.app/
- **GitHub**: https://github.com/ObservedObserver/streamlit-shadcn-ui
- **shadcn/ui**: https://ui.shadcn.com/

## Next Steps

1. Explore the demo: `streamlit run demo_shadcn_ui_integration.py`
2. Read the full reference: `components/SHADCN_UI_INTEGRATION_REFERENCE.md`
3. Try the examples: `components/SHADCN_UI_INTEGRATION_USAGE_EXAMPLE.md`
4. Integrate into your app!

---

**Happy coding with shadcn/ui! 🎨**
