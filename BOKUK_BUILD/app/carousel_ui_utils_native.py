"""
Universal Carousel UI Components - NATIVE STREAMLIT VERSION
===========================================================

Verwendet native Streamlit-Komponenten statt HTML für bessere Kompatibilität.
"""

import base64
import os
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

    Verwendet NATIVE STREAMLIT-KOMPONENTEN statt HTML!

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
        # Finde Index der aktuellen Seite
        current_key = st.session_state.get(state_key, options[0][0])
        current_index = next(
            (i for i, (k, _) in enumerate(options) if k == current_key), 0)
        st.session_state[preview_key] = current_index

    if confirm_key not in st.session_state:
        current_key = st.session_state.get(state_key, options[0][0])
        current_index = next(
            (i for i, (k, _) in enumerate(options) if k == current_key), 0)
        st.session_state[confirm_key] = current_index

    preview_index = st.session_state[preview_key]
    confirmed_index = st.session_state[confirm_key]

    # Helper: Bild als base64-Daten-URI laden
    def get_base64_image(path: str) -> str | None:
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None

    # CSS für größere, einheitliche Buttons
    st.markdown("""
    <style>
    /* Sidebar breiter machen */
    [data-testid="stSidebar"] {
        min-width: 340px !important;
        max-width: 340px !important;
    }

    /* Alle Buttons größer und einheitlich */
    .stButton > button {
        height: 75px !important;
        min-height: 75px !important;
        padding: 18px 20px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        white-space: normal !important;
        line-height: 1.5 !important;
        text-align: left !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    /* Success/Info Boxes größer */
    .stSuccess, .stInfo {
        padding: 20px 20px !important;
        min-height: 75px !important;
        display: flex !important;
        align-items: center !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        line-height: 1.5 !important;
    }

    /* Icon hervorheben */
    .stButton > button strong,
    .stSuccess strong,
    .stInfo strong {
        font-size: 17px !important;
        font-weight: 700 !important;
    }

    /* Divider zwischen Items */
    hr {
        margin: 16px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Label und Help Text
    if label:
        st.markdown(f"### {label}")
    if help_text:
        st.caption(help_text)

    st.markdown("---")

    # Berechne sichtbaren Bereich
    half_visible = visible_count // 2
    start_index = max(0, preview_index - half_visible)
    end_index = min(len(options), start_index + visible_count)

    # Korrektur falls am Ende
    if end_index == len(options):
        start_index = max(0, end_index - visible_count)

    # Oben: Rauf-Button mit Bild
    up_img_b64 = get_base64_image("assets/menu_backgrounds/up.png")
    if up_img_b64:
        st.markdown(
            f"""
            <div style="text-align:center;margin:8px 0;">
              <img src="data:image/png;base64,{up_img_b64}" alt="Up" style="max-width:48px;opacity:{'1.0' if preview_index > 0 else '0.4'};">
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.button(
            "⬆️",
            key=f"{state_key}_up",
            disabled=(
                preview_index <= 0),
            use_container_width=True):
        st.session_state[preview_key] = max(0, preview_index - 1)
        st.rerun()

    # Rendere Cards (HTML mit Link) – nur einmal pro Eintrag, keine doppelten
    # Buttons
    for i in range(start_index, end_index):
        key, item_label = options[i]
        icon = icons.get(key, "") if icons else ""

        # Bestimme Typ und Emoji basierend auf Status
        if i == confirmed_index:
            # Aktuell aktive Seite - grün
            button_type = "primary"
            status_emoji = "✓"
            disabled = True
        elif i == preview_index:
            # Preview - blau markiert
            button_type = "secondary"
            status_emoji = "→"
            disabled = False
        else:
            # Dimmed - inaktiv
            button_type = "secondary"
            status_emoji = ""
            disabled = False

        # Mapping von Kategorien zu lokalen Bildern

        category_images = {
            "input": "assets/menu_backgrounds/bedarf.png",
            "solar_calculator": "assets/menu_backgrounds/solar.jpg",
            "heatpump": "assets/menu_backgrounds/heat.jpg",
            "analysis": "assets/menu_backgrounds/ergebnis.jpg",
            "crm": "assets/menu_backgrounds/crm.jpg",
            "options": "assets/menu_backgrounds/setup.jpg",
            "admin": "assets/menu_backgrounds/admin.jpg",
            "doc_output": "assets/menu_backgrounds/pdf.png",
            "quick_calc": "assets/menu_backgrounds/ergebnis.jpg",
            "info_platform": "assets/menu_backgrounds/info.jpg",
        }

        # Bestimme Bildpfad
        image_path = category_images.get(
            key, "assets/menu_backgrounds/bedarf.png")

        img_base64 = get_base64_image(image_path)

        # Nur den Menüpunkt-Namen, keine Icons oder Emojis
        clean_label = item_label

        # Styling basierend auf Status mit Bildern (HTML-Card, klickbar per
        # Link)
        if img_base64:
            # Bestimme Dateiendung für MIME-Type
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/jpeg" if ext in [".jpg",
                                                ".jpeg"] else "image/png"
            img_data_uri = f"data:{mime_type};base64,{img_base64}"

            # Bestimme Border-Style basierend auf Status
            if i == confirmed_index:
                border_style = "border: 3px solid #28a745; box-shadow: 0 4px 20px rgba(40, 167, 69, 0.5);"
                cursor_style = "default"
            elif i == preview_index:
                border_style = "border: 3px solid #007bff; box-shadow: 0 4px 20px rgba(0, 123, 255, 0.5);"
                cursor_style = "default"
            else:
                border_style = "border: 2px solid rgba(255,255,255,0.3);"
                cursor_style = "pointer"

            # Button für Klick - MIT Bild als Hintergrund im Button selbst
            button_key = f"{state_key}_item_{i}"

            if i == confirmed_index:
                # Aktive Card - nicht klickbar, nur Anzeige
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('{img_data_uri}');
                        background-size: cover;
                        background-position: center;
                        border-radius: 12px;
                        padding: 30px;
                        margin: 10px 0;
                        color: white;
                        text-align: center;
                        min-height: 110px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        {border_style}
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                        font-weight: bold;
                        font-size: 16px;
                    ">
                        ✓ {clean_label}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif i == preview_index:
                # Preview Card - nicht klickbar, nur Anzeige
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('{img_data_uri}');
                        background-size: cover;
                        background-position: center;
                        border-radius: 12px;
                        padding: 30px;
                        margin: 10px 0;
                        color: white;
                        text-align: center;
                        min-height: 110px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        {border_style}
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                        font-weight: bold;
                        font-size: 16px;
                    ">
                        → {clean_label}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # Normale Card - HTML + klickbarer Button
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('{img_data_uri}');
                        background-size: cover;
                        background-position: center;
                        border-radius: 12px;
                        padding: 30px;
                        margin: 10px 0;
                        color: white;
                        text-align: center;
                        min-height: 110px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        {border_style}
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                        font-weight: bold;
                        font-size: 16px;
                    ">
                        {clean_label}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Klickbarer Button direkt darunter
                if st.button(
                        f"📍 Wählen: {clean_label}",
                        key=button_key,
                        use_container_width=True):
                    st.session_state[preview_key] = i
                    st.rerun()

    # Unten: Runter-Button mit Bild
    if st.button(
            "⬇️",
            key=f"{state_key}_down",
            disabled=(
                preview_index >= len(options) -
                1),
            use_container_width=True):
        st.session_state[preview_key] = min(
            len(options) - 1, preview_index + 1)
        st.rerun()

    down_img_b64 = get_base64_image("assets/menu_backgrounds/down.png")
    if down_img_b64:
        st.markdown(
            f"""
            <div style="text-align:center;margin:8px 0;">
              <img src="data:image/png;base64,{down_img_b64}" alt="Down" style="max-width:48px;opacity:{'1.0' if preview_index < len(options) - 1 else '0.4'};">
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Confirm Button - wenn Preview != Active
    if preview_index != confirmed_index:
        st.markdown("---")
        preview_label = options[preview_index][1]

        # Enter-Button - KOMPLETT SICHTBAR ohne Bild darüber
        if st.button(
                f"✓ ENTER: {preview_label}",
                key=f"{state_key}_confirm",
                use_container_width=True,
                type="primary"):
            st.session_state[confirm_key] = preview_index
            st.session_state[state_key] = options[preview_index][0]
            st.rerun()

    # Return bestätigten Key
    return options[confirmed_index][0]


def render_horizontal_carousel(
    state_key: str,
    options: list[tuple[str, str]],  # [(key, label), ...]
    *,
    icons: dict[str, str] | None = None,
    visible_count: int = 3,
    theme: Literal["default", "admin", "sidebar"] = "default",
) -> str:
    """
    Rendert ein horizontales Carousel (für Admin-Tabs).

    Verwendet NATIVE STREAMLIT-KOMPONENTEN!

    Args:
        state_key: Session State Key
        options: Liste von (key, label) Tupeln
        icons: Optional dict mit Icons pro Key
        visible_count: Anzahl sichtbarer Items (default 3)
        theme: Farbschema

    Returns:
        str: Key der ausgewählten Option
    """

    # Session State
    index_key = f"{state_key}_index"

    if index_key not in st.session_state:
        current_key = st.session_state.get(state_key, options[0][0])
        current_index = next(
            (i for i, (k, _) in enumerate(options) if k == current_key), 0)
        st.session_state[index_key] = current_index

    current_index = st.session_state[index_key]

    # Berechne sichtbaren Bereich
    half_visible = visible_count // 2
    start_index = max(0, current_index - half_visible)
    end_index = min(len(options), start_index + visible_count)

    if end_index == len(options):
        start_index = max(0, end_index - visible_count)

    # Navigation + Items in Columns
    total_cols = visible_count + 2  # +2 für Left/Right Buttons
    cols = st.columns([0.5] + [1] * visible_count + [0.5])

    # Left Button
    with cols[0]:
        if st.button(
            "◀",
            key=f"{state_key}_left",
            disabled=(
                current_index <= 0)):
            st.session_state[index_key] = max(0, current_index - 1)
            st.session_state[state_key] = options[st.session_state[index_key]][0]
            st.rerun()

    # Items
    for idx, i in enumerate(range(start_index, end_index)):
        with cols[idx + 1]:
            key, item_label = options[i]
            icon = icons.get(key, "") if icons else ""
            display_label = f"[{icon}]\n{item_label}" if icon else item_label

            is_active = (i == current_index)
            button_type = "primary" if is_active else "secondary"

            if st.button(display_label, key=f"{state_key}_item_{i}",
                         use_container_width=True, type=button_type):
                st.session_state[index_key] = i
                st.session_state[state_key] = key
                st.rerun()

    # Right Button
    with cols[-1]:
        if st.button(
            "▶", key=f"{state_key}_right", disabled=(
                current_index >= len(options) - 1)):
            st.session_state[index_key] = min(
                len(options) - 1, current_index + 1)
            st.session_state[state_key] = options[st.session_state[index_key]][0]
            st.rerun()

    return options[current_index][0]
