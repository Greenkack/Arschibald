# admin_ui_effects_settings.py
"""
Datei: admin_ui_effects_settings.py
Zweck: Admin-UI für die Verwaltung globaler UI-Effekte
Autor: GitHub Copilot
Datum: 2025-10-23
"""
import json
from pathlib import Path

import streamlit as st

from ui_effects_library import (
    get_default_effect,
    get_effect_info,
    get_effect_names,
)


def load_ui_effects_settings():
    """Lädt die UI-Effekt-Einstellungen aus JSON"""
    settings_file = Path("data/ui_effects_settings.json")
    default_settings = {
        "active_effect": get_default_effect(),
        "enabled": True
    }

    try:
        if settings_file.exists():
            with open(settings_file, encoding='utf-8') as f:
                loaded = json.load(f)
                # Validierung: Prüfe ob der Effekt existiert
                if loaded.get("active_effect") not in get_effect_names():
                    loaded["active_effect"] = get_default_effect()
                return loaded
    except Exception as e:
        st.error(f"Fehler beim Laden der Effekt-Einstellungen: {e}")

    return default_settings


def save_ui_effects_settings(settings):
    """Speichert die UI-Effekt-Einstellungen in JSON"""
    settings_file = Path("data/ui_effects_settings.json")
    settings_file.parent.mkdir(exist_ok=True, parents=True)

    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Effekt-Einstellungen: {e}")
        return False


