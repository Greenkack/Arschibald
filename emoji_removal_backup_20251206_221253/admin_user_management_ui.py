"""
admin_user_management_ui.py
Zweck: Admin-UI für vollständige Benutzerverwaltung
"""

import pandas as pd
import streamlit as st

from user_management import UserManagement

# Rang-Hierarchie
RANKS = [
    "Praktikant",
    "Junior Mitarbeiter",
    "Mitarbeiter",
    "Senior Mitarbeiter",
    "Team Lead",
    "Abteilungsleiter",
    "Geschäftsführer",
    "Administrator"
]

# Rollen
ROLES = {
    "user": "Benutzer",
    "manager": "Manager",
    "admin": "Administrator"
}

# Standard-Berechtigungen
DEFAULT_PERMISSIONS = {
    "view_data": "Daten ansehen",
    "edit_data": "Daten bearbeiten",
    "create_offers": "Angebote erstellen",
    "view_finances": "Finanzen einsehen",
    "manage_users": "Benutzer verwalten",
    "admin_panel": "Admin-Panel"
}


def render_user_management_tab():
    """Rendert den Benutzerverwaltungs-Tab"""

    st.markdown("### Benutzerverwaltung")

    # User Management initialisieren
    um = UserManagement()

    # Haupt-Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Benutzerliste",
        "Benutzer erstellen",
        "Statistiken",
        "Import/Export"
    ])

    # Tab 1: Benutzerliste
    with tab1:
        render_user_list(um)

    # Tab 2: Benutzer erstellen
    with tab2:
        render_create_user(um)

    # Tab 3: Statistiken
    with tab3:
        render_statistics(um)

    # Tab 4: Import/Export
    with tab4:
        render_import_export(um)


