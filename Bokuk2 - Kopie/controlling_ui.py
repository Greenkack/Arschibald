"""
Controlling Main UI

Main user interface for the Employee Controlling System.
Provides performance data entry, report generation, visualization, and export.

Requirements: 1.1, 1.2, 8.1, 8.2, 9.1, 12.4, 13.1, 16.1, 16.2
"""

import logging
import streamlit as st
from datetime import date, datetime
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal  # noqa: E402
from controlling.managers import (  # noqa: E402
    EmployeeManager,
    PositionManager,
    PerformanceDataManager,
    ValidationError
)
from controlling.models import ReportType  # noqa: E402
from controlling.models import (  # noqa: E402
    PeriodType,
    PeriodStatus,
    EvaluationPeriod,
    PerformanceData  # ← Für direkte DB-Abfragen
)
from controlling.report_generator import ReportGenerator  # noqa: E402
from controlling.chart_generator import ChartGenerator  # noqa: E402
from controlling.notifications import NotificationManager  # noqa: E402
from controlling.period_manager import PeriodManager  # noqa: E402
from controlling.team_analytics import TeamAnalytics  # noqa: E402
from controlling.pdf_config import (  # noqa: E402
    get_pdf_config_manager,
    PDFColorScheme,
    get_color_scheme
)

logger = logging.getLogger(__name__)


def render_controlling_page():
    """
    Main controlling page in Hauptmenü/Sidemenu.

    Requirements: 1.1, 1.2
    """
    st.header(" Controlling")
    st.caption("Mitarbeiterleistung erfassen, auswerten und visualisieren")

    # Initialize session state
    if 'controlling_selected_employees' not in st.session_state:
        st.session_state.controlling_selected_employees = []
    if 'controlling_filters' not in st.session_state:
        st.session_state.controlling_filters = {}
    if 'controlling_current_report' not in st.session_state:
        st.session_state.controlling_current_report = None
    if 'notification_manager' not in st.session_state:
        st.session_state.notification_manager = NotificationManager()
    if 'active_period_id' not in st.session_state:
        st.session_state.active_period_id = None
    if 'period_creation_mode' not in st.session_state:
        st.session_state.period_creation_mode = False

    # Create tabs
    tabs = st.tabs([
        "📝 Leistungsdaten erfassen",
        "📊 Berichte erstellen",
        "🏢 Team-Auswertung",
        "🔍 Mitarbeiter-Vergleich",
        "🏆 Rangliste",
        "🎨 PDF-Farben",
        "📁 Archiv"
    ])

    with tabs[0]:
        render_performance_entry_tab()

    with tabs[1]:
        render_report_generation_tab()

    with tabs[2]:
        render_team_analysis_tab()

    with tabs[3]:
        render_comparison_tab()

    with tabs[4]:
        render_ranking_tab()

    with tabs[5]:
        render_pdf_color_settings()

    with tabs[6]:
        render_archive_tab()


