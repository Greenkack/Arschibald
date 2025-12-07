"""
Demo: Theme Validator

Demonstriert die Verwendung des Theme-Validierungssystems.
"""

import streamlit as st
import json
import tempfile
from pathlib import Path
from theming.theme_validator import (
    ThemeValidator,
    validate_theme_file,
    ValidationResult,
    DEFAULT_THEME_VALUES
)


def main():
    st.set_page_config(page_title="Theme Validator Demo", page_icon="✅", layout="wide")
    
    st.title("🎨 Theme Validator Demo")
    st.markdown("Demonstriert die Validierung von Theme-Dateien")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Datei validieren",
        "✏️ Theme erstellen",
        "📊 Batch-Validierung",
        "📖 Dokumentation"
    ])
    
    with tab1:
        demo_file_validation()
    
    with tab2:
        demo_theme_creation()
    
    with tab3:
        demo_batch_validation()
    
    with tab4:
        show_documentation()


def demo_file_validation():
    """Demo: Datei-Validierung"""
    st.header("Theme-Datei validieren")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload")
        
        # File Upload
        uploaded_file = st.file_uploader(
            "Theme-Datei hochladen",
            type=['json'],
            help="Lade eine Theme-JSON-Datei hoch"
        )
        
        # Optionen
        fix_errors = st.checkbox("Fehlende Properties automatisch auffüllen", value=True)
        save_fixed = st.checkbox("Korrigiertes Theme speichern", value=False)
        
        if uploaded_file:
            # Speichere temporär
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as tmp:
                content = uploaded_file.getvalue().decode('utf-8')
                tmp.write(content)
                tmp_path = tmp.name
            
            # Validiere
            with st.spinner("Validiere Theme..."):
                result = validate_theme_file(tmp_path, fix_errors=fix_errors, save_fixed=save_fixed)
            
            # Zeige Ergebnis in rechter Spalte
            with col2:
                show_validation_result(result, uploaded_file.name)
    
    with col2:
        if not uploaded_file:
            st.info("👈 Lade eine Theme-Datei hoch, um zu beginnen")
            
            # Beispiel-Themes zum Download
            st.subheader("Beispiel-Themes")
            
            themes_dir = Path('theming/themes')
            if themes_dir.exists():
                for theme_file in themes_dir.glob('*.json'):
                    with open(theme_file, 'r') as f:
                        theme_data = f.read()
                    
                    st.download_button(
                        f"📥 {theme_file.stem}",
                        theme_data,
                        file_name=theme_file.name,
                        mime="application/json",
                        key=f"download_{theme_file.stem}"
                    )


def demo_theme_creation():
    """Demo: Theme-Erstellung"""
    st.header("Neues Theme erstellen")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Theme-Eigenschaften")
        
        # Basis-Informationen
        theme_name = st.text_input(
            "Theme-Name",
            value="my-custom-theme",
            help="Nur Kleinbuchstaben, Zahlen und Bindestriche"
        )
        
        display_name = st.text_input(
            "Anzeigename",
            value="My Custom Theme"
        )
        
        # Farben
        st.subheader("Farben")
        
        col_a, col_b = st.columns(2)
        with col_a:
            background = st.color_picker("Background", "#ffffff")
            primary = st.color_picker("Primary", "#3b82f6")
            success = st.color_picker("Success", "#22c55e")
        
        with col_b:
            foreground = st.color_picker("Foreground", "#0a0a0a")
            secondary = st.color_picker("Secondary", "#f4f4f5")
            error = st.color_picker("Error", "#ef4444")
        
        # Typography
        st.subheader("Typography")
        
        font_family = st.text_input(
            "Font Family",
            value="Inter, sans-serif"
        )
        
        font_size_base = st.selectbox(
            "Base Font Size",
            ["0.875rem", "1rem", "1.125rem"],
            index=1
        )
        
        # Theme erstellen
        if st.button("🎨 Theme erstellen", type="primary"):
            theme_data = create_theme_data(
                theme_name, display_name,
                background, foreground,
                primary, secondary,
                success, error,
                font_family, font_size_base
            )
            
            # Validiere
            validator = ThemeValidator()
            result = validator.validate_theme(theme_data, fix_errors=True)
            
            # Zeige Ergebnis
            with col2:
                show_validation_result(result, f"{theme_name}.json")
                
                # Download-Button
                if result.is_valid and result.fixed_theme:
                    theme_json = json.dumps(result.fixed_theme, indent=2)
                    st.download_button(
                        "📥 Theme herunterladen",
                        theme_json,
                        file_name=f"{theme_name}.json",
                        mime="application/json"
                    )
    
    with col2:
        if 'result' not in locals():
            st.info("👈 Erstelle ein Theme, um die Vorschau zu sehen")


