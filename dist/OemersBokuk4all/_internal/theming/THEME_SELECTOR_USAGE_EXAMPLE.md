# Theme Selector UI - Verwendungsbeispiele

Praktische Beispiele für die Verwendung der Theme-Selector-UI.

## Beispiel 1: Minimale Integration

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def main():
    st.set_page_config(page_title="My App", layout="wide")

    # Theme Manager initialisieren
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager

    # CSS injizieren
    inject_theme_css(theme_manager)

    # Theme Selector in Sidebar
    with st.sidebar:
        render_theme_selector(theme_manager)

    # Deine App
    st.title("Welcome to My App")
    st.button("Click me")

if __name__ == "__main__":
    main()
```

## Beispiel 2: Mit Callback

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    # Callback für Theme-Wechsel
    def on_theme_change(theme_name: str):
        st.toast(f"✅ Theme gewechselt zu: {theme_name}", icon="🎨")
        # Weitere Aktionen...

    with st.sidebar:
        render_theme_selector(
            theme_manager,
            on_theme_change=on_theme_change
        )

    st.title("My App")

if __name__ == "__main__":
    main()
```

## Beispiel 3: Mit Analytics

```python
import streamlit as st
from datetime import datetime
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css,
    get_current_theme_name
)

def track_theme_change(theme_name: str):
    """Trackt Theme-Wechsel für Analytics"""
    if 'theme_changes' not in st.session_state:
        st.session_state.theme_changes = []

    st.session_state.theme_changes.append({
        'theme': theme_name,
        'timestamp': datetime.now()
    })

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    with st.sidebar:
        render_theme_selector(
            theme_manager,
            on_theme_change=track_theme_change
        )

        # Zeige Analytics
        if 'theme_changes' in st.session_state:
            changes = st.session_state.theme_changes
            st.metric("Theme-Wechsel", len(changes))

    st.title("My App")
    st.write(f"Aktuelles Theme: {get_current_theme_name()}")

if __name__ == "__main__":
    main()
```

## Beispiel 4: Ohne Dark Mode Toggle

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    with st.sidebar:
        # Ohne Dark Mode Toggle
        render_theme_selector(
            theme_manager,
            show_dark_mode_toggle=False
        )

    st.title("My App")

if __name__ == "__main__":
    main()
```

## Beispiel 5: Ohne Vorschau

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    with st.sidebar:
        # Ohne Farbvorschau
        render_theme_selector(
            theme_manager,
            show_preview=False
        )

    st.title("My App")

if __name__ == "__main__":
    main()
```

## Beispiel 6: Mit Theme-Info-Dashboard

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css,
    get_current_theme_name,
    is_dark_mode
)

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    with st.sidebar:
        render_theme_selector(theme_manager)

    # Theme-Info-Dashboard
    st.title("Theme Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Aktuelles Theme", get_current_theme_name())

    with col2:
        st.metric("Dark Mode", "Aktiv" if is_dark_mode() else "Inaktiv")

    with col3:
        themes = theme_manager.get_available_themes()
        st.metric("Verfügbare Themes", len(themes))

    # Theme-Details
    theme = theme_manager.current_theme
    if theme:
        st.subheader("Theme-Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Farben**")
            st.write(f"Primary: {theme.colors.primary}")
            st.write(f"Secondary: {theme.colors.secondary}")
            st.write(f"Success: {theme.colors.success}")

        with col2:
            st.write("**Typografie**")
            st.write(f"Font: {theme.typography.font_family}")
            st.write(f"Size: {theme.typography.font_size_base}")

if __name__ == "__main__":
    main()