def render_user_list(um: UserManagement):
    """Rendert die Benutzerliste"""

    st.markdown("#### Alle Benutzer")

    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status filtern",
            options=[
                "Alle",
                "active",
                "terminated",
                "deleted"],
            format_func=lambda x: {
                "Alle": "Alle",
                "active": "Aktiv",
                "terminated": "Gekündigt",
                "deleted": "Gelöscht"}[x])

    with col2:
        search_term = st.text_input(
            "Suchen", placeholder="Name oder Benutzername")

    with col3:
        if st.button("Aktualisieren", use_container_width=True):
            st.rerun()

    # Benutzer laden
    if status_filter == "Alle":
        users = um.list_users()
    else:
        users = um.list_users(status=status_filter)

    # Filtern nach Suchbegriff
    if search_term:
        users = [u for u in users if search_term.lower() in u['username'].lower(
        ) or search_term.lower() in u.get('full_name', '').lower()]

    if not users:
        st.info("Keine Benutzer gefunden.")
        return

    # Benutzer anzeigen
    for user in users:
        # Prefix basierend auf Rolle und Super-Admin Status
        is_super = user.get('is_super_admin', 0) == 1
        if is_super:
            role_prefix = "⭐ [SUPER-ADMIN] "
        elif user['role'] == 'admin':
            role_prefix = "[Admin] "
        else:
            role_prefix = ""

        with st.expander(f"{role_prefix}{user['username']} - {user.get('full_name', 'N/A')}",
                         expanded=False):

            # Super-Admin Warnung
            if is_super:
                st.error(
                    "[LOCK] SUPER-ADMIN: Höchste Sicherheitsstufe - Kann nur Rechte selbst übertragen")

            col_info1, col_info2 = st.columns(2)

            with col_info1:
                st.markdown(f"""
                **ID:** {user['id']}
                **Benutzername:** `{user['username']}`
                **Vollständiger Name:** {user.get('full_name', 'N/A')}
                **Email:** {user.get('email', 'N/A')}
                **Telefon:** {user.get('phone', 'N/A')}
                **Firma:** {user.get('company_id', 'N/A')}
                """)

            with col_info2:
                st.markdown(f"""
                **Rang:** {user['rank']}
                **Rolle:** {ROLES.get(user['role'], user['role'])}
                **Provision:** {user['commission_rate']}%
                **Status:** {user['status']}
                **Erstellt:** {user['created_at'][:10]}
                **Letzter Login:** {user.get('last_login', 'Nie')[:10] if user.get('last_login') else 'Nie'}
                """)

            # Berechtigungen
            if user['permissions']:
                st.markdown("**Berechtigungen:**")
                perms = user['permissions']
                if isinstance(perms, dict):
                    if perms.get('all'):
                        st.success("Alle Berechtigungen")
                    else:
                        perm_list = [
                            DEFAULT_PERMISSIONS.get(
                                k, k) for k, v in perms.items() if v]
                        if perm_list:
                            st.write(", ".join(perm_list))

            # Notizen
            if user.get('notes'):
                st.info(f"Notiz: {user['notes']}")

            st.markdown("---")

            # Aktionen
            st.markdown("##### Aktionen")

            # Super-Admin kann nicht bearbeitet/gelöscht werden
            if is_super:
                st.warning(
                    "[LOCK] Super-Admin kann nur selbst seine Daten ändern oder Rechte übertragen")
                if st.button("Rechte übertragen", key=f"transfer_{user['id']}",
                             use_container_width=True, type="primary"):
                    st.session_state[f'transfer_super_admin_{user["id"]}'] = True
                    st.rerun()
            else:
                col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns(
                    5)

                with col_act1:
                    if st.button(
                            "Bearbeiten",
                            key=f"edit_{
                                user['id']}",
                            use_container_width=True):
                        st.session_state[f'editing_user_{user["id"]}'] = True
                        st.rerun()

                with col_act2:
                    if st.button(
                            "Passwort",
                            key=f"pwd_{
                                user['id']}",
                            use_container_width=True):
                        st.session_state[f'change_pwd_{user["id"]}'] = True
                        st.rerun()

                with col_act3:
                    if user['status'] == 'active':
                        if st.button(
                                "Befördern",
                                key=f"promote_{
                                    user['id']}",
                                use_container_width=True):
                            st.session_state[f'promote_user_{user["id"]}'] = True
                            st.rerun()

                with col_act4:
                    if user['status'] == 'active':
                        if st.button(
                                "Kündigen",
                                key=f"term_{
                                    user['id']}",
                                use_container_width=True):
                            st.session_state[f'terminate_user_{user["id"]}'] = True
                            st.rerun()

                with col_act5:
                    if user['username'] not in ['admin', 'TSchwarz']:
                        if st.button(
                                "Löschen",
                                key=f"del_{
                                    user['id']}",
                                use_container_width=True):
                            st.session_state[f'delete_user_{user["id"]}'] = True
                            st.rerun()

            # Bearbeitungsformulare
            if st.session_state.get(f'editing_user_{user["id"]}'):
                render_edit_user_form(um, user)

            if st.session_state.get(f'change_pwd_{user["id"]}'):
                render_change_password_form(um, user)

            if st.session_state.get(f'promote_user_{user["id"]}'):
                render_promote_form(um, user)

            if st.session_state.get(f'terminate_user_{user["id"]}'):
                render_terminate_form(um, user)

            if st.session_state.get(f'delete_user_{user["id"]}'):
                render_delete_form(um, user)

            if st.session_state.get(f'transfer_super_admin_{user["id"]}'):
                render_super_admin_transfer_form(um, user)

            if st.session_state.get(f'delete_user_{user["id"]}'):
                render_delete_form(um, user)


def render_edit_user_form(um: UserManagement, user: dict):
    """Formular zum Bearbeiten eines Benutzers"""
    with st.form(f"edit_form_{user['id']}"):
        st.markdown("##### Benutzer bearbeiten")

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Vollständiger Name", value=user.get(
                    'full_name', ''))
            email = st.text_input("Email", value=user.get('email', ''))
            phone = st.text_input("Telefon", value=user.get('phone', ''))

        with col2:
            rank = st.selectbox(
                "Rang", options=RANKS, index=RANKS.index(
                    user['rank']) if user['rank'] in RANKS else 0)
            role = st.selectbox(
                "Rolle", options=list(
                    ROLES.keys()), format_func=lambda x: ROLES[x], index=list(
                    ROLES.keys()).index(
                    user['role']) if user['role'] in ROLES else 0)
            commission = st.number_input(
                "Provision (%)",
                min_value=0.0,
                max_value=100.0,
                value=user['commission_rate'],
                step=0.5)

        st.markdown("**Berechtigungen:**")
        perms = {}
        perm_cols = st.columns(3)
        for i, (key, label) in enumerate(DEFAULT_PERMISSIONS.items()):
            with perm_cols[i % 3]:
                perms[key] = st.checkbox(
                    label, value=user['permissions'].get(
                        key, False), key=f"perm_{
                        user['id']}_{key}")

        notes = st.text_area("Notizen", value=user.get('notes', ''))

        col_submit1, col_submit2 = st.columns(2)

        with col_submit1:
            if st.form_submit_button("Speichern", use_container_width=True):
                if um.update_user(
                    user['id'],
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    rank=rank,
                    role=role,
                    commission_rate=commission,
                    permissions=perms,
                    notes=notes
                ):
                    st.success("Benutzer aktualisiert!")
                    st.session_state[f'editing_user_{user["id"]}'] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Aktualisieren")

        with col_submit2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f'editing_user_{user["id"]}'] = False
                st.rerun()


