"""
Excel Grid UI - Basis-Komponente

Streamlit UI-Komponente für die Excel-ähnliche Grid-Darstellung.
Bietet Matrix-Auswahl, Toolbar und Grid-Bearbeitung.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

# Import der Excel-Integration Module
try:
    from excel.excel_manager import ExcelManager
    from excel.excel_models import ExcelMatrix, Cell
    from excel.excel_utils import cell_to_a1, a1_to_cell
    from price_matrix_store import (
        list_matrices,
        create_matrix,
        get_matrix_full,
        set_cell_value as db_set_cell_value,
        add_row as db_add_row,
        add_column as db_add_column
    )
    EXCEL_INTEGRATION_AVAILABLE = True
except ImportError as e:
    EXCEL_INTEGRATION_AVAILABLE = False
    print(f"Excel Integration nicht verfügbar: {e}")


def _get_column_label(col_idx: int) -> str:
    """
    Konvertiert Spaltenindex zu Excel-Spaltenbezeichnung (A, B, C, ..., Z, AA, AB, ...)
    
    Args:
        col_idx: Spaltenindex (0-basiert)
        
    Returns:
        Spaltenbezeichnung (z.B. 'A', 'B', 'AA')
    """
    label = ""
    col_idx += 1  # Excel ist 1-basiert
    
    while col_idx > 0:
        col_idx -= 1
        label = chr(65 + (col_idx % 26)) + label
        col_idx //= 26
    
    return label


def _initialize_session_state():
    """Initialisiert Session State für Excel Grid UI"""
    if 'excel_grid_selected_matrix_id' not in st.session_state:
        st.session_state.excel_grid_selected_matrix_id = None
    
    if 'excel_grid_manager' not in st.session_state:
        st.session_state.excel_grid_manager = None
    
    if 'excel_grid_show_formulas' not in st.session_state:
        st.session_state.excel_grid_show_formulas = False
    
    if 'excel_grid_active_cell' not in st.session_state:
        st.session_state.excel_grid_active_cell = None
    
    # Rerun-Loop-Prevention Flag
    if 'excel_grid_rerun_pending' not in st.session_state:
        st.session_state.excel_grid_rerun_pending = False
    
    # Erweiterte Features - Task 10
    if 'excel_grid_clipboard' not in st.session_state:
        st.session_state.excel_grid_clipboard = None
    
    if 'excel_grid_cell_format' not in st.session_state:
        st.session_state.excel_grid_cell_format = {}  # {(row, col): format_type}
    
    if 'excel_grid_keyboard_nav_enabled' not in st.session_state:
        st.session_state.excel_grid_keyboard_nav_enabled = True
    
    # Matrix-Verwaltung Dialoge - Task 11
    if 'excel_grid_show_new_matrix_dialog' not in st.session_state:
        st.session_state.excel_grid_show_new_matrix_dialog = False
    
    if 'excel_grid_show_load_dialog' not in st.session_state:
        st.session_state.excel_grid_show_load_dialog = False
    
    if 'excel_grid_show_clone_dialog' not in st.session_state:
        st.session_state.excel_grid_show_clone_dialog = False
    
    if 'excel_grid_clone_matrix_id' not in st.session_state:
        st.session_state.excel_grid_clone_matrix_id = None
    
    if 'excel_grid_show_rename_dialog' not in st.session_state:
        st.session_state.excel_grid_show_rename_dialog = False
    
    if 'excel_grid_rename_matrix_id' not in st.session_state:
        st.session_state.excel_grid_rename_matrix_id = None
    
    if 'excel_grid_show_delete_confirm' not in st.session_state:
        st.session_state.excel_grid_show_delete_confirm = False
    
    if 'excel_grid_delete_matrix_id' not in st.session_state:
        st.session_state.excel_grid_delete_matrix_id = None
    
    # Auto-Save Funktionalität - Task 12
    if 'excel_grid_auto_save_enabled' not in st.session_state:
        st.session_state.excel_grid_auto_save_enabled = True
    
    if 'excel_grid_auto_save_interval' not in st.session_state:
        st.session_state.excel_grid_auto_save_interval = 60  # Sekunden
    
    if 'excel_grid_last_auto_save' not in st.session_state:
        st.session_state.excel_grid_last_auto_save = None


def _safe_rerun():
    """
    Sicherer Rerun der nur ausgeführt wird, wenn kein Rerun bereits pending ist.
    Verhindert Rerun-Loops und permanentes Blinken.
    """
    if not st.session_state.get('excel_grid_rerun_pending', False):
        st.session_state.excel_grid_rerun_pending = True
        _safe_rerun()


def _reset_rerun_flag():
    """Setzt das Rerun-Flag zurück"""
    if 'excel_grid_rerun_pending' in st.session_state:
        st.session_state.excel_grid_rerun_pending = False
    
    # Import/Export Dialoge - Task 13, 15
    if 'excel_grid_show_import_dialog' not in st.session_state:
        st.session_state.excel_grid_show_import_dialog = False
    
    if 'excel_grid_show_csv_export_dialog' not in st.session_state:
        st.session_state.excel_grid_show_csv_export_dialog = False
    
    if 'excel_grid_show_excel_export_dialog' not in st.session_state:
        st.session_state.excel_grid_show_excel_export_dialog = False
    
    if 'excel_grid_show_export_info' not in st.session_state:
        st.session_state.excel_grid_show_export_info = False
    
    # Hilfe und Validierung - Task 4.2
    if 'excel_grid_show_help_dialog' not in st.session_state:
        st.session_state.excel_grid_show_help_dialog = False
    
    if 'excel_grid_show_validation_dialog' not in st.session_state:
        st.session_state.excel_grid_show_validation_dialog = False
    
    if 'excel_grid_create_example' not in st.session_state:
        st.session_state.excel_grid_create_example = None


def _load_matrix(matrix_id: int) -> Optional[ExcelManager]:
    """
    Lädt eine Matrix aus der Datenbank
    
    Args:
        matrix_id: ID der zu ladenden Matrix
        
    Returns:
        ExcelManager oder None bei Fehler
    """
    try:
        manager = ExcelManager.load_from_database(matrix_id)
        return manager
    except Exception as e:
        st.error(f"Fehler beim Laden der Matrix: {str(e)}")
        return None


def _create_dataframe_from_matrix(manager: ExcelManager, show_formulas: bool = False) -> pd.DataFrame:
    """
    Erstellt ein pandas DataFrame aus einer ExcelMatrix für die Anzeige
    
    Args:
        manager: ExcelManager mit der Matrix
        show_formulas: Ob Formeln statt Werte angezeigt werden sollen
        
    Returns:
        pandas DataFrame
    """
    matrix = manager.get_matrix()
    
    # Erstelle leeres DataFrame mit Spalten A, B, C, ...
    columns = [_get_column_label(i) for i in range(matrix.columns)]
    index = [str(i + 1) for i in range(matrix.rows)]
    
    # Initialisiere mit leeren Strings
    data = [['' for _ in range(matrix.columns)] for _ in range(matrix.rows)]
    
    # Fülle mit Zellwerten und wende Formatierung an (Task 10)
    for (row, col), cell in matrix.cells.items():
        if row < matrix.rows and col < matrix.columns:
            if show_formulas and cell.is_formula():
                data[row][col] = cell.formula
            else:
                # Prüfe ob Zelle formatiert ist
                cell_format = st.session_state.excel_grid_cell_format.get((row, col), "auto")
                
                if cell_format != "auto" and cell.formatted_value:
                    # Verwende formatierte Darstellung
                    data[row][col] = cell.formatted_value
                else:
                    # Verwende Standard-Darstellung
                    data[row][col] = cell.get_display_value()
    
    df = pd.DataFrame(data, columns=columns, index=index)
    return df


def _render_toolbar():
    """Rendert die Toolbar mit Basis-Buttons und erweiterten Features"""
    manager = st.session_state.excel_grid_manager
    
    # Zeige Änderungs-Status
    if manager:
        changes_indicator = _get_unsaved_changes_indicator(manager)
        if manager.has_unsaved_changes:
            st.warning(f"{changes_indicator}Ungespeicherte Änderungen vorhanden")
        else:
            if manager.last_save_time:
                st.success(f"{changes_indicator}Zuletzt gespeichert: {manager.last_save_time.strftime('%H:%M:%S')}")
            else:
                st.info(f"{changes_indicator}Keine Änderungen")
    
    # Erste Zeile: Basis-Operationen
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])
    
    with col1:
        if st.button("➕ Neue Matrix", help="Erstellt eine neue leere Matrix", use_container_width=True):
            st.session_state.excel_grid_show_new_matrix_dialog = True
    
    with col2:
        save_disabled = manager is None or not manager.has_unsaved_changes
        if st.button(
            "💾 Speichern",
            help="Speichert die aktuelle Matrix" if not save_disabled else "Keine Änderungen zum Speichern",
            disabled=save_disabled,
            use_container_width=True,
            type="primary" if manager and manager.has_unsaved_changes else "secondary"
        ):
            if manager:
                _save_matrix_to_database(manager)
    
    with col3:
        if st.button("📂 Laden", help="Lädt eine gespeicherte Matrix", use_container_width=True):
            st.session_state.excel_grid_show_load_dialog = True
    
    with col4:
        manager = st.session_state.excel_grid_manager
        undo_disabled = manager is None or not manager.can_undo()
        if st.button(
            "↶ Undo",
            help="Macht letzte Änderung rückgängig (Strg+Z)",
            disabled=undo_disabled,
            use_container_width=True
        ):
            if manager and manager.undo():
                st.success("Änderung rückgängig gemacht")
                _safe_rerun()
    
    with col5:
        manager = st.session_state.excel_grid_manager
        redo_disabled = manager is None or not manager.can_redo()
        if st.button(
            "↷ Redo",
            help="Wiederholt rückgängig gemachte Änderung (Strg+Y)",
            disabled=redo_disabled,
            use_container_width=True
        ):
            if manager and manager.redo():
                st.success("Änderung wiederhergestellt")
                _safe_rerun()
    
    with col6:
        # Auto-Save Toggle
        auto_save = st.checkbox(
            "🔄 Auto-Save",
            value=st.session_state.excel_grid_auto_save_enabled,
            help=f"Automatisches Speichern alle {st.session_state.excel_grid_auto_save_interval} Sekunden"
        )
        if auto_save != st.session_state.excel_grid_auto_save_enabled:
            st.session_state.excel_grid_auto_save_enabled = auto_save
            if auto_save:
                st.info("Auto-Save aktiviert")
            else:
                st.info("Auto-Save deaktiviert")
        
        # Formel-Anzeige Toggle
        show_formulas = st.checkbox(
            "Formeln anzeigen",
            value=st.session_state.excel_grid_show_formulas,
            help="Zeigt Formeln statt berechneter Werte"
        )
        if show_formulas != st.session_state.excel_grid_show_formulas:
            st.session_state.excel_grid_show_formulas = show_formulas
            _safe_rerun()
    
    # Zweite Zeile: Erweiterte Features (Task 10) + Import/Export (Task 13)
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Copy-Paste Funktionalität
        active_cell = st.session_state.excel_grid_active_cell
        copy_disabled = manager is None or active_cell is None
        if st.button(
            "📋 Kopieren",
            help="Kopiert die aktive Zelle (Strg+C)",
            disabled=copy_disabled,
            use_container_width=True
        ):
            if manager and active_cell:
                _copy_cell(manager, active_cell)
    
    with col2:
        paste_disabled = manager is None or active_cell is None or st.session_state.excel_grid_clipboard is None
        if st.button(
            "📄 Einfügen",
            help="Fügt kopierten Inhalt ein (Strg+V)",
            disabled=paste_disabled,
            use_container_width=True
        ):
            if manager and active_cell and st.session_state.excel_grid_clipboard:
                _paste_cell(manager, active_cell)
                _safe_rerun()
    
    with col3:
        # Zell-Formatierung
        format_disabled = manager is None or active_cell is None
        if not format_disabled and active_cell:
            row, col = active_cell
            current_format = st.session_state.excel_grid_cell_format.get((row, col), "auto")
            
            format_type = st.selectbox(
                "Format",
                options=["auto", "number", "currency", "percentage", "date", "text"],
                index=["auto", "number", "currency", "percentage", "date", "text"].index(current_format),
                help="Formatierung für die aktive Zelle",
                key="cell_format_selector"
            )
            
            if format_type != current_format:
                st.session_state.excel_grid_cell_format[(row, col)] = format_type
                _apply_cell_format(manager, row, col, format_type)
                _safe_rerun()
        else:
            st.selectbox(
                "Format",
                options=["auto"],
                disabled=True,
                help="Wählen Sie eine Zelle aus, um das Format zu ändern"
            )
    
    with col4:
        # Tastaturnavigation Toggle
        keyboard_nav = st.checkbox(
            "⌨️ Tastaturnavigation",
            value=st.session_state.excel_grid_keyboard_nav_enabled,
            help="Aktiviert Tastaturnavigation (Pfeiltasten, Tab, Enter)"
        )
        if keyboard_nav != st.session_state.excel_grid_keyboard_nav_enabled:
            st.session_state.excel_grid_keyboard_nav_enabled = keyboard_nav
    
    with col5:
        # CSV Import Button (Task 13)
        if st.button(
            "📥 CSV Import",
            help="Importiert eine CSV-Datei als neue Matrix",
            use_container_width=True
        ):
            st.session_state.excel_grid_show_import_dialog = True
    
    # Dritte Zeile: Export-Funktionen (Task 15)
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # CSV Export Button
        export_disabled = manager is None
        if st.button(
            "📤 CSV Export",
            help="Exportiert die Matrix als CSV-Datei",
            disabled=export_disabled,
            use_container_width=True
        ):
            if manager:
                st.session_state.excel_grid_show_csv_export_dialog = True
    
    with col2:
        # Excel Export Button
        if st.button(
            "📤 Excel Export",
            help="Exportiert die Matrix als Excel-Datei (XLSX) mit Formeln",
            disabled=export_disabled,
            use_container_width=True
        ):
            if manager:
                st.session_state.excel_grid_show_excel_export_dialog = True
    
    with col3:
        # Export-Vorschau
        if not export_disabled and manager:
            if st.button(
                "👁️ Export-Info",
                help="Zeigt Informationen über den Export",
                use_container_width=True
            ):
                st.session_state.excel_grid_show_export_info = True
    
    with col4:
        # Matrix-Validierung (Task 4.2)
        if st.button(
            "✓ Validieren",
            help="Validiert die Matrix-Struktur für Preisberechnung",
            disabled=export_disabled,
            use_container_width=True
        ):
            if manager:
                st.session_state.excel_grid_show_validation_dialog = True
    
    with col5:
        # Hilfe anzeigen (Task 4.2)
        if st.button(
            "❓ Hilfe",
            help="Zeigt Hilfe zur Matrix-Struktur und Beispiele",
            use_container_width=True
        ):
            st.session_state.excel_grid_show_help_dialog = True
    
    # Vierte Zeile: Beispiel-Matrizen (Task 4.2)
    st.markdown("---")
    st.markdown("**📋 Beispiel-Matrizen erstellen:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button(
            "📊 Kleine Anlage",
            help="Erstellt Beispiel-Matrix für 10-25 Module",
            use_container_width=True
        ):
            st.session_state.excel_grid_create_example = 'small'
    
    with col2:
        if st.button(
            "📊 Mittlere Anlage",
            help="Erstellt Beispiel-Matrix für 30-50 Module",
            use_container_width=True
        ):
            st.session_state.excel_grid_create_example = 'medium'
    
    with col3:
        if st.button(
            "📊 Große Anlage",
            help="Erstellt Beispiel-Matrix für 60-100 Module",
            use_container_width=True
        ):
            st.session_state.excel_grid_create_example = 'large'


def _render_matrix_selector():
    """Rendert die Matrix-Auswahl Dropdown"""
    matrices = list_matrices()
    
    if not matrices:
        st.info("Keine Matrizen vorhanden. Erstellen Sie eine neue Matrix.")
        return None
    
    # Erstelle Optionen für Selectbox
    matrix_options = {f"{m['name']} (ID: {m['id']})": m['id'] for m in matrices}
    
    # Finde aktuell ausgewählte Matrix
    current_selection = None
    if st.session_state.excel_grid_selected_matrix_id:
        for label, mid in matrix_options.items():
            if mid == st.session_state.excel_grid_selected_matrix_id:
                current_selection = label
                break
    
    # Selectbox
    selected_label = st.selectbox(
        "Matrix auswählen",
        options=list(matrix_options.keys()),
        index=list(matrix_options.keys()).index(current_selection) if current_selection else 0,
        help="Wählen Sie eine Matrix zum Bearbeiten aus"
    )
    
    selected_id = matrix_options[selected_label]
    
    # Lade Matrix wenn geändert
    if selected_id != st.session_state.excel_grid_selected_matrix_id:
        st.session_state.excel_grid_selected_matrix_id = selected_id
        st.session_state.excel_grid_manager = _load_matrix(selected_id)
        _safe_rerun()
    
    return selected_id


def _render_formula_bar():
    """
    Rendert die Formelleiste mit Zellreferenz-Anzeige und Eingabefeld
    
    Die Formelleiste zeigt:
    - Aktive Zellreferenz (z.B. A1)
    - Formel oder Wert der aktiven Zelle
    - Eingabefeld zur Bearbeitung
    - Fehleranzeige bei ungültigen Formeln
    """
    manager = st.session_state.excel_grid_manager
    
    if manager is None:
        st.info("💡 Wählen Sie eine Matrix aus, um die Formelleiste zu nutzen")
        st.text_input(
            "Formelleiste",
            value="",
            disabled=True,
            help="Wählen Sie eine Matrix aus, um die Formelleiste zu nutzen",
            label_visibility="collapsed"
        )
        return
    
    # Zeige aktive Zelle und Formel/Wert
    active_cell = st.session_state.excel_grid_active_cell
    
    if active_cell:
        row, col = active_cell
        cell = manager.get_cell(row, col)
        cell_ref = cell_to_a1(row, col)
        
        # Container für Zellreferenz und Fehleranzeige
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Zeige Zellreferenz prominent
            st.markdown(f"### 📍 {cell_ref}")
            
            # Zeige Zelltyp mit visueller Unterscheidung (Task 3.3)
            if cell.is_formula():
                st.markdown("🔢 **Formel**")
            elif cell.is_error():
                st.markdown("⚠️ **Fehler**")
            elif cell.data_type == "number":
                st.markdown("🔢 **Zahl**")
            elif cell.data_type == "text":
                st.markdown("📝 **Text**")
            else:
                st.markdown("📄 **Wert**")
        
        with col2:
            # Zeige Fehler falls vorhanden mit vollständigem Tooltip
            if cell.is_error():
                st.error(f"**Fehler:** {cell.error}")
                
                # Zeige vollständigen Tooltip mit Lösungen
                error_tooltip = _get_error_tooltip_full(cell.error)
                
                with st.expander("🔍 Fehlerdetails & Lösungen", expanded=True):
                    st.markdown(f"**{error_tooltip['title']}**")
                    st.caption(error_tooltip['description'])
                    
                    st.markdown("**💡 Lösungsvorschläge:**")
                    for i, solution in enumerate(error_tooltip['solutions'], 1):
                        st.caption(f"{i}. {solution}")
        
        # Zeige Formel oder Wert - IMMER die ursprüngliche Eingabe anzeigen
        # WICHTIG: Auch bei Fehlern die Formel anzeigen!
        if cell.is_formula() or (cell.is_error() and cell.formula):
            # Bei Formeln (auch mit Fehler): Zeige die Formel (mit =)
            formula_value = cell.formula if cell.formula else ""
            input_label = "Formel" + (" (Fehler)" if cell.is_error() else "")
            input_help = "Bearbeiten Sie die Formel. Beginnen Sie mit '=' für Formeln."
            input_placeholder = "=SUM(A1:A10)"
        elif cell.raw_input:
            # Wenn raw_input vorhanden ist, zeige das (ursprüngliche Eingabe)
            formula_value = cell.raw_input
            # Task 3.3: Unterschiedliche Hinweise für Text vs. Zahlen
            if cell.data_type == "text":
                input_label = "Text-Wert"
                input_help = "Text wird ohne Formatierung gespeichert. Für Formeln beginnen Sie mit '='"
                input_placeholder = "Text eingeben (z.B. Speichermodell-Name)"
            elif cell.data_type == "number":
                input_label = "Zahlen-Wert"
                input_help = "Zahlen können in Berechnungen verwendet werden. Komma oder Punkt als Dezimaltrennzeichen."
                input_placeholder = "Zahl eingeben (z.B. 15000 oder 15000.50)"
            else:
                input_label = "Wert"
                input_help = "Geben Sie Text, Zahl oder Formel (beginnend mit =) ein"
                input_placeholder = "Wert eingeben"
        else:
            # Sonst zeige den berechneten Wert
            display_val = cell.get_display_value()
            formula_value = str(display_val) if display_val is not None else ""
            input_label = "Wert"
            input_help = "Geben Sie Text, Zahl oder Formel (beginnend mit =) ein"
            input_placeholder = "Wert eingeben"
        
        # Zeige aktuelle Formel/Wert prominent in einem Info-Container (Task 3.3: mit Typ-Kennzeichnung)
        if cell.is_formula():
            st.info(f"📝 **Aktuelle Formel:** `{formula_value}`")
        elif formula_value:
            if cell.data_type == "text":
                st.info(f"📝 **Aktueller Text:** `{formula_value}`")
            elif cell.data_type == "number":
                st.info(f"🔢 **Aktuelle Zahl:** `{formula_value}`")
            else:
                st.info(f"📝 **Aktueller Wert:** `{formula_value}`")
        
        # Eingabefeld für Formel/Wert mit Validierung
        col1, col2 = st.columns([5, 1])
        
        with col1:
            new_value = st.text_input(
                input_label,
                value=formula_value,
                key=f"formula_bar_{cell_ref}",
                help=input_help,
                placeholder=input_placeholder  # Task 3.3: Dynamischer Platzhalter basierend auf Typ
            )
        
        with col2:
            # Button zum Übernehmen der Änderung
            if st.button("✓ Übernehmen", key=f"apply_{cell_ref}", use_container_width=True):
                if new_value != formula_value:
                    # Validiere und aktualisiere Zelle mit umfassender Fehlerbehandlung
                    validation_result = _validate_cell_input(new_value)
                    
                    if validation_result['valid']:
                        # Prüfe auf Zirkelbezüge bei Formeln
                        if validation_result['type'] == 'formula':
                            circular_check = _check_circular_reference(manager, row, col, new_value)
                            if circular_check['has_circular']:
                                st.error(f"⚠️ Zirkelbezug erkannt: {circular_check['message']}")
                                
                                # Zeige Zirkel-Pfad
                                if circular_check['path']:
                                    st.caption("**Zirkel-Pfad:**")
                                    path_str = " → ".join([cell_to_a1(r, c) for r, c in circular_check['path']])
                                    st.caption(path_str)
                                
                                # Zeige Lösungsvorschläge
                                error_tooltip = _get_error_tooltip_full('#CIRCULAR!')
                                with st.expander("💡 Lösungsvorschläge"):
                                    for solution in error_tooltip['solutions']:
                                        st.caption(f"• {solution}")
                                return
                        
                        # Aktualisiere Zelle
                        _update_cell_value(manager, row, col, new_value)
                        
                        # WICHTIG: Speichere IMMER in Datenbank, damit Änderungen beim Neuladen erhalten bleiben
                        _save_matrix_to_database(manager)
                        
                        st.success(f"✓ Zelle {cell_ref} aktualisiert und gespeichert")
                        
                        # Zeige Warnung falls vorhanden
                        if validation_result.get('warning'):
                            st.warning(f"⚠️ {validation_result['warning']}")
                            if validation_result.get('suggestions'):
                                with st.expander("💡 Vorschläge"):
                                    for suggestion in validation_result['suggestions']:
                                        st.caption(f"• {suggestion}")
                        
                        _safe_rerun()
                    else:
                        # Zeige Validierungsfehler mit Details
                        st.error(f"⚠️ Validierungsfehler: {validation_result['error']}")
                        
                        # Zeige Fehlercode falls vorhanden
                        if validation_result.get('error_code'):
                            st.caption(f"Fehlercode: {validation_result['error_code']}")
                        
                        # Zeige Vorschläge
                        if validation_result.get('suggestions'):
                            with st.expander("💡 Verbesserungsvorschläge", expanded=True):
                                for i, suggestion in enumerate(validation_result['suggestions'], 1):
                                    st.caption(f"{i}. {suggestion}")
        
        # Zeige berechneten Wert bei Formeln
        if cell.is_formula() and not cell.is_error():
            st.caption(f"**Berechneter Wert:** {cell.get_display_value()}")
        
        # Zeige Abhängigkeiten
        if cell.is_formula():
            with st.expander("🔗 Formel-Details"):
                _show_formula_details(manager, cell, cell_ref)
    
    else:
        st.info("💡 Klicken Sie auf eine Zelle im Grid, um sie zu bearbeiten")
        st.text_input(
            "Formelleiste",
            value="",
            disabled=True,
            help="Klicken Sie auf eine Zelle, um sie zu bearbeiten",
            label_visibility="collapsed"
        )


def _render_grid():
    """
    Rendert das Excel-Grid mit Streamlit Data Editor
    
    Features:
    - Zeigt Zellwerte oder Formeln an
    - Markiert Fehler farblich
    - Ermöglicht direkte Bearbeitung
    - Zeigt Matrix-Statistiken
    """
    manager = st.session_state.excel_grid_manager
    
    if manager is None:
        st.info("Keine Matrix geladen. Wählen Sie eine Matrix aus oder erstellen Sie eine neue.")
        return
    
    # Erstelle DataFrame
    show_formulas = st.session_state.excel_grid_show_formulas
    df = _create_dataframe_from_matrix(manager, show_formulas)
    
    # Zeige Matrix-Informationen
    info = manager.get_matrix_info()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Zeilen", info['rows'])
    with col2:
        st.metric("Spalten", info['columns'])
    with col3:
        st.metric("Zellen mit Werten", info['cell_count'])
    with col4:
        st.metric("Formeln", info['formula_count'])
    
    st.markdown("---")
    
    # Zeilen/Spalten Buttons - Erweitert (Task 10)
    st.subheader("Zeilen & Spalten verwalten")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Zeile hinzufügen mit Position
        st.markdown("**Zeile hinzufügen**")
        row_position = st.number_input(
            "Position",
            min_value=1,
            max_value=info['rows'] + 1,
            value=info['rows'] + 1,
            step=1,
            key="add_row_position",
            help="Position, an der die neue Zeile eingefügt wird"
        )
        if st.button("➕ Zeile hinzufügen", use_container_width=True, help="Fügt eine neue Zeile an der angegebenen Position ein"):
            manager.add_row(position=row_position - 1)  # 0-basiert
            st.success(f"✓ Zeile an Position {row_position} hinzugefügt")
            _safe_rerun()
    
    with col2:
        # Spalte hinzufügen mit Position
        st.markdown("**Spalte hinzufügen**")
        col_position = st.number_input(
            "Position",
            min_value=1,
            max_value=info['columns'] + 1,
            value=info['columns'] + 1,
            step=1,
            key="add_col_position",
            help="Position, an der die neue Spalte eingefügt wird"
        )
        if st.button("➕ Spalte hinzufügen", use_container_width=True, help="Fügt eine neue Spalte an der angegebenen Position ein"):
            manager.add_column(position=col_position - 1)  # 0-basiert
            st.success(f"✓ Spalte an Position {col_position} hinzugefügt")
            _safe_rerun()
    
    with col3:
        # Zeile löschen
        st.markdown("**Zeile löschen**")
        row_to_delete = st.number_input(
            "Zeile",
            min_value=1,
            max_value=info['rows'],
            value=1,
            step=1,
            key="delete_row_input",
            help="Zeilennummer, die gelöscht werden soll"
        )
        if st.button("🗑️ Zeile löschen", use_container_width=True, help="Löscht die angegebene Zeile und passt Formeln an"):
            if info['rows'] > 1:
                manager.delete_row(row_to_delete - 1)  # 0-basiert
                st.success(f"✓ Zeile {row_to_delete} gelöscht")
                _safe_rerun()
            else:
                st.error("Mindestens eine Zeile muss vorhanden sein")
    
    with col4:
        # Spalte löschen
        st.markdown("**Spalte löschen**")
        col_to_delete = st.selectbox(
            "Spalte",
            options=[_get_column_label(i) for i in range(info['columns'])],
            key="delete_col_input",
            help="Spalte, die gelöscht werden soll"
        )
        if st.button("🗑️ Spalte löschen", use_container_width=True, help="Löscht die angegebene Spalte und passt Formeln an"):
            if info['columns'] > 1:
                col_idx = ord(col_to_delete[0]) - 65  # A=0, B=1, ...
                manager.delete_column(col_idx)
                st.success(f"✓ Spalte {col_to_delete} gelöscht")
                _safe_rerun()
            else:
                st.error("Mindestens eine Spalte muss vorhanden sein")
    
    st.markdown("---")
    
    # Cell Selection Interface mit Tastaturnavigation (Task 10)
    st.subheader("Zell-Auswahl & Navigation")
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        # Zellreferenz-Eingabe
        cell_ref_input = st.text_input(
            "Zelle auswählen",
            value="A1",
            key="cell_ref_input",
            help="Geben Sie eine Zellreferenz ein (z.B. A1, B5) oder nutzen Sie die Navigationstasten"
        )
    
    with col2:
        if st.button("📍 Zelle auswählen", use_container_width=True, help="Springt zur angegebenen Zelle"):
            try:
                from excel.excel_utils import a1_to_cell
                row, col = a1_to_cell(cell_ref_input)
                if row < info['rows'] and col < info['columns']:
                    st.session_state.excel_grid_active_cell = (row, col)
                    st.success(f"✓ Zelle {cell_ref_input} ausgewählt")
                    _safe_rerun()
                else:
                    st.error(f"Zelle {cell_ref_input} existiert nicht in dieser Matrix")
            except Exception as e:
                st.error(f"Ungültige Zellreferenz: {str(e)}")
    
    with col3:
        # Zeige aktive Zelle mit Format-Info
        if st.session_state.excel_grid_active_cell:
            row, col = st.session_state.excel_grid_active_cell
            cell = manager.get_cell(row, col)
            active_ref = cell_to_a1(row, col)
            cell_format = st.session_state.excel_grid_cell_format.get((row, col), "auto")
            
            if cell.is_error():
                st.error(f"📍 {active_ref} - ⚠️ {cell.error}")
            elif cell.is_formula():
                st.info(f"📍 {active_ref} - 🔢 Formel ({cell_format})")
            else:
                st.success(f"📍 {active_ref} - 📄 {cell_format}")
    
    # Tastaturnavigation (Task 10)
    if st.session_state.excel_grid_keyboard_nav_enabled:
        st.markdown("**⌨️ Tastaturnavigation:**")
        nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
        
        with nav_col1:
            if st.button("⬆️", use_container_width=True, help="Nach oben (↑)"):
                _navigate_cell(manager, 'up')
                _safe_rerun()
        
        with nav_col2:
            if st.button("⬇️", use_container_width=True, help="Nach unten (↓)"):
                _navigate_cell(manager, 'down')
                _safe_rerun()
        
        with nav_col3:
            if st.button("⬅️", use_container_width=True, help="Nach links (←)"):
                _navigate_cell(manager, 'left')
                _safe_rerun()
        
        with nav_col4:
            if st.button("➡️", use_container_width=True, help="Nach rechts (→)"):
                _navigate_cell(manager, 'right')
                _safe_rerun()
        
        with nav_col5:
            if st.button("↵ Enter", use_container_width=True, help="Nächste Zeile (Enter)"):
                _navigate_cell(manager, 'enter')
                _safe_rerun()
    
    st.markdown("---")
    
    # Data Editor mit erweiterten Features (Task 10)
    st.subheader("Excel Grid")
    
    # Zeige erweiterte Legende mit Tooltips (Task 21)
    with st.expander("📖 Legende & Hilfe", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Fehler-Codes:**")
            
            # Zeige alle Fehlertypen mit Tooltips
            error_codes = ['#ERROR!', '#REF!', '#DIV/0!', '#CIRCULAR!', '#NAME?', '#VALUE!', '#NUM!', '#N/A', '#NULL!']
            
            for error_code in error_codes:
                error_tooltip = _get_error_tooltip_full(error_code)
                with st.expander(f"`{error_code}` - {error_tooltip['title']}", expanded=False):
                    st.caption(error_tooltip['description'])
                    st.markdown("**Lösungen:**")
                    for solution in error_tooltip['solutions'][:2]:  # Zeige nur erste 2 Lösungen
                        st.caption(f"• {solution}")
            
            st.markdown("---")
            st.markdown("""
            **Zell-Formatierung:**
            - **Auto** - Automatische Erkennung
            - **Zahl** - Dezimalzahl (z.B. 123.45)
            - **Währung** - Betrag in Euro (z.B. 1.234,56 €)
            - **Prozent** - Prozentwert (z.B. 12.34%)
            - **Datum** - Datumsformat (z.B. 31.12.2023)
            - **Text** - Textformat
            """)
        
        with col2:
            st.markdown("""
            **Bedienung:**
            - Doppelklicken Sie auf eine Zelle zum Bearbeiten
            - Beginnen Sie mit `=` für Formeln
            - Verwenden Sie A1-Notation für Zellreferenzen
            - Verwenden Sie `:` für Bereiche (z.B. A1:A10)
            
            **Tastenkombinationen:**
            - `Strg+C` - Kopieren (oder Button)
            - `Strg+V` - Einfügen (oder Button)
            - `Strg+Z` - Rückgängig (oder Button)
            - `Strg+Y` - Wiederholen (oder Button)
            - `↑↓←→` - Navigation (oder Buttons)
            - `Enter` - Nächste Zeile
            - `Tab` - Nächste Spalte
            """)
    
    # Konfiguration für Data Editor mit erweiterten Tooltips (Task 10)
    column_config = {}
    for col_idx, col in enumerate(df.columns):
        # Erstelle hilfreichen Tooltip mit Spalten-Info
        col_letter = col
        col_info = f"Spalte {col_letter}"
        
        # Zähle Zellen mit Werten in dieser Spalte
        mat = manager.get_matrix()
        non_empty = sum(1 for row in range(mat.rows) if mat.cells.get((row, col_idx)) and mat.cells.get((row, col_idx)).value is not None)
        if non_empty > 0:
            col_info += f" ({non_empty} Werte)"
        
        column_config[col] = st.column_config.TextColumn(
            col,
            help=col_info,
            max_chars=1000,
            width="medium"
        )
    
    # Zeige Data Editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config=column_config,
        hide_index=False,
        key="excel_grid_editor"
    )
    
    # Prüfe auf Änderungen und aktualisiere Matrix
    if not df.equals(edited_df):
        _update_matrix_from_dataframe(manager, edited_df)
        st.success("Änderungen gespeichert")
        _safe_rerun()
    
    # Zeige Fehler-Zusammenfassung
    error_cells = _get_error_cells(manager)
    if error_cells:
        st.markdown("---")
        st.warning(f"⚠️ {len(error_cells)} Zelle(n) mit Fehlern")
        
        with st.expander("Fehler anzeigen"):
            for row, col, error in error_cells:
                cell_ref = cell_to_a1(row, col)
                cell = manager.get_cell(row, col)
                st.markdown(f"**{cell_ref}:** {error}")
                if cell.is_formula():
                    st.caption(f"Formel: `{cell.formula}`")
                error_help = _get_error_help(error)
                if error_help:
                    st.caption(f"💡 {error_help}")


def _validate_cell_input(value: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Validiert Benutzereingabe für eine Zelle mit umfassender Fehlerbehandlung
    
    Args:
        value: Zu validierender Wert
        expected_type: Erwarteter Typ (optional)
        
    Returns:
        Dictionary mit Validierungsergebnis
    """
    from excel.excel_validation import ExcelValidator
    
    validator = ExcelValidator()
    result = validator.validate_cell_input(value, expected_type)
    
    return result.to_dict()


