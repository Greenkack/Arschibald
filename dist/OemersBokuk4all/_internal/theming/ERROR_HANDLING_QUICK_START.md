# Error Handling Quick Start

Get started with the Theme System error handling in 5 minutes.

## Installation

The error handling system is already integrated into the theming package:

```python
from theming import (
    ThemeError,
    ThemeLoadError,
    ErrorHandler,
    get_error_handler
)
```

## Basic Usage

### 1. Handle Any Error

```python
from theming.error_handler import get_error_handler

handler = get_error_handler()

try:
    # Your code
    load_theme("custom")
except Exception as e:
    handler.handle_error(e, notify_user=True)
```

### 2. Use Fallback Mechanisms

```python
# Theme loading with fallback
try:
    theme = load_theme("custom")
except Exception as e:
    theme = handler.handle_theme_load_error(
        "custom",
        e,
        lambda: get_default_theme()
    )

# Component rendering with fallback
try:
    card.render(title="Test")
except Exception as e:
    handler.handle_component_error(
        "Card",
        e,
        lambda: st.container()
    )
```

### 3. Show Error Dashboard

```python
from theming.error_dashboard import render_error_dashboard

# In your Streamlit app
render_error_dashboard()
```

### 4. Add Error Summary Widget

```python
from theming.error_dashboard import render_error_summary_widget

# In sidebar
with st.sidebar:
    render_error_summary_widget()
```

## Common Patterns

### Pattern 1: Theme Manager

```python
class ThemeManager:
    def __init__(self):
        self.error_handler = get_error_handler()
    
    def load_theme(self, name):
        try:
            return self._load_theme_file(name)
        except Exception as e:
            return self.error_handler.handle_theme_load_error(
                name, e, self._get_fallback
            )
```

### Pattern 2: Component

```python
class MyComponent:
    def render(self, **kwargs):
        handler = get_error_handler()
        try:
            self._do_render(**kwargs)
        except Exception as e:
            handler.handle_component_error(
                "MyComponent", e, self._fallback
            )
```

### Pattern 3: CSS Generator

```python
class CSSGenerator:
    def generate(self):
        handler = get_error_handler()
        try:
            return self._generate_css()
        except Exception as e:
            return handler.handle_css_generation_error(
                self.theme.name, e, self._minimal_css
            )
```

## Exception Types

Use specific exceptions for better error handling:

```python
from theming import (
    ThemeLoadError,
    ThemeValidationError,
    CSSGenerationError,
    ComponentRenderError
)

# Raise specific error
raise ThemeLoadError("custom", "File not found")

# Catch specific error
try:
    load_theme("custom")
except ThemeLoadError as e:
    print(f"Theme error: {e.theme_name}")
```

## Notifications

### Inline Notification

```python
from theming.error_dashboard import render_inline_error_notification

render_inline_error_notification(
    "Error",
    "Something went wrong",
    severity="error"
)
```

### Toast Notification

```python
from theming.error_dashboard import render_error_toast

render_error_toast("Success!", "success")
```

## Error Reports

```python
handler = get_error_handler()

# Get report
report = handler.get_error_report()
print(f"Total errors: {report['total_errors']}")

# Export report
handler.export_error_report('logs/report.json')

# Clear history
handler.clear_history()
```

## Configuration

```python
handler = ErrorHandler()

# Adjust retry limit
handler.max_recovery_attempts = 5

# Adjust history size
handler.max_history_size = 200

# Use custom logger
import logging
logger = logging.getLogger("my_logger")
handler = ErrorHandler(logger=logger)
```

## Demo

Run the demo to see all features:

```bash
streamlit run demo_error_handling.py
```

## Documentation

- **Full Reference:** `theming/ERROR_HANDLING_REFERENCE.md`
- **Quick Reference:** `docs/ERROR_HANDLING_QUICK_REFERENCE.md`
- **API Docs:** See docstrings in code

## Testing

Run tests:

```bash
pytest tests/test_error_handling.py -v
```

## Need Help?

1. Check the full reference guide
2. Run the demo application
3. Review the test examples
4. Check inline documentation

---

**Ready to use!** The error handling system is production-ready and fully tested.
