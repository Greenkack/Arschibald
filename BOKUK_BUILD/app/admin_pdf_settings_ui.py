"""
admin_pdf_settings_ui.py

Admin UI für PDF & Design Einstellungen
Zentrale Verwaltung für:
- PDF-Design-Einstellungen (Farben, Schriftarten, Layout)
- Diagramm-Farbkonfigurationen (Global & Individuell)
- UI-Theme-System
- PDF-Template-Verwaltung
- Layout-Optionen

Autor: Kiro AI
Datum: 2025-01-09
"""

import streamlit as st


def get_db_functions():
    """Get database load/save functions"""
    try:
        from database import load_admin_setting, save_admin_setting

        return load_admin_setting, save_admin_setting
    except ImportError:
        st.error("❌ Datenbankmodul nicht verfügbar")
        return None, None


def render_pdf_settings_ui():
    """
    Hauptfunktion für PDF & Design Einstellungen UI

    Zeigt Tab-Navigation für verschiedene Einstellungsbereiche:
    - PDF-Design
    - Diagramm-Farben
    - UI-Themes
    - PDF-Templates
    - Layout-Optionen
    """
    load_setting, save_setting = get_db_functions()

    if not load_setting or not save_setting:
        st.error(
            "❌ Datenbank-Funktionen nicht verfügbar. "
            "Einstellungen können nicht geladen werden."
        )
        return

    st.title("⚙️ PDF & Design Einstellungen")
    st.markdown("---")

    # Tab-Navigation für verschiedene Einstellungsbereiche
    tabs = st.tabs(
        [
            "🎨 PDF-Design",
            "📊 Diagramm-Farben",
            "🖼️ UI-Themes",
            "📄 PDF-Templates",
            "📐 Layout-Optionen",
            "💾 Import/Export",
            "📦 Versionierung",
        ]
    )

    # Tab 1: PDF-Design-Einstellungen
    with tabs[0]:
        render_pdf_design_settings(load_setting, save_setting)

    # Tab 2: Diagramm-Farbeinstellungen
    with tabs[1]:
        render_chart_color_settings(load_setting, save_setting)

    # Tab 3: UI-Theme-System
    with tabs[2]:
        render_ui_theme_settings(load_setting, save_setting)

    # Tab 4: PDF-Template-Verwaltung
    with tabs[3]:
        render_pdf_template_management(load_setting, save_setting)

    # Tab 5: Layout-Optionen
    with tabs[4]:
        render_layout_options(load_setting, save_setting)

    # Tab 6: Import/Export
    with tabs[5]:
        render_import_export(load_setting, save_setting)

    # Tab 7: Versionierung
    with tabs[6]:
        render_version_management(load_setting, save_setting)


def render_pdf_design_settings(load_setting, save_setting):
    """
    Rendert PDF-Design-Einstellungen

    Einstellungen für:
    - Primär- und Sekundärfarben
    - Schriftarten und -größen
    - Logo-Position
    - Footer-Format
    - Wasserzeichen
    """
    st.header("🎨 PDF-Design-Einstellungen")
    st.markdown("Passen Sie das Aussehen Ihrer PDF-Dokumente an.")

    # Load current settings
    pdf_design = load_setting("pdf_design_settings", {})

    # Default values
    defaults = {
        "primary_color": "#1E3A8A",
        "secondary_color": "#3B82F6",
        "font_family": "Helvetica",
        "font_size_h1": 18,
        "font_size_h2": 14,
        "font_size_body": 10,
        "font_size_small": 8,
        "logo_position": "left",
        "footer_format": "with_page_number",
        "custom_footer_text": "",
        "watermark_enabled": False,
        "watermark_text": "ENTWURF",
        "watermark_opacity": 0.1,
    }

    # Merge with defaults
    for key, value in defaults.items():
        if key not in pdf_design:
            pdf_design[key] = value

    # Create two columns for layout
    col_settings, col_preview = st.columns([2, 1])

    with col_settings:
        # Section 1: Farbauswahl (Task 9.1)
        st.subheader("🎨 Farbauswahl")

        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker(
                "Primärfarbe",
                value=pdf_design["primary_color"],
                help="Hauptfarbe für Überschriften und Akzente",
            )

        with col2:
            secondary_color = st.color_picker(
                "Sekundärfarbe",
                value=pdf_design["secondary_color"],
                help="Farbe für Tabellen und Hintergründe",
            )

        st.markdown("---")

        # Section 2: Schriftart-Einstellungen (Task 9.2)
        st.subheader("🔤 Schriftart-Einstellungen")

        font_family = st.selectbox(
            "Schriftart",
            options=["Helvetica", "Times-Roman", "Courier"],
            index=["Helvetica", "Times-Roman", "Courier"].index(
                pdf_design["font_family"]
            ),
            help="Schriftart für das gesamte PDF-Dokument",
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            font_size_h1 = st.number_input(
                "H1 Größe",
                min_value=12,
                max_value=24,
                value=pdf_design["font_size_h1"],
                step=1,
                help="Schriftgröße für Hauptüberschriften",
            )

        with col2:
            font_size_h2 = st.number_input(
                "H2 Größe",
                min_value=10,
                max_value=20,
                value=pdf_design["font_size_h2"],
                step=1,
                help="Schriftgröße für Unterüberschriften",
            )

        with col3:
            font_size_body = st.number_input(
                "Body Größe",
                min_value=8,
                max_value=14,
                value=pdf_design["font_size_body"],
                step=1,
                help="Schriftgröße für Fließtext",
            )

        with col4:
            font_size_small = st.number_input(
                "Small Größe",
                min_value=6,
                max_value=10,
                value=pdf_design["font_size_small"],
                step=1,
                help="Schriftgröße für Kleintext",
            )

        st.markdown("---")

        # Section 3: Logo & Layout-Einstellungen (Task 9.3)
        st.subheader("🖼️ Logo & Layout-Einstellungen")

        col1, col2 = st.columns(2)
        with col1:
            logo_position = st.selectbox(
                "Logo-Position",
                options=["left", "center", "right"],
                index=["left", "center", "right"].index(pdf_design["logo_position"]),
                help="Position des Logos im PDF-Header",
            )

        with col2:
            footer_format = st.selectbox(
                "Footer-Format",
                options=["with_page_number", "without_page_number", "custom"],
                format_func=lambda x: {
                    "with_page_number": "Mit Seitenzahl",
                    "without_page_number": "Ohne Seitenzahl",
                    "custom": "Benutzerdefiniert",
                }[x],
                index=["with_page_number", "without_page_number", "custom"].index(
                    pdf_design["footer_format"]
                ),
                help="Format des PDF-Footers",
            )

        if footer_format == "custom":
            custom_footer_text = st.text_input(
                "Benutzerdefinierter Footer-Text",
                value=pdf_design["custom_footer_text"],
                help="Text für benutzerdefinierten Footer",
            )
        else:
            custom_footer_text = pdf_design["custom_footer_text"]

        st.markdown("---")

        # Section 4: Wasserzeichen-Einstellungen (Task 9.4)
        st.subheader("💧 Wasserzeichen-Einstellungen")

        watermark_enabled = st.checkbox(
            "Wasserzeichen aktivieren",
            value=pdf_design["watermark_enabled"],
            help="Fügt ein Wasserzeichen zu allen PDF-Seiten hinzu",
        )

        if watermark_enabled:
            col1, col2 = st.columns(2)
            with col1:
                watermark_text = st.text_input(
                    "Wasserzeichen-Text",
                    value=pdf_design["watermark_text"],
                    help="Text des Wasserzeichens",
                )

            with col2:
                watermark_opacity = st.slider(
                    "Transparenz",
                    min_value=0.0,
                    max_value=1.0,
                    value=pdf_design["watermark_opacity"],
                    step=0.05,
                    help="Transparenz des Wasserzeichens (0 = unsichtbar, 1 = voll sichtbar)",
                )
        else:
            watermark_text = pdf_design["watermark_text"]
            watermark_opacity = pdf_design["watermark_opacity"]

        st.markdown("---")

        # Save button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Speichern", type="primary", use_container_width=True):
                new_settings = {
                    "primary_color": primary_color,
                    "secondary_color": secondary_color,
                    "font_family": font_family,
                    "font_size_h1": font_size_h1,
                    "font_size_h2": font_size_h2,
                    "font_size_body": font_size_body,
                    "font_size_small": font_size_small,
                    "logo_position": logo_position,
                    "footer_format": footer_format,
                    "custom_footer_text": custom_footer_text,
                    "watermark_enabled": watermark_enabled,
                    "watermark_text": watermark_text,
                    "watermark_opacity": watermark_opacity,
                }

                if save_setting("pdf_design_settings", new_settings):
                    _show_success_message("Einstellungen erfolgreich gespeichert!")
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Speichern der Einstellungen.")

        with col2:
            if st.button("🔄 Zurücksetzen", use_container_width=True):
                if save_setting("pdf_design_settings", defaults):
                    _show_success_message("Einstellungen auf Standard zurückgesetzt!")
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Zurücksetzen.")

    # Section 5: Live-Vorschau (Task 9.5)
    with col_preview:
        st.subheader("👁️ Live-Vorschau")

        # Create preview HTML
        preview_html = f"""
        <div style="
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="
                text-align: {logo_position};
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid {primary_color};
            ">
                <div style="
                    display: inline-block;
                    width: 60px;
                    height: 60px;
                    background-color: {primary_color};
                    border-radius: 50%;
                    line-height: 60px;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                ">LOGO</div>
            </div>
            
            <h1 style="
                color: {primary_color};
                font-family: {font_family}, sans-serif;
                font-size: {font_size_h1}pt;
                margin: 10px 0;
            ">Hauptüberschrift</h1>
            
            <h2 style="
                color: {secondary_color};
                font-family: {font_family}, sans-serif;
                font-size: {font_size_h2}pt;
                margin: 8px 0;
            ">Unterüberschrift</h2>
            
            <p style="
                color: #374151;
                font-family: {font_family}, sans-serif;
                font-size: {font_size_body}pt;
                line-height: 1.5;
                margin: 10px 0;
            ">
                Dies ist ein Beispieltext im Body-Format. 
                Er zeigt, wie der Fließtext in Ihrem PDF aussehen wird.
            </p>
            
            <div style="
                background-color: {secondary_color}20;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            ">
                <p style="
                    color: #374151;
                    font-family: {font_family}, sans-serif;
                    font-size: {font_size_body}pt;
                    margin: 0;
                ">Beispiel-Tabellenzelle mit Sekundärfarbe</p>
            </div>
            
            <p style="
                color: #6b7280;
                font-family: {font_family}, sans-serif;
                font-size: {font_size_small}pt;
                margin: 10px 0;
            ">Kleintext für Fußnoten und Details</p>
            
            {f'''
            <div style="
                position: relative;
                margin-top: 20px;
            ">
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 24pt;
                    color: rgba(0, 0, 0, {watermark_opacity});
                    font-weight: bold;
                    white-space: nowrap;
                ">{watermark_text}</div>
            </div>
            ''' if watermark_enabled else ''}

            <div style="
                margin-top: 20px;
                padding-top: 10px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-family: {font_family}, sans-serif;
                font-size: {font_size_small}pt;
            ">
                {
            'Seite 1 von 8' if footer_format == 'with_page_number'
            else custom_footer_text if footer_format == 'custom'
            else ''
        }
            </div>
        </div>
        """

        st.markdown(preview_html, unsafe_allow_html=True)

        st.markdown("---")

        # Settings summary
        with st.expander("📋 Einstellungsübersicht"):
            st.markdown(
                f"""
            **Farben:**
            - Primärfarbe: `{primary_color}`
            - Sekundärfarbe: `{secondary_color}`
            
            **Schriftart:**
            - Familie: {font_family}
            - H1: {font_size_h1}pt
            - H2: {font_size_h2}pt
            - Body: {font_size_body}pt
            - Small: {font_size_small}pt
            
            **Layout:**
            - Logo-Position: {logo_position}
            - Footer: {footer_format}
            
            **Wasserzeichen:**
            - Aktiviert: {'Ja' if watermark_enabled else 'Nein'}
            {f"- Text: {watermark_text}" if watermark_enabled else ""}
            {f"- Transparenz: {watermark_opacity:.0%}" if watermark_enabled else ""}
            """
            )


def render_chart_color_settings(load_setting, save_setting):
    """
    Rendert Diagramm-Farbeinstellungen

    Einstellungen für:
    - Globale Diagrammfarben
    - Farbpaletten-Bibliothek
    - Individuelle Diagramm-Konfiguration
    """
    st.header("📊 Diagramm-Farbeinstellungen")
    st.markdown(
        "Konfigurieren Sie die Farben für alle Diagramme " "und Visualisierungen."
    )

    # Load current settings
    visualization_settings = load_setting("visualization_settings", {})

    # Create sub-tabs for different chart color settings
    sub_tabs = st.tabs(
        ["🌐 Globale Farben", "🎨 Farbpaletten", "⚙️ Individuelle Konfiguration"]
    )

    # Sub-Tab 1: Globale Farbeinstellungen (Task 10.1)
    with sub_tabs[0]:
        render_global_chart_colors(visualization_settings, load_setting, save_setting)

    # Sub-Tab 2: Farbpaletten-Bibliothek (Task 10.2)
    with sub_tabs[1]:
        render_color_palette_library(visualization_settings, load_setting, save_setting)

    # Sub-Tab 3: Individuelle Diagramm-Konfiguration (Task 10.3)
    with sub_tabs[2]:
        render_individual_chart_config(
            visualization_settings, load_setting, save_setting
        )


def render_global_chart_colors(visualization_settings, load_setting, save_setting):
    """
    Rendert globale Diagramm-Farbeinstellungen (Task 10.1)

    Ermöglicht die Konfiguration von 6 globalen Farben für alle Diagramme
    """
    st.subheader("🌐 Globale Diagrammfarben")
    st.markdown("Diese Farben werden standardmäßig für alle Diagramme verwendet.")

    # Default global colors
    default_colors = [
        "#1E3A8A",  # Dark Blue
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
    ]

    # Get current global colors
    global_colors = visualization_settings.get("global_chart_colors", default_colors)

    # Ensure we have exactly 6 colors
    while len(global_colors) < 6:
        global_colors.append(default_colors[len(global_colors)])

    st.markdown("**Wählen Sie 6 Farben für Ihre Diagramme:**")

    # Create 3 rows with 2 color pickers each
    new_colors = []

    for row in range(3):
        col1, col2 = st.columns(2)

        with col1:
            idx = row * 2
            color = st.color_picker(
                f"Farbe {idx + 1}", value=global_colors[idx], key=f"global_color_{idx}"
            )
            new_colors.append(color)

        with col2:
            idx = row * 2 + 1
            color = st.color_picker(
                f"Farbe {idx + 1}", value=global_colors[idx], key=f"global_color_{idx}"
            )
            new_colors.append(color)

    st.markdown("---")

    # Preview section
    st.markdown("**Vorschau der Farbpalette:**")
    preview_html = '<div style="display: flex; gap: 10px; margin: 10px 0;">'
    for color in new_colors:
        preview_html += f"""
        <div style="
            width: 60px;
            height: 60px;
            background-color: {color};
            border-radius: 8px;
            border: 2px solid #e5e7eb;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        "></div>
        """
    preview_html += "</div>"
    st.markdown(preview_html, unsafe_allow_html=True)

    st.markdown("---")

    # Save buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            "💾 Speichern",
            type="primary",
            use_container_width=True,
            key="save_global_colors",
        ):
            visualization_settings["global_chart_colors"] = new_colors

            if save_setting("visualization_settings", visualization_settings):
                _show_success_message("Globale Farben erfolgreich gespeichert!")
                st.rerun()
            else:
                _show_error_message("Fehler beim Speichern.")

    with col2:
        if st.button(
            "🔄 Zurücksetzen", use_container_width=True, key="reset_global_colors"
        ):
            visualization_settings["global_chart_colors"] = default_colors

            if save_setting("visualization_settings", visualization_settings):
                _show_success_message("Farben auf Standard zurückgesetzt!")
                st.rerun()
            else:
                _show_error_message("Fehler beim Zurücksetzen.")


