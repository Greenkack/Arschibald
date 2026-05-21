# Phase 3: Design System Definition - ABGESCHLOSSEN

**Datum**: 2025-12-09  
**Status**: COMPLETED  
**Ziel**: Zentrales Design System für konsistente UI-Gestaltung

---

## Zusammenfassung

Erstellt: `theming/ui_design_system.py` (650+ Zeilen)

Zentrales Design System mit folgenden Komponenten:
- Farb-Palette (Primary, Secondary, Status-Farben)
- Typografie-System (Schriftgrößen, Gewichte, Line-Heights)
- Spacing-System (XS bis XXXL)
- Border & Shadow Styles
- Component Variants (Button, Card, Badge)
- Responsive Breakpoints
- Icon-Mapping (Lucide Icons)
- Animation-Definitionen
- Utility Functions

---

## Design System Komponenten

### 1. Farb-Palette (ColorPalette)

#### Primärfarben
```python
PRIMARY = "#0066CC"         # Blau (Hauptfarbe)
PRIMARY_LIGHT = "#3399FF"   # Hellblau
PRIMARY_DARK = "#004C99"    # Dunkelblau
PRIMARY_HOVER = "#0052A3"   # Hover-State
```

**Verwendung**: Hauptaktionen, Links, wichtige Buttons

#### Sekundärfarben
```python
SECONDARY = "#6B7280"       # Grau
SECONDARY_LIGHT = "#9CA3AF" # Hellgrau
SECONDARY_DARK = "#4B5563"  # Dunkelgrau
```

**Verwendung**: Sekundäre Buttons, neutrale Elemente

#### Statusfarben
```python
SUCCESS = "#10B981"   # Grün - Erfolg
WARNING = "#F59E0B"   # Orange - Warnung
ERROR = "#EF4444"     # Rot - Fehler
INFO = "#3B82F6"      # Hellblau - Information
```

**Verwendung**: Alerts, Badges, Status-Anzeigen

#### Feature-Spezifische Farben
```python
SOLAR_YELLOW = "#FCD34D"        # PV-Anlagen
HEAT_PUMP_ORANGE = "#FB923C"    # Wärmepumpen
CRM_BLUE = "#60A5FA"            # CRM
CONTROLLING_PURPLE = "#A78BFA"  # Controlling
```

**Verwendung**: Feature-spezifische Cards, Icons, Badges

#### Neutrale Farben
```python
BACKGROUND_LIGHT = "#FFFFFF"    # Hintergrund
BACKGROUND_DARK = "#F9FAFB"     # Alternativ-Hintergrund
BORDER = "#E5E7EB"              # Rahmen
TEXT_PRIMARY = "#111827"        # Haupttext
TEXT_SECONDARY = "#6B7280"      # Sekundärtext
```

#### Dark Mode (vorbereitet für Phase 17)
```python
DARK_BACKGROUND = "#1F2937"
DARK_SURFACE = "#111827"
DARK_TEXT_PRIMARY = "#F9FAFB"
```

---

### 2. Typografie (Typography)

#### Font Families
```python
FONT_FAMILY_PRIMARY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
FONT_FAMILY_MONOSPACE = "'Fira Code', 'Courier New', monospace"
```

**Hinweis**: Inter ist moderne, professionelle Sans-Serif Font (Google Fonts)

#### Font Sizes
```python
H1: 2.5rem (40px)   # Seiten-Titel
H2: 2rem (32px)     # Haupt-Sections
H3: 1.75rem (28px)  # Sub-Sections
H4: 1.5rem (24px)   # Card Titles
H5: 1.25rem (20px)  # Kleinere Titles
H6: 1rem (16px)     # Labels
Body: 1rem (16px)   # Fließtext
Body Small: 0.875rem (14px)  # Kleinerer Text
Caption: 0.75rem (12px)      # Captions, Hints
Tiny: 0.625rem (10px)        # Badge-Text
```

#### Font Weights
```python
LIGHT = 300
REGULAR = 400       # Standard
MEDIUM = 500
SEMIBOLD = 600      # Buttons
BOLD = 700          # Headings
EXTRABOLD = 800     # Hero-Sections
```

