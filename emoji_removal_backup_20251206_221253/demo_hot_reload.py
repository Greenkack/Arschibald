"""
Demo: Hot Reload für Theme-Entwicklung

Zeigt wie Hot Reload für Theme-Dateien funktioniert.
"""

import streamlit as st
import time
from pathlib import Path

# Theme System
from theming.theme_manager import ThemeManager
from theming.hot_reload_manager import HotReloadManager, create_hot_reload_manager
from theming.dev_mode import get_dev_mode_config, is_dev_mode, enable_dev_mode
from theming.validation_display import ValidationDisplay
from theming.theme_validator import ThemeValidator

# CSS Generator
from theming.css_generator import CSSGenerator


def main():
    """Hauptfunktion"""
    
    st.set_page_config(
        page_title="Hot Reload Demo",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Hot Reload für Theme-Entwicklung")
    st.markdown("---")
    
    # Initialisiere Session State
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    if 'hot_reload_manager' not in st.session_state:
        st.session_state.hot_reload_manager = None
    
    if 'validation_display' not in st.session_state:
        st.session_state.validation_display = ValidationDisplay()
    
    if 'reload_count' not in st.session_state:
        st.session_state.reload_count = 0
    
    theme_manager = st.session_state.theme_manager
    validation_display = st.session_state.validation_display
    
    # Sidebar: Konfiguration
    with st.sidebar:
        st.header("⚙️ Konfiguration")
        
        # Development Mode
        dev_mode = st.checkbox(
            "Development Mode",
            value=is_dev_mode(),
            help="Aktiviert Development-Features wie Hot Reload"
        )
        
        if dev_mode:
            enable_dev_mode()
        
        st.markdown("---")
        
        # Hot Reload Einstellungen
        st.subheader("🔄 Hot Reload")
        
        hot_reload_enabled = st.checkbox(
            "Hot Reload aktivieren",
            value=st.session_state.hot_reload_manager is not None,
            disabled=not dev_mode,
            help="Überwacht Theme-Dateien und lädt sie automatisch neu"
        )
        
        debounce_seconds = st.slider(
            "Debounce (Sekunden)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1,
            disabled=not dev_mode,
            help="Wartezeit zwischen File-Events"
        )
        
        # Validierung
        st.markdown("---")
        st.subheader("✅ Validierung")
        
        validate_on_reload = st.checkbox(
            "Bei Reload validieren",
            value=True,
            disabled=not dev_mode,
            help="Validiert Theme automatisch nach Reload"
        )
        
        show_validation_errors = st.checkbox(
            "Fehler anzeigen",
            value=True,
            disabled=not dev_mode,
            help="Zeigt Validierungs-Fehler in Echtzeit"
        )
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Theme-Dateien")
        
        # Zeige Theme-Verzeichnis
        themes_dir = theme_manager.themes_dir
        st.code(str(themes_dir), language="text")
        
        # Liste verfügbare Themes
        st.subheader("Verfügbare Themes")
        
        themes = theme_manager.get_available_themes()
        for theme_name in themes:
            theme_file = themes_dir / f"{theme_name}.json"
            
            col_a, col_b, col_c = st.columns([3, 1, 1])
            
            with col_a:
                st.text(f"📄 {theme_name}.json")
            
            with col_b:
                if theme_file.exists():
                    size = theme_file.stat().st_size
                    st.text(f"{size} bytes")
            
            with col_c:
                if st.button("Validieren", key=f"validate_{theme_name}"):
                    validator = ThemeValidator()
                    theme = theme_manager.get_theme(theme_name)
                    
                    if theme:
                        is_valid, errors = validator.validate_theme(theme.to_dict())
                        
                        if is_valid:
                            st.success(f"✅ {theme_name} ist valide")
                        else:
                            st.error(f"❌ {theme_name} hat Fehler:")
                            for error in errors:
                                st.text(f"  - {error}")
        
        st.markdown("---")
        
        # Anleitung
        st.subheader("📝 Anleitung")
        
        st.markdown("""
        **So verwendest du Hot Reload:**
        
        1. ✅ Aktiviere "Development Mode" in der Sidebar
        2. ✅ Aktiviere "Hot Reload aktivieren"
        3. 📝 Öffne eine Theme-Datei in deinem Editor
        4. ✏️ Ändere Farben, Schriftarten, etc.
        5. 💾 Speichere die Datei
        6. 🔄 Das Theme wird automatisch neu geladen!
        
        **Beispiel-Änderung:**
        
        ```json
        {
          "colors": {
            "primary": "#ff0000",  // Ändere zu einer anderen Farbe
            "background": "#ffffff"
          }
        }
        ```
        
        **Tipps:**
        
        - 🎯 Nutze den Debounce-Slider um die Reaktionszeit anzupassen
        - ✅ Aktiviere "Bei Reload validieren" um Fehler sofort zu sehen
        - 📊 Beobachte die Statistiken um zu sehen wie oft Themes geladen wurden
        """)
    
    with col2:
        st.header("📊 Status")
        
        # Hot Reload Status
        if st.session_state.hot_reload_manager:
            st.success("🟢 Hot Reload aktiv")
            
            stats = st.session_state.hot_reload_manager.get_stats()
            
            st.metric("Reloads", stats['reloads'])
            st.metric("Fehler", stats['errors'])
            
            if stats['last_reload']:
                st.text(f"Letzter Reload:")
                st.text(stats['last_reload'])
            
            if stats['uptime_formatted']:
                st.text(f"Uptime:")
                st.text(stats['uptime_formatted'])
        else:
            st.warning("🔴 Hot Reload inaktiv")
        
        st.markdown("---")
        
        # Aktuelles Theme
        st.subheader("🎨 Aktuelles Theme")
        current_theme = theme_manager.get_current_theme()
        st.info(f"**{current_theme}**")
        
        # Theme wechseln
        new_theme = st.selectbox(
            "Theme wechseln",
            options=themes,
            index=themes.index(current_theme) if current_theme in themes else 0
        )
        
        if new_theme != current_theme:
            theme_manager.set_theme(new_theme)
            st.rerun()
        
        st.markdown("---")
        
        # Actions
        st.subheader("🎬 Aktionen")
        
        if st.button("🔄 Alle Themes neu laden", use_container_width=True):
            theme_manager.load_themes()
            st.success("Themes neu geladen!")
            st.rerun()
        
        if st.button("🧹 Historie löschen", use_container_width=True):
            validation_display.clear_history()
            st.success("Historie gelöscht!")
    
    # Hot Reload Manager starten/stoppen
    if hot_reload_enabled and not st.session_state.hot_reload_manager:
        # Callback für Theme-Reload
        def on_theme_reload(theme_name: str):
            st.session_state.reload_count += 1
            
            # Validiere Theme wenn aktiviert
            if validate_on_reload:
                validator = ThemeValidator()
                theme = theme_manager.get_theme(theme_name)
                
                if theme:
                    is_valid, errors = validator.validate_theme(theme.to_dict())
                    
                    if show_validation_errors:
                        if is_valid:
                            validation_display.show_validation_success(theme_name)
                        else:
                            validation_display.show_validation_errors(
                                theme_name,
                                errors
                            )
        
        # Erstelle und starte Hot Reload Manager
        manager = create_hot_reload_manager(
            theme_manager,
            enabled=True,
            debounce_seconds=debounce_seconds
        )
        
        if manager:
            manager.start(callback=on_theme_reload)
            st.session_state.hot_reload_manager = manager
            st.success("✅ Hot Reload gestartet!")
            time.sleep(1)
            st.rerun()
    
    elif not hot_reload_enabled and st.session_state.hot_reload_manager:
        # Stoppe Hot Reload Manager
        st.session_state.hot_reload_manager.stop()
        st.session_state.hot_reload_manager = None
        st.info("Hot Reload gestoppt")
        time.sleep(1)
        st.rerun()
    
    # Validierungs-Historie
    st.markdown("---")
    st.header("📋 Validierungs-Historie")
    
    summary = validation_display.get_error_summary()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Validierungen", summary['total_validations'])
    
    with col2:
        st.metric("Fehler", summary['total_errors'])
    
    with col3:
        st.metric("Warnungen", summary['total_warnings'])
    
    if summary['themes_with_errors']:
        st.warning(
            f"Themes mit Fehlern: {', '.join(summary['themes_with_errors'])}"
        )
    
    # Zeige Historie
    validation_display.show_validation_history(limit=10)
    
    # CSS Preview
    st.markdown("---")
    st.header("🎨 CSS Preview")
    
    with st.expander("Generiertes CSS anzeigen", expanded=False):
        try:
            css = theme_manager.generate_css(minified=False)
            st.code(css, language="css")
        except Exception as e:
            st.error(f"Fehler beim Generieren von CSS: {e}")


if __name__ == "__main__":
    main()