def render_change_password_form(um: UserManagement, user: dict):
    """Formular zum Ändern des Passworts"""
    with st.form(f"pwd_form_{user['id']}"):
        st.markdown("##### Passwort ändern")

        new_password = st.text_input("Neues Passwort", type="password")
        confirm_password = st.text_input(
            "Passwort bestätigen", type="password")

        col_pwd1, col_pwd2 = st.columns(2)

        with col_pwd1:
            if st.form_submit_button(
                "Passwort ändern",
                    use_container_width=True):
                if not new_password:
                    st.error("Bitte Passwort eingeben")
                elif new_password != confirm_password:
                    st.error("Passwörter stimmen nicht überein")
                elif len(new_password) < 6:
                    st.error("Passwort muss mindestens 6 Zeichen lang sein")
                else:
                    if um.change_password(user['id'], new_password):
                        st.success("Passwort geändert!")
                        st.session_state[f'change_pwd_{user["id"]}'] = False
                        st.rerun()
                    else:
                        st.error("Fehler beim Ändern des Passworts")

        with col_pwd2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f'change_pwd_{user["id"]}'] = False
                st.rerun()


def render_promote_form(um: UserManagement, user: dict):
    """Formular zum Befördern eines Benutzers"""
    with st.form(f"promote_form_{user['id']}"):
        st.markdown("##### Benutzer befördern")

        current_rank_index = RANKS.index(
            user['rank']) if user['rank'] in RANKS else 0
        available_ranks = RANKS[current_rank_index +
                                1:] if current_rank_index < len(RANKS) - 1 else []

        if not available_ranks:
            st.warning("Benutzer hat bereits den höchsten Rang")
            if st.form_submit_button("Schließen", use_container_width=True):
                st.session_state[f'promote_user_{user["id"]}'] = False
                st.rerun()
        else:
            new_rank = st.selectbox("Neuer Rang", options=available_ranks)

            col_promo1, col_promo2 = st.columns(2)

            with col_promo1:
                if st.form_submit_button(
                        "Befördern", use_container_width=True):
                    if um.promote_user(user['id'], new_rank):
                        st.success(f"Benutzer zu {new_rank} befördert!")
                        st.session_state[f'promote_user_{user["id"]}'] = False
                        st.rerun()
                    else:
                        st.error("Fehler beim Befördern")

            with col_promo2:
                if st.form_submit_button(
                        "Abbrechen", use_container_width=True):
                    st.session_state[f'promote_user_{user["id"]}'] = False
                    st.rerun()


def render_terminate_form(um: UserManagement, user: dict):
    """Formular zum Kündigen eines Benutzers"""
    with st.form(f"term_form_{user['id']}"):
        st.markdown("##### Benutzer kündigen")
        st.warning(
            "Der Benutzer wird gekündigt und kann sich nicht mehr anmelden!")

        reason = st.text_area("Grund (optional)")

        col_term1, col_term2 = st.columns(2)

        with col_term1:
            if st.form_submit_button(
                "Kündigen",
                use_container_width=True,
                    type="primary"):
                if um.terminate_user(user['id'], reason):
                    st.success("Benutzer gekündigt!")
                    st.session_state[f'terminate_user_{user["id"]}'] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Kündigen")

        with col_term2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f'terminate_user_{user["id"]}'] = False
                st.rerun()