def render_ui_effects_admin():
    """
    Rendert die Admin-Oberfläche für UI-Effekte-Einstellungen
    """
    st.subheader("Globale UI-Effekte")
    st.info("Wählen Sie einen Effekt-Stil aus, der auf alle Buttons, Slider, Dropdowns und Expander in der gesamten Anwendung angewendet wird.")

    # Lade aktuelle Einstellungen
    current_settings = load_ui_effects_settings()
    current_effect = current_settings.get(
        "active_effect", get_default_effect())
    is_enabled = current_settings.get("enabled", True)

    # Effekte aktivieren/deaktivieren
    st.markdown("---")
    st.markdown("#### ⚙️ Grundeinstellungen")

    enabled = st.checkbox(
        "UI-Effekte aktivieren",
        value=is_enabled,
        help="Aktiviert oder deaktiviert alle UI-Effekte global"
    )

    if not enabled:
        st.warning(
            "UI-Effekte sind derzeit deaktiviert. Aktivieren Sie sie, um einen Effekt auszuwählen.")

    st.markdown("---")
    st.markdown("####  Effekt-Auswahl")

    # Erstelle eine Liste mit Effekt-Optionen für das Selectbox
    effect_options = []
    for effect_key in get_effect_names():
        effect_info = get_effect_info(effect_key)
        effect_name = effect_info.get("name", effect_key)
        effect_options.append((effect_key, effect_name))

    # Finde den aktuellen Index
    current_index = 0
    for idx, (key, name) in enumerate(effect_options):
        if key == current_effect:
            current_index = idx
            break

    # Selectbox für Effekt-Auswahl
    selected_effect_tuple = st.selectbox(
        "Wählen Sie einen Effekt-Stil",
        options=effect_options,
        format_func=lambda x: x[1],  # Zeige nur den Namen
        index=current_index,
        disabled=not enabled,
        help="Wählen Sie aus 10 verschiedenen visuellen Effekt-Stilen"
    )

    selected_effect_key = selected_effect_tuple[0]

    # Zeige Beschreibung des ausgewählten Effekts
    if selected_effect_key:
        effect_info = get_effect_info(selected_effect_key)
        effect_name = effect_info.get("name", selected_effect_key)
        effect_description = effect_info.get(
            "description", "Keine Beschreibung verfügbar")

        st.markdown("---")
        st.markdown("#### Effekt-Details")

        # Styled Info Box
        st.markdown(f"""
        <div style="
            padding: 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
        ">
            <h5 style="margin: 0 0 10px 0; color: #667eea;">✨ {effect_name}</h5>
            <p style="margin: 0; color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
                {effect_description}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Effekt-Vorschau mit Beispiel-Button
        st.markdown("####  Live-Vorschau")
        st.markdown(
            "Bewegen Sie die Maus über die Elemente, um den Effekt zu sehen:")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "🔘 Beispiel Button",
                key="preview_btn_1",
                    help="Hover für Effekt"):
                pass

        with col2, st.expander(" Beispiel Expander"):
            st.write("Beispielinhalt")

        with col3:
            st.number_input(
                "Beispiel Slider",
                min_value=0,
                max_value=100,
                value=50,
                key="preview_slider")

    # Speichern-Button
    st.markdown("---")

    col_save, col_reset = st.columns([3, 1])

    with col_save:
        if st.button(
            " Einstellungen speichern",
            type="primary",
                use_container_width=True):
            new_settings = {
                "active_effect": selected_effect_key,
                "enabled": enabled
            }

            if save_ui_effects_settings(new_settings):
                st.success(
                    f"UI-Effekt '{effect_info.get('name')}' wurde erfolgreich gespeichert!")
                st.info(
                    "Die Änderungen werden beim nächsten Laden der Seite aktiv. Bitte laden Sie die Seite neu (F5).")

                # Optional: Auto-Rerun nach kurzer Verzögerung
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Fehler beim Speichern der Einstellungen!")

    with col_reset:
        if st.button(" Zurücksetzen", help="Auf Standard zurücksetzen"):
            default_settings = {
                "active_effect": get_default_effect(),
                "enabled": True
            }
            if save_ui_effects_settings(default_settings):
                st.success("Auf Standard zurückgesetzt!")
                st.rerun()

    # Hinweise und Dokumentation
    st.markdown("---")
    st.markdown("#### Hinweise")

    with st.expander(" Effekt-Übersicht", expanded=False):
        st.markdown("""
        **Verfügbare Effekte:**

        1. **Shimmer + Pulse** - Glänzender Sweep mit Puls-Animation (Standard)
        2. **Glow + Bounce** - Leuchtender Glow mit Bounce-Bewegung
        3. **Neon + Wave** - Neon-Effekt mit wellenförmiger Animation
        4. **Gradient + Slide** - Farbverlauf mit gleitender Bewegung
        5. **Glass + Morph** - Glasmorphismus mit Morphing-Animation
        6. **Minimal + Fade** - Minimalistisch mit sanften Übergängen
        7. **Retro + Pixel** - Retro-Gaming-Stil mit pixeliger Animation
        8. **Rainbow + Spin** - Regenbogen-Farbverlauf mit Rotation
        9. **Cyberpunk + Glitch** - Cyberpunk-Stil mit Glitch-Effekt
        10. **Elegant + Luxury** - Luxus-Stil mit goldenen Akzenten

        **Betroffene Elemente:**
        - Alle Buttons (Primary, Secondary, Standard)
        - Slider-Steuerelemente (+/- Buttons)
        - Dropdown-Menüs
        - Expander/Accordion-Elemente
        - Checkboxen und Radio-Buttons
        """)

    with st.expander(" Technische Details", expanded=False):
        st.markdown("""
        **Implementierung:**
        - Die Effekte werden als CSS-Animationen implementiert
        - Änderungen werden in `data/ui_effects_settings.json` gespeichert
        - Die Effekte werden beim Start der Anwendung geladen
        - Keine Auswirkung auf die Performance bei modernen Browsern

        **Kompatibilität:**
        - Alle modernen Browser (Chrome, Firefox, Safari, Edge)
        - Mobile Geräte werden unterstützt
        - Fallback auf Standard-Styling bei älteren Browsern

        **Wartung:**
        - Neue Effekte können in `ui_effects_library.py` hinzugefügt werden
        - Jeder Effekt ist modular und unabhängig
        - Effekte können individuell angepasst werden
        """)

    # Aktueller Status
    st.markdown("---")
    st.markdown("#### Aktueller Status")

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.metric("Aktiver Effekt", effect_info.get("name", "N/A"))

    with status_col2:
        st.metric("Status", "🟢 Aktiv" if enabled else "🔴 Deaktiviert")
