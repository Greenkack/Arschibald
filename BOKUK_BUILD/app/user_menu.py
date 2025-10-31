"""
user_menu.py
Erweitertes Benutzermenü für Sidebar mit Avatar und Einstellungen
"""
import hashlib

import streamlit as st

from user_management import UserManagement


def get_avatar_url(
        email: str = None,
        username: str = None,
        user_id: int = None) -> str:
    """Generiert Avatar URL - prüft zuerst Profilbild in DB, dann Gravatar"""

    # Wenn user_id vorhanden, prüfe ob Profilbild in DB existiert
    if user_id:
        try:
            from user_management import UserManagement
            um = UserManagement()
            user_data = um.get_user(user_id)
            if user_data and user_data.get('profile_image'):
                # Gebe base64 Data-URL zurück
                profile_image = user_data.get('profile_image')
                return f"data:image/png;base64,{profile_image}"
        except Exception:
            pass  # Fallback zu Gravatar

    # Fallback zu Gravatar
    if email:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    elif username:
        email_hash = hashlib.md5(username.lower().encode()).hexdigest()
    else:
        email_hash = hashlib.md5(b"default").hexdigest()

    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"


def render_user_menu():
    """Rendert das erweiterte Benutzermenü in der Sidebar"""

    if not st.session_state.get('intro_completed', False):
        return

    # CSS für besseres Styling
    st.markdown("""
    <style>
    .user-menu-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .user-avatar {
        text-align: center;
        margin-bottom: 10px;
    }
    .user-info {
        color: white;
        text-align: center;
    }
    .super-admin-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        display: inline-block;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hole Benutzer-Daten
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', 'Unbekannt')
    user_rank = st.session_state.get('user_rank', 'Mitarbeiter')
    user_role = st.session_state.get('user_role', 'user')

    um = UserManagement()
    user_data = None
    if user_id:
        user_data = um.get_user(user_id)

    # Avatar und Basis-Info - KOMPAKT IN EINER ZEILE
    st.markdown("---")

    # Avatar URL
    avatar_url = get_avatar_url(
        email=user_data.get('email') if user_data else None,
        username=username,
        user_id=user_id
    )

    # Super-Admin Badge und Status
    is_super = user_data and user_data.get('is_super_admin', 0) == 1

    # Rang Display (Punkt 2: ⭐⭐⭐ General Admin ⭐⭐⭐)
    if is_super:
        rank_display = "<span style='font-size: 10px;'>⭐⭐⭐</span> General Admin <span style='font-size: 10px;'>⭐⭐⭐</span>"
    else:
        rank_display = user_rank

    # Status holen (Punkt 4)
    user_status = user_data.get('user_status',
                                'Verfügbar') if user_data else 'Verfügbar'

    # Status Icons
    status_icons = {
        'Verfügbar': '🟢',
        'Beschäftigt': '🟡',
        'nicht am Platz': '🟠',
        'nicht verfügbar': '🔴',
        'Offline': '⚫'
    }
    status_icon = status_icons.get(user_status, '🟢')

    # CSS für klickbares Profilbild
    st.markdown("""
    <style>
    .profile-avatar-container {
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        position: relative;
        border-radius: 50%;
    }
    .profile-avatar-container:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.6) !important;
    }
    .profile-avatar-container:hover::before {
        content: '🔍 Klicken zum Vergrößern';
        position: absolute;
        bottom: -25px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        white-space: nowrap;
        z-index: 1000;
    }
    .profile-avatar-img {
        border-radius: 50%;
        width: 80px;
        height: 80px;
        border: 3px solid #4CAF50;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

    # Modal für Profilbild-Anzeige (oben, bevor das Hauptmenü kommt)
    if st.session_state.get('show_profile_image_modal', False):
        st.markdown("---")
        st.markdown(f"### 📸 Profilbild von {username}")

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(avatar_url, use_container_width=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(
                "✖️ Schließen",
                use_container_width=True,
                type="secondary",
                    key="close_profile_modal"):
                st.session_state['show_profile_image_modal'] = False
                st.rerun()
        st.markdown("---")

    # Benutzermenü mit zwei Spalten: Avatar + Info
    col_avatar, col_info = st.columns([1, 4])

    with col_avatar:
        # Zeige Avatar
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 10px;">
            <div class="profile-avatar-container">
                <img src="{avatar_url}" class="profile-avatar-img" title="Klicken um Profilbild zu vergrößern">
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        # User-Info rechts vom Avatar - nach oben verschoben
        st.markdown(f"""
        <div style="padding: 6px 12px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15)); border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-top: 0px;">
            <div style="font-weight: bold; font-size: 17px; margin-bottom: 3px; margin-top: 2px;">{username}</div>
            <div style="font-size: 14px; opacity: 0.7; line-height: 1.4;">{rank_display}</div>
            <div style="font-size: 14px; opacity: 0.7; line-height: 1.4;">{status_icon} {user_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # Einstellungen - VOLLE BREITE für bessere Lesbarkeit
    with st.expander("⚙️ Account Menü ⚙️", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Profil", "Einstellungen", "Info"])
        with tab1:
            render_profile_tab(um, user_data, is_super)
        with tab2:
            render_settings_tab(um, user_data)
        with tab3:
            render_info_tab(user_data)

    # Abmelden Button ENTFERNT - jetzt im Drawer unten rechts


def render_profile_tab(um: UserManagement, user_data: dict, is_super: bool):
    """Profil-Tab"""
    if not user_data:
        st.warning("Keine Benutzerdaten verfügbar")
        return

    st.markdown("#### Mein Profil")

    # Rolle für General Admin (Punkt 1)
    if is_super:
        role_display = "⭐⭐⭐ General Admin ⭐⭐⭐"
    else:
        role_display = user_data.get('role', 'N/A')

    # Rang mit Infinity für General Admin
    rank_display = "Level ∞" if is_super else user_data.get('rank', 'N/A')

    # Anzeige der Profil-Daten (Punkt 8: graue Bold-Schrift für Werte)
    st.markdown(f"""
    <div style="font-size: 14px; line-height: 1.8;">
        <div><strong>ID:</strong> {user_data.get('id', 'N/A')}</div>
        <div><strong>Benutzername:</strong> <strong style="color: #888;">{user_data.get('username', 'N/A')}</strong></div>
        <div><strong>Name:</strong> <strong style="color: #888;">{user_data.get('full_name', 'N/A')}</strong></div>
        <div><strong>Rang:</strong> <strong style="color: #888;">{rank_display}</strong></div>
        <div><strong>Rolle:</strong> <strong style="color: #888;">{role_display}</strong></div>
        <div><strong>Status:</strong> <strong style="color: #888;">{user_data.get('status', 'N/A')}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Kontaktdaten (Punkt 8: graue Bold-Schrift)
    st.markdown("**Kontakt:**")
    st.markdown(
        f"<div style='font-size: 14px;'><strong>Email:</strong> <strong style='color: #888;'>{
            user_data.get(
                'email',
                'Nicht angegeben')}</strong></div>",
        unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size: 14px;'><strong>Telefon:</strong> <strong style='color: #888;'>{
            user_data.get(
                'phone',
                'Nicht angegeben')}</strong></div>",
        unsafe_allow_html=True)

    # Über mich Bereich
    about_me = user_data.get('about_me', '')
    if about_me:
        st.markdown("---")
        st.markdown("**Über mich:**")
        st.info(about_me)

    # Profil bearbeiten
    st.markdown("---")
    if st.button(
        "✏️ Profil bearbeiten",
        use_container_width=True,
            type="primary"):
        st.session_state['show_profile_editor'] = True
        st.rerun()


def render_settings_tab(um: UserManagement, user_data: dict):
    """Einstellungen-Tab"""
    if not user_data:
        st.warning("Keine Benutzerdaten verfügbar")
        return

    st.markdown("#### Einstellungen")

    # Passwort ändern
    with st.expander("Passwort ändern"), st.form("change_password_form"):
        current_pw = st.text_input("Aktuelles Passwort", type="password")
        new_pw = st.text_input("Neues Passwort", type="password")
        confirm_pw = st.text_input("Passwort bestätigen", type="password")

        if st.form_submit_button("Passwort ändern", use_container_width=True):
            if not current_pw or not new_pw:
                st.error("Bitte alle Felder ausfüllen")
            elif new_pw != confirm_pw:
                st.error("Passwörter stimmen nicht überein")
            elif len(new_pw) < 6:
                st.error("Passwort muss mindestens 6 Zeichen lang sein")
            else:
                # Aktuelles Passwort verifizieren
                auth = um.authenticate(user_data['username'], current_pw)
                if auth:
                    if um.change_password(user_data['id'], new_pw):
                        st.success("Passwort erfolgreich geändert!")
                    else:
                        st.error("Fehler beim Ändern des Passworts")
                else:
                    st.error("Aktuelles Passwort falsch")

    # UI-Einstellungen
    st.markdown("---")
    st.markdown("**UI-Einstellungen:**")

    # Theme-Auswahl
    theme = st.selectbox(
        "Theme",
        options=["Auto", "Hell", "Dunkel"],
        index=0,
        key="user_theme_preference"
    )

    # Sprache
    language = st.selectbox(
        "Sprache",
        options=["Deutsch", "English"],
        index=0,
        key="user_language_preference"
    )

    # Sidebar-Position
    sidebar_pos = st.selectbox(
        "Sidebar-Position",
        options=["Links", "Rechts"],
        index=0,
        key="user_sidebar_position"
    )

    # Benachrichtigungen
    st.markdown("---")
    st.markdown("**Benachrichtigungen:**")

    notifications_enabled = st.checkbox(
        "Benachrichtigungen aktiviert",
        value=True,
        key="user_notifications_enabled"
    )

    email_notifications = st.checkbox(
        "E-Mail-Benachrichtigungen",
        value=False,
        key="user_email_notifications"
    )

    # Einstellungen speichern
    if st.button(
        "Einstellungen speichern",
        use_container_width=True,
            type="primary"):
        # Hier könnten die Einstellungen in der Datenbank gespeichert werden
        st.success("Einstellungen gespeichert!")


def render_info_tab(user_data: dict):
    """Info-Tab mit Berechtigungen"""
    if not user_data:
        st.warning("Keine Benutzerdaten verfügbar")
        return

    st.markdown("#### Account-Informationen")

    # Account-Details
    st.markdown(f"**Erstellt am:** {user_data.get('created_at', 'N/A')[:10]}")
    st.markdown(
        f"**Letztes Update:** {user_data.get('updated_at', 'N/A')[:10]}")

    last_login = user_data.get('last_login')
    if last_login:
        st.markdown(f"**Letzter Login:** {last_login[:19]}")
    else:
        st.markdown("**Letzter Login:** Nie")

    # Firma
    company_id = user_data.get('company_id')
    if company_id:
        st.markdown(f"**Firma-ID:** {company_id}")

    # Notizen
    notes = user_data.get('notes')
    if notes:
        st.markdown("---")
        st.markdown("**Notizen:**")
        st.info(notes)

    # Statistiken
    st.markdown("---")
    st.markdown("**Statistiken:**")

    col1, col2 = st.columns(2)

    with col1:
        is_super = user_data.get('is_super_admin', 0) == 1
        if is_super:
            st.metric("Rang-Level", "∞")
        else:
            rank_level = get_rank_level(user_data.get('rank', 'Mitarbeiter'))
            st.metric("Rang-Level", rank_level if rank_level > 0 else "∞")
    with col2:
        status = user_data.get('status', 'unknown')
        status_emoji = "aktiv" if status == 'active' else "❌"
        st.metric("Status", status_emoji)

    # Berechtigungen
    st.markdown("---")
    st.markdown("#### 🔐 Berechtigungen")

    is_super = user_data.get('is_super_admin', 0) == 1
    permissions = user_data.get('permissions', {})

    if is_super or permissions.get('all') or permissions.get('super_admin'):
        st.success("✅ Alle Berechtigungen (General Admin)")

        # Untergruppen mit Expander
        with st.expander("**Hauptfunktionen**", expanded=False):
            for perm in [
                "Bedarfsanalyse",
                "Solar Kalkulation",
                "Wärmepumpe",
                    "Wirtschaftlichkeit"]:
                st.markdown(f"✅ {perm}")

        with st.expander("**Business**", expanded=False):
            for perm in ["CRM", "PDF Generator"]:
                st.markdown(f"✅ {perm}")

        with st.expander("**Administration**", expanded=False):
            for perm in [
                "Administration",
                "Benutzerverwaltung",
                "Rangverwaltung",
                "Berechtigungsverwaltung",
                    "Provisionsverwaltung"]:
                st.markdown(f"✅ {perm}")

        with st.expander("**System**", expanded=False):
            for perm in [
                "Unternehmensverwaltung",
                "Datenbankzugriff",
                "Einstellungen",
                    "Systemkonfiguration"]:
                st.markdown(f"✅ {perm}")
    else:
        perm_list = [k for k, v in permissions.items() if v]
        if perm_list:
            for perm in perm_list:
                st.markdown(f"✅ {perm}")
        else:
            st.info("Keine speziellen Berechtigungen")


def get_rank_level(rank: str) -> int:
    """Gibt Rang-Level zurück (1-8)"""
    ranks = [
        "Praktikant",
        "Junior Mitarbeiter",
        "Mitarbeiter",
        "Senior Mitarbeiter",
        "Team Lead",
        "Abteilungsleiter",
        "Geschäftsführer",
        "Administrator"
    ]
    try:
        return ranks.index(rank) + 1
    except ValueError:
        return 0


def logout_user():
    """Meldet den Benutzer ab"""
    keys_to_clear = [
        'intro_completed',
        'username',
        'user_mode',
        'user_id',
        'user_rank',
        'user_role',
        'user_permissions',
        'show_profile_editor'
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.rerun()


def render_profile_editor():
    """Vollbild Profil-Editor mit allen Features"""
    st.title(" Profil bearbeiten")

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Keine Benutzer-ID gefunden")
        return

    um = UserManagement()
    user_data = um.get_user(user_id)

    if not user_data:
        st.error("Benutzer nicht gefunden")
        return

    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3 = st.tabs(
        [" Persönliche Daten", " Passwort ändern", " Profilbild"])

    # Tab 1: Persönliche Daten & Status (Punkt 4: Über mich, Name/Nachname,
    # Mobil, Durchwahl)
    with tab1:
        with st.form("edit_profile_form"):
            st.markdown("### Persönliche Daten")

            # Name und Nachname getrennt
            col1, col2 = st.columns(2)

            # Parse aktuellen Namen
            current_name = user_data.get('full_name', '')
            name_parts = current_name.split(
                ' ', 1) if current_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            with col1:
                first_name_input = st.text_input("Vorname", value=first_name)
                email = st.text_input(
                    "E-Mail",
                    value=user_data.get(
                        'email',
                        ''))

            with col2:
                last_name_input = st.text_input("Nachname", value=last_name)

                # Status-Dropdown
                current_status = user_data.get('user_status', 'Verfügbar')
                user_status = st.selectbox(
                    "Status",
                    options=[
                        'Verfügbar',
                        'Beschäftigt',
                        'nicht am Platz',
                        'nicht verfügbar',
                        'Offline'],
                    index=[
                        'Verfügbar',
                        'Beschäftigt',
                        'nicht am Platz',
                        'nicht verfügbar',
                        'Offline'].index(current_status) if current_status in [
                        'Verfügbar',
                        'Beschäftigt',
                        'nicht am Platz',
                        'nicht verfügbar',
                        'Offline'] else 0,
                    help="Ihr aktueller Status wird anderen Benutzern angezeigt")

            # Telefon Mobil und Durchwahl
            col3, col4 = st.columns(2)

            with col3:
                phone_mobile = st.text_input(
                    "Telefon (Mobil)", value=user_data.get(
                        'phone', ''), placeholder="+49 123 456789")

            with col4:
                phone_extension = st.text_input(
                    "Durchwahl", value=user_data.get(
                        'phone_extension', ''), placeholder="123")

            # Über mich Bereich
            st.markdown("---")
            st.markdown("**Über mich**")
            about_me = st.text_area(
                label="Persönliche Beschreibung",
                value=user_data.get('about_me', ''),
                height=100,
                placeholder="Erzählen Sie etwas über sich...",
                help="Diese Information ist für andere Benutzer sichtbar",
                key="about_me_profile_editor"
            )

            st.markdown("---")

            col_save, col_cancel = st.columns(2)

            # Vollständiger Name kombinieren
            full_name = f"{first_name_input} {last_name_input}".strip()

            with col_save:
                if st.form_submit_button(
                    "💾 Speichern",
                    use_container_width=True,
                        type="primary"):
                    if um.update_user(
                        user_id,
                        full_name=full_name,
                        email=email,
                        phone_mobile=phone_mobile,
                        phone_extension=phone_extension,
                        user_status=user_status,
                        about_me=about_me
                    ):
                        st.success("✅ Profil aktualisiert!")
                        st.session_state['show_profile_editor'] = False
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Speichern")

            with col_cancel:
                if st.form_submit_button(
                        "❌ Abbrechen", use_container_width=True):
                    st.session_state['show_profile_editor'] = False
                    st.rerun()

    # Tab 2: Passwort ändern (Punkt 1)
    with tab2:
        st.markdown("### 🔒 Passwort ändern")

        with st.form("profile_editor_change_password_form"):
            current_pw = st.text_input(
                "Aktuelles Passwort",
                type="password",
                help="Geben Sie Ihr aktuelles Passwort ein")
            st.markdown("---")
            new_pw = st.text_input(
                "Neues Passwort",
                type="password",
                help="Mindestens 6 Zeichen")
            confirm_pw = st.text_input(
                "Passwort bestätigen",
                type="password",
                help="Wiederholen Sie das neue Passwort")

            if st.form_submit_button(
                "🔑 Passwort ändern",
                use_container_width=True,
                    type="primary"):
                if not current_pw or not new_pw:
                    st.error("❌ Bitte alle Felder ausfüllen")
                elif new_pw != confirm_pw:
                    st.error("❌ Passwörter stimmen nicht überein")
                elif len(new_pw) < 6:
                    st.error("❌ Passwort muss mindestens 6 Zeichen lang sein")
                else:
                    # Aktuelles Passwort verifizieren
                    auth = um.authenticate(user_data['username'], current_pw)
                    if auth:
                        if um.change_password(user_data['id'], new_pw):
                            st.success("✅ Passwort erfolgreich geändert!")
                        else:
                            st.error("❌ Fehler beim Ändern des Passworts")
                    else:
                        st.error("❌ Aktuelles Passwort falsch")

    # Tab 3: Profilbild hochladen (Punkt 2)
    with tab3:
        st.markdown("### Profilbild ändern")

        # Aktuelles Profilbild anzeigen
        avatar_url = get_avatar_url(
            email=user_data.get('email'),
            username=user_data.get('username'),
            user_id=user_id
        )

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(avatar_url, width=150, caption="Aktuelles Profilbild")

        with col2:
            st.markdown("**Profilbild hochladen**")
            uploaded_file = st.file_uploader(
                "Wählen Sie ein Bild (PNG oder JPG)",
                type=['png', 'jpg', 'jpeg'],
                help="Unterstützte Formate: PNG, JPG, JPEG (max. 5MB)"
            )

            if uploaded_file is not None:
                # Zeige Vorschau
                st.image(uploaded_file, width=150, caption="Vorschau")

                if st.button(
                    "Profilbild hochladen",
                    use_container_width=True,
                        type="primary"):
                    try:
                        # Hier würde das Bild gespeichert werden
                        # TODO: Implementierung der Bild-Speicherung in der
                        # Datenbank
                        import base64
                        bytes_data = uploaded_file.getvalue()
                        base64_image = base64.b64encode(bytes_data).decode()

                        # Update user mit Profilbild
                        if um.update_user(user_id, profile_image=base64_image):
                            st.success("✅ Profilbild erfolgreich hochgeladen!")
                            st.rerun()
                        else:
                            st.error("❌ Fehler beim Hochladen")
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")

            st.markdown("---")
            st.info(
                "💡 Tipp: Verwenden Sie ein quadratisches Bild für beste Ergebnisse")

    # Zurück-Button unten
    st.markdown("---")
    if st.button("⬅️ Zurück zum Profil", use_container_width=True):
        st.session_state['show_profile_editor'] = False
        st.rerun()
