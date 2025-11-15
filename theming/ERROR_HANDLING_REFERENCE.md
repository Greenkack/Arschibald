# Error Handling System Reference

Complete reference for the Theme System error handling infrastructure.

## Overview

The error handling system provides:
- **Exception Hierarchy**: Custom exceptions for all error types
- **Error Handler**: Centralized error handling with fallback mechanisms
- **Error Dashboard**: Visual error reporting and monitoring
- **Automatic Recovery**: Self-healing capabilities
- **User Notifications**: Streamlit-based error notifications

## Exception Hierarchy

### Base Exception

```python
from theming.theme_errors import ThemeError

try:
    # Your code
    pass
except ThemeError as e:
    print(f"Theme error: {e}")
    print(f"Details: {e.details}")
```

### Specific Exceptions

#### ThemeLoadError
Raised when a theme cannot be loaded.

```python
from theming.theme_errors import ThemeLoadError

raise ThemeLoadError(
    theme_name="my-theme",
    reason="File not found",
    details={'path': '/themes/my-theme.json'}
)
```

#### ThemeValidationError
Raised when theme validation fails.

```python
from theming.theme_errors import ThemeValidationError

raise ThemeValidationError(
    theme_name="my-theme",
    errors=["Invalid color format", "Missing font-family"],
    details={'schema_version': '1.0'}
)
```

#### ThemeNotFoundError
Raised when a requested theme doesn't exist.

```python
from theming.theme_errors import ThemeNotFoundError

raise ThemeNotFoundError(
    theme_name="missing-theme",
    available_themes=["default", "dark", "ocean"]
)
```

#### CSSGenerationError
Raised when CSS generation fails.

```python
from theming.theme_errors import CSSGenerationError

raise CSSGenerationError(
    theme_name="my-theme",
    reason="Invalid token reference",
    details={'token': 'colors.invalid'}
)
```

#### CSSInjectionError
Raised when CSS injection fails.

```python
from theming.theme_errors import CSSInjectionError

raise CSSInjectionError(
    reason="Streamlit markdown failed",
    details={'css_size': 50000}
)
```

#### ComponentRenderError
Raised when component rendering fails.

```python
from theming.theme_errors import ComponentRenderError

raise ComponentRenderError(
    component_name="Card",
    reason="Missing required prop: title",
    details={'props': {'content': 'test'}}
)
```

## Error Handler

### Basic Usage

```python
from theming.error_handler import ErrorHandler

# Create handler
handler = ErrorHandler()

# Handle an error
try:
    # Your code
    raise ValueError("Something went wrong")
except Exception as e:
    handler.handle_error(
        error=e,
        context={'operation': 'theme_load'},
        notify_user=True,
        severity='error'
    )
```

### Using Global Handler

```python
from theming.error_handler import get_error_handler

# Get global handler instance
handler = get_error_handler()

# Use it
handler.handle_error(error)
```

### Specialized Error Handlers

#### Theme Load Error with Fallback

```python
def load_fallback_theme():
    return Theme(name="fallback", ...)

try:
    theme = load_theme("custom-theme")
except Exception as e:
    theme = handler.handle_theme_load_error(
        theme_name="custom-theme",
        error=e,
        fallback_callback=load_fallback_theme
    )
```

#### CSS Generation Error with Fallback

```python
def generate_fallback_css():
    return "/* Minimal CSS */"

try:
    css = generate_css(theme)
except Exception as e:
    css = handler.handle_css_generation_error(
        theme_name=theme.name,
        error=e,
        fallback_callback=generate_fallback_css
    )
```

#### Component Error with Fallback

```python
def render_fallback_component():
    st.container()  # Native Streamlit component

try:
    card.render(title="Test")
except Exception as e:
    handler.handle_component_error(
        component_name="Card",
        error=e,
        fallback_callback=render_fallback_component
    )
```

### Automatic Recovery

The error handler automatically attempts recovery with retry limits:

```python
# Recovery is automatic when using specialized handlers
theme = handler.handle_theme_load_error(
    theme_name="custom",
    error=e,
    fallback_callback=load_fallback
)
# Will retry up to 3 times before giving up
```

### Error Reports

#### Get Error Report

```python
report = handler.get_error_report()

print(f"Total errors: {report['total_errors']}")
print(f"Error types: {report['error_types']}")
print(f"Recent errors: {len(report['recent_errors'])}")
```

#### Export Error Report

```python
handler.export_error_report('logs/error_report.json')
```

#### Clear Error History

```python
handler.clear_history()
```

## Error Dashboard

### Render Full Dashboard

```python
import streamlit as st
from theming.error_dashboard import render_error_dashboard

st.set_page_config(layout="wide")
render_error_dashboard()
```

### Render Summary Widget

```python
from theming.error_dashboard import render_error_summary_widget

# In your sidebar or main page
render_error_summary_widget()
```

### Inline Error Notifications

```python
from theming.error_dashboard import render_inline_error_notification

render_inline_error_notification(
    error_type="ThemeLoadError",
    message="Failed to load theme",
    details={'theme': 'custom', 'reason': 'File not found'},
    severity="error"
)
```

### Toast Notifications

```python
from theming.error_dashboard import render_error_toast

render_error_toast(
    message="Theme loaded successfully!",
    severity="success"
)
```

## Integration Examples

### Theme Manager Integration

