

# Accessibility (A11y) Guide

Complete guide to accessibility features in the shadcn/ui theme system.

## Table of Contents

1. [Overview](#overview)
2. [WCAG Compliance](#wcag-compliance)
3. [Contrast Checking](#contrast-checking)
4. [Color Blindness Support](#color-blindness-support)
5. [Keyboard Navigation](#keyboard-navigation)
6. [ARIA Labels](#aria-labels)
7. [Focus Management](#focus-management)
8. [Screen Reader Support](#screen-reader-support)
9. [Text Scaling](#text-scaling)
10. [Theme Auditing](#theme-auditing)
11. [Best Practices](#best-practices)

## Overview

The accessibility module provides comprehensive tools to ensure your application meets WCAG 2.1 Level AA standards and is usable by everyone, including people with disabilities.

### Key Features

- ✅ WCAG 2.1 Level AA/AAA contrast checking
- ✅ Color blindness simulation and safe themes
- ✅ Keyboard navigation support
- ✅ ARIA labels and attributes
- ✅ Focus indicators and management
- ✅ Screen reader support
- ✅ Text scaling up to 200%
- ✅ Automated accessibility auditing

## WCAG Compliance

### What is WCAG?

WCAG (Web Content Accessibility Guidelines) 2.1 is the international standard for web accessibility. It has three levels:

- **Level A:** Basic accessibility (minimum)
- **Level AA:** Recommended standard (legal requirement in many jurisdictions)
- **Level AAA:** Enhanced accessibility (gold standard)

### Contrast Requirements

| Text Type | Level AA | Level AAA |
|-----------|----------|-----------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18pt+ or 14pt+ bold) | 3:1 | 4.5:1 |

## Contrast Checking

### Basic Usage

```python
from theming.accessibility import ContrastChecker

# Check contrast between two colors
result = ContrastChecker.check_contrast(
    foreground="#000000",
    background="#ffffff",
    is_large_text=False
)

print(f"Contrast Ratio: {result.ratio:.2f}:1")
print(f"Passes WCAG AA: {result.passes_aa_normal}")
print(f"Passes WCAG AAA: {result.passes_aaa_normal}")
print(f"Recommendation: {result.recommendation}")
```

### Example Output

```
Contrast Ratio: 21.00:1
Passes WCAG AA: True
Passes WCAG AAA: True
Recommendation: ✅ Excellent contrast (WCAG AAA)
```

### Checking Theme Colors

```python
# Check all critical color combinations in a theme
theme_colors = {
    'foreground': '#000000',
    'background': '#ffffff',
    'primary': '#3b82f6',
    'primary_foreground': '#ffffff'
}

# Check body text
body_result = ContrastChecker.check_contrast(
    theme_colors['foreground'],
    theme_colors['background']
)

# Check button text
button_result = ContrastChecker.check_contrast(
    theme_colors['primary_foreground'],
    theme_colors['primary']
)
```

## Color Blindness Support

### Types of Color Blindness

1. **Protanopia** (Red-blind) - ~1% of males
2. **Deuteranopia** (Green-blind) - ~1% of males
3. **Tritanopia** (Blue-blind) - ~0.01% of people
4. **Achromatopsia** (Total color blindness) - ~0.003% of people

### Simulating Color Blindness

```python
from theming.accessibility import ColorBlindnessSimulator, ColorBlindnessType

original_color = "#3b82f6"  # Blue

# Simulate different types
protanopia = ColorBlindnessSimulator.simulate(
    original_color, 
    ColorBlindnessType.PROTANOPIA
)

deuteranopia = ColorBlindnessSimulator.simulate(
    original_color,
    ColorBlindnessType.DEUTERANOPIA
)

tritanopia = ColorBlindnessSimulator.simulate(
    original_color,
    ColorBlindnessType.TRITANOPIA
)

achromatopsia = ColorBlindnessSimulator.simulate(
    original_color,
    ColorBlindnessType.ACHROMATOPSIA
)
```

### Generating Colorblind-Friendly Themes

```python
from theming.accessibility import ColorBlindnessFriendlyThemeGenerator

# Generate high contrast theme
high_contrast = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(
    base_theme_data
)

# Generate colorblind-safe theme
colorblind_safe = ColorBlindnessFriendlyThemeGenerator.generate_colorblind_safe_theme(
    base_theme_data
)
```

### Design Tips for Color Blindness

- ❌ **Don't** rely solely on color to convey information
- ✅ **Do** use patterns, shapes, and text labels
- ✅ **Do** use blue and orange (safe for most types)
- ❌ **Avoid** red-green combinations
- ✅ **Do** ensure sufficient contrast
- ✅ **Do** test with simulation tools

## Keyboard Navigation

### CSS for Keyboard Navigation

```python
from theming.accessibility import KeyboardNavigationHelper

# Get keyboard navigation CSS
css = KeyboardNavigationHelper.get_keyboard_nav_css()

# Inject into Streamlit
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Skip to Main Content

```python
# Add skip link for keyboard users
skip_link = KeyboardNavigationHelper.get_skip_to_main_html()
st.markdown(skip_link, unsafe_allow_html=True)

# Mark main content
st.markdown('<div id="main-content">', unsafe_allow_html=True)
# ... your content ...
st.markdown('</div>', unsafe_allow_html=True)
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Move to next focusable element |
| Shift + Tab | Move to previous element |
| Enter/Space | Activate buttons and links |
| Arrow Keys | Navigate within components |
| Esc | Close modals and dropdowns |

## ARIA Labels

### Button ARIA

```python
from theming.accessibility import ARIAHelper

# Basic button
aria = ARIAHelper.get_button_aria("Save document")
# Output: aria-label="Save document"

# Toggle button
aria = ARIAHelper.get_button_aria("Mute", pressed=False)
# Output: aria-label="Mute" aria-pressed="false"

# Expandable button
aria = ARIAHelper.get_button_aria("Menu", expanded=True)
# Output: aria-label="Menu" aria-expanded="true"

# Disabled button
aria = ARIAHelper.get_button_aria("Submit", disabled=True)
# Output: aria-label="Submit" aria-disabled="true"
```

### Input ARIA

```python
# Basic input
aria = ARIAHelper.get_input_aria("Email address")

# Required input
aria = ARIAHelper.get_input_aria("Name", required=True)

# Invalid input
aria = ARIAHelper.get_input_aria("Email", invalid=True)

# Input with description
aria = ARIAHelper.get_input_aria(
    "Password",
    describedby="password-help"
)
```

### Dialog ARIA

```python
# Modal dialog
aria = ARIAHelper.get_dialog_aria("Confirm deletion", modal=True)
# Output: role="dialog" aria-label="Confirm deletion" aria-modal="true"
```

### Alert ARIA

```python
# Polite alert (doesn't interrupt)
aria = ARIAHelper.get_alert_aria(live="polite")

# Assertive alert (interrupts immediately)
aria = ARIAHelper.get_alert_aria(live="assertive")
```

### Navigation ARIA

```python
# Navigation landmark
aria = ARIAHelper.get_navigation_aria("Main navigation")
# Output: role="navigation" aria-label="Main navigation"
```

## Focus Management

### Focus Indicators

```python
from theming.accessibility import FocusManager

# Get enhanced focus indicator CSS
css = FocusManager.get_focus_indicator_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Focus Trapping (for Modals)

```python
# Trap focus inside modal
focus_trap_js = FocusManager.get_focus_trap_js("modal-container")

st.markdown(f"""
<div id="modal-container">
    <button>First</button>
    <button>Second</button>
    <button>Last</button>
</div>
{focus_trap_js}
""", unsafe_allow_html=True)
```

### Focus Management Best Practices

1. **Visible Focus Indicators:** Always show where focus is
2. **Logical Tab Order:** Follow visual flow (left-to-right, top-to-bottom)
3. **Focus Trapping:** Keep focus inside modals
4. **Focus Restoration:** Return focus after closing modals
5. **Skip Links:** Allow skipping repetitive content

## Screen Reader Support

### Screen Reader Only Content

```python
from theming.accessibility import ScreenReaderHelper

# Hide content visually but keep for screen readers
sr_text = ScreenReaderHelper.wrap_sr_only("Additional context")

st.markdown(f"""
<button>
    Save
    {sr_text}
</button>
""", unsafe_allow_html=True)
```

### Live Regions

```python
# Create live region for announcements
live_region = ScreenReaderHelper.get_live_region_html(
    "announcements",
    politeness="polite"
)

st.markdown(live_region, unsafe_allow_html=True)

# Announce message
if form_submitted:
    announcement = ScreenReaderHelper.announce(
        "announcements",
        "Form submitted successfully"
    )
    st.markdown(announcement, unsafe_allow_html=True)
```

### Testing with Screen Readers

| Platform | Screen Reader | Cost |
|----------|--------------|------|
| Windows | NVDA | Free |
| Windows | JAWS | Commercial |
| macOS/iOS | VoiceOver | Built-in |
| Android | TalkBack | Built-in |

## Text Scaling

### Responsive Text CSS

```python
from theming.accessibility import TextScalingHelper

# Get responsive text scaling CSS
css = TextScalingHelper.get_responsive_text_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Requirements

- ✅ Text can be resized up to 200%
- ✅ No loss of content or functionality
- ✅ Use rem/em instead of px
- ✅ Flexible layouts (avoid fixed widths)
- ✅ Minimum touch target size: 44x44 pixels

### User Preferences

The CSS automatically respects:

- `prefers-reduced-motion` - Reduces animations
- `prefers-contrast` - Enhances contrast
- `prefers-color-scheme` - Dark/light mode

## Theme Auditing

### Running an Audit

```python
from theming.accessibility import AccessibilityAuditor

# Create auditor
auditor = AccessibilityAuditor()

# Audit theme
theme_data = {
    'name': 'my-theme',
    'colors': {
        'foreground': '#000000',
        'background': '#ffffff',
        'primary': '#3b82f6',
        'primary_foreground': '#ffffff',
        # ... more colors
    }
}

report = auditor.audit_theme(theme_data)

# Display results
print(f"Overall Score: {report.overall_score}%")
print(f"Contrast Issues: {len(report.contrast_issues)}")

for issue in report.contrast_issues:
    print(f"- {issue['description']}: {issue['recommendation']}")
```

### Generating HTML Report

```python
# Generate HTML report
html_report = auditor.generate_report_html(report)

# Save to file
with open("accessibility_report.html", "w") as f:
    f.write(html_report)

# Or display in Streamlit
st.markdown(html_report, unsafe_allow_html=True)
```

## Best Practices

### Color and Contrast

1. ✅ Ensure 4.5:1 contrast for normal text
2. ✅ Ensure 3:1 contrast for large text
3. ✅ Don't rely solely on color
4. ✅ Use patterns and labels
5. ✅ Test with color blindness simulators

### Keyboard Navigation

1. ✅ All interactive elements must be keyboard accessible
2. ✅ Provide visible focus indicators
3. ✅ Maintain logical tab order
4. ✅ Trap focus in modals
5. ✅ Provide skip links

### ARIA and Semantics

1. ✅ Use semantic HTML first
2. ✅ Add ARIA only when needed
3. ✅ Provide descriptive labels
4. ✅ Use landmarks (nav, main, aside)
5. ✅ Test with screen readers

### Forms

1. ✅ Label all form inputs
2. ✅ Provide clear error messages
3. ✅ Indicate required fields
4. ✅ Group related inputs
5. ✅ Provide helpful descriptions

### Images and Media

1. ✅ Provide alt text for images
2. ✅ Provide captions for videos
3. ✅ Provide transcripts for audio
4. ✅ Don't use images of text
5. ✅ Ensure decorative images are hidden from screen readers

### Testing Checklist

- [ ] Run automated accessibility audit
- [ ] Check all color contrasts
- [ ] Test keyboard navigation
- [ ] Test with screen reader
- [ ] Test at 200% zoom
- [ ] Test with color blindness simulator
- [ ] Validate ARIA attributes
- [ ] Check focus indicators
- [ ] Test form validation
- [ ] Review with real users

## Code Examples

### Complete Accessible Component

```python
import streamlit as st
from theming.accessibility import (
    ContrastChecker,
    ARIAHelper,
    KeyboardNavigationHelper,
    ScreenReaderHelper
)

# Inject accessibility CSS
st.markdown(f"""
<style>
{KeyboardNavigationHelper.get_keyboard_nav_css()}
{ScreenReaderHelper.get_sr_only_css()}
</style>
""", unsafe_allow_html=True)

# Skip link
st.markdown(KeyboardNavigationHelper.get_skip_to_main_html(), 
            unsafe_allow_html=True)

# Main content
st.markdown('<main id="main-content">', unsafe_allow_html=True)

# Accessible button
button_aria = ARIAHelper.get_button_aria("Save document", disabled=False)
st.markdown(f"""
<button {button_aria} class="focus-ring">
    Save
    {ScreenReaderHelper.wrap_sr_only("document to disk")}
</button>
""", unsafe_allow_html=True)

# Accessible input
input_aria = ARIAHelper.get_input_aria(
    "Email address",
    required=True,
    describedby="email-help"
)
st.markdown(f"""
<label for="email">Email</label>
<input type="email" id="email" {input_aria} />
<span id="email-help" class="sr-only">
    We'll never share your email
</span>
""", unsafe_allow_html=True)

st.markdown('</main>', unsafe_allow_html=True)
```

### Accessible Theme

```python
from theming.accessibility import (
    AccessibilityAuditor,
    ColorBlindnessFriendlyThemeGenerator
)

# Load base theme
base_theme = load_theme("shadcn-default")

# Audit for issues
auditor = AccessibilityAuditor()
report = auditor.audit_theme(base_theme)

if report.overall_score < 80:
    # Generate accessible version
    accessible_theme = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(
        base_theme
    )
    save_theme(accessible_theme)
```

## Resources

### Standards and Guidelines

- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM](https://webaim.org/)

### Testing Tools

- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)

### Screen Readers

- [NVDA](https://www.nvaccess.org/) (Windows, Free)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) (Windows, Commercial)
- VoiceOver (macOS/iOS, Built-in)
- TalkBack (Android, Built-in)

## Support

For questions or issues with accessibility features:

1. Check this documentation
2. Run the demo: `streamlit run demo_accessibility.py`
3. Review test cases: `tests/test_accessibility.py`
4. File an issue on GitHub

## License

This accessibility module is part of the shadcn/ui theme system and follows the same license.