#### Line Heights
```python
TIGHT = 1.25        # Headings
NORMAL = 1.5        # Body Text
RELAXED = 1.75      # Längere Texte
LOOSE = 2           # Lesbare Paragraphen
```

---

### 3. Spacing System (Spacing)

```python
XS = 4px      # Sehr enge Abstände
SM = 8px      # Kleine Abstände
MD = 16px     # Standard Abstände
LG = 24px     # Große Abstände
XL = 32px     # Sehr große Abstände
XXL = 48px    # Section-Abstände
XXXL = 64px   # Page-Abstände
```

#### Component-Spezifisches Spacing
```python
CARD_PADDING = 16px
BUTTON_PADDING_X = 16px
BUTTON_PADDING_Y = 8px
INPUT_PADDING = 12px
CONTAINER_PADDING = 24px
SECTION_GAP = 32px
```

**Verwendung**:
```python
from theming.ui_design_system import Spacing

# Padding für Container
st.markdown(f'<div style="padding: {Spacing.CONTAINER_PADDING};">...</div>')

# Gap zwischen Sections
st.markdown(f'<div style="margin-bottom: {Spacing.SECTION_GAP};">...</div>')
```

---

### 4. Border & Shadows

#### Border Radius
```python
RADIUS_NONE = 0
RADIUS_SM = 4px     # Kleine Ecken
RADIUS_MD = 8px     # Standard (Cards, Buttons)
RADIUS_LG = 12px    # Große Ecken
RADIUS_XL = 16px    # Sehr runde Ecken
RADIUS_FULL = 9999px  # Pill-Shape (Badges)
```

#### Box Shadows
```python
SHADOW_SM = "0 1px 2px 0 rgba(0,0,0,0.05)"              # Subtle
SHADOW_MD = "0 4px 6px -1px rgba(0,0,0,0.1)"            # Standard (Cards)
SHADOW_LG = "0 10px 15px -3px rgba(0,0,0,0.1)"          # Hover-State
SHADOW_XL = "0 20px 25px -5px rgba(0,0,0,0.1)"          # Elevated
SHADOW_2XL = "0 25px 50px -12px rgba(0,0,0,0.25)"       # Modal/Dialog
```

**Verwendung**: Cards sollten SHADOW_MD nutzen, Hover-State SHADOW_LG

---

### 5. Component Variants

#### Button Variants
```python
primary:      Blue Background, White Text
secondary:    Gray Background, White Text
outline:      Transparent, Blue Border, Blue Text
ghost:        Transparent, No Border, Dark Text
destructive:  Red Background, White Text
```

#### Button Sizes
```python
sm:  32px height, 14px text   # Kompakte Buttons
md:  40px height, 16px text   # Standard Buttons
lg:  48px height, 18px text   # Prominente Buttons
```

#### Card Variants
```python
elevated:  White Background, Medium Shadow, Hover Shadow
outlined:  White Background, Border, Small Shadow on Hover
flat:      Light Gray Background, No Shadow
```

#### Badge Variants
```python
default:    Blue Background, White Text
secondary:  Gray Background, White Text
success:    Green Background, White Text
warning:    Orange Background, Dark Text
error:      Red Background, White Text
outline:    Transparent, Border, Dark Text
```

---

### 6. Responsive Breakpoints (Breakpoints)

```python
MOBILE:   < 768px    → 1 Spalte
TABLET:   768-1023px → 2 Spalten
DESKTOP:  1024-1439px → 3 Spalten
WIDE:     >= 1440px  → 4 Spalten
```

**Grid-Columns automatisch**:
```python
from theming.ui_design_system import Breakpoints

# In Streamlit
viewport_width = 1200  # Beispiel
columns = Breakpoints.get_columns_for_viewport(viewport_width)
st.columns(columns)
```

---

### 7. Icon-Mapping (Lucide Icons)

