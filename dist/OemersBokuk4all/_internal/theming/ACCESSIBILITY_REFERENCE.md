# Accessibility Module Reference

Complete API reference for the accessibility module.

## Classes

### ContrastChecker

Checks color contrast ratios according to WCAG 2.1.

#### Methods

##### `hex_to_rgb(hex_color: str) -> Tuple[int, int, int]`

Convert hex color to RGB tuple.

**Parameters:**
- `hex_color` (str): Color in hex format (e.g., "#ffffff" or "ffffff")

**Returns:**
- Tuple[int, int, int]: RGB values (0-255)

**Example:**
```python
rgb = ContrastChecker.hex_to_rgb("#3b82f6")
# Returns: (59, 130, 246)
```

##### `get_relative_luminance(rgb: Tuple[int, int, int]) -> float`

Calculate relative luminance according to WCAG formula.

**Parameters:**
- `rgb` (Tuple[int, int, int]): RGB values (0-255)

**Returns:**
- float: Relative luminance (0-1)

##### `calculate_contrast_ratio(color1: str, color2: str) -> float`

Calculate contrast ratio between two colors.

**Parameters:**
- `color1` (str): First color (hex format)
- `color2` (str): Second color (hex format)

**Returns:**
- float: Contrast ratio (1-21)

**Example:**
```python
ratio = ContrastChecker.calculate_contrast_ratio("#000000", "#ffffff")
# Returns: 21.0
```

##### `check_contrast(foreground: str, background: str, is_large_text: bool = False) -> ContrastResult`

Check if color combination meets WCAG standards.

**Parameters:**
- `foreground` (str): Foreground color (hex)
- `background` (str): Background color (hex)
- `is_large_text` (bool): Whether text is large (18pt+ or 14pt+ bold)

**Returns:**
- ContrastResult: Detailed contrast information

**Example:**
```python
result = ContrastChecker.check_contrast("#000000", "#ffffff")
print(f"Ratio: {result.ratio:.2f}:1")
print(f"Passes AA: {result.passes_aa_normal}")
```

---

### ColorBlindnessSimulator

Simulates how colors appear to people with color blindness.

#### Methods

##### `simulate_protanopia(hex_color: str) -> str`

Simulate red-blindness (protanopia).

**Parameters:**
- `hex_color` (str): Original color (hex format)

**Returns:**
- str: Simulated color (hex format)

##### `simulate_deuteranopia(hex_color: str) -> str`

Simulate green-blindness (deuteranopia).

##### `simulate_tritanopia(hex_color: str) -> str`

Simulate blue-blindness (tritanopia).

##### `simulate_achromatopsia(hex_color: str) -> str`

Simulate total color blindness (achromatopsia).

##### `simulate(hex_color: str, cb_type: ColorBlindnessType) -> str`

Simulate color blindness for a given color.

**Parameters:**
- `hex_color` (str): Color in hex format
- `cb_type` (ColorBlindnessType): Type of color blindness

**Returns:**
- str: Simulated color in hex format

**Example:**
```python
simulated = ColorBlindnessSimulator.simulate(
    "#ff0000",
    ColorBlindnessType.PROTANOPIA
)
```

---

### KeyboardNavigationHelper

Provides keyboard navigation support.

#### Methods

##### `get_keyboard_nav_css() -> str`

Generate CSS for keyboard navigation.

**Returns:**
- str: CSS code