def render_performance_entry_tab():
    """
    Performance data entry form with evaluation period management.

    Requirements: 8.1, 8.2
    """
    st.subheader("📝 Leistungsdaten erfassen")

    db = SessionLocal()
    emp_manager = EmployeeManager(db)
    perf_manager = PerformanceDataManager(db)
    period_manager = PeriodManager(db)

    try:
        # ============ AUSWERTUNGSPERIODEN-VERWALTUNG ============
        st.markdown("### 🗓️ Auswertungsperiode")
        
        col_header1, col_header2 = st.columns([2, 1])
        
        with col_header1:
            st.caption("Wähle oder erstelle eine Auswertungsperiode für strukturierte Leistungserfassung")
        
        with col_header2:
            if st.button("➕ Neue Auswertung starten", key="btn_new_period", type="primary"):
                st.session_state.period_creation_mode = True
                st.rerun()
        
        # NEUE PERIODE ERSTELLEN
        if st.session_state.get('period_creation_mode', False):
            st.markdown("---")
            st.markdown("#### ✨ Neue Auswertungsperiode erstellen")
            
            with st.form("create_period_form", clear_on_submit=False):
                col_p1, col_p2 = st.columns(2)
                
                with col_p1:
                    period_type_options = {
                        "📅 Täglich": PeriodType.DAILY,
                        "📆 Wöchentlich": PeriodType.WEEKLY,
                        "📊 Monatlich": PeriodType.MONTHLY,
                        "📈 Quartalsweise": PeriodType.QUARTERLY,
                        "📉 Jährlich": PeriodType.YEARLY,
                        "🎯 Benutzerdefiniert": PeriodType.CUSTOM
                    }
                    
                    selected_type_label = st.selectbox(
                        "Zeitraum-Typ",
                        options=list(period_type_options.keys()),
                        key="new_period_type"
                    )
                    selected_period_type = period_type_options[selected_type_label]
                
                with col_p2:
                    period_name = st.text_input(
                        "Name der Auswertung",
                        placeholder="z.B. 'Dezember 2025' oder 'Q4 2025'",
                        key="new_period_name"
                    )
                
                # Automatische Datumsberechnung für Standard-Typen
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    if selected_period_type == PeriodType.MONTHLY:
                        month = st.selectbox(
                            "Monat",
                            options=list(range(1, 13)),
                            index=date.today().month - 1,
                            format_func=lambda x: [
                                "Januar", "Februar", "März", "April", "Mai", "Juni",
                                "Juli", "August", "September", "Oktober", "November", "Dezember"
                            ][x-1],
                            key="month_selector"
                        )
                        year = st.number_input("Jahr", min_value=2020, max_value=2030, value=date.today().year, key="year_selector_monthly")
                        
                        start_date = date(year, month, 1)
                        if month == 12:
                            end_date = date(year, 12, 31)
                        else:
                            from datetime import timedelta
                            end_date = date(year, month + 1, 1) - timedelta(days=1)
                        
                        st.date_input("Start (automatisch)", value=start_date, disabled=True, key="auto_start_monthly")
                    
                    elif selected_period_type == PeriodType.QUARTERLY:
                        quarter = st.selectbox("Quartal", options=[1, 2, 3, 4], key="quarter_selector")
                        year = st.number_input("Jahr", min_value=2020, max_value=2030, value=date.today().year, key="year_selector_quarterly")
                        
                        start_month = (quarter - 1) * 3 + 1
                        start_date = date(year, start_month, 1)
                        
                        from datetime import timedelta
                        end_month = start_month + 2
                        if end_month == 12:
                            end_date = date(year, 12, 31)
                        else:
                            end_date = date(year, end_month + 1, 1) - timedelta(days=1)
                        
                        st.date_input("Start (automatisch)", value=start_date, disabled=True, key="auto_start_quarterly")
                    
                    elif selected_period_type == PeriodType.YEARLY:
                        year = st.number_input("Jahr", min_value=2020, max_value=2030, value=date.today().year, key="year_selector_yearly")
                        start_date = date(year, 1, 1)
                        end_date = date(year, 12, 31)
                        st.date_input("Start (automatisch)", value=start_date, disabled=True, key="auto_start_yearly")
                    
                    else:
                        # Custom oder Täglich/Wöchentlich
                        start_date = st.date_input("Startdatum", value=date.today(), key="custom_start")
                
                with col_d2:
                    if selected_period_type in [PeriodType.MONTHLY, PeriodType.QUARTERLY, PeriodType.YEARLY]:
                        st.date_input("Ende (automatisch)", value=end_date, disabled=True, key="auto_end")
                    else:
                        if selected_period_type == PeriodType.WEEKLY:
                            from datetime import timedelta
                            default_end = start_date + timedelta(days=6)
                        elif selected_period_type == PeriodType.DAILY:
                            default_end = start_date
                        else:
                            default_end = start_date
                        
                        end_date = st.date_input("Enddatum", value=default_end, key="custom_end")
                
                period_description = st.text_area(
                    "Beschreibung (optional)",
                    placeholder="Zusätzliche Notizen oder Ziele für diese Auswertungsperiode",
                    key="new_period_description"
                )
                
                # Mitarbeiter-Zuordnung (optional)
                employees = emp_manager.list_employees()
                employee_options = {0: "Alle Mitarbeiter (global)"}
                employee_options.update({emp.id: emp.display_name for emp in employees})
                
                selected_emp_id = st.selectbox(
                    "Mitarbeiter",
                    options=list(employee_options.keys()),
                    format_func=lambda x: employee_options[x],
                    key="period_employee_selector"
                )
                
                col_submit1, col_submit2 = st.columns([1, 1])
                
                with col_submit1:
                    submitted = st.form_submit_button("✅ Periode erstellen", type="primary")
                
                with col_submit2:
                    cancelled = st.form_submit_button("❌ Abbrechen")
                
                if cancelled:
                    st.session_state.period_creation_mode = False
                    st.rerun()
                
                if submitted:
                    try:
                        # Auto-generate name if empty
                        if not period_name or not period_name.strip():
                            if selected_period_type == PeriodType.MONTHLY:
                                month_names = [
                                    "Januar", "Februar", "März", "April", "Mai", "Juni",
                                    "Juli", "August", "September", "Oktober", "November", "Dezember"
                                ]
                                period_name = f"{month_names[month - 1]} {year}"
                            elif selected_period_type == PeriodType.QUARTERLY:
                                period_name = f"Q{quarter} {year}"
                            elif selected_period_type == PeriodType.YEARLY:
                                period_name = f"Jahr {year}"
                            else:
                                period_name = f"Auswertung {start_date} - {end_date}"
                        
                        # Create period
                        new_period = period_manager.create_period(
                            name=period_name,
                            period_type=selected_period_type,
                            start_date=start_date,
                            end_date=end_date,
                            description=period_description.strip() if period_description else None,
                            employee_id=selected_emp_id if selected_emp_id > 0 else None
                        )
                        
                        st.success(f"✅ Auswertungsperiode '{new_period.name}' erfolgreich erstellt!")
                        st.session_state.active_period_id = new_period.id
                        st.session_state.period_creation_mode = False
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Fehler beim Erstellen der Periode: {e}")
                        logger.error(f"Error creating period: {e}")
            
            st.markdown("---")
        
        # BESTEHENDE PERIODEN ANZEIGEN
        active_periods = period_manager.get_active_periods()
        
        if active_periods:
            col_select1, col_select2 = st.columns([3, 1])
            
            with col_select1:
                period_options = {p.id: f"{p.name} ({p.start_date} - {p.end_date})" for p in active_periods}
                
                selected_period_id = st.selectbox(
                    "Aktive Auswertungsperiode wählen",
                    options=[None] + list(period_options.keys()),
                    format_func=lambda x: "Keine Periode (direkter Modus)" if x is None else period_options[x],
                    index=0 if st.session_state.active_period_id is None else (
                        list(period_options.keys()).index(st.session_state.active_period_id) + 1
                        if st.session_state.active_period_id in period_options else 0
                    ),
                    key="select_active_period"
                )
                
                if selected_period_id != st.session_state.active_period_id:
                    st.session_state.active_period_id = selected_period_id
            
            with col_select2:
                if selected_period_id and st.button("🗑️ Periode löschen", key="btn_delete_period"):
                    if period_manager.delete_period(selected_period_id):
                        st.success("Periode gelöscht!")
                        st.session_state.active_period_id = None
                        st.rerun()
            
            # Zeige Details der gewählten Periode
            if selected_period_id:
                current_period = period_manager.get_period(selected_period_id)
                if current_period:
                    st.info(
                        f"📅 **{current_period.name}**  \n"
                        f"Typ: {current_period.period_type.value} | "
                        f"Zeitraum: {current_period.start_date} - {current_period.end_date} | "
                        f"Dauer: {current_period.duration_days} Tage  \n"
                        f"{current_period.description if current_period.description else ''}"
                    )
        else:
            st.warning("⚠️ Keine aktiven Auswertungsperioden vorhanden. Erstelle eine neue Auswertung, um strukturiert Daten zu erfassen.")
        
        st.markdown("---")
        
        # ============ LEISTUNGSDATEN EINGABE ============
        st.markdown("### 📊 Leistungsdaten erfassen")

        # Employee selector
        employees = emp_manager.list_employees()

        if not employees:
            st.warning(
                "Keine Mitarbeiter vorhanden. "
                "Bitte erstellen Sie zuerst Mitarbeiter im Admin-Bereich."
            )
            return

        # Employee selection
        employee_options = {emp.id: emp.display_name for emp in employees}
        selected_emp_id = st.selectbox(
            "Mitarbeiter auswählen",
            options=list(employee_options.keys()),
            format_func=lambda x: employee_options[x],
            key="perf_entry_employee_selector"
        )

        if not selected_emp_id:
            return

        # Get selected employee
        employee = emp_manager.get_employee(selected_emp_id)

        if not employee or not employee.position:
            st.error("Mitarbeiter hat keine Position zugeordnet.")
            return

        # Get criteria for employee's position
        criteria = emp_manager.get_employee_criteria(selected_emp_id)

        if not criteria:
            st.warning(
                f"Keine Auswertungskriterien für Position "
                f"'{employee.position.name}' definiert."
            )
            return

        # Display employee info
        st.info(
            f"**{employee.full_name}** - {employee.position.name} "
            f"({len(criteria)} Kriterien)"
        )

        # Date selector
        entry_date = st.date_input(
            "Datum",
            value=date.today(),
            max_value=date.today(),
            key="perf_entry_date"
        )

        # ============ VORHANDENE DATEN LADEN ============
        # Lade gespeicherte Performance-Daten für diesen Mitarbeiter und Datum
        existing_data = perf_manager.get_performance_data(
            employee_id=selected_emp_id,
            start_date=entry_date,
            end_date=entry_date
        )
        
        # Erstelle Dictionary: criterion_id -> gespeicherter Wert
        existing_values = {}
        for perf_record in existing_data:
            existing_values[perf_record.criterion_id] = perf_record.value
        
        # Info anzeigen wenn Daten vorhanden
        if existing_values:
            st.info(
                f"ℹ️ **Gespeicherte Daten werden geladen** - "
                f"{len(existing_values)} Kriterien mit Werten vom {entry_date.strftime('%d.%m.%Y')}"
            )
        else:
            st.caption("Keine gespeicherten Daten für dieses Datum vorhanden")

        # Performance data entry form
        st.markdown("### Leistungsdaten eingeben")

        with st.form("performance_entry_form", clear_on_submit=False):
            performance_data = {}

            # Create input fields for each criterion
            cols = st.columns(2)
            for idx, criterion in enumerate(criteria):
                col = cols[idx % 2]
                with col:
                    # Bestimme ob das Kriterium nur ganze Zahlen erlauben sollte
                    integer_only_criteria = [
                        "Verkauf", "Kunden terminiert", "Angefahrene Termine",
                        "Angefahrene Termine gesamt", "Getätigte Anrufe gesamt",
                        "QC bestanden", "Storniert / kein Interesse",
                        "Nicht erreicht / neu terminieren", "Technisch nicht machbar",
                        "Nicht angefahrene Termine", "Folgetermin gemacht",
                        "Zu teuer gewesen", "Angebot erhalten"
                    ]
                    
                    is_integer_criterion = criterion.name in integer_only_criteria
                    
                    # WICHTIG: Lade gespeicherten Wert falls vorhanden
                    saved_value = existing_values.get(criterion.id, 0)
                    
                    if is_integer_criterion:
                        # Nur ganze Zahlen erlauben
                        value = st.number_input(
                            criterion.name,
                            min_value=0,
                            value=int(saved_value),  # ← Gespeicherter Wert!
                            step=1,
                            key=f"perf_input_{criterion.id}_{entry_date}_{selected_emp_id}",  # ← Unique Key!
                            help=criterion.description or "",
                            format="%d"
                        )
                    else:
                        # Dezimalzahlen erlaubt (für zukünftige erweiterte Kriterien)
                        value = st.number_input(
                            criterion.name,
                            min_value=0.0,
                            value=float(saved_value),  # ← Gespeicherter Wert!
                            step=0.1,
                            key=f"perf_input_{criterion.id}_{entry_date}_{selected_emp_id}",  # ← Unique Key!
                            help=criterion.description or ""
                        )
                    
                    performance_data[criterion.id] = value

            submitted = st.form_submit_button(
                "Leistungsdaten speichern",
                type="primary"
            )

            if submitted:
                try:
                    # Get active period ID from session
                    period_id = st.session_state.get('active_period_id')
                    
                    # Validate and save performance data
                    saved_count = 0
                    updated_count = 0
                    deleted_count = 0
                    validation_warnings = []
                    
                    for criterion_id, value in performance_data.items():
                        # Zusätzliche Validierung: Runde auf ganze Zahl für Zählkriterien
                        criterion = next((c for c in criteria if c.id == criterion_id), None)
                        if criterion:
                            integer_only_criteria = [
                                "Verkauf", "Kunden terminiert", "Angefahrene Termine",
                                "Angefahrene Termine gesamt", "Getätigte Anrufe gesamt",
                                "QC bestanden", "Storniert / kein Interesse",
                                "Nicht erreicht / neu terminieren", "Technisch nicht machbar",
                                "Nicht angefahrene Termine", "Folgetermin gemacht",
                                "Zu teuer gewesen", "Angebot erhalten"
                            ]
                            
                            if criterion.name in integer_only_criteria:
                                # Runde auf ganze Zahl und warne bei Abweichung
                                rounded_value = round(value)
                                if abs(value - rounded_value) > 0.01:
                                    validation_warnings.append(
                                        f"'{criterion.name}': {value:.2f} wurde auf {rounded_value} gerundet"
                                    )
                                value = float(rounded_value)
                        
                        # ============ UPDATE ODER INSERT LOGIK ============
                        # Prüfe ob bereits Daten für diesen Mitarbeiter/Kriterium/Datum existieren
                        existing_record = db.query(PerformanceData).filter(
                            PerformanceData.employee_id == selected_emp_id,
                            PerformanceData.criterion_id == criterion_id,
                            PerformanceData.date == entry_date
                        ).first()
                        
                        if value > 0:
                            # Wert > 0: Speichern oder aktualisieren
                            if existing_record:
                                # UPDATE: Vorhandenen Eintrag aktualisieren
                                if existing_record.value != value:
                                    perf_manager.update_performance(
                                        performance_id=existing_record.id,
                                        value=value
                                    )
                                    updated_count += 1
                            else:
                                # INSERT: Neuen Eintrag erstellen
                                perf_manager.record_performance(
                                    employee_id=selected_emp_id,
                                    criterion_id=criterion_id,
                                    value=value,
                                    date=entry_date,
                                    period_id=period_id
                                )
                                saved_count += 1
                        else:
                            # Wert = 0: Existierenden Eintrag löschen falls vorhanden
                            if existing_record:
                                db.delete(existing_record)
                                db.commit()
                                deleted_count += 1

                    # Zeige Validierungswarnungen an
                    if validation_warnings:
                        st.warning(
                            "⚠️ **Automatische Korrektur durchgeführt:**\n\n" +
                            "\n".join(f"- {w}" for w in validation_warnings) +
                            "\n\n*Hinweis: Zählkriterien erlauben nur ganze Zahlen!*"
                        )
                    
                    # Erfolgs-Nachricht mit Details
                    if saved_count > 0 or updated_count > 0 or deleted_count > 0:
                        success_parts = []
                        if saved_count > 0:
                            success_parts.append(f"**{saved_count} neu gespeichert**")
                        if updated_count > 0:
                            success_parts.append(f"**{updated_count} aktualisiert**")
                        if deleted_count > 0:
                            success_parts.append(f"**{deleted_count} gelöscht** (Wert = 0)")
                        
                        st.success(
                            f"✅ **Leistungsdaten gespeichert!**\n\n" +
                            " | ".join(success_parts) +
                            f"\n\n📅 Datum: {entry_date.strftime('%d.%m.%Y')}"
                        )
                        
                        # Seite neu laden um aktualisierte Daten anzuzeigen
                        st.rerun()
                    else:
                        st.info("ℹ️ Keine Änderungen - alle Werte sind 0 oder unverändert")

                except ValidationError as e:
                    st.error(f"❌ Validierungsfehler: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
                    logger.error(f"Error saving performance data: {e}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        logger.error(f"Error in performance entry tab: {e}")
    
    finally:
        db.close()


def render_report_generation_tab():
    """
    Report generation controls and visualization.

    Requirements: 9.1, 12.4, 13.1, 16.1, 16.2
    """
    st.subheader("Berichte erstellen und visualisieren")

    db = SessionLocal()
    emp_manager = EmployeeManager(db)
    report_gen = ReportGenerator(db)
    chart_gen = ChartGenerator()

    # Employee selector with filters
    st.markdown("### Mitarbeiter auswählen")

    try:
        employees = emp_manager.list_employees()

        if not employees:
            st.warning(
                "Keine Mitarbeiter vorhanden. "
                "Bitte erstellen Sie zuerst Mitarbeiter im Admin-Bereich."
            )
            return

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            # Position filter
            positions = set(
                emp.position.name for emp in employees
                if emp.position
            )
            position_filter = st.multiselect(
                "Nach Position filtern",
                options=sorted(positions),
                key="report_position_filter"
            )

        with col2:
            # City filter
            cities = set(emp.city for emp in employees)
            city_filter = st.multiselect(
                "Nach Wohnort filtern",
                options=sorted(cities),
                key="report_city_filter"
            )

        with col3:
            # Name search
            name_search = st.text_input(
                "Nach Name suchen",
                key="report_name_search"
            )

        # Apply filters
        filtered_employees = employees
        if position_filter:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp.position and emp.position.name in position_filter
            ]
        if city_filter:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp.city in city_filter
            ]
        if name_search:
            search_lower = name_search.lower()
            filtered_employees = [
                emp for emp in filtered_employees
                if search_lower in emp.full_name.lower() or (emp.agent_name and search_lower in emp.agent_name.lower())
            ]

        # Employee selection
        st.markdown("---")
        employee_options = {
            emp.id: f"{emp.display_name} - {emp.position.name if emp.position else 'Keine Position'}"
            for emp in filtered_employees
        }

        if not employee_options:
            st.info("Keine Mitarbeiter entsprechen den Filterkriterien.")
            return

        selected_emp_ids = st.multiselect(
            f"Mitarbeiter auswählen ({len(filtered_employees)} verfügbar)",
            options=list(employee_options.keys()),
            format_func=lambda x: employee_options[x],
            key="report_employee_selector"
        )

        if not selected_emp_ids:
            st.info("Bitte wählen Sie mindestens einen Mitarbeiter aus.")
            return

        # Report type and date range
        st.markdown("---")
        st.markdown("### Berichtszeitraum")

        col1, col2 = st.columns(2)

        with col1:
            report_type = st.selectbox(
                "Berichtstyp",
                options=[
                    ReportType.DAILY,
                    ReportType.WEEKLY,
                    ReportType.MONTHLY,
                    ReportType.QUARTERLY,
                    ReportType.YEARLY,
                    ReportType.SINCE_START
                ],
                format_func=lambda x: {
                    ReportType.DAILY: "Täglich",
                    ReportType.WEEKLY: "Wöchentlich",
                    ReportType.MONTHLY: "Monatlich",
                    ReportType.QUARTERLY: "Quartalsweise",
                    ReportType.YEARLY: "Jährlich",
                    ReportType.SINCE_START: "Seit Arbeitsbeginn"
                }.get(x, x.value),
                key="report_type_selector"
            )

        with col2:
            reference_date = st.date_input(
                "Referenzdatum",
                value=date.today(),
                max_value=date.today(),
                key="report_reference_date"
            )

        # Generate report button
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            generate_button = st.button(
                " Bericht erstellen",
                type="primary",
                use_container_width=True
            )

        # Generate report
        if generate_button:
            try:
                with st.spinner("Bericht wird erstellt..."):
                    is_comparison = len(selected_emp_ids) > 1

                    if not is_comparison:
                        # Single employee report
                        report_data = report_gen.generate_report(
                            employee_id=selected_emp_ids[0],
                            report_type=report_type,
                            end_date=reference_date
                        )
                    else:
                        # Comparison report
                        report_data = report_gen.generate_comparison_report(
                            employee_ids=selected_emp_ids,
                            report_type=report_type,
                            end_date=reference_date
                        )

                    # Store in session state
                    st.session_state.controlling_current_report = report_data

                    st.success(" Bericht erfolgreich erstellt!")

                    # Check for notifications
                    notification_manager = (
                        st.session_state.notification_manager
                    )
                    if not is_comparison and "quotas" in report_data:
                        employee_name = report_data.get("employee_name")
                        notifications = notification_manager.check_quotas(
                            report_data["quotas"],
                            employee_name=employee_name
                        )

                        # Display notifications
                        if notifications:
                            st.markdown("---")
                            st.markdown("###  Benachrichtigungen")
                            for notification in notifications:
                                (
                                    streamlit_type,
                                    title,
                                    message
                                ) = (
                                    notification_manager
                                    .format_notification_for_streamlit(
                                        notification
                                    )
                                )

                                if streamlit_type == "success":
                                    st.success(f"**{title}**\n\n{message}")
                                elif streamlit_type == "warning":
                                    st.warning(f"**{title}**\n\n{message}")
                                elif streamlit_type == "info":
                                    st.info(f"**{title}**\n\n{message}")
                                elif streamlit_type == "error":
                                    st.error(f"**{title}**\n\n{message}")

            except Exception as e:
                st.error(f"Fehler beim Erstellen des Berichts: {e}")
                logger.error(f"Error generating report: {e}")

        # Display report if available
        if st.session_state.controlling_current_report:
            render_report_dashboard(
                st.session_state.controlling_current_report,
                chart_gen,
                report_gen
            )

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        logger.error(f"Error in report generation tab: {e}")