def _validate_cell_input_mixed(value: str) -> Dict[str, Any]:
    """
    Validiert Zell-Eingabe für gemischte Text/Zahlen-Eingabe ohne Zwangskonvertierung
    
    Diese Funktion ist speziell für die Preismatrix-Erweiterung (Task 3.1) und erlaubt:
    - Text-Eingabe ohne automatische Zahlen-Konvertierung
    - Zahlen-Eingabe mit korrekter Typ-Erkennung
    - Formeln mit '=' Präfix
    
    Args:
        value: Zu validierender Wert (String)
        
    Returns:
        Dictionary mit:
        - 'valid': bool - Ob die Eingabe gültig ist
        - 'type': str - Erkannter Typ ('text', 'number', 'formula', 'empty')
        - 'value': Any - Geparster Wert (bei Zahlen: float, sonst: str)
        - 'error': str | None - Fehlermeldung falls ungültig
    """
    # Leere Eingabe
    if not value or value.strip() == "":
        return {
            'valid': True,
            'type': 'empty',
            'value': None,
            'error': None
        }
    
    value = value.strip()
    
    # Formel-Erkennung (beginnt mit '=')
    if value.startswith('='):
        # Verwende bestehende Formel-Validierung
        from excel.excel_validation import ExcelValidator
        validator = ExcelValidator()
        result = validator.validate_formula(value)
        
        return {
            'valid': result.valid,
            'type': 'formula',
            'value': value,
            'error': result.error
        }
    
    # Zahlen-Erkennung: Versuche als Zahl zu parsen
    # Aber NUR wenn es wirklich wie eine Zahl aussieht
    # (keine Buchstaben außer am Ende für Einheiten)
    try:
        # Normalisiere Dezimaltrennzeichen
        value_normalized = value.replace(',', '.')
        
        # Entferne Tausendertrennzeichen (Leerzeichen)
        value_normalized = value_normalized.replace(' ', '')
        
        # Versuche zu parsen
        parsed_number = float(value_normalized)
        
        # Erfolgreich geparst -> Es ist eine Zahl
        return {
            'valid': True,
            'type': 'number',
            'value': parsed_number,
            'error': None
        }
    except ValueError:
        # Konnte nicht als Zahl geparst werden -> Es ist Text
        pass
    
    # Text-Eingabe (alles was keine Formel oder Zahl ist)
    # WICHTIG: Keine Validierung oder Konvertierung!
    # Text wird so akzeptiert wie eingegeben
    return {
        'valid': True,
        'type': 'text',
        'value': value,  # Original-String beibehalten
        'error': None
    }


