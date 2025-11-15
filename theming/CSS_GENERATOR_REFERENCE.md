# CSS Generator Reference

## Übersicht

Der CSS Generator ist verantwortlich für die Generierung von CSS aus Theme-Tokens. Er erstellt CSS-Variablen, Component-Styles und Utility-Klassen im shadcn/ui-Stil.

## Klasse: CSSGenerator

### Initialisierung

```python
from theming.theme_manager import ThemeManager
from theming.css_generator import CSSGenerator

# Theme Manager initialisieren
theme_manager = ThemeManager()
theme_manager.set_theme("shadcn-default")

# CSS Generator erstellen
css_generator = CSSGenerator(theme_manager.current_theme)
```

### Methoden

#### `generate_css_variables() -> str`

Generiert CSS Custom Properties (Variablen) aus Theme-Tokens.

**Returns:** CSS-String mit `:root` Variablen

**Beispiel:**
```python
css_vars = css_generator.generate_css_variables()
print(css_vars)
```

**Output:**
```css
:root {
  /* Colors */
  --background: #ffffff;
  --foreground: #0a0a0a;
  --primary: #18181b;
  /* ... weitere Variablen */
}
```

**Generierte Variablen:**
- **Colors:** `--background`, `--foreground`, `--primary`, `--secondary`, `--accent`, `--success`, `--warning`, `--error`, `--info`, `--muted`, `--border`, `--input`, `--ring`, `--chart-1` bis `--chart-5`
- **Typography:** `--font-family`, `--font-size-*`, `--font-weight-*`, `--line-height-*`
- **Spacing:** `--spacing-0` bis `--spacing-16`
- **Shadows:** `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`
- **Borders:** `--border-width`, `--border-radius-*`
- **Animations:** `--transition-*`, `--easing-default`

---

#### `generate_component_styles() -> str`

Generiert Styles für Streamlit-Komponenten.

**Returns:** CSS-String mit Component-Styles

**Beispiel:**
```python
component_styles = css_generator.generate_component_styles()
```

**Gestylte Komponenten:**

1. **Buttons** (`.stButton > button`)
   - Primary, Secondary, Tertiary Varianten
   - Hover, Focus, Active States
   - Transitions und Shadows

2. **Inputs** (`.stTextInput`, `.stNumberInput`, `.stTextArea`)
   - Border und Focus-Styles
   - Hover-Effekte
   - Label-Styling

3. **Selects** (`.stSelectbox`, `.stMultiSelect`)
   - Dropdown-Styling
   - Menu-Item-Hover
   - Border und Transitions

4. **Sliders** (`.stSlider`)
   - Track und Thumb-Styling
   - Hover-Effekte

5. **Checkboxes & Radios** (`.stCheckbox`, `.stRadio`)
   - Custom-Styling
   - Checked-States

6. **Tabs** (`.stTabs`)
   - Tab-List und Tab-Styling
   - Active-State
   - Transitions

7. **Containers** (`.element-container`, `.streamlit-expanderHeader`)
   - Expander-Styling
   - Content-Padding

---

#### `generate_utility_classes() -> str`

Generiert Utility-Klassen (ähnlich Tailwind CSS).

**Returns:** CSS-String mit Utility-Klassen

**Beispiel:**
```python
utilities = css_generator.generate_utility_classes()
```

**Verfügbare Utilities:**

**Spacing:**
```css
.p-0, .p-1, .p-2, .p-3, .p-4, .p-6, .p-8  /* Padding */
.px-0, .px-1, .px-2, ...                   /* Padding X */
.py-0, .py-1, .py-2, ...                   /* Padding Y */
.m-0, .m-1, .m-2, ...                      /* Margin */
```

**Typography:**
```css
.text-xs, .text-sm, .text-base, .text-lg, .text-xl, .text-2xl
.font-normal, .font-medium, .font-semibold, .font-bold
```

**Colors:**
```css
.text-foreground, .text-muted, .text-primary, .text-success, ...
.bg-background, .bg-muted, .bg-primary, .bg-secondary, ...
```

**Borders:**
```css
.border, .border-t, .border-b, .border-l, .border-r
.rounded-sm, .rounded-md, .rounded-lg, .rounded-full
```

**Shadows:**
```css
.shadow-sm, .shadow-md, .shadow-lg, .shadow-xl
```

**Transitions:**
```css
.transition-fast, .transition-base, .transition-slow
```

---

#### `generate_full_css() -> str`

Generiert vollständiges CSS (Variablen + Components + Utilities).

**Returns:** Vollständiger CSS-String

**Beispiel:**
```python
full_css = css_generator.generate_full_css()

# In Streamlit injizieren
import streamlit as st
st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)
```

---

## Integration mit ThemeManager

Der ThemeManager bietet eine Convenience-Methode:

```python
theme_manager = ThemeManager()
theme_manager.set_theme("shadcn-dark")

# CSS direkt vom ThemeManager generieren
css = theme_manager.generate_css()
```

---

## Verwendung in Streamlit

### Basis-Integration

```python
import streamlit as st
from theming.theme_manager import ThemeManager

# Theme System initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

# CSS injizieren (nur einmal)
if 'css_injected' not in st.session_state:
    css = st.session_state.theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.session_state.css_injected = True

# Normale Streamlit-Komponenten verwenden
st.button("Primary Button")
st.text_input("Name")
st.selectbox("Option", ["A", "B", "C"])
```

