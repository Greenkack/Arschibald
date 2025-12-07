"""
Theme Selector UI

Provides UI components for theme selection in Streamlit sidebar.
Includes live preview, theme switching, and persistence.
"""

import streamlit as st
from typing import Optional, Callable
from theming.theme_manager import ThemeManager


class ThemeSelectorUI:
    """UI-Komponente für Theme-Auswahl"""

    def __init__(self, theme_manager: ThemeManager):
        """
        Initialisiert ThemeSelectorUI

        Args:
            theme_manager: ThemeManager-Instanz
        """
        self.theme_manager = theme_manager

    def render(
        self,
        on_theme_change: Optional[Callable[[str], None]] = None,
        show_preview: bool = True,
        show_dark_mode_toggle: bool = True
    ) -> None:
        """
        Rendert Theme-Selector in Sidebar

        Args:
            on_theme_change: Callback-Funktion bei Theme-Wechsel
            show_preview: Zeige Live-Vorschau der Theme-Farben
            show_dark_mode_toggle: Zeige Dark Mode Toggle
        """
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎨 Theme")

        # Initialisiere Session State
        self._init_session_state()

        # Dark Mode Toggle
        if show_dark_mode_toggle:
            self._render_dark_mode_toggle()

        # Theme Selector
        self._render_theme_selector(on_theme_change)

        # Live Preview
        if show_preview:
            self._render_theme_preview()

        # Theme Info
        self._render_theme_info()

    def _init_session_state(self) -> None:
        """Initialisiert Session State für Theme-Verwaltung"""
        # Lade Theme aus Local Storage (wenn verfügbar)
        if 'shadcn_theme_loaded' not in st.session_state:
            self._load_theme_from_local_storage()
            st.session_state.shadcn_theme_loaded = True

        # Setze Default-Theme wenn noch nicht gesetzt
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = 'shadcn-default'
            self.theme_manager.set_theme('shadcn-default')

        # Dark Mode State
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False

    def _load_theme_from_local_storage(self) -> None:
        """Lädt Theme-Präferenz aus Browser Local Storage"""
        # JavaScript zum Laden aus Local Storage
        js_code = """
        <script>
        // Lade Theme aus Local Storage
        const savedTheme = localStorage.getItem('shadcn_theme');
        const savedDarkMode = localStorage.getItem('shadcn_dark_mode');

        // Sende an Streamlit via Query Params (Workaround)
        if (savedTheme) {
            const url = new URL(window.location);
            url.searchParams.set('theme', savedTheme);
            if (savedDarkMode) {
                url.searchParams.set('dark_mode', savedDarkMode);
            }
            // Nur beim ersten Laden
            if (!url.searchParams.has('theme_loaded')) {
                url.searchParams.set('theme_loaded', 'true');
                window.history.replaceState({}, '', url);
            }
        }
        </script>
        """
        st.components.v1.html(js_code, height=0)

        # Lese aus Query Params
        query_params = st.query_params
        if 'theme' in query_params:
            theme_name = query_params['theme']
            if theme_name in self.theme_manager.get_available_themes():
                st.session_state.current_theme = theme_name
                self.theme_manager.set_theme(theme_name)

        if 'dark_mode' in query_params:
            st.session_state.dark_mode = (
                query_params['dark_mode'].lower() == 'true'
            )

    def _save_theme_to_local_storage(
        self,
        theme_name: str,
        dark_mode: bool
    ) -> None:
        """
        Speichert Theme-Präferenz in Browser Local Storage

        Args:
            theme_name: Name des Themes
            dark_mode: Dark Mode aktiviert
        """
        js_code = f"""
        <script>
        localStorage.setItem('shadcn_theme', '{theme_name}');
        localStorage.setItem('shadcn_dark_mode', '{str(dark_mode).lower()}');
        console.log('Theme saved to localStorage:', '{theme_name}');
        </script>
        """
        st.components.v1.html(js_code, height=0)

    def _render_dark_mode_toggle(self) -> None:
        """Rendert Dark Mode Toggle"""
        dark_mode = st.sidebar.toggle(
            "🌙 Dark Mode",
            value=st.session_state.dark_mode,
            key="dark_mode_toggle"
        )

        # Wenn Dark Mode geändert wurde
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode

            # Wechsle zwischen Light und Dark Theme
            current_theme = st.session_state.current_theme
            if dark_mode:
                # Wechsle zu Dark-Variante
                if not current_theme.endswith('-dark'):
                    new_theme = 'shadcn-dark'
                    st.session_state.current_theme = new_theme
                    self.theme_manager.set_theme(new_theme)
            else:
                # Wechsle zu Light-Variante
                if current_theme.endswith('-dark'):
                    new_theme = 'shadcn-default'
                    st.session_state.current_theme = new_theme
                    self.theme_manager.set_theme(new_theme)

            # Speichere in Local Storage
            self._save_theme_to_local_storage(
                st.session_state.current_theme,
                dark_mode
            )

            # Rerun um CSS zu aktualisieren
            st.rerun()

    def _render_theme_selector(
        self,
        on_theme_change: Optional[Callable[[str], None]]
    ) -> None:
        """
        Rendert Theme-Auswahl Dropdown

        Args:
            on_theme_change: Callback bei Theme-Wechsel
        """
        # Hole verfügbare Themes
        theme_names = self.theme_manager.get_available_themes()
        theme_display_names = self.theme_manager.get_theme_display_names()

        # Erstelle Options-Liste mit Display-Namen
        options = [theme_display_names[name] for name in theme_names]

        # Finde aktuellen Index
        current_theme = st.session_state.current_theme
        current_index = (
            theme_names.index(current_theme)
            if current_theme in theme_names
            else 0
        )

        # Theme Selector
        selected_display_name = st.sidebar.selectbox(
            "Theme auswählen",
            options=options,
            index=current_index,
            key="theme_selector"
        )

        # Finde Theme-Namen aus Display-Namen
        selected_theme = None
        for name, display_name in theme_display_names.items():
            if display_name == selected_display_name:
                selected_theme = name
                break

        # Wenn Theme geändert wurde
        if selected_theme and selected_theme != current_theme:
            # Aktualisiere Session State
            st.session_state.current_theme = selected_theme

            # Setze Theme im Manager
            self.theme_manager.set_theme(selected_theme)

            # Update Dark Mode State basierend auf Theme
            st.session_state.dark_mode = selected_theme.endswith('-dark')

            # Speichere in Local Storage
            self._save_theme_to_local_storage(
                selected_theme,
                st.session_state.dark_mode
            )

            # Callback aufrufen
            if on_theme_change:
                on_theme_change(selected_theme)

            # Rerun um CSS zu aktualisieren
            st.rerun()

    def _render_theme_preview(self) -> None:
        """Rendert Live-Vorschau der Theme-Farben"""
        st.sidebar.markdown("**Farbvorschau**")

        # Hole aktuelles Theme
        theme = self.theme_manager.current_theme
        if not theme:
            return

        colors = theme.colors

        # Erstelle Farb-Swatches
        preview_html = f"""
        <style>
        .color-preview {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-top: 8px;
            margin-bottom: 16px;
        }}
        .color-swatch {{
            height: 40px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            font-weight: 500;
        }}
        </style>
        <div class="color-preview">
            <div class="color-swatch"
                 style="background-color: {colors.primary};">
                Primary
            </div>
            <div class="color-swatch"
                 style="background-color: {colors.secondary};
                        color: {colors.secondary_foreground};">
                Secondary
            </div>
            <div class="color-swatch"
                 style="background-color: {colors.accent};
                        color: {colors.accent_foreground};">
                Accent
            </div>
            <div class="color-swatch"
                 style="background-color: {colors.success};">
                Success
            </div>
            <div class="color-swatch"
                 style="background-color: {colors.warning};">
                Warning
            </div>
            <div class="color-swatch"
                 style="background-color: {colors.error};">
                Error
            </div>
        </div>
        """

        st.sidebar.markdown(preview_html, unsafe_allow_html=True)

    def _render_theme_info(self) -> None:
        """Rendert Theme-Informationen"""
        theme = self.theme_manager.current_theme
        if not theme:
            return

        with st.sidebar.expander("ℹ️ Theme Info"):
            st.markdown(f"**Name:** {theme.display_name}")
            st.markdown(f"**ID:** `{theme.name}`")
            st.markdown(
                f"**Font:** {theme.typography.font_family.split(',')[0]}"
            )

            # Zeige Anzahl verfügbarer Themes
            theme_count = len(self.theme_manager.get_available_themes())
            st.markdown(f"**Verfügbare Themes:** {theme_count}")


