# streamlit-shadcn-ui Integration Reference

Complete reference for the streamlit-shadcn-ui integration module with wrapper functions and fallback implementations.

## Overview

The `shadcn_ui_integration` module provides a unified interface to streamlit-shadcn-ui components with automatic fallbacks to native Streamlit widgets when the library is not available.

## Installation

```bash
pip install streamlit-shadcn-ui
```

## Quick Start

```python
from components import shadcn_ui_integration as sui

# Check if library is available
if sui.is_available():
    print(f"Using shadcn/ui version: {sui.get_version()}")

# Use components (automatically falls back if not available)
if sui.button("Click Me", variant="default"):
    st.success("Button clicked!")
```

## Component Reference

### Button

Render a shadcn/ui styled button.

```python
sui.button(
    text: str,
    key: Optional[str] = None,
    variant: Literal["default", "destructive", "outline", "secondary", "ghost", "link"] = "default",
    size: Literal["default", "sm", "lg", "icon"] = "default",
    disabled: bool = False
) -> bool
```

**Parameters:**
- `text`: Button text
- `key`: Unique key for the button
- `variant`: Button style variant
- `size`: Button size
- `disabled`: Whether button is disabled

**Returns:** `bool` - True if button was clicked

**Example:**
```python
if sui.button("Save", variant="default", size="lg"):
    st.success("Saved!")

if sui.button("Delete", variant="destructive"):
    st.error("Deleted!")
```

**Fallback:** Uses `st.button()` with native Streamlit styling.

---

### Badge

Render a small badge component.