def render_delete_form(um: UserManagement, user: dict):
    """Formular zum Löschen eines Benutzers"""
    with st.form(f"del_form_{user['id']}"):
        st.markdown("##### Benutzer löschen")
        st.error("WARNUNG: Diese Aktion kann nicht rückgängig gemacht werden!")

        delete_type = st.radio(
            "Löschtyp",
            options=["soft", "hard"],
            format_func=lambda x: "Soft Delete (Status auf 'gelöscht')" if x == "soft" else "Hard Delete (Permanent)"
        )

        confirm = st.checkbox("Ich bestätige die Löschung")

        col_del1, col_del2 = st.columns(2)

        with col_del1:
            if st.form_submit_button(
                "Löschen",
                use_container_width=True,
                type="primary",
                    disabled=not confirm):
                if um.delete_user(
                    user['id'], hard_delete=(
                        delete_type == "hard")):
                    st.success("Benutzer gelöscht!")
                    st.session_state[f'delete_user_{user["id"]}'] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Löschen")

        with col_del2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f'delete_user_{user["id"]}'] = False
                st.rerun()


def render_create_user(um: UserManagement):
    """Formular zum Erstellen eines neuen Benutzers"""

    st.markdown("#### Neuen Benutzer erstellen")

    with st.form("create_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Benutzername *", placeholder="max.mustermann")
            password = st.text_input(
                "Passwort *",
                type="password",
                placeholder="Mindestens 6 Zeichen")
            full_name = st.text_input(
                "Vollständiger Name",
                placeholder="Max Mustermann")
            email = st.text_input("Email", placeholder="max@firma.de")

        with col2:
            phone = st.text_input("Telefon", placeholder="+49 123 456789")
            rank = st.selectbox("Rang", options=RANKS)
            role = st.selectbox(
                "Rolle",
                options=list(
                    ROLES.keys()),
                format_func=lambda x: ROLES[x])
            commission = st.number_input(
                "Provision (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5)

        st.markdown("**Berechtigungen:**")
        perms = {}
        perm_cols = st.columns(3)
        for i, (key, label) in enumerate(DEFAULT_PERMISSIONS.items()):
            with perm_cols[i % 3]:
                perms[key] = st.checkbox(label, key=f"new_perm_{key}")

        if st.form_submit_button(
            "Benutzer erstellen",
            use_container_width=True,
                type="primary"):
            if not username or not password:
                st.error("Benutzername und Passwort sind erforderlich!")
            elif len(password) < 6:
                st.error("Passwort muss mindestens 6 Zeichen lang sein!")
            else:
                user_id = um.create_user(
                    username=username,
                    password=password,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    rank=rank,
                    role=role,
                    permissions=perms,
                    commission_rate=commission
                )

                if user_id:
                    st.success(
                        f"Benutzer '{username}' erfolgreich erstellt! (ID: {user_id})")
                    st.balloons()
                else:
                    st.error(
                        "Fehler beim Erstellen - Benutzername bereits vergeben!")


def render_statistics(um: UserManagement):
    """Zeigt Benutzerstatistiken"""

    st.markdown("#### Benutzerstatistiken")

    stats = um.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gesamt", stats['total'])

    with col2:
        active_count = stats['by_status'].get('active', 0)
        st.metric("Aktiv", active_count)

    with col3:
        terminated_count = stats['by_status'].get('terminated', 0)
        st.metric("Gekündigt", terminated_count)

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**Nach Rang:**")
        if stats['by_rank']:
            df_rank = pd.DataFrame(
                list(
                    stats['by_rank'].items()),
                columns=[
                    'Rang',
                    'Anzahl'])
            st.bar_chart(df_rank.set_index('Rang'))
        else:
            st.info("Keine Daten")

    with col_chart2:
        st.markdown("**Nach Rolle:**")
        if stats['by_role']:
            df_role = pd.DataFrame(
                list(
                    stats['by_role'].items()),
                columns=[
                    'Rolle',
                    'Anzahl'])
            df_role['Rolle'] = df_role['Rolle'].map(lambda x: ROLES.get(x, x))
            st.bar_chart(df_role.set_index('Rolle'))
        else:
            st.info("Keine Daten")


def render_import_export(um: UserManagement):
    """Import/Export-Funktionen"""

    st.markdown("#### Import/Export")

    col_ie1, col_ie2 = st.columns(2)

    with col_ie1:
        st.markdown("##### Export")
        st.info("Exportiert alle Benutzer als JSON-Datei")

        export_path = st.text_input(
            "Exportpfad", value="data/users_export.json")

        if st.button("Exportieren", use_container_width=True):
            if um.export_users(export_path):
                st.success(
                    f"Benutzer erfolgreich exportiert nach: {export_path}")
            else:
                st.error("Fehler beim Exportieren")

    with col_ie2:
        st.markdown("##### Import")
        st.warning("Importiert Benutzer aus JSON-Datei")

        import_path = st.text_input(
            "Importpfad", value="data/users_export.json")
        overwrite = st.checkbox("Existierende Benutzer überschreiben")

        if st.button("Importieren", use_container_width=True):
            imported = um.import_users(import_path, overwrite=overwrite)
            if imported > 0:
                st.success(f"{imported} Benutzer erfolgreich importiert!")
            else:
                st.error("Fehler beim Importieren oder keine neuen Benutzer")


def render_super_admin_transfer_form(um: UserManagement, from_user: dict):
    """Formular für Super-Admin-Rechteübertragung"""
    with st.form(f"transfer_form_{from_user['id']}"):
        st.markdown("##### [LOCK] Super-Admin-Rechte übertragen")
        st.error(
            "[!] WARNUNG: Sie übertragen Ihre höchsten Rechte an einen anderen Benutzer!")

        st.markdown("""
        **Sicherheitshinweise:**
        - Nach der Übertragung verlieren Sie Super-Admin-Rechte
        - Der neue Super-Admin erhält vollständige Kontrolle
        - Diese Aktion kann nicht rückgängig gemacht werden
        - Der Empfänger muss die Übertragung mit eigenem Passwort bestätigen
        """)

        # Empfänger auswählen
        all_users = um.list_users(status='active')
        eligible_users = [u for u in all_users if u['id'] != from_user['id']]

        if not eligible_users:
            st.warning(
                "Keine anderen aktiven Benutzer für Übertragung verfügbar")
            if st.form_submit_button("Schließen", use_container_width=True):
                st.session_state[f'transfer_super_admin_{from_user["id"]}'] = False
                st.rerun()
            return

        user_options = {f"{u['username']} - {u.get('full_name', 'N/A')}": u['id']
                        for u in eligible_users}

        selected_user = st.selectbox(
            "Empfänger auswählen",
            options=list(user_options.keys())
        )

        st.markdown("---")
        st.markdown("**Bestätigung erforderlich:**")

        current_password = st.text_input(
            "Ihr aktuelles Passwort zur Bestätigung",
            type="password",
            help="Geben Sie Ihr Passwort ein, um die Übertragung zu autorisieren")

        confirm_text = st.text_input(
            "Geben Sie 'RECHTE ÜBERTRAGEN' ein",
            help="Tippen Sie exakt diesen Text zur finalen Bestätigung"
        )

        col_transfer1, col_transfer2 = st.columns(2)

        with col_transfer1:
            transfer_enabled = (
                current_password and
                confirm_text == "RECHTE ÜBERTRAGEN" and
                selected_user
            )

            if st.form_submit_button(
                "Rechte übertragen",
                type="primary",
                use_container_width=True,
                    disabled=not transfer_enabled):
                to_user_id = user_options[selected_user]

                # Initiiere Übertragung
                transfer_code = um.initiate_super_admin_transfer(
                    from_user['id'],
                    to_user_id,
                    current_password
                )

                if transfer_code:
                    st.success("Übertragung initiiert!")
                    st.info(f"""
                    **Transfer-Code:** `{transfer_code}`

                    Der Empfänger muss sich anmelden und diesen Code eingeben,
                    um die Super-Admin-Rechte zu erhalten.

                    Code gültig bis: Heute 23:59 Uhr
                    """)
                    st.session_state[f'transfer_super_admin_{from_user["id"]}'] = False
                    st.rerun()
                else:
                    st.error(
                        "Fehler: Falsches Passwort oder Übertragung fehlgeschlagen")

        with col_transfer2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f'transfer_super_admin_{from_user["id"]}'] = False
                st.rerun()