**Icon Library**: Lucide Icons (https://lucide.dev/)

#### Feature Icons
```python
SOLAR = "sun"               # PV-Anlagen
HEAT_PUMP = "flame"         # Wärmepumpen
CRM = "users"               # CRM
CONTROLLING = "bar-chart-2" # Controlling
ADMIN = "settings"          # Admin
PDF = "file-text"           # PDF
ANALYSIS = "trending-up"    # Analysis
CALCULATOR = "calculator"   # Calculator
```

#### UI Icons
```python
HOME = "home"
MENU = "menu"
CLOSE = "x"
SEARCH = "search"
FILTER = "filter"
USER = "user"
```

#### Action Icons
```python
SAVE = "save"
EDIT = "edit-2"
DELETE = "trash-2"
ADD = "plus"
DOWNLOAD = "download"
UPLOAD = "upload"
```

#### Status Icons
```python
SUCCESS = "check-circle"
WARNING = "alert-triangle"
ERROR = "x-circle"
INFO = "info"
```

**Verwendung**:
```python
from theming.ui_design_system import IconMapping

icon_name = IconMapping.get_icon("photovoltaik")  # Returns: "sun"
# Dann in shadcn/ui Component nutzen mit icon=icon_name
```

---

### 8. Animations

#### Transition Durations
```python
FAST = 150ms     # Hover-Effekte
NORMAL = 300ms   # Standard Transitions
SLOW = 500ms     # Drawer/Modal Animationen
```

#### Easing Functions
```python
EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"  # Standard
```

#### Keyframe Animations
```python
FADE_IN:        Opacity 0 → 1
SLIDE_IN_RIGHT: Transform translateX(100%) → 0
SHIMMER:        Background Position Animation (Skeleton)
```

---

## Utility Functions

### 1. apply_custom_css()

Wendet globale CSS-Styles an (Custom Scrollbar, Typography, Transitions)

```python
from theming.ui_design_system import apply_custom_css

# In gui.py oder intro_screen.py
apply_custom_css()
```

**Effekte**:
- CSS Variables für alle Farben
- Typography Styles für H1-H6
- Smooth Transitions für alle Elemente
- Custom Scrollbar (schmal, gerundet, grau)
- Card Hover Effects
- Shimmer Animation für Skeleton

---

### 2. get_component_style()

Gibt Style-Dictionary für Component zurück

```python
from theming.ui_design_system import get_component_style

# Button Style
button_style = get_component_style("button", variant="primary", size="md")
# Returns: {"background": "#0066CC", "color": "#FFFFFF", ...}

# Card Style
card_style = get_component_style("card", variant="elevated")
# Returns: {"background": "#FFFFFF", "box-shadow": "...", ...}

# Badge Style
badge_style = get_component_style("badge", variant="success")
# Returns: {"background": "#10B981", "color": "#FFFFFF"}
```

---

### 3. ColorPalette.get_status_color()

Gibt Farbe basierend auf Status-String zurück

```python
from theming.ui_design_system import ColorPalette

color = ColorPalette.get_status_color("success")  # Returns: "#10B981"
color = ColorPalette.get_status_color("active")   # Returns: "#10B981" (Grün)
color = ColorPalette.get_status_color("pending")  # Returns: "#F59E0B" (Orange)
color = ColorPalette.get_status_color("error")    # Returns: "#EF4444" (Rot)
```

---

## Integration in bestehende Komponenten

### Beispiel: Button mit Design System

```python
from theming.ui_design_system import (
    ColorPalette, Typography, Spacing, 
    BorderStyles, get_component_style
)
from components.shadcn_ui_integration import button

# Hol Style aus Design System
style = get_component_style("button", variant="primary", size="lg")

# Nutze in shadcn Button
if button("Speichern", variant="default", key="save_btn"):
    st.success("Gespeichert!")
```

### Beispiel: Card mit Custom Styling

```python
from theming.ui_design_system import ColorPalette, Spacing, Shadows
from components.shadcn_ui_integration import card

# Custom Card Style
card_css = f"""
<div style="
    background: {ColorPalette.SURFACE};
    padding: {Spacing.CARD_PADDING};
    border-radius: 8px;
    box-shadow: {Shadows.SHADOW_MD};
    transition: all 0.3s ease-in-out;
">
    <h4 style="color: {ColorPalette.TEXT_PRIMARY};">KPI Title</h4>
    <p style="font-size: 2rem; color: {ColorPalette.PRIMARY};">45.678 kWh</p>
</div>
"""
st.markdown(card_css, unsafe_allow_html=True)
```

### Beispiel: Badge mit Status-Farbe

```python
from theming.ui_design_system import ColorPalette
from components.shadcn_ui_integration import badge

status = "active"
color = ColorPalette.get_status_color(status)

badge(status.capitalize(), variant="default")  # Nutzt Design System Farbe
```

---

## Responsive Grid Layout

```python
from theming.ui_design_system import Breakpoints

# Automatische Column-Anzahl basierend auf Viewport
viewport_width = 1200  # Aus Browser (JavaScript oder Streamlit-Defaults)
columns = Breakpoints.get_columns_for_viewport(viewport_width)

# Grid Layout
cols = st.columns(columns)

for i, col in enumerate(cols):
    with col:
        card(title=f"Card {i+1}", content="Content", key=f"card_{i}")
```

---

## Dark Mode (vorbereitet)

Alle Dark Mode Farben sind bereits definiert in `ColorPalette`:

```python
DARK_BACKGROUND = "#1F2937"
DARK_SURFACE = "#111827"
DARK_TEXT_PRIMARY = "#F9FAFB"
DARK_BORDER = "#374151"
```

**Implementation in Phase 17**:
- Theme Toggle Switch
- Session State für Theme-Präferenz
- Conditional Rendering basierend auf Theme

---

## Best Practices

### 1. Farben
- IMMER `ColorPalette` nutzen (keine Hard-coded Hex-Werte)
- Status-Farben für Status-Anzeigen (`get_status_color()`)
- Feature-Farben für Feature-spezifische Elemente

### 2. Spacing
- IMMER `Spacing` Konstanten nutzen
- Konsistente Abstände zwischen Komponenten
- `SECTION_GAP` für große Abstände

### 3. Typography
- Headings IMMER mit `Typography.FONT_SIZE_H*`
- Font Weights: `BOLD` für Headings, `REGULAR` für Body
- Line Heights: `TIGHT` für Headings, `NORMAL` für Body

### 4. Shadows
- Cards: `SHADOW_MD`
- Hover-State: `SHADOW_LG`
- Modals: `SHADOW_XL` oder `SHADOW_2XL`

### 5. Responsive
- Grid Columns basierend auf `Breakpoints.get_columns_for_viewport()`
- Mobile-First Approach (1 Spalte Standard, dann erweitern)

---

## Nächste Schritte (Phase 4)

### Intro Screen Modernization

**Anwenden**:
1. `apply_custom_css()` in `intro_screen.py`
2. Hero Section mit `ColorPalette.PRIMARY`
3. Feature Cards mit `get_component_style("card", "elevated")`
4. Feature Carousel mit `IconMapping` Icons
5. Buttons mit `get_component_style("button", "primary", "lg")`

**Ziel**: Konsistente, moderne UI mit Design System

---

## Changelog

**2025-12-09 - Phase 3 Abschluss**:
- Erstellt: `theming/ui_design_system.py` (650+ Zeilen)
- Definiert: 5 Farbpaletten (Primary, Secondary, Status, Feature, Neutral)
- Definiert: Typography System (9 Font Sizes, 6 Weights, 4 Line Heights)
- Definiert: Spacing System (7 Stufen)
- Definiert: Border & Shadow Styles
- Definiert: Component Variants (Button, Card, Badge)
- Definiert: Responsive Breakpoints (Mobile, Tablet, Desktop, Wide)
- Definiert: Icon Mapping (40+ Icons)
- Definiert: Animation System
- Utility Functions: `apply_custom_css()`, `get_component_style()`, `get_status_color()`

---

**Phase 3 Status**: ABGESCHLOSSEN  
**Nächste Phase**: Intro Screen Modernization (Phase 4)
