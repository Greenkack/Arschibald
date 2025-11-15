# Error Handling Quick Reference

Quick reference guide for Theme System error handling.

## Quick Start

```python
from theming.error_handler import get_error_handler

# Get global handler
handler = get_error_handler()

# Handle an error
try:
    # Your code
    pass
except Exception as e:
    handler.handle_error(e, notify_user=True)
```

## Common Patterns

### Theme Load with Fallback

```python
try:
    theme = load_theme("custom")
except Exception as e:
    theme = handler.handle_theme_load_error(
        "custom", e, lambda: get_default_theme()
    )
```

### Component with Fallback

```python
try:
    card.render(title="Test")
except Exception as e:
    handler.handle_component_error(
        "Card", e, lambda: st.container()
    )
```

### CSS Generation with Fallback

```python
try:
    css = generate_css(theme)
except Exception as e:
    css = handler.handle_css_generation_error(
        theme.name, e, lambda: "/* fallback */"
    )
```

## Error Dashboard

### Full Dashboard

```python
from theming.error_dashboard import render_error_dashboard

render_error_dashboard()
```

### Summary Widget

```python
from theming.error_dashboard import render_error_summary_widget

render_error_summary_widget()
```

### Notifications

```python
from theming.error_dashboard import (
    render_inline_error_notification,
    render_error_toast
)

# Inline
render_inline_error_notification(
    "Error", "Message", severity="error"
)

# Toast
render_error_toast("Success!", "success")
```

## Exception Types

| Exception | Use Case |
|-----------|----------|
| `ThemeLoadError` | Theme file loading failed |
| `ThemeValidationError` | Theme validation failed |
| `ThemeNotFoundError` | Theme doesn't exist |
| `CSSGenerationError` | CSS generation failed |
| `CSSInjectionError` | CSS injection failed |
| `ComponentRenderError` | Component rendering failed |
| `TokenNotFoundError` | Design token not found |

## Error Reports

```python
# Get report
report = handler.get_error_report()

# Export report
handler.export_error_report('logs/report.json')

# Clear history
handler.clear_history()
```

## Severity Levels

- `error`: Critical (red notification)
- `warning`: Non-critical (yellow notification)
- `info`: Informational (blue notification)

```python
handler.handle_error(e, severity='warning')
```

## Configuration

```python
handler = ErrorHandler()
handler.max_recovery_attempts = 5  # Default: 3
handler.max_history_size = 200     # Default: 100
```

## Integration Example

```python
from theming.error_handler import get_error_handler

class MyComponent:
    def __init__(self):
        self.error_handler = get_error_handler()
    
    def render(self):
        try:
            self._do_render()
        except Exception as e:
            self.error_handler.handle_component_error(
                "MyComponent", e, self._render_fallback
            )
    
    def _render_fallback(self):
        st.info("Using fallback rendering")
```

## Best Practices

1. ✅ Use specific exception types
2. ✅ Always provide fallback callbacks
3. ✅ Include context in error handling
4. ✅ Monitor error dashboard regularly
5. ✅ Export reports for analysis

## See Also

- [Full Reference](../theming/ERROR_HANDLING_REFERENCE.md)
- [Theme System Guide](THEME_SYSTEM_GUIDE.md)
