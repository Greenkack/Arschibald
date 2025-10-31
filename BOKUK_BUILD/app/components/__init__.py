"""
Components Package für die Solar-App
Enthält wiederverwendbare UI-Komponenten mit shadcn UI Design
"""

# Hauptkomponenten exportieren
try:
    from .progress_manager import (
        ProgressBar,
        ProgressContext,
        ProgressManager,
        ProgressStyle,
        create_progress_bar,
        progress_decorator,
        progress_manager,
        set_progress_colors,
        set_progress_style,
    )

    PROGRESS_MANAGER_AVAILABLE = True

except ImportError:
    PROGRESS_MANAGER_AVAILABLE = False

    # Fallback-Implementierungen für den Fall, dass Abhängigkeiten fehlen
    class ProgressStyle:
        SHADCN_DEFAULT = "default"
        SHADCN_MINIMAL = "minimal"
        SHADCN_GRADIENT = "gradient"
        SHADCN_ANIMATED = "animated"
        SHADCN_MODERN = "modern"

    def create_progress_bar(message, container=None):
        """Fallback progress bar"""
        import streamlit as st
        if container:
            return container.progress(0, text=message)
        return st.progress(0, text=message)

    def progress_decorator(message):
        """Fallback decorator"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                import streamlit as st
                with st.spinner(message):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    class ProgressContext:
        """Fallback context manager"""

        def __init__(self, message):
            self.message = message

        def __enter__(self):
            import streamlit as st
            self.spinner = st.spinner(self.message)
            self.spinner.__enter__()
            return self

        def __exit__(self, *args):
            self.spinner.__exit__(*args)

        def update(self, value, text=""):
            # Fallback: nichts zu updaten bei st.spinner
            pass

# Settings-Komponenten
try:
    from .progress_settings import render_progress_settings, render_quick_themes
    PROGRESS_SETTINGS_AVAILABLE = True
except ImportError:
    PROGRESS_SETTINGS_AVAILABLE = False

    def render_progress_settings():
        """Fallback settings"""
        import streamlit as st
        st.info("Progress Settings nicht verfügbar (Abhängigkeiten fehlen)")

    def render_quick_themes():
        """Fallback themes"""
        import streamlit as st
        st.info("Quick Themes nicht verfügbar (Abhängigkeiten fehlen)")

# Exportierte Symbole
__all__ = [
    'ProgressStyle',
    'ProgressManager',
    'ProgressBar',
    'ProgressContext',
    'progress_manager',
    'create_progress_bar',
    'progress_decorator',
    'set_progress_style',
    'set_progress_colors',
    'render_progress_settings',
    'render_quick_themes',
    'PROGRESS_MANAGER_AVAILABLE',
    'PROGRESS_SETTINGS_AVAILABLE'
]

# Version Information
__version__ = "1.0.0"
__author__ = "Solar-App Team"
__description__ = "Wiederverwendbare UI-Komponenten mit shadcn UI Design"