def _get_error_help(error_code: str) -> Optional[str]:
    """
    Gibt Hilfetext für einen Fehlercode zurück
    
    Args:
        error_code: Fehlercode (z.B. "#DIV/0!")
        
    Returns:
        Hilfetext oder None
    """
    from excel.excel_validation import get_error_tooltip
    
    tooltip = get_error_tooltip(error_code)
    return tooltip['description']


def _get_error_tooltip_full(error_code: str) -> Dict[str, Any]:
    """
    Gibt vollständige Tooltip-Informationen für einen Fehlercode zurück
    
    Args:
        error_code: Fehlercode (z.B. "#DIV/0!")
        
    Returns:
        Dictionary mit 'title', 'description', 'solutions'
    """
    from excel.excel_validation import get_error_tooltip
    
    return get_error_tooltip(error_code)


def _show_formula_details(manager: ExcelManager, cell: Cell, cell_ref: str):
    """
    Zeigt Details zu einer Formel an
    
    Args:
        manager: ExcelManager
        cell: Cell-Objekt
        cell_ref: Zellreferenz (z.B. "A1")
    """
    if not cell.is_formula():
        return
    
    try:
        # Extrahiere Zellreferenzen aus der Formel
        from excel.excel_utils import extract_cell_references
        
        refs = extract_cell_references(cell.formula)
        
        if refs:
            st.markdown("**Referenzierte Zellen:**")
            
            # Zeige Referenzen mit ihren Werten
            for ref in refs:
                if ':' in ref:
                    # Bereich
                    st.caption(f"- {ref} (Bereich)")
                else:
                    # Einzelne Zelle
                    try:
                        from excel.excel_utils import a1_to_cell
                        ref_row, ref_col = a1_to_cell(ref)
                        ref_cell = manager.get_cell(ref_row, ref_col)
                        ref_value = ref_cell.get_display_value()
                        st.caption(f"- {ref} = {ref_value}")
                    except Exception:
                        st.caption(f"- {ref}")
        else:
            st.caption("Keine Zellreferenzen")
        
        # Zeige abhängige Zellen
        dependents = manager.formula_engine.get_dependent_cells((cell.row, cell.col))
        if dependents:
            st.markdown("**Abhängige Zellen:**")
            for dep_row, dep_col in dependents:
                dep_ref = cell_to_a1(dep_row, dep_col)
                st.caption(f"- {dep_ref}")
        else:
            st.caption("Keine abhängigen Zellen")
            
    except Exception as e:
        st.caption(f"Fehler beim Laden der Details: {str(e)}")


