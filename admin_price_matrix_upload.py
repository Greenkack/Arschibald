"""
Admin Panel Matrix Upload mit erweiterter Validierung

Dieses Modul erweitert die Admin Panel Funktionalität um:
- Struktur-Validierung vor dem Speichern
- Aussagekräftige Fehlermeldungen
- Vorschau-Validierung
- Upload-Workflow für CSV und Excel

Task 5: Verbessere Admin Panel Matrix-Upload Validierung
Requirements: 2.1, 2.2, 2.4
"""

import io
import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import openpyxl

from price_matrix_validation import (
    validate_matrix_for_pricing,
    get_validation_summary,
    EXAMPLE_MATRIX_STRUCTURE
)
from price_matrix_store import (
    create_matrix,
    import_matrix_csv,
    get_matrix_full,
    list_matrices,
    set_active_matrix
)


def validate_uploaded_file(
    file_content: bytes,
    file_type: str
) -> Dict[str, Any]:
    """
    Validiert eine hochgeladene Matrix-Datei (CSV oder Excel)
    
    Args:
        file_content: Dateiinhalt als Bytes
        file_type: 'csv' oder 'excel'
        
    Returns:
        Dictionary mit Validierungsergebnis:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'preview_df': Optional[pd.DataFrame],
            'info': Dict[str, Any]
        }
    
    Requirements: 2.2
    """
    errors = []
    warnings = []
    info = {}
    preview_df = None
    
    try:
        # Parse Datei basierend auf Typ
        if file_type == 'csv':
            result = _parse_csv_file(file_content)
        elif file_type == 'excel':
            result = _parse_excel_file(file_content)
        else:
            errors.append(f"Nicht unterstützter Dateityp: {file_type}")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'preview_df': None,
                'info': info
            }
        
        if not result['success']:
            errors.extend(result['errors'])
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'preview_df': None,
                'info': info
            }
        
        preview_df = result['dataframe']
        info = result['info']
        
        # Validiere Matrix-Struktur
        structure_validation = _validate_matrix_structure(preview_df)
        errors.extend(structure_validation['errors'])
        warnings.extend(structure_validation['warnings'])
        
        # Zusätzliche Informationen
        info.update(structure_validation['info'])
        
    except Exception as e:
        errors.append(f"Fehler beim Verarbeiten der Datei: {str(e)}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'preview_df': preview_df,
        'info': info
    }


def _parse_csv_file(file_content: bytes) -> Dict[str, Any]:
    """
    Parst eine CSV-Datei und gibt DataFrame zurück
    
    Requirements: 2.2, 3.3
    """
    errors = []
    info = {}
    
    try:
        # Versuche verschiedene Encodings
        encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                # Versuche verschiedene Delimiters
                for delimiter in [';', ',', '\t', '|']:
                    try:
                        df = pd.read_csv(
                            io.BytesIO(file_content),
                            encoding=encoding,
                            delimiter=delimiter,
                            index_col=0
                        )
                        
                        # Prüfe ob DataFrame sinnvoll ist (mindestens 2 Spalten)
                        if len(df.columns) >= 1 and len(df) >= 1:
                            used_encoding = encoding
                            info['delimiter'] = delimiter
                            info['encoding'] = encoding
                            break
                    except Exception:
                        continue
                
                if df is not None:
                    break
                    
            except Exception:
                continue
        
        if df is None:
            errors.append(
                "CSV-Datei konnte nicht gelesen werden. "
                "Bitte prüfen Sie das Format (Delimiter, Encoding)."
            )
            return {
                'success': False,
                'errors': errors,
                'dataframe': None,
                'info': info
            }
        
        info['rows'] = len(df)
        info['columns'] = len(df.columns)
        
        return {
            'success': True,
            'errors': [],
            'dataframe': df,
            'info': info
        }
        
    except Exception as e:
        errors.append(f"Fehler beim Parsen der CSV-Datei: {str(e)}")
        return {
            'success': False,
            'errors': errors,
            'dataframe': None,
            'info': info
        }


def _parse_excel_file(file_content: bytes) -> Dict[str, Any]:
    """
    Parst eine Excel-Datei und gibt DataFrame zurück
    
    Requirements: 2.2, 3.3
    """
    errors = []
    info = {}
    
    try:
        # Lese Excel-Datei
        df = pd.read_excel(
            io.BytesIO(file_content),
            index_col=0,
            engine='openpyxl'
        )
        
        info['rows'] = len(df)
        info['columns'] = len(df.columns)
        info['format'] = 'Excel (XLSX)'
        
        return {
            'success': True,
            'errors': [],
            'dataframe': df,
            'info': info
        }
        
    except Exception as e:
        errors.append(f"Fehler beim Parsen der Excel-Datei: {str(e)}")
        return {
            'success': False,
            'errors': errors,
            'dataframe': None,
            'info': info
        }


