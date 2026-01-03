# streamlit-shadcn-ui Integration - Quick Reference

## Installation

```bash
pip install streamlit-shadcn-ui
```

## Import

```python
from components import shadcn_ui_integration as sui
```

## Quick Examples

### Buttons
```python
# Basic button
if sui.button("Click Me"):
    st.success("Clicked!")

# Variants
sui.button("Default", variant="default")
sui.button("Delete", variant="destructive")
sui.button("Outline", variant="outline")
sui.button("Secondary", variant="secondary")
sui.button("Ghost", variant="ghost")
sui.button("Link", variant="link")

# Sizes
sui.button("Small", size="sm")
sui.button("Default", size="default")
sui.button("Large", size="lg")
sui.button("🔍", size="icon")
```

### Badges
```python
sui.badge("New", variant="default")
sui.badge("Beta", variant="secondary")
sui.badge("Error", variant="destructive")
sui.badge("Info", variant="outline")
```

### Cards
```python
sui.card(
    title="Card Title",
    description="Card description",
    content="Card content here"
)
```

### Alerts
```python
sui.alert(
    title="Success",
    description="Operation completed",
    variant="default"
)

sui.alert(
    title="Error",
    description="Something went wrong",
    variant="destructive"
)
```

### Inputs
```python
# Text input
name = sui.input("Name", placeholder="John Doe")

# Password
password = sui.input("Password", type="password")

# Email
email = sui.input("Email", type="email")

# Textarea
text = sui.textarea("Description", rows=4)
```

### Select & Radio
```python
# Select dropdown
option = sui.select(
    "Choose",
    options=["A", "B", "C"]
)

# Radio group
choice = sui.radio_group(
    "Select one",
    options=["Option 1", "Option 2"]
)
```

### Checkbox & Switch
```python
# Checkbox
checked = sui.checkbox("I agree")

# Switch
enabled = sui.switch("Enable feature")
```

### Slider
```python
value = sui.slider(
    "Temperature",
    min_value=0.0,
    max_value=100.0,
    default_value=20.0
)
```

### Date Picker
```python
from datetime import date

selected = sui.date_picker(
    "Select date",
    default_value=date.today()
)
```

### Metrics
```python
sui.metric(
    label="Revenue",
    value="$45,231",
    delta="+20.1%"
)
```

### Table
```python
import pandas as pd

df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
sui.table(data=df)
```

### Links
```python
sui.link(
    "Visit site",
    href="https://example.com",
    target="_blank"
)
```

### Tabs
```python
selected = sui.tabs(
    options=["Tab 1", "Tab 2", "Tab 3"],
    default_value="Tab 1"
)
```

## Utility Functions

```python
# Check availability
if sui.is_available():
    st.success("Library available!")

# Get version
version = sui.get_version()

# Show status
sui.show_availability_status()

# List components
components = sui.get_available_components()

# Get component by name
btn = sui.get_component("button")
```

## Component Variants

### Button Variants
- `default` - Primary button
- `destructive` - Danger/delete button
- `outline` - Outlined button
- `secondary` - Secondary button
- `ghost` - Transparent button
- `link` - Link-styled button

### Button Sizes
- `sm` - Small
- `default` - Default
- `lg` - Large
- `icon` - Icon only

### Badge Variants
- `default` - Default badge
- `secondary` - Secondary badge
- `destructive` - Error/warning badge
- `outline` - Outlined badge

### Alert Variants
- `default` - Info alert
- `destructive` - Error alert

### Input Types
- `text` - Text input
- `password` - Password input
- `email` - Email input
- `number` - Number input

## Fallback Behavior

All components automatically fall back to native Streamlit widgets if `streamlit-shadcn-ui` is not installed.

## Complete Form Example

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("User Registration")

# Show library status
sui.show_availability_status()

# Form
with st.form("registration"):
    name = sui.input("Full Name", placeholder="John Doe")
    email = sui.input("Email", type="email")
    password = sui.input("Password", type="password")
    
    country = sui.select(
        "Country",
        options=["USA", "UK", "Germany"]
    )
    
    notifications = sui.switch("Enable notifications")
    terms = sui.checkbox("I agree to terms")
    
    if sui.button("Register", variant="default"):
        if name and email and password and terms:
            sui.alert(
                title="Success",
                description="Registration complete!",
                variant="default"
            )
        else:
            sui.alert(
                title="Error",
                description="Please fill all fields",
                variant="destructive"
            )
```

## Dashboard Example

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("Dashboard")

# Metrics row
col1, col2, col3 = st.columns(3)

with col1:
    sui.metric("Revenue", "$45,231", "+20.1%")

with col2:
    sui.metric("Users", "2,350", "+180")

with col3:
    sui.metric("Rate", "3.2%", "-0.5%")

# Cards
col1, col2 = st.columns(2)

with col1:
    sui.card(
        title="Recent Activity",
        description="Last 7 days",
        content="View your recent activities"
    )

with col2:
    sui.card(
        title="Notifications",
        description="3 new",
        content="You have unread notifications"
    )
```

## Resources

- **Demo**: https://shadcn.streamlit.app/
- **GitHub**: https://github.com/ObservedObserver/streamlit-shadcn-ui
- **Docs**: See `SHADCN_UI_INTEGRATION_REFERENCE.md`