```

## Beispiel 7: Mit User-Präferenzen-Speicherung

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css,
    get_current_theme_name
)

def save_user_preference(user_id: str, theme_name: str):
    """Speichert User-Präferenz in Datenbank"""
    # Beispiel: Speichere in SQLite
    import sqlite3
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO preferences (user_id, theme) VALUES (?, ?)",
        (user_id, theme_name)
    )
    conn.commit()
    conn.close()

def load_user_preference(user_id: str) -> str:
    """Lädt User-Präferenz aus Datenbank"""
    import sqlite3
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    result = cursor.execute(
        "SELECT theme FROM preferences WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return result[0] if result else 'shadcn-default'

def main():
    st.set_page_config(page_title="My App", layout="wide")

    # User ID (z.B. aus Authentication)
    user_id = "user123"

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

        # Lade User-Präferenz
        saved_theme = load_user_preference(user_id)
        st.session_state.current_theme = saved_theme
        st.session_state.theme_manager.set_theme(saved_theme)

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    def on_theme_change(theme_name: str):
        # Speichere in Datenbank
        save_user_preference(user_id, theme_name)
        st.toast(f"✅ Präferenz gespeichert: {theme_name}")

    with st.sidebar:
        render_theme_selector(
            theme_manager,
            on_theme_change=on_theme_change
        )

    st.title("My App")
    st.write(f"Willkommen, User {user_id}")
    st.write(f"Dein Theme: {get_current_theme_name()}")

if __name__ == "__main__":
    main()
```

## Beispiel 8: Multi-Page App

```python
# main.py
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def init_theme():
    """Initialisiert Theme (in jeder Page aufrufen)"""
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)

    return theme_manager

def render_sidebar(theme_manager):
    """Rendert Sidebar mit Theme Selector"""
    with st.sidebar:
        st.title("My Multi-Page App")

        # Navigation
        st.page_link("main.py", label="Home")
        st.page_link("pages/page1.py", label="Page 1")
        st.page_link("pages/page2.py", label="Page 2")

        st.markdown("---")

        # Theme Selector
        render_theme_selector(theme_manager)

def main():
    st.set_page_config(page_title="Home", layout="wide")

    theme_manager = init_theme()
    render_sidebar(theme_manager)

    st.title("Home Page")
    st.write("Welcome to the home page")

if __name__ == "__main__":
    main()
```

```python
# pages/page1.py
import streamlit as st
from main import init_theme, render_sidebar

def main():
    st.set_page_config(page_title="Page 1", layout="wide")

    theme_manager = init_theme()
    render_sidebar(theme_manager)

    st.title("Page 1")
    st.write("Content of page 1")

if __name__ == "__main__":
    main()
```

## Beispiel 9: Mit Custom Styling

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def inject_custom_css():
    """Injiziert zusätzliches Custom CSS"""
    custom_css = """
    <style>
    /* Custom Styles */
    .custom-card {
        background-color: var(--background);
        border: 1px solid var(--border);
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-4);
        box-shadow: var(--shadow-md);
    }

    .custom-button {
        background-color: var(--primary);
        color: var(--primary-foreground);
        padding: var(--spacing-2) var(--spacing-4);
        border-radius: var(--border-radius-md);
        border: none;
        cursor: pointer;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="My App", layout="wide")

    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager
    inject_theme_css(theme_manager)
    inject_custom_css()

    with st.sidebar:
        render_theme_selector(theme_manager)

    st.title("My App with Custom Styling")

    # Verwende Custom CSS
    st.markdown("""
    <div class="custom-card">
        <h3>Custom Card</h3>
        <p>This card uses custom CSS with theme variables</p>
        <button class="custom-button">Custom Button</button>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```

## Beispiel 10: Mit Feature-Flag

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

def main():
    st.set_page_config(page_title="My App", layout="wide")

    # Feature-Flag für Theme-System
    enable_themes = st.sidebar.checkbox(
        "Enable Theme System",
        value=True,
        key="enable_themes"
    )

    if enable_themes:
        # Theme-System aktiviert
        if 'theme_manager' not in st.session_state:
            st.session_state.theme_manager = ThemeManager()

        theme_manager = st.session_state.theme_manager
        inject_theme_css(theme_manager)

        with st.sidebar:
            render_theme_selector(theme_manager)

        st.success("✅ Theme-System aktiviert")
    else:
        # Standard Streamlit
        st.info("ℹ️ Theme-System deaktiviert")

    st.title("My App")
    st.button("Click me")

if __name__ == "__main__":
    main()
```

## Siehe auch

- [Theme Selector Referenz](THEME_SELECTOR_REFERENCE.md)
- [Theme Selector Quick Reference](THEME_SELECTOR_QUICK_REFERENCE.md)
- [Theme Manager Referenz](THEME_MANAGER_REFERENCE.md)
