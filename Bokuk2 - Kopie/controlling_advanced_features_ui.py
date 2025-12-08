"""
Streamlit UI für Team-Auswertung, Mitarbeiter-Vergleich und PDF-Farbeinstellungen
"""

import streamlit as st
from datetime import date, timedelta
from pathlib import Path
import sys

def format_german_date(date_obj):
    """Formatiert Datum als 'Wochentag, der TT.MM.JJJJ' z.B. 'Montag, der 30.12.2025'"""
    if isinstance(date_obj, str):
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except:
            return date_obj
    
    weekday_names = {
        0: 'Montag',
        1: 'Dienstag',
        2: 'Mittwoch',
        3: 'Donnerstag',
        4: 'Freitag',
        5: 'Samstag',
        6: 'Sonntag'
    }
    
    weekday = weekday_names.get(date_obj.weekday(), 'Unbekannt')
    return f"{weekday}, der {date_obj.strftime('%d.%m.%Y')}"

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal
from controlling.models import Employee, Position
from controlling.team_analytics import TeamAnalytics
from controlling.report_generator import ReportGenerator
from controlling.pdf_config import (
    get_pdf_config_manager,
    PDFColorScheme,
    get_color_scheme
)


def render_team_analysis_tab():
    """Rendere Team-Auswertungs-Tab."""
    st.header("Team-Auswertung")
    st.markdown("---")
    
    db = SessionLocal()
    try:
        # Hole alle Positionen
        positions = db.query(Position).all()
        
        if not positions:
            st.warning("Keine Positionen gefunden. Bitte erst Positionen erstellen.")
            return
        
        # Position auswählen
        col1, col2 = st.columns(2)
        
        with col1:
            position_names = {pos.name: pos.id for pos in positions}
            selected_position_name = st.selectbox(
                "Position wählen",
                options=list(position_names.keys()),
                key="team_position_select"
            )
            position_id = position_names[selected_position_name]
        
        with col2:
            include_inactive = st.checkbox(
                "Inaktive Mitarbeiter einbeziehen",
                value=False,
                key="team_include_inactive"
            )
        
        # Zeitraum
        st.subheading("Zeitraum")
        col3, col4 = st.columns(2)
        
        with col3:
            start_date = st.date_input(
                "Von",
                value=date.today() - timedelta(days=30),
                key="team_start_date"
            )
        
        with col4:
            end_date = st.date_input(
                "Bis",
                value=date.today(),
                key="team_end_date"
            )
        
        # Auswertung erstellen
        if st.button("Team-Auswertung erstellen", type="primary", key="create_team_report"):
            with st.spinner("Erstelle Team-Auswertung..."):
                try:
                    team_analytics = TeamAnalytics(db)
                    team_data = team_analytics.generate_team_report(
                        position_id=position_id,
                        start_date=start_date,
                        end_date=end_date,
                        include_inactive=include_inactive
                    )
                    
                    # Speichere in Session State
                    st.session_state['team_report_data'] = team_data
                    st.success(f"Team-Auswertung erstellt für {team_data['employee_count']} Mitarbeiter!")
                    
                except Exception as e:
                    st.error(f"Fehler beim Erstellen der Team-Auswertung: {e}")
                    return
        
        # Zeige Auswertung
        if 'team_report_data' in st.session_state:
            team_data = st.session_state['team_report_data']
            
            st.markdown("---")
            st.subheading("Überschrift Ergebnisse")
            
            # Team-Quotas
            st.write("**Team-Leistungsquoten (Gesamt)**")
            team_quotas = team_data.get('team_quotas', {})
            
            if team_quotas:
                cols = st.columns(len(team_quotas))
                for i, (quota_name, quota_value) in enumerate(team_quotas.items()):
                    with cols[i]:
                        st.metric(
                            label=quota_name,
                            value=f"{quota_value:.2f}%"
                        )
            
            # Statistiken
            st.markdown("---")
            st.write("**Statistiken & Leistungsvergleich**")
            
            statistics = team_data.get('statistics', {})
            quota_stats = statistics.get('quota_statistics', {})
            
            if quota_stats:
                for quota_name, stats in quota_stats.items():
                    with st.expander(f"{quota_name}"):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Durchschnitt", f"{stats['average']:.2f}%")
                            st.metric("Minimum", f"{stats['min']:.2f}%")
                        
                        with col_b:
                            st.metric("Maximum", f"{stats['max']:.2f}%")
                            st.info(f"**Bester:** {stats['best_performer']}")
                        
                        with col_c:
                            st.warning(f"**Schlechtester:** {stats['worst_performer']}")
            
            # Einzelne Mitarbeiter
            st.markdown("---")
            st.write("**Einzelne Mitarbeiter**")
            
            employees = team_data.get('employees', [])
            
            for emp in employees:
                emp_name = emp.get('name', 'N/A')
                if emp.get('agent_name'):
                    emp_name += f" ({emp.get('agent_name')})"
                
                with st.expander(f"{emp_name}"):
                    emp_quotas = emp.get('quotas', {})
                    
                    if emp_quotas:
                        emp_cols = st.columns(len(emp_quotas))
                        for i, (quota_name, quota_value) in enumerate(emp_quotas.items()):
                            with emp_cols[i]:
                                st.metric(quota_name, f"{quota_value:.2f}%")
            
            # PDF Export
            st.markdown("---")
            col_export1, col_export2 = st.columns([3, 1])
            
            with col_export1:
                st.write("**Export**")
            
            with col_export2:
                if st.button("Als PDF exportieren", key="export_team_pdf"):
                    try:
                        report_gen = ReportGenerator(db)
                        pdf_bytes = report_gen.export_team_report_to_pdf(team_data)
                        
                        st.download_button(
                            label="PDF herunterladen",
                            data=pdf_bytes,
                            file_name=f"team_auswertung_{selected_position_name}_{date.today()}.pdf",
                            mime="application/pdf",
                            key="download_team_pdf"
                        )
                        st.success("PDF erfolgreich erstellt!")
                    
                    except Exception as e:
                        st.error(f"Fehler beim PDF-Export: {e}")
    
    finally:
        db.close()