**Example:**
```python
css = KeyboardNavigationHelper.get_keyboard_nav_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

##### `get_skip_to_main_html() -> str`

Generate skip to main content link.

**Returns:**
- str: HTML code

---

### ARIAHelper

Provides ARIA labels and attributes.

#### Methods

##### `get_button_aria(label: str, pressed: Optional[bool] = None, expanded: Optional[bool] = None, disabled: bool = False) -> str`

Generate ARIA attributes for button.

**Parameters:**
- `label` (str): Button label
- `pressed` (Optional[bool]): Toggle state
- `expanded` (Optional[bool]): Expansion state
- `disabled` (bool): Disabled state

**Returns:**
- str: ARIA attributes

**Example:**
```python
aria = ARIAHelper.get_button_aria("Save", pressed=False)
# Returns: 'aria-label="Save" aria-pressed="false"'
```

##### `get_input_aria(label: str, required: bool = False, invalid: bool = False, describedby: Optional[str] = None) -> str`

Generate ARIA attributes for input.

**Parameters:**
- `label` (str): Input label
- `required` (bool): Required field
- `invalid` (bool): Validation error
- `describedby` (Optional[str]): Description element ID

**Returns:**
- str: ARIA attributes

##### `get_dialog_aria(label: str, modal: bool = True) -> str`

Generate ARIA attributes for dialog.

##### `get_alert_aria(live: str = "polite") -> str`

Generate ARIA attributes for alert.

##### `get_navigation_aria(label: str) -> str`

Generate ARIA attributes for navigation.

---

### FocusManager

Manages focus indicators and focus trapping.

#### Methods

##### `get_focus_trap_js(container_id: str) -> str`

Generate JavaScript for focus trapping in modals.

**Parameters:**
- `container_id` (str): Container element ID

**Returns:**
- str: JavaScript code

**Example:**
```python
js = FocusManager.get_focus_trap_js("modal-container")
st.markdown(js, unsafe_allow_html=True)
```

##### `get_focus_indicator_css() -> str`

Generate enhanced focus indicator CSS.

**Returns:**
- str: CSS code

---

### ScreenReaderHelper

Provides screen reader support.

#### Methods

##### `get_sr_only_css() -> str`

Generate CSS for screen-reader-only content.

**Returns:**
- str: CSS code

##### `wrap_sr_only(text: str) -> str`

Wrap text in screen-reader-only span.

**Parameters:**
- `text` (str): Text to wrap

**Returns:**
- str: HTML code

**Example:**
```python
sr_text = ScreenReaderHelper.wrap_sr_only("Additional info")
# Returns: '<span class="sr-only">Additional info</span>'
```

##### `get_live_region_html(region_id: str, politeness: str = "polite") -> str`

Generate live region for dynamic content announcements.

**Parameters:**
- `region_id` (str): Region element ID
- `politeness` (str): "polite" or "assertive"

**Returns:**
- str: HTML code

##### `announce(region_id: str, message: str) -> str`

Generate JavaScript to announce message to screen readers.

**Parameters:**
- `region_id` (str): Live region ID
- `message` (str): Message to announce

**Returns:**
- str: JavaScript code

---

### TextScalingHelper

Ensures proper text scaling support.

#### Methods

##### `get_responsive_text_css() -> str`

Generate CSS for responsive text scaling.

**Returns:**
- str: CSS code

**Example:**
```python
css = TextScalingHelper.get_responsive_text_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

---

### AccessibilityAuditor

Audits themes and components for accessibility issues.

#### Methods

##### `audit_theme(theme_data: Dict[str, Any]) -> AccessibilityReport`

Perform comprehensive accessibility audit on theme.

**Parameters:**
- `theme_data` (Dict[str, Any]): Theme data dictionary

**Returns:**
- AccessibilityReport: Audit findings

**Example:**
```python
auditor = AccessibilityAuditor()
report = auditor.audit_theme(theme_data)
print(f"Score: {report.overall_score}%")
```

##### `generate_report_html(report: AccessibilityReport) -> str`

Generate HTML report of accessibility audit.

**Parameters:**
- `report` (AccessibilityReport): Audit report

**Returns:**
- str: HTML report

---

### ColorBlindnessFriendlyThemeGenerator

Generates color blindness friendly themes.

#### Methods

##### `generate_high_contrast_theme(base_theme: Dict[str, Any]) -> Dict[str, Any]`

Generate high contrast version of theme.

**Parameters:**
- `base_theme` (Dict[str, Any]): Base theme data

**Returns:**
- Dict[str, Any]: High contrast theme

**Example:**
```python
hc_theme = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(
    base_theme
)
```