def demo_batch_validation():
    """Demo: Batch-Validierung"""
    st.header("Alle Themes validieren")
    
    themes_dir = Path('theming/themes')
    
    if not themes_dir.exists():
        st.warning(f"Themes-Verzeichnis nicht gefunden: {themes_dir}")
        return
    
    theme_files = list(themes_dir.glob('*.json'))
    
    if not theme_files:
        st.info(f"Keine Theme-Dateien gefunden in: {themes_dir}")
        return
    
    st.info(f"Gefunden: {len(theme_files)} Theme-Dateien")
    
    # Optionen
    col1, col2 = st.columns([1, 3])
    with col1:
        fix_errors = st.checkbox("Fehler korrigieren", value=True, key="batch_fix")
    with col2:
        show_details = st.checkbox("Details anzeigen", value=False, key="batch_details")
    
    if st.button("🔍 Alle validieren", type="primary"):
        validator = ThemeValidator()
        
        # Progress Bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = {}
        for i, theme_file in enumerate(theme_files):
            status_text.text(f"Validiere {theme_file.name}...")
            result = validator.validate_file(str(theme_file), fix_errors=fix_errors)
            results[theme_file.name] = result
            progress_bar.progress((i + 1) / len(theme_files))
        
        status_text.empty()
        progress_bar.empty()
        
        # Zusammenfassung
        valid_count = sum(1 for r in results.values() if r.is_valid)
        invalid_count = len(results) - valid_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamt", len(results))
        with col2:
            st.metric("✅ Gültig", valid_count)
        with col3:
            st.metric("❌ Ungültig", invalid_count)
        
        # Details
        st.subheader("Ergebnisse")
        
        for name, result in results.items():
            with st.expander(
                f"{'✅' if result.is_valid else '❌'} {name}",
                expanded=not result.is_valid or show_details
            ):
                show_validation_result(result, name, compact=not show_details)


def show_validation_result(result: ValidationResult, filename: str, compact: bool = False):
    """Zeigt Validierungs-Ergebnis an"""
    
    # Status
    if result.is_valid:
        st.success(f"✅ **{filename}** ist gültig!")
    else:
        st.error(f"❌ **{filename}** ist ungültig!")
    
    # Metriken
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fehler", len(result.errors))
    with col2:
        st.metric("Warnungen", len(result.warnings))
    with col3:
        st.metric("Hinweise", len(result.info))
    
    if compact and result.is_valid:
        return
    
    # Fehler
    if result.errors:
        st.subheader("❌ Fehler")
        for error in result.errors:
            st.error(str(error))
    
    # Warnungen
    if result.warnings:
        st.subheader("⚠️ Warnungen")
        for warning in result.warnings:
            st.warning(str(warning))
    
    # Hinweise
    if result.info:
        st.subheader("ℹ️ Hinweise")
        for info in result.info:
            st.info(str(info))
    
    # Korrigiertes Theme
    if result.fixed_theme and not compact:
        with st.expander("📄 Korrigiertes Theme anzeigen"):
            st.json(result.fixed_theme)


def create_theme_data(
    name: str,
    display_name: str,
    background: str,
    foreground: str,
    primary: str,
    secondary: str,
    success: str,
    error: str,
    font_family: str,
    font_size_base: str
) -> dict:
    """Erstellt Theme-Daten aus Eingaben"""
    
    return {
        "name": name,
        "display_name": display_name,
        "colors": {
            "background": background,
            "foreground": foreground,
            "primary": primary,
            "secondary": secondary,
            "success": success,
            "error": error
        },
        "typography": {
            "font_family": font_family,
            "font_size_base": font_size_base
        }
    }


def show_documentation():
    """Zeigt Dokumentation an"""
    st.header("📖 Dokumentation")
    
    st.markdown("""
    ## Theme Validator
    
    Das Theme-Validierungssystem bietet umfassende Validierung von Theme-Dateien.
    
    ### Features
    
    - ✅ JSON-Schema-Validierung
    - 🎨 Farb-Validierung (Hex, RGB, RGBA)
    - 📝 Typography-Validierung
    - 🔧 Automatisches Auffüllen fehlender Properties
    - 📊 Detaillierte Fehlerberichte
    
    ### Verwendung
    
    #### Python API
    
    ```python
    from theming.theme_validator import validate_theme_file
    
    # Theme validieren
    result = validate_theme_file('my-theme.json', fix_errors=True)
    
    if result.is_valid:
        print("✅ Theme ist gültig!")
        theme_data = result.fixed_theme
    else:
        print("❌ Theme ist ungültig!")
        for error in result.errors:
            print(f"  {error}")
    ```
    
    #### CLI-Tool
    
    ```bash
    # Einzelne Datei validieren
    python tools/validate_theme.py theming/themes/my-theme.json
    
    # Mit Fehlerkorrektur
    python tools/validate_theme.py theming/themes/my-theme.json --fix
    
    # Alle Themes validieren
    python tools/validate_theme.py --validate-all
    ```
    
    ### Validierungs-Regeln
    
    #### Farben
    
    Gültige Formate:
    - Hex: `#ffffff`, `#fff`, `#3b82f6`
    - RGB: `rgb(255, 255, 255)`
    - RGBA: `rgba(255, 255, 255, 0.5)`
    
    #### Typography
    
    - Font-Sizes müssen mit 'rem', 'px' oder 'em' enden
    - Font-Weights sollten Vielfache von 100 sein (100-900)
    - Line-Heights sollten zwischen 1.0 und 3.0 liegen
    
    ### Siehe auch
    
    - [Theme Validator Reference](theming/THEME_VALIDATOR_REFERENCE.md)
    - [Theme Validator Quick Reference](docs/THEME_VALIDATOR_QUICK_REFERENCE.md)
    - [Theme Validator Usage Examples](theming/THEME_VALIDATOR_USAGE_EXAMPLE.md)
    """)


if __name__ == '__main__':
    main()
