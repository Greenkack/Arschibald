# Accessibility Quick Reference

Quick reference for common accessibility tasks.

## Contrast Checking

```python
from theming.accessibility import ContrastChecker

# Check contrast
result = ContrastChecker.check_contrast("#000000", "#ffffff")
print(f"Ratio: {result.ratio:.2f}:1")
print(f"Passes AA: {result.passes_aa_normal}")
```

## Color Blindness Simulation

```python
from theming.accessibility import ColorBlindnessSimulator, ColorBlindnessType

# Simulate protanopia (red-blind)
simulated = ColorBlindnessSimulator.simulate(
    "#ff0000",
    ColorBlindnessType.PROTANOPIA
)
```

## Keyboard Navigation

```python
from theming.accessibility import KeyboardNavigationHelper

# Add keyboard navigation CSS
css = KeyboardNavigationHelper.get_keyboard_nav_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Add skip link
skip_link = KeyboardNavigationHelper.get_skip_to_main_html()
st.markdown(skip_link, unsafe_allow_html=True)
```

## ARIA Labels

```python
from theming.accessibility import ARIAHelper

# Button
aria = ARIAHelper.get_button_aria("Save", pressed=False)

# Input
aria = ARIAHelper.get_input_aria("Email", required=True)

# Dialog
aria = ARIAHelper.get_dialog_aria("Confirm", modal=True)

# Alert
aria = ARIAHelper.get_alert_aria(live="polite")
```

## Focus Management

```python
from theming.accessibility import FocusManager

# Focus indicators CSS
css = FocusManager.get_focus_indicator_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Focus trap for modal
js = FocusManager.get_focus_trap_js("modal-id")
st.markdown(js, unsafe_allow_html=True)
```

## Screen Reader Support

```python
from theming.accessibility import ScreenReaderHelper

# Screen reader only text
sr_text = ScreenReaderHelper.wrap_sr_only("Hidden text")

# Live region
live_region = ScreenReaderHelper.get_live_region_html("announcements")
st.markdown(live_region, unsafe_allow_html=True)

# Announce message
announcement = ScreenReaderHelper.announce("announcements", "Success!")
st.markdown(announcement, unsafe_allow_html=True)
```

## Text Scaling

```python
from theming.accessibility import TextScalingHelper

# Responsive text CSS
css = TextScalingHelper.get_responsive_text_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

## Theme Auditing

```python
from theming.accessibility import AccessibilityAuditor

# Audit theme
auditor = AccessibilityAuditor()
report = auditor.audit_theme(theme_data)

print(f"Score: {report.overall_score}%")
print(f"Issues: {len(report.contrast_issues)}")

# Generate HTML report
html = auditor.generate_report_html(report)
```

## Colorblind-Friendly Themes

```python
from theming.accessibility import ColorBlindnessFriendlyThemeGenerator

# High contrast theme
hc_theme = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(
    base_theme
)

# Colorblind-safe theme
cb_theme = ColorBlindnessFriendlyThemeGenerator.generate_colorblind_safe_theme(
    base_theme
)
```

## WCAG Standards

| Text Type | Level AA | Level AAA |
|-----------|----------|-----------|
| Normal | 4.5:1 | 7:1 |
| Large (18pt+) | 3:1 | 4.5:1 |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Next element |
| Shift+Tab | Previous element |
| Enter/Space | Activate |
| Esc | Close modal |

## Common ARIA Attributes

- `aria-label` - Accessible name
- `aria-describedby` - Description reference
- `aria-pressed` - Toggle state
- `aria-expanded` - Expansion state
- `aria-invalid` - Validation error
- `aria-required` - Required field
- `aria-live` - Dynamic updates
- `role` - Element purpose

## Testing Checklist

- [ ] Contrast ratios meet WCAG AA
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Screen reader compatible
- [ ] Text scales to 200%
- [ ] Color blindness tested
- [ ] Touch targets 44x44px

## Quick Setup

```python
import streamlit as st
from theming.accessibility import (
    KeyboardNavigationHelper,
    ScreenReaderHelper,
    TextScalingHelper
)

# Inject all accessibility CSS
st.markdown(f"""
<style>
{KeyboardNavigationHelper.get_keyboard_nav_css()}
{ScreenReaderHelper.get_sr_only_css()}
{TextScalingHelper.get_responsive_text_css()}
</style>
""", unsafe_allow_html=True)

# Add skip link
st.markdown(
    KeyboardNavigationHelper.get_skip_to_main_html(),
    unsafe_allow_html=True
)

# Main content
st.markdown('<main id="main-content">', unsafe_allow_html=True)
# Your app content here
st.markdown('</main>', unsafe_allow_html=True)
```

## Resources

- [Full Guide](ACCESSIBILITY_GUIDE.md)
- [Demo](../demo_accessibility.py)
- [Tests](../tests/test_accessibility.py)
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