```python
sui.badge(
    text: str,
    variant: Literal["default", "secondary", "destructive", "outline"] = "default",
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `text`: Badge text
- `variant`: Badge style variant
- `key`: Unique key for the badge

**Example:**
```python
sui.badge("New", variant="destructive")
sui.badge("Beta", variant="secondary")
```

**Fallback:** Uses styled markdown with inline CSS.

---

### Card

Render a card container with title, description, and content.

```python
sui.card(
    title: Optional[str] = None,
    description: Optional[str] = None,
    content: Optional[str] = None,
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `title`: Card title
- `description`: Card description
- `content`: Card content
- `key`: Unique key for the card

**Example:**
```python
sui.card(
    title="User Profile",
    description="Manage your account settings",
    content="Update your profile information here."
)
```

**Fallback:** Uses `st.container()` with subheader and caption.

---

### Alert

Display an alert message.

```python
sui.alert(
    title: Optional[str] = None,
    description: Optional[str] = None,
    variant: Literal["default", "destructive"] = "default",
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `title`: Alert title
- `description`: Alert description
- `variant`: Alert style (default or destructive)
- `key`: Unique key for the alert

**Example:**
```python
sui.alert(
    title="Success",
    description="Your changes have been saved.",
    variant="default"
)

sui.alert(
    title="Error",
    description="Something went wrong.",
    variant="destructive"
)
```

**Fallback:** Uses `st.info()` or `st.error()` based on variant.

---

### Tabs

Render tabbed navigation.

```python
sui.tabs(
    options: List[str],
    default_value: Optional[str] = None,
    key: Optional[str] = None
) -> str
```

**Parameters:**
- `options`: List of tab labels
- `default_value`: Default selected tab
- `key`: Unique key for the tabs

**Returns:** `str` - Selected tab label

**Example:**
```python
selected_tab = sui.tabs(
    options=["Overview", "Analytics", "Settings"],
    default_value="Overview"
)

if selected_tab == "Overview":
    st.write("Overview content")
```

**Fallback:** Uses `st.tabs()` with native Streamlit tabs.

---

### Switch

Render a toggle switch.

```python
sui.switch(
    label: str,
    default: bool = False,
    key: Optional[str] = None,
    disabled: bool = False
) -> bool
```

**Parameters:**
- `label`: Switch label
- `default`: Default state
- `key`: Unique key for the switch
- `disabled`: Whether switch is disabled

**Returns:** `bool` - Switch state

**Example:**
```python
notifications = sui.switch("Enable notifications", default=True)
if notifications:
    st.write("Notifications enabled")
```

**Fallback:** Uses `st.checkbox()`.

---

### Slider

Render a slider input.

```python
sui.slider(
    label: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    default_value: Optional[float] = None,
    step: float = 1.0,
    key: Optional[str] = None,
    disabled: bool = False
) -> float
```

**Parameters:**
- `label`: Slider label
- `min_value`: Minimum value
- `max_value`: Maximum value
- `default_value`: Default value
- `step`: Step size
- `key`: Unique key for the slider
- `disabled`: Whether slider is disabled

**Returns:** `float` - Slider value

**Example:**
```python
value = sui.slider(
    "Select temperature",
    min_value=0.0,
    max_value=100.0,
    default_value=20.0,
    step=0.5
)
```

**Fallback:** Uses `st.slider()`.

---

### Input

Render a text input field.

```python
sui.input(
    label: str,
    default_value: str = "",
    placeholder: str = "",
    type: Literal["text", "password", "email", "number"] = "text",
    key: Optional[str] = None,
    disabled: bool = False
) -> str
```

**Parameters:**
- `label`: Input label
- `default_value`: Default value
- `placeholder`: Placeholder text
- `type`: Input type
- `key`: Unique key for the input
- `disabled`: Whether input is disabled

**Returns:** `str` - Input value

**Example:**
```python
name = sui.input("Enter your name", placeholder="John Doe")
email = sui.input("Email", type="email", placeholder="user@example.com")
password = sui.input("Password", type="password")
```

**Fallback:** Uses `st.text_input()`.

---

### Textarea

Render a multi-line text input.

```python
sui.textarea(
    label: str,
    default_value: str = "",
    placeholder: str = "",
    rows: int = 3,
    key: Optional[str] = None,
    disabled: bool = False
) -> str
```

**Parameters:**
- `label`: Textarea label
- `default_value`: Default value
- `placeholder`: Placeholder text
- `rows`: Number of rows
- `key`: Unique key for the textarea
- `disabled`: Whether textarea is disabled

**Returns:** `str` - Textarea value

**Example:**
```python
description = sui.textarea(
    "Description",
    placeholder="Enter description...",
    rows=5
)
```

**Fallback:** Uses `st.text_area()`.

---

### Select

Render a dropdown select.

```python
sui.select(
    label: str,
    options: List[str],
    default_value: Optional[str] = None,
    placeholder: str = "Select an option",
    key: Optional[str] = None,
    disabled: bool = False
) -> Optional[str]
```

**Parameters:**
- `label`: Select label
- `options`: List of options
- `default_value`: Default selected value
- `placeholder`: Placeholder text
- `key`: Unique key for the select
- `disabled`: Whether select is disabled

**Returns:** `Optional[str]` - Selected value

**Example:**
```python
country = sui.select(
    "Select country",
    options=["USA", "UK", "Germany", "France"],
    placeholder="Choose..."
)
```

**Fallback:** Uses `st.selectbox()`.

---

### Checkbox

Render a checkbox.

```python
sui.checkbox(
    label: str,
    default: bool = False,
    key: Optional[str] = None,
    disabled: bool = False
) -> bool
```

**Parameters:**
- `label`: Checkbox label
- `default`: Default state
- `key`: Unique key for the checkbox
- `disabled`: Whether checkbox is disabled

**Returns:** `bool` - Checkbox state

**Example:**
```python
agreed = sui.checkbox("I agree to the terms")
if agreed:
    st.write("Thank you for agreeing!")
```

**Fallback:** Uses `st.checkbox()`.

---

### Radio Group

Render a radio button group.

```python
sui.radio_group(
    label: str,
    options: List[str],
    default_value: Optional[str] = None,
    key: Optional[str] = None,
    disabled: bool = False
) -> str
```

**Parameters:**
- `label`: Radio group label
- `options`: List of options
- `default_value`: Default selected value
- `key`: Unique key for the radio group
- `disabled`: Whether radio group is disabled

**Returns:** `str` - Selected value

**Example:**
```python
theme = sui.radio_group(
    "Select theme",
    options=["Light", "Dark", "Auto"],
    default_value="Auto"
)
```

**Fallback:** Uses `st.radio()`.

---

### Date Picker

Render a date picker.

```python
sui.date_picker(
    label: str,
    default_value: Optional[Any] = None,
    key: Optional[str] = None,
    disabled: bool = False
) -> Any
```

**Parameters:**
- `label`: Date picker label
- `default_value`: Default date value
- `key`: Unique key for the date picker
- `disabled`: Whether date picker is disabled

**Returns:** Date value

**Example:**
```python
from datetime import date

selected_date = sui.date_picker(
    "Select date",
    default_value=date.today()
)
```

**Fallback:** Uses `st.date_input()`.

---

### Link

Render a hyperlink.

```python
sui.link(
    text: str,
    href: str,
    target: Literal["_self", "_blank"] = "_blank",
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `text`: Link text
- `href`: Link URL
- `target`: Link target (_self or _blank)
- `key`: Unique key for the link

**Example:**
```python
sui.link(
    "Visit our website",
    href="https://example.com",
    target="_blank"
)
```

**Fallback:** Uses markdown link with `st.markdown()`.

---

### Metric

Render a metric card with value and delta.

```python
sui.metric(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: Literal["normal", "inverse", "off"] = "normal",
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `label`: Metric label
- `value`: Metric value
- `delta`: Delta value (change)
- `delta_color`: Delta color scheme
- `key`: Unique key for the metric

**Example:**
```python
sui.metric(
    label="Total Revenue",
    value="$45,231",
    delta="+20.1%"
)
```

**Fallback:** Uses `st.metric()`.

---

### Table

Render a data table.

```python
sui.table(
    data: Any,
    key: Optional[str] = None
) -> None
```

**Parameters:**
- `data`: Table data (DataFrame or dict)
- `key`: Unique key for the table

**Example:**
```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob"],
    "Age": [25, 30]
})