def render_report_dashboard(
    report_data: Dict[str, Any],
    chart_gen: ChartGenerator,
    report_gen: ReportGenerator
):
    """
    Display report visualization dashboard.

    Requirements: 12.4
    """
    st.markdown("---")
    st.markdown("##  Berichtsvisualisierung")

    # Report metadata
    is_comparison = "employee_reports" in report_data

    if not is_comparison:
        st.info(
            f"**Mitarbeiter:** {report_data.get('employee_name')} | "
            f"**Position:** {report_data.get('position')} | "
            f"**Zeitraum:** {report_data.get('start_date')} bis "
            f"{report_data.get('end_date')}"
        )
    else:
        st.info(
            f"**Vergleichsbericht** | "
            f"**{report_data.get('employee_count')} Mitarbeiter** | "
            f"**Zeitraum:** {report_data.get('start_date')} bis "
            f"{report_data.get('end_date')}"
        )

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(" Bericht speichern", use_container_width=True):
            try:
                report_id = report_gen.save_report(
                    report_data,
                    is_comparison=is_comparison
                )
                st.success(f" Bericht gespeichert (ID: {report_id})")
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

    with col2:
        if st.button(" JSON Export", use_container_width=True):
            try:
                json_data = report_gen.export_report_json(report_data)
                st.download_button(
                    label="JSON herunterladen",
                    data=json_data,
                    file_name=f"bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Fehler beim Export: {e}")

    with col3:
        if st.button(" Excel Export", use_container_width=True):
            try:
                excel_data = report_gen.export_report_excel(report_data)
                st.download_button(
                    label="Excel herunterladen",
                    data=excel_data,
                    file_name=f"bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Fehler beim Export: {e}")

    with col4:
        if st.button(" PDF Export", use_container_width=True):
            try:
                pdf_data = report_gen.export_report_pdf(report_data)
                st.download_button(
                    label="PDF herunterladen",
                    data=pdf_data,
                    file_name=f"bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Fehler beim Export: {e}")

    # Display charts
    if not is_comparison:
        # Single employee report
        st.markdown("### Leistungsübersicht")

        # Generate dashboard charts
        figures = chart_gen.create_dashboard(report_data)

        # Display charts in grid
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)

        # Display quotas table
        quotas = report_data.get("quotas", {})
        ratios = report_data.get("ratio_descriptions", {})

        if quotas:
            st.markdown("### Quoten im Detail")

            # Create table data with bold, italic, black formatting
            table_data = []
            for quota_name, quota_value in quotas.items():
                table_data.append({
                    "***Quote***": f"***{quota_name}***",
                    "***Prozentsatz***": f"***{quota_value:.2f}%***",
                    "***Verhältnis***": f"***{ratios.get(quota_name, '')}***"
                })

            st.table(table_data)

    else:
        # Comparison report
        st.markdown("### Mitarbeitervergleich")

        employee_reports = report_data.get("employee_reports", [])

        # Create comparison table
        if employee_reports:
            comparison_data = []
            for emp_report in employee_reports:
                row = {
                    "Mitarbeiter": emp_report.get("employee_name"),
                    "Position": emp_report.get("position")
                }
                # Add quotas
                quotas = emp_report.get("quotas", {})
                for quota_name, quota_value in quotas.items():
                    row[quota_name] = f"{quota_value:.2f}%"

                comparison_data.append(row)

            st.table(comparison_data)


