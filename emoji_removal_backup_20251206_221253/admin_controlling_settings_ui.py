"""
Admin Controlling Settings UI

Provides admin interface for managing employees, positions, criteria, and
position-criterion assignments for the Employee Controlling System.

Requirements: 1.3, 1.4, 7.1, 7.2, 7.3, 7.4
"""

import logging
import streamlit as st
from datetime import date
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal as BackendSessionLocal  # noqa: E402
from controlling.managers import (  # noqa: E402
    EmployeeManager,
    PositionManager,
    CriterionManager,
    ValidationError
)
from controlling.models import CalculationMethod  # noqa: E402
from controlling.notifications import (  # noqa: E402
    NotificationManager,
    NotificationType,
    ThresholdType
)

logger = logging.getLogger(__name__)


def SessionLocal():
    """Get a database session for controlling operations."""
    return BackendSessionLocal()


def render_admin_controlling_settings():
    """
    Main admin controlling settings page with tab navigation.

    Requirements: 1.3, 1.4, 7.1
    """
    st.header("Controlling Einstellungen")
    st.caption(
        "Verwaltung von Mitarbeitern, Positionen und Auswertungskriterien"
    )

    # Create tabs
    tabs = st.tabs([
        " Mitarbeiter",
        " Positionen",
        " Auswertungskriterien",
        " Zuordnungen",
        " Benachrichtigungen"
    ])

    with tabs[0]:
        render_employee_management_tab()

    with tabs[1]:
        render_position_management_tab()

    with tabs[2]:
        render_criterion_management_tab()

    with tabs[3]:
        render_assignment_tab()

    with tabs[4]:
        render_notification_threshold_tab()


