"""
CSS Generator

Generiert CSS aus Theme-Tokens für shadcn/ui-Styling.
Erstellt CSS-Variablen, Component-Styles und Utility-Klassen.
"""

from typing import Optional
from theming.theme_tokens import Theme


class CSSGenerator:
    """Generiert CSS aus Theme-Tokens"""

    def __init__(self, theme: Theme):
        """
        Initialisiert CSSGenerator

        Args:
            theme: Theme-Objekt mit allen Design-Tokens
        """
        self.theme = theme

    def generate_css_variables(self) -> str:
        """
        Generiert CSS Custom Properties (Variablen) aus Theme-Tokens

        Returns:
            CSS-String mit :root Variablen
        """
        colors = self.theme.colors
        typography = self.theme.typography
        spacing = self.theme.spacing
        shadows = self.theme.shadows
        borders = self.theme.borders
        animations = self.theme.animations

        css = ":root {\n"

        # Color variables
        css += "  /* Colors */\n"
        css += f"  --background: {colors.background};\n"
        css += f"  --foreground: {colors.foreground};\n"
        css += f"  --primary: {colors.primary};\n"
        css += f"  --primary-foreground: {colors.primary_foreground};\n"
        css += f"  --secondary: {colors.secondary};\n"
        css += (
            f"  --secondary-foreground: {colors.secondary_foreground};\n"
        )
        css += f"  --accent: {colors.accent};\n"
        css += f"  --accent-foreground: {colors.accent_foreground};\n"
        css += f"  --success: {colors.success};\n"
        css += f"  --warning: {colors.warning};\n"
        css += f"  --error: {colors.error};\n"
        css += f"  --info: {colors.info};\n"
        css += f"  --muted: {colors.muted};\n"
        css += f"  --muted-foreground: {colors.muted_foreground};\n"
        css += f"  --border: {colors.border};\n"
        css += f"  --input: {colors.input};\n"
        css += f"  --ring: {colors.ring};\n"
        css += f"  --chart-1: {colors.chart_1};\n"
        css += f"  --chart-2: {colors.chart_2};\n"
        css += f"  --chart-3: {colors.chart_3};\n"
        css += f"  --chart-4: {colors.chart_4};\n"
        css += f"  --chart-5: {colors.chart_5};\n"

        # Typography variables
        css += "\n  /* Typography */\n"
        css += f"  --font-family: {typography.font_family};\n"
        css += f"  --font-family-mono: {typography.font_family_mono};\n"
        css += f"  --font-size-xs: {typography.font_size_xs};\n"
        css += f"  --font-size-sm: {typography.font_size_sm};\n"
        css += f"  --font-size-base: {typography.font_size_base};\n"
        css += f"  --font-size-lg: {typography.font_size_lg};\n"
        css += f"  --font-size-xl: {typography.font_size_xl};\n"
        css += f"  --font-size-2xl: {typography.font_size_2xl};\n"
        css += f"  --font-weight-normal: {typography.font_weight_normal};\n"
        css += f"  --font-weight-medium: {typography.font_weight_medium};\n"
        css += (
            f"  --font-weight-semibold: {typography.font_weight_semibold};\n"
        )
        css += f"  --font-weight-bold: {typography.font_weight_bold};\n"
        css += f"  --line-height-tight: {typography.line_height_tight};\n"
        css += f"  --line-height-normal: {typography.line_height_normal};\n"
        css += (
            f"  --line-height-relaxed: {typography.line_height_relaxed};\n"
        )

        # Spacing variables
        css += "\n  /* Spacing */\n"
        css += f"  --spacing-0: {spacing.spacing_0};\n"
        css += f"  --spacing-1: {spacing.spacing_1};\n"
        css += f"  --spacing-2: {spacing.spacing_2};\n"
        css += f"  --spacing-3: {spacing.spacing_3};\n"
        css += f"  --spacing-4: {spacing.spacing_4};\n"
        css += f"  --spacing-6: {spacing.spacing_6};\n"
        css += f"  --spacing-8: {spacing.spacing_8};\n"
        css += f"  --spacing-12: {spacing.spacing_12};\n"
        css += f"  --spacing-16: {spacing.spacing_16};\n"

        # Shadow variables
        css += "\n  /* Shadows */\n"
        css += f"  --shadow-sm: {shadows.shadow_sm};\n"
        css += f"  --shadow-md: {shadows.shadow_md};\n"
        css += f"  --shadow-lg: {shadows.shadow_lg};\n"
        css += f"  --shadow-xl: {shadows.shadow_xl};\n"

        # Border variables
        css += "\n  /* Borders */\n"
        css += f"  --border-width: {borders.border_width};\n"
        css += f"  --border-radius-sm: {borders.border_radius_sm};\n"
        css += f"  --border-radius-md: {borders.border_radius_md};\n"
        css += f"  --border-radius-lg: {borders.border_radius_lg};\n"
        css += f"  --border-radius-full: {borders.border_radius_full};\n"

        # Animation variables
        css += "\n  /* Animations */\n"
        css += f"  --transition-fast: {animations.transition_fast};\n"
        css += f"  --transition-base: {animations.transition_base};\n"
        css += f"  --transition-slow: {animations.transition_slow};\n"
        css += f"  --easing-default: {animations.easing_default};\n"

        css += "}\n"

        return css

    def generate_component_styles(self) -> str:
        """
        Generiert Styles für Streamlit-Komponenten

        Returns:
            CSS-String mit Component-Styles
        """
        css = ""

        # Button styles
        css += self._generate_button_styles()

        # Input styles
        css += self._generate_input_styles()

        # Select styles
        css += self._generate_select_styles()

        # Slider styles
        css += self._generate_slider_styles()

        # Checkbox and Radio styles
        css += self._generate_checkbox_radio_styles()

        # Tab styles
        css += self._generate_tab_styles()

        # Container styles
        css += self._generate_container_styles()

        return css

    def _generate_button_styles(self) -> str:
        """Generiert Button-Styles"""
        return """
/* Button Styles */
.stButton > button {
    background-color: var(--primary);
    color: var(--primary-foreground);
    border: var(--border-width) solid var(--primary);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-2) var(--spacing-4);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    line-height: var(--line-height-normal);
    transition: all var(--transition-base);
    cursor: pointer;
}

.stButton > button:hover {
    opacity: 0.9;
    box-shadow: var(--shadow-sm);
}

.stButton > button:active {
    transform: scale(0.98);
}

.stButton > button:focus {
    outline: 2px solid var(--ring);
    outline-offset: 2px;
}

/* Secondary Button */
.stButton > button[kind="secondary"] {
    background-color: var(--secondary);
    color: var(--secondary-foreground);
    border-color: var(--secondary);
}

/* Tertiary Button */
.stButton > button[kind="tertiary"] {
    background-color: transparent;
    color: var(--foreground);
    border-color: var(--border);
}

.stButton > button[kind="tertiary"]:hover {
    background-color: var(--accent);
    color: var(--accent-foreground);
}

"""

    def _generate_input_styles(self) -> str:
        """Generiert Input-Styles"""
        return """
/* Input Styles */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--background);
    color: var(--foreground);
    border: var(--border-width) solid var(--input);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-2) var(--spacing-3);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    line-height: var(--line-height-normal);
    transition: all var(--transition-base);
}

.stTextInput > div > div > input:hover,
.stNumberInput > div > div > input:hover,
.stTextArea > div > div > textarea:hover {
    border-color: var(--ring);
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    outline: none;
    border-color: var(--ring);
    box-shadow: 0 0 0 2px var(--ring);
}

/* Input Labels */
.stTextInput > label,
.stNumberInput > label,
.stTextArea > label {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--foreground);
    margin-bottom: var(--spacing-2);
}

"""

    def _generate_select_styles(self) -> str:
        """Generiert Select/Dropdown-Styles"""
        return """
/* Select Styles */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: var(--background);
    border: var(--border-width) solid var(--input);
    border-radius: var(--border-radius-md);
    transition: all var(--transition-base);
}

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: var(--ring);
}

.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    color: var(--foreground);
}

/* Dropdown Menu */
.stSelectbox [data-baseweb="popover"],
.stMultiSelect [data-baseweb="popover"] {
    background-color: var(--background);
    border: var(--border-width) solid var(--border);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-lg);
}

.stSelectbox [data-baseweb="menu"] > ul > li,
.stMultiSelect [data-baseweb="menu"] > ul > li {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    color: var(--foreground);
    padding: var(--spacing-2) var(--spacing-3);
    transition: all var(--transition-fast);
}

.stSelectbox [data-baseweb="menu"] > ul > li:hover,
.stMultiSelect [data-baseweb="menu"] > ul > li:hover {
    background-color: var(--accent);
    color: var(--accent-foreground);
}

"""

    def _generate_slider_styles(self) -> str:
        """Generiert Slider-Styles"""
        return """
/* Slider Styles */
.stSlider > div > div > div > div {
    background-color: var(--muted);
}

.stSlider > div > div > div > div > div {
    background-color: var(--primary);
}

.stSlider > div > div > div > div > div > div {
    background-color: var(--primary);
    border: 2px solid var(--background);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-base);
}

.stSlider > div > div > div > div > div > div:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-md);
}

"""

    def _generate_checkbox_radio_styles(self) -> str:
        """Generiert Checkbox und Radio-Styles"""
        return """
/* Checkbox Styles */
.stCheckbox > label {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    color: var(--foreground);
}

.stCheckbox > label > div {
    background-color: var(--background);
    border: var(--border-width) solid var(--input);
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-base);
}

.stCheckbox > label > div[data-checked="true"] {
    background-color: var(--primary);
    border-color: var(--primary);
}

/* Radio Styles */
.stRadio > label {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    color: var(--foreground);
}

.stRadio > div {
    gap: var(--spacing-2);
}

.stRadio > div > label {
    background-color: var(--background);
    border: var(--border-width) solid var(--input);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-2) var(--spacing-3);
    transition: all var(--transition-base);
}

.stRadio > div > label:hover {
    border-color: var(--ring);
    background-color: var(--accent);
}

.stRadio > div > label[data-checked="true"] {
    background-color: var(--primary);
    color: var(--primary-foreground);
    border-color: var(--primary);
}

"""

    def _generate_tab_styles(self) -> str:
        """Generiert Tab-Styles"""
        return """
/* Tab Styles */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--spacing-2);
    background-color: var(--muted);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-1);
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--muted-foreground);
    background-color: transparent;
    border-radius: var(--border-radius-md);
    padding: var(--spacing-2) var(--spacing-4);
    transition: all var(--transition-base);
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--foreground);
    background-color: var(--background);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: var(--background);
    color: var(--foreground);
    box-shadow: var(--shadow-sm);
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: var(--spacing-4);
}

"""

    def _generate_container_styles(self) -> str:
        """Generiert Container-Styles"""
        return """
/* Container Styles */
.element-container {
    font-family: var(--font-family);
    color: var(--foreground);
}

/* Expander Styles */
.streamlit-expanderHeader {
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--foreground);
    background-color: var(--muted);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-3) var(--spacing-4);
    transition: all var(--transition-base);
}

.streamlit-expanderHeader:hover {
    background-color: var(--accent);
}

.streamlit-expanderContent {
    border: var(--border-width) solid var(--border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-4);
    margin-top: var(--spacing-2);
}

"""

    def generate_utility_classes(self) -> str:
        """
        Generiert Utility-Klassen (ähnlich Tailwind)

        Returns:
            CSS-String mit Utility-Klassen
        """
        css = """
/* Utility Classes */

/* Spacing Utilities */
.p-0 { padding: var(--spacing-0); }
.p-1 { padding: var(--spacing-1); }
.p-2 { padding: var(--spacing-2); }
.p-3 { padding: var(--spacing-3); }
.p-4 { padding: var(--spacing-4); }
.p-6 { padding: var(--spacing-6); }
.p-8 { padding: var(--spacing-8); }

.px-0 { padding-left: var(--spacing-0); padding-right: var(--spacing-0); }
.px-1 { padding-left: var(--spacing-1); padding-right: var(--spacing-1); }
.px-2 { padding-left: var(--spacing-2); padding-right: var(--spacing-2); }
.px-3 { padding-left: var(--spacing-3); padding-right: var(--spacing-3); }
.px-4 { padding-left: var(--spacing-4); padding-right: var(--spacing-4); }
.px-6 { padding-left: var(--spacing-6); padding-right: var(--spacing-6); }
.px-8 { padding-left: var(--spacing-8); padding-right: var(--spacing-8); }

.py-0 { padding-top: var(--spacing-0); padding-bottom: var(--spacing-0); }
.py-1 { padding-top: var(--spacing-1); padding-bottom: var(--spacing-1); }
.py-2 { padding-top: var(--spacing-2); padding-bottom: var(--spacing-2); }
.py-3 { padding-top: var(--spacing-3); padding-bottom: var(--spacing-3); }
.py-4 { padding-top: var(--spacing-4); padding-bottom: var(--spacing-4); }
.py-6 { padding-top: var(--spacing-6); padding-bottom: var(--spacing-6); }
.py-8 { padding-top: var(--spacing-8); padding-bottom: var(--spacing-8); }

.m-0 { margin: var(--spacing-0); }
.m-1 { margin: var(--spacing-1); }
.m-2 { margin: var(--spacing-2); }
.m-3 { margin: var(--spacing-3); }
.m-4 { margin: var(--spacing-4); }
.m-6 { margin: var(--spacing-6); }
.m-8 { margin: var(--spacing-8); }

/* Text Utilities */
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }
.text-xl { font-size: var(--font-size-xl); }
.text-2xl { font-size: var(--font-size-2xl); }

.font-normal { font-weight: var(--font-weight-normal); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold { font-weight: var(--font-weight-bold); }

/* Color Utilities */
.text-foreground { color: var(--foreground); }
.text-muted { color: var(--muted-foreground); }
.text-primary { color: var(--primary); }
.text-success { color: var(--success); }
.text-warning { color: var(--warning); }
.text-error { color: var(--error); }
.text-info { color: var(--info); }

.bg-background { background-color: var(--background); }
.bg-muted { background-color: var(--muted); }
.bg-primary { background-color: var(--primary); }
.bg-secondary { background-color: var(--secondary); }
.bg-accent { background-color: var(--accent); }

/* Border Utilities */
.border { border: var(--border-width) solid var(--border); }
.border-t { border-top: var(--border-width) solid var(--border); }
.border-b { border-bottom: var(--border-width) solid var(--border); }
.border-l { border-left: var(--border-width) solid var(--border); }
.border-r { border-right: var(--border-width) solid var(--border); }

.rounded-sm { border-radius: var(--border-radius-sm); }
.rounded-md { border-radius: var(--border-radius-md); }
.rounded-lg { border-radius: var(--border-radius-lg); }
.rounded-full { border-radius: var(--border-radius-full); }

/* Shadow Utilities */
.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }
.shadow-xl { box-shadow: var(--shadow-xl); }

/* Transition Utilities */
.transition-fast { transition: all var(--transition-fast); }
.transition-base { transition: all var(--transition-base); }
.transition-slow { transition: all var(--transition-slow); }

"""
        return css

    def generate_full_css(self) -> str:
        """
        Generiert vollständiges CSS (Variablen + Components + Utilities)

        Returns:
            Vollständiger CSS-String
        """
        css = "/* shadcn/ui Theme CSS - Auto-generated */\n\n"
        css += self.generate_css_variables()
        css += "\n"
        css += self.generate_component_styles()
        css += "\n"
        css += self.generate_utility_classes()

        return css