def _check_circular_reference(
    manager: ExcelManager,
    row: int,
    col: int,
    formula: str
) -> Dict[str, Any]:
    """
    Prüft ob eine Formel einen Zirkelbezug erstellen würde
    
    Args:
        manager: ExcelManager
        row: Zeilennummer (0-basiert)
        col: Spaltennummer (0-basiert)
        formula: Zu prüfende Formel
        
    Returns:
        Dictionary mit:
        - 'has_circular': bool - Ob Zirkelbezug vorhanden
        - 'message': str - Fehlermeldung
        - 'path': List - Pfad des Zirkelbezugs
    """
    from excel.excel_validation import CircularReferenceDetector
    
    try:
        detector = CircularReferenceDetector()
        detector.build_graph(manager.get_matrix().cells)
        
        circular_path = detector.detect_circular_reference((row, col), formula)
        
        if circular_path:
            path_str = " → ".join([cell_to_a1(r, c) for r, c in circular_path])
            return {
                'has_circular': True,
                'message': f"Die Formel würde einen Zirkelbezug erstellen: {path_str}",
                'path': circular_path
            }
        
        return {
            'has_circular': False,
            'message': None,
            'path': None
        }
        
    except Exception as e:
        # Bei Fehler: Vorsichtshalber als Zirkelbezug behandeln
        return {
            'has_circular': True,
            'message': f"Fehler bei Zirkelbezug-Prüfung: {str(e)}",
            'path': None
        }


def _update_cell_value(manager: ExcelManager, row: int, col: int, value: str):
    """
    Aktualisiert den Wert einer Zelle mit Validierung
    
    Verwendet die neue _validate_cell_input_mixed() Funktion für korrekte
    Text/Zahlen-Erkennung ohne Zwangskonvertierung (Task 3.2).
    
    Args:
        manager: ExcelManager
        row: Zeilennummer (0-basiert)
        col: Spaltennummer (0-basiert)
        value: Neuer Wert
    """
    try:
        # Verwende neue gemischte Validierung (Task 3.1)
        validation_result = _validate_cell_input_mixed(value)
        
        if not validation_result['valid']:
            st.error(f"Ungültige Eingabe: {validation_result['error']}")
            return
        
        # Setze Wert basierend auf erkanntem Typ
        input_type = validation_result['type']
        parsed_value = validation_result['value']
        
        if input_type == 'formula':
            # Formel: raw_input enthält die Formel, value wird berechnet
            manager.set_cell_value(row, col, None, raw_input=value)
        elif input_type == 'number':
            # Zahl: Speichere als numerischen Wert
            manager.set_cell_value(row, col, parsed_value, raw_input=value)
        elif input_type == 'text':
            # Text: Speichere als String OHNE Konvertierung
            # WICHTIG: raw_input behält die ursprüngliche Eingabe
            manager.set_cell_value(row, col, parsed_value, raw_input=value)
        elif input_type == 'empty':
            # Leere Zelle
            manager.clear_cell(row, col, save_undo=False)
        
    except Exception as e:
        st.error(f"Fehler beim Aktualisieren der Zelle: {str(e)}")


def _get_error_cells(manager: ExcelManager) -> List[Tuple[int, int, str]]:
    """
    Gibt alle Zellen mit Fehlern zurück
    
    Args:
        manager: ExcelManager
        
    Returns:
        Liste von Tupeln (row, col, error_message)
    """
    error_cells = []
    matrix = manager.get_matrix()
    
    for (row, col), cell in matrix.cells.items():
        if cell.is_error():
            error_cells.append((row, col, cell.error))
    
    return error_cells


def _update_matrix_from_dataframe(manager: ExcelManager, df: pd.DataFrame):
    """
    Aktualisiert die Matrix aus einem bearbeiteten DataFrame
    
    Args:
        manager: ExcelManager
        df: Bearbeitetes DataFrame
    """
    # Iteriere über alle Zellen im DataFrame
    for row_idx, row_label in enumerate(df.index):
        for col_idx, col_label in enumerate(df.columns):
            value = df.iloc[row_idx, col_idx]
            
            # Überspringe leere Zellen
            if pd.isna(value) or value == '':
                continue
            
            # Aktualisiere Zelle
            _update_cell_value(manager, row_idx, col_idx, str(value))


def _copy_cell(manager: ExcelManager, cell_pos: Tuple[int, int]):
    """
    Kopiert eine Zelle in die Zwischenablage
    
    Args:
        manager: ExcelManager
        cell_pos: Position der zu kopierenden Zelle (row, col)
    """
    row, col = cell_pos
    cell = manager.get_cell(row, col)
    
    # Speichere Zellinhalt in Session State
    st.session_state.excel_grid_clipboard = {
        'value': cell.value,
        'formula': cell.formula,
        'raw_input': cell.raw_input,
        'data_type': cell.data_type,
        'format': st.session_state.excel_grid_cell_format.get((row, col), "auto")
    }
    
    cell_ref = cell_to_a1(row, col)
    st.success(f"✓ Zelle {cell_ref} kopiert")


def _paste_cell(manager: ExcelManager, cell_pos: Tuple[int, int]):
    """
    Fügt kopierten Inhalt in eine Zelle ein
    
    Args:
        manager: ExcelManager
        cell_pos: Zielposition (row, col)
    """
    if not st.session_state.excel_grid_clipboard:
        st.warning("Keine Daten in der Zwischenablage")
        return
    
    row, col = cell_pos
    clipboard = st.session_state.excel_grid_clipboard
    
    # Füge Inhalt ein
    if clipboard['formula']:
        # Formel einfügen (mit relativen Referenzen)
        manager.set_cell_value(row, col, None, raw_input=clipboard['formula'])
    else:
        manager.set_cell_value(row, col, clipboard['value'], raw_input=clipboard['raw_input'])
    
    # Übernehme Format
    if clipboard['format'] != "auto":
        st.session_state.excel_grid_cell_format[(row, col)] = clipboard['format']
    
    cell_ref = cell_to_a1(row, col)
    st.success(f"✓ Inhalt in Zelle {cell_ref} eingefügt")


def _apply_cell_format(manager: ExcelManager, row: int, col: int, format_type: str):
    """
    Wendet Formatierung auf eine Zelle an
    
    Args:
        manager: ExcelManager
        row: Zeilennummer
        col: Spaltennummer
        format_type: Format-Typ ('auto', 'number', 'currency', 'percentage', 'date', 'text')
    """
    cell = manager.get_cell(row, col)
    
    # Formatiere Wert basierend auf Typ
    if cell.value is not None and not cell.is_formula():
        try:
            if format_type == "number":
                # Formatiere als Zahl mit 2 Dezimalstellen
                if isinstance(cell.value, (int, float)):
                    cell.formatted_value = f"{cell.value:.2f}"
                else:
                    cell.formatted_value = str(cell.value)
            
            elif format_type == "currency":
                # Formatiere als Währung
                if isinstance(cell.value, (int, float)):
                    cell.formatted_value = f"{cell.value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    cell.formatted_value = str(cell.value)
            
            elif format_type == "percentage":
                # Formatiere als Prozent
                if isinstance(cell.value, (int, float)):
                    cell.formatted_value = f"{cell.value * 100:.2f}%"
                else:
                    cell.formatted_value = str(cell.value)
            
            elif format_type == "date":
                # Formatiere als Datum
                from datetime import datetime
                if isinstance(cell.value, datetime):
                    cell.formatted_value = cell.value.strftime("%d.%m.%Y")
                elif isinstance(cell.value, str):
                    try:
                        date_obj = datetime.strptime(cell.value, "%Y-%m-%d")
                        cell.formatted_value = date_obj.strftime("%d.%m.%Y")
                    except:
                        cell.formatted_value = str(cell.value)
                else:
                    cell.formatted_value = str(cell.value)
            
            elif format_type == "text":
                # Formatiere als Text
                cell.formatted_value = str(cell.value)
            
            else:  # auto
                cell.formatted_value = None
            
            cell_ref = cell_to_a1(row, col)
            st.success(f"✓ Format '{format_type}' auf Zelle {cell_ref} angewendet")
            
        except Exception as e:
            st.error(f"Fehler beim Formatieren: {str(e)}")


def _navigate_cell(manager: ExcelManager, direction: str):
    """
    Navigiert zu einer benachbarten Zelle
    
    Args:
        manager: ExcelManager
        direction: Richtung ('up', 'down', 'left', 'right', 'tab', 'enter')
    """
    if not st.session_state.excel_grid_active_cell:
        # Starte bei A1
        st.session_state.excel_grid_active_cell = (0, 0)
        return
    
    row, col = st.session_state.excel_grid_active_cell
    matrix = manager.get_matrix()
    
    # Berechne neue Position
    if direction == 'up':
        row = max(0, row - 1)
    elif direction == 'down':
        row = min(matrix.rows - 1, row + 1)
    elif direction == 'left':
        col = max(0, col - 1)
    elif direction == 'right' or direction == 'tab':
        col = min(matrix.columns - 1, col + 1)
    elif direction == 'enter':
        row = min(matrix.rows - 1, row + 1)
    
    st.session_state.excel_grid_active_cell = (row, col)