def render_color_palette_library(visualization_settings, load_setting, save_setting):
    """
    Rendert Farbpaletten-Bibliothek (Task 10.2)

    Zeigt vordefinierte Farbpaletten und ermöglicht deren Anwendung
    """
    st.subheader("🎨 Farbpaletten-Bibliothek")
    st.markdown(
        "Wählen Sie eine vordefinierte Palette oder " "erstellen Sie eine eigene."
    )

    # Define predefined palettes
    palettes = {
        "Corporate": {
            "name": "Corporate",
            "description": "Professionelle Blau-Grau-Töne",
            "colors": [
                "#1E3A8A",  # Dark Blue
                "#3B82F6",  # Blue
                "#60A5FA",  # Light Blue
                "#6B7280",  # Gray
                "#9CA3AF",  # Light Gray
                "#1F2937",  # Dark Gray
            ],
        },
        "Eco": {
            "name": "Eco",
            "description": "Nachhaltige Grün-Töne",
            "colors": [
                "#065F46",  # Dark Green
                "#10B981",  # Green
                "#34D399",  # Light Green
                "#6EE7B7",  # Mint
                "#A7F3D0",  # Light Mint
                "#D1FAE5",  # Very Light Green
            ],
        },
        "Energy": {
            "name": "Energy",
            "description": "Energiegeladene Orange-Gelb-Töne",
            "colors": [
                "#DC2626",  # Red
                "#F59E0B",  # Amber
                "#FBBF24",  # Yellow
                "#FCD34D",  # Light Yellow
                "#FDE68A",  # Very Light Yellow
                "#FEF3C7",  # Pale Yellow
            ],
        },
        "Accessible": {
            "name": "Accessible",
            "description": "Farbenblind-freundliche Palette",
            "colors": [
                "#0173B2",  # Blue
                "#DE8F05",  # Orange
                "#029E73",  # Green
                "#CC78BC",  # Pink
                "#CA9161",  # Brown
                "#949494",  # Gray
            ],
        },
    }

    # Display palettes
    for palette_key, palette in palettes.items():
        with st.expander(f"**{palette['name']}** - {palette['description']}"):
            # Show color swatches
            preview_html = '<div style="display: flex; gap: 10px; margin: 10px 0;">'
            for color in palette["colors"]:
                preview_html += f"""
                <div style="
                    width: 50px;
                    height: 50px;
                    background-color: {color};
                    border-radius: 6px;
                    border: 2px solid #e5e7eb;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                "></div>
                """
            preview_html += "</div>"
            st.markdown(preview_html, unsafe_allow_html=True)

            # Show color codes
            st.markdown("**Farbcodes:**")
            color_codes = " • ".join(palette["colors"])
            st.code(color_codes, language=None)

            # Apply button
            if st.button(
                "✓ Palette anwenden",
                key=f"apply_palette_{palette_key}",
                use_container_width=True,
            ):
                visualization_settings["global_chart_colors"] = palette["colors"]

                if save_setting("visualization_settings", visualization_settings):
                    _show_success_message(
                        f"Palette '{palette['name']}' erfolgreich angewendet!"
                    )
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Anwenden der Palette.")

    st.markdown("---")

    # Current palette info
    current_colors = visualization_settings.get("global_chart_colors", [])

    if current_colors:
        st.markdown("**Aktuell verwendete Palette:**")
        preview_html = '<div style="display: flex; gap: 10px; margin: 10px 0;">'
        for color in current_colors:
            preview_html += f"""
            <div style="
                width: 50px;
                height: 50px;
                background-color: {color};
                border-radius: 6px;
                border: 2px solid #e5e7eb;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            "></div>
            """
        preview_html += "</div>"
        st.markdown(preview_html, unsafe_allow_html=True)


