# === AUTO-GENERATED INSERT PATCH ===
# target_module: components/progress_manager.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

import streamlit as st


# --- DEF BLOCK START: func set_progress_style ---
def set_progress_style(style: ProgressStyle):
    """Ändert den globalen Ladebalken-Style"""
    progress_manager.set_style(style)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func set_progress_colors ---
def set_progress_colors(
        primary: str,
        secondary: str = None,
        background: str = None):
    """Ändert die Ladebalken-Farben"""
    progress_manager.set_colors(primary, secondary, background)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func progress ---
@contextmanager
def progress(title: str = "Verarbeitung läuft...",
             container: st.container | None = None):
    """Einfacher Context Manager für Ladebalken"""
    with progress_manager.progress_context(title, container) as progress_bar:
        yield progress_bar
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func create_progress_bar ---
def create_progress_bar(
        title: str = "",
        container: st.container | None = None) -> ProgressBar:
    """Erstellt einen neuen Ladebalken"""
    return progress_manager.create_progress_bar(
        f"progress_{int(time.time() * 1000)}", title, container)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func with_progress ---
def with_progress(title: str = "Verarbeitung läuft..."):
    """Decorator für automatische Ladebalken-Anzeige"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            with progress(title) as progress_bar:
                # Simuliere Fortschritt für Berechnungen
                progress_bar.update(10, "Initialisierung...")
                time.sleep(0.1)
                progress_bar.update(30, "Daten werden verarbeitet...")
                result = func(*args, **kwargs)
                progress_bar.update(90, "Finalisierung...")
                time.sleep(0.1)
                progress_bar.complete("Fertig!")
                return result
        return wrapper
    return decorator
# --- DEF BLOCK END ---


# --- DEF BLOCK START: class ProgressStyle ---
class ProgressStyle(Enum):
    """Verfügbare Ladebalken-Styles im shadcn Design"""
    SHADCN_DEFAULT = "shadcn_default"
    SHADCN_MINIMAL = "shadcn_minimal"
    SHADCN_GRADIENT = "shadcn_gradient"
    SHADCN_ANIMATED = "shadcn_animated"
    SHADCN_MODERN = "shadcn_modern"
# --- DEF BLOCK END ---


# --- DEF BLOCK START: class ProgressConfig ---
@dataclass
class ProgressConfig:
    """Konfiguration für Ladebalken"""
    style: ProgressStyle = ProgressStyle.SHADCN_DEFAULT
    color_primary: str = "#18181b"  # shadcn zinc-900
    color_secondary: str = "#3b82f6"  # shadcn blue-500
    color_background: str = "#f4f4f5"  # shadcn zinc-100
    show_percentage: bool = True
    show_text: bool = True
    animation_speed: float = 1.0
    height: int = 8
    border_radius: int = 6
# --- DEF BLOCK END ---


# --- DEF BLOCK START: class ProgressManager ---
class ProgressManager:
    """Zentraler Manager für alle Ladebalken in der App"""

    def __init__(self):
        self.config = ProgressConfig()
        self._active_progress = {}
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialisiert Session State für Progress Manager"""
        if 'progress_config' not in st.session_state:
            st.session_state.progress_config = self.config
        if 'progress_active' not in st.session_state:
            st.session_state.progress_active = {}

    def set_style(self, style: ProgressStyle):
        """Ändert den globalen Ladebalken-Style"""
        self.config.style = style
        st.session_state.progress_config.style = style

    def set_colors(
            self,
            primary: str,
            secondary: str = None,
            background: str = None):
        """Ändert die Farben des Ladebalkens"""
        self.config.color_primary = primary
        if secondary:
            self.config.color_secondary = secondary
        if background:
            self.config.color_background = background
        st.session_state.progress_config = self.config

    @contextmanager
    def progress_context(self, title: str = "Verarbeitung läuft...",
                         container: st.container | None = None):
        """Context Manager für automatischen Ladebalken"""
        progress_id = f"progress_{int(time.time() * 1000)}"

        try:
            # Erstelle Progress Bar
            progress_bar = self.create_progress_bar(
                progress_id, title, container
            )
            yield progress_bar
        finally:
            # Cleanup
            if progress_id in st.session_state.progress_active:
                del st.session_state.progress_active[progress_id]

    def create_progress_bar(
            self,
            progress_id: str,
            title: str = "",
            container: st.container | None = None) -> 'ProgressBar':
        """Erstellt einen neuen Ladebalken"""
        if container is None:
            container = st.container()

        progress_bar = ProgressBar(
            progress_id, title, container, self.config
        )

        st.session_state.progress_active[progress_id] = {
            'bar': progress_bar,
            'container': container
        }

        return progress_bar

    def get_style_css(self) -> str:
        """Generiert CSS für den aktuellen Style im shadcn Design"""
        config = st.session_state.progress_config

        base_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        .progress-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 1rem 0;
        }

        .progress-text {
            font-size: 0.875rem;
            font-weight: 500;
            color: #09090b;
            margin-bottom: 0.5rem;
            line-height: 1.25rem;
        }

        .progress-percentage {
            font-size: 0.75rem;
            color: #71717a;
            text-align: right;
            margin-top: 0.25rem;
            font-weight: 500;
        }
        </style>
        """

        if config.style == ProgressStyle.SHADCN_DEFAULT:
            return base_css + self._get_shadcn_default_css(config)
        if config.style == ProgressStyle.SHADCN_MINIMAL:
            return base_css + self._get_shadcn_minimal_css(config)
        if config.style == ProgressStyle.SHADCN_GRADIENT:
            return base_css + self._get_shadcn_gradient_css(config)
        if config.style == ProgressStyle.SHADCN_ANIMATED:
            return base_css + self._get_shadcn_animated_css(config)
        if config.style == ProgressStyle.SHADCN_MODERN:
            return base_css + self._get_shadcn_modern_css(config)
        return base_css + self._get_shadcn_default_css(config)

    def _get_shadcn_default_css(self, config: ProgressConfig) -> str:
        return f"""
        <style>
        .shadcn-default-progress {{
            width: 100%;
            height: {config.height}px;
            background-color: {config.color_background};
            border-radius: {config.border_radius}px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 1px 3px 0 rgb(0 0 0 / 0.1);
        }}
        .shadcn-default-progress-bar {{
            height: 100%;
            background-color: {config.color_secondary};
            border-radius: {config.border_radius}px;
            transition: width 0.5s cubic-bezier(0.65, 0, 0.35, 1);
            position: relative;
        }}
        </style>
        """

    def _get_shadcn_minimal_css(self, config: ProgressConfig) -> str:
        return f"""
        <style>
        .shadcn-minimal-progress {{
            width: 100%;
            height: {config.height // 2}px;
            background-color: transparent;
            border-bottom: 1px solid #e4e4e7;
            position: relative;
        }}
        .shadcn-minimal-progress-bar {{
            height: 100%;
            background-color: {config.color_primary};
            transition: width 0.3s ease-out;
        }}
        .progress-text {{
            font-size: 0.75rem;
            color: #71717a;
            margin-bottom: 0.25rem;
        }}
        </style>
        """

    def _get_shadcn_gradient_css(self, config: ProgressConfig) -> str:
        return f"""
        <style>
        .shadcn-gradient-progress {{
            width: 100%;
            height: {config.height}px;
            background: linear-gradient(90deg, {config.color_background}, #e4e4e7);
            border-radius: {config.border_radius}px;
            overflow: hidden;
            position: relative;
            border: 1px solid #e4e4e7;
        }}
        .shadcn-gradient-progress-bar {{
            height: 100%;
            background: linear-gradient(45deg, {config.color_secondary}, #8b5cf6, #06b6d4);
            border-radius: {config.border_radius}px;
            transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
        }}
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .progress-text {{
            background: linear-gradient(45deg, {config.color_secondary}, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        </style>
        """

    def _get_shadcn_animated_css(self, config: ProgressConfig) -> str:
        return f"""
        <style>
        .shadcn-animated-progress {{
            width: 100%;
            height: {config.height}px;
            background-color: {config.color_background};
            border-radius: {config.border_radius}px;
            overflow: hidden;
            position: relative;
            border: 1px solid #e4e4e7;
        }}
        .shadcn-animated-progress-bar {{
            height: 100%;
            background-color: {config.color_secondary};
            border-radius: {config.border_radius}px;
            transition: width 0.5s cubic-bezier(0.65, 0, 0.35, 1);
            position: relative;
            overflow: hidden;
        }}
        .shadcn-animated-progress-bar::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -50%;
            height: 100%;
            width: 50%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer {2 / config.animation_speed}s infinite;
        }}
        @keyframes shimmer {{
            0% {{ left: -50%; }}
            100% {{ left: 100%; }}
        }}
        .progress-text {{
            animation: pulse 2s ease-in-out infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        </style>
        """

    def _get_shadcn_modern_css(self, config: ProgressConfig) -> str:
        return f"""
        <style>
        .shadcn-modern-progress {{
            width: 100%;
            height: {config.height + 2}px;
            background-color: {config.color_background};
            border-radius: {config.border_radius + 2}px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            border: 1px solid #e4e4e7;
        }}
        .shadcn-modern-progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, {config.color_secondary}, #06b6d4);
            border-radius: {config.border_radius + 2}px;
            transition: width 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            position: relative;
        }}
        .shadcn-modern-progress-bar::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shine 2s infinite;
        }}
        @keyframes shine {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        .progress-text {{
            font-weight: 600;
            color: #18181b;
        }}
        .progress-percentage {{
            color: {config.color_secondary};
            font-weight: 600;
        }}
        </style>
        """
# --- DEF BLOCK END ---


# --- DEF BLOCK START: class ProgressBar ---
class ProgressBar:
    """Einzelner Ladebalken mit shadcn UI Design"""

    def __init__(self, progress_id: str, title: str, container: st.container,
                 config: ProgressConfig):
        self.progress_id = progress_id
        self.title = title
        self.container = container
        self.config = config
        self.current_value = 0
        self.max_value = 100
        self._placeholder = None
        self._initialize()

    def _initialize(self):
        """Initialisiert den Ladebalken"""
        with self.container:
            self._placeholder = st.empty()
            self._render()

    def update(self, value: int, text: str = None):
        """Aktualisiert den Ladebalken"""
        self.current_value = min(max(0, value), self.max_value)
        if text:
            self.title = text
        self._render()

    def set_max(self, max_value: int):
        """Setzt den Maximalwert"""
        self.max_value = max_value
        self._render()

    def increment(self, step: int = 1, text: str = None):
        """Erhöht den Fortschritt um einen Schritt"""
        self.update(self.current_value + step, text)

    def complete(self, text: str = "Abgeschlossen!"):
        """Setzt den Ladebalken auf 100%"""
        self.update(100, text)
        time.sleep(0.5)  # Kurz anzeigen bevor cleanup

    def _render(self):
        """Rendert den Ladebalken im shadcn Design"""
        if not self._placeholder:
            return

        percentage = (self.current_value / self.max_value) * 100
        style_class = self.config.style.value.replace('_', '-')

        html = """
        <div class="progress-container">
        """

        if self.config.show_text and self.title:
            html += f'<div class="progress-text">{self.title}</div>'

        html += f"""
            <div class="{style_class}-progress">
                <div class="{style_class}-progress-bar" style="width: {percentage}%"></div>
            </div>
        """

        if self.config.show_percentage:
            html += f'<div class="progress-percentage">{percentage:.0f}%</div>'

        html += "</div>"

        with self._placeholder.container():
            st.markdown(
                progress_manager.get_style_css(),
                unsafe_allow_html=True)
            st.markdown(html, unsafe_allow_html=True)
# --- DEF BLOCK END ---