def render_archive_tab():
    """
    Archive browser for saved reports and evaluation periods.

    Requirements: 13.1
    """
    st.subheader("📁 Archiv")

    db = SessionLocal()
    report_gen = ReportGenerator(db)
    chart_gen = ChartGenerator()
    period_manager = PeriodManager(db)

    try:
        # Tabs für verschiedene Archiv-Bereiche
        archive_tabs = st.tabs(["📊 Berichte", "🗓️ Auswertungsperioden"])
        
        # ========== BERICHTE ARCHIV ==========
        with archive_tabs[0]:
            st.markdown("### 📊 Gespeicherte Berichte")
            
            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                report_type_filter = st.selectbox(
                    "Nach Berichtstyp filtern",
                    options=[None] + list(ReportType),
                    format_func=lambda x: "Alle" if x is None else {
                        ReportType.DAILY: "Täglich",
                        ReportType.WEEKLY: "Wöchentlich",
                        ReportType.MONTHLY: "Monatlich",
                        ReportType.QUARTERLY: "Quartalsweise",
                        ReportType.YEARLY: "Jährlich",
                        ReportType.SINCE_START: "Seit Arbeitsbeginn"
                    }.get(x, x.value),
                    key="archive_report_type_filter"
                )

            with col2:
                limit = st.number_input(
                    "Anzahl Berichte",
                    min_value=1,
                    max_value=100,
                    value=20,
                    key="archive_limit"
                )

            # Load reports
            reports = report_gen.list_reports(
                report_type=report_type_filter,
                limit=limit
            )

            if not reports:
                st.info("Keine gespeicherten Berichte vorhanden.")
            else:
                st.caption(f"{len(reports)} Berichte gefunden")

                # Display reports
                for report_meta in reports:
                    with st.expander(
                        f"{'🔍 Vergleich' if report_meta['is_comparison'] else '📊'} "
                        f"{report_meta.get('employee_name', 'Mehrere Mitarbeiter')} - "
                        f"{report_meta['report_type']} "
                        f"({report_meta['start_date']} bis {report_meta['end_date']})",
                        expanded=False
                    ):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"**Erstellt:** {report_meta['created_at']}")
                            st.write(f"**Typ:** {report_meta['report_type']}")
                            st.write(
                                f"**Zeitraum:** {report_meta['start_date']} bis "
                                f"{report_meta['end_date']}"
                            )

                        with col2:
                            if st.button(
                                "📂 Laden",
                                key=f"load_report_{report_meta['report_id']}",
                                type="primary"
                            ):
                                try:
                                    # Load report
                                    report_data = report_gen.load_report(
                                        report_meta['report_id']
                                    )
                                    st.session_state.controlling_current_report = report_data
                                    st.success("✅ Bericht geladen!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler beim Laden: {e}")

                # Display loaded report
                if st.session_state.controlling_current_report:
                    st.markdown("---")
                    render_report_dashboard(
                        st.session_state.controlling_current_report,
                        chart_gen,
                        report_gen
                    )
        
        # ========== AUSWERTUNGSPERIODEN ARCHIV ==========
        with archive_tabs[1]:
            st.markdown("### 🗓️ Gespeicherte Auswertungsperioden")
            
            # Filter
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                status_filter = st.selectbox(
                    "Status",
                    options=[None, PeriodStatus.ACTIVE, PeriodStatus.COMPLETED, PeriodStatus.ARCHIVED],
                    format_func=lambda x: {
                        None: "Alle",
                        PeriodStatus.ACTIVE: "🟢 Aktiv",
                        PeriodStatus.COMPLETED: "🔵 Abgeschlossen",
                        PeriodStatus.ARCHIVED: "⚫ Archiviert"
                    }.get(x, str(x)),
                    key="period_status_filter"
                )
            
            with col_p2:
                type_filter = st.selectbox(
                    "Typ",
                    options=[None] + list(PeriodType),
                    format_func=lambda x: {
                        None: "Alle",
                        PeriodType.DAILY: "📅 Täglich",
                        PeriodType.WEEKLY: "📆 Wöchentlich",
                        PeriodType.MONTHLY: "📊 Monatlich",
                        PeriodType.QUARTERLY: "📈 Quartalsweise",
                        PeriodType.YEARLY: "📉 Jährlich",
                        PeriodType.CUSTOM: "🎯 Benutzerdefiniert"
                    }.get(x, str(x)),
                    key="period_type_filter"
                )
            
            # Load periods
            periods = period_manager.list_periods(
                status=status_filter,
                period_type=type_filter
            )
            
            if not periods:
                st.info("Keine Auswertungsperioden gefunden.")
            else:
                st.caption(f"{len(periods)} Perioden gefunden")
                
                for period in periods:
                    # Status-Icon
                    status_icon = {
                        PeriodStatus.ACTIVE: "🟢",
                        PeriodStatus.COMPLETED: "🔵",
                        PeriodStatus.ARCHIVED: "⚫"
                    }.get(period.status, "⚪")
                    
                    # Typ-Icon
                    type_icon = {
                        PeriodType.DAILY: "📅",
                        PeriodType.WEEKLY: "📆",
                        PeriodType.MONTHLY: "📊",
                        PeriodType.QUARTERLY: "📈",
                        PeriodType.YEARLY: "📉",
                        PeriodType.CUSTOM: "🎯"
                    }.get(period.period_type, "📋")
                    
                    with st.expander(
                        f"{status_icon} {type_icon} {period.name} "
                        f"({period.start_date} - {period.end_date})",
                        expanded=False
                    ):
                        col_det1, col_det2 = st.columns([2, 1])
                        
                        with col_det1:
                            st.write(f"**Typ:** {period.period_type.value}")
                            st.write(f"**Status:** {period.status.value}")
                            st.write(f"**Zeitraum:** {period.start_date} bis {period.end_date}")
                            st.write(f"**Dauer:** {period.duration_days} Tage")
                            
                            if period.description:
                                st.write(f"**Beschreibung:** {period.description}")
                            
                            if period.employee:
                                st.write(f"**Mitarbeiter:** {period.employee.full_name}")
                            else:
                                st.write("**Mitarbeiter:** Alle (global)")
                            
                            # Anzahl Leistungsdaten
                            data_count = len(period.performance_data)
                            st.write(f"**Leistungsdaten:** {data_count} Einträge")
                        
                        with col_det2:
                            # Actions
                            if period.status == PeriodStatus.ACTIVE:
                                if st.button(
                                    "✅ Abschließen",
                                    key=f"complete_period_{period.id}"
                                ):
                                    if period_manager.complete_period(period.id):
                                        st.success("Periode abgeschlossen!")
                                        st.rerun()
                                
                                if st.button(
                                    "📂 Aktivieren",
                                    key=f"activate_period_{period.id}"
                                ):
                                    st.session_state.active_period_id = period.id
                                    st.success(f"Periode '{period.name}' aktiviert!")
                                    st.rerun()
                            
                            elif period.status == PeriodStatus.COMPLETED:
                                if st.button(
                                    "📦 Archivieren",
                                    key=f"archive_period_{period.id}"
                                ):
                                    if period_manager.archive_period(period.id):
                                        st.success("Periode archiviert!")
                                        st.rerun()
                            
                            if st.button(
                                "🗑️ Löschen",
                                key=f"delete_period_archive_{period.id}"
                            ):
                                if data_count > 0:
                                    st.warning(
                                        f"⚠️ Diese Periode enthält {data_count} Leistungsdaten! "
                                        "Diese werden ebenfalls gelöscht."
                                    )
                                
                                if period_manager.delete_period(period.id):
                                    st.success("Periode gelöscht!")
                                    st.rerun()

    except Exception as e:
        st.error(f"Fehler beim Laden des Archivs: {e}")
        logger.error(f"Error in archive tab: {e}")
    
    finally:
        db.close()