sui.table(data=df)
```

**Fallback:** Uses `st.dataframe()`.

---

## Utility Functions

### is_available()

Check if streamlit-shadcn-ui is available.

```python
sui.is_available() -> bool
```

**Example:**
```python
if sui.is_available():
    st.success("shadcn/ui is available!")
else:
    st.warning("Using fallback components")
```

---

### get_version()

Get the version of streamlit-shadcn-ui.

```python
sui.get_version() -> Optional[str]
```

**Example:**
```python
version = sui.get_version()
if version:
    st.write(f"Version: {version}")
```

---

### show_availability_status()

Display the availability status of streamlit-shadcn-ui.

```python
sui.show_availability_status() -> None
```

**Example:**
```python
sui.show_availability_status()
```

---

### get_available_components()

Get list of all available component names.

```python
sui.get_available_components() -> List[str]
```

**Example:**
```python
components = sui.get_available_components()
st.write(f"Available components: {', '.join(components)}")
```

---

### get_component()

Get a component function by name.

```python
sui.get_component(name: str) -> Optional[Callable]
```

**Example:**
```python
button_func = sui.get_component("button")
if button_func:
    button_func("Dynamic Button")
```

---

## Fallback Behavior

When `streamlit-shadcn-ui` is not available, all components automatically fall back to native Streamlit widgets:

| shadcn/ui Component | Fallback Component |
|---------------------|-------------------|
| `button` | `st.button()` |
| `badge` | Styled `st.markdown()` |
| `card` | `st.container()` |
| `alert` | `st.info()` / `st.error()` |
| `tabs` | `st.tabs()` |
| `switch` | `st.checkbox()` |
| `slider` | `st.slider()` |
| `input` | `st.text_input()` |
| `textarea` | `st.text_area()` |
| `select` | `st.selectbox()` |
| `checkbox` | `st.checkbox()` |
| `radio_group` | `st.radio()` |
| `date_picker` | `st.date_input()` |
| `link` | `st.markdown()` |
| `metric` | `st.metric()` |
| `table` | `st.dataframe()` |

## Error Handling

All components include error handling with automatic fallback:

```python
try:
    # Try to use shadcn/ui component
    ui.button(...)
except Exception as e:
    logger.error(f"Error: {e}")
    # Automatically falls back to native component
    st.button(...)
```

## Best Practices

1. **Always use the wrapper functions** instead of importing `streamlit_shadcn_ui` directly
2. **Check availability** at app startup with `sui.is_available()`
3. **Use unique keys** for all interactive components
4. **Test with and without** the library installed
5. **Handle return values** appropriately (some components return values, others don't)

## Complete Example

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("My App")

# Show library status
sui.show_availability_status()

# Use components
if sui.button("Submit", variant="default", size="lg"):
    name = sui.input("Name", placeholder="Enter name")
    email = sui.input("Email", type="email")
    
    if name and email:
        sui.alert(
            title="Success",
            description=f"Welcome {name}!",
            variant="default"
        )
```

## Resources

- [streamlit-shadcn-ui Demo](https://shadcn.streamlit.app/)
- [GitHub Repository](https://github.com/ObservedObserver/streamlit-shadcn-ui)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

## Troubleshooting

### Library not found

```bash
pip install streamlit-shadcn-ui
```

### Components not rendering

Check if the library is available:
```python
if not sui.is_available():
    st.warning("Please install: pip install streamlit-shadcn-ui")
```

### Version conflicts

Ensure compatible versions:
```bash
pip install --upgrade streamlit streamlit-shadcn-ui
```