def _validate_matrix_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validiert die Struktur einer Matrix (DataFrame)
    
    Prüfungen:
    - Erste Spalte (Index) enthält numerische Werte (Modulanzahl)
    - Spaltenüberschriften sind vorhanden
    - Mindestens eine "Ohne Speicher" Spalte
    - Preis-Zellen enthalten numerische Werte
    
    Requirements: 2.2
    """
    errors = []
    warnings = []
    info = {}
    
    # Prüfe ob DataFrame leer ist
    if df.empty:
        errors.append("Matrix ist leer - keine Daten vorhanden")
        return {'errors': errors, 'warnings': warnings, 'info': info}
    
    # Prüfe Index (Modulanzahl)
    index_errors = _validate_index_numeric(df)
    errors.extend(index_errors)
    
    # Prüfe Spaltenüberschriften
    column_errors = _validate_column_headers(df)
    errors.extend(column_errors)
    
    # Prüfe "Ohne Speicher" Spalte
    no_storage_result = _find_no_storage_column(df)
    if not no_storage_result['found']:
        errors.append(
            'Keine "Ohne Speicher" Spalte gefunden. '
            'Mindestens eine Spalte muss "Kein Speicher", "Ohne Speicher" oder ähnlich heißen.'
        )
    else:
        info['no_storage_column'] = no_storage_result['column_name']
    
    # Prüfe Preis-Zellen
    price_errors, price_warnings = _validate_price_cells(df)
    errors.extend(price_errors)
    warnings.extend(price_warnings)
    
    # Zusätzliche Informationen
    info['module_counts'] = _extract_module_counts_from_df(df)
    info['storage_models'] = list(df.columns)
    info['total_cells'] = df.size
    info['empty_cells'] = df.isna().sum().sum()
    
    # Warnungen
    if len(df) < 2:
        warnings.append('Matrix hat nur eine Zeile. Mindestens 2 Zeilen empfohlen.')
    
    if len(df.columns) < 2:
        warnings.append('Matrix hat nur eine Spalte. Mindestens 2 Spalten empfohlen.')
    
    if info['empty_cells'] > 0:
        warnings.append(
            f'{info["empty_cells"]} Zellen sind leer. '
            'Dies kann zu Fehlern bei der Preisberechnung führen.'
        )
    
    return {
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def _validate_index_numeric(df: pd.DataFrame) -> List[str]:
    """
    Validiert dass der Index numerische Werte enthält (Modulanzahl)
    
    Requirements: 2.2
    """
    errors = []
    
    non_numeric_indices = []
    for idx in df.index:
        try:
            float(str(idx).replace(',', '.'))
        except (ValueError, TypeError):
            non_numeric_indices.append(str(idx))
    
    if non_numeric_indices:
        errors.append(
            f"Index (erste Spalte) muss numerische Werte (Modulanzahl) enthalten. "
            f"Folgende Werte sind nicht numerisch: {', '.join(non_numeric_indices[:5])}"
        )
        if len(non_numeric_indices) > 5:
            errors[-1] += f" ... und {len(non_numeric_indices) - 5} weitere"
    
    return errors


def _validate_column_headers(df: pd.DataFrame) -> List[str]:
    """
    Validiert dass Spaltenüberschriften vorhanden sind
    
    Requirements: 2.2
    """
    errors = []
    
    # Prüfe ob Spaltenüberschriften leer sind
    empty_columns = []
    for col in df.columns:
        if pd.isna(col) or str(col).strip() == '':
            empty_columns.append(f"Spalte {df.columns.get_loc(col) + 1}")
    
    if empty_columns:
        errors.append(
            f"Folgende Spalten haben keine Überschrift: {', '.join(empty_columns)}"
        )
    
    return errors


def _find_no_storage_column(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Sucht nach einer "Ohne Speicher" Spalte
    
    Requirements: 2.2
    """
    no_storage_keywords = [
        'kein speicher',
        'ohne speicher',
        'no storage',
        'none',
        'kein',
        'ohne'
    ]
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        for keyword in no_storage_keywords:
            if keyword in col_lower:
                return {
                    'found': True,
                    'column_name': col
                }
    
    return {'found': False}


