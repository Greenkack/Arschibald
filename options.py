# options.py
# Modul für den Optionen Tab (E)


import json
from typing import Any

import streamlit as st

from emoji_toggle import initialize_emoji_support, set_show_emojis
from theming.pdf_styles import AVAILABLE_THEMES

# Importiere benötigte Funktionen/Daten (falls Optionen darauf zugreifen)
try:
    # Beispiel: Wenn Optionen Admin Settings speichert/lädt
    from database import load_admin_setting, save_admin_setting
    options_dependencies_available = True
except ImportError as e:
    # KEIN st.error hier - das würde die Seite blockieren!
    # Error wird nur geloggt, nicht angezeigt
    print(f"WARNING: Benötigte Module für Optionen konnten nicht geladen werden: {e}")
    options_dependencies_available = True
    # Definiere Dummy Funktionen, falls Import fehlschlägt
    def load_admin_setting(key, default=None): 
        print(f"DUMMY load_admin_setting called: {key} -> {default}")
        return default
    def save_admin_setting(key, value): 
        print(f"DUMMY save_admin_setting called: {key} = {value}")
        return False  # Gibt False zurück um Fehler anzuzeigen


def convert_to_bool(value):
    """Konvertiert verschiedene Datentypen zu Boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    if isinstance(value, (int, float)):
        return bool(value)
    return bool(value)


def display_options_ui():
    """
    DEPRECATED: Diese Funktion wurde durch render_options() ersetzt.
    Wird nur noch für Rückwärtskompatibilität beibehalten.
    """
    # Diese Funktion ist jetzt leer, da alle Inhalte in render_options() verschoben wurden
    pass


# KORREKTUR: render_options Funktion mit korrekter Signatur, die **kwargs
# akzeptiert
# KORREKTUR: **kwargs hinzugefügt
def render_options(texts: dict[str, str], **kwargs):
    """
    Rendert den Optionen Tab (E) der Streamlit Anwendung.
    Ermöglicht die Konfiguration von App-Einstellungen.

    Args:
        texts: Dictionary mit den lokalisierten Texten.
        **kwargs: Zusätzliche Keyword-Argumente, z.B. 'module_name' von gui.py.
    """
    # Emoji-Support initialisieren
    initialize_emoji_support()

    module_name = kwargs.get(
        'module_name', texts.get(
            "menu_item_options", "Optionen"))

    # Warnung anzeigen, wenn Datenbank nicht verfügbar ist
    if not options_dependencies_available:
        st.warning("""
        ⚠️ **Eingeschränkter Modus**
        
        Die Datenbank-Verbindung konnte nicht hergestellt werden.
        Einstellungen können angezeigt, aber nicht dauerhaft gespeichert werden.
        
        **Mögliche Ursachen:**
        - Datenbank-Modul nicht geladen
        - Fehlende Berechtigungen
        - Datenbankdatei nicht gefunden
        """)

    # === HEADER MIT MODERNER GESTALTUNG ===
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px; padding: 25px; margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <h2 style="color: white; margin: 0; font-weight: 600;">
            ⚙️ Globale Einstellungen
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
            Konfigurieren Sie die Anwendung nach Ihren Bedürfnissen
        </p>
    </div>
    """, unsafe_allow_html=True)

    # === WICHTIGSTE EINSTELLUNGEN DIREKT SICHTBAR (OHNE EXPANDER) ===
    
    # DEBUG: Zeige an, dass die Funktion aufgerufen wird
    print("=" * 80)
    print("DEBUG: render_options() wurde aufgerufen")
    print(f"  options_dependencies_available: {options_dependencies_available}")
    print(f"  module_name: {module_name}")
    print(f"  AVAILABLE_THEMES: {list(AVAILABLE_THEMES.keys())}")
    print("=" * 80)
    
    # === 1. PV-GIS INTEGRATION (KRITISCH) ===
    # PV-Gis Section mit Expander
    with st.expander("🌍 PV-GIS INTEGRATION & PRODUKTIONSWERTE", expanded=False):
        st.info("PV-Gis liefert präzise Ertragsdaten basierend auf geografischen und meteorologischen Daten der EU-Kommission.")

        # Aktuelle PV-Gis Einstellung laden - KORRIGIERT: Boolean handling
        pvgis_db_value = load_admin_setting('pvgis_enabled', 'true')
        
        # Intelligente Konvertierung
        if isinstance(pvgis_db_value, bool):
            current_pvgis_enabled = pvgis_db_value
        elif isinstance(pvgis_db_value, str):
            current_pvgis_enabled = pvgis_db_value.lower() in ('true', '1', 'yes')
        else:
            current_pvgis_enabled = True  # Default fallback

        # Session State Check - verhindert, dass sich Werte zurücksetzen
        session_key = 'pvgis_enabled_checkbox'
        if session_key not in st.session_state:
            st.session_state[session_key] = current_pvgis_enabled

        col1, col2 = st.columns(2)

        with col1:
            # PV-Gis aktivieren/deaktivieren
            pvgis_enabled = st.checkbox(
                "🌍 PV-Gis Integration & Produktionswerte aktivieren",
                value=st.session_state[session_key],
                key=session_key,
                help="Wenn aktiviert, werden Ertragsdaten von PV-Gis abgerufen. API-Zugriff auf EU-Server erforderlich!"
            )
            
            # ✅ Session State wird automatisch durch key= Parameter aktualisiert
            # NICHT MEHR NÖTIG: st.session_state[session_key] = pvgis_enabled

            # System Loss Einstellung
            current_system_loss_raw = load_admin_setting(
                'pvgis_system_loss_default_percent', 14.0)
            system_loss = st.slider(
                "📉 Standard Systemverluste (%)",
                min_value=5.0,
                max_value=25.0,
                value=float(current_system_loss_raw),
                step=0.5,
                help="Systemverluste durch Wechselrichter, Verkabelung, Verschattung etc.")

        with col2:
            # API Timeout Einstellung
            current_timeout = load_admin_setting(
                'pvgis_api_timeout_seconds', 25)
            api_timeout = st.number_input(
                "⏱️ API Timeout (Sekunden)",
                min_value=10,
                max_value=60,
                value=int(current_timeout),
                help="Maximale Wartezeit für PV-Gis API-Anfragen"
            )

            # Fallback-Spezifischer Ertrag
            current_fallback_yield = load_admin_setting(
                'default_specific_yield_kwh_kwp', 950.0)
            fallback_yield = st.number_input(
                "☀️ Spezifischer Ertrag (kWh/kWp/a)",
                min_value=600.0,
                max_value=1500.0,
                value=float(current_fallback_yield),
                step=10.0,
                help="Wird verwendet, wenn PV-Gis nicht verfügbar ist"
            )

        # Speichern-Button für PV-Gis Einstellungen
        # Speichern-Button für PV-Gis Einstellungen
        if st.button("💾 PV-Gis Einstellungen speichern", type="primary", key="save_pvgis"):
            # Alle PV-Gis Einstellungen speichern
            success_count = 0
            total_count = 4

            # ✅ Session State wird automatisch durch key= Parameter aktualisiert
            # Der aktuelle Wert ist bereits in st.session_state[session_key] gespeichert

            # Speichere als Boolean direkt (kein String mehr!)
            if save_admin_setting('pvgis_enabled', pvgis_enabled):
                success_count += 1
            if save_admin_setting(
                'pvgis_system_loss_default_percent',
                    system_loss):
                success_count += 1
            if save_admin_setting('pvgis_api_timeout_seconds', api_timeout):
                success_count += 1
            if save_admin_setting(
                'default_specific_yield_kwh_kwp',
                    fallback_yield):
                success_count += 1

            if success_count == total_count:
                st.success("✅ PV-Gis Einstellungen erfolgreich gespeichert!")
                st.session_state['pvgis_settings_saved'] = True
                # Setze Flag damit Berechnungen die neuen Werte verwenden
                st.session_state['settings_updated'] = True
                # Force rerun für sofortige Aktualisierung
                import time
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(f"❌ Fehler beim Speichern ({success_count}/{total_count} erfolgreich)")

        # Status-Information
        col_status1, col_status2 = st.columns(2)

        with col_status1:
            if pvgis_enabled:
                st.success("✅ PV-Gis Integration ist **AKTIVIERT**")
                st.info("📊 Präzise Ertragsdaten werden von EU-Servern abgerufen")
            else:
                st.warning("⚠️ PV-Gis Integration ist **DEAKTIVIERT**")
                st.info("📝 Manuell eingetragene Werte werden für Berechnungen verwendet")

        with col_status2:
            # Debug-Informationen nur im Debug-Modus anzeigen
            if st.session_state.get('app_debug_mode_enabled', True):
                st.markdown("**Debug-Info:**")
                pvgis_db_raw = load_admin_setting('pvgis_enabled', 'NICHT_GEFUNDEN')
                pvgis_session = st.session_state.get('pvgis_enabled_checkbox', 'NICHT_GESETZT')
                st.code(f"""
Datenbank-Wert: {pvgis_db_raw}
Session State: {pvgis_session}
Aktueller Wert: {pvgis_enabled}
Typ DB: {type(pvgis_db_raw).__name__}
Typ Session: {type(pvgis_session).__name__}
            """.strip())
            else:
                # Kompakte Status-Anzeige
                st.markdown("**System-Status:**")
                if pvgis_enabled:
                    st.success("✅ API-Verbindung aktiv")
                    st.info(f"⏱️ Timeout: {api_timeout}s")
                else:
                    st.warning("⚠️ API-Verbindung deaktiviert")
                    st.info(f"📊 Fallback: {fallback_yield} kWh/kWp/a")

        # Automatische Anzeige bei Änderungen
        if 'pvgis_settings_saved' in st.session_state and st.session_state['pvgis_settings_saved']:
            st.info("ℹ️ Einstellungen wurden gespeichert. Die Änderungen sind ab sofort aktiv!")
            # Flag zurücksetzen
            del st.session_state['pvgis_settings_saved']

    st.markdown("---")

    # === 2. PDF DESIGN & LAYOUT (WICHTIG) ===
    st.markdown("### 📄 PDF Design & Layout")
    
    # NEU: Auswahl des PDF-Themes
    theme_names = list(AVAILABLE_THEMES.keys())

    # Setze den Index auf das aktuell ausgewählte Theme oder das erste in
    # der Liste
    current_theme_name = st.session_state.get(
        "pdf_theme_name", theme_names[0])
    current_index = theme_names.index(
        current_theme_name) if current_theme_name in theme_names else 0

    selected_theme = st.selectbox(
        "Wählen Sie eine Design Vorlage für Ihre PDF-Angebote:",
        options=theme_names,
        index=current_index,
        key="pdf_theme_selector"
    )

    # Speichere die Auswahl im Session State für den PDF-Generator
    if selected_theme:
        st.session_state["pdf_theme_name"] = selected_theme
        st.success(f"✅ PDF-Theme '{selected_theme}' ausgewählt")

    st.markdown("---")

    # === 3. EMOJI DARSTELLUNG (WICHTIG) ===
    st.markdown("### 😀 Emoji Darstellung")

    default_show_emojis = convert_to_bool(
        load_admin_setting('ui_show_emojis', True))
    current_show_emojis = st.session_state.get(
        'show_emojis', default_show_emojis)

    show_emojis = st.checkbox(
        "Emojis in der gesamten App anzeigen",
        value=current_show_emojis,
        key='show_emojis_global',
        help="Aktiviert/deaktiviert Emojis in der gesamten Anwendung"
    )

    if show_emojis != current_show_emojis:
        set_show_emojis(show_emojis)

        if options_dependencies_available:
            if save_admin_setting('ui_show_emojis', show_emojis):
                st.success(
                    " Emoji-Einstellung gespeichert!" if show_emojis else "Emoji-Einstellung deaktiviert!")
            else:
                st.warning(
                    "Emoji-Einstellung konnte nicht gespeichert werden. Bitte erneut versuchen.")
        else:
            st.info(
                "Emoji-Einstellung geändert (wird nicht dauerhaft gespeichert – Datenbank-Modul fehlt).")

    st.markdown("---")

    # === ERWEITERTE EINSTELLUNGEN IN EXPANDERN ===
    st.markdown("### 🔧 Erweiterte Einstellungen")
    st.info("💡 Klicken Sie auf die Bereiche, um weitere Optionen anzuzeigen")

    # === PV-Gis INTEGRATION EINSTELLUNGEN ===
    with st.expander("🌍 Erweiterte PV-Gis Einstellungen", expanded=False):
        st.markdown("**Zusätzliche PV-Gis Konfiguration**")
        st.info("Hier können Sie weitere technische Parameter für die PV-Gis Integration einstellen.")
        
        # Platzhalter für zukünftige erweiterte Optionen
        st.markdown("*Weitere Optionen folgen in zukünftigen Updates*")

    # === LADEBALKEN DESIGN ===
    with st.expander("🎨 Ladebalken Design", expanded=False):
        try:
            from components.progress_settings import (
                render_progress_settings,
                render_quick_themes,
            )
            render_progress_settings()
            st.markdown("---")
            render_quick_themes()
        except ImportError as e:
            st.error(f"Progress Settings konnten nicht geladen werden: {e}")

    # ===  UI/UX EXPERIENCE EINSTELLUNGEN ===
    with st.expander("🎨 UI/UX EXPERIENCE", expanded=False):
        st.markdown("**Personalisierung der Benutzeroberfläche**")

        col1, col2 = st.columns(2)

        with col1:
            # Dark Mode Toggle mit Session State
            session_key_dark = 'ui_dark_mode_checkbox'
            if session_key_dark not in st.session_state:
                st.session_state[session_key_dark] = convert_to_bool(
                    load_admin_setting('ui_dark_mode_enabled', True))
            
            dark_mode = st.checkbox(
                " Dark Mode aktivieren",
                value=st.session_state[session_key_dark],
                key=session_key_dark,
                help="Dunkles Design für eine entspannte Arbeitsatmosphäre"
            )

            # Animationen mit Session State
            session_key_anim = 'ui_animations_checkbox'
            if session_key_anim not in st.session_state:
                st.session_state[session_key_anim] = convert_to_bool(
                    load_admin_setting('ui_animations_enabled', True))
            
            animations_enabled = st.checkbox(
                " UI-Animationen aktivieren",
                value=st.session_state[session_key_anim],
                key=session_key_anim,
                help="Smooth Transitions und Hover-Effekte"
            )

            # Kompakte Ansicht mit Session State
            session_key_compact = 'ui_compact_view_checkbox'
            if session_key_compact not in st.session_state:
                st.session_state[session_key_compact] = convert_to_bool(
                    load_admin_setting('ui_compact_view_enabled', True))
            
            compact_view = st.checkbox(
                " Kompakte Ansicht",
                value=st.session_state[session_key_compact],
                key=session_key_compact,
                help="Reduzierte Abstände für mehr Inhalte auf dem Bildschirm"
            )

        with col2:
            # Sound Effects mit Session State
            session_key_sound = 'ui_sound_effects_checkbox'
            if session_key_sound not in st.session_state:
                st.session_state[session_key_sound] = convert_to_bool(
                    load_admin_setting('ui_sound_effects_enabled', True))
            
            sound_effects = st.checkbox(
                " Sound-Effekte aktivieren",
                value=st.session_state[session_key_sound],
                key=session_key_sound,
                help="Akustisches Feedback für Aktionen"
            )

            # Farbschema
            current_color_scheme = load_admin_setting(
                'ui_color_scheme', 'Standard')
            
            color_scheme_options = [
                'Standard',
                'Ocean Blue',
                'Forest Green',
                'Sunset Orange',
                'Purple Rain',
                'Monochrome'
            ]
            
            color_scheme_index = 0
            try:
                color_scheme_index = color_scheme_options.index(current_color_scheme)
            except ValueError:
                color_scheme_index = 0
                
            color_scheme = st.selectbox(
                " Farbschema",
                options=color_scheme_options,
                index=color_scheme_index,
                help="Wählen Sie Ihr bevorzugtes Farbschema")

            # Sidebar Position
            current_sidebar_pos = load_admin_setting(
                'ui_sidebar_position', 'left')
            sidebar_position = st.selectbox(
                " Sidebar Position",
                options=['left', 'right'],
                index=['left', 'right'].index(current_sidebar_pos) if current_sidebar_pos in ['left', 'right'] else 0,
                help="Position der Navigationsleiste"
            )

    # ===  PERFORMANCE & CACHING ===
    with st.expander(" PERFORMANCE & CACHING", expanded=False):
        st.markdown("**Optimierung für maximale Geschwindigkeit**")

        col1, col2 = st.columns(2)

        with col1:
            # Auto-Cache
            current_auto_cache = convert_to_bool(
                load_admin_setting(
                    'performance_auto_cache_enabled', True))
            auto_cache = st.checkbox(
                " Intelligentes Caching",
                value=current_auto_cache,
                help="Automatisches Zwischenspeichern für schnellere Berechnungen")

            # Cache-Größe
            current_cache_size = load_admin_setting(
                'performance_cache_size_mb', 100)
            cache_size = st.slider(
                " Cache-Größe (MB)",
                min_value=50,
                max_value=500,
                value=int(current_cache_size),
                step=25,
                help="Mehr Cache = Schnellere App, aber mehr RAM-Verbrauch"
            )

        with col2:
            # Background Processing
            current_background_proc = convert_to_bool(
                load_admin_setting('performance_background_processing', True))
            background_processing = st.checkbox(
                " Hintergrund-Verarbeitung",
                value=current_background_proc,
                help="Berechnungen im Hintergrund für bessere Responsivität"
            )

            # Preload Settings
            current_preload = convert_to_bool(
                load_admin_setting(
                    'performance_preload_data', True))
            preload_data = st.checkbox(
                " Daten vorladen",
                value=current_preload,
                help="Lädt häufig verwendete Daten beim Start vor"
            )

    # ===  SICHERHEIT & DATENSCHUTZ ===
    with st.expander(" SICHERHEIT & DATENSCHUTZ", expanded=False):
        st.markdown("**Schutz Ihrer sensiblen Daten**")

        col1, col2 = st.columns(2)

        with col1:
            # Automatisches Logout
            current_auto_logout = load_admin_setting(
                'security_auto_logout_minutes', 60)
            auto_logout = st.slider(
                "⏰ Auto-Logout (Minuten)",
                min_value=15,
                max_value=240,
                value=int(current_auto_logout),
                step=15,
                help="Automatische Abmeldung bei Inaktivität"
            )

            # Daten-Verschlüsselung
            current_encryption = convert_to_bool(
                load_admin_setting(
                    'security_data_encryption_enabled', True))
            data_encryption = st.checkbox(
                " Daten-Verschlüsselung",
                value=current_encryption,
                help="AES-256 Verschlüsselung für gespeicherte Daten"
            )

        with col2:
            # Session Security
            current_session_security = convert_to_bool(
                load_admin_setting('security_enhanced_session', True))
            session_security = st.checkbox(
                " Erweiterte Session-Sicherheit",
                value=current_session_security,
                help="Zusätzliche Sicherheitsmaßnahmen für Sessions"
            )

            # Audit Log
            current_audit_log = convert_to_bool(
                load_admin_setting(
                    'security_audit_log_enabled', True))
            audit_log = st.checkbox(
                " Audit-Protokoll",
                value=current_audit_log,
                help="Protokollierung aller wichtigen Benutzeraktionen"
            )

    # === 🤖 AI & MACHINE LEARNING ===
    with st.expander("🤖 AI & MACHINE LEARNING", expanded=False):
        st.markdown("**Künstliche Intelligenz Features**")

        col1, col2 = st.columns(2)

        with col1:
            # AI Assistent
            current_ai_assistant = convert_to_bool(
                load_admin_setting('ai_assistant_enabled', True))
            ai_assistant = st.checkbox(
                "🤖 AI-Assistent aktivieren",
                value=current_ai_assistant,
                help="Intelligenter Chatbot für Benutzerunterstützung"
            )

            # Predictive Analytics
            current_predictive = convert_to_bool(
                load_admin_setting('ai_predictive_analytics', True))
            predictive_analytics = st.checkbox(
                " Predictive Analytics",
                value=current_predictive,
                help="Vorhersage von Trends und Mustern in Ihren Daten"
            )

        with col2:
            # Smart Recommendations
            current_smart_rec = convert_to_bool(
                load_admin_setting('ai_smart_recommendations', True))
            smart_recommendations = st.checkbox(
                " Intelligente Empfehlungen",
                value=current_smart_rec,
                help="AI-basierte Vorschläge für optimale Konfigurationen"
            )

            # Auto PDF Optimization
            current_pdf_optimization = convert_to_bool(
                load_admin_setting('ai_pdf_optimization', True))
            pdf_optimization = st.checkbox(
                " Auto PDF-Optimierung",
                value=current_pdf_optimization,
                help="AI optimiert PDF-Layout automatisch"
            )

    # ===  ERWEITERTE BERECHNUNGSOPTIONEN ===
    with st.expander(" ERWEITERTE BERECHNUNGEN", expanded=False):
        st.markdown("**Präzision und Detailgrad der Analysen**")

        col1, col2 = st.columns(2)

        with col1:
            # Berechnungsgenauigkeit
            current_calculation_precision = load_admin_setting(
                'calc_precision_level', 'standard')
            calculation_precision = st.selectbox(
                " Berechnungsgenauigkeit",
                options=[
                    'basic',
                    'standard',
                    'high',
                    'ultra'],
                index=[
                    'basic',
                    'standard',
                    'high',
                    'ultra'].index(current_calculation_precision),
                help="Höhere Genauigkeit = Langsamere aber präzisere Berechnungen")

            # Monte Carlo Simulation
            current_monte_carlo = convert_to_bool(
                load_admin_setting('calc_monte_carlo_enabled', True))
            monte_carlo = st.checkbox(
                " Monte Carlo Simulation",
                value=current_monte_carlo,
                help="Statistische Simulation für Risikobewertung"
            )

        with col2:
            # Wetterdatenintegration
            current_weather_data = convert_to_bool(
                load_admin_setting('calc_weather_integration', True))
            weather_integration = st.checkbox(
                " Erweiterte Wetterdaten",
                value=current_weather_data,
                help="Integration historischer und prognostizierter Wetterdaten")

            # Degradation Analysis
            current_degradation = convert_to_bool(
                load_admin_setting('calc_degradation_analysis', True))
            degradation_analysis = st.checkbox(
                " Degradations-Analyse",
                value=current_degradation,
                help="Berücksichtigung der Modulalterung über 25 Jahre"
            )

    # ===  GAMIFICATION & MOTIVATION ===
    with st.expander(" GAMIFICATION & MOTIVATION", expanded=False):
        st.markdown("**Spielerische Elemente für mehr Engagement**")

        col1, col2 = st.columns(2)

        with col1:
            # Achievement System
            current_achievements = convert_to_bool(
                load_admin_setting(
                    'gamification_achievements_enabled', True))
            achievements = st.checkbox(
                " Achievement-System",
                value=current_achievements,
                help="Sammeln Sie Erfolge für verschiedene Meilensteine"
            )

            # Progress Tracking
            current_progress = convert_to_bool(
                load_admin_setting(
                    'gamification_progress_tracking', True))
            progress_tracking = st.checkbox(
                " Fortschritts-Tracking",
                value=current_progress,
                help="Visualisierung Ihres Arbeitsfortschritts"
            )

        with col2:
            # Daily Challenges
            current_challenges = convert_to_bool(
                load_admin_setting(
                    'gamification_daily_challenges', True))
            daily_challenges = st.checkbox(
                " Tägliche Herausforderungen",
                value=current_challenges,
                help="Tägliche Mini-Aufgaben für aktive Nutzung"
            )

            # Leaderboard
            current_leaderboard = convert_to_bool(
                load_admin_setting('gamification_leaderboard', True))
            leaderboard = st.checkbox(
                "🥇 Bestenliste",
                value=current_leaderboard,
                help="Vergleichen Sie sich mit anderen Nutzern"
            )

    # ===  NACHHALTIGKEIT & UMWELT ===
    with st.expander(" NACHHALTIGKEIT & UMWELT", expanded=False):
        st.markdown("**Umweltbewusstsein und Nachhaltigkeit**")

        col1, col2 = st.columns(2)

        with col1:
            # CO2 Tracking
            current_co2_tracking = convert_to_bool(
                load_admin_setting('sustainability_co2_tracking', True))
            co2_tracking = st.checkbox(
                " Erweiterte CO₂-Bilanz",
                value=current_co2_tracking,
                help="Detaillierte Analyse der Umweltauswirkungen"
            )

            # Green Energy Badge
            current_green_badge = convert_to_bool(
                load_admin_setting('sustainability_green_badge', True))
            green_badge = st.checkbox(
                " Grüne Energie Badge",
                value=current_green_badge,
                help="Zeigt Umweltfreundlichkeit der Konfiguration"
            )

        with col2:
            # Nachhaltigkeits-Score
            current_sustainability_score = convert_to_bool(
                load_admin_setting('sustainability_score_enabled', True))
            sustainability_score = st.checkbox(
                " Nachhaltigkeits-Score",
                value=current_sustainability_score,
                help="Bewertung der ökologischen Effizienz (0-100)"
            )

            # Recycling Info
            current_recycling_info = convert_to_bool(
                load_admin_setting('sustainability_recycling_info', True))
            recycling_info = st.checkbox(
                " Recycling-Hinweise",
                value=current_recycling_info,
                help="Informationen zur umweltgerechten Entsorgung"
            )

    # ===  MOBILE & RESPONSIVE EINSTELLUNGEN ===
    with st.expander(" MOBILE & RESPONSIVE", expanded=False):
        st.markdown("**Optimierung für mobile Geräte**")

        col1, col2 = st.columns(2)

        with col1:
            # Mobile Optimierung
            current_mobile_opt = convert_to_bool(
                load_admin_setting('mobile_optimization_enabled', True))
            mobile_optimization = st.checkbox(
                " Mobile Optimierung",
                value=current_mobile_opt,
                help="Spezielle Anpassungen für Smartphones und Tablets"
            )

            # Touch-friendly UI
            current_touch_ui = convert_to_bool(
                load_admin_setting('mobile_touch_friendly', True))
            touch_friendly = st.checkbox(
                " Touch-optimierte Bedienung",
                value=current_touch_ui,
                help="Größere Buttons und Touch-Gesten"
            )

        with col2:
            # Offline Modus
            current_offline_mode = convert_to_bool(
                load_admin_setting('mobile_offline_mode', True))
            offline_mode = st.checkbox(
                " Offline-Modus",
                value=current_offline_mode,
                help="Grundfunktionen auch ohne Internetverbindung"
            )

            # Progressive Web App
            current_pwa = convert_to_bool(
                load_admin_setting(
                    'mobile_pwa_enabled', True))
            pwa_enabled = st.checkbox(
                " Progressive Web App",
                value=current_pwa,
                help="Installation als App auf dem Smartphone möglich"
            )

    # ===  AUDIO & MULTIMEDIA ===
    with st.expander(" AUDIO & MULTIMEDIA", expanded=False):
        st.markdown("**Multimediale Erweiterungen**")

        col1, col2 = st.columns(2)

        with col1:
            # Voice Commands
            current_voice_commands = convert_to_bool(
                load_admin_setting('audio_voice_commands', True))
            voice_commands = st.checkbox(
                " Sprachsteuerung",
                value=current_voice_commands,
                help="Bedienung per Sprachbefehle"
            )

            # Text-to-Speech
            current_tts = convert_to_bool(
                load_admin_setting(
                    'audio_text_to_speech', True))
            text_to_speech = st.checkbox(
                " Text-zu-Sprache",
                value=current_tts,
                help="Vorlesen von Berechnungsergebnissen"
            )

        with col2:
            # Background Music
            current_bg_music = convert_to_bool(
                load_admin_setting('audio_background_music', True))
            background_music = st.checkbox(
                " Hintergrundmusik",
                value=current_bg_music,
                help="Entspannende Musik während der Arbeit"
            )

            # Video Tutorials
            current_video_tutorials = convert_to_bool(
                load_admin_setting('multimedia_video_tutorials', True))
            video_tutorials = st.checkbox(
                " Integrierte Video-Tutorials",
                value=current_video_tutorials,
                help="Hilfe-Videos direkt in der App"
            )

    st.markdown("---")
    # ===  SUPER SAVE BUTTON ===
    st.markdown("### 💾 Alle Einstellungen speichern")
    
    # Info-Box mit Hinweis
    st.info("""
    **💡 Hinweis:** Dieser Button speichert ALLE erweiterten Einstellungen auf einmal und wendet sie sofort an!
    
    ✓ UI/UX Einstellungen  
    ✓ Performance-Optimierungen  
    ✓ Sicherheitseinstellungen  
    ✓ AI & ML Features  
    ✓ Berechnungsoptionen  
    ✓ Gamification & Motivation  
    ✓ Nachhaltigkeit & Umwelt  
    ✓ Mobile & Responsive  
    ✓ Audio & Multimedia  
    """)
    
    if st.button(
        "🚀 **ALLE ERWEITERTEN EINSTELLUNGEN SPEICHERN**",
        type="primary",
            use_container_width=True):
        with st.spinner("💫 Speichere alle Einstellungen..."):
            success_count = 0
            total_settings = 0
            failed_settings = []

            # UI/UX Settings
            settings_to_save = [
                ('ui_dark_mode_enabled', st.session_state.get('ui_dark_mode_checkbox', dark_mode), "Dark Mode"),
                ('ui_animations_enabled', st.session_state.get('ui_animations_checkbox', animations_enabled), "Animationen"),
                ('ui_compact_view_enabled', st.session_state.get('ui_compact_view_checkbox', compact_view), "Kompakte Ansicht"),
                ('ui_sound_effects_enabled', st.session_state.get('ui_sound_effects_checkbox', sound_effects), "Sound-Effekte"),
                ('ui_color_scheme', color_scheme, "Farbschema"),
                ('ui_sidebar_position', sidebar_position, "Sidebar Position"),

                # Performance Settings
                ('performance_auto_cache_enabled', auto_cache, "Auto-Cache"),
                ('performance_cache_size_mb', cache_size, "Cache-Größe"),
                ('performance_background_processing', background_processing, "Hintergrund-Verarbeitung"),
                ('performance_preload_data', preload_data, "Daten vorladen"),

                # Security Settings
                ('security_auto_logout_minutes', auto_logout, "Auto-Logout"),
                ('security_data_encryption_enabled', data_encryption, "Daten-Verschlüsselung"),
                ('security_enhanced_session', session_security, "Session-Sicherheit"),
                ('security_audit_log_enabled', audit_log, "Audit-Protokoll"),

                # AI Settings
                ('ai_assistant_enabled', ai_assistant, "AI-Assistent"),
                ('ai_predictive_analytics', predictive_analytics, "Predictive Analytics"),
                ('ai_smart_recommendations', smart_recommendations, "Intelligente Empfehlungen"),
                ('ai_pdf_optimization', pdf_optimization, "PDF-Optimierung"),

                # Calculation Settings
                ('calc_precision_level', calculation_precision, "Berechnungsgenauigkeit"),
                ('calc_monte_carlo_enabled', monte_carlo, "Monte Carlo"),
                ('calc_weather_integration', weather_integration, "Wetterdaten"),
                ('calc_degradation_analysis', degradation_analysis, "Degradations-Analyse"),

                # Gamification Settings
                ('gamification_achievements_enabled', achievements, "Achievement-System"),
                ('gamification_progress_tracking', progress_tracking, "Fortschritts-Tracking"),
                ('gamification_daily_challenges', daily_challenges, "Tägliche Herausforderungen"),
                ('gamification_leaderboard', leaderboard, "Bestenliste"),

                # Sustainability Settings
                ('sustainability_co2_tracking', co2_tracking, "CO₂-Bilanz"),
                ('sustainability_green_badge', green_badge, "Grüne Energie Badge"),
                ('sustainability_score_enabled', sustainability_score, "Nachhaltigkeits-Score"),
                ('sustainability_recycling_info', recycling_info, "Recycling-Hinweise"),

                # Mobile Settings
                ('mobile_optimization_enabled', mobile_optimization, "Mobile Optimierung"),
                ('mobile_touch_friendly', touch_friendly, "Touch-optimiert"),
                ('mobile_offline_mode', offline_mode, "Offline-Modus"),
                ('mobile_pwa_enabled', pwa_enabled, "Progressive Web App"),

                # Audio/Multimedia Settings
                ('ui_show_emojis', show_emojis, "Emojis"),
                ('audio_voice_commands', voice_commands, "Sprachsteuerung"),
                ('audio_text_to_speech', text_to_speech, "Text-zu-Sprache"),
                ('audio_background_music', background_music, "Hintergrundmusik"),
                ('multimedia_video_tutorials', video_tutorials, "Video-Tutorials"),
            ]

            for key, value, display_name in settings_to_save:
                total_settings += 1
                try:
                    if save_admin_setting(key, value):
                        success_count += 1
                        # Session State aktualisieren
                        st.session_state[key] = value
                    else:
                        failed_settings.append(display_name)
                except Exception as e:
                    failed_settings.append(f"{display_name} ({str(e)})")

            # Erfolgsmeldung mit Statistik
            if success_count == total_settings:
                st.success(f"""
                ✅ **ALLE EINSTELLUNGEN ERFOLGREICH GESPEICHERT!**

                 **{success_count}/{total_settings}** Einstellungen wurden gespeichert

                🔄 Die App wird gleich neu geladen, um alle Änderungen anzuwenden...
                """)

                # Session State für UI-Updates setzen
                st.session_state['settings_updated'] = True
                st.session_state['ui_refresh_needed'] = True
                st.session_state['settings_save_success'] = True

                # Wende UI-Settings sofort an
                try:
                    from ui_settings_handler import apply_ui_settings
                    apply_ui_settings()
                except ImportError:
                    pass  # Modul optional
                except Exception as e:
                    st.warning(f"⚠️ UI-Settings konnten nicht angewendet werden: {e}")

                # Performance-Settings neu laden
                try:
                    from performance_handler import load_performance_settings
                    load_performance_settings()
                except ImportError:
                    pass  # Modul optional
                except Exception as e:
                    st.warning(f"⚠️ Performance-Settings konnten nicht geladen werden: {e}")

                # Auto-Reload nach 2 Sekunden
                import time
                time.sleep(2)
                st.rerun()

            elif success_count > 0:
                # Teilweise erfolgreich
                st.warning(f"""
                ⚠️ **TEILWEISE ERFOLGREICH**
                
                ✅ {success_count}/{total_settings} Einstellungen gespeichert  
                ❌ {total_settings - success_count} Einstellungen fehlgeschlagen
                """)
                
                if failed_settings:
                    with st.expander("🔍 Details zu fehlgeschlagenen Einstellungen", expanded=False):
                        st.markdown("**Folgende Einstellungen konnten nicht gespeichert werden:**")
                        for i, failed in enumerate(failed_settings[:15], 1):  # Max 15
                            st.markdown(f"{i}. {failed}")
                        if len(failed_settings) > 15:
                            st.markdown(f"\n*... und {len(failed_settings) - 15} weitere*")
                        
                        st.info("💡 **Tipp:** Prüfen Sie die Datenbankverbindung oder kontaktieren Sie den Administrator.")
            else:
                # Vollständig fehlgeschlagen
                st.error(f"""
                ❌ **SPEICHERN FEHLGESCHLAGEN**
                
                Keine Einstellungen konnten gespeichert werden!
                
                **Mögliche Ursachen:**
                - Datenbankverbindung unterbrochen
                - Fehlende Schreibrechte
                - Serverprobleme
                """)
                
                if failed_settings:
                    with st.expander("🔍 Fehlerdetails anzeigen"):
                        for failed in failed_settings:
                            st.code(failed)

    # === DEBUG INFO ===
    with st.expander(" DEBUG-INFORMATIONEN", expanded=False):
        current_debug_mode = convert_to_bool(
            load_admin_setting('app_debug_mode_enabled', True))
        debug_mode = st.checkbox(
            " Debug-Modus aktivieren",
            value=current_debug_mode,
            help="Aktiviert erweiterte Debugging-Informationen in der Anwendung")

        if debug_mode:
            st.json({
                "session_state_keys": list(st.session_state.keys()),
                "current_user_agent": st.get_option("server.address"),
                "total_settings_available": 40,
                "database_available": options_dependencies_available
            })

        if st.button(" Debug-Einstellungen speichern"):
            if save_admin_setting('app_debug_mode_enabled', debug_mode):
                st.success(" Debug-Einstellungen gespeichert!")
            else:
                st.error(" Fehler beim Speichern")

    # Entfernen Sie dies, wenn Sie den Inhalt implementieren