def render_comparison_tab():
    """Rendere Mitarbeiter-Vergleichs-Tab."""
    st.header("Mitarbeiter-Vergleich")
    st.markdown("---")
    
    db = SessionLocal()
    try:
        # Hole alle Positionen
        positions = db.query(Position).all()
        
        if not positions:
            st.warning("Keine Positionen gefunden.")
            return
        
        # Position-Filter (optional)
        col1, col2 = st.columns(2)
        
        with col1:
            filter_by_position = st.checkbox(
                "Nach Position filtern",
                value=True,
                key="comp_filter_position"
            )
        
        with col2:
            if filter_by_position:
                position_names = {pos.name: pos.id for pos in positions}
                selected_position_name = st.selectbox(
                    "Position",
                    options=list(position_names.keys()),
                    key="comp_position_select"
                )
                position_id = position_names[selected_position_name]
            else:
                position_id = None
        
        # Hole Mitarbeiter
        if position_id:
            employees = db.query(Employee).filter(
                Employee.position_id == position_id,
                Employee.is_active == True
            ).all()
        else:
            employees = db.query(Employee).filter(
                Employee.is_active == True
            ).all()
        
        if not employees:
            st.warning("Keine Mitarbeiter gefunden.")
            return
        
        # Mitarbeiter auswählen
        st.subheading("Mitarbeiter wählen (mindestens 2)")
        
        employee_options = {f"{emp.full_name} ({emp.position.name})": emp.id for emp in employees}
        
        selected_employees = st.multiselect(
            "Mitarbeiter",
            options=list(employee_options.keys()),
            key="comp_employee_select"
        )
        
        if len(selected_employees) < 2:
            st.info("👆 Bitte mindestens 2 Mitarbeiter auswählen")
        
        # Zeitraum
        st.subheading("Zeitraum")
        col3, col4 = st.columns(2)
        
        with col3:
            start_date = st.date_input(
                "Von",
                value=date.today() - timedelta(days=30),
                key="comp_start_date"
            )
        
        with col4:
            end_date = st.date_input(
                "Bis",
                value=date.today(),
                key="comp_end_date"
            )
        
        # Vergleich erstellen
        if st.button(
            "Vergleich erstellen",
            type="primary",
            disabled=len(selected_employees) < 2,
            key="create_comparison"
        ):
            employee_ids = [employee_options[name] for name in selected_employees]
            
            with st.spinner("Erstelle Vergleich..."):
                try:
                    team_analytics = TeamAnalytics(db)
                    comparison_data = team_analytics.generate_comparison_report(
                        employee_ids=employee_ids,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Speichere in Session State
                    st.session_state['comparison_data'] = comparison_data
                    st.success(f"Vergleich erstellt für {len(selected_employees)} Mitarbeiter!")
                    
                except Exception as e:
                    st.error(f"Fehler beim Erstellen des Vergleichs: {e}")
                    return
        
        # Zeige Vergleich
        if 'comparison_data' in st.session_state:
            comp_data = st.session_state['comparison_data']
            
            st.markdown("---")
            st.subheading("Vergleichsergebnisse")
            
            # Rankings
            comparison_stats = comp_data.get('comparison_statistics', {})
            rankings = comparison_stats.get('rankings', {})
            
            if rankings:
                st.write("**Leistungsranking**")
                
                for quota_name, ranking_list in rankings.items():
                    with st.expander(f"{quota_name}"):
                        # Erstelle Ranking-Tabelle
                        for item in ranking_list:
                            rank_marker = ""
                            if item['rank'] == 1:
                                rank_marker = "[1.]"
                            elif item['rank'] == 2:
                                rank_marker = "[2.]"
                            elif item['rank'] == 3:
                                rank_marker = "[3.]"
                            else:
                                rank_marker = f"[{item['rank']}.]"
                            
                            st.write(f"{rank_marker} **{item['name']}**: **{item['value']:.2f}%**")
            
            # Unterschiede
            differences = comparison_stats.get('differences', {})
            
            if differences:
                st.markdown("---")
                st.write("**Leistungsunterschiede**")
                
                for quota_name, diff_info in differences.items():
                    with st.expander(f"{quota_name}"):
                        col_diff1, col_diff2, col_diff3 = st.columns(3)
                        
                        with col_diff1:
                            st.success(f"**Bester:** {diff_info['leader']}")
                            st.metric("Wert", f"{diff_info['leader_value']:.2f}%")
                        
                        with col_diff2:
                            st.error(f"**Schlechtester:** {diff_info['last']}")
                            st.metric("Wert", f"{diff_info['last_value']:.2f}%")
                        
                        with col_diff3:
                            st.info("**Differenz**")
                            st.metric("Absolut", f"{diff_info['difference']:.2f}%")
                            if diff_info['last_value'] > 0:
                                st.metric("Relativ", f"{diff_info['difference_percent']:.1f}%")
            
            # PDF Export
            st.markdown("---")
            col_export1, col_export2 = st.columns([3, 1])
            
            with col_export1:
                st.write("**Export**")
            
            with col_export2:
                if st.button("Als PDF exportieren", key="export_comp_pdf"):
                    try:
                        report_gen = ReportGenerator(db)
                        pdf_bytes = report_gen.export_comparison_report_to_pdf(comp_data)
                        
                        st.download_button(
                            label="PDF herunterladen",
                            data=pdf_bytes,
                            file_name=f"mitarbeiter_vergleich_{date.today()}.pdf",
                            mime="application/pdf",
                            key="download_comp_pdf"
                        )
                        st.success("PDF erfolgreich erstellt!")
                    
                    except Exception as e:
                        st.error(f"Fehler beim PDF-Export: {e}")
    
    finally:
        db.close()


def render_pdf_color_settings():
    """Rendere PDF-Farbeinstellungs-Tab."""
    st.header("PDF-Farbeinstellungen")
    st.markdown("---")
    
    config_manager = get_pdf_config_manager()
    current_scheme = config_manager.color_scheme
    
    # Tabs für verschiedene Einstellungsoptionen
    tab1, tab2, tab3 = st.tabs(["Vordefinierte Schemata", "Individuelle Farben", "Vorschau"])
    
    with tab1:
        st.subheading("Vordefinierte Farbschemata")
        
        predefined_schemes = config_manager.get_predefined_schemes()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_scheme_name = st.selectbox(
                "Schema wählen",
                options=list(predefined_schemes.keys()),
                key="predefined_scheme_select"
            )
        
        with col2:
            if st.button("Schema anwenden", key="apply_predefined_scheme"):
                if config_manager.apply_predefined_scheme(selected_scheme_name):
                    st.success(f"Schema '{selected_scheme_name}' erfolgreich angewendet!")
                    st.rerun()
                else:
                    st.error("Fehler beim Anwenden des Schemas")
        
        # Zeige Vorschau des gewählten Schemas
        preview_scheme = predefined_schemes[selected_scheme_name]
        
        st.write("**Vorschau:**")
        preview_cols = st.columns(4)
        
        with preview_cols[0]:
            st.markdown(f"**Primärfarbe**")
            st.color_picker("", value=preview_scheme.primary_color, disabled=True, key="preview_primary")
        
        with preview_cols[1]:
            st.markdown(f"**Sekundärfarbe**")
            st.color_picker("", value=preview_scheme.secondary_color, disabled=True, key="preview_secondary")
        
        with preview_cols[2]:
            st.markdown(f"**Tabellen-Header**")
            st.color_picker("", value=preview_scheme.table_header_bg, disabled=True, key="preview_header")
        
        with preview_cols[3]:
            st.markdown(f"**Tabellenzeilen**")
            st.color_picker("", value=preview_scheme.table_row_bg, disabled=True, key="preview_row")
    
    with tab2:
        st.subheading("Individuelle Farbanpassung")
        
        # Hauptfarben
        st.write("**Hauptfarben**")
        col_main1, col_main2 = st.columns(2)
        
        with col_main1:
            new_primary = st.color_picker(
                "Primärfarbe",
                value=current_scheme.primary_color,
                key="custom_primary"
            )
        
        with col_main2:
            new_secondary = st.color_picker(
                "Sekundärfarbe",
                value=current_scheme.secondary_color,
                key="custom_secondary"
            )
        
        # Textfarben
        st.write("**Textfarben**")
        col_text1, col_text2, col_text3 = st.columns(3)
        
        with col_text1:
            new_title_color = st.color_picker(
                "Titel",
                value=current_scheme.title_color,
                key="custom_title"
            )
        
        with col_text2:
            new_text_color = st.color_picker(
                "Text",
                value=current_scheme.text_color,
                key="custom_text"
            )
        
        with col_text3:
            new_header_text = st.color_picker(
                "Header-Text",
                value=current_scheme.header_text_color,
                key="custom_header_text"
            )
        
        # Hintergrundfarben
        st.write("**Hintergrundfarben**")
        col_bg1, col_bg2, col_bg3 = st.columns(3)
        
        with col_bg1:
            new_table_header_bg = st.color_picker(
                "Tabellen-Header",
                value=current_scheme.table_header_bg,
                key="custom_table_header"
            )
        
        with col_bg2:
            new_table_row_bg = st.color_picker(
                "Tabellenzeilen",
                value=current_scheme.table_row_bg,
                key="custom_table_row"
            )
        
        with col_bg3:
            new_table_alt_row_bg = st.color_picker(
                "Alternative Zeilen",
                value=current_scheme.table_alt_row_bg,
                key="custom_alt_row"
            )
        
        # Akzentfarben
        st.write("**Akzentfarben**")
        col_accent1, col_accent2, col_accent3, col_accent4 = st.columns(4)
        
        with col_accent1:
            new_success = st.color_picker(
                "Erfolg",
                value=current_scheme.success_color,
                key="custom_success"
            )
        
        with col_accent2:
            new_warning = st.color_picker(
                "Warnung",
                value=current_scheme.warning_color,
                key="custom_warning"
            )
        
        with col_accent3:
            new_error = st.color_picker(
                "Fehler",
                value=current_scheme.error_color,
                key="custom_error"
            )
        
        with col_accent4:
            new_info = st.color_picker(
                "Info",
                value=current_scheme.info_color,
                key="custom_info"
            )
        
        # Rahmen & Linien
        st.write("**Rahmen & Linien**")
        col_border1, col_border2 = st.columns(2)
        
        with col_border1:
            new_border = st.color_picker(
                "Rahmen",
                value=current_scheme.border_color,
                key="custom_border"
            )
        
        with col_border2:
            new_grid = st.color_picker(
                "Rasterlinien",
                value=current_scheme.grid_color,
                key="custom_grid"
            )
        
        # Speichern
        st.markdown("---")
        col_save1, col_save2, col_save3 = st.columns([2, 1, 1])
        
        with col_save2:
            if st.button("Farben speichern", type="primary", key="save_custom_colors"):
                new_scheme = PDFColorScheme(
                    primary_color=new_primary,
                    secondary_color=new_secondary,
                    title_color=new_title_color,
                    text_color=new_text_color,
                    header_text_color=new_header_text,
                    table_header_bg=new_table_header_bg,
                    table_row_bg=new_table_row_bg,
                    table_alt_row_bg=new_table_alt_row_bg,
                    success_color=new_success,
                    warning_color=new_warning,
                    error_color=new_error,
                    info_color=new_info,
                    border_color=new_border,
                    grid_color=new_grid
                )
                
                if config_manager.save_color_scheme(new_scheme):
                    st.success("Farben erfolgreich gespeichert!")
                    st.rerun()
                else:
                    st.error("Fehler beim Speichern")
        
        with col_save3:
            if st.button("Auf Standard zurücksetzen", key="reset_colors"):
                if config_manager.reset_to_default():
                    st.success("Auf Standard zurückgesetzt!")
                    st.rerun()
    
    with tab3:
        st.subheading("Farbschema-Vorschau")
        
        st.write("**Aktuelles Farbschema:**")
        
        # Farben-Grid
        preview_data = [
            ("Primärfarbe", current_scheme.primary_color),
            ("Sekundärfarbe", current_scheme.secondary_color),
            ("Titel", current_scheme.title_color),
            ("Text", current_scheme.text_color),
            ("Header-Text", current_scheme.header_text_color),
            ("Tabellen-Header", current_scheme.table_header_bg),
            ("Tabellenzeilen", current_scheme.table_row_bg),
            ("Alt. Zeilen", current_scheme.table_alt_row_bg),
            ("Erfolg", current_scheme.success_color),
            ("Warnung", current_scheme.warning_color),
            ("Fehler", current_scheme.error_color),
            ("Info", current_scheme.info_color),
            ("Rahmen", current_scheme.border_color),
            ("Raster", current_scheme.grid_color),
        ]
        
        cols_per_row = 4
        for i in range(0, len(preview_data), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(preview_data):
                    name, color = preview_data[i + j]
                    with col:
                        st.markdown(f"**{name}**")
                        st.markdown(
                            f'<div style="background-color: {color}; '
                            f'width: 100%; height: 60px; border: 1px solid #ccc; '
                            f'border-radius: 5px;"></div>',
                            unsafe_allow_html=True
                        )
                        st.caption(color)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Controlling - Erweiterte Funktionen",
        layout="wide"
    )
    
    st.title("Controlling - Erweiterte Funktionen")
    
    tab1, tab2, tab3 = st.tabs([
        "Team-Auswertung",
        "Mitarbeiter-Vergleich",
        "PDF-Farben"
    ])
    
    with tab1:
        render_team_analysis_tab()
    
    with tab2:
        render_comparison_tab()
    
    with tab3:
        render_pdf_color_settings()
