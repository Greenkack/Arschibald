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
from controlling.report_generator import ReportGenerator  # noqa: E402
from controlling.chart_generator import ChartGenerator  # noqa: E402
from controlling.notifications import NotificationManager  # noqa: E402

logger = logging.getLogger(__name__)


def render_controlling_page():
    """
    Main controlling page in Hauptmenü/Sidemenu.

    Requirements: 1.1, 1.2
    """
    st.header("📊 Controlling")
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

    # Create tabs
    tabs = st.tabs([
        "📝 Leistungsdaten erfassen",
        "📈 Berichte erstellen",
        "📁 Archiv"
    ])

    with tabs[0]:
        render_performance_entry_tab()

    with tabs[1]:
        render_report_generation_tab()

    with tabs[2]:
        render_archive_tab()


def render_performance_entry_tab():
    """
    Performance data entry form.

    Requirements: 8.1, 8.2
    """
    st.subheader("Leistungsdaten erfassen")

    db = SessionLocal()
    emp_manager = EmployeeManager(db)
    perf_manager = PerformanceDataManager(db)

    # Employee selector
    try:
        employees = emp_manager.list_employees()

        if not employees:
            st.warning(
                "Keine Mitarbeiter vorhanden. "
                "Bitte erstellen Sie zuerst Mitarbeiter im Admin-Bereich."
            )
            return

        # Employee selection
        employee_options = {emp.id: emp.full_name for emp in employees}
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

        # Performance data entry form
        st.markdown("### Leistungsdaten eingeben")

        with st.form("performance_entry_form", clear_on_submit=False):
            performance_data = {}

            # Create input fields for each criterion
            cols = st.columns(2)
            for idx, criterion in enumerate(criteria):
                col = cols[idx % 2]
                with col:
                    value = st.number_input(
                        criterion.name,
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key=f"perf_input_{criterion.id}",
                        help=criterion.description or ""
                    )
                    performance_data[criterion.id] = value

            submitted = st.form_submit_button(
                "Leistungsdaten speichern",
                type="primary"
            )

            if submitted:
                try:
                    # Save performance data
                    saved_count = 0
                    for criterion_id, value in performance_data.items():
                        if value > 0:  # Only save non-zero values
                            perf_manager.record_performance(
                                employee_id=selected_emp_id,
                                criterion_id=criterion_id,
                                value=value,
                                date=entry_date
                            )
                            saved_count += 1

                    if saved_count > 0:
                        st.success(
                            f"✅ {saved_count} Leistungsdaten erfolgreich "
                            f"gespeichert!"
                        )
                    else:
                        st.info("Keine Daten zum Speichern (alle Werte = 0)")

                except ValidationError as e:
                    st.error(f"Validierungsfehler: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
                    logger.error(f"Error saving performance data: {e}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        logger.error(f"Error in performance entry tab: {e}")


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
                if search_lower in emp.full_name.lower()
            ]

        # Employee selection
        st.markdown("---")
        employee_options = {
            emp.id: f"{emp.full_name} - {emp.position.name if emp.position else 'Keine Position'}"
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
                "📊 Bericht erstellen",
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

                    st.success("✅ Bericht erfolgreich erstellt!")

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
                            st.markdown("### 🔔 Benachrichtigungen")
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
    st.markdown("## 📈 Berichtsvisualisierung")

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
        if st.button("💾 Bericht speichern", use_container_width=True):
            try:
                report_id = report_gen.save_report(
                    report_data,
                    is_comparison=is_comparison
                )
                st.success(f"✅ Bericht gespeichert (ID: {report_id})")
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

    with col2:
        if st.button("📄 JSON Export", use_container_width=True):
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
        if st.button("📊 Excel Export", use_container_width=True):
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
        if st.button("📑 PDF Export", use_container_width=True):
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

            # Create table data
            table_data = []
            for quota_name, quota_value in quotas.items():
                table_data.append({
                    "Quote": quota_name,
                    "Wert": f"{quota_value:.2f}%",
                    "Verhältnis": ratios.get(quota_name, "")
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
    Archive browser for saved reports.

    Requirements: 13.1
    """
    st.subheader("Berichtsarchiv")

    db = SessionLocal()
    report_gen = ReportGenerator(db)
    chart_gen = ChartGenerator()

    try:
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
            return

        st.markdown(f"### {len(reports)} Berichte gefunden")

        # Display reports
        for report_meta in reports:
            with st.expander(
                f"{'🔄 Vergleich' if report_meta['is_comparison'] else '👤'} "
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

    except Exception as e:
        st.error(f"Fehler beim Laden des Archivs: {e}")
        logger.error(f"Error in archive tab: {e}")


if __name__ == "__main__":
    # For testing
    render_controlling_page()