def _save_matrix_to_database(manager: ExcelManager, show_success: bool = True) -> bool:
    """
    Speichert die Matrix in die Datenbank
    
    Args:
        manager: ExcelManager mit zu speichernder Matrix
        show_success: Ob Erfolgsmeldung angezeigt werden soll
        
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        success = manager.save_to_database()
        
        if success:
            if show_success:
                matrix = manager.get_matrix()
                st.success(f"✓ Matrix '{matrix.name}' erfolgreich gespeichert!")
            return True
        else:
            st.error("Fehler beim Speichern der Matrix")
            return False
        
    except Exception as e:
        st.error(f"Fehler beim Speichern: {str(e)}")
        return False


def _auto_save_matrix(manager: ExcelManager):
    """
    Führt Auto-Save durch wenn aktiviert und Änderungen vorhanden
    
    Args:
        manager: ExcelManager mit zu speichernder Matrix
    """
    if not st.session_state.excel_grid_auto_save_enabled:
        return
    
    if not manager or not manager.has_unsaved_changes:
        return
    
    # Prüfe ob Auto-Save-Intervall abgelaufen ist
    now = datetime.now()
    last_save = st.session_state.excel_grid_last_auto_save
    
    if last_save is None:
        # Erster Auto-Save
        should_save = True
    else:
        # Prüfe Intervall
        elapsed = (now - last_save).total_seconds()
        should_save = elapsed >= st.session_state.excel_grid_auto_save_interval
    
    if should_save:
        success = _save_matrix_to_database(manager, show_success=False)
        if success:
            st.session_state.excel_grid_last_auto_save = now
            # Zeige dezente Info-Meldung
            st.caption(f"🔄 Auto-Save: {now.strftime('%H:%M:%S')}")


def _get_unsaved_changes_indicator(manager: ExcelManager) -> str:
    """
    Gibt einen Indikator für ungespeicherte Änderungen zurück
    
    Args:
        manager: ExcelManager
        
    Returns:
        String mit Indikator
    """
    if not manager:
        return ""
    
    if manager.has_unsaved_changes:
        return "● "  # Roter Punkt für ungespeicherte Änderungen
    else:
        return "✓ "  # Häkchen für gespeichert


def _render_new_matrix_dialog():
    """Rendert den Dialog zum Erstellen einer neuen Matrix"""
    if not st.session_state.get('excel_grid_show_new_matrix_dialog', False):
        return
    
    with st.form("new_matrix_form"):
        st.subheader("Neue Matrix erstellen")
        
        name = st.text_input(
            "Name",
            value=f"Matrix {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            help="Name der neuen Matrix"
        )
        
        description = st.text_area(
            "Beschreibung",
            value="",
            help="Optionale Beschreibung"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            rows = st.number_input("Anzahl Zeilen", min_value=10, max_value=1000, value=100)
        with col2:
            cols = st.number_input("Anzahl Spalten", min_value=5, max_value=100, value=26)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Erstellen", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if submitted:
            try:
                # Erstelle Matrix in Datenbank
                matrix_id = create_matrix(name, description)
                
                if matrix_id:
                    # Füge Zeilen und Spalten hinzu
                    for i in range(rows):
                        db_add_row(matrix_id, str(i + 1))
                    
                    for i in range(cols):
                        db_add_column(matrix_id, _get_column_label(i))
                    
                    st.success(f"Matrix '{name}' erfolgreich erstellt!")
                    st.session_state.excel_grid_show_new_matrix_dialog = False
                    st.session_state.excel_grid_selected_matrix_id = matrix_id
                    st.session_state.excel_grid_manager = _load_matrix(matrix_id)
                    _safe_rerun()
                else:
                    st.error("Fehler beim Erstellen der Matrix")
            except Exception as e:
                st.error(f"Fehler: {str(e)}")
        
        if cancelled:
            st.session_state.excel_grid_show_new_matrix_dialog = False
            _safe_rerun()


def _render_matrix_management_dialog():
    """
    Rendert den Dialog zur Matrix-Verwaltung
    
    Bietet folgende Funktionen:
    - Matrix-Liste anzeigen
    - Matrix laden
    - Matrix löschen
    - Matrix umbenennen
    - Matrix klonen
    """
    if not st.session_state.get('excel_grid_show_load_dialog', False):
        return
    
    st.subheader("📂 Matrix-Verwaltung")
    st.markdown("Verwalten Sie Ihre gespeicherten Matrizen")
    
    # Lade alle Matrizen
    matrices = list_matrices()
    
    if not matrices:
        st.info("Keine Matrizen vorhanden. Erstellen Sie eine neue Matrix.")
        if st.button("Schließen", use_container_width=True):
            st.session_state.excel_grid_show_load_dialog = False
            _safe_rerun()
        return
    
    # Zeige Matrix-Liste mit Details
    st.markdown("### Verfügbare Matrizen")
    
    for matrix in matrices:
        with st.expander(
            f"{'🟢 ' if matrix['is_active'] else '⚪ '}{matrix['name']} (ID: {matrix['id']})",
            expanded=False
        ):
            # Matrix-Details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Name:** {matrix['name']}")
                st.markdown(f"**ID:** {matrix['id']}")
                st.markdown(f"**Status:** {'Aktiv' if matrix['is_active'] else 'Inaktiv'}")
            
            with col2:
                st.markdown(f"**Erstellt:** {matrix['created_at']}")
                st.markdown(f"**Aktualisiert:** {matrix['updated_at']}")
                st.markdown(f"**Beschreibung:** {matrix.get('description', 'Keine Beschreibung')}")
            
            # Lade Matrix-Details für Statistiken
            try:
                matrix_data = get_matrix_full(matrix['id'])
                if matrix_data:
                    st.markdown("---")
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        st.metric("Zeilen", len(matrix_data['rows']))
                    with stat_col2:
                        st.metric("Spalten", len(matrix_data['columns']))
                    with stat_col3:
                        st.metric("Zellen", len(matrix_data['cells']))
            except Exception as e:
                st.caption(f"Fehler beim Laden der Details: {str(e)}")
            
            st.markdown("---")
            
            # Aktionen
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                # Laden
                if st.button(
                    "📂 Laden",
                    key=f"load_{matrix['id']}",
                    use_container_width=True,
                    help="Matrix laden und bearbeiten"
                ):
                    st.session_state.excel_grid_selected_matrix_id = matrix['id']
                    st.session_state.excel_grid_manager = _load_matrix(matrix['id'])
                    st.session_state.excel_grid_show_load_dialog = False
                    st.success(f"Matrix '{matrix['name']}' geladen!")
                    _safe_rerun()
            
            with action_col2:
                # Klonen
                if st.button(
                    "📋 Klonen",
                    key=f"clone_{matrix['id']}",
                    use_container_width=True,
                    help="Kopie dieser Matrix erstellen"
                ):
                    st.session_state.excel_grid_clone_matrix_id = matrix['id']
                    st.session_state.excel_grid_show_clone_dialog = True
                    _safe_rerun()
            
            with action_col3:
                # Umbenennen
                if st.button(
                    "✏️ Umbenennen",
                    key=f"rename_{matrix['id']}",
                    use_container_width=True,
                    help="Matrix umbenennen"
                ):
                    st.session_state.excel_grid_rename_matrix_id = matrix['id']
                    st.session_state.excel_grid_show_rename_dialog = True
                    _safe_rerun()
            
            with action_col4:
                # Löschen
                if st.button(
                    "🗑️ Löschen",
                    key=f"delete_{matrix['id']}",
                    use_container_width=True,
                    help="Matrix unwiderruflich löschen",
                    type="secondary"
                ):
                    st.session_state.excel_grid_delete_matrix_id = matrix['id']
                    st.session_state.excel_grid_show_delete_confirm = True
                    _safe_rerun()
    
    st.markdown("---")
    
    # Schließen-Button
    if st.button("Schließen", use_container_width=True):
        st.session_state.excel_grid_show_load_dialog = False
        _safe_rerun()


def _render_clone_matrix_dialog():
    """Rendert den Dialog zum Klonen einer Matrix"""
    if not st.session_state.get('excel_grid_show_clone_dialog', False):
        return
    
    matrix_id = st.session_state.get('excel_grid_clone_matrix_id')
    if not matrix_id:
        st.session_state.excel_grid_show_clone_dialog = False
        return
    
    # Lade Original-Matrix
    try:
        from price_matrix_store import clone_matrix
        
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            st.error("Matrix nicht gefunden")
            st.session_state.excel_grid_show_clone_dialog = False
            return
        
        with st.form("clone_matrix_form"):
            st.subheader(f"📋 Matrix klonen: {matrix_data['meta']['name']}")
            
            new_name = st.text_input(
                "Neuer Name",
                value=f"{matrix_data['meta']['name']} (Kopie)",
                help="Name für die geklonte Matrix"
            )
            
            st.info(f"Die Matrix wird mit allen Zeilen, Spalten und Zellwerten kopiert.")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Klonen", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
            
            if submitted:
                try:
                    new_matrix_id = clone_matrix(matrix_id, new_name)
                    
                    if new_matrix_id:
                        st.success(f"Matrix '{new_name}' erfolgreich erstellt!")
                        st.session_state.excel_grid_show_clone_dialog = False
                        st.session_state.excel_grid_clone_matrix_id = None
                        st.session_state.excel_grid_selected_matrix_id = new_matrix_id
                        st.session_state.excel_grid_manager = _load_matrix(new_matrix_id)
                        _safe_rerun()
                    else:
                        st.error("Fehler beim Klonen der Matrix")
                except Exception as e:
                    st.error(f"Fehler: {str(e)}")
            
            if cancelled:
                st.session_state.excel_grid_show_clone_dialog = False
                st.session_state.excel_grid_clone_matrix_id = None
                _safe_rerun()
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Matrix: {str(e)}")
        st.session_state.excel_grid_show_clone_dialog = False


def _render_rename_matrix_dialog():
    """Rendert den Dialog zum Umbenennen einer Matrix"""
    if not st.session_state.get('excel_grid_show_rename_dialog', False):
        return
    
    matrix_id = st.session_state.get('excel_grid_rename_matrix_id')
    if not matrix_id:
        st.session_state.excel_grid_show_rename_dialog = False
        return
    
    # Lade Matrix
    try:
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            st.error("Matrix nicht gefunden")
            st.session_state.excel_grid_show_rename_dialog = False
            return
        
        with st.form("rename_matrix_form"):
            st.subheader(f"✏️ Matrix umbenennen")
            
            st.markdown(f"**Aktueller Name:** {matrix_data['meta']['name']}")
            
            new_name = st.text_input(
                "Neuer Name",
                value=matrix_data['meta']['name'],
                help="Neuer Name für die Matrix"
            )
            
            new_description = st.text_area(
                "Beschreibung",
                value=matrix_data['meta'].get('description', ''),
                help="Optionale Beschreibung"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Umbenennen", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
            
            if submitted:
                try:
                    # Aktualisiere Matrix-Metadaten in der Datenbank
                    from database import get_db_connection
                    
                    conn = get_db_connection()
                    if conn:
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE price_matrix_sets SET name=?, description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                            (new_name, new_description, matrix_id)
                        )
                        conn.commit()
                        conn.close()
                        
                        st.success(f"Matrix erfolgreich umbenannt zu '{new_name}'!")
                        st.session_state.excel_grid_show_rename_dialog = False
                        st.session_state.excel_grid_rename_matrix_id = None
                        
                        # Aktualisiere Manager falls diese Matrix geladen ist
                        if st.session_state.excel_grid_selected_matrix_id == matrix_id:
                            st.session_state.excel_grid_manager = _load_matrix(matrix_id)
                        
                        _safe_rerun()
                    else:
                        st.error("Fehler beim Verbinden mit der Datenbank")
                except Exception as e:
                    st.error(f"Fehler: {str(e)}")
            
            if cancelled:
                st.session_state.excel_grid_show_rename_dialog = False
                st.session_state.excel_grid_rename_matrix_id = None
                _safe_rerun()
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Matrix: {str(e)}")
        st.session_state.excel_grid_show_rename_dialog = False


def _render_delete_confirm_dialog():
    """Rendert den Bestätigungsdialog zum Löschen einer Matrix"""
    if not st.session_state.get('excel_grid_show_delete_confirm', False):
        return
    
    matrix_id = st.session_state.get('excel_grid_delete_matrix_id')
    if not matrix_id:
        st.session_state.excel_grid_show_delete_confirm = False
        return
    
    # Lade Matrix
    try:
        from price_matrix_store import delete_matrix
        
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            st.error("Matrix nicht gefunden")
            st.session_state.excel_grid_show_delete_confirm = False
            return
        
        with st.form("delete_matrix_form"):
            st.subheader("⚠️ Matrix löschen")
            
            st.warning(
                f"**Achtung:** Sie sind dabei, die Matrix '{matrix_data['meta']['name']}' "
                f"unwiderruflich zu löschen. Diese Aktion kann nicht rückgängig gemacht werden!"
            )
            
            st.markdown("**Matrix-Details:**")
            st.markdown(f"- **Name:** {matrix_data['meta']['name']}")
            st.markdown(f"- **ID:** {matrix_id}")
            st.markdown(f"- **Zeilen:** {len(matrix_data['rows'])}")
            st.markdown(f"- **Spalten:** {len(matrix_data['columns'])}")
            st.markdown(f"- **Zellen:** {len(matrix_data['cells'])}")
            
            # Sicherheitsabfrage
            confirm_text = st.text_input(
                f"Geben Sie '{matrix_data['meta']['name']}' ein, um zu bestätigen:",
                help="Geben Sie den exakten Namen der Matrix ein"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(
                    "🗑️ Endgültig löschen",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
            
            if submitted:
                if confirm_text == matrix_data['meta']['name']:
                    try:
                        success = delete_matrix(matrix_id)
                        
                        if success:
                            st.success(f"Matrix '{matrix_data['meta']['name']}' erfolgreich gelöscht!")
                            st.session_state.excel_grid_show_delete_confirm = False
                            st.session_state.excel_grid_delete_matrix_id = None
                            
                            # Wenn die gelöschte Matrix aktuell geladen war, zurücksetzen
                            if st.session_state.excel_grid_selected_matrix_id == matrix_id:
                                st.session_state.excel_grid_selected_matrix_id = None
                                st.session_state.excel_grid_manager = None
                            
                            _safe_rerun()
                        else:
                            st.error("Fehler beim Löschen der Matrix")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")
                else:
                    st.error("Der eingegebene Name stimmt nicht überein. Matrix wurde nicht gelöscht.")
            
            if cancelled:
                st.session_state.excel_grid_show_delete_confirm = False
                st.session_state.excel_grid_delete_matrix_id = None
                _safe_rerun()
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Matrix: {str(e)}")
        st.session_state.excel_grid_show_delete_confirm = False


def _render_csv_import_dialog():
    """Rendert den Dialog zum Importieren einer CSV-Datei (Task 13)"""
    if not st.session_state.get('excel_grid_show_import_dialog', False):
        return
    
    st.subheader("📥 CSV Import")
    st.markdown("Importieren Sie eine CSV-Datei als neue Matrix")
    
    # Datei-Upload Widget
    uploaded_file = st.file_uploader(
        "CSV-Datei auswählen",
        type=['csv', 'txt'],
        help="Wählen Sie eine CSV-Datei zum Importieren aus",
        key="csv_upload_widget"
    )
    
    if uploaded_file is not None:
        try:
            # Lese Dateiinhalt
            file_content = uploaded_file.read()
            
            # Validiere Datei
            from excel.excel_import import validate_csv_file, get_csv_preview
            
            validation = validate_csv_file(file_content)
            
            # Zeige Validierungsergebnis
            if validation['valid']:
                st.success("✓ CSV-Datei ist gültig")
                
                # Zeige erkannte Parameter
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Encoding", validation['encoding'])
                with col2:
                    st.metric("Delimiter", validation['delimiter'])
                with col3:
                    st.metric("Zeilen", validation['num_rows'])
                with col4:
                    st.metric("Spalten", validation['num_cols'])
                
                if validation['has_formulas']:
                    st.info("ℹ️ Die Datei enthält Formeln (beginnen mit =)")
                
                # Zeige Vorschau
                st.markdown("### Vorschau")
                preview = get_csv_preview(file_content, max_rows=10)
                
                # Erstelle DataFrame für Vorschau
                import pandas as pd
                preview_df = pd.DataFrame(
                    preview['rows'],
                    columns=preview['header']
                )
                st.dataframe(preview_df, use_container_width=True)
                
                if preview['total_rows'] > 10:
                    st.caption(f"Zeige 10 von {preview['total_rows']} Zeilen")
                
                st.markdown("---")
                
                # Import-Optionen
                with st.form("csv_import_form"):
                    st.markdown("### Import-Optionen")
                    
                    matrix_name = st.text_input(
                        "Matrix-Name",
                        value=f"Import {uploaded_file.name}",
                        help="Name für die neue Matrix"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Delimiter-Auswahl (mit Auto-Erkennung als Standard)
                        delimiter_options = {
                            "Automatisch": None,
                            "Semikolon (;)": ";",
                            "Komma (,)": ",",
                            "Tab": "\t",
                            "Pipe (|)": "|"
                        }
                        
                        delimiter_choice = st.selectbox(
                            "Delimiter",
                            options=list(delimiter_options.keys()),
                            index=0,
                            help="Trennzeichen zwischen Spalten (wird automatisch erkannt)"
                        )
                        delimiter = delimiter_options[delimiter_choice]
                    
                    with col2:
                        # Encoding-Auswahl (mit Auto-Erkennung als Standard)
                        encoding_options = {
                            "Automatisch": None,
                            "UTF-8": "utf-8",
                            "Latin-1 (ISO-8859-1)": "latin-1",
                            "Windows-1252": "windows-1252"
                        }
                        
                        encoding_choice = st.selectbox(
                            "Encoding",
                            options=list(encoding_options.keys()),
                            index=0,
                            help="Zeichenkodierung der Datei (wird automatisch erkannt)"
                        )
                        encoding = encoding_options[encoding_choice]
                    
                    has_header = st.checkbox(
                        "Erste Zeile als Spaltenüberschriften verwenden",
                        value=True,
                        help="Wenn aktiviert, wird die erste Zeile als Spaltenüberschriften verwendet"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button(
                            "📥 Importieren",
                            use_container_width=True,
                            type="primary"
                        )
                    with col2:
                        cancelled = st.form_submit_button(
                            "Abbrechen",
                            use_container_width=True
                        )
                    
                    if submitted:
                        try:
                            # Importiere CSV
                            from excel.excel_import import import_csv_to_matrix
                            
                            with st.spinner("Importiere CSV-Datei..."):
                                manager = import_csv_to_matrix(
                                    file_content,
                                    matrix_name,
                                    delimiter=delimiter,
                                    has_header=has_header,
                                    encoding=encoding
                                )
                            
                            if manager:
                                # Speichere in Datenbank
                                # Erstelle Matrix in DB
                                matrix_id = create_matrix(
                                    matrix_name,
                                    f"Importiert aus {uploaded_file.name}"
                                )
                                
                                if matrix_id:
                                    # Setze ID in Manager
                                    manager.matrix.id = matrix_id
                                    
                                    # Füge Zeilen und Spalten zur DB hinzu
                                    for i in range(manager.matrix.rows):
                                        db_add_row(matrix_id, str(i + 1))
                                    
                                    for i in range(manager.matrix.columns):
                                        db_add_column(matrix_id, _get_column_label(i))
                                    
                                    # Speichere Zellwerte
                                    if manager.save_to_database():
                                        st.success(f"✓ CSV-Datei erfolgreich importiert als '{matrix_name}'!")
                                        st.session_state.excel_grid_show_import_dialog = False
                                        st.session_state.excel_grid_selected_matrix_id = matrix_id
                                        st.session_state.excel_grid_manager = manager
                                        _safe_rerun()
                                    else:
                                        st.error("Fehler beim Speichern der Matrix in der Datenbank")
                                else:
                                    st.error("Fehler beim Erstellen der Matrix in der Datenbank")
                            else:
                                st.error("Fehler beim Importieren der CSV-Datei")
                        
                        except Exception as e:
                            st.error(f"Fehler beim Import: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                    
                    if cancelled:
                        st.session_state.excel_grid_show_import_dialog = False
                        _safe_rerun()
            
            else:
                # Zeige Validierungsfehler
                st.error("⚠️ CSV-Datei ist ungültig")
                for error in validation['errors']:
                    st.error(f"- {error}")
                
                if st.button("Schließen", use_container_width=True):
                    st.session_state.excel_grid_show_import_dialog = False
                    _safe_rerun()
        
        except Exception as e:
            st.error(f"Fehler beim Lesen der Datei: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    else:
        st.info("Wählen Sie eine CSV-Datei aus, um fortzufahren")
        
        # Hilfe-Text
        with st.expander("ℹ️ Hilfe zum CSV-Import"):
            st.markdown("""
            **Unterstützte Formate:**
            - CSV-Dateien mit verschiedenen Delimitern (`;`, `,`, Tab, `|`)
            - Verschiedene Encodings (UTF-8, Latin-1, Windows-1252)
            - Dateien mit oder ohne Spaltenüberschriften
            - Formeln (beginnen mit `=`)
            
            **Tipps:**
            - Die Datei sollte eine rechteckige Struktur haben (gleiche Anzahl Spalten pro Zeile)
            - Leere Zellen werden automatisch übersprungen
            - Zahlen werden automatisch erkannt (auch mit Komma als Dezimaltrennzeichen)
            - Formeln werden erkannt und können berechnet werden
            
            **Beispiel CSV-Struktur:**
            ```
            Modulanzahl;10kWh;15kWh;20kWh
            10;15000;17000;19000
            20;25000;27000;29000
            30;=B2*1.5;=C2*1.5;=D2*1.5
            ```
            """)
        
        if st.button("Abbrechen", use_container_width=True):
            st.session_state.excel_grid_show_import_dialog = False
            _safe_rerun()


def render_excel_grid_ui():
    """
    Hauptfunktion für Excel-Grid-Oberfläche
    
    Diese Funktion rendert die vollständige Excel-Grid UI mit:
    - Matrix-Auswahl
    - Toolbar
    - Formelleiste
    - Grid-Darstellung
    - Auto-Save Funktionalität
    """
    if not EXCEL_INTEGRATION_AVAILABLE:
        st.error("Excel-Integration ist nicht verfügbar. Bitte prüfen Sie die Installation.")
        return
    
    # Initialisiere Session State
    _initialize_session_state()
    
    # Reset Rerun Flag am Anfang jedes Renders
    _reset_rerun_flag()
    
    # Titel
    st.title("📊 Excel Preis Matrix")
    
    # Beschreibung in Expander
    with st.expander("ℹ️ Was ist die Excel Preis Matrix?", expanded=False):
        st.markdown("""
        Erstellen und bearbeiten Sie Excel-ähnliche Preismatrizen mit Formelunterstützung.
        
        **Features:**
        - 📊 Excel-ähnliche Grid-Darstellung
        - 🔢 Formelunterstützung (SUM, AVERAGE, IF, etc.)
        - 💾 Auto-Save Funktion
        - 📥 CSV/Excel Import & Export
        - 🎨 Zellformatierung (Währung, Prozent, Datum)
        - ⌨️ Tastaturnavigation
        """)
    
    # Hilfe-Bereich (zugeklappt)
    with st.expander("📖 Hilfe & Anleitung", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Schnellstart
            
            **1. Matrix erstellen:**
            - Klicken Sie auf "➕ Neue Matrix"
            - Geben Sie Name, Zeilen und Spalten ein
            - Bestätigen Sie mit "Erstellen"
            
            **2. Zellen bearbeiten:**
            - Klicken Sie auf eine Zelle im Grid
            - Geben Sie einen Wert oder eine Formel ein
            - Formeln beginnen mit `=`
            
            **📝 Text vs. 🔢 Zahlen (Neu!):**
            - **Text:** Wird ohne Formatierung gespeichert
              - Beispiel: "10kWh Speicher", "Kein Speicher"
            - **Zahlen:** Automatisch erkannt für Berechnungen
              - Beispiel: 15000, 15000.50, 15.000,50
            - **Formeln:** Beginnen mit `=`
              - Beispiel: =SUM(A1:A10)
            
            **3. Formeln verwenden:**
            ```
            =SUM(A1:A10)      → Summe
            =AVERAGE(B1:B10)  → Durchschnitt
            =A1*1.19          → Berechnung
            =IF(A1>100, "Hoch", "Niedrig")
            ```
            
            **4. Speichern:**
            - Auto-Save ist standardmäßig aktiv
            - Oder nutzen Sie "💾 Speichern"
            """)
        
        with col2:
            st.markdown("""
            ### ⌨️ Tastenkombinationen
            
            **Bearbeitung:**
            - `Strg+C` - Zelle kopieren
            - `Strg+V` - Zelle einfügen
            - `Strg+Z` - Rückgängig
            - `Strg+Y` - Wiederholen
            
            **Navigation:**
            - `↑↓←→` - Zelle bewegen
            - `Tab` - Nächste Spalte
            - `Enter` - Nächste Zeile
            
            **Formatierung:**
            - Wählen Sie Format: Auto, Zahl, Währung, Prozent, Datum, Text
            
            ### 📥 Import/Export
            - **CSV Import**: Laden Sie bestehende Daten
            - **CSV/Excel Export**: Speichern Sie Ihre Matrix
            
            💡 **Tipp**: Detaillierte Hilfe finden Sie ganz unten unter "ℹ️ Hilfe & Tastenkombinationen"
            """)
    
    # Zeige Dialoge
    _render_new_matrix_dialog()
    _render_matrix_management_dialog()
    _render_clone_matrix_dialog()
    _render_rename_matrix_dialog()
    _render_delete_confirm_dialog()
    _render_csv_import_dialog()  # Task 13
    _render_csv_export_dialog()  # Task 15
    _render_excel_export_dialog()  # Task 15
    _render_export_info_dialog()  # Task 15
    _render_help_dialog()  # Task 4.2
    _render_validation_dialog()  # Task 4.2
    _handle_example_matrix_creation()  # Task 4.2
    
    st.markdown("---")
    
    # Matrix-Auswahl
    _render_matrix_selector()
    
    st.markdown("---")
    
    # Toolbar
    _render_toolbar()
    
    st.markdown("---")
    
    # Auto-Save ausführen wenn aktiviert
    manager = st.session_state.excel_grid_manager
    if manager:
        _auto_save_matrix(manager)
    
    # Formelleiste
    _render_formula_bar()
    
    st.markdown("---")
    
    # Grid
    _render_grid()
    
    # Dialoge
    _render_new_matrix_dialog()
    _render_matrix_management_dialog()
    _render_clone_matrix_dialog()
    _render_rename_matrix_dialog()
    _render_delete_confirm_dialog()
    
    # Erweiterte Hilfe-Sektion (Task 10)
    with st.expander("ℹ️ Hilfe & Tastenkombinationen", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Excel-Funktionen", "⌨️ Tastenkombinationen", "🎨 Formatierung", "❓ Fehler & Tipps"])
        
        with tab1:
            st.markdown("""
            ### Excel-Funktionen
            
            Die folgenden Excel-Funktionen werden unterstützt:
            
            **Mathematische Funktionen:**
            - `SUM(A1:A10)` - Summe eines Bereichs
            - `AVERAGE(A1:A10)` - Durchschnitt
            - `MIN(A1:A10)` - Minimum
            - `MAX(A1:A10)` - Maximum
            - `ROUND(A1, 2)` - Runden auf 2 Dezimalstellen
            - `ROUNDUP(A1, 0)` - Aufrunden
            - `ROUNDDOWN(A1, 0)` - Abrunden
            
            **Logische Funktionen:**
            - `IF(A1>10, "Ja", "Nein")` - Bedingung
            - `AND(A1>0, B1<100)` - Logisches UND
            - `OR(A1>0, B1>0)` - Logisches ODER
            - `IFERROR(A1/B1, 0)` - Fehlerbehandlung
            
            **Lookup-Funktionen:**
            - `VLOOKUP(A1, B1:C10, 2, FALSE)` - Vertikale Suche
            - `HLOOKUP(A1, B1:E2, 2, FALSE)` - Horizontale Suche
            - `INDEX(A1:A10, 5)` - Wert an Position
            - `MATCH(A1, B1:B10, 0)` - Position eines Werts
            
            **Zähl-Funktionen:**
            - `COUNT(A1:A10)` - Anzahl Zahlen
            - `COUNTA(A1:A10)` - Anzahl nicht-leere Zellen
            - `SUMIF(A1:A10, ">10")` - Bedingte Summe
            """)
        
        with tab2:
            st.markdown("""
            ### Tastenkombinationen
            
            **Bearbeitung:**
            - `Strg+C` - Zelle kopieren
            - `Strg+V` - Zelle einfügen
            - `Strg+Z` - Rückgängig
            - `Strg+Y` - Wiederholen
            - `Strg+S` - Speichern
            
            **Navigation:**
            - `↑` - Eine Zelle nach oben
            - `↓` - Eine Zelle nach unten
            - `←` - Eine Zelle nach links
            - `→` - Eine Zelle nach rechts
            - `Tab` - Nächste Spalte
            - `Enter` - Nächste Zeile
            - `Pos1` - Erste Spalte
            - `Ende` - Letzte Spalte
            
            **Hinweis:** Tastenkombinationen funktionieren am besten, wenn die Tastaturnavigation aktiviert ist.
            """)
        
        with tab3:
            st.markdown("""
            ### Zell-Formatierung
            
            **Verfügbare Formate:**
            
            1. **Auto** - Automatische Erkennung des Formats
               - Zahlen werden als Zahlen erkannt
               - Text bleibt Text
            
            2. **Zahl** - Dezimalzahl mit 2 Nachkommastellen
               - Beispiel: `123.45`
               - Gut für Mengen, Maße, etc.
            
            3. **Währung** - Betrag in Euro
               - Beispiel: `1.234,56 €`
               - Deutsche Formatierung mit Tausenderpunkt
            
            4. **Prozent** - Prozentwert
               - Beispiel: `12.34%`
               - Wert wird mit 100 multipliziert
            
            5. **Datum** - Datumsformat
               - Beispiel: `31.12.2023`
               - Deutsche Formatierung (TT.MM.JJJJ)
            
            6. **Text** - Textformat
               - Erzwingt Textdarstellung
               - Nützlich für Zahlen, die als Text behandelt werden sollen
            
            **Format anwenden:**
            1. Wählen Sie eine Zelle aus
            2. Wählen Sie das gewünschte Format aus dem Dropdown
            3. Das Format wird automatisch angewendet
            """)
        
        with tab4:
            st.markdown("""
            ### Fehler-Codes
            
            - `#ERROR!` - **Syntaxfehler in der Formel**
              - Prüfen Sie die Formel-Syntax
              - Achten Sie auf korrekte Klammern und Anführungszeichen
            
            - `#REF!` - **Ungültige Zellreferenz**
              - Die referenzierte Zelle existiert nicht
              - Möglicherweise wurde eine Zeile/Spalte gelöscht
            
            - `#DIV/0!` - **Division durch Null**
              - Prüfen Sie die Werte in der Formel
              - Verwenden Sie IFERROR() zur Fehlerbehandlung
            
            - `#CIRCULAR!` - **Zirkelbezug erkannt**
              - Die Formel referenziert sich selbst
              - Überprüfen Sie die Formel-Abhängigkeiten
            
            - `#NAME?` - **Unbekannte Funktion**
              - Prüfen Sie den Funktionsnamen
              - Siehe Liste der unterstützten Funktionen
            
            - `#VALUE!` - **Falscher Wert-Typ**
              - Die Funktion erwartet einen anderen Datentyp
              - Prüfen Sie die Eingabewerte
            
            ### Tipps & Tricks
            
            - **Formeln kopieren:** Kopieren Sie eine Zelle mit Formel, die Referenzen werden automatisch angepasst
            - **Absolute Referenzen:** Verwenden Sie `$A$1` für absolute Referenzen (noch nicht unterstützt)
            - **Bereiche:** Verwenden Sie `:` für Bereiche (z.B. `A1:A10`)
            - **Verschachtelte Formeln:** Kombinieren Sie Funktionen (z.B. `=IF(SUM(A1:A10)>100, "Hoch", "Niedrig")`)
            - **Fehlerbehandlung:** Verwenden Sie `IFERROR()` um Fehler abzufangen
            - **Speichern nicht vergessen:** Klicken Sie regelmäßig auf "Speichern"
            """)
        


# Hauptfunktion für Integration in Admin Panel
def render_price_matrix_tab():
    """
    Rendert den Preis Matrix Tab im Admin Panel
    
    Diese Funktion wird vom Admin Panel aufgerufen.
    """
    render_excel_grid_ui()


def _render_csv_export_dialog():
    """Rendert den Dialog zum Exportieren als CSV-Datei (Task 15)"""
    if not st.session_state.get('excel_grid_show_csv_export_dialog', False):
        return
    
    manager = st.session_state.excel_grid_manager
    if not manager:
        st.session_state.excel_grid_show_csv_export_dialog = False
        return
    
    st.subheader("📤 CSV Export")
    st.markdown("Exportieren Sie die Matrix als CSV-Datei")
    
    # Zeige Matrix-Info
    matrix = manager.get_matrix()
    info = manager.get_matrix_info()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matrix", matrix.name)
    with col2:
        st.metric("Zeilen", info['rows'])
    with col3:
        st.metric("Spalten", info['columns'])
    with col4:
        st.metric("Zellen", info['cell_count'])
    
    st.markdown("---")
    
    # Export-Optionen
    with st.form("csv_export_form"):
        st.markdown("### Export-Optionen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Delimiter-Auswahl
            delimiter_options = {
                "Semikolon (;)": ";",
                "Komma (,)": ",",
                "Tab": "\t",
                "Pipe (|)": "|"
            }
            
            delimiter_choice = st.selectbox(
                "Delimiter",
                options=list(delimiter_options.keys()),
                index=0,
                help="Trennzeichen zwischen Spalten"
            )
            delimiter = delimiter_options[delimiter_choice]
        
        with col2:
            # Encoding-Auswahl
            encoding_options = {
                "UTF-8": "utf-8",
                "Latin-1 (ISO-8859-1)": "latin-1",
                "Windows-1252": "windows-1252"
            }
            
            encoding_choice = st.selectbox(
                "Encoding",
                options=list(encoding_options.keys()),
                index=0,
                help="Zeichenkodierung der Datei"
            )
            encoding = encoding_options[encoding_choice]
        
        include_formulas = st.checkbox(
            "Formeln exportieren (statt berechneter Werte)",
            value=False,
            help="Wenn aktiviert, werden Formeln statt der berechneten Werte exportiert"
        )
        
        include_timestamp = st.checkbox(
            "Zeitstempel im Dateinamen",
            value=True,
            help="Fügt Datum und Uhrzeit zum Dateinamen hinzu"
        )
        
        # Zeige geschätzten Dateinamen
        from excel.excel_export import generate_filename
        filename = generate_filename(matrix.name, 'csv', include_timestamp)
        st.info(f"📄 Dateiname: `{filename}`")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "📤 Exportieren",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancelled = st.form_submit_button(
                "Abbrechen",
                use_container_width=True
            )
        
        if submitted:
            try:
                from excel.excel_export import export_to_csv
                
                with st.spinner("Exportiere CSV-Datei..."):
                    csv_data = export_to_csv(
                        manager,
                        delimiter=delimiter,
                        include_formulas=include_formulas,
                        encoding=encoding
                    )
                
                # Download-Button
                st.download_button(
                    label="💾 CSV-Datei herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.success(f"✓ CSV-Datei erfolgreich erstellt!")
                st.info(f"📊 Größe: {len(csv_data)} Bytes")
                
            except Exception as e:
                st.error(f"Fehler beim Export: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        if cancelled:
            st.session_state.excel_grid_show_csv_export_dialog = False
            _safe_rerun()


def _render_excel_export_dialog():
    """Rendert den Dialog zum Exportieren als Excel-Datei (Task 15)"""
    if not st.session_state.get('excel_grid_show_excel_export_dialog', False):
        return
    
    manager = st.session_state.excel_grid_manager
    if not manager:
        st.session_state.excel_grid_show_excel_export_dialog = False
        return
    
    st.subheader("📤 Excel Export")
    st.markdown("Exportieren Sie die Matrix als Excel-Datei (XLSX) mit Formeln")
    
    # Prüfe ob openpyxl verfügbar ist
    try:
        import openpyxl
        openpyxl_available = True
    except ImportError:
        openpyxl_available = False
    
    if not openpyxl_available:
        st.error(
            "⚠️ openpyxl ist nicht installiert. "
            "Bitte installieren Sie es mit: `pip install openpyxl`"
        )
        if st.button("Schließen", use_container_width=True):
            st.session_state.excel_grid_show_excel_export_dialog = False
            _safe_rerun()
        return
    
    # Zeige Matrix-Info
    matrix = manager.get_matrix()
    info = manager.get_matrix_info()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matrix", matrix.name)
    with col2:
        st.metric("Zeilen", info['rows'])
    with col3:
        st.metric("Spalten", info['columns'])
    with col4:
        st.metric("Zellen", info['cell_count'])
    
    if info['formula_count'] > 0:
        st.info(f"ℹ️ Die Matrix enthält {info['formula_count']} Formel(n)")
    
    st.markdown("---")
    
    # Export-Optionen
    with st.form("excel_export_form"):
        st.markdown("### Export-Optionen")
        
        include_formulas = st.checkbox(
            "Formeln exportieren",
            value=True,
            help="Wenn aktiviert, werden Formeln in die Excel-Datei exportiert"
        )
        
        include_formatting = st.checkbox(
            "Formatierung anwenden",
            value=True,
            help="Wenn aktiviert, wird die Excel-Datei formatiert (Header, Fehler-Markierungen)"
        )
        
        include_timestamp = st.checkbox(
            "Zeitstempel im Dateinamen",
            value=True,
            help="Fügt Datum und Uhrzeit zum Dateinamen hinzu"
        )
        
        # Zeige geschätzten Dateinamen
        from excel.excel_export import generate_filename
        filename = generate_filename(matrix.name, 'xlsx', include_timestamp)
        st.info(f"📄 Dateiname: `{filename}`")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "📤 Exportieren",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancelled = st.form_submit_button(
                "Abbrechen",
                use_container_width=True
            )
        
        if submitted:
            try:
                from excel.excel_export import export_to_excel
                
                with st.spinner("Exportiere Excel-Datei..."):
                    excel_data = export_to_excel(
                        manager,
                        include_formulas=include_formulas,
                        include_formatting=include_formatting
                    )
                
                # Download-Button
                st.download_button(
                    label="💾 Excel-Datei herunterladen",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                st.success(f"✓ Excel-Datei erfolgreich erstellt!")
                st.info(f"📊 Größe: {len(excel_data)} Bytes")
                
            except Exception as e:
                st.error(f"Fehler beim Export: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        if cancelled:
            st.session_state.excel_grid_show_excel_export_dialog = False
            _safe_rerun()


def _render_export_info_dialog():
    """Rendert den Dialog mit Export-Informationen (Task 15)"""
    if not st.session_state.get('excel_grid_show_export_info', False):
        return
    
    manager = st.session_state.excel_grid_manager
    if not manager:
        st.session_state.excel_grid_show_export_info = False
        return
    
    st.subheader("👁️ Export-Informationen")
    st.markdown("Informationen über den Export dieser Matrix")
    
    try:
        from excel.excel_export import get_export_info, validate_export
        
        # Hole Export-Informationen
        export_info = get_export_info(manager)
        
        # Zeige Basis-Informationen
        st.markdown("### Matrix-Informationen")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Zeilen", export_info['rows'])
        with col2:
            st.metric("Spalten", export_info['columns'])
        with col3:
            st.metric("Zellen mit Werten", export_info['cell_count'])
        with col4:
            st.metric("Formeln", export_info['formula_count'])
        
        # Zeige Fehler-Status
        if export_info['has_errors']:
            st.warning(f"⚠️ {export_info['error_count']} Zelle(n) enthalten Fehler")
        else:
            st.success("✓ Keine Fehler in der Matrix")
        
        st.markdown("---")
        
        # Zeige geschätzte Dateigrößen
        st.markdown("### Geschätzte Dateigrößen")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_size = export_info['estimated_csv_size']
            if csv_size < 1024:
                csv_size_str = f"{csv_size} Bytes"
            elif csv_size < 1024 * 1024:
                csv_size_str = f"{csv_size / 1024:.2f} KB"
            else:
                csv_size_str = f"{csv_size / (1024 * 1024):.2f} MB"
            
            st.metric("CSV-Export", csv_size_str)
        
        with col2:
            xlsx_size = export_info['estimated_xlsx_size']
            if xlsx_size < 1024:
                xlsx_size_str = f"{xlsx_size} Bytes"
            elif xlsx_size < 1024 * 1024:
                xlsx_size_str = f"{xlsx_size / 1024:.2f} KB"
            else:
                xlsx_size_str = f"{xlsx_size / (1024 * 1024):.2f} MB"
            
            st.metric("Excel-Export", xlsx_size_str)
        
        st.caption("Hinweis: Dies sind grobe Schätzungen. Die tatsächliche Dateigröße kann abweichen.")
        
        st.markdown("---")
        
        # Validiere Export
        validation = validate_export(manager)
        
        if validation['warnings']:
            st.markdown("### ⚠️ Warnungen")
            for warning in validation['warnings']:
                st.warning(warning)
        
        if validation['errors']:
            st.markdown("### ❌ Fehler")
            for error in validation['errors']:
                st.error(error)
        
        if not validation['warnings'] and not validation['errors']:
            st.success("✓ Export kann ohne Probleme durchgeführt werden")
        
        st.markdown("---")
        
        # Schließen-Button
        if st.button("Schließen", use_container_width=True):
            st.session_state.excel_grid_show_export_info = False
            _safe_rerun()
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Export-Informationen: {str(e)}")
        if st.button("Schließen", use_container_width=True):
            st.session_state.excel_grid_show_export_info = False
            _safe_rerun()


def _render_help_dialog():
    """
    Rendert den Hilfe-Dialog mit Matrix-Struktur-Anleitung (Task 4.2)
    
    Requirement: 2.5
    """
    if not st.session_state.get('excel_grid_show_help_dialog', False):
        return
    
    st.markdown("---")
    st.subheader("❓ Hilfe: Preismatrix-Struktur")
    
    try:
        from price_matrix_examples import get_matrix_structure_help, get_quick_help_tooltips
        
        # Zeige Haupt-Hilfetext
        help_text = get_matrix_structure_help()
        st.markdown(help_text)
        
        # Zeige Tooltips in Tabs
        st.markdown("### 📚 Detaillierte Hilfe")
        
        tooltips = get_quick_help_tooltips()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Spalte A",
            "Zeile 1",
            "Preis-Zellen",
            "'Kein Speicher'",
            "Validierung"
        ])
        
        with tab1:
            st.info(tooltips['column_a'])
        
        with tab2:
            st.info(tooltips['row_1'])
        
        with tab3:
            st.info(tooltips['price_cells'])
        
        with tab4:
            st.info(tooltips['no_storage'])
        
        with tab5:
            st.info(tooltips['validation'])
        
        # Link zur vollständigen Dokumentation
        st.markdown("---")
        st.markdown("📖 **Vollständige Dokumentation:** `docs/PRICE_MATRIX_STRUCTURE_GUIDE.md`")
        
        # Schließen-Button
        if st.button("Schließen", key="close_help_dialog"):
            st.session_state.excel_grid_show_help_dialog = False
            st.rerun()
    
    except ImportError as e:
        st.error(f"Fehler beim Laden der Hilfe: {str(e)}")
        if st.button("Schließen", key="close_help_dialog_error"):
            st.session_state.excel_grid_show_help_dialog = False
            st.rerun()


def _render_validation_dialog():
    """
    Rendert den Validierungs-Dialog für die Matrix (Task 4.2)
    
    Requirement: 7.1
    """
    if not st.session_state.get('excel_grid_show_validation_dialog', False):
        return
    
    manager = st.session_state.excel_grid_manager
    if not manager:
        st.session_state.excel_grid_show_validation_dialog = False
        return
    
    st.markdown("---")
    st.subheader("✓ Matrix-Validierung")
    
    try:
        from price_matrix_validation import validate_matrix_for_pricing, get_validation_summary
        
        matrix_id = manager.get_matrix().id
        
        if not matrix_id:
            st.error("Matrix hat keine ID. Kann nicht validiert werden.")
            if st.button("Schließen", key="close_validation_no_id"):
                st.session_state.excel_grid_show_validation_dialog = False
                st.rerun()
            return
        
        # Führe Validierung durch
        with st.spinner("Validiere Matrix..."):
            validation_result = validate_matrix_for_pricing(matrix_id)
        
        # Zeige Ergebnis
        if validation_result['valid']:
            st.success("✓ Matrix ist gültig für Preisberechnung!")
        else:
            st.error("✗ Matrix ist NICHT gültig für Preisberechnung")
        
        # Zeige Zusammenfassung
        summary = get_validation_summary(validation_result)
        st.code(summary, language=None)
        
        # Zeige Details in Tabs
        if validation_result['errors'] or validation_result['warnings']:
            st.markdown("### Details")
            
            if validation_result['errors']:
                with st.expander("❌ Fehler", expanded=True):
                    for idx, error in enumerate(validation_result['errors'], 1):
                        st.error(f"{idx}. {error}")
            
            if validation_result['warnings']:
                with st.expander("⚠️ Warnungen", expanded=False):
                    for idx, warning in enumerate(validation_result['warnings'], 1):
                        st.warning(f"{idx}. {warning}")
        
        # Zeige Informationen
        info = validation_result.get('info', {})
        if info:
            with st.expander("ℹ️ Matrix-Informationen", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Zeilen", info.get('total_rows', 0))
                    st.metric("Spalten", info.get('total_columns', 0))
                
                with col2:
                    st.metric("Zellen mit Werten", info.get('total_cells', 0))
                    if 'empty_price_cells' in info:
                        st.metric("Leere Preis-Zellen", info['empty_price_cells'])
                
                with col3:
                    if 'no_storage_column' in info:
                        st.info(f"**'Kein Speicher' Spalte:**\n{info['no_storage_column']}")
                
                # Zeige Modulanzahlen
                if 'module_counts' in info and info['module_counts']:
                    st.markdown("**Modulanzahlen:**")
                    counts_str = ', '.join(str(c) for c in info['module_counts'])
                    st.caption(counts_str)
                
                # Zeige Speichermodelle
                if 'storage_models' in info and info['storage_models']:
                    st.markdown("**Speichermodelle:**")
                    models_str = ', '.join(info['storage_models'])
                    st.caption(models_str)
        
        # Aktionen
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Erneut validieren", key="revalidate_matrix"):
                st.rerun()
        
        with col2:
            if st.button("Schließen", key="close_validation_dialog"):
                st.session_state.excel_grid_show_validation_dialog = False
                st.rerun()
    
    except ImportError as e:
        st.error(f"Fehler beim Laden der Validierung: {str(e)}")
        if st.button("Schließen", key="close_validation_error"):
            st.session_state.excel_grid_show_validation_dialog = False
            st.rerun()


def _handle_example_matrix_creation():
    """
    Behandelt die Erstellung von Beispiel-Matrizen (Task 4.2)
    
    Requirement: 2.5
    """
    example_type = st.session_state.get('excel_grid_create_example')
    
    if not example_type:
        return
    
    try:
        from price_matrix_examples import (
            create_example_matrix_small,
            create_example_matrix_medium,
            create_example_matrix_large
        )
        
        # Erstelle Beispiel-Matrix basierend auf Typ
        with st.spinner(f"Erstelle Beispiel-Matrix ({example_type})..."):
            if example_type == 'small':
                matrix_id = create_example_matrix_small()
                name = "Kleine Anlage (10-25 Module)"
            elif example_type == 'medium':
                matrix_id = create_example_matrix_medium()
                name = "Mittlere Anlage (30-50 Module)"
            elif example_type == 'large':
                matrix_id = create_example_matrix_large()
                name = "Große Anlage (60-100 Module)"
            else:
                st.error(f"Unbekannter Beispiel-Typ: {example_type}")
                st.session_state.excel_grid_create_example = None
                return
        
        if matrix_id:
            st.success(f"✓ Beispiel-Matrix '{name}' erfolgreich erstellt!")
            
            # Lade die neue Matrix
            st.session_state.excel_grid_selected_matrix_id = matrix_id
            st.session_state.excel_grid_manager = _load_matrix(matrix_id)
            
            # Reset Flag
            st.session_state.excel_grid_create_example = None
            
            # Zeige Info
            st.info(
                "💡 Die Beispiel-Matrix enthält Dummy-Daten. "
                "Sie können diese als Vorlage verwenden und anpassen."
            )
            
            st.rerun()
        else:
            st.error("Fehler beim Erstellen der Beispiel-Matrix")
            st.session_state.excel_grid_create_example = None
    
    except ImportError as e:
        st.error(f"Fehler beim Laden der Beispiel-Matrizen: {str(e)}")
        st.session_state.excel_grid_create_example = None
    except Exception as e:
        st.error(f"Fehler beim Erstellen der Beispiel-Matrix: {str(e)}")
        st.session_state.excel_grid_create_example = None