### Theme-Wechsel

```python
# Theme wechseln
new_theme = st.sidebar.selectbox(
    "Theme",
    st.session_state.theme_manager.get_available_themes()
)

if new_theme != st.session_state.theme_manager.current_theme.name:
    st.session_state.theme_manager.set_theme(new_theme)
    css = st.session_state.theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.rerun()
```

### Utility-Klassen verwenden

```python
# HTML mit Utility-Klassen
st.markdown("""
    <div class="p-4 bg-muted rounded-lg shadow-md">
        <h3 class="text-lg font-bold text-foreground">Card Title</h3>
        <p class="text-sm text-muted">Card content goes here</p>
    </div>
""", unsafe_allow_html=True)
```

---

## Performance

### CSS-Größe

- **CSS-Variablen:** ~2 KB
- **Component-Styles:** ~7 KB
- **Utility-Klassen:** ~4 KB
- **Gesamt:** ~13 KB (unkomprimiert)

### Optimierung

```python
# CSS nur einmal generieren und cachen
@st.cache_data
def get_theme_css(theme_name: str) -> str:
    theme_manager = ThemeManager()
    theme_manager.set_theme(theme_name)
    return theme_manager.generate_css()

css = get_theme_css("shadcn-default")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

---

## Requirements Coverage

Der CSS Generator erfüllt folgende Requirements:

- **Requirement 1.5:** CSS-Generierung aus Theme-Tokens ✓
- **Requirement 3.1:** Button-Styling ✓
- **Requirement 3.2:** Input-Styling (Text, Number, TextArea) ✓
- **Requirement 3.3:** Select-Styling (Selectbox, MultiSelect) ✓
- **Requirement 3.4:** Slider-Styling ✓
- **Requirement 3.5:** Checkbox/Radio-Styling ✓
- **Requirement 3.6:** Tab-Styling ✓
- **Requirement 3.7:** Hover/Focus/Active-States ✓

---

## Beispiele

### Beispiel 1: Basis-Setup

```python
import streamlit as st
from theming.theme_manager import ThemeManager

def main():
    # Theme System initialisieren
    theme_manager = ThemeManager()
    theme_manager.set_theme("shadcn-default")
    
    # CSS injizieren
    css = theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # App-Inhalt
    st.title("Meine App")
    st.button("Click me")
    st.text_input("Name")

if __name__ == "__main__":
    main()
```

### Beispiel 2: Multi-Theme-Support

```python
import streamlit as st
from theming.theme_manager import ThemeManager

def main():
    # Theme Manager in Session State
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme("shadcn-default")
    
    # Theme Selector
    with st.sidebar:
        themes = st.session_state.theme_manager.get_theme_display_names()
        selected = st.selectbox("Theme", list(themes.keys()), 
                                format_func=lambda x: themes[x])
        
        if selected != st.session_state.theme_manager.current_theme.name:
            st.session_state.theme_manager.set_theme(selected)
            st.rerun()
    
    # CSS injizieren
    css = st.session_state.theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # App-Inhalt
    st.title("Multi-Theme App")
    st.write(f"Aktuelles Theme: {st.session_state.theme_manager.current_theme.display_name}")

if __name__ == "__main__":
    main()
```

### Beispiel 3: Custom-Komponente mit Utilities

```python
import streamlit as st
from theming.theme_manager import ThemeManager

def custom_card(title: str, content: str):
    """Custom Card mit Utility-Klassen"""
    st.markdown(f"""
        <div class="p-6 bg-background border rounded-lg shadow-md transition-base">
            <h3 class="text-xl font-bold text-foreground mb-2">{title}</h3>
            <p class="text-sm text-muted">{content}</p>
        </div>
    """, unsafe_allow_html=True)

def main():
    theme_manager = ThemeManager()
    theme_manager.set_theme("shadcn-default")
    css = theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    custom_card("Welcome", "This is a custom card component")

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

### Problem: CSS wird nicht angewendet

**Lösung:** Stelle sicher, dass `unsafe_allow_html=True` gesetzt ist:
```python
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Problem: Styles überschreiben sich

**Lösung:** CSS nur einmal injizieren:
```python
if 'css_injected' not in st.session_state:
    css = theme_manager.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.session_state.css_injected = True
```

### Problem: Theme-Wechsel funktioniert nicht

**Lösung:** Nach Theme-Wechsel CSS neu injizieren und rerun:
```python
theme_manager.set_theme(new_theme)
css = theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
st.rerun()
```

---

## Nächste Schritte

Nach der CSS Generator Implementierung:

1. **Task 3:** Theme Selector UI erstellen
2. **Task 4:** Basis-Komponenten-Klasse und Card implementieren
3. **Task 10:** Chart-Styling-System
4. **Task 11:** Sidebar-Styling modernisieren

---

## Siehe auch

- [Theme Manager Reference](./THEME_MANAGER_REFERENCE.md)
- [Theme Tokens Reference](./THEME_TOKENS_REFERENCE.md)
- [Usage Example](./USAGE_EXAMPLE.md)
