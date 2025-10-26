"""
Demo-Script für den Progress Manager
Zeigt alle Funktionen und Verwendungsmöglichkeiten
"""

import time

import streamlit as st

from components.progress_manager import (
    ProgressContext,
    ProgressStyle,
    create_progress_bar,
    progress_decorator,
    progress_manager,
)


def main():
    st.title("🎯 Progress Manager Demo")
    st.markdown(
        "Demo aller Ladebalken-Features mit verschiedenen Design-Optionen")

    # Demo 1: Einfacher Progress Bar
    st.header("1. 📊 Einfacher Progress Bar")
    if st.button("Starte einfache Demo", key="demo1"):
        progress_bar = create_progress_bar("Lade Daten...", st.container())

        for i in range(0, 101, 20):
            progress_bar.update(
                i, f"Schritt {
                    i // 20 + 1}/5 wird verarbeitet...")
            time.sleep(0.5)

        progress_bar.complete("Alle Daten geladen!")
        time.sleep(1)

    # Demo 2: Context Manager
    st.header("2. 🔄 Context Manager")
    if st.button("Starte Context Manager Demo", key="demo2"):
        with ProgressContext("Verarbeite mit Context Manager...") as progress:
            for i in range(5):
                progress.update((i + 1) * 20, f"Verarbeite Block {i + 1}/5...")
                time.sleep(0.3)

    # Demo 3: Decorator
    st.header("3. ⚡ Progress Decorator")

    @progress_decorator("Berechne komplexe Simulation...")
    def complex_calculation():
        # Simuliere komplexe Berechnung
        for i in range(10):
            time.sleep(0.2)
        return "Berechnung erfolgreich!"

    if st.button("Starte Decorator Demo", key="demo3"):
        result = complex_calculation()
        st.success(f"Ergebnis: {result}")

    # Demo 4: Verschiedene Styles
    st.header("4. 🎨 Verschiedene Design-Styles")

    style_options = {
        "Modern (Standard)": ProgressStyle.SHADCN_DEFAULT,
        "Minimal": ProgressStyle.SHADCN_MINIMAL,
        "Gradient": ProgressStyle.SHADCN_GRADIENT,
        "Animiert": ProgressStyle.SHADCN_ANIMATED,
        "Classic": ProgressStyle.SHADCN_MODERN
    }

    for style_name, style in style_options.items():
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button(f"Test {style_name}", key=f"demo4_{style_name}"):
                # Temporarily change style
                original_style = progress_manager.config.style
                progress_manager.config.style = style

                progress_bar = create_progress_bar(
                    f"Teste {style_name} Style...", st.container())

                for i in range(0, 101, 25):
                    progress_bar.update(i, f"Fortschritt: {i}%")
                    time.sleep(0.3)

                progress_bar.complete(f"{style_name} Demo abgeschlossen!")

                # Restore original style
                progress_manager.config.style = original_style
                time.sleep(1)

    # Demo 5: Error Handling
    st.header("5. ❌ Error Handling")
    if st.button("Simuliere Fehler", key="demo5"):
        progress_bar = create_progress_bar(
            "Verarbeite Daten...", st.container())

        try:
            for i in range(0, 80, 20):
                progress_bar.update(i, f"Schritt {i // 20 + 1}...")
                time.sleep(0.3)

            # Simuliere Fehler
            progress_bar.update(80, "Fehler aufgetreten!", error=True)
            time.sleep(1)
            raise Exception("Simulierter Fehler")

        except Exception as e:
            st.error(f"Fehler: {e}")

    # Demo 6: Nested Progress (ohne Context Manager für Simplizität)
    st.header("6. 🔗 Verschachtelte Progress Bars")
    if st.button("Starte verschachtelte Demo", key="demo6"):
        main_progress = create_progress_bar(
            "Hauptprozess läuft...", st.container())

        for i in range(3):
            main_progress.update((i + 1) * 33, f"Hauptschritt {i + 1}/3")

            # Sub-progress für jeden Hauptschritt
            sub_progress = create_progress_bar(
                f"Teilschritt {i + 1} Details...", st.container())

            for j in range(5):
                sub_progress.update((j + 1) * 20, f"Detail {j + 1}/5")
                time.sleep(0.2)

            sub_progress.complete(f"Teilschritt {i + 1} abgeschlossen!")
            time.sleep(0.3)

        main_progress.complete("Alle Hauptschritte abgeschlossen!")

    # Demo 7: Custom Colors (falls verfügbar)
    st.header("7. 🌈 Eigene Farben")

    col1, col2, col3 = st.columns(3)

    with col1:
        primary_color = st.color_picker("Primärfarbe", "#3b82f6")
    with col2:
        secondary_color = st.color_picker("Sekundärfarbe", "#10b981")
    with col3:
        background_color = st.color_picker("Hintergrund", "#f1f5f9")

    if st.button("Teste eigene Farben", key="demo7"):
        # Temporarily change colors
        original_config = progress_manager.config
        progress_manager.config.color_primary = primary_color
        progress_manager.config.color_secondary = secondary_color
        progress_manager.config.color_background = background_color

        progress_bar = create_progress_bar(
            "Teste eigene Farben...", st.container())

        for i in range(0, 101, 10):
            progress_bar.update(i, f"Custom Colors: {i}%")
            time.sleep(0.1)

        progress_bar.complete("Eigene Farben getestet!")

        # Restore original config
        progress_manager.config = original_config
        time.sleep(1)

    # Einstellungen anzeigen
    st.header("8. ⚙️ Aktuelle Einstellungen")

    with st.expander("Progress Manager Konfiguration"):
        config = progress_manager.config
        st.json({
            "style": config.style.name,
            "color_primary": config.color_primary,
            "color_secondary": config.color_secondary,
            "color_background": config.color_background,
            "show_percentage": config.show_percentage,
            "show_text": config.show_text,
            "height": config.height,
            "animation_speed": config.animation_speed
        })


if __name__ == "__main__":
    main()
