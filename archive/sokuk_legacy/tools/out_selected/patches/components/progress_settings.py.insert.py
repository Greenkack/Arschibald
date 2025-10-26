# === AUTO-GENERATED INSERT PATCH ===
# target_module: components/progress_settings.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import streamlit as st

from .progress_manager import (
    ProgressStyle,
    progress_manager,
    set_progress_colors,
    set_progress_style,
)


# --- DEF BLOCK START: func render_progress_settings ---
def render_progress_settings():
    """Rendert die Einstellungen für Ladebalken im Optionen-Menü"""

    st.subheader("🎨 Ladebalken-Design")

    # Style-Auswahl
    col1, col2 = st.columns(2)

    with col1:
        current_style = st.session_state.get(
            'progress_config', progress_manager.config).style

        style_options = {
            "Standard (shadcn)": ProgressStyle.SHADCN_DEFAULT,
            "Minimal": ProgressStyle.SHADCN_MINIMAL,
            "Gradient": ProgressStyle.SHADCN_GRADIENT,
            "Animiert": ProgressStyle.SHADCN_ANIMATED,
            "Modern": ProgressStyle.SHADCN_MODERN
        }

        # Finde aktuellen Index
        current_index = 0
        for i, (name, style) in enumerate(style_options.items()):
            if style == current_style:
                current_index = i
                break

        selected_style_name = st.selectbox(
            "Ladebalken-Style",
            options=list(style_options.keys()),
            index=current_index,
            help="Wählen Sie das Design für alle Ladebalken in der App"
        )

        selected_style = style_options[selected_style_name]

        if selected_style != current_style:
            set_progress_style(selected_style)
            st.rerun()

    with col2:
        # Farbauswahl
        current_config = st.session_state.get(
            'progress_config', progress_manager.config)

        primary_color = st.color_picker(
            "Primärfarbe",
            value=current_config.color_primary,
            help="Hauptfarbe für den Ladebalken"
        )

        secondary_color = st.color_picker(
            "Sekundärfarbe",
            value=current_config.color_secondary,
            help="Akzentfarbe für Farbverläufe"
        )

        background_color = st.color_picker(
            "Hintergrundfarbe",
            value=current_config.color_background,
            help="Hintergrundfarbe des Ladebalkens"
        )

        # Farben aktualisieren
        if (primary_color != current_config.color_primary or
            secondary_color != current_config.color_secondary or
                background_color != current_config.color_background):
            set_progress_colors(
                primary_color,
                secondary_color,
                background_color)

    # Zusätzliche Optionen
    st.subheader("⚙️ Erweiterte Optionen")

    col3, col4 = st.columns(2)

    with col3:
        show_percentage = st.checkbox(
            "Prozentanzeige",
            value=current_config.show_percentage,
            help="Zeigt den Fortschritt in Prozent an"
        )

        show_text = st.checkbox(
            "Textanzeige",
            value=current_config.show_text,
            help="Zeigt beschreibenden Text über dem Ladebalken"
        )

    with col4:
        height = st.slider(
            "Höhe des Ladebalkens",
            min_value=4,
            max_value=20,
            value=current_config.height,
            help="Höhe in Pixeln"
        )

        animation_speed = st.slider(
            "Animationsgeschwindigkeit",
            min_value=0.5,
            max_value=3.0,
            value=current_config.animation_speed,
            step=0.1,
            help="Geschwindigkeit der Animationen"
        )

    # Konfiguration aktualisieren
    if (show_percentage != current_config.show_percentage or
        show_text != current_config.show_text or
        height != current_config.height or
            animation_speed != current_config.animation_speed):

        current_config.show_percentage = show_percentage
        current_config.show_text = show_text
        current_config.height = height
        current_config.animation_speed = animation_speed
        st.session_state.progress_config = current_config

    # Vorschau
    st.subheader("👀 Vorschau")

    # Demo-Ladebalken
    if st.button("Demo starten", type="primary"):
        demo_progress_bar(selected_style)
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func demo_progress_bar ---
def demo_progress_bar(style: ProgressStyle):
    """Zeigt eine Demo des ausgewählten Ladebalken-Styles"""
    import time

    from .progress_manager import create_progress_bar

    # Container für Demo
    demo_container = st.container()

    with demo_container:
        st.info("Demo läuft - so sieht Ihr Ladebalken aus:")

        # Erstelle Demo-Progress Bar
        progress_bar = create_progress_bar(
            "Demo wird ausgeführt...", demo_container)

        # Simuliere Fortschritt
        steps = [
            (0, "Initialisierung..."),
            (15, "Daten werden geladen..."),
            (35, "Berechnungen laufen..."),
            (60, "Ergebnisse werden verarbeitet..."),
            (85, "PDF wird erstellt..."),
            (100, "Demo abgeschlossen!")
        ]

        for value, text in steps:
            progress_bar.update(value, text)
            time.sleep(0.5)

        # Kurz warten dann aufräumen
        time.sleep(1)
        demo_container.empty()
        st.success("Demo beendet! So sehen Ihre Ladebalken aus.")
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_quick_themes ---
def render_quick_themes():
    """Rendert Quick-Theme-Buttons"""
    st.subheader("🎨 Schnell-Designs")

    cols = st.columns(len(PRESET_THEMES))

    for i, (theme_name, colors) in enumerate(PRESET_THEMES.items()):
        with cols[i]:
            if st.button(theme_name, key=f"theme_{i}"):
                set_progress_colors(
                    colors["primary"],
                    colors["secondary"],
                    colors["background"]
                )
                st.success(f"{theme_name} angewendet!")
                st.rerun()
# --- DEF BLOCK END ---