```python
from theming.theme_manager import ThemeManager
from theming.error_handler import get_error_handler

class ThemeManager:
    def __init__(self):
        self.error_handler = get_error_handler()
        # ...
    
    def load_theme(self, theme_name: str):
        try:
            # Load theme
            theme = self._load_theme_file(theme_name)
            return theme
        except Exception as e:
            return self.error_handler.handle_theme_load_error(
                theme_name=theme_name,
                error=e,
                fallback_callback=self._get_fallback_theme
            )
    
    def _get_fallback_theme(self):
        return self.themes.get('shadcn-default')
```

### Component Integration

```python
from components.shadcn_base import ShadcnComponent
from theming.error_handler import get_error_handler

class Card(ShadcnComponent):
    def render(self, **kwargs):
        handler = get_error_handler()
        
        try:
            # Render component
            self._render_card(**kwargs)
        except Exception as e:
            handler.handle_component_error(
                component_name="Card",
                error=e,
                fallback_callback=lambda: st.container()
            )
```

### CSS Generator Integration

```python
from theming.css_generator import CSSGenerator
from theming.error_handler import get_error_handler

class CSSGenerator:
    def generate_full_css(self):
        handler = get_error_handler()
        
        try:
            css = self._generate_css()
            return css
        except Exception as e:
            return handler.handle_css_generation_error(
                theme_name=self.theme.name,
                error=e,
                fallback_callback=self._generate_minimal_css
            )
    
    def _generate_minimal_css(self):
        return "/* Minimal fallback CSS */"
```

## Best Practices

### 1. Always Use Specific Exceptions

```python
# Good
raise ThemeLoadError(theme_name="custom", reason="File not found")

# Avoid
raise Exception("Theme load failed")
```

### 2. Provide Context

```python
handler.handle_error(
    error=e,
    context={
        'operation': 'theme_switch',
        'from_theme': 'dark',
        'to_theme': 'light',
        'user_id': 'user123'
    }
)
```

### 3. Use Fallback Callbacks

```python
# Always provide fallback for critical operations
theme = handler.handle_theme_load_error(
    theme_name=name,
    error=e,
    fallback_callback=get_default_theme  # Always provide fallback
)
```

### 4. Monitor Error Dashboard

```python
# Add error summary to your app
with st.sidebar:
    render_error_summary_widget()
```

### 5. Export Reports Regularly

```python
# In production, export reports periodically
if datetime.now().hour == 0:  # Daily at midnight
    handler.export_error_report(f'logs/daily_report_{date}.json')
```

## Configuration

### Custom Logger

```python
import logging

# Create custom logger
logger = logging.getLogger("my_theme_logger")
logger.setLevel(logging.DEBUG)

# Create handler with custom logger
handler = ErrorHandler(logger=logger)
```

### Adjust Recovery Attempts

```python
handler = ErrorHandler()
handler.max_recovery_attempts = 5  # Default is 3
```

### Adjust History Size

```python
handler = ErrorHandler()
handler.max_history_size = 200  # Default is 100
```

## Error Severity Levels

- **error**: Critical errors that prevent functionality
- **warning**: Non-critical issues with fallback available
- **info**: Informational messages

```python
handler.handle_error(error, severity='error')    # Red notification
handler.handle_error(error, severity='warning')  # Yellow notification
handler.handle_error(error, severity='info')     # Blue notification
```

## Testing

### Simulate Errors

```python
from theming.theme_errors import ThemeLoadError
from theming.error_handler import get_error_handler

handler = get_error_handler()

# Simulate error
error = ThemeLoadError("test-theme", "Test error")
handler.handle_error(error)

# Check report
report = handler.get_error_report()
assert report['total_errors'] == 1
```

### Test Recovery

```python
def test_recovery():
    handler = ErrorHandler()
    
    call_count = 0
    def fallback():
        nonlocal call_count
        call_count += 1
        return "fallback"
    
    result = handler._attempt_recovery("test_op", fallback)
    assert result == "fallback"
    assert call_count == 1
```

## Troubleshooting

### Errors Not Showing in Dashboard

1. Check if error handler is initialized
2. Verify Streamlit is available
3. Check if errors are being handled with `notify_user=True`

### Recovery Not Working

1. Check recovery attempt limit (default: 3)
2. Verify fallback callback is provided
3. Check logs for recovery attempt messages

### Reports Not Exporting

1. Verify logs directory exists
2. Check file permissions
3. Review error handler logs

## API Reference

### ErrorHandler Methods

- `handle_error(error, context, notify_user, severity)`: Handle any error
- `handle_theme_load_error(theme_name, error, fallback_callback)`: Handle theme load error
- `handle_css_generation_error(theme_name, error, fallback_callback)`: Handle CSS error
- `handle_css_injection_error(error)`: Handle CSS injection error
- `handle_component_error(component_name, error, fallback_callback)`: Handle component error
- `get_error_report()`: Get error statistics
- `export_error_report(filepath)`: Export report to JSON
- `clear_history()`: Clear error history

### Dashboard Functions

- `render_error_dashboard(error_handler)`: Render full dashboard
- `render_error_summary_widget(error_handler)`: Render summary widget
- `render_inline_error_notification(error_type, message, details, severity)`: Inline notification
- `render_error_toast(message, severity, duration)`: Toast notification

## See Also

- [Theme System Guide](THEME_SYSTEM_GUIDE.md)
- [Component Development Guide](../components/README.md)
- [CSS Generator Reference](CSS_GENERATOR_REFERENCE.md)
