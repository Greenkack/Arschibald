"""
Universal Carousel UI Components
================================

Wiederverwendbare Carousel-Komponenten für horizontale und vertikale Navigation.
Unterstützt verschiedene Themes und Modi (mit/ohne Confirmation).

Author: Bokuk2 Team
Created: 2025-10-19
"""

from typing import Literal

import streamlit as st


def render_vertical_carousel_with_confirmation(
    state_key: str,
    options: list[tuple[str, str]],  # [(key, label), ...]
    *,
    icons: dict[str, str] | None = None,
    visible_count: int = 5,
    theme: Literal["default", "admin", "sidebar"] = "sidebar",
    label: str | None = None,
    help_text: str | None = None,
) -> str:
    """
    Rendert ein vertikales Carousel mit Confirmation-Step.

    Zwei-Stufen-Navigation:
    1. Scroll/Navigate durch Optionen (Preview)
    2. Bestätigen um tatsächlich zu navigieren

    Args:
        state_key: Session State Key für aktive Seite
        options: Liste von (key, label) Tupeln
        icons: Optional dict mit Icons pro Key
        visible_count: Anzahl sichtbarer Items (default 5)
        theme: Farbschema ("default", "admin", "sidebar")
        label: Optional Label über Carousel
        help_text: Optional Hilfetext

    Returns:
        str: Key der bestätigten/aktiven Option
    """

    # Session State Keys
    preview_key = f"{state_key}_preview_index"
    confirm_key = f"{state_key}_confirmed"

    # Initialisierung
    if preview_key not in st.session_state:
        st.session_state[preview_key] = 0
    if confirm_key not in st.session_state:
        # Suche Index der aktuell aktiven Seite
        current_active = st.session_state.get(state_key)
        active_index = 0
        for i, (key, _) in enumerate(options):
            if key == current_active:
                active_index = i
                break
        st.session_state[confirm_key] = active_index
        st.session_state[preview_key] = active_index

    preview_index = st.session_state[preview_key]
    confirmed_index = st.session_state[confirm_key]

    # Sicherstellen dass Indices gültig sind
    preview_index = max(0, min(preview_index, len(options) - 1))
    confirmed_index = max(0, min(confirmed_index, len(options) - 1))

    # Theme-Farben
    themes = {
        "default": {
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "preview_border": "#667eea",
            "active_bg": "#764ba2",
        },
        "admin": {
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "preview_border": "#667eea",
            "active_bg": "#764ba2",
        },
        "sidebar": {
            "gradient": "linear-gradient(135deg, #4a5568 0%, #2d3748 100%)",
            "preview_border": "#4299e1",
            "active_bg": "#2d3748",
        },
    }

    theme_colors = themes.get(theme, themes["default"])

    # CSS Styling
    st.markdown(f"""
    <style>
    .vertical-carousel-container {{
        background: {theme_colors["gradient"]};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}

    .carousel-label {{
        color: white;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 12px;
        text-align: center;
    }}

    .carousel-help {{
        color: rgba(255, 255, 255, 0.8);
        font-size: 11px;
        margin-bottom: 8px;
        text-align: center;
    }}

    .vertical-carousel-items {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 12px 0;
    }}

    .vertical-carousel-card {{
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 12px;
        color: white;
        text-align: center;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }}

    .vertical-carousel-card.dimmed {{
        opacity: 0.4;
    }}

    .vertical-carousel-card.preview {{
        border-color: {theme_colors["preview_border"]};
        background: rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 12px {theme_colors["preview_border"]};
        transform: scale(1.05);
        opacity: 1;
    }}

    .vertical-carousel-card.active {{
        background: {theme_colors["active_bg"]};
        border-color: #48bb78;
        box-shadow: 0 0 16px rgba(72, 187, 120, 0.6);
        font-weight: 700;
        opacity: 1;
    }}

    .carousel-icon {{
        font-size: 16px;
        font-weight: bold;
        color: rgba(255, 255, 255, 0.9);
    }}

    .carousel-nav-buttons {{
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin: 12px 0;
    }}

    .carousel-confirm-button {{
        margin-top: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Container starten
    html_content = '<div class="vertical-carousel-container">'

    if label:
        html_content += f'<div class="carousel-label">{label}</div>'
    if help_text:
        html_content += f'<div class="carousel-help">{help_text}</div>'

    html_content += '<div class="vertical-carousel-items">'

    # Berechne sichtbaren Bereich
    half_visible = visible_count // 2
    start_index = max(0, preview_index - half_visible)
    end_index = min(len(options), start_index + visible_count)

    # Korrektur falls am Ende
    if end_index == len(options):
        start_index = max(0, end_index - visible_count)

    # Rendere Cards
    for i in range(start_index, end_index):
        key, item_label = options[i]
        icon = icons.get(key, "") if icons else ""

        # CSS-Klassen bestimmen
        classes = ["vertical-carousel-card"]
        if i == confirmed_index:
            classes.append("active")
        elif i == preview_index:
            classes.append("preview")
        else:
            classes.append("dimmed")

        class_str = " ".join(classes)

        html_content += f'''
        <div class="{class_str}">
            {f'<span class="carousel-icon">{icon}</span>' if icon else ''}
            <span>{item_label}</span>
        </div>
        '''

    html_content += '</div>'  # vertical-carousel-items
    html_content += '</div>'  # vertical-carousel-container

    st.markdown(html_content, unsafe_allow_html=True)

    # Navigation Buttons
    col_up, col_down = st.columns(2)

    with col_up:
        if st.button("↑ Hoch", key=f"{state_key}_up", use_container_width=True,
                     disabled=(preview_index <= 0)):
            st.session_state[preview_key] = max(0, preview_index - 1)
            st.rerun()

    with col_down:
        if st.button(
            "↓ Runter",
            key=f"{state_key}_down",
            use_container_width=True,
            disabled=(
                preview_index >= len(options) -
                1)):
            st.session_state[preview_key] = min(
                len(options) - 1, preview_index + 1)
            st.rerun()

    # Confirm Button (nur zeigen wenn Preview != Active)
    if preview_index != confirmed_index:
        st.markdown(
            '<div class="carousel-confirm-button"></div>',
            unsafe_allow_html=True)
        preview_label = options[preview_index][1]
        if st.button(f"✓ Wechseln zu: {preview_label}",
                     key=f"{state_key}_confirm",
                     use_container_width=True,
                     type="primary"):
            st.session_state[confirm_key] = preview_index
            # Aktualisiere auch die eigentliche State-Variable
            st.session_state[state_key] = options[preview_index][0]
            st.rerun()

    # Return bestätigten Key
    return options[confirmed_index][0]


def render_horizontal_carousel(
    state_key: str,
    options: list[tuple[str, str]],
    *,
    icons: dict[str, str] | None = None,
    visible_count: int = 3,
    theme: Literal["default", "admin"] = "default",
    label: str | None = None,
    help_text: str | None = None,
) -> str:
    """
    Rendert ein horizontales Carousel (wie im Admin-Panel).

    Args:
        state_key: Session State Key
        options: Liste von (key, label) Tupeln
        icons: Optional dict mit Icons
        visible_count: Anzahl sichtbarer Items (default 3)
        theme: Farbschema
        label: Optional Label
        help_text: Optional Hilfetext

    Returns:
        str: Key der ausgewählten Option
    """

    # Initialisierung
    if state_key not in st.session_state:
        st.session_state[state_key] = options[0][0]

    current_key = st.session_state[state_key]
    current_index = 0
    for i, (key, _) in enumerate(options):
        if key == current_key:
            current_index = i
            break

    # Theme-Farben
    themes = {
        "default": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "admin": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    }
    gradient = themes.get(theme, themes["default"])

    # CSS (vereinfacht - aus admin_panel.py)
    st.markdown(f"""
    <style>
    .horizontal-carousel {{
        background: {gradient};
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }}
    .h-carousel-cards {{
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 16px 0;
    }}
    .h-carousel-card {{
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid transparent;
        border-radius: 10px;
        padding: 20px;
        min-width: 150px;
        text-align: center;
        color: white;
        cursor: pointer;
        transition: all 0.3s;
    }}
    .h-carousel-card.active {{
        background: rgba(255, 255, 255, 0.25);
        border-color: white;
        transform: scale(1.08);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

    # Render (vereinfacht)
    html = '<div class="horizontal-carousel">'
    if label:
        html += f'<div style="color: white; text-align: center; font-weight: 600; margin-bottom: 12px;">{label}</div>'

    html += '<div class="h-carousel-cards">'

    # Berechne sichtbaren Bereich
    half = visible_count // 2
    start = max(0, current_index - half)
    end = min(len(options), start + visible_count)

    for i in range(start, end):
        key, item_label = options[i]
        icon = icons.get(key, "") if icons else ""
        active_class = " active" if i == current_index else ""

        html += f'''
        <div class="h-carousel-card{active_class}">
            {f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''}
            <div>{item_label}</div>
        </div>
        '''

    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

    # Navigation
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button(
            "◄ Zurück",
            key=f"{state_key}_prev",
            disabled=(
                current_index <= 0)):
            st.session_state[state_key] = options[current_index - 1][0]
            st.rerun()
    with col_next:
        if st.button(
            "Weiter ►",
            key=f"{state_key}_next",
            disabled=(
                current_index >= len(options) -
                1)):
            st.session_state[state_key] = options[current_index + 1][0]
            st.rerun()

    return current_key