def _validate_price_cells(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Validiert dass Preis-Zellen numerische Werte enthalten
    
    Requirements: 2.2
    """
    errors = []
    warnings = []
    
    non_numeric_cells = []
    
    for row_idx in df.index:
        for col in df.columns:
            value = df.loc[row_idx, col]
            
            if pd.notna(value):
                try:
                    float(str(value).replace(',', '.'))
                except (ValueError, TypeError):
                    cell_ref = f"{col} / {row_idx}"
                    non_numeric_cells.append(f"{cell_ref} ('{value}')")
    
    if non_numeric_cells:
        errors.append(
            f"Preis-Zellen müssen numerische Werte enthalten. "
            f"Folgende Zellen sind ungültig: {', '.join(non_numeric_cells[:5])}"
        )
        if len(non_numeric_cells) > 5:
            errors[-1] += f" ... und {len(non_numeric_cells) - 5} weitere"
    
    return errors, warnings


def _extract_module_counts_from_df(df: pd.DataFrame) -> List[float]:
    """Extrahiert Modulanzahlen aus DataFrame-Index"""
    module_counts = []
    
    for idx in df.index:
        try:
            count = float(str(idx).replace(',', '.'))
            module_counts.append(count)
        except (ValueError, TypeError):
            pass
    
    return sorted(module_counts)


def render_matrix_upload_ui():
    """
    Rendert die Upload-UI für Preismatrizen im Admin Panel
    
    Features:
    - Datei-Upload (CSV/Excel)
    - Vorschau-Validierung
    - Struktur-Prüfung
    - Aussagekräftige Fehlermeldungen
    
    Requirements: 2.1, 2.2, 2.4
    """
    st.subheader("📤 Preismatrix hochladen")
    
    # Hilfetext
    with st.expander("ℹ️ Hilfe: Matrix-Struktur", expanded=False):
        st.markdown(EXAMPLE_MATRIX_STRUCTURE)
    
    # Datei-Upload
    uploaded_file = st.file_uploader(
        "Wählen Sie eine Preismatrix-Datei",
        type=['csv', 'xlsx', 'xls'],
        help="Unterstützte Formate: CSV, Excel (XLSX, XLS)",
        key="price_matrix_upload"
    )
    
    if uploaded_file is not None:
        # Bestimme Dateityp
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_type = 'excel' if file_extension in ['xlsx', 'xls'] else 'csv'
        
        # Lese Dateiinhalt
        file_content = uploaded_file.read()
        
        # Validiere Datei
        with st.spinner("Validiere Datei..."):
            validation_result = validate_uploaded_file(file_content, file_type)
        
        # Zeige Validierungsergebnis
        if validation_result['valid']:
            st.success("✓ Datei ist gültig und kann importiert werden")
        else:
            st.error("✗ Datei enthält Fehler und kann nicht importiert werden")
        
        # Zeige Fehler
        if validation_result['errors']:
            st.error("**Fehler:**")
            for error in validation_result['errors']:
                st.error(f"• {error}")
        
        # Zeige Warnungen
        if validation_result['warnings']:
            st.warning("**Warnungen:**")
            for warning in validation_result['warnings']:
                st.warning(f"⚠ {warning}")
        
        # Zeige Informationen
        if validation_result['info']:
            st.info("**Datei-Informationen:**")
            info = validation_result['info']
            
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
                st.success(f"✓ 'Ohne Speicher' Spalte gefunden: **{info['no_storage_column']}**")
            
            if 'module_counts' in info and info['module_counts']:
                counts_str = ', '.join(str(int(c)) for c in info['module_counts'][:10])
                if len(info['module_counts']) > 10:
                    counts_str += f" ... ({len(info['module_counts'])} gesamt)"
                st.info(f"📊 Modulanzahlen: {counts_str}")
            
            if 'storage_models' in info and info['storage_models']:
                models_str = ', '.join(str(m) for m in info['storage_models'][:5])
                if len(info['storage_models']) > 5:
                    models_str += f" ... ({len(info['storage_models'])} gesamt)"
                st.info(f"🔋 Speichermodelle: {models_str}")
        
        # Zeige Vorschau
        if validation_result['preview_df'] is not None:
            st.markdown("---")
            st.markdown("### 👁️ Vorschau")
            
            preview_df = validation_result['preview_df']
            
            # Zeige nur erste 10 Zeilen
            display_df = preview_df.head(10)
            st.dataframe(display_df, use_container_width=True)
            
            if len(preview_df) > 10:
                st.caption(f"Zeige 10 von {len(preview_df)} Zeilen")
        
        # Import-Formular (nur wenn gültig)
        if validation_result['valid']:
            st.markdown("---")
            
            with st.form("matrix_import_form"):
                st.markdown("### 💾 Matrix importieren")
                
                matrix_name = st.text_input(
                    "Matrix-Name",
                    value=f"Import {uploaded_file.name}",
                    help="Name für die neue Matrix"
                )
                
                matrix_description = st.text_area(
                    "Beschreibung (optional)",
                    value=f"Importiert aus {uploaded_file.name}",
                    help="Optionale Beschreibung der Matrix"
                )
                
                set_as_active = st.checkbox(
                    "Als aktive Matrix setzen",
                    value=True,
                    help="Wenn aktiviert, wird diese Matrix sofort für Berechnungen verwendet"
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
                        with st.spinner("Importiere Matrix..."):
                            # Konvertiere DataFrame zu CSV für Import
                            csv_buffer = io.StringIO()
                            validation_result['preview_df'].to_csv(csv_buffer, sep=';')
                            csv_data = csv_buffer.getvalue()
                            
                            # Importiere Matrix
                            matrix_id = import_matrix_csv(
                                matrix_name,
                                csv_data,
                                delimiter=';'
                            )
                            
                            if matrix_id:
                                st.success(f"✓ Matrix '{matrix_name}' erfolgreich importiert (ID: {matrix_id})")
                                
                                # Setze als aktiv wenn gewünscht
                                if set_as_active:
                                    if set_active_matrix(matrix_id):
                                        st.success("✓ Matrix als aktiv gesetzt")
                                    else:
                                        st.warning("⚠ Matrix konnte nicht als aktiv gesetzt werden")
                                
                                # Validiere importierte Matrix
                                st.info("Validiere importierte Matrix...")
                                validation = validate_matrix_for_pricing(matrix_id)
                                
                                if validation['valid']:
                                    st.success("✓ Importierte Matrix ist gültig für Preisberechnung")
                                else:
                                    st.warning("⚠ Importierte Matrix hat Validierungsprobleme:")
                                    for error in validation['errors']:
                                        st.warning(f"• {error}")
                                
                                # Zeige Zusammenfassung
                                st.markdown("---")
                                st.markdown("### 📋 Import-Zusammenfassung")
                                st.code(get_validation_summary(validation))
                                
                                # Rerun um Upload-Widget zurückzusetzen
                                st.rerun()
                            else:
                                st.error("✗ Fehler beim Importieren der Matrix")
                    
                    except Exception as e:
                        st.error(f"✗ Fehler beim Importieren: {str(e)}")
                        st.exception(e)


def render_matrix_list_ui():
    """
    Rendert eine Liste aller Matrizen mit Validierungsstatus
    
    Requirements: 2.4
    """
    st.subheader("📊 Vorhandene Matrizen")
    
    matrices = list_matrices()
    
    if not matrices:
        st.info("Keine Matrizen vorhanden. Laden Sie eine Matrix hoch, um zu beginnen.")
        return
    
    for matrix in matrices:
        with st.expander(
            f"{'🟢' if matrix['is_active'] else '⚪'} {matrix['name']}",
            expanded=matrix['is_active']
        ):
            # Matrix-Informationen
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ID", matrix['id'])
            with col2:
                st.metric("Status", "Aktiv" if matrix['is_active'] else "Inaktiv")
            with col3:
                st.metric("Modus", matrix.get('pricing_mode', 'pauschal'))
            
            if matrix.get('description'):
                st.info(f"📝 {matrix['description']}")
            
            # Validierung
            if st.button(f"🔍 Validieren", key=f"validate_{matrix['id']}"):
                with st.spinner("Validiere Matrix..."):
                    validation = validate_matrix_for_pricing(matrix['id'])
                
                if validation['valid']:
                    st.success("✓ Matrix ist gültig")
                else:
                    st.error("✗ Matrix hat Validierungsprobleme")
                
                st.code(get_validation_summary(validation))
            
            # Aktionen
            col1, col2 = st.columns(2)
            with col1:
                if not matrix['is_active']:
                    if st.button(f"✓ Aktivieren", key=f"activate_{matrix['id']}"):
                        if set_active_matrix(matrix['id']):
                            st.success("Matrix aktiviert")
                            st.rerun()
                        else:
                            st.error("Fehler beim Aktivieren")


__all__ = [
    'validate_uploaded_file',
    'render_matrix_upload_ui',
    'render_matrix_list_ui'
]