def render_theme_selector(
    theme_manager: ThemeManager,
    on_theme_change: Optional[Callable[[str], None]] = None,
    show_preview: bool = True,
    show_dark_mode_toggle: bool = True
) -> None:
    """
    Convenience-Funktion zum Rendern des Theme-Selectors

    Args:
        theme_manager: ThemeManager-Instanz
        on_theme_change: Callback bei Theme-Wechsel
        show_preview: Zeige Live-Vorschau
        show_dark_mode_toggle: Zeige Dark Mode Toggle
    """
    selector = ThemeSelectorUI(theme_manager)
    selector.render(
        on_theme_change=on_theme_change,
        show_preview=show_preview,
        show_dark_mode_toggle=show_dark_mode_toggle
    )


def inject_theme_css(theme_manager: ThemeManager) -> None:
    """
    Injiziert Theme-CSS in die App

    Args:
        theme_manager: ThemeManager-Instanz
    """
    # Nur einmal injizieren oder bei Theme-Wechsel
    current_theme = st.session_state.get('current_theme', 'shadcn-default')

    # Prüfe ob CSS neu generiert werden muss
    if (
        'injected_theme' not in st.session_state
        or st.session_state.injected_theme != current_theme
    ):
        try:
            # Generiere CSS
            css = theme_manager.generate_css()

            # Injiziere CSS
            st.markdown(
                f"<style>{css}</style>",
                unsafe_allow_html=True
            )

            # Merke injiziertes Theme
            st.session_state.injected_theme = current_theme

        except Exception as e:
            st.error(f"Fehler beim Laden des Themes: {e}")


def get_current_theme_name() -> str:
    """
    Gibt den Namen des aktuellen Themes zurück

    Returns:
        Theme-Name aus Session State
    """
    return st.session_state.get('current_theme', 'shadcn-default')


def is_dark_mode() -> bool:
    """
    Prüft ob Dark Mode aktiv ist

    Returns:
        True wenn Dark Mode aktiv
    """
    return st.session_state.get('dark_mode', False)