def render_individual_chart_config(visualization_settings, load_setting, save_setting):
    """
    Rendert individuelle Diagramm-Konfiguration (Task 10.3)

    Ermöglicht die Konfiguration von Farben für einzelne Diagramme
    """
    st.subheader("⚙️ Individuelle Diagramm-Konfiguration")
    st.markdown(
        "Konfigurieren Sie Farben für einzelne Diagramme. "
        "Diese überschreiben die globalen Einstellungen."
    )

    # Chart categories and their charts
    chart_categories = {
        "Wirtschaftlichkeit": [
            ("cumulative_cashflow_chart", "Kumulierter Cashflow"),
            ("cost_projection_chart", "Stromkosten-Hochrechnung"),
            ("break_even_chart", "Break-Even-Analyse"),
            ("amortisation_chart", "Amortisationsdiagramm"),
            ("project_roi_matrix", "Projektrendite-Matrix"),
            ("roi_comparison", "ROI-Vergleich"),
        ],
        "Produktion & Verbrauch": [
            ("monthly_prod_cons_chart", "Monatliche Produktion vs. Verbrauch"),
            ("yearly_production_chart", "Jahresproduktion"),
            ("daily_production", "Tagesproduktion"),
            ("weekly_production", "Wochenproduktion"),
            ("prod_vs_cons", "Produktion vs. Verbrauch"),
        ],
        "Eigenverbrauch & Autarkie": [
            ("consumption_coverage_pie", "Verbrauchsdeckung"),
            ("pv_usage_pie", "PV-Nutzung"),
            ("storage_effect", "Speicherwirkung"),
            ("selfuse_stack", "Eigenverbrauch vs. Einspeisung"),
            ("selfuse_ratio", "Eigenverbrauchsgrad"),
        ],
        "Finanzielle Analyse": [
            ("feed_in_revenue", "Einspeisevergütung"),
            ("income_projection", "Einnahmenprognose"),
            ("tariff_cube", "Tarifvergleich (3D)"),
            ("tariff_comparison", "Tarifvergleich"),
            ("cost_growth", "Stromkostensteigerung"),
        ],
        "CO2 & Umwelt": [("co2_savings_value", "CO2-Ersparnis vs. Wert")],
        "Vergleiche & Szenarien": [
            ("scenario_comparison", "Szenarienvergleich"),
            ("investment_value", "Investitionsnutzwert"),
        ],
    }

    # Get individual chart settings
    individual_charts = visualization_settings.get("individual_chart_colors", {})

    # Category selection
    st.markdown("**1. Wählen Sie eine Kategorie:**")
    selected_category = st.selectbox(
        "Kategorie",
        options=list(chart_categories.keys()),
        key="chart_category_select",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Chart selection within category
    st.markdown("**2. Wählen Sie ein Diagramm:**")
    charts_in_category = chart_categories[selected_category]

    selected_chart_key = st.selectbox(
        "Diagramm",
        options=[chart[0] for chart in charts_in_category],
        format_func=lambda x: next(
            chart[1] for chart in charts_in_category if chart[0] == x
        ),
        key="chart_select",
        label_visibility="collapsed",
    )

    selected_chart_name = next(
        chart[1] for chart in charts_in_category if chart[0] == selected_chart_key
    )

    st.markdown("---")

    # Chart configuration
    st.markdown(f"**3. Konfigurieren Sie '{selected_chart_name}':**")

    # Get current settings for this chart
    chart_config = individual_charts.get(selected_chart_key, {})

    # Use global colors toggle
    use_global = st.checkbox(
        "Globale Farben verwenden",
        value=chart_config.get("use_global", True),
        key=f"use_global_{selected_chart_key}",
        help="Wenn aktiviert, werden die globalen Farben verwendet",
    )

    if not use_global:
        st.markdown("**Benutzerdefinierte Farben:**")

        # Get global colors as default
        global_colors = visualization_settings.get(
            "global_chart_colors",
            ["#1E3A8A", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"],
        )

        # Get custom colors or use global as default
        custom_colors = chart_config.get("custom_colors", global_colors[:3])

        # Ensure we have at least 3 colors
        while len(custom_colors) < 3:
            custom_colors.append(global_colors[len(custom_colors) % len(global_colors)])

        # Color pickers for custom colors
        new_custom_colors = []

        col1, col2, col3 = st.columns(3)

        with col1:
            color1 = st.color_picker(
                "Primärfarbe",
                value=custom_colors[0],
                key=f"custom_color_1_{selected_chart_key}",
            )
            new_custom_colors.append(color1)

        with col2:
            color2 = st.color_picker(
                "Sekundärfarbe",
                value=custom_colors[1],
                key=f"custom_color_2_{selected_chart_key}",
            )
            new_custom_colors.append(color2)

        with col3:
            color3 = st.color_picker(
                "Akzentfarbe",
                value=custom_colors[2],
                key=f"custom_color_3_{selected_chart_key}",
            )
            new_custom_colors.append(color3)

        # Preview
        st.markdown("**Vorschau:**")
        preview_html = '<div style="display: flex; gap: 10px; margin: 10px 0;">'
        for color in new_custom_colors:
            preview_html += f"""
            <div style="
                width: 60px;
                height: 60px;
                background-color: {color};
                border-radius: 8px;
                border: 2px solid #e5e7eb;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            "></div>
            """
        preview_html += "</div>"
        st.markdown(preview_html, unsafe_allow_html=True)

    st.markdown("---")

    # Save buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            "💾 Speichern",
            type="primary",
            use_container_width=True,
            key=f"save_chart_{selected_chart_key}",
        ):
            # Update chart config
            if use_global:
                chart_config = {"use_global": True}
            else:
                chart_config = {"use_global": False, "custom_colors": new_custom_colors}

            individual_charts[selected_chart_key] = chart_config
            visualization_settings["individual_chart_colors"] = individual_charts

            if save_setting("visualization_settings", visualization_settings):
                _show_success_message(
                    f"Einstellungen für '{selected_chart_name}' gespeichert!"
                )
                st.rerun()
            else:
                _show_error_message("Fehler beim Speichern.")

    with col2:
        if st.button(
            "🔄 Auf Global zurücksetzen",
            use_container_width=True,
            key=f"reset_chart_{selected_chart_key}",
        ):
            # Remove custom settings for this chart
            if selected_chart_key in individual_charts:
                del individual_charts[selected_chart_key]
                visualization_settings["individual_chart_colors"] = individual_charts

                if save_setting("visualization_settings", visualization_settings):
                    _show_success_message(
                        f"'{selected_chart_name}' auf globale Farben " "zurückgesetzt!"
                    )
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Zurücksetzen.")

    # Show configured charts summary
    st.markdown("---")

    if individual_charts:
        with st.expander(f"📋 Konfigurierte Diagramme ({len(individual_charts)})"):
            for chart_key, config in individual_charts.items():
                # Find chart name
                chart_name = chart_key
                for category, charts in chart_categories.items():
                    for chart in charts:
                        if chart[0] == chart_key:
                            chart_name = chart[1]
                            break

                if config.get("use_global", True):
                    st.markdown(f"- **{chart_name}**: Globale Farben")
                else:
                    colors = config.get("custom_colors", [])
                    color_preview = " ".join(
                        [
                            f'<span style="display:inline-block;width:20px;'
                            f"height:20px;background-color:{c};"
                            f"border-radius:3px;border:1px solid #ccc;"
                            f'margin:0 2px;"></span>'
                            for c in colors
                        ]
                    )
                    st.markdown(
                        f"- **{chart_name}**: Benutzerdefiniert " f"{color_preview}",
                        unsafe_allow_html=True,
                    )


def render_ui_theme_settings(load_setting, save_setting):
    """
    Rendert UI-Theme-Einstellungen (Task 11)

    Einstellungen für:
    - Theme-Auswahl (Task 11.1)
    - Theme-Vorschau (Task 11.2)
    - Theme-Editor (Task 11.3)
    """
    st.header("🖼️ UI-Theme-System")
    st.markdown(
        "Wählen Sie ein Theme für die Benutzeroberfläche "
        "oder erstellen Sie ein eigenes."
    )

    # Load current settings
    ui_theme = load_setting("ui_theme_settings", {})

    # Define predefined themes
    predefined_themes = {
        "light": {
            "name": "Light Theme",
            "description": "Helles Standard-Theme",
            "primary_color": "#1E3A8A",
            "secondary_color": "#3B82F6",
            "background_color": "#FFFFFF",
            "text_color": "#1F2937",
            "accent_color": "#10B981",
        },
        "dark": {
            "name": "Dark Theme",
            "description": "Dunkles Theme für reduzierte Augenbelastung",
            "primary_color": "#60A5FA",
            "secondary_color": "#3B82F6",
            "background_color": "#1F2937",
            "text_color": "#F9FAFB",
            "accent_color": "#34D399",
        },
        "corporate": {
            "name": "Corporate Theme",
            "description": "Professionelles Business-Theme",
            "primary_color": "#1E40AF",
            "secondary_color": "#6B7280",
            "background_color": "#F9FAFB",
            "text_color": "#111827",
            "accent_color": "#059669",
        },
        "high_contrast": {
            "name": "High Contrast Theme",
            "description": "Hoher Kontrast für bessere Barrierefreiheit",
            "primary_color": "#000000",
            "secondary_color": "#1F2937",
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "accent_color": "#DC2626",
        },
    }

    # Get current theme or default to light
    current_theme_key = ui_theme.get("active_theme", "light")
    current_theme = ui_theme.get("theme_config", predefined_themes["light"])

    # Create two columns for layout
    col_settings, col_preview = st.columns([2, 1])

    with col_settings:
        # Task 11.1: Theme-Auswahl
        st.subheader("🎨 Theme-Auswahl")

        # Theme dropdown
        selected_theme_key = st.selectbox(
            "Verfügbare Themes",
            options=list(predefined_themes.keys()) + ["custom"],
            format_func=lambda x: (
                predefined_themes[x]["name"] if x != "custom" else "Custom Theme"
            ),
            index=(
                list(predefined_themes.keys()).index(current_theme_key)
                if current_theme_key in predefined_themes
                else len(predefined_themes)
            ),
            help="Wählen Sie ein vordefiniertes Theme oder erstellen Sie ein eigenes",
        )

        # Show theme description
        if selected_theme_key != "custom":
            st.info(
                f"ℹ️ {
                    predefined_themes[selected_theme_key]['description']}"
            )

        # Theme aktivieren button
        if selected_theme_key != "custom":
            if st.button(
                "✓ Theme aktivieren",
                type="primary",
                use_container_width=True,
                key="activate_theme",
            ):
                new_theme_settings = {
                    "active_theme": selected_theme_key,
                    "theme_config": predefined_themes[selected_theme_key],
                }

                if save_setting("ui_theme_settings", new_theme_settings):
                    _show_success_message(
                        f"Theme '{
                            predefined_themes[selected_theme_key]['name']}' erfolgreich aktiviert!"
                    )
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Aktivieren des Themes.")

        st.markdown("---")

        # Task 11.3: Theme-Editor (nur für Custom Theme)
        if selected_theme_key == "custom":
            st.subheader("✏️ Theme-Editor")
            st.markdown("Erstellen Sie Ihr eigenes Theme mit individuellen Farben.")

            # Get custom theme or use current as base
            custom_theme = ui_theme.get("custom_theme", current_theme)

            # Color pickers for all theme colors
            st.markdown("**Farben konfigurieren:**")

            col1, col2 = st.columns(2)

            with col1:
                primary_color = st.color_picker(
                    "Primärfarbe",
                    value=custom_theme.get("primary_color", "#1E3A8A"),
                    help="Hauptfarbe für wichtige UI-Elemente",
                    key="theme_primary",
                )

                background_color = st.color_picker(
                    "Hintergrundfarbe",
                    value=custom_theme.get("background_color", "#FFFFFF"),
                    help="Hintergrundfarbe der Anwendung",
                    key="theme_background",
                )

                accent_color = st.color_picker(
                    "Akzentfarbe",
                    value=custom_theme.get("accent_color", "#10B981"),
                    help="Farbe für Hervorhebungen und Aktionen",
                    key="theme_accent",
                )

            with col2:
                secondary_color = st.color_picker(
                    "Sekundärfarbe",
                    value=custom_theme.get("secondary_color", "#3B82F6"),
                    help="Sekundäre Farbe für UI-Elemente",
                    key="theme_secondary",
                )

                text_color = st.color_picker(
                    "Textfarbe",
                    value=custom_theme.get("text_color", "#1F2937"),
                    help="Haupttextfarbe",
                    key="theme_text",
                )

            st.markdown("---")

            # Theme name input
            custom_theme_name = st.text_input(
                "Theme-Name",
                value=custom_theme.get("name", "Mein Custom Theme"),
                help="Geben Sie Ihrem Theme einen Namen",
            )

            # Save custom theme button
            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 Theme speichern",
                    type="primary",
                    use_container_width=True,
                    key="save_custom_theme",
                ):
                    new_custom_theme = {
                        "name": custom_theme_name,
                        "description": "Benutzerdefiniertes Theme",
                        "primary_color": primary_color,
                        "secondary_color": secondary_color,
                        "background_color": background_color,
                        "text_color": text_color,
                        "accent_color": accent_color,
                    }

                    new_theme_settings = {
                        "active_theme": "custom",
                        "theme_config": new_custom_theme,
                        "custom_theme": new_custom_theme,
                    }

                    if save_setting("ui_theme_settings", new_theme_settings):
                        _show_success_message(
                            f"Custom Theme '{custom_theme_name}' erfolgreich gespeichert und aktiviert!"
                        )
                        st.rerun()
                    else:
                        _show_error_message("Fehler beim Speichern des Themes.")

            with col2:
                if st.button(
                    "🔄 Zurücksetzen",
                    use_container_width=True,
                    key="reset_custom_theme",
                ):
                    # Reset to light theme
                    new_theme_settings = {
                        "active_theme": "light",
                        "theme_config": predefined_themes["light"],
                    }

                    if save_setting("ui_theme_settings", new_theme_settings):
                        _show_success_message("Theme auf Standard zurückgesetzt!")
                        st.rerun()
                    else:
                        _show_error_message("Fehler beim Zurücksetzen.")

    # Task 11.2: Theme-Vorschau
    with col_preview:
        st.subheader("👁️ Theme-Vorschau")

        # Get theme to preview
        if selected_theme_key == "custom":
            preview_theme = {
                "primary_color": (
                    primary_color
                    if "primary_color" in locals()
                    else current_theme.get("primary_color", "#1E3A8A")
                ),
                "secondary_color": (
                    secondary_color
                    if "secondary_color" in locals()
                    else current_theme.get("secondary_color", "#3B82F6")
                ),
                "background_color": (
                    background_color
                    if "background_color" in locals()
                    else current_theme.get("background_color", "#FFFFFF")
                ),
                "text_color": (
                    text_color
                    if "text_color" in locals()
                    else current_theme.get("text_color", "#1F2937")
                ),
                "accent_color": (
                    accent_color
                    if "accent_color" in locals()
                    else current_theme.get("accent_color", "#10B981")
                ),
            }
        else:
            preview_theme = predefined_themes[selected_theme_key]

        # Create HTML preview with theme colors
        preview_html = f"""
        <div style="
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            background-color: {preview_theme['background_color']};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-height: 400px;
        ">
            <!-- Header -->
            <div style="
                background-color: {preview_theme['primary_color']};
                color: white;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 15px;
                font-weight: bold;
                text-align: center;
            ">
                Header / Navigation
            </div>

            <!-- Main Content -->
            <div style="
                padding: 15px;
                margin-bottom: 15px;
            ">
                <h2 style="
                    color: {preview_theme['primary_color']};
                    margin: 10px 0;
                    font-size: 18pt;
                ">Hauptüberschrift</h2>

                <p style="
                    color: {preview_theme['text_color']};
                    line-height: 1.6;
                    margin: 10px 0;
                ">
                    Dies ist ein Beispieltext, der zeigt, wie der
                    Fließtext in diesem Theme aussieht. Die Textfarbe
                    sollte gut lesbar sein.
                </p>

                <!-- Secondary Element -->
                <div style="
                    background-color: {preview_theme['secondary_color']};
                    color: white;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 15px 0;
                ">
                    Sekundäres Element / Info-Box
                </div>

                <!-- Accent Button -->
                <button style="
                    background-color: {preview_theme['accent_color']};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    cursor: pointer;
                    margin: 10px 0;
                ">
                    Aktions-Button
                </button>

                <!-- Text Elements -->
                <div style="
                    margin-top: 15px;
                    padding: 10px;
                    border-left: 3px solid {preview_theme['accent_color']};
                    background-color: {preview_theme['secondary_color']}20;
                ">
                    <p style="
                        color: {preview_theme['text_color']};
                        margin: 0;
                        font-size: 10pt;
                    ">
                        Hervorgehobener Text mit Akzentfarbe
                    </p>
                </div>
            </div>

            <!-- Footer -->
            <div style="
                background-color: {preview_theme['secondary_color']}40;
                padding: 10px;
                border-radius: 6px;
                text-align: center;
                color: {preview_theme['text_color']};
                font-size: 9pt;
            ">
                Footer / Zusatzinformationen
            </div>
        </div>
        """

        st.markdown(preview_html, unsafe_allow_html=True)

        st.markdown("---")

        # Theme color summary
        with st.expander("🎨 Farbübersicht"):
            st.markdown(
                f"""
            **Primärfarbe:** `{preview_theme['primary_color']}`
            <div style="width: 100%; height: 30px; background-color: {preview_theme['primary_color']}; border-radius: 4px; margin: 5px 0;"></div>

            **Sekundärfarbe:** `{preview_theme['secondary_color']}`
            <div style="width: 100%; height: 30px; background-color: {preview_theme['secondary_color']}; border-radius: 4px; margin: 5px 0;"></div>

            **Hintergrundfarbe:** `{preview_theme['background_color']}`
            <div style="width: 100%; height: 30px; background-color: {preview_theme['background_color']}; border: 1px solid #ccc; border-radius: 4px; margin: 5px 0;"></div>

            **Textfarbe:** `{preview_theme['text_color']}`
            <div style="width: 100%; height: 30px; background-color: {preview_theme['text_color']}; border-radius: 4px; margin: 5px 0;"></div>

            **Akzentfarbe:** `{preview_theme['accent_color']}`
            <div style="width: 100%; height: 30px; background-color: {preview_theme['accent_color']}; border-radius: 4px; margin: 5px 0;"></div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Current active theme info
    st.markdown("### 📌 Aktuell aktives Theme")

    if current_theme_key in predefined_themes:
        theme_name = predefined_themes[current_theme_key]["name"]
    elif current_theme_key == "custom":
        theme_name = current_theme.get("name", "Custom Theme")
    else:
        theme_name = "Light Theme (Standard)"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Theme", theme_name)

    with col2:
        st.metric(
            "Typ",
            "Vordefiniert" if current_theme_key != "custom" else "Benutzerdefiniert",
        )

    with col3:
        # Color preview
        preview_colors_html = f"""
        <div style="display: flex; gap: 5px; margin-top: 10px;">
            <div style="width: 30px; height: 30px; background-color: {current_theme.get('primary_color', '#1E3A8A')}; border-radius: 4px;"></div>
            <div style="width: 30px; height: 30px; background-color: {current_theme.get('secondary_color', '#3B82F6')}; border-radius: 4px;"></div>
            <div style="width: 30px; height: 30px; background-color: {current_theme.get('accent_color', '#10B981')}; border-radius: 4px;"></div>
        </div>
        """
        st.markdown("**Farben:**")
        st.markdown(preview_colors_html, unsafe_allow_html=True)


def render_pdf_template_management(load_setting, save_setting):
    """
    Rendert PDF-Template-Verwaltung (Task 12)

    Ermöglicht:
    - Template-Auswahl und Aktivierung (Task 12.1)
    - Template-Details-Anzeige (Task 12.2)
    - Neues Template hinzufügen (Task 12.3)
    """
    st.header("📄 PDF-Template-Verwaltung")
    st.markdown(
        "Verwalten Sie verschiedene PDF-Templates für unterschiedliche "
        "Angebots-Designs."
    )

    # Load current templates
    pdf_templates = load_setting("pdf_templates", {})

    # Default templates structure
    if not pdf_templates:
        pdf_templates = {"templates": [], "active_template_id": None}

    # Ensure structure exists
    if "templates" not in pdf_templates:
        pdf_templates["templates"] = []
    if "active_template_id" not in pdf_templates:
        pdf_templates["active_template_id"] = None

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["📋 Template-Auswahl", "➕ Neues Template hinzufügen"])

    # Tab 1: Template-Auswahl (Task 12.1 & 12.2)
    with tab1:
        render_template_selection(pdf_templates, load_setting, save_setting)

    # Tab 2: Neues Template hinzufügen (Task 12.3)
    with tab2:
        render_add_new_template(pdf_templates, load_setting, save_setting)


def render_template_selection(pdf_templates, load_setting, save_setting):
    """
    Rendert Template-Auswahl und Details (Task 12.1 & 12.2)

    Zeigt:
    - Dropdown für verfügbare Templates
    - "Template aktivieren" Button
    - Template-Details (Name, Beschreibung, Dateipfade)
    """
    st.subheader("📋 Verfügbare Templates")

    templates = pdf_templates.get("templates", [])
    active_template_id = pdf_templates.get("active_template_id")

    if not templates:
        st.info(
            "ℹ️ Noch keine Templates vorhanden. "
            "Fügen Sie ein neues Template im Tab "
            "'Neues Template hinzufügen' hinzu."
        )
        return

    # Task 12.1: Template-Auswahl Dropdown
    st.markdown("**Wählen Sie ein Template:**")

    # Create template options for dropdown
    template_options = {template["id"]: template["name"] for template in templates}

    # Default selection
    default_index = 0
    if active_template_id and active_template_id in template_options:
        template_ids = list(template_options.keys())
        default_index = template_ids.index(active_template_id)

    selected_template_id = st.selectbox(
        "Template",
        options=list(template_options.keys()),
        format_func=lambda x: template_options[x],
        index=default_index,
        key="template_select",
        label_visibility="collapsed",
    )

    # Get selected template details
    selected_template = next(
        (t for t in templates if t["id"] == selected_template_id), None
    )

    if not selected_template:
        st.error("❌ Template nicht gefunden.")
        return

    st.markdown("---")

    # Task 12.2: Template-Details-Anzeige
    st.markdown("**Template-Details:**")

    # Show template information in a more structured way
    col_info, col_preview = st.columns([2, 1])

    with col_info:
        # Name with larger font
        st.markdown(f"### {selected_template.get('name', 'N/A')}")

        # Description
        description = selected_template.get("description", "Keine Beschreibung")
        st.markdown(f"**Beschreibung:** {description}")

        st.markdown("---")

        # Metadata in columns
        meta_col1, meta_col2 = st.columns(2)

        with meta_col1:
            # Template ID
            st.markdown(f"**ID:** `{selected_template.get('id', 'N/A')}`")

            # Status indicator
            is_active = selected_template_id == active_template_id
            status_color = "🟢" if is_active else "⚪"
            status_text = "Aktiv" if is_active else "Inaktiv"
            st.markdown(f"**Status:** {status_color} {status_text}")

        with meta_col2:
            # Creation date (if available)
            if "created_at" in selected_template:
                st.markdown(f"**Erstellt:** {selected_template['created_at']}")

            # Count configured pages
            configured_pages = sum(
                1 for i in range(1, 9) if selected_template.get(f"page_{i}_background")
            )
            st.markdown(f"**Konfigurierte Seiten:** {configured_pages}/8")

    with col_preview:
        # Task 12.2: Vorschau-Bild (Preview Image)
        st.markdown("**Vorschau:**")

        preview_image_path = selected_template.get("preview_image")

        if preview_image_path:
            import os

            if os.path.exists(preview_image_path):
                try:
                    st.image(
                        preview_image_path,
                        caption="Template-Vorschau",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.warning(f"⚠️ Vorschau konnte nicht geladen werden: {e}")
            else:
                st.info("ℹ️ Vorschaubild nicht gefunden")
        else:
            # Show placeholder preview
            placeholder_html = """
            <div style="
                width: 100%;
                aspect-ratio: 1/1.414;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 14px;
                text-align: center;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div>
                    <div style="font-size: 48px; margin-bottom: 10px;">📄</div>
                    <div>Keine Vorschau verfügbar</div>
                </div>
            </div>
            """
            st.markdown(placeholder_html, unsafe_allow_html=True)

    st.markdown("---")

    # Show file paths with enhanced display
    st.markdown("**Dateipfade:**")

    with st.expander("📁 Template-Dateien anzeigen", expanded=False):
        import os

        # Summary statistics
        bg_count = sum(
            1
            for i in range(1, 9)
            if selected_template.get(f"page_{i}_background")
            and os.path.exists(selected_template.get(f"page_{i}_background", ""))
        )
        coord_count = sum(
            1
            for i in range(1, 9)
            if selected_template.get(f"page_{i}_coords")
            and os.path.exists(selected_template.get(f"page_{i}_coords", ""))
        )

        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Hintergrund-PDFs", f"{bg_count}/8", delta=None)
        with col_stat2:
            st.metric("Koordinaten-Dateien", f"{coord_count}/8", delta=None)

        st.markdown("---")

        # Background PDFs with detailed status
        st.markdown("**Hintergrund-PDFs (Seite 1-8):**")

        for i in range(1, 9):
            page_key = f"page_{i}_background"
            page_path = selected_template.get(page_key, "")

            if not page_path:
                st.text(f"⚪ Seite {i}: Nicht konfiguriert")
            else:
                # Check if file exists
                file_exists = os.path.exists(page_path)

                if file_exists:
                    # Get file size
                    try:
                        file_size = os.path.getsize(page_path)
                        size_kb = file_size / 1024
                        status_icon = "✅"
                        status_text = f"({size_kb:.1f} KB)"
                    except BaseException:
                        status_icon = "✅"
                        status_text = ""
                else:
                    status_icon = "❌"
                    status_text = "(Datei nicht gefunden)"

                st.text(f"{status_icon} Seite {i}: {page_path} {status_text}")

        st.markdown("---")

        # Coordinate files with detailed status
        st.markdown("**Koordinaten-Dateien (YML):**")

        for i in range(1, 9):
            coord_key = f"page_{i}_coords"
            coord_path = selected_template.get(coord_key, "")

            if not coord_path:
                st.text(f"⚪ Seite {i}: Nicht konfiguriert")
            else:
                # Check if file exists
                file_exists = os.path.exists(coord_path)

                if file_exists:
                    # Get file size
                    try:
                        file_size = os.path.getsize(coord_path)
                        size_kb = file_size / 1024
                        status_icon = "✅"
                        status_text = f"({size_kb:.1f} KB)"
                    except BaseException:
                        status_icon = "✅"
                        status_text = ""
                else:
                    status_icon = "❌"
                    status_text = "(Datei nicht gefunden)"

                st.text(f"{status_icon} Seite {i}: {coord_path} {status_text}")

        st.markdown("---")

        # Validation summary
        st.markdown("**Validierung:**")

        total_files = bg_count + coord_count
        expected_files = 16  # 8 backgrounds + 8 coords

        if total_files == expected_files:
            st.success(f"✅ Alle Dateien vorhanden ({total_files}/{expected_files})")
        elif total_files > 0:
            st.warning(
                f"⚠️ Unvollständig: {total_files}/{expected_files} Dateien vorhanden"
            )
        else:
            st.error("❌ Keine Dateien konfiguriert")

    st.markdown("---")

    # Task 12.1: "Template aktivieren" Button
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # Only show activate button if not already active
        if not is_active:
            if st.button(
                "✓ Template aktivieren",
                type="primary",
                use_container_width=True,
                key="activate_template",
            ):
                pdf_templates["active_template_id"] = selected_template_id

                if save_setting("pdf_templates", pdf_templates):
                    _show_success_message(
                        f"Template '{selected_template['name']}' "
                        "erfolgreich aktiviert!"
                    )
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Aktivieren des Templates.")
        else:
            st.success("✓ Dieses Template ist aktiv")

    with col2:
        # Delete template button
        if st.button(
            "🗑️ Löschen",
            use_container_width=True,
            key="delete_template",
            help="Template löschen",
        ):
            # Confirm deletion
            if "confirm_delete" not in st.session_state:
                st.session_state.confirm_delete = False

            st.session_state.confirm_delete = True

    # Confirmation dialog for deletion
    if st.session_state.get("confirm_delete", False):
        st.warning(
            f"⚠️ Möchten Sie das Template '{selected_template['name']}' "
            "wirklich löschen?"
        )

        col_yes, col_no = st.columns(2)

        with col_yes:
            if st.button("Ja, löschen", type="primary", key="confirm_yes"):
                # Remove template from list
                pdf_templates["templates"] = [
                    t for t in templates if t["id"] != selected_template_id
                ]

                # If deleted template was active, clear active_template_id
                if active_template_id == selected_template_id:
                    pdf_templates["active_template_id"] = None

                if save_setting("pdf_templates", pdf_templates):
                    st.session_state.confirm_delete = False
                    _show_success_message("Template erfolgreich gelöscht!")
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Löschen des Templates.")

        with col_no:
            if st.button("Abbrechen", key="confirm_no"):
                st.session_state.confirm_delete = False
                st.rerun()


def render_add_new_template(pdf_templates, load_setting, save_setting):
    """
    Rendert "Neues Template hinzufügen" Formular (Task 12.3)

    Ermöglicht:
    - Text Inputs für Template-Informationen
    - Text Inputs für Dateipfade
    - "Template hinzufügen" Button
    """
    st.subheader("➕ Neues Template hinzufügen")
    st.markdown(
        "Erstellen Sie ein neues PDF-Template mit benutzerdefinierten "
        "Hintergründen und Koordinaten."
    )

    # Template information section
    st.markdown("**1. Template-Informationen:**")

    col1, col2 = st.columns(2)

    with col1:
        template_name = st.text_input(
            "Template-Name *",
            placeholder="z.B. Standard-Template",
            help="Eindeutiger Name für das Template",
            key="new_template_name",
        )

    with col2:
        template_id = st.text_input(
            "Template-ID *",
            placeholder="z.B. standard_template",
            help="Eindeutige ID (nur Kleinbuchstaben, Zahlen und Unterstriche)",
            key="new_template_id",
        )

    template_description = st.text_area(
        "Beschreibung",
        placeholder="Beschreiben Sie das Template...",
        help="Optional: Beschreibung des Templates",
        key="new_template_description",
    )

    # Preview image path (Task 12.2 - Requirement 23.2)
    preview_image_path = st.text_input(
        "Vorschau-Bild (optional)",
        placeholder="z.B. pdf_templates_static/preview_standard.png",
        help="Pfad zu einem Vorschaubild des Templates (PNG, JPG)",
        key="new_template_preview",
    )

    st.markdown("---")

    # File paths section
    st.markdown("**2. Hintergrund-PDFs (Seite 1-8):**")
    st.caption("Geben Sie die Dateipfade zu den PDF-Hintergründen für jede Seite an.")

    background_paths = {}

    # Create 2 columns for better layout
    for row in range(4):
        col1, col2 = st.columns(2)

        with col1:
            page_num = row * 2 + 1
            background_paths[f"page_{page_num}_background"] = st.text_input(
                f"Seite {page_num}",
                placeholder=f"pdf_templates_static/seite{page_num}.pdf",
                key=f"bg_page_{page_num}",
            )

        with col2:
            page_num = row * 2 + 2
            background_paths[f"page_{page_num}_background"] = st.text_input(
                f"Seite {page_num}",
                placeholder=f"pdf_templates_static/seite{page_num}.pdf",
                key=f"bg_page_{page_num}",
            )

    st.markdown("---")

    # Coordinate files section
    st.markdown("**3. Koordinaten-Dateien (YML, Seite 1-8):**")
    st.caption(
        "Geben Sie die Dateipfade zu den YML-Koordinatendateien für jede Seite an."
    )

    coord_paths = {}

    # Create 2 columns for better layout
    for row in range(4):
        col1, col2 = st.columns(2)

        with col1:
            page_num = row * 2 + 1
            coord_paths[f"page_{page_num}_coords"] = st.text_input(
                f"Seite {page_num}",
                placeholder=f"coords/seite{page_num}.yml",
                key=f"coord_page_{page_num}",
            )

        with col2:
            page_num = row * 2 + 2
            coord_paths[f"page_{page_num}_coords"] = st.text_input(
                f"Seite {page_num}",
                placeholder=f"coords/seite{page_num}.yml",
                key=f"coord_page_{page_num}",
            )

    st.markdown("---")

    # Validation and save section
    st.markdown("**4. Template hinzufügen:**")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            "➕ Template hinzufügen",
            type="primary",
            use_container_width=True,
            key="add_template_button",
        ):
            # Validate inputs
            errors = []

            if not template_name:
                errors.append("Template-Name ist erforderlich")

            if not template_id:
                errors.append("Template-ID ist erforderlich")

            # Check if ID already exists
            existing_ids = [t["id"] for t in pdf_templates.get("templates", [])]
            if template_id in existing_ids:
                errors.append(f"Template-ID '{template_id}' existiert bereits")

            # Validate ID format (only lowercase, numbers, underscores)
            import re

            if template_id and not re.match(r"^[a-z0-9_]+$", template_id):
                errors.append(
                    "Template-ID darf nur Kleinbuchstaben, "
                    "Zahlen und Unterstriche enthalten"
                )

            # Check if at least one background path is provided
            has_background = any(path for path in background_paths.values() if path)
            if not has_background:
                errors.append("Mindestens ein Hintergrund-PDF muss angegeben werden")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create new template
                import datetime

                new_template = {
                    "id": template_id,
                    "name": template_name,
                    "description": template_description or "Keine Beschreibung",
                    "preview_image": preview_image_path or "",
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    **background_paths,
                    **coord_paths,
                }

                # Add to templates list
                if "templates" not in pdf_templates:
                    pdf_templates["templates"] = []

                pdf_templates["templates"].append(new_template)

                # Save to database
                if save_setting("pdf_templates", pdf_templates):
                    _show_success_message(
                        f"Template '{template_name}' erfolgreich hinzugefügt!"
                    )

                    # Clear form by rerunning
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Speichern des Templates.")

    with col2:
        if st.button(
            "🔄 Formular zurücksetzen", use_container_width=True, key="reset_form"
        ):
            st.rerun()

    # Help section
    with st.expander("ℹ️ Hilfe zu Template-Dateipfaden"):
        st.markdown(
            """
        **Hintergrund-PDFs:**
        - Pfade relativ zum Projekt-Root angeben
        - Beispiel: `pdf_templates_static/seite1.pdf`
        - PDFs sollten im A4-Format sein

        **Koordinaten-Dateien:**
        - YML-Dateien mit Textpositionen
        - Beispiel: `coords/seite1.yml`
        - Format: `key: [x, y, width, height]`

        **Tipps:**
        - Verwenden Sie konsistente Pfadstrukturen
        - Stellen Sie sicher, dass alle Dateien existieren
        - Testen Sie das Template nach dem Hinzufügen
        """
        )


def render_layout_options(load_setting, save_setting):
    """
    Rendert Layout-Optionen-Verwaltung (Task 13)

    Funktionen für:
    - Layout-Liste (Task 13.1)
    - Layout-Konfiguration (Task 13.2)
    """
    st.header("📐 Layout-Optionen")
    st.markdown("Verwalten Sie verfügbare PDF-Layouts und deren Einstellungen.")

    # Load current settings
    layout_options = load_setting("pdf_layout_options", {})

    # Define available layouts with their properties
    available_layouts = {
        "standard": {
            "name": "Standard-Layout",
            "description": "8-Seiten PDF mit allen Standardinformationen",
            "icon": "📄",
            "pages": 8,
            "features": [
                "Deckblatt mit Projektübersicht",
                "Wirtschaftlichkeitsanalyse",
                "Technische Details",
                "Finanzierungsoptionen",
                "Umweltbeitrag",
                "Diagramme und Visualisierungen",
                "Produktübersicht",
                "Kontaktinformationen",
            ],
        },
        "extended": {
            "name": "Erweiterte Layouts",
            "description": "Standard-PDF mit optionalen Zusatzseiten",
            "icon": "📑",
            "pages": "8+",
            "features": [
                "Alle Standard-Seiten",
                "Detaillierte Finanzierungsberechnungen",
                "Produktdatenblätter",
                "Firmendokumente",
                "Zusätzliche Diagramme",
                "Individuelle Anpassungen",
            ],
        },
        "compact": {
            "name": "Kompakt-Layout",
            "description": "Reduzierte Version mit Kerninfos (4-6 Seiten)",
            "icon": "📋",
            "pages": "4-6",
            "features": [
                "Deckblatt",
                "Wirtschaftlichkeitsübersicht",
                "Technische Zusammenfassung",
                "Kontaktinformationen",
            ],
        },
        "custom": {
            "name": "Custom-Layout",
            "description": "Frei konfigurierbares Layout",
            "icon": "⚙️",
            "pages": "variabel",
            "features": [
                "Individuelle Seitenauswahl",
                "Benutzerdefinierte Reihenfolge",
                "Flexible Inhalte",
                "Anpassbare Struktur",
            ],
        },
    }

    # Initialize layout options if not exists
    if not layout_options:
        layout_options = {
            "layouts": {
                "standard": {"enabled": True, "is_default": True},
                "extended": {"enabled": True, "is_default": False},
                "compact": {"enabled": False, "is_default": False},
                "custom": {"enabled": False, "is_default": False},
            }
        }

    # Ensure all layouts exist in settings
    if "layouts" not in layout_options:
        layout_options["layouts"] = {}

    for layout_key in available_layouts:
        if layout_key not in layout_options["layouts"]:
            layout_options["layouts"][layout_key] = {
                "enabled": layout_key in ["standard", "extended"],
                "is_default": layout_key == "standard",
            }

    st.markdown("---")

    # Task 13.1: Layout-Liste
    st.subheader("📋 Verfügbare Layouts")
    st.markdown(
        "Aktivieren oder deaktivieren Sie Layouts und "
        "legen Sie ein Standard-Layout fest."
    )

    # Track changes
    changes_made = False
    updated_layouts = layout_options["layouts"].copy()

    # Display each layout in an expander (Task 13.1)
    for layout_key, layout_info in available_layouts.items():
        current_config = updated_layouts[layout_key]

        with st.expander(
            f"{layout_info['icon']} **{layout_info['name']}** "
            f"({'✓ Aktiviert' if current_config['enabled'] else '✗ Deaktiviert'}"
            f"{' • ⭐ Standard' if current_config['is_default'] else ''})",
            expanded=current_config["is_default"],
        ):
            # Layout description
            st.markdown(f"**Beschreibung:** {layout_info['description']}")
            st.markdown(f"**Seitenanzahl:** {layout_info['pages']}")

            # Features list
            st.markdown("**Enthaltene Features:**")
            for feature in layout_info["features"]:
                st.markdown(f"- {feature}")

            st.markdown("---")

            # Task 13.2: Layout-Konfiguration
            st.markdown("**Konfiguration:**")

            col1, col2 = st.columns(2)

            with col1:
                # Checkbox "Aktiviert"
                enabled = st.checkbox(
                    "Aktiviert",
                    value=current_config["enabled"],
                    key=f"layout_enabled_{layout_key}",
                    help=f"Layout '{
                        layout_info['name']}' aktivieren/deaktivieren",
                )

                if enabled != current_config["enabled"]:
                    updated_layouts[layout_key]["enabled"] = enabled
                    changes_made = True

            with col2:
                # Checkbox "Als Standard"
                # Only allow if layout is enabled
                is_default = st.checkbox(
                    "Als Standard",
                    value=current_config["is_default"],
                    key=f"layout_default_{layout_key}",
                    disabled=not enabled,
                    help=(
                        f"Layout '{layout_info['name']}' als Standard festlegen"
                        if enabled
                        else "Layout muss aktiviert sein, um als Standard festgelegt zu werden"
                    ),
                )

                if is_default != current_config["is_default"]:
                    # If setting as default, unset all others
                    if is_default:
                        for key in updated_layouts.keys():
                            updated_layouts[key]["is_default"] = False
                        updated_layouts[layout_key]["is_default"] = True
                    else:
                        updated_layouts[layout_key]["is_default"] = False

                    changes_made = True

            # Individual save button for this layout
            if st.button(
                "💾 Speichern",
                key=f"save_layout_{layout_key}",
                use_container_width=True,
                type="primary" if changes_made else "secondary",
            ):
                # Validate: At least one layout must be enabled
                if not any(cfg["enabled"] for cfg in updated_layouts.values()):
                    _show_error_message("Mindestens ein Layout muss aktiviert sein!")
                else:
                    # Validate: Exactly one layout must be default
                    default_count = sum(
                        1 for cfg in updated_layouts.values() if cfg["is_default"]
                    )

                    if default_count == 0:
                        _show_error_message(
                            "Ein Layout muss als Standard festgelegt sein!"
                        )
                    elif default_count > 1:
                        _show_error_message(
                            "Nur ein Layout kann als Standard festgelegt sein!"
                        )
                    else:
                        # Save settings
                        layout_options["layouts"] = updated_layouts

                        if save_setting("pdf_layout_options", layout_options):
                            _show_success_message(
                                f"Layout '{layout_info['name']}' "
                                "erfolgreich gespeichert!"
                            )
                            st.rerun()
                        else:
                            _show_error_message(
                                "Fehler beim Speichern der Einstellungen."
                            )

    st.markdown("---")

    # Global save button
    st.subheader("💾 Alle Änderungen speichern")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            "💾 Alle speichern",
            type="primary",
            use_container_width=True,
            key="save_all_layouts",
        ):
            # Validate: At least one layout must be enabled
            if not any(cfg["enabled"] for cfg in updated_layouts.values()):
                _show_error_message("Mindestens ein Layout muss aktiviert sein!")
            else:
                # Validate: Exactly one layout must be default
                default_count = sum(
                    1 for cfg in updated_layouts.values() if cfg["is_default"]
                )

                if default_count == 0:
                    _show_error_message("Ein Layout muss als Standard festgelegt sein!")
                elif default_count > 1:
                    _show_error_message(
                        "Nur ein Layout kann als Standard festgelegt sein!"
                    )
                else:
                    # Save settings
                    layout_options["layouts"] = updated_layouts

                    if save_setting("pdf_layout_options", layout_options):
                        _show_success_message(
                            "Alle Layout-Einstellungen erfolgreich gespeichert!"
                        )
                        st.rerun()
                    else:
                        _show_error_message("Fehler beim Speichern der Einstellungen.")

    with col2:
        if st.button(
            "🔄 Zurücksetzen", use_container_width=True, key="reset_all_layouts"
        ):
            # Reset to defaults
            default_layout_options = {
                "layouts": {
                    "standard": {"enabled": True, "is_default": True},
                    "extended": {"enabled": True, "is_default": False},
                    "compact": {"enabled": False, "is_default": False},
                    "custom": {"enabled": False, "is_default": False},
                }
            }

            if save_setting("pdf_layout_options", default_layout_options):
                _show_success_message(
                    "Layout-Einstellungen auf Standard zurückgesetzt!"
                )
                st.rerun()
            else:
                _show_error_message("Fehler beim Zurücksetzen.")

    st.markdown("---")

    # Summary section
    st.subheader("📊 Übersicht")

    # Count enabled layouts
    enabled_count = sum(1 for cfg in updated_layouts.values() if cfg["enabled"])

    # Find default layout
    default_layout = next(
        (key for key, cfg in updated_layouts.items() if cfg["is_default"]), None
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Aktivierte Layouts", enabled_count, delta=None)

    with col2:
        if default_layout:
            default_name = available_layouts[default_layout]["name"]
            st.metric("Standard-Layout", default_name, delta=None)
        else:
            st.metric("Standard-Layout", "Nicht festgelegt", delta=None)

    with col3:
        st.metric("Verfügbare Layouts", len(available_layouts), delta=None)

    # Detailed status table
    with st.expander("📋 Detaillierte Status-Übersicht"):
        st.markdown("**Status aller Layouts:**")

        for layout_key, layout_info in available_layouts.items():
            config = updated_layouts[layout_key]

            status_icon = "✅" if config["enabled"] else "❌"
            default_icon = "⭐" if config["is_default"] else ""

            st.markdown(f"{status_icon} **{layout_info['name']}** {default_icon}")
            st.markdown(
                f"  - Status: {'Aktiviert' if config['enabled'] else 'Deaktiviert'}"
            )
            st.markdown(f"  - Standard: {'Ja' if config['is_default'] else 'Nein'}")
            st.markdown(f"  - Seiten: {layout_info['pages']}")
            st.markdown("")


def render_import_export(load_setting, save_setting):
    """
    Rendert Import/Export-Funktionen für Design-Konfigurationen (Task 14)

    Ermöglicht:
    - Export aller Design-Einstellungen als JSON
    - Import von Design-Konfigurationen
    - Validierung importierter Daten
    """
    st.header("💾 Import/Export von Design-Konfigurationen")
    st.markdown(
        "Exportieren und importieren Sie alle Design-Einstellungen " "als JSON-Datei."
    )

    # Create two columns for Export and Import
    col_export, col_import = st.columns(2)

    # Export Section (Task 14.1)
    with col_export:
        st.subheader("📤 Export")
        st.markdown(
            "Exportieren Sie alle aktuellen Design-Einstellungen " "in eine JSON-Datei."
        )

        # Show what will be exported
        with st.expander("📋 Was wird exportiert?"):
            st.markdown(
                """
            Die folgenden Einstellungen werden exportiert:
            - **PDF-Design-Einstellungen**: Farben, Schriftarten, Layout
            - **Diagramm-Farbkonfigurationen**: Globale und individuelle Farben
            - **UI-Theme-Einstellungen**: Aktives Theme und Custom-Themes
            - **PDF-Template-Einstellungen**: Aktives Template
            - **Layout-Optionen**: Aktivierte Layouts
            - **Custom-Farbpaletten**: Benutzerdefinierte Paletten
            """
            )

        st.markdown("---")

        # Export button
        if st.button(
            "📥 Konfiguration exportieren",
            type="primary",
            use_container_width=True,
            key="export_config_btn",
        ):
            config_data = _collect_all_design_settings(load_setting)

            if config_data:
                # Create JSON file
                import json
                from datetime import datetime

                # Add metadata
                config_data["_metadata"] = {
                    "export_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "PDF & Design Konfiguration Export",
                }

                json_str = json.dumps(config_data, indent=2, ensure_ascii=False)

                # Create download button
                st.download_button(
                    label="💾 JSON-Datei herunterladen",
                    data=json_str,
                    file_name=f"design_config_{
                        datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_config_btn",
                )

                _show_success_message(
                    "Konfiguration erfolgreich exportiert! "
                    "Klicken Sie auf den Download-Button."
                )

                # Show preview
                with st.expander("👁️ Vorschau der exportierten Daten"):
                    st.json(config_data)
            else:
                _show_error_message("Fehler beim Sammeln der Konfigurationsdaten.")

    # Import Section (Task 14.2)
    with col_import:
        st.subheader("📥 Import")
        st.markdown("Importieren Sie Design-Einstellungen aus einer JSON-Datei.")

        # File upload
        uploaded_file = st.file_uploader(
            "JSON-Datei auswählen",
            type=["json"],
            help="Wählen Sie eine zuvor exportierte Konfigurationsdatei",
            key="import_config_file",
        )

        if uploaded_file is not None:
            try:
                import json

                # Read and parse JSON
                json_str = uploaded_file.read().decode("utf-8")
                imported_config = json.loads(json_str)

                # Validate configuration
                is_valid, validation_errors = _validate_imported_config(imported_config)

                if is_valid:
                    st.success("✅ Konfiguration erfolgreich geladen und validiert!")

                    # Show metadata if available
                    if "_metadata" in imported_config:
                        metadata = imported_config["_metadata"]
                        with st.expander("ℹ️ Datei-Informationen"):
                            st.markdown(
                                f"""
                            - **Export-Datum**: {metadata.get('export_date', 'Unbekannt')}
                            - **Version**: {metadata.get('version', 'Unbekannt')}
                            - **Beschreibung**: {metadata.get('description', 'Keine')}
                            """
                            )

                    # Show what will be imported
                    with st.expander("📋 Was wird importiert?"):
                        settings_count = len(
                            [k for k in imported_config.keys() if not k.startswith("_")]
                        )
                        st.markdown(
                            f"**{settings_count} Einstellungsbereiche gefunden:**"
                        )

                        for key in imported_config.keys():
                            if not key.startswith("_"):
                                friendly_name = _get_setting_friendly_name(key)
                                st.markdown(f"- ✓ {friendly_name}")

                    # Preview imported data
                    with st.expander("👁️ Vorschau der importierten Daten"):
                        # Remove metadata for preview
                        preview_data = {
                            k: v
                            for k, v in imported_config.items()
                            if not k.startswith("_")
                        }
                        st.json(preview_data)

                    st.markdown("---")

                    # Warning message
                    st.warning(
                        "⚠️ **Achtung**: Der Import überschreibt alle "
                        "aktuellen Einstellungen!"
                    )

                    # Confirmation checkbox
                    confirm_import = st.checkbox(
                        "Ich bestätige, dass ich alle aktuellen Einstellungen "
                        "überschreiben möchte",
                        key="confirm_import_checkbox",
                    )

                    # Import button
                    if st.button(
                        "✓ Konfiguration importieren",
                        type="primary",
                        disabled=not confirm_import,
                        use_container_width=True,
                        key="import_config_btn",
                    ):
                        success = _import_design_settings(imported_config, save_setting)

                        if success:
                            _show_success_message(
                                "Konfiguration erfolgreich importiert! "
                                "Die Seite wird neu geladen..."
                            )
                            st.rerun()
                        else:
                            _show_error_message(
                                "Fehler beim Importieren der Konfiguration."
                            )

                else:
                    st.error("❌ Ungültige Konfigurationsdatei!")

                    with st.expander("🔍 Validierungsfehler"):
                        for error in validation_errors:
                            st.markdown(f"- {error}")

            except json.JSONDecodeError as e:
                st.error(f"❌ Fehler beim Parsen der JSON-Datei: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unerwarteter Fehler: {str(e)}")

        else:
            st.info(
                "ℹ️ Wählen Sie eine JSON-Datei aus, um die "
                "Konfiguration zu importieren."
            )

    st.markdown("---")

    # Additional information
    with st.expander("ℹ️ Hilfe & Informationen"):
        st.markdown(
            """
        ### Import/Export-Funktionen

        **Export:**
        - Exportiert alle Design-Einstellungen in eine JSON-Datei
        - Enthält Metadaten wie Export-Datum und Version
        - Kann als Backup oder zum Teilen verwendet werden

        **Import:**
        - Importiert Design-Einstellungen aus einer JSON-Datei
        - Validiert die Daten vor dem Import
        - Überschreibt alle aktuellen Einstellungen
        - Erfordert Bestätigung vor dem Import

        **Verwendungszwecke:**
        - Backup von Einstellungen erstellen
        - Einstellungen zwischen Installationen teilen
        - Verschiedene Design-Varianten testen
        - Schnelles Zurücksetzen auf bekannte Konfiguration

        **Hinweise:**
        - Exportierte Dateien sind im JSON-Format
        - Dateien können mit einem Texteditor bearbeitet werden
        - Ungültige Daten werden beim Import abgelehnt
        - Ein Backup vor dem Import wird empfohlen
        """
        )


def _collect_all_design_settings(load_setting) -> dict:
    """
    Sammelt alle Design-Einstellungen für den Export (Task 14.1)

    Returns:
        Dictionary mit allen Design-Einstellungen
    """
    try:
        config_data = {}

        # PDF-Design-Einstellungen
        pdf_design = load_setting("pdf_design_settings", {})
        if pdf_design:
            config_data["pdf_design_settings"] = pdf_design

        # Diagramm-Farbkonfigurationen
        visualization_settings = load_setting("visualization_settings", {})
        if visualization_settings:
            config_data["visualization_settings"] = visualization_settings

        # UI-Theme-Einstellungen
        ui_theme = load_setting("ui_theme_settings", {})
        if ui_theme:
            config_data["ui_theme_settings"] = ui_theme

        # PDF-Template-Einstellungen
        pdf_templates = load_setting("pdf_templates", {})
        if pdf_templates:
            config_data["pdf_templates"] = pdf_templates

        # Layout-Optionen
        layout_options = load_setting("pdf_layout_options", {})
        if layout_options:
            config_data["pdf_layout_options"] = layout_options

        # Custom-Farbpaletten (falls vorhanden)
        custom_palettes = load_setting("custom_color_palettes", {})
        if custom_palettes:
            config_data["custom_color_palettes"] = custom_palettes

        return config_data

    except Exception as e:
        print(f"Error collecting design settings: {e}")
        return {}


def _validate_imported_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validiert importierte Konfigurationsdaten (Task 14.2)

    Args:
        config: Importierte Konfigurationsdaten

    Returns:
        Tuple (is_valid, errors)
    """
    errors = []

    # Check if config is a dictionary
    if not isinstance(config, dict):
        errors.append("Konfiguration muss ein JSON-Objekt sein")
        return False, errors

    # Check if config has at least one setting
    valid_keys = [
        "pdf_design_settings",
        "visualization_settings",
        "ui_theme_settings",
        "pdf_templates",
        "pdf_layout_options",
        "custom_color_palettes",
    ]

    has_valid_key = any(key in config for key in valid_keys)
    if not has_valid_key:
        errors.append(
            "Keine gültigen Einstellungen gefunden. "
            "Erwartete Keys: " + ", ".join(valid_keys)
        )
        return False, errors

    # Validate pdf_design_settings
    if "pdf_design_settings" in config:
        pdf_design = config["pdf_design_settings"]
        if not isinstance(pdf_design, dict):
            errors.append("pdf_design_settings muss ein Objekt sein")
        else:
            # Check for required color fields
            if "primary_color" in pdf_design:
                if not isinstance(pdf_design["primary_color"], str):
                    errors.append("primary_color muss ein String sein")
            if "secondary_color" in pdf_design:
                if not isinstance(pdf_design["secondary_color"], str):
                    errors.append("secondary_color muss ein String sein")

    # Validate visualization_settings
    if "visualization_settings" in config:
        vis_settings = config["visualization_settings"]
        if not isinstance(vis_settings, dict):
            errors.append("visualization_settings muss ein Objekt sein")
        else:
            # Check global_chart_colors
            if "global_chart_colors" in vis_settings:
                colors = vis_settings["global_chart_colors"]
                if not isinstance(colors, list):
                    errors.append("global_chart_colors muss eine Liste sein")
                elif len(colors) < 1:
                    errors.append(
                        "global_chart_colors muss mindestens eine Farbe enthalten"
                    )

    # Validate ui_theme_settings
    if "ui_theme_settings" in config:
        theme_settings = config["ui_theme_settings"]
        if not isinstance(theme_settings, dict):
            errors.append("ui_theme_settings muss ein Objekt sein")

    # Validate pdf_templates
    if "pdf_templates" in config:
        templates = config["pdf_templates"]
        if not isinstance(templates, dict):
            errors.append("pdf_templates muss ein Objekt sein")

    # Validate pdf_layout_options
    if "pdf_layout_options" in config:
        layout_opts = config["pdf_layout_options"]
        if not isinstance(layout_opts, dict):
            errors.append("pdf_layout_options muss ein Objekt sein")

    # Return validation result
    is_valid = len(errors) == 0
    return is_valid, errors


def _import_design_settings(config: dict, save_setting) -> bool:
    """
    Importiert Design-Einstellungen (Task 14.2)

    Args:
        config: Validierte Konfigurationsdaten
        save_setting: Funktion zum Speichern von Einstellungen

    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        # Import each setting type
        success_count = 0
        total_count = 0

        # PDF-Design-Einstellungen
        if "pdf_design_settings" in config:
            total_count += 1
            if save_setting("pdf_design_settings", config["pdf_design_settings"]):
                success_count += 1

        # Diagramm-Farbkonfigurationen
        if "visualization_settings" in config:
            total_count += 1
            if save_setting("visualization_settings", config["visualization_settings"]):
                success_count += 1

        # UI-Theme-Einstellungen
        if "ui_theme_settings" in config:
            total_count += 1
            if save_setting("ui_theme_settings", config["ui_theme_settings"]):
                success_count += 1

        # PDF-Template-Einstellungen
        if "pdf_templates" in config:
            total_count += 1
            if save_setting("pdf_templates", config["pdf_templates"]):
                success_count += 1

        # Layout-Optionen
        if "pdf_layout_options" in config:
            total_count += 1
            if save_setting("pdf_layout_options", config["pdf_layout_options"]):
                success_count += 1

        # Custom-Farbpaletten
        if "custom_color_palettes" in config:
            total_count += 1
            if save_setting("custom_color_palettes", config["custom_color_palettes"]):
                success_count += 1

        # Return success if all settings were saved
        return success_count == total_count

    except Exception as e:
        print(f"Error importing design settings: {e}")
        return False


def render_version_management(load_setting, save_setting):
    """
    Rendert Versionsverwaltung für Design-Konfigurationen (Task 15)

    Ermöglicht:
    - Speichern von Versionen (Task 15.1)
    - Laden von Versionen (Task 15.2)
    - Löschen von Versionen (Task 15.3)
    """
    st.header("📦 Versionsverwaltung")
    st.markdown(
        "Speichern und verwalten Sie verschiedene Versionen "
        "Ihrer Design-Konfigurationen."
    )

    # Load existing versions
    versions = load_setting("design_config_versions", {})

    # Create default version if none exists
    if not versions:
        versions = {}
        save_setting("design_config_versions", versions)

    st.markdown("---")

    # Section 1: Version speichern (Task 15.1)
    st.subheader("💾 Neue Version speichern")
    st.markdown("Erstellen Sie einen Snapshot aller aktuellen Design-Einstellungen.")

    col1, col2 = st.columns([3, 1])

    with col1:
        version_name = st.text_input(
            "Versionsname",
            placeholder="z.B. Corporate Design v1.0",
            help="Geben Sie einen eindeutigen Namen für diese Version ein",
            key="new_version_name",
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button(
            "💾 Version speichern",
            type="primary",
            use_container_width=True,
            disabled=not version_name or version_name.strip() == "",
            key="save_version_btn",
        ):
            if version_name.strip() in versions:
                st.warning(
                    f"⚠️ Version '{version_name}' existiert bereits. "
                    "Bitte wählen Sie einen anderen Namen."
                )
            else:
                # Create snapshot of all settings
                snapshot = _create_settings_snapshot(load_setting)

                # Add metadata
                import datetime

                snapshot["_metadata"] = {
                    "name": version_name.strip(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "description": "",
                }

                # Save version
                versions[version_name.strip()] = snapshot

                if save_setting("design_config_versions", versions):
                    _show_success_message(
                        f"Version '{version_name}' erfolgreich gespeichert!"
                    )
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Speichern der Version.")

    # Optional description
    if version_name and version_name.strip():
        version_description = st.text_area(
            "Beschreibung (optional)",
            placeholder="Beschreiben Sie die Änderungen in dieser Version...",
            help="Optionale Beschreibung für diese Version",
            key="version_description",
        )

    st.markdown("---")

    # Section 2: Gespeicherte Versionen (Task 15.2 & 15.3)
    st.subheader("📚 Gespeicherte Versionen")

    if not versions:
        st.info("ℹ️ Noch keine Versionen gespeichert.")
    else:
        st.markdown(f"**{len(versions)} Version(en) verfügbar:**")

        # Display versions in a table-like format
        for version_name, version_data in versions.items():
            with st.expander(f"📦 {version_name}", expanded=False):
                # Get metadata
                metadata = version_data.get("_metadata", {})
                created_at = metadata.get("created_at", "Unbekannt")
                description = metadata.get("description", "Keine Beschreibung")

                # Format date
                try:
                    import datetime

                    dt = datetime.datetime.fromisoformat(created_at)
                    created_at_formatted = dt.strftime("%d.%m.%Y %H:%M")
                except BaseException:
                    created_at_formatted = created_at

                # Display metadata
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Erstellt am:** {created_at_formatted}")
                    if description and description != "Keine Beschreibung":
                        st.markdown(f"**Beschreibung:** {description}")

                    # Show what's included
                    st.markdown("**Enthaltene Einstellungen:**")
                    included_settings = []
                    for key in [
                        "pdf_design_settings",
                        "visualization_settings",
                        "ui_theme_settings",
                        "pdf_templates",
                        "pdf_layout_options",
                    ]:
                        if key in version_data:
                            included_settings.append(
                                f"✓ {_get_setting_friendly_name(key)}"
                            )

                    if included_settings:
                        for setting in included_settings:
                            st.markdown(f"- {setting}")
                    else:
                        st.markdown("- Keine Einstellungen")

                with col2:
                    # Load button (Task 15.2)
                    if st.button(
                        "📥 Version laden",
                        use_container_width=True,
                        key=f"load_version_{version_name}",
                        help="Stellt alle Einstellungen dieser Version wieder her",
                    ):
                        # Show confirmation dialog
                        if "confirm_load_version" not in st.session_state:
                            st.session_state.confirm_load_version = version_name
                            st.rerun()

                    # Delete button (Task 15.3)
                    if st.button(
                        "🗑️ Löschen",
                        use_container_width=True,
                        key=f"delete_version_{version_name}",
                        help="Löscht diese Version permanent",
                    ):
                        # Show confirmation dialog
                        if "confirm_delete_version" not in st.session_state:
                            st.session_state.confirm_delete_version = version_name
                            st.rerun()

    # Confirmation dialog for loading version (Task 15.2)
    if "confirm_load_version" in st.session_state:
        version_to_load = st.session_state.confirm_load_version

        st.markdown("---")
        st.warning(
            f"⚠️ **Bestätigung erforderlich**\n\n"
            f"Möchten Sie wirklich die Version '{version_to_load}' laden?\n\n"
            f"**Alle aktuellen Einstellungen werden überschrieben!**"
        )

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button(
                "✓ Ja, laden",
                type="primary",
                use_container_width=True,
                key="confirm_load_yes",
            ):
                # Load version
                if _load_version(version_to_load, versions, save_setting):
                    _show_success_message(
                        f"Version '{version_to_load}' erfolgreich geladen!"
                    )
                    del st.session_state.confirm_load_version
                    st.rerun()
                else:
                    _show_error_message("Fehler beim Laden der Version.")
                    del st.session_state.confirm_load_version

        with col2:
            if st.button(
                "✗ Abbrechen", use_container_width=True, key="confirm_load_no"
            ):
                del st.session_state.confirm_load_version
                st.rerun()

    # Confirmation dialog for deleting version (Task 15.3)
    if "confirm_delete_version" in st.session_state:
        version_to_delete = st.session_state.confirm_delete_version

        st.markdown("---")
        st.error(
            f"⚠️ **Bestätigung erforderlich**\n\n"
            f"Möchten Sie wirklich die Version '{version_to_delete}' löschen?\n\n"
            f"**Diese Aktion kann nicht rückgängig gemacht werden!**"
        )

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button(
                "✓ Ja, löschen",
                type="primary",
                use_container_width=True,
                key="confirm_delete_yes",
            ):
                # Delete version
                if version_to_delete in versions:
                    del versions[version_to_delete]

                    if save_setting("design_config_versions", versions):
                        _show_success_message(
                            f"Version '{version_to_delete}' erfolgreich gelöscht!"
                        )
                        del st.session_state.confirm_delete_version
                        st.rerun()
                    else:
                        _show_error_message("Fehler beim Löschen der Version.")
                        del st.session_state.confirm_delete_version
                else:
                    _show_error_message("Version nicht gefunden.")
                    del st.session_state.confirm_delete_version

        with col2:
            if st.button(
                "✗ Abbrechen", use_container_width=True, key="confirm_delete_no"
            ):
                del st.session_state.confirm_delete_version
                st.rerun()

    st.markdown("---")

    # Info section
    with st.expander("ℹ️ Hilfe zur Versionsverwaltung"):
        st.markdown(
            """
        ### Wie funktioniert die Versionsverwaltung?

        **Version speichern:**
        - Erstellt einen Snapshot aller aktuellen Design-Einstellungen
        - Geben Sie einen eindeutigen Namen ein (z.B. "Corporate Design v1.0")
        - Optional können Sie eine Beschreibung hinzufügen

        **Version laden:**
        - Stellt alle Einstellungen einer gespeicherten Version wieder her
        - **Achtung:** Alle aktuellen Einstellungen werden überschrieben
        - Eine Bestätigung ist erforderlich

        **Version löschen:**
        - Löscht eine gespeicherte Version permanent
        - Diese Aktion kann nicht rückgängig gemacht werden
        - Eine Bestätigung ist erforderlich

        ### Was wird gespeichert?

        Eine Version enthält:
        - PDF-Design-Einstellungen (Farben, Schriftarten, Layout)
        - Diagramm-Farbkonfigurationen (Global & Individuell)
        - UI-Theme-Einstellungen
        - PDF-Template-Einstellungen
        - Layout-Optionen

        ### Best Practices

        - Speichern Sie regelmäßig Versionen vor größeren Änderungen
        - Verwenden Sie aussagekräftige Namen (z.B. mit Versionsnummer)
        - Fügen Sie Beschreibungen hinzu, um Änderungen zu dokumentieren
        - Behalten Sie wichtige Versionen als Backup
        """
        )


def _create_settings_snapshot(load_setting) -> dict:
    """
    Erstellt einen Snapshot aller Design-Einstellungen (Task 15.1)

    Args:
        load_setting: Funktion zum Laden von Einstellungen

    Returns:
        Dictionary mit allen Einstellungen
    """
    snapshot = {}

    # List of settings to include in snapshot
    setting_keys = [
        "pdf_design_settings",
        "visualization_settings",
        "ui_theme_settings",
        "pdf_templates",
        "pdf_layout_options",
        "custom_color_palettes",
    ]

    # Load each setting
    for key in setting_keys:
        setting_value = load_setting(key, None)
        if setting_value is not None:
            snapshot[key] = setting_value

    return snapshot


def _load_version(version_name: str, versions: dict, save_setting) -> bool:
    """
    Lädt eine gespeicherte Version (Task 15.2)

    Args:
        version_name: Name der zu ladenden Version
        versions: Dictionary mit allen Versionen
        save_setting: Funktion zum Speichern von Einstellungen

    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    if version_name not in versions:
        return False

    version_data = versions[version_name]

    try:
        # Restore each setting
        success_count = 0
        total_count = 0

        for key in [
            "pdf_design_settings",
            "visualization_settings",
            "ui_theme_settings",
            "pdf_templates",
            "pdf_layout_options",
            "custom_color_palettes",
        ]:
            if key in version_data and key != "_metadata":
                total_count += 1
                if save_setting(key, version_data[key]):
                    success_count += 1

        # Return success if all settings were restored
        return success_count == total_count

    except Exception as e:
        print(f"Error loading version: {e}")
        return False


def _get_setting_friendly_name(key: str) -> str:
    """
    Gibt einen benutzerfreundlichen Namen für einen Einstellungs-Key zurück

    Args:
        key: Einstellungs-Key

    Returns:
        Benutzerfreundlicher Name
    """
    friendly_names = {
        "pdf_design_settings": "PDF-Design-Einstellungen",
        "visualization_settings": "Diagramm-Farbkonfigurationen",
        "ui_theme_settings": "UI-Theme-Einstellungen",
        "pdf_templates": "PDF-Template-Einstellungen",
        "pdf_layout_options": "Layout-Optionen",
        "custom_color_palettes": "Custom-Farbpaletten",
    }

    return friendly_names.get(key, key)


# Helper function for future use
def _show_success_message(message: str):
    """Shows a success message"""
    st.success(f"✅ {message}")


def _show_error_message(message: str):
    """Shows an error message"""
    st.error(f"❌ {message}")


def _show_info_message(message: str):
    """Shows an info message"""
    st.info(f"ℹ️ {message}")


# Main entry point for testing
if __name__ == "__main__":
    st.set_page_config(
        page_title="PDF & Design Einstellungen", page_icon="⚙️", layout="wide"
    )
    render_pdf_settings_ui()