##### `generate_colorblind_safe_theme(base_theme: Dict[str, Any]) -> Dict[str, Any]`

Generate colorblind-safe theme using patterns and shapes.

**Parameters:**
- `base_theme` (Dict[str, Any]): Base theme data

**Returns:**
- Dict[str, Any]: Colorblind-safe theme

---

## Data Classes

### ContrastResult

Result of contrast check.

**Attributes:**
- `ratio` (float): Contrast ratio
- `passes_aa_normal` (bool): Passes WCAG AA for normal text
- `passes_aa_large` (bool): Passes WCAG AA for large text
- `passes_aaa_normal` (bool): Passes WCAG AAA for normal text
- `passes_aaa_large` (bool): Passes WCAG AAA for large text
- `recommendation` (str): Human-readable recommendation

### AccessibilityReport

Comprehensive accessibility report.

**Attributes:**
- `theme_name` (str): Name of audited theme
- `contrast_issues` (List[Dict]): List of contrast issues
- `keyboard_nav_issues` (List[str]): Keyboard navigation issues
- `aria_issues` (List[str]): ARIA-related issues
- `focus_issues` (List[str]): Focus management issues
- `overall_score` (float): Overall score (0-100)
- `recommendations` (List[str]): List of recommendations

---

## Enums

### ContrastLevel

WCAG Contrast Levels.

**Values:**
- `AAA_LARGE` = 4.5
- `AA_NORMAL` = 4.5
- `AA_LARGE` = 3.0
- `AAA_NORMAL` = 7.0

### ColorBlindnessType

Types of color blindness.

**Values:**
- `PROTANOPIA` = "protanopia" (Red-blind)
- `DEUTERANOPIA` = "deuteranopia" (Green-blind)
- `TRITANOPIA` = "tritanopia" (Blue-blind)
- `ACHROMATOPSIA` = "achromatopsia" (Total color blindness)

---

## Usage Examples

### Complete Accessibility Setup

```python
import streamlit as st
from theming.accessibility import (
    KeyboardNavigationHelper,
    ScreenReaderHelper,
    TextScalingHelper,
    FocusManager
)

# Inject all accessibility CSS
st.markdown(f"""
<style>
{KeyboardNavigationHelper.get_keyboard_nav_css()}
{ScreenReaderHelper.get_sr_only_css()}
{TextScalingHelper.get_responsive_text_css()}
{FocusManager.get_focus_indicator_css()}
</style>
""", unsafe_allow_html=True)

# Add skip link
st.markdown(
    KeyboardNavigationHelper.get_skip_to_main_html(),
    unsafe_allow_html=True
)

# Main content
st.markdown('<main id="main-content">', unsafe_allow_html=True)
# Your app content
st.markdown('</main>', unsafe_allow_html=True)
```

### Checking Theme Accessibility

```python
from theming.accessibility import (
    ContrastChecker,
    AccessibilityAuditor
)

# Check specific color pair
result = ContrastChecker.check_contrast("#000000", "#ffffff")
if not result.passes_aa_normal:
    print(f"Warning: {result.recommendation}")

# Audit entire theme
auditor = AccessibilityAuditor()
report = auditor.audit_theme(theme_data)

if report.overall_score < 80:
    print("Theme needs accessibility improvements:")
    for rec in report.recommendations:
        print(f"- {rec}")
```

### Creating Accessible Components

```python
from theming.accessibility import ARIAHelper, ScreenReaderHelper

# Accessible button
button_aria = ARIAHelper.get_button_aria("Save document")
sr_text = ScreenReaderHelper.wrap_sr_only("to disk")

st.markdown(f"""
<button {button_aria} class="focus-ring">
    Save {sr_text}
</button>
""", unsafe_allow_html=True)

# Accessible form
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
```

---

## See Also

- [Accessibility Guide](../docs/ACCESSIBILITY_GUIDE.md)
- [Quick Reference](../docs/ACCESSIBILITY_QUICK_REFERENCE.md)
- [Demo](../demo_accessibility.py)
- [Tests](../tests/test_accessibility.py)
