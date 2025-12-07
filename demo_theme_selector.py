"""
Demo: Theme Selector UI

Demonstriert die Verwendung des Theme-Selectors mit Live-Vorschau,
Theme-Wechsel und Local Storage Persistierung.
"""

import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css,
    get_current_theme_name,
    is_dark_mode
)


def main():
    """Haupt-Demo-Funktion"""
    st.set_page_config(
        page_title="Theme Selector Demo",
        page_icon="",
        layout="wide"
    )

    # Initialisiere Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager

    # Injiziere Theme CSS
    inject_theme_css(theme_manager)

    # Sidebar mit Theme Selector
    with st.sidebar:
        st.title(" Theme Demo")

        # Callback für Theme-Wechsel
        def on_theme_change(theme_name: str):
            st.toast(f" Theme gewechselt zu: {theme_name}", icon="")

        # Rendere Theme Selector
        render_theme_selector(
            theme_manager=theme_manager,
            on_theme_change=on_theme_change,
            show_preview=True,
            show_dark_mode_toggle=True
        )

    # Hauptinhalt
    st.title(" Theme Selector Demo")

    # Zeige aktuelles Theme
    current_theme = get_current_theme_name()
    dark_mode = is_dark_mode()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Aktuelles Theme", current_theme)
    with col2:
        st.metric("Dark Mode", "Aktiv" if dark_mode else "Inaktiv")

    st.markdown("---")

    # Demo-Komponenten
    st.header("Demo-Komponenten")

    st.subheader("Buttons")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Primary Button", type="primary")
    with col2:
        st.button("Secondary Button", type="secondary")
    with col3:
        st.button("Tertiary Button")

    st.subheader("Inputs")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Text Input", placeholder="Enter text...")
        st.number_input("Number Input", value=42)
    with col2:
        st.text_area("Text Area", placeholder="Enter longer text...")
        st.date_input("Date Input")

    st.subheader("Selects")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Selectbox",
            options=["Option 1", "Option 2", "Option 3"]
        )
    with col2:
        st.multiselect(
            "Multiselect",
            options=["Option A", "Option B", "Option C"]
        )

    st.subheader("Sliders & Toggles")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("Slider", 0, 100, 50)
        st.select_slider(
            "Select Slider",
            options=["Low", "Medium", "High"]
        )
    with col2:
        st.checkbox("Checkbox")
        st.toggle("Toggle")
        st.radio("Radio", options=["Option 1", "Option 2"])

    st.subheader("Tabs")
    tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    with tab1:
        st.write("Content of Tab 1")
    with tab2:
        st.write("Content of Tab 2")
    with tab3:
        st.write("Content of Tab 3")

    st.subheader("Containers")
    with st.container():
        st.write("This is a container")
        st.info("This is an info message")

    with st.expander("Expandable Section"):
        st.write("This content is inside an expander")
        st.success("This is a success message")

    st.subheader("Messages")
    col1, col2 = st.columns(2)
    with col1:
        st.success("Success message")
        st.info("Info message")
    with col2:
        st.warning("Warning message")
        st.error("Error message")

    st.markdown("---")

    # Theme-Informationen
    st.header("Theme-Informationen")

    theme = theme_manager.current_theme
    if theme:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Farben")
            st.write(f"**Primary:** {theme.colors.primary}")
            st.write(f"**Secondary:** {theme.colors.secondary}")
            st.write(f"**Accent:** {theme.colors.accent}")
            st.write(f"**Success:** {theme.colors.success}")
            st.write(f"**Warning:** {theme.colors.warning}")
            st.write(f"**Error:** {theme.colors.error}")

        with col2:
            st.subheader("Typografie")
            st.write(f"**Font Family:** {theme.typography.font_family}")
            st.write(f"**Base Size:** {theme.typography.font_size_base}")
            st.write(
                f"**Normal Weight:** {theme.typography.font_weight_normal}"
            )
            st.write(
                f"**Bold Weight:** {theme.typography.font_weight_bold}"
            )

        with col3:
            st.subheader("Abstände & Schatten")
            st.write(f"**Spacing 4:** {theme.spacing.spacing_4}")
            st.write(f"**Spacing 8:** {theme.spacing.spacing_8}")
            st.write(f"**Shadow SM:** {theme.shadows.shadow_sm}")
            st.write(f"**Shadow MD:** {theme.shadows.shadow_md}")

    st.markdown("---")

    # Anleitung
    st.header(" Anleitung")

    st.markdown("""
    ### Theme-Wechsel

    1. **Theme auswählen**: Wähle ein Theme aus dem Dropdown in der Sidebar
    2. **Dark Mode**: Aktiviere den Dark Mode Toggle für dunkle Themes
    3. **Live-Vorschau**: Sieh die Farben des Themes in der Vorschau
    4. **Persistierung**: Deine Theme-Auswahl wird im Browser gespeichert

    ### Features

    -  **Live Theme-Wechsel** ohne Seiten-Reload
    -  **Dark Mode Toggle** für schnellen Wechsel
    -  **Farbvorschau** mit allen wichtigen Theme-Farben
    -  **Local Storage** Persistierung der Theme-Auswahl
    -  **Session State** Integration
    -  **Callback-Support** für Theme-Wechsel-Events

    ### Verfügbare Themes

    - **shadcn/ui Default** - Helles Standard-Theme
    - **shadcn/ui Dark** - Dunkles Theme
    - **shadcn/ui Ocean** - Blaues Theme
    - **shadcn/ui Forest** - Grünes Theme
    - **shadcn/ui Sunset** - Orange/Rotes Theme

    ### Integration in eigene App

    ```python
    from theming.theme_manager import ThemeManager
    from theming.theme_selector_ui import (
        render_theme_selector,
        inject_theme_css
    )

    # Initialisiere Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager

    # Injiziere CSS
    inject_theme_css(theme_manager)

    # Rendere Theme Selector in Sidebar
    with st.sidebar:
        render_theme_selector(theme_manager)
    ```
    """)


if __name__ == "__main__":
    main()