def render_team_analysis_tab():
    """
    Team-based performance analysis and reporting.
    
    Requirements: Team organization and collective reporting
    """
    st.subheader("🏢 Team-Auswertung")

    db = SessionLocal()
    
    try:
        from controlling.team_manager import TeamManager
        from controlling.managers import EmployeeManager
        
        team_manager = TeamManager(db)
        emp_manager = EmployeeManager(db)
        report_gen = ReportGenerator(db)
        chart_gen = ChartGenerator()
    except ImportError as e:
        st.error(f"Team-Funktionen konnten nicht geladen werden: {e}")
        db.close()
        return
    
    # Team selection
    st.markdown("### 👥 Team auswählen")
    
    try:
        teams = team_manager.list_teams(active_only=True, include_employee_count=True)
        
        if not teams:
            st.info(
                "Keine Teams vorhanden. Bitte erstellen Sie zuerst Teams in den "
                "Controlling-Einstellungen."
            )
            db.close()
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            team_options = {
                team.id: f"{team.name} ({team.employee_count if hasattr(team, 'employee_count') else 0} Mitarbeiter)"
                for team in teams
            }
            
            selected_team_id = st.selectbox(
                "Team",
                options=list(team_options.keys()),
                format_func=lambda x: team_options[x],
                key="team_selector"
            )
        
        with col2:
            # Team statistics button
            if st.button("📊 Team-Statistiken anzeigen", use_container_width=True):
                st.session_state['show_team_stats'] = True
        
        # Show team statistics
        if st.session_state.get('show_team_stats', False):
            st.markdown("---")
            st.markdown("### 📊 Team-Statistiken")
            
            stats = team_manager.get_team_statistics(selected_team_id)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Aktive Mitglieder", stats['active_members'])
            
            with col2:
                st.metric("Positionen", len(stats['positions']))
            
            with col3:
                if stats['has_team_leader']:
                    st.metric("Teamleiter", stats['team_leader'])
                else:
                    st.info("Kein Teamleiter")
            
            # Position distribution
            if stats['positions']:
                st.markdown("**Positionen im Team:**")
                for position_name, count in stats['positions'].items():
                    st.markdown(f"  - {position_name}: {count}")
        
        # Get team members
        team_members = team_manager.get_team_members(selected_team_id, active_only=True)
        
        if not team_members:
            st.warning("Dieses Team hat keine aktiven Mitglieder.")
            db.close()
            return
        
        st.markdown("---")
        st.markdown("### 📅 Auswertungszeitraum")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type_options = {
                "Täglich": ReportType.DAILY,
                "Wöchentlich": ReportType.WEEKLY,
                "Monatlich": ReportType.MONTHLY,
                "Quartalsweise": ReportType.QUARTERLY,
                "Jährlich": ReportType.YEARLY,
                "Seit Arbeitsbeginn": ReportType.SINCE_START
            }
            
            report_type = st.selectbox(
                "Zeitraum",
                options=list(report_type_options.values()),
                format_func=lambda x: {v: k for k, v in report_type_options.items()}[x],
                key="team_report_type"
            )
        
        with col2:
            reference_date = st.date_input(
                "Referenzdatum",
                value=date.today(),
                max_value=date.today(),
                key="team_reference_date"
            )
        
        # Generate team report
        if st.button("📊 Team-Bericht erstellen", type="primary", use_container_width=True):
            with st.spinner("Team-Bericht wird erstellt..."):
                try:
                    # Generate reports for all team members
                    employee_ids = [member.id for member in team_members]
                    
                    team_report = report_gen.generate_comparison_report(
                        employee_ids=employee_ids,
                        report_type=report_type,
                        end_date=reference_date
                    )
                    
                    # Add team information
                    team = team_manager.get_team(selected_team_id)
                    team_report['team_name'] = team.name
                    team_report['team_id'] = team.id
                    
                    st.session_state['current_team_report'] = team_report
                    st.success(f"✅ Team-Bericht für '{team.name}' erstellt!")
                
                except Exception as e:
                    st.error(f"Fehler beim Erstellen des Team-Berichts: {e}")
                    logger.error(f"Team report generation error: {e}")
        
        # Display team report
        if 'current_team_report' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Team-Auswertung")
            
            team_report = st.session_state['current_team_report']
            
            # Team header
            st.markdown(f"**Team:** {team_report.get('team_name', 'Unbekannt')}")
            st.markdown(f"**Zeitraum:** {team_report.get('start_date', '')} - {team_report.get('end_date', '')}")
            st.markdown(f"**Mitarbeiter:** {len(team_report.get('employee_reports', []))}")
            
            # Employee reports table
            st.markdown("#### Mitarbeiter-Übersicht")
            
            employee_reports = team_report.get("employee_reports", [])
            
            if employee_reports:
                # Create comparison table
                comparison_data = []
                
                for emp_report in employee_reports:
                    row = {
                        "**Mitarbeiter**": emp_report.get("employee_name"),
                        "**Position**": emp_report.get("position")
                    }
                    
                    # Add key quotas
                    quotas = emp_report.get("quotas", {})
                    for quota_name, quota_value in quotas.items():
                        row[f"**{quota_name}**"] = f"{quota_value:.2f}%"
                    
                    comparison_data.append(row)
                
                st.table(comparison_data)
                
                # Charts
                st.markdown("#### 📈 Visualisierungen")
                
                try:
                    figures = chart_gen.create_comparison_charts(team_report)
                    
                    if figures:
                        for fig in figures:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Keine Visualisierungen verfügbar.")
                
                except Exception as e:
                    st.warning(f"Diagramme konnten nicht erstellt werden: {e}")
                
                # Export options
                st.markdown("---")
                st.markdown("#### 💾 Export")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Als PDF exportieren", use_container_width=True):
                        try:
                            pdf_bytes = report_gen.export_comparison_report_to_pdf(team_report)
                            
                            st.download_button(
                                label="💾 PDF herunterladen",
                                data=pdf_bytes,
                                file_name=f"team_report_{team_report.get('team_name', 'team')}_{date.today()}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        except Exception as e:
                            st.error(f"PDF-Export fehlgeschlagen: {e}")
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Team-Auswertung: {e}")
        logger.error(f"Team analysis error: {e}")
    
    finally:
        db.close()
    """Rendere Team-Auswertungs-Tab."""
    st.subheader("📊 Team-Auswertung")
    st.caption("Alle Mitarbeiter einer Position gemeinsam auswerten")
    
    db = SessionLocal()
    try:
        from controlling.models import Position
        
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
        st.markdown("**Zeitraum**")
        col3, col4 = st.columns(2)
        
        from datetime import timedelta
        
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
        if st.button("🎯 Team-Auswertung erstellen", type="primary", key="create_team_report"):
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
                    st.success(f"✅ Team-Auswertung erstellt für {team_data['employee_count']} Mitarbeiter!")
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Erstellen der Team-Auswertung: {e}")
                    logger.error(f"Error creating team report: {e}")
                    return
        
        # Zeige Auswertung
        if 'team_report_data' in st.session_state:
            team_data = st.session_state['team_report_data']
            
            st.markdown("---")
            st.markdown("### 📈 Ergebnisse")
            
            # Team-Quotas
            st.write("**Team-Leistungsquoten (Gesamt)**")
            team_quotas = team_data.get('team_quotas', {})
            
            if team_quotas:
                cols = st.columns(min(4, len(team_quotas)))
                for i, (quota_name, quota_value) in enumerate(team_quotas.items()):
                    with cols[i % 4]:
                        st.markdown(f"**{quota_name}**")
                        st.markdown(f"<h2 style='margin:0; font-weight:bold;'>{quota_value:.2f}%</h2>", unsafe_allow_html=True)
            
            # Statistiken
            st.markdown("---")
            st.write("**📊 Statistiken & Leistungsvergleich**")
            
            statistics = team_data.get('statistics', {})
            quota_stats = statistics.get('quota_statistics', {})
            
            if quota_stats:
                for quota_name, stats in quota_stats.items():
                    with st.expander(f"📈 {quota_name}"):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.markdown("Durchschnitt")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0;'>{stats['average']:.2f}%</p>", unsafe_allow_html=True)
                            st.markdown("Minimum")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0;'>{stats['min']:.2f}%</p>", unsafe_allow_html=True)
                        
                        with col_b:
                            st.markdown("Maximum")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0;'>{stats['max']:.2f}%</p>", unsafe_allow_html=True)
                            st.info(f"**Bester:** {stats['best_performer']}")
                        
                        with col_c:
                            st.warning(f"**Schlechtester:** {stats['worst_performer']}")
            
            # PDF Export
            st.markdown("---")
            col_export1, col_export2 = st.columns([3, 1])
            
            with col_export1:
                st.write("**📄 Export**")
            
            with col_export2:
                if st.button("📥 Als PDF exportieren", key="export_team_pdf"):
                    try:
                        report_gen = ReportGenerator(db)
                        pdf_bytes = report_gen.export_team_report_to_pdf(team_data)
                        
                        st.download_button(
                            label="💾 PDF herunterladen",
                            data=pdf_bytes,
                            file_name=f"team_auswertung_{selected_position_name}_{date.today()}.pdf",
                            mime="application/pdf",
                            key="download_team_pdf"
                        )
                        st.success("✅ PDF erfolgreich erstellt!")
                    
                    except Exception as e:
                        st.error(f"❌ Fehler beim PDF-Export: {e}")
                        logger.error(f"Error exporting team PDF: {e}")
    
    finally:
        db.close()


def render_comparison_tab():
    """Rendere Mitarbeiter-Vergleichs-Tab."""
    st.subheader("🔍 Mitarbeiter-Vergleich")
    st.caption("Mitarbeiter derselben Position direkt vergleichen")
    
    db = SessionLocal()
    try:
        from controlling.models import Position, Employee
        
        # Hole alle Positionen
        positions = db.query(Position).all()
        
        if not positions:
            st.warning("Keine Positionen gefunden.")
            return
        
        # Position-Filter
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
        st.markdown("**Mitarbeiter wählen (mindestens 2)**")
        
        employee_options = {f"{emp.display_name} ({emp.position.name})": emp.id for emp in employees}
        
        selected_employees = st.multiselect(
            "Mitarbeiter",
            options=list(employee_options.keys()),
            key="comp_employee_select"
        )
        
        if len(selected_employees) < 2:
            st.info("👆 Bitte mindestens 2 Mitarbeiter auswählen")
        
        # Zeitraum
        st.markdown("**Zeitraum**")
        col3, col4 = st.columns(2)
        
        from datetime import timedelta
        
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
            "🎯 Vergleich erstellen",
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
                    st.success(f"✅ Vergleich erstellt für {len(selected_employees)} Mitarbeiter!")
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Erstellen des Vergleichs: {e}")
                    logger.error(f"Error creating comparison: {e}")
                    return
        
        # Zeige Vergleich
        if 'comparison_data' in st.session_state:
            comp_data = st.session_state['comparison_data']
            
            st.markdown("---")
            st.markdown("### 📈 Vergleichsergebnisse")
            
            # Rankings
            comparison_stats = comp_data.get('comparison_statistics', {})
            rankings = comparison_stats.get('rankings', {})
            
            if rankings:
                st.write("**🏆 Leistungsranking**")
                
                for quota_name, ranking_list in rankings.items():
                    with st.expander(f"📊 {quota_name}"):
                        # Erstelle Ranking-Tabelle
                        for item in ranking_list:
                            rank_emoji = ""
                            if item['rank'] == 1:
                                rank_emoji = "🥇"
                            elif item['rank'] == 2:
                                rank_emoji = "🥈"
                            elif item['rank'] == 3:
                                rank_emoji = "🥉"
                            
                            st.write(f"{rank_emoji} **{item['rank']}.** {item['name']}: **{item['value']:.2f}%**")
            
            # Unterschiede
            differences = comparison_stats.get('differences', {})
            
            if differences:
                st.markdown("---")
                st.write("**📊 Leistungsunterschiede**")
                
                for quota_name, diff_info in differences.items():
                    with st.expander(f"📈 {quota_name}"):
                        col_diff1, col_diff2, col_diff3 = st.columns(3)
                        
                        with col_diff1:
                            st.success(f"**Bester:** {diff_info['leader']}")
                            st.markdown("Wert")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0; color:#0e8a16;'>{diff_info['leader_value']:.2f}%</p>", unsafe_allow_html=True)
                        
                        with col_diff2:
                            st.error(f"**Schlechtester:** {diff_info['last']}")
                            st.markdown("Wert")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0; color:#cb2431;'>{diff_info['last_value']:.2f}%</p>", unsafe_allow_html=True)
                        
                        with col_diff3:
                            st.info("**Differenz**")
                            st.markdown("Absolut")
                            st.markdown(f"<p style='font-size:24px; font-weight:bold; margin:0; color:#0366d6;'>{diff_info['difference']:.2f}%</p>", unsafe_allow_html=True)
            
            # PDF Export
            st.markdown("---")
            col_export1, col_export2 = st.columns([3, 1])
            
            with col_export1:
                st.write("**📄 Export**")
            
            with col_export2:
                if st.button("📥 Als PDF exportieren", key="export_comp_pdf"):
                    try:
                        report_gen = ReportGenerator(db)
                        pdf_bytes = report_gen.export_comparison_report_to_pdf(comp_data)
                        
                        st.download_button(
                            label="💾 PDF herunterladen",
                            data=pdf_bytes,
                            file_name=f"mitarbeiter_vergleich_{date.today()}.pdf",
                            mime="application/pdf",
                            key="download_comp_pdf"
                        )
                        st.success("✅ PDF erfolgreich erstellt!")
                    
                    except Exception as e:
                        st.error(f"❌ Fehler beim PDF-Export: {e}")
                        logger.error(f"Error exporting comparison PDF: {e}")
    
    finally:
        db.close()


def render_ranking_tab():
    """
    Rendere Mitarbeiter-Ranglisten-Tab.
    
    Zeigt dynamische Rankings für alle Zeiträume/Perioden.
    """
    st.subheader("🏆 Mitarbeiter-Rangliste")
    st.caption("Dynamische Platzierungen nach Leistungskriterien")
    
    db = SessionLocal()
    
    try:
        from controlling.ranking_system import RankingSystem
        
        ranking_sys = RankingSystem(db)
        pos_manager = PositionManager(db)
        period_manager = PeriodManager(db)
        
        # Position auswählen
        positions = pos_manager.list_positions()
        
        if not positions:
            st.warning("⚠️ Keine Positionen vorhanden. Bitte legen Sie zuerst Positionen an.")
            return
        
        position_options = {pos.name: pos.id for pos in positions}
        selected_position_name = st.selectbox(
            "Position auswählen",
            options=list(position_options.keys()),
            key="ranking_position_select"
        )
        
        selected_position_id = position_options[selected_position_name]
        
        # Ansichtstyp wählen
        st.markdown("---")
        view_type = st.radio(
            "Ansicht",
            options=["📅 Nach Periode", "📆 Benutzerdefinierter Zeitraum", "📜 Alle Perioden"],
            horizontal=True,
            key="ranking_view_type"
        )
        
        ranking_data = None
        all_period_rankings = None
        
        if view_type == "📅 Nach Periode":
            # Perioden für diese Position holen - Alle aktiven und abgeschlossenen
            all_periods = period_manager.list_periods(include_global=True)
            periods = [
                p for p in all_periods 
                if p.status in [PeriodStatus.ACTIVE, PeriodStatus.COMPLETED]
            ]
            
            if not periods:
                st.info("ℹ️ Keine Auswertungsperioden vorhanden. Erstellen Sie zuerst eine Periode im Tab 'Leistungsdaten erfassen'.")
                return
            
            period_options = {
                f"{p.name} ({p.start_date} - {p.end_date})": p.id 
                for p in periods
            }
            
            selected_period_str = st.selectbox(
                "Periode wählen",
                options=list(period_options.keys()),
                key="ranking_period_select"
            )
            
            selected_period_id = period_options[selected_period_str]
            selected_period = next(p for p in periods if p.id == selected_period_id)
            
            if st.button("🔄 Ranking berechnen", key="calc_period_ranking"):
                with st.spinner("Berechne Rankings..."):
                    ranking_data = ranking_sys.calculate_employee_rankings(
                        position_id=selected_position_id,
                        start_date=selected_period.start_date,
                        end_date=selected_period.end_date,
                        period_id=selected_period_id
                    )
                    ranking_data["period_name"] = selected_period.name
                    st.session_state["current_ranking"] = ranking_data
        
        elif view_type == "📆 Benutzerdefinierter Zeitraum":
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                start_date = st.date_input(
                    "Von",
                    value=date.today().replace(day=1),
                    key="ranking_custom_start"
                )
            
            with col_date2:
                end_date = st.date_input(
                    "Bis",
                    value=date.today(),
                    key="ranking_custom_end"
                )
            
            if st.button("🔄 Ranking berechnen", key="calc_custom_ranking"):
                if start_date > end_date:
                    st.error("❌ Startdatum muss vor Enddatum liegen!")
                else:
                    with st.spinner("Berechne Rankings..."):
                        ranking_data = ranking_sys.calculate_employee_rankings(
                            position_id=selected_position_id,
                            start_date=start_date,
                            end_date=end_date
                        )
                        st.session_state["current_ranking"] = ranking_data
        
        else:  # Alle Perioden
            if st.button("🔄 Alle Rankings laden", key="load_all_rankings"):
                with st.spinner("Lade Rankings für alle Perioden..."):
                    all_period_rankings = ranking_sys.get_rankings_for_all_periods(
                        position_id=selected_position_id
                    )
                    st.session_state["all_period_rankings"] = all_period_rankings
        
        # Zeige gespeicherte Rankings
        if "current_ranking" in st.session_state and view_type != "📜 Alle Perioden":
            ranking_data = st.session_state["current_ranking"]
        
        if "all_period_rankings" in st.session_state and view_type == "📜 Alle Perioden":
            all_period_rankings = st.session_state["all_period_rankings"]
        
        # ========== ANZEIGE: EINZELNES RANKING ==========
        if ranking_data and view_type != "📜 Alle Perioden":
            st.markdown("---")
            st.markdown("### 📊 Ranking-Ergebnisse")
            
            # Gesamt-Ranking
            overall_ranking = ranking_data.get("overall_ranking", [])
            
            if overall_ranking:
                st.markdown("#### 🥇 Gesamt-Rangliste")
                st.caption("Sortiert nach Durchschnitt aller Leistungskriterien")
                
                # Tabelle erstellen
                ranking_table_data = []
                for entry in overall_ranking:
                    medal = ""
                    if entry["rank"] == 1:
                        medal = "🥇"
                    elif entry["rank"] == 2:
                        medal = "🥈"
                    elif entry["rank"] == 3:
                        medal = "🥉"
                    
                    ranking_table_data.append({
                        "Rang": f"{medal} {entry['rank']}" if medal else str(entry['rank']),
                        "Mitarbeiter": entry["name"],
                        "Agentenname": entry.get("agent_name", "-"),
                        "Durchschnitt": f"{entry['average_score']:.2f}%",
                        "Anzahl Quotas": entry["quota_count"]
                    })
                
                st.table(ranking_table_data)
            
            # Quota-spezifische Rankings
            quota_rankings = ranking_data.get("quota_rankings", {})
            
            if quota_rankings:
                st.markdown("---")
                st.markdown("#### 📈 Rankings nach Leistungskriterien")
                
                for quota_name, ranking_list in quota_rankings.items():
                    with st.expander(f"🎯 {quota_name}", expanded=False):
                        quota_table_data = []
                        for entry in ranking_list:
                            medal = "🥇" if entry["rank"] == 1 else ""
                            quota_table_data.append({
                                "Rang": f"{medal} {entry['rank']}" if medal else str(entry['rank']),
                                "Mitarbeiter": entry["name"],
                                "Agentenname": entry.get("agent_name", "-"),
                                "Wert": f"{entry['value']:.2f}%"
                            })
                        st.table(quota_table_data)
            
            # PDF Export
            st.markdown("---")
            if st.button("📥 Ranking als PDF exportieren", key="export_ranking_pdf"):
                try:
                    from controlling.report_generator import ReportGenerator
                    
                    report_gen = ReportGenerator(db)
                    pdf_bytes = report_gen.export_ranking_report_to_pdf(ranking_data)
                    
                    period_suffix = ranking_data.get("period_name", "zeitraum").replace(" ", "_")
                    
                    st.download_button(
                        label="💾 PDF herunterladen",
                        data=pdf_bytes,
                        file_name=f"rangliste_{period_suffix}_{date.today()}.pdf",
                        mime="application/pdf",
                        key="download_ranking_pdf"
                    )
                    st.success("✅ PDF erfolgreich erstellt!")
                
                except Exception as e:
                    st.error(f"❌ Fehler beim PDF-Export: {e}")
                    logger.error(f"Error exporting ranking PDF: {e}")
        
        # ========== ANZEIGE: ALLE PERIODEN ==========
        elif all_period_rankings and view_type == "📜 Alle Perioden":
            st.markdown("---")
            st.markdown(f"### 📅 Rankings für alle Perioden ({len(all_period_rankings)} Perioden)")
            
            for period_ranking in all_period_rankings:
                with st.expander(
                    f"🗓️ {period_ranking.get('period_name')} "
                    f"({period_ranking.get('start_date')} - {period_ranking.get('end_date')})",
                    expanded=False
                ):
                    overall = period_ranking.get("overall_ranking", [])
                    
                    if overall:
                        st.markdown("**Top 3:**")
                        top3_data = []
                        for entry in overall[:3]:
                            medal = ["🥇", "🥈", "🥉"][entry["rank"] - 1]
                            top3_data.append({
                                "": medal,
                                "Mitarbeiter": entry["name"],
                                "Durchschnitt": f"{entry['average_score']:.2f}%"
                            })
                        st.table(top3_data)
                        
                        # PDF Export für diese Periode
                        if st.button(
                            f"📥 PDF für {period_ranking.get('period_name')}",
                            key=f"export_period_{period_ranking.get('period_id')}_pdf"
                        ):
                            try:
                                from controlling.report_generator import ReportGenerator
                                
                                report_gen = ReportGenerator(db)
                                pdf_bytes = report_gen.export_ranking_report_to_pdf(period_ranking)
                                
                                period_name = period_ranking.get("period_name", "periode").replace(" ", "_")
                                
                                st.download_button(
                                    label=f"💾 PDF {period_name} herunterladen",
                                    data=pdf_bytes,
                                    file_name=f"rangliste_{period_name}_{date.today()}.pdf",
                                    mime="application/pdf",
                                    key=f"download_period_{period_ranking.get('period_id')}_pdf"
                                )
                                st.success("✅ PDF erstellt!")
                            
                            except Exception as e:
                                st.error(f"❌ Fehler: {e}")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Ranking-Systems: {e}")
        logger.error(f"Error in ranking tab: {e}", exc_info=True)
    
    finally:
        db.close()


def render_pdf_color_settings():
    """Rendere PDF-Farbeinstellungs-Tab."""
    st.subheader("🎨 PDF-Farbeinstellungen")
    st.caption("Individuelle Anpassung aller PDF-Farben")
    
    config_manager = get_pdf_config_manager()
    current_scheme = config_manager.color_scheme
    
    # Tabs für verschiedene Einstellungsoptionen
    tab1, tab2, tab3 = st.tabs(["Vordefinierte Schemata", "Individuelle Farben", "Vorschau"])
    
    with tab1:
        st.markdown("**Vordefinierte Farbschemata**")
        
        predefined_schemes = config_manager.get_predefined_schemes()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_scheme_name = st.selectbox(
                "Schema wählen",
                options=list(predefined_schemes.keys()),
                key="predefined_scheme_select"
            )
        
        with col2:
            if st.button("✅ Schema anwenden", key="apply_predefined_scheme"):
                if config_manager.apply_predefined_scheme(selected_scheme_name):
                    st.success(f"✅ Schema '{selected_scheme_name}' erfolgreich angewendet!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Anwenden des Schemas")
        
        # Zeige Vorschau des gewählten Schemas
        preview_scheme = predefined_schemes[selected_scheme_name]
        
        st.write("**Vorschau:**")
        preview_cols = st.columns(4)
        
        with preview_cols[0]:
            st.markdown("**Primärfarbe**")
            st.color_picker("", value=preview_scheme.primary_color, disabled=True, key="preview_primary")
        
        with preview_cols[1]:
            st.markdown("**Sekundärfarbe**")
            st.color_picker("", value=preview_scheme.secondary_color, disabled=True, key="preview_secondary")
        
        with preview_cols[2]:
            st.markdown("**Tabellen-Header**")
            st.color_picker("", value=preview_scheme.table_header_bg, disabled=True, key="preview_header")
        
        with preview_cols[3]:
            st.markdown("**Tabellenzeilen**")
            st.color_picker("", value=preview_scheme.table_row_bg, disabled=True, key="preview_row")
    
    with tab2:
        st.markdown("**Individuelle Farbanpassung**")
        
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
        
        # Hintergrundfarben
        st.write("**Hintergrundfarben**")
        col_bg1, col_bg2 = st.columns(2)
        
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
        
        # Speichern
        st.markdown("---")
        col_save1, col_save2, col_save3 = st.columns([2, 1, 1])
        
        with col_save2:
            if st.button("💾 Farben speichern", type="primary", key="save_custom_colors"):
                new_scheme = PDFColorScheme(
                    primary_color=new_primary,
                    secondary_color=new_secondary,
                    title_color=new_primary,
                    text_color=current_scheme.text_color,
                    header_text_color=current_scheme.header_text_color,
                    table_header_bg=new_table_header_bg,
                    table_row_bg=new_table_row_bg,
                    table_alt_row_bg=current_scheme.table_alt_row_bg,
                    success_color=current_scheme.success_color,
                    warning_color=current_scheme.warning_color,
                    error_color=current_scheme.error_color,
                    info_color=current_scheme.info_color,
                    border_color=current_scheme.border_color,
                    grid_color=current_scheme.grid_color
                )
                
                if config_manager.save_color_scheme(new_scheme):
                    st.success("✅ Farben erfolgreich gespeichert!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Speichern")
        
        with col_save3:
            if st.button("🔄 Auf Standard zurücksetzen", key="reset_colors"):
                if config_manager.reset_to_default():
                    st.success("✅ Auf Standard zurückgesetzt!")
                    st.rerun()
    
    with tab3:
        st.markdown("**Aktuelles Farbschema:**")
        
        # Farben-Grid
        preview_data = [
            ("Primärfarbe", current_scheme.primary_color),
            ("Sekundärfarbe", current_scheme.secondary_color),
            ("Tabellen-Header", current_scheme.table_header_bg),
            ("Tabellenzeilen", current_scheme.table_row_bg),
        ]
        
        cols = st.columns(4)
        for i, (name, color) in enumerate(preview_data):
            with cols[i]:
                st.markdown(f"**{name}**")
                st.markdown(
                    f'<div style="background-color: {color}; '
                    f'width: 100%; height: 60px; border: 1px solid #ccc; '
                    f'border-radius: 5px;"></div>',
                    unsafe_allow_html=True
                )
                st.caption(color)


if __name__ == "__main__":
    # For testing
    render_controlling_page()
