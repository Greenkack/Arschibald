"""
Demo: Admin Panel Matrix Upload mit Validierung

Dieses Demo zeigt die Verwendung der erweiterten Upload-Validierung
im Admin Panel.

Task 5: Verbessere Admin Panel Matrix-Upload Validierung
Requirements: 2.1, 2.2, 2.4
"""

import streamlit as st
from admin_price_matrix_upload import (
    render_matrix_upload_ui,
    render_matrix_list_ui,
    validate_uploaded_file
)


def main():
    """Hauptfunktion für Demo"""
    
    st.set_page_config(
        page_title="Admin Matrix Upload Demo",
        page_icon="📤",
        layout="wide"
    )
    
    st.title("📤 Admin Panel Matrix Upload Demo")
    st.markdown("---")
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs([
        "📤 Matrix hochladen",
        "Vorhandene Matrizen",
        "🧪 Validierung testen"
    ])
    
    # Tab 1: Matrix hochladen
    with tab1:
        st.header("Matrix hochladen")
        st.markdown("""
        Laden Sie eine Preismatrix-Datei (CSV oder Excel) hoch.
        Die Datei wird automatisch validiert und eine Vorschau angezeigt.
        """)
        
        render_matrix_upload_ui()
    
    # Tab 2: Vorhandene Matrizen
    with tab2:
        st.header("Vorhandene Matrizen")
        st.markdown("""
        Zeigt alle vorhandenen Matrizen mit Validierungsstatus.
        Sie können Matrizen aktivieren und validieren.
        """)
        
        render_matrix_list_ui()
    
    # Tab 3: Validierung testen
    with tab3:
        st.header("Validierung testen")
        st.markdown("""
        Testen Sie die Validierung mit verschiedenen Matrix-Beispielen.
        """)
        
        render_validation_test_ui()


def render_validation_test_ui():
    """Rendert UI zum Testen der Validierung"""
    
    st.subheader("Test-Beispiele")
    
    # Beispiel-Matrizen
    examples = {
        "Gültige Matrix": """Anzahl Module;10kWh;15kWh;Ohne Speicher
10;15000.00;17500.00;12000.00
15;18000.00;20500.00;15000.00
20;21000.00;23500.00;18000.00""",
        
        "Fehlende 'Ohne Speicher' Spalte": """Anzahl Module;10kWh;15kWh
10;15000.00;17500.00
15;18000.00;20500.00""",
        
        "Nicht-numerischer Index": """Anzahl Module;10kWh;Ohne Speicher
ABC;15000.00;12000.00
DEF;18000.00;15000.00""",
        
        "Nicht-numerische Preise": """Anzahl Module;10kWh;Ohne Speicher
10;ABC;12000.00
15;18000.00;XYZ""",
        
        "⚠ Leere Zellen (Warnung)": """Anzahl Module;10kWh;15kWh;Ohne Speicher
10;15000.00;;12000.00
15;;20500.00;15000.00
20;21000.00;23500.00;"""
    }
    
    # Beispiel auswählen
    selected_example = st.selectbox(
        "Wählen Sie ein Beispiel:",
        options=list(examples.keys())
    )
    
    # Zeige CSV-Inhalt
    st.markdown("### CSV-Inhalt")
    csv_content = examples[selected_example]
    st.code(csv_content, language='csv')
    
    # Validiere Button
    if st.button("Validieren", type="primary"):
        with st.spinner("Validiere..."):
            # Konvertiere zu Bytes
            file_content = csv_content.encode('utf-8')
            
            # Validiere
            result = validate_uploaded_file(file_content, 'csv')
            
            # Zeige Ergebnis
            st.markdown("---")
            st.markdown("### Validierungsergebnis")
            
            if result['valid']:
                st.success("Matrix ist gültig und kann importiert werden")
            else:
                st.error("Matrix enthält Fehler und kann nicht importiert werden")
            
            # Fehler
            if result['errors']:
                st.error("**Fehler:**")
                for error in result['errors']:
                    st.error(f"• {error}")
            
            # Warnungen
            if result['warnings']:
                st.warning("**Warnungen:**")
                for warning in result['warnings']:
                    st.warning(f"⚠ {warning}")
            
            # Informationen
            if result['info']:
                st.info("**Informationen:**")
                info = result['info']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Zeilen", info.get('rows', 0))
                with col2:
                    st.metric("Spalten", info.get('columns', 0))
                with col3:
                    st.metric("Zellen", info.get('total_cells', 0))
                with col4:
                    st.metric("Leere Zellen", info.get('empty_cells', 0))
                
                if 'no_storage_column' in info:
                    st.success(f"'Ohne Speicher' Spalte: **{info['no_storage_column']}**")
                
                if 'module_counts' in info and info['module_counts']:
                    counts_str = ', '.join(str(int(c)) for c in info['module_counts'])
                    st.info(f"Modulanzahlen: {counts_str}")
                
                if 'storage_models' in info and info['storage_models']:
                    models_str = ', '.join(str(m) for m in info['storage_models'])
                    st.info(f"🔋 Speichermodelle: {models_str}")
            
            # Vorschau
            if result['preview_df'] is not None:
                st.markdown("---")
                st.markdown("### Vorschau")
                st.dataframe(result['preview_df'], use_container_width=True)


def render_help_section():
    """Rendert Hilfe-Sektion"""
    
    with st.expander("Hilfe: Matrix-Struktur", expanded=False):
        st.markdown("""
        ### Erforderliche Matrix-Struktur
        
        ```
             A              B              C              D
        (Modulanzahl)  (10kWh)        (15kWh)        (Kein Speicher)
        1   Modulanzahl    10kWh          15kWh          Kein Speicher
        2   10             15000.00       17500.00       12000.00
        3   15             18000.00       20500.00       15000.00
        4   20             21000.00       23500.00       18000.00
        ```
        
        ### Validierungsregeln
        
        1. **Erste Spalte (Index):** Numerische Werte (Modulanzahl)
        2. **Spaltenüberschriften:** Text-Werte (Speichermodell-Namen)
        3. **"Ohne Speicher" Spalte:** Mindestens eine Spalte erforderlich
        4. **Preis-Zellen:** Numerische Werte oder leer
        
        ### Unterstützte Formate
        
        - **CSV:** Verschiedene Delimiters (`;`, `,`, `\\t`, `|`)
        - **Excel:** XLSX, XLS
        - **Encoding:** UTF-8, Latin-1, Windows-1252 (automatisch erkannt)
        """)


if __name__ == "__main__":
    main()
