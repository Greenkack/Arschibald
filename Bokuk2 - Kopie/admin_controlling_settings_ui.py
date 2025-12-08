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
        "Mitarbeiter",
        "Positionen",
        "Auswertungskriterien",
        "Zuordnungen",
        "Team",
        "Benachrichtigungen"
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
        render_team_management_tab()

    with tabs[5]:
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
    
    try:
        from controlling.team_manager import TeamManager
        team_manager = TeamManager(db)
    except ImportError:
        team_manager = None

    # ==========================================
    # ADD NEW EMPLOYEE FORM - AT THE TOP!
    # ==========================================
    with st.expander("➕ Neuen Mitarbeiter hinzufügen", expanded=False):
        with st.form("add_employee_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("Vorname *")
                last_name = st.text_input("Nachname *")
                agent_name = st.text_input("Agentname (optional)")
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
                
                # Get teams for dropdown
                team_id = None
                if team_manager:
                    try:
                        teams = team_manager.list_teams(active_only=True)
                        if teams:
                            team_options = {0: "Kein Team"}
                            team_options.update({t.id: t.name for t in teams})
                            
                            selected_team = st.selectbox(
                                "Team",
                                options=list(team_options.keys()),
                                format_func=lambda x: team_options[x],
                                index=0,
                                key="new_employee_team"
                            )
                            team_id = selected_team if selected_team != 0 else None
                        else:
                            st.info("Keine Teams verfügbar. Team-Zuordnung optional.")
                    except Exception as e:
                        st.warning(f"Team-Auswahl nicht verfügbar: {e}")

            submitted = st.form_submit_button("Mitarbeiter hinzufügen", type="primary")

            if submitted:
                if not all([first_name, last_name, city, position_id]):
                    st.error("Bitte füllen Sie alle Pflichtfelder aus.")
                else:
                    try:
                        new_emp = emp_manager.create_employee(
                            first_name=first_name,
                            last_name=last_name,
                            agent_name=agent_name if agent_name.strip() else None,
                            city=city,
                            birth_date=birth_date_input,
                            position_id=position_id,
                            start_date=start_date_input
                        )
                        
                        # Assign to team if selected
                        if team_id and team_manager:
                            try:
                                team_manager.assign_employee_to_team(new_emp.id, team_id)
                            except Exception as e:
                                logger.error(f"Error assigning team: {e}")
                        
                        st.success(
                            f"Mitarbeiter {new_emp.full_name} erfolgreich erstellt!"
                        )
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"Validierungsfehler: {e}")
                    except Exception as e:
                        st.error(f"Fehler beim Erstellen: {e}")
                        logger.error(f"Error creating employee: {e}")

    # ==========================================
    # EMPLOYEE LIST - COMPACT VIEW
    # ==========================================
    st.markdown("---")
    st.markdown("### Mitarbeiterliste")

    try:
        employees = emp_manager.list_employees()

        if not employees:
            st.info("Keine Mitarbeiter vorhanden. Erstellen Sie einen neuen Mitarbeiter oben.")
        else:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt", len(employees))
            with col2:
                active_count = sum(1 for emp in employees if emp.is_active)
                st.metric("Aktiv", active_count)
            with col3:
                if team_manager:
                    with_team = sum(1 for emp in employees if hasattr(emp, 'team_id') and emp.team_id)
                    st.metric("Mit Team", with_team)
            
            st.markdown("---")
            
            # Display employees in compact expanders
            for emp in employees:
                # Create compact title with key info
                title_parts = [f"{emp.full_name}"]
                title_parts.append(f"• {emp.position.name if emp.position else 'Keine Position'}")
                
                if team_manager and hasattr(emp, 'team') and emp.team:
                    title_parts.append(f"• Team: {emp.team.name}")
                
                title = " ".join(title_parts)
                
                with st.expander(title, expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.markdown("**Stammdaten**")
                        st.write(f"Vorname: {emp.first_name}")
                        st.write(f"Nachname: {emp.last_name}")
                        st.write(f"Agentname: {emp.agent_name or 'Nicht angegeben'}")
                        st.write(f"Wohnort: {emp.city}")

                    with col2:
                        st.markdown("**Beschäftigung**")
                        st.write(f"Geburtsdatum: {emp.birth_date}")
                        st.write(f"Alter: {emp.age} Jahre")
                        st.write(f"Start: {emp.start_date}")
                        st.write(f"Gearbeitete Tage: {emp.days_employed}")
                        
                        st.markdown("**Zuordnungen**")
                        st.write(f"Position: {emp.position.name if emp.position else 'N/A'}")
                        
                        # Team info
                        if team_manager:
                            if hasattr(emp, 'team') and emp.team:
                                st.write(f"Team: {emp.team.name}")
                            else:
                                st.write("Team: Nicht zugeordnet")

                    with col3:
                        st.markdown("**Aktionen**")
                        
                        # Edit button
                        if st.button(
                            "Bearbeiten",
                            key=f"edit_emp_{emp.id}",
                            use_container_width=True
                        ):
                            st.session_state[f"editing_emp_{emp.id}"] = True
                            st.rerun()
                        
                        # Delete button with confirmation
                        if st.button(
                            "Löschen",
                            key=f"delete_emp_{emp.id}",
                            type="secondary",
                            use_container_width=True
                        ):
                            st.session_state[f"confirm_delete_emp_{emp.id}"] = True
                            st.rerun()
                        
                        # Delete confirmation dialog
                        if st.session_state.get(f"confirm_delete_emp_{emp.id}", False):
                            st.warning(f"Wirklich löschen?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("Ja", key=f"confirm_yes_emp_{emp.id}", type="primary"):
                                    try:
                                        emp_manager.delete_employee(emp.id)
                                        st.success(f"{emp.full_name} gelöscht")
                                        del st.session_state[f"confirm_delete_emp_{emp.id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler: {e}")
                            with col_no:
                                if st.button("Nein", key=f"confirm_no_emp_{emp.id}"):
                                    del st.session_state[f"confirm_delete_emp_{emp.id}"]
                                    st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_emp_{emp.id}", False):
                        st.markdown("---")
                        with st.form(f"edit_emp_form_{emp.id}"):
                            st.markdown("#### Mitarbeiter bearbeiten")
                            
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                new_first_name = st.text_input("Vorname", value=emp.first_name, key=f"edit_fn_{emp.id}")
                                new_last_name = st.text_input("Nachname", value=emp.last_name, key=f"edit_ln_{emp.id}")
                                new_agent_name = st.text_input("Agentname", value=emp.agent_name or "", key=f"edit_an_{emp.id}")
                            with col_e2:
                                new_city = st.text_input("Wohnort", value=emp.city, key=f"edit_city_{emp.id}")
                                positions = pos_manager.list_positions()
                                pos_options = {p.id: p.name for p in positions}
                                new_position_id = st.selectbox(
                                    "Position",
                                    options=list(pos_options.keys()),
                                    format_func=lambda x: pos_options[x],
                                    index=list(pos_options.keys()).index(emp.position_id) if emp.position_id in pos_options else 0,
                                    key=f"edit_pos_{emp.id}"
                                )
                            
                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                submitted = st.form_submit_button("Speichern", type="primary", use_container_width=True)
                            with col_cancel:
                                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
                            
                            if submitted:
                                try:
                                    emp_manager.update_employee(
                                        employee_id=emp.id,
                                        first_name=new_first_name,
                                        last_name=new_last_name,
                                        agent_name=new_agent_name if new_agent_name.strip() else None,
                                        city=new_city,
                                        position_id=new_position_id
                                    )
                                    st.success(f"{new_first_name} {new_last_name} aktualisiert!")
                                    del st.session_state[f"editing_emp_{emp.id}"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler: {e}")
                            
                            if cancelled:
                                del st.session_state[f"editing_emp_{emp.id}"]
                                st.rerun()

    except Exception as e:
        st.error(f"Fehler beim Laden der Mitarbeiter: {e}")
        logger.error(f"Error loading employees: {e}")
    finally:
        db.close()

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
                        # Edit button
                        if st.button("Bearbeiten", key=f"edit_pos_{pos.id}", use_container_width=True):
                            st.session_state[f"editing_pos_{pos.id}"] = True
                            st.rerun()
                        
                        # Delete button
                        if st.button(
                            "Löschen",
                            key=f"delete_pos_{pos.id}",
                            type="secondary",
                            use_container_width=True
                        ):
                            st.session_state[f"confirm_delete_pos_{pos.id}"] = True
                            st.rerun()
                        
                        # Delete confirmation
                        if st.session_state.get(f"confirm_delete_pos_{pos.id}", False):
                            st.warning("Wirklich löschen?")
                            col_y, col_n = st.columns(2)
                            with col_y:
                                if st.button("Ja", key=f"yes_pos_{pos.id}", type="primary"):
                                    try:
                                        pos_manager.delete_position(pos.id)
                                        st.success(f"{pos.name} gelöscht")
                                        del st.session_state[f"confirm_delete_pos_{pos.id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler: {e}")
                            with col_n:
                                if st.button("Nein", key=f"no_pos_{pos.id}"):
                                    del st.session_state[f"confirm_delete_pos_{pos.id}"]
                                    st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_pos_{pos.id}", False):
                        st.markdown("---")
                        with st.form(f"edit_pos_form_{pos.id}"):
                            st.markdown("#### Position bearbeiten")
                            new_name = st.text_input("Name", value=pos.name, key=f"edit_pname_{pos.id}")
                            new_desc = st.text_area("Beschreibung", value=pos.description or "", key=f"edit_pdesc_{pos.id}")
                            
                            col_s, col_c = st.columns(2)
                            with col_s:
                                submitted = st.form_submit_button("Speichern", type="primary", use_container_width=True)
                            with col_c:
                                cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
                            
                            if submitted:
                                try:
                                    pos_manager.update_position(pos.id, name=new_name, description=new_desc)
                                    st.success(f"{new_name} aktualisiert!")
                                    del st.session_state[f"editing_pos_{pos.id}"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler: {e}")
                            if cancelled:
                                del st.session_state[f"editing_pos_{pos.id}"]
                                st.rerun()

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
                            # Edit button
                            if st.button("Bearbeiten", key=f"edit_crit_{crit.id}", use_container_width=True):
                                st.session_state[f"editing_crit_{crit.id}"] = True
                                st.rerun()
                            
                            # Delete button
                            if st.button(
                                "Löschen",
                                key=f"delete_crit_{crit.id}",
                                type="secondary",
                                use_container_width=True
                            ):
                                st.session_state[f"confirm_delete_crit_{crit.id}"] = True
                                st.rerun()
                            
                            # Delete confirmation
                            if st.session_state.get(f"confirm_delete_crit_{crit.id}", False):
                                st.warning("Wirklich löschen?")
                                col_y, col_n = st.columns(2)
                                with col_y:
                                    if st.button("Ja", key=f"yes_crit_{crit.id}", type="primary"):
                                        try:
                                            crit_manager.delete_criterion(crit.id)
                                            st.success(f"{crit.name} gelöscht")
                                            del st.session_state[f"confirm_delete_crit_{crit.id}"]
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Fehler: {e}")
                                with col_n:
                                    if st.button("Nein", key=f"no_crit_{crit.id}"):
                                        del st.session_state[f"confirm_delete_crit_{crit.id}"]
                                        st.rerun()
                        
                        # Edit form
                        if st.session_state.get(f"editing_crit_{crit.id}", False):
                            st.markdown("---")
                            with st.form(f"edit_crit_form_{crit.id}"):
                                st.markdown("#### Kriterium bearbeiten")
                                new_cname = st.text_input("Name", value=crit.name, key=f"edit_cname_{crit.id}")
                                new_cdesc = st.text_area("Beschreibung", value=crit.description or "", key=f"edit_cdesc_{crit.id}")
                                
                                col_s, col_c = st.columns(2)
                                with col_s:
                                    submitted = st.form_submit_button("Speichern", type="primary", use_container_width=True)
                                with col_c:
                                    cancelled = st.form_submit_button("Abbrechen", use_container_width=True)
                                
                                if submitted:
                                    try:
                                        crit_manager.update_criterion(crit.id, name=new_cname, description=new_cdesc)
                                        st.success(f"{new_cname} aktualisiert!")
                                        del st.session_state[f"editing_crit_{crit.id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler: {e}")
                                if cancelled:
                                    del st.session_state[f"editing_crit_{crit.id}"]
                                    st.rerun()

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
    Position-Criterion and Team-Employee assignment interface.

    Requirements: 7.3
    """
    st.subheader("Zuordnungen")
    
    # Create tabs for different assignment types
    assignment_tabs = st.tabs([
        "Position ↔ Kriterium",
        "Mitarbeiter ↔ Team"
    ])
    
    # Tab 1: Position-Criterion assignments
    with assignment_tabs[0]:
        render_position_criterion_assignments()
    
    # Tab 2: Employee-Team assignments
    with assignment_tabs[1]:
        render_employee_team_assignments()


def render_position_criterion_assignments():
    """
    Position-Criterion assignment interface.
    
    Requirements: 7.3
    """
    st.markdown("### Position-Kriterium Zuordnungen")
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
                        st.write(f" {crit.name}")
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
                        st.write(f" {crit.name}")
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
    finally:
        db.close()


def render_employee_team_assignments():
    """
    Employee-Team assignment interface with bulk operations.
    
    Allows assigning employees to teams individually or in bulk.
    """
    st.markdown("### Mitarbeiter ↔ Team Zuordnungen")
    st.caption(
        "Weisen Sie Mitarbeiter zu Teams zu für Team-basierte Auswertungen"
    )
    
    db = SessionLocal()
    
    try:
        from controlling.team_manager import TeamManager
        from controlling.managers import EmployeeManager
        
        team_manager = TeamManager(db)
        emp_manager = EmployeeManager(db)
        
        # Get all teams and employees
        teams = team_manager.list_teams(active_only=True, include_employee_count=True)
        all_employees = emp_manager.list_employees()
        
        if not teams:
            st.warning("Keine Teams vorhanden. Bitte erstellen Sie zuerst Teams im 'Team'-Tab.")
            return
        
        if not all_employees:
            st.warning("Keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst Mitarbeiter.")
            return
        
        # Team selector
        col1, col2 = st.columns([3, 1])
        
        with col1:
            team_options = {t.id: f"{t.name} ({getattr(t, 'employee_count', 0)} Mitarbeiter)" for t in teams}
            selected_team_id = st.selectbox(
                "Team auswählen",
                options=list(team_options.keys()),
                format_func=lambda x: team_options[x],
                key="team_assignment_selector"
            )
        
        with col2:
            # Show team info
            selected_team = team_manager.get_team(selected_team_id)
            if selected_team and selected_team.team_leader_id:
                leader = emp_manager.get_employee(selected_team.team_leader_id)
                if leader:
                    st.info(f"Teamleiter: {leader.full_name}")
        
        if selected_team_id:
            st.markdown("---")
            
            # Get current team members
            team_members = team_manager.get_team_members(selected_team_id, active_only=True)
            team_member_ids = {emp.id for emp in team_members}
            
            # Display current team members
            st.markdown("### Team-Mitglieder")
            
            if team_members:
                for emp in team_members:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**{emp.full_name}**")
                    
                    with col2:
                        st.caption(f"{emp.position.name}")
                    
                    with col3:
                        if st.button(
                            "Entfernen",
                            key=f"remove_emp_{emp.id}_from_team",
                            type="secondary"
                        ):
                            try:
                                team_manager.assign_employee_to_team(emp.id, None)
                                st.success(f"{emp.full_name} aus Team entfernt")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {e}")
            else:
                st.info("Keine Mitarbeiter in diesem Team")
            
            # Display available employees (not in this team)
            st.markdown("---")
            st.markdown("### Verfügbare Mitarbeiter")
            
            available_employees = [
                emp for emp in all_employees 
                if emp.id not in team_member_ids
            ]
            
            if available_employees:
                # Bulk assignment option
                with st.expander("🔄 Mehrere Mitarbeiter gleichzeitig zuweisen"):
                    employee_options = {
                        emp.id: f"{emp.full_name} ({emp.position.name})" 
                        for emp in available_employees
                    }
                    
                    selected_emp_ids = st.multiselect(
                        "Mitarbeiter auswählen",
                        options=list(employee_options.keys()),
                        format_func=lambda x: employee_options[x],
                        key="bulk_assign_employees"
                    )
                    
                    if st.button("Ausgewählte Mitarbeiter zuweisen", type="primary"):
                        if selected_emp_ids:
                            success_count = 0
                            for emp_id in selected_emp_ids:
                                try:
                                    team_manager.assign_employee_to_team(
                                        emp_id, 
                                        selected_team_id
                                    )
                                    success_count += 1
                                except Exception as e:
                                    st.error(f"Fehler bei Mitarbeiter {emp_id}: {e}")
                            
                            if success_count > 0:
                                st.success(
                                    f"{success_count} Mitarbeiter erfolgreich zugewiesen"
                                )
                                st.rerun()
                        else:
                            st.warning("Keine Mitarbeiter ausgewählt")
                
                st.markdown("### Einzelzuweisung")
                
                # Individual assignment
                for emp in available_employees:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{emp.full_name}**")
                    
                    with col2:
                        st.caption(f"{emp.position.name}")
                    
                    with col3:
                        # Show current team if any
                        if emp.team_id:
                            current_team = team_manager.get_team(emp.team_id)
                            if current_team:
                                st.caption(f"Team: {current_team.name}")
                        else:
                            st.caption("Kein Team")
                    
                    with col4:
                        if st.button(
                            "Zuweisen",
                            key=f"assign_emp_{emp.id}_to_team",
                            type="primary"
                        ):
                            try:
                                team_manager.assign_employee_to_team(
                                    emp.id, 
                                    selected_team_id
                                )
                                st.success(
                                    f"{emp.full_name} zu Team zugewiesen"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {e}")
            else:
                st.success("Alle Mitarbeiter sind bereits in diesem Team")
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        logger.error(f"Error in employee-team assignment: {e}")
    finally:
        db.close()



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
            with st.expander(f"{quota_name}", expanded=False):
                for threshold in quota_thresholds:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        # Notification type icon
                        type_icons = {
                            NotificationType.SUCCESS: "",
                            NotificationType.INFO: "ℹ",
                            NotificationType.WARNING: "",
                            NotificationType.ERROR: ""
                        }
                        icon = type_icons.get(
                            threshold.notification_type,
                            ""
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
                            "Löschen",
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
                    "success": " Erfolg (Grün)",
                    "info": "ℹ Information (Blau)",
                    "warning": " Warnung (Gelb)",
                    "error": " Fehler (Rot)"
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
        **Hinweise:**
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


def render_team_management_tab():
    """
    Team CRUD operations tab.
    
    Requirements: Team organization and management
    """
    st.subheader("Team-Verwaltung")

    db = SessionLocal()
    
    try:
        from controlling.team_manager import TeamManager
        from controlling.managers import EmployeeManager
        
        team_manager = TeamManager(db)
        emp_manager = EmployeeManager(db)
    except ImportError as e:
        st.error(f"Team-Manager konnte nicht geladen werden: {e}")
        db.close()
        return

    # ==========================================
    # ADD NEW TEAM FORM - AT THE TOP!
    # ==========================================
    with st.expander("➕ Neues Team erstellen", expanded=False):
        with st.form("create_team_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                team_name = st.text_input(
                    "Team-Name *",
                    placeholder="z.B. Vertrieb Nord, Call Center Team A"
                )
            
            with col2:
                # Team leader selection
                all_employees = emp_manager.list_employees()
                leader_options = {"Kein Teamleiter": None}
                leader_options.update({
                    f"{emp.full_name} ({emp.position.name})": emp.id
                    for emp in all_employees
                })
                
                selected_leader = st.selectbox(
                    "Teamleiter (optional)",
                    options=list(leader_options.keys())
                )
            
            team_description = st.text_area(
                "Beschreibung (optional)",
                placeholder="Beschreibung des Teams...",
                height=100
            )

            submitted = st.form_submit_button("Team erstellen", type="primary")

            if submitted:
                if not team_name.strip():
                    st.error("Bitte geben Sie einen Team-Namen ein.")
                else:
                    try:
                        new_team = team_manager.create_team(
                            name=team_name,
                            description=team_description if team_description.strip() else None,
                            team_leader_id=leader_options[selected_leader]
                        )
                        st.success(f"Team '{new_team.name}' erfolgreich erstellt!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Fehler beim Erstellen: {e}")
                        logger.error(f"Error creating team: {e}")

    # ==========================================
    # TEAM LIST - COMPACT VIEW
    # ==========================================
    st.markdown("---")
    st.markdown("### Team-Liste")

    try:
        teams = team_manager.list_teams(active_only=False, include_employee_count=True)

        if not teams:
            st.info("Keine Teams vorhanden. Erstellen Sie ein neues Team oben.")
        else:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt", len(teams))
            with col2:
                active_count = sum(1 for t in teams if t.is_active)
                st.metric("Aktiv", active_count)
            with col3:
                total_members = sum(
                    getattr(t, 'employee_count', 0) for t in teams
                )
                st.metric("Mitglieder", total_members)
            
            st.markdown("---")
            
            # Display teams in expandable sections
            # Display teams in compact expanders
            for team in teams:
                # Create compact title
                title_parts = [
                    f"[{'Aktiv' if team.is_active else 'Inaktiv'}] {team.name}",
                    f"• {getattr(team, 'employee_count', 0)} Mitarbeiter"
                ]
                
                # Add team leader to title
                if team.team_leader_id:
                    leader = emp_manager.get_employee(team.team_leader_id)
                    if leader:
                        title_parts.append(f"• Leiter: {leader.full_name}")
                
                title = " ".join(title_parts)
                
                with st.expander(title, expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown("**Team-Info**")
                        st.write(f"Name: {team.name}")
                        st.write(f"Status: {'Aktiv' if team.is_active else 'Inaktiv'}")
                        if team.description:
                            st.write(f"Beschreibung: {team.description}")
                    
                    with col2:
                        # Team leader
                        st.markdown("**Führung**")
                        if team.team_leader_id:
                            leader = emp_manager.get_employee(team.team_leader_id)
                            if leader:
                                st.write(f"Teamleiter: {leader.full_name}")
                        else:
                            st.write("Teamleiter: Nicht zugewiesen")
                        
                        # Team members
                        st.markdown("**Mitglieder**")
                        members = team_manager.get_team_members(team.id, active_only=False)
                        if members:
                            st.write(f"Anzahl: {len(members)}")
                            with st.expander("Details anzeigen", expanded=False):
                                for member in members:
                                    status = "Aktiv" if member.is_active else "Inaktiv"
                                    st.markdown(
                                        f"- {status} {member.full_name} ({member.position.name})"
                                    )
                        else:
                            st.write("Keine Mitglieder")
                    
                    with col3:
                        st.markdown("**Aktionen**")
                        # Edit button
                        if st.button(
                            "Bearbeiten",
                            key=f"edit_team_{team.id}",
                            use_container_width=True
                        ):
                            st.session_state[f"editing_team_{team.id}"] = True
                            st.rerun()
                        
                        # Delete button with confirmation
                        member_count = len(team_manager.get_team_members(team.id, active_only=True))
                        if st.button(
                            "Löschen",
                            key=f"delete_team_{team.id}",
                            type="secondary",
                            use_container_width=True,
                            disabled=member_count > 0
                        ):
                            st.session_state[f"confirm_delete_team_{team.id}"] = True
                            st.rerun()
                        
                        if member_count > 0:
                            st.caption(f"{member_count} aktiv")
                        
                        # Delete confirmation
                        if st.session_state.get(f"confirm_delete_team_{team.id}", False):
                            st.warning("Wirklich löschen?")
                            col_y, col_n = st.columns(2)
                            with col_y:
                                if st.button("Ja", key=f"yes_team_{team.id}", type="primary"):
                                    try:
                                        team_manager.delete_team(team.id, force=False)
                                        st.success(f"Team '{team.name}' gelöscht!")
                                        del st.session_state[f"confirm_delete_team_{team.id}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler: {e}")
                            with col_n:
                                if st.button("Nein", key=f"no_team_{team.id}"):
                                    del st.session_state[f"confirm_delete_team_{team.id}"]
                                    st.rerun()

                    
                    # Edit form
                    if st.session_state.get(f"editing_team_{team.id}", False):
                        st.markdown("---")
                        with st.form(f"edit_team_form_{team.id}"):
                            st.markdown("#### Team bearbeiten")
                            
                            new_name = st.text_input(
                                "Team-Name",
                                value=team.name,
                                key=f"edit_name_{team.id}"
                            )
                            
                            new_description = st.text_area(
                                "Beschreibung",
                                value=team.description or "",
                                key=f"edit_desc_{team.id}",
                                height=100
                            )
                            
                            # Team leader selection
                            all_employees = emp_manager.list_employees()
                            leader_options = {"Kein Teamleiter": None}
                            leader_options.update({
                                f"{emp.full_name} ({emp.position.name})": emp.id
                                for emp in all_employees
                            })
                            
                            current_leader_label = "Kein Teamleiter"
                            if team.team_leader_id:
                                leader = emp_manager.get_employee(team.team_leader_id)
                                if leader:
                                    current_leader_label = f"{leader.full_name} ({leader.position.name})"
                            
                            selected_leader = st.selectbox(
                                "Teamleiter",
                                options=list(leader_options.keys()),
                                index=list(leader_options.keys()).index(current_leader_label),
                                key=f"edit_leader_{team.id}"
                            )
                            
                            new_is_active = st.checkbox(
                                "Team aktiv",
                                value=team.is_active,
                                key=f"edit_active_{team.id}"
                            )
                            
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                submitted = st.form_submit_button(
                                    "Speichern",
                                    type="primary",
                                    use_container_width=True
                                )
                            
                            with col_cancel:
                                cancelled = st.form_submit_button(
                                    "Abbrechen",
                                    use_container_width=True
                                )
                            
                            if submitted:
                                try:
                                    team_manager.update_team(
                                        team_id=team.id,
                                        name=new_name,
                                        description=new_description,
                                        team_leader_id=leader_options[selected_leader],
                                        is_active=new_is_active
                                    )
                                    st.success(f"Team '{new_name}' aktualisiert!")
                                    del st.session_state[f"editing_team_{team.id}"]
                                    st.rerun()
                                except ValidationError as e:
                                    st.error(str(e))
                            
                            if cancelled:
                                del st.session_state[f"editing_team_{team.id}"]
                                st.rerun()

    except Exception as e:
        st.error(f"Fehler beim Laden der Teams: {e}")
        logger.error(f"Error loading teams: {e}")
    finally:
        db.close()