def render_employee_management_tab():
    """
    Employee CRUD operations tab.

    Requirements: 7.2
    """
    st.subheader("Mitarbeiterverwaltung")

    db = SessionLocal()
    emp_manager = EmployeeManager(db)
    pos_manager = PositionManager(db)

    # List employees
    st.markdown("### Mitarbeiterliste")

    try:
        employees = emp_manager.list_employees()

        if not employees:
            st.info("Keine Mitarbeiter vorhanden.")
        else:
            # Display employees in a table
            for emp in employees:
                with st.expander(
                    f"{emp.full_name} - {emp.position.name if emp.position else 'Keine Position'}",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Name:** {emp.full_name}")
                        st.write(f"**Wohnort:** {emp.city}")
                        st.write(f"**Geburtsdatum:** {emp.birth_date}")
                        st.write(f"**Alter:** {emp.age} Jahre")
                        st.write(
                            f"**Position:** {emp.position.name if emp.position else 'N/A'}"
                        )
                        st.write(f"**Arbeitsbeginndatum:** {emp.start_date}")
                        st.write(
                            f"**Gearbeitete Tage:** {emp.days_employed}"
                        )

                    with col2:
                        if st.button(
                            " Löschen",
                            key=f"delete_emp_{emp.id}",
                            type="secondary"
                        ):
                            try:
                                emp_manager.delete_employee(emp.id)
                                st.success(
                                    f"Mitarbeiter {emp.full_name} gelöscht"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler beim Löschen: {e}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Mitarbeiter: {e}")
        logger.error(f"Error loading employees: {e}")

    # Add new employee
    st.markdown("---")
    st.markdown("### Neuen Mitarbeiter hinzufügen")

    with st.form("add_employee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("Vorname *")
            last_name = st.text_input("Nachname *")
            city = st.text_input("Wohnort *")

        with col2:
            birth_date_input = st.date_input(
                "Geburtsdatum *",
                value=date(1990, 1, 1),
                max_value=date.today()
            )
            start_date_input = st.date_input(
                "Arbeitsbeginndatum *",
                value=date.today(),
                max_value=date.today()
            )

            # Get positions for dropdown
            try:
                positions = pos_manager.list_positions()
                if positions:
                    position_options = {
                        pos.id: pos.name for pos in positions
                    }
                    position_id = st.selectbox(
                        "Position *",
                        options=list(position_options.keys()),
                        format_func=lambda x: position_options[x]
                    )
                else:
                    st.warning(
                        "Keine Positionen verfügbar. "
                        "Bitte erstellen Sie zuerst eine Position."
                    )
                    position_id = None
            except Exception as e:
                st.error(f"Fehler beim Laden der Positionen: {e}")
                position_id = None

        submitted = st.form_submit_button("Mitarbeiter hinzufügen")

        if submitted:
            if not all([first_name, last_name, city, position_id]):
                st.error("Bitte füllen Sie alle Pflichtfelder aus.")
            else:
                try:
                    new_emp = emp_manager.create_employee(
                        first_name=first_name,
                        last_name=last_name,
                        city=city,
                        birth_date=birth_date_input,
                        position_id=position_id,
                        start_date=start_date_input
                    )
                    st.success(
                        f"Mitarbeiter {new_emp.full_name} erfolgreich erstellt!"
                    )
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Validierungsfehler: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Erstellen: {e}")
                    logger.error(f"Error creating employee: {e}")


def render_position_management_tab():
    """
    Position CRUD operations tab.

    Requirements: 7.2
    """
    st.subheader("Positionsverwaltung")

    db = SessionLocal()
    pos_manager = PositionManager(db)

    # List positions
    st.markdown("### Positionsliste")

    try:
        positions = pos_manager.list_positions()

        if not positions:
            st.info("Keine Positionen vorhanden.")
        else:
            for pos in positions:
                with st.expander(pos.name, expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Name:** {pos.name}")
                        st.write(f"**Beschreibung:** {pos.description or 'N/A'}")

                        # Show assigned criteria
                        try:
                            criteria = pos_manager.get_position_criteria(pos.id)
                            if criteria:
                                st.write("**Zugeordnete Kriterien:**")
                                for crit in criteria:
                                    st.write(f"- {crit.name}")
                            else:
                                st.write("**Zugeordnete Kriterien:** Keine")
                        except Exception as e:
                            st.warning(f"Fehler beim Laden der Kriterien: {e}")

                    with col2:
                        if st.button(
                            " Löschen",
                            key=f"delete_pos_{pos.id}",
                            type="secondary"
                        ):
                            try:
                                pos_manager.delete_position(pos.id)
                                st.success(f"Position {pos.name} gelöscht")
                                st.rerun()
                            except ValidationError as e:
                                st.error(f"Fehler: {e}")
                            except Exception as e:
                                st.error(f"Fehler beim Löschen: {e}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Positionen: {e}")
        logger.error(f"Error loading positions: {e}")

    # Add new position
    st.markdown("---")
    st.markdown("### Neue Position hinzufügen")

    with st.form("add_position_form", clear_on_submit=True):
        name = st.text_input("Positionsname *")
        description = st.text_area("Beschreibung")

        submitted = st.form_submit_button("Position hinzufügen")

        if submitted:
            if not name:
                st.error("Bitte geben Sie einen Positionsnamen ein.")
            else:
                try:
                    new_pos = pos_manager.create_position(
                        name=name,
                        description=description
                    )
                    st.success(
                        f"Position {new_pos.name} erfolgreich erstellt!"
                    )
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Validierungsfehler: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Erstellen: {e}")
                    logger.error(f"Error creating position: {e}")


def render_criterion_management_tab():
    """
    Criterion CRUD operations tab.

    Requirements: 7.2
    """
    st.subheader("Auswertungskriterien-Verwaltung")

    db = SessionLocal()
    crit_manager = CriterionManager(db)

    # List criteria
    st.markdown("### Kriterienliste")

    try:
        criteria = crit_manager.list_criteria()

        if not criteria:
            st.info("Keine Kriterien vorhanden.")
        else:
            # Separate standard and custom criteria
            standard_criteria = [c for c in criteria if c.is_standard]
            custom_criteria = [c for c in criteria if not c.is_standard]

            if standard_criteria:
                st.markdown("#### Standard-Kriterien")
                for crit in standard_criteria:
                    with st.expander(crit.name, expanded=False):
                        st.write(f"**Name:** {crit.name}")
                        st.write(f"**Beschreibung:** {crit.description or 'N/A'}")
                        st.write(
                            f"**Berechnungsmethode:** {crit.calculation_method.value}"
                        )
                        st.info("Standard-Kriterien können nicht gelöscht werden.")

            if custom_criteria:
                st.markdown("#### Benutzerdefinierte Kriterien")
                for crit in custom_criteria:
                    with st.expander(crit.name, expanded=False):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"**Name:** {crit.name}")
                            st.write(
                                f"**Beschreibung:** {crit.description or 'N/A'}"
                            )
                            st.write(
                                f"**Berechnungsmethode:** {crit.calculation_method.value}"
                            )

                        with col2:
                            if st.button(
                                " Löschen",
                                key=f"delete_crit_{crit.id}",
                                type="secondary"
                            ):
                                try:
                                    crit_manager.delete_criterion(crit.id)
                                    st.success(f"Kriterium {crit.name} gelöscht")
                                    st.rerun()
                                except ValidationError as e:
                                    st.error(f"Fehler: {e}")
                                except Exception as e:
                                    st.error(f"Fehler beim Löschen: {e}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Kriterien: {e}")
        logger.error(f"Error loading criteria: {e}")

    # Add new criterion
    st.markdown("---")
    st.markdown("### Neues Kriterium hinzufügen")

    with st.form("add_criterion_form", clear_on_submit=True):
        name = st.text_input("Kriteriumsname *")
        description = st.text_area("Beschreibung")
        calc_method = st.selectbox(
            "Berechnungsmethode *",
            options=[m.value for m in CalculationMethod],
            format_func=lambda x: {
                "SUM": "Summe",
                "AVERAGE": "Durchschnitt",
                "PERCENTAGE": "Prozentsatz",
                "RATIO": "Verhältnis"
            }.get(x, x)
        )

        submitted = st.form_submit_button("Kriterium hinzufügen")

        if submitted:
            if not name:
                st.error("Bitte geben Sie einen Kriteriumnamen ein.")
            else:
                try:
                    new_crit = crit_manager.create_criterion(
                        name=name,
                        description=description,
                        calculation_method=CalculationMethod(calc_method),
                        is_standard=False
                    )
                    st.success(
                        f"Kriterium {new_crit.name} erfolgreich erstellt!"
                    )
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Validierungsfehler: {e}")
                except Exception as e:
                    st.error(f"Fehler beim Erstellen: {e}")
                    logger.error(f"Error creating criterion: {e}")


def render_assignment_tab():
    """
    Position-Criterion assignment interface.

    Requirements: 7.3
    """
    st.subheader("Position-Kriterium Zuordnungen")
    st.caption(
        "Ordnen Sie Auswertungskriterien bestimmten Positionen zu"
    )

    db = SessionLocal()
    pos_manager = PositionManager(db)
    crit_manager = CriterionManager(db)

    try:
        positions = pos_manager.list_positions()
        criteria = crit_manager.list_criteria()

        if not positions:
            st.warning(
                "Keine Positionen vorhanden. "
                "Bitte erstellen Sie zuerst Positionen."
            )
            return

        if not criteria:
            st.warning(
                "Keine Kriterien vorhanden. "
                "Bitte erstellen Sie zuerst Kriterien."
            )
            return

        # Position selector
        position_options = {pos.id: pos.name for pos in positions}
        selected_position_id = st.selectbox(
            "Position auswählen",
            options=list(position_options.keys()),
            format_func=lambda x: position_options[x],
            key="assignment_position_selector"
        )

        if selected_position_id:
            st.markdown("---")

            # Get currently assigned criteria
            assigned_criteria = pos_manager.get_position_criteria(
                selected_position_id
            )
            assigned_ids = {c.id for c in assigned_criteria}

            # Display assigned criteria
            st.markdown("### Zugeordnete Kriterien")
            if assigned_criteria:
                for crit in assigned_criteria:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"✅ {crit.name}")
                    with col2:
                        if st.button(
                            "Entfernen",
                            key=f"remove_crit_{crit.id}",
                            type="secondary"
                        ):
                            try:
                                pos_manager.remove_criteria(
                                    selected_position_id,
                                    [crit.id]
                                )
                                st.success(
                                    f"Kriterium {crit.name} entfernt"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {e}")
            else:
                st.info("Keine Kriterien zugeordnet")

            # Display available criteria
            st.markdown("---")
            st.markdown("### Verfügbare Kriterien")

            available_criteria = [
                c for c in criteria if c.id not in assigned_ids
            ]

            if available_criteria:
                for crit in available_criteria:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"⚪ {crit.name}")
                        if crit.description:
                            st.caption(crit.description)
                    with col2:
                        if st.button(
                            "Zuordnen",
                            key=f"assign_crit_{crit.id}",
                            type="primary"
                        ):
                            try:
                                pos_manager.assign_criteria(
                                    selected_position_id,
                                    [crit.id]
                                )
                                st.success(
                                    f"Kriterium {crit.name} zugeordnet"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {e}")
            else:
                st.info("Alle Kriterien sind bereits zugeordnet")

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        logger.error(f"Error in assignment tab: {e}")



def render_notification_threshold_tab():
    """
    Notification threshold configuration interface.

    Requirements: 21.4
    """
    st.subheader("Benachrichtigungs-Schwellenwerte")
    st.caption(
        "Konfigurieren Sie Schwellenwerte für automatische "
        "Benachrichtigungen bei Quoten"
    )

    # Initialize notification manager
    if "notification_manager" not in st.session_state:
        st.session_state.notification_manager = NotificationManager()

    notification_manager = st.session_state.notification_manager

    # Display current thresholds
    st.markdown("### Aktuelle Schwellenwerte")

    thresholds = notification_manager.get_thresholds()

    if not thresholds:
        st.info("Keine Schwellenwerte konfiguriert.")
    else:
        # Group by quota name
        quota_groups = {}
        for threshold in thresholds:
            if threshold.quota_name not in quota_groups:
                quota_groups[threshold.quota_name] = []
            quota_groups[threshold.quota_name].append(threshold)

        for quota_name, quota_thresholds in quota_groups.items():
            with st.expander(f" {quota_name}", expanded=False):
                for threshold in quota_thresholds:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        # Notification type icon
                        type_icons = {
                            NotificationType.SUCCESS: "✅",
                            NotificationType.INFO: "ℹ️",
                            NotificationType.WARNING: "⚠️",
                            NotificationType.ERROR: "❌"
                        }
                        icon = type_icons.get(
                            threshold.notification_type,
                            "🔔"
                        )
                        st.write(
                            f"{icon} {threshold.notification_type.value}"
                        )

                    with col2:
                        threshold_text = (
                            "über" if threshold.threshold_type ==
                            ThresholdType.ABOVE else "unter"
                        )
                        st.write(f"{threshold_text}")

                    with col3:
                        st.write(f"{threshold.threshold_value:.1f}%")

                    with col4:
                        if st.button(
                            "🗑️",
                            key=f"remove_threshold_{quota_name}_{threshold.threshold_value}_{threshold.threshold_type.value}",
                            help="Schwellenwert entfernen"
                        ):
                            notification_manager.remove_threshold(
                                quota_name,
                                threshold.threshold_value,
                                threshold.threshold_type
                            )
                            st.success("Schwellenwert entfernt")
                            st.rerun()

                st.caption(threshold.message_template)

    # Add new threshold
    st.markdown("---")
    st.markdown("### Neuen Schwellenwert hinzufügen")

    # Common quota names
    common_quotas = [
        "Abschlussquote",
        "Terminvereinbarungsquote",
        "Termine-Anfahrquote",
        "Nicht interessierte Kunden Quote",
        "Technisch nicht machbar Quote",
        "Quote der nicht erreichten Kunden",
        "Quote für Folgetermine-Vereinbarungen",
        "Quote für Angebote",
        "Quote für zu teuer",
        "QC bestanden Quote"
    ]

    with st.form("add_threshold_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            quota_name = st.selectbox(
                "Quota auswählen *",
                options=common_quotas,
                help="Wählen Sie die Quote für den Schwellenwert"
            )

            threshold_value = st.number_input(
                "Schwellenwert (%) *",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                help="Prozentwert für den Schwellenwert"
            )

            threshold_type = st.selectbox(
                "Schwellenwert-Typ *",
                options=[t.value for t in ThresholdType],
                format_func=lambda x: {
                    "above": "Über (Benachrichtigung wenn Quote höher)",
                    "below": "Unter (Benachrichtigung wenn Quote niedriger)"
                }.get(x, x),
                help="Wann soll die Benachrichtigung ausgelöst werden?"
            )

        with col2:
            notification_type = st.selectbox(
                "Benachrichtigungs-Typ *",
                options=[t.value for t in NotificationType],
                format_func=lambda x: {
                    "success": "✅ Erfolg (Grün)",
                    "info": "ℹ️ Information (Blau)",
                    "warning": "⚠️ Warnung (Gelb)",
                    "error": "❌ Fehler (Rot)"
                }.get(x, x),
                help="Art der Benachrichtigung"
            )

            message_template = st.text_area(
                "Nachrichtenvorlage *",
                value=(
                    "Die {quota_name} beträgt {quota_value:.1f}% "
                    "(Schwellenwert: {threshold_value:.1f}%)"
                ),
                help=(
                    "Verwenden Sie {quota_value} und {threshold_value} "
                    "als Platzhalter"
                ),
                height=100
            )

        submitted = st.form_submit_button(
            "Schwellenwert hinzufügen",
            type="primary"
        )

        if submitted:
            if not all([quota_name, message_template]):
                st.error("Bitte füllen Sie alle Pflichtfelder aus.")
            else:
                try:
                    notification_manager.add_threshold(
                        quota_name=quota_name,
                        threshold_value=threshold_value,
                        threshold_type=ThresholdType(threshold_type),
                        notification_type=NotificationType(notification_type),
                        message_template=message_template
                    )
                    st.success(
                        f"Schwellenwert für {quota_name} hinzugefügt!"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Hinzufügen: {e}")
                    logger.error(f"Error adding threshold: {e}")

    # Info box
    st.markdown("---")
    st.info(
        """
        **💡 Hinweise:**
        - Schwellenwerte werden verwendet, um automatische 
          Benachrichtigungen zu generieren
        - "Über"-Schwellenwerte lösen aus, wenn die Quote den Wert 
          überschreitet
        - "Unter"-Schwellenwerte lösen aus, wenn die Quote den Wert 
          unterschreitet
        - Verwenden Sie {quota_value} und {threshold_value} in der 
          Nachrichtenvorlage
        - Mehrere Schwellenwerte pro Quote sind möglich
        """
    )
