"""
user_menu.py
Erweitertes Benutzermenü für Sidebar mit Avatar und Einstellungen
"""
import hashlib
import secrets

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
    """Rendert das erweiterte Benutzermenü in der Sidebar."""

    if not st.session_state.get('intro_completed', False):
        return

    # Avatar-Link öffnet über Query-Parameter das Modal
    params = {}
    if hasattr(st, "query_params"):
        try:
            params = dict(st.query_params)
        except Exception:
            params = {}
    else:
        try:
            params = dict(st.experimental_get_query_params())  # pragma: no cover - legacy fallback
        except Exception:
            params = {}

    if params.get("open_avatar"):
        st.session_state['show_profile_image_modal'] = True
        params.pop("open_avatar", None)
        if hasattr(st, "query_params"):
            st.query_params = params
        else:
            st.experimental_set_query_params(**params)  # pragma: no cover - legacy fallback

    # CSS für besseres Styling - Card-Stil mit ORANGE Akzenten
    st.markdown("""
    <style>
    .user-menu-container {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
        border-left: 4px solid #ff8c00;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.08);
    }
    .user-avatar {
        text-align: center;
        margin-bottom: 10px;
    }
    .user-info {
        color: #1a202c;
        text-align: center;
        font-weight: 700;
    }
    .super-admin-badge {
        background: linear-gradient(135deg, #ff8c00 0%, #ff9a1f 100%);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        color: white;
        display: inline-block;
        margin-bottom: 5px;
        box-shadow: 0 10px 10px rgba(0, 0, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # Hole Benutzer-Daten (Owner darf auch user_id == 0 sein)
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', 'Unbekannt')
    user_rank = st.session_state.get('user_rank', 'Mitarbeiter')
    user_role = st.session_state.get('user_role', 'user')
    user_permissions = st.session_state.get('user_permissions', {})
    user_status_state = st.session_state.get('user_status', 'Verfügbar')

    um = UserManagement()
    user_data = None
    if user_id is not None:
        user_data = um.get_user(user_id)

    # Fallback, wenn kein Datensatz in der DB gefunden wurde (z. B. Owner)
    if not user_data:
        user_data = {
            'id': user_id,
            'username': username,
            'full_name': username,
            'rank': user_rank,
            'role': user_role,
            'permissions': user_permissions,
            'user_status': user_status_state,
            'status': 'active',
            'is_super_admin': 1 if st.session_state.get('is_owner') else 0,
        }

    # Avatar und Basis-Info - KOMPAKT IN EINER ZEILE
    st.markdown("---")

    # Avatar URL
    avatar_url = get_avatar_url(
        email=user_data.get('email'),
        username=username,
        user_id=user_id
    )

    # Super-Admin Badge und Status
    is_super = user_data and user_data.get('is_super_admin', 0) == 1
    
    # FIX #2: Owner bekommt "General-Admin" statt "(owner)" - Owner-Check hinzugefügt
    is_owner = st.session_state.get('is_owner', False)

    # Rang Display (Punkt 2:  General Admin )
    if is_owner:
        # FIX #2: Owner zeigt ★★★★★ General-Admin ★★★★★
        rank_display = "★★★★★ General-Admin ★★★★★"
    elif is_super:
        rank_display = "<span style='font-size: 10px;'></span> General Admin <span style='font-size: 10px;'></span>"
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
        'nicht verfügbar': '',
        'Offline': ''
    }
    status_icon = status_icons.get(user_status, '🟢')

    # CSS für klickbares Profilbild - ORANGE Akzent
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
        transform: scale(1.08);
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.4) !important;
    }
    .profile-avatar-container:hover::before {
        content: 'Klicken um Profilbild zu vergrößern';
        position: absolute;
        bottom: -25px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #ff8c00 0%, #ff9a1f 100%);
        color: white;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 10px 12px rgba(0, 0, 0, 0.4);
    }
    .profile-avatar-img {
        border-radius: 50%;
        width: 80px;
        height: 80px;
        border: 4px solid #ff8c00;
        display: block;
        box-shadow: 0 10px 18px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.18);
    }
    </style>
    """, unsafe_allow_html=True)

    # Modal für Profilbild-Anzeige (oben, bevor das Hauptmenü kommt)
    if st.session_state.get('show_profile_image_modal', False):
        st.markdown("---")
        st.markdown(f"###  Profilbild von {username}")

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(avatar_url, use_container_width=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(
                " Schließen",
                use_container_width=True,
                type="secondary",
                    key="close_profile_modal"):
                st.session_state['show_profile_image_modal'] = False
                st.rerun()
        st.markdown("---")

    # Session State für Account-Menü-Zustand initialisieren (persistent)
    if 'account_menu_expanded' not in st.session_state:
        st.session_state['account_menu_expanded'] = False

    # Toggle-Button für Account-Menü (einfach und clean)
    if st.button(f"👤 {username} - Account Menü", key="toggle_account_menu", use_container_width=True):
        st.session_state['account_menu_expanded'] = not st.session_state['account_menu_expanded']
        st.rerun()
    
    # Zeige Account-Menü nur wenn expanded = True
    if st.session_state['account_menu_expanded']:
        # Benutzermenü mit zwei Spalten: Avatar + Info
        col_avatar, col_info = st.columns([1, 4])

        with col_avatar:
            # Zeige Avatar
            st.markdown(f"""
            <div style="position: relative; margin-bottom: 10px;">
                <a href="?open_avatar=1" class="profile-avatar-container" title="Profilbild vergrößern">
                    <img src="{avatar_url}" class="profile-avatar-img" alt="Profilbild">
                </a>
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            # User-Info rechts vom Avatar - Card-Stil mit schwarzer Schattierung
            st.markdown(f"""
            <div style="padding: 12px 14px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-radius: 12px; border: 2px solid rgba(200, 210, 220, 0.5); border-left: 4px solid #ff8c00; margin-top: 0px; box-shadow: 0 10px 18px rgba(0, 0, 0, 0.2), 0 3px 10px rgba(0, 0, 0, 0.14);">
                <div style="font-weight: 700; font-size: 17px; margin-bottom: 4px; margin-top: 2px; color: #1a202c;">{username}</div>
                <div style="font-size: 14px; font-weight: 600; color: #4a5568; line-height: 1.5;">{rank_display}</div>
                <div style="font-size: 14px; font-weight: 600; color: #4a5568; line-height: 1.5;">{status_icon} {user_status}</div>
            </div>
            """, unsafe_allow_html=True)

        # CSS für Tabs mit ORANGE Akzenten - transparenter Hintergrund
        st.markdown("""
        <style>
        /* Tab-Buttons mit orangenem Akzent */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-list"] button {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
            border-bottom: 3px solid transparent !important;
            border-radius: 8px 8px 0 0 !important;
            margin-right: 4px !important;
            padding: 12px 20px !important;
            font-weight: 700 !important;
            color: #1a202c !important;
            transition: all 0.3s ease !important;
        }
        .stTabs [data-baseweb="tab-list"] button:hover {
            border-bottom-color: rgba(255, 140, 0, 0.5) !important;
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            border-bottom: 3px solid #ff8c00 !important;
            color: #ff8c00 !important;
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        }
        /* Tab-Content mit Card-Stil - transparenter Hintergrund außen */
        .stTabs [data-baseweb="tab-panel"] {
            background: transparent !important;
            border-radius: 0 !important;
            border: none !important;
            padding: 12px 0 !important;
            box-shadow: none !important;
        }
        /* Expander Hintergrund transparent */
        section[data-testid="stSidebar"] .streamlit-expanderContent {
            background: transparent !important;
        }
        /* Alle Tab-Container transparent */
        section[data-testid="stSidebar"] .stTabs {
            background: transparent !important;
        }
        section[data-testid="stSidebar"] div[data-baseweb="tab"] {
            background: transparent !important;
        }
        section[data-testid="stSidebar"] div[role="tablist"] {
            background: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs für Profil, Einstellungen, Info
        tab1, tab2, tab3 = st.tabs(["📋 Profil", "⚙️ Einstellungen", "ℹ️ Info"])
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

    st.markdown("""
    <div style="padding: 12px 16px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-left: 4px solid #ff8c00; border-radius: 10px; margin-bottom: 16px; box-shadow: 0 10px 14px rgba(0, 0, 0, 0.2);">
        <h4 style="margin: 0; color: #1a202c; font-weight: 700;">Mein Profil</h4>
    </div>
    """, unsafe_allow_html=True)

    # Rolle für General Admin (Punkt 1)
    if is_super:
        role_display = " General Admin "
    else:
        role_display = user_data.get('role', 'N/A')

    # FIX #3: Rang mit ★★★★★ für Owner (unten bei owner ersetzen mit 5 sternen)
    is_owner = st.session_state.get('is_owner', False)
    if is_owner:
        rank_display = "★★★★★"  # FIX #3: 5 Sterne für Owner
    elif is_super:
        rank_display = "Level ∞"
    else:
        rank_display = user_data.get('rank', 'N/A')

    # Ausklappbarer Bereich für Profilinformationen
    with st.expander("📋 Profilinformationen anzeigen", expanded=False):
        # Anzeige der Profil-Daten im Card-Stil mit schwarzer Schattierung
        st.markdown(f"""
        <div style="padding: 16px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-radius: 12px; border-left: 4px solid #ff8c00; box-shadow: 0 10px 18px rgba(0, 0, 0, 0.2), 0 10px 10px rgba(0, 0, 0, 0.14); font-size: 14px; line-height: 2;">
            <div><strong style="color: #1a202c;">ID:</strong> <strong style="color: #666;">{user_data.get('id', 'N/A')}</strong></div>
            <div><strong style="color: #1a202c;">Benutzername:</strong> <strong style="color: #666;">{user_data.get('username', 'N/A')}</strong></div>
            <div><strong style="color: #1a202c;">Name:</strong> <strong style="color: #666;">{user_data.get('full_name', 'N/A')}</strong></div>
            <div><strong style="color: #1a202c;">Rang:</strong> <strong style="color: #666;">{rank_display}</strong></div>
            <div><strong style="color: #1a202c;">Rolle:</strong> <strong style="color: #666;">{role_display}</strong></div>
            <div><strong style="color: #1a202c;">Status:</strong> <strong style="color: #666;">{user_data.get('status', 'N/A')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Kontaktdaten im Card-Stil mit schwarzer Schattierung
        st.markdown("**Kontakt:**")
        st.markdown(f"""
        <div style="padding: 14px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-radius: 12px; border-left: 4px solid #ff8c00; box-shadow: 0 10px 18px rgba(0, 0, 0, 0.2), 0 10px 10px rgba(0, 0, 0, 0.14); font-size: 14px; line-height: 1.8; margin-top: 8px;">
            <div><strong style="color: #1a202c;">Email:</strong> <strong style="color: #666;">{user_data.get('email', 'Nicht angegeben')}</strong></div>
            <div><strong style="color: #1a202c;">Telefon:</strong> <strong style="color: #666;">{user_data.get('phone', 'Nicht angegeben')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        # Über mich Bereich
        about_me = user_data.get('about_me', '')
        if about_me:
            st.markdown("---")
            st.markdown("**Über mich:**")
            st.info(about_me)

    # Profil bearbeiten
    st.markdown("---")
    if st.button(
        " Profil bearbeiten",
        use_container_width=True,
            type="primary"):
        st.session_state['show_profile_editor'] = True
        st.rerun()


def render_settings_tab(um: UserManagement, user_data: dict):
    """Einstellungen-Tab"""
    if not user_data:
        st.warning("Keine Benutzerdaten verfügbar")
        return

    st.markdown("""
    <div style="padding: 12px 16px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-left: 4px solid #ff8c00; border-radius: 10px; margin-bottom: 16px; box-shadow: 0 10px 14px rgba(0, 0, 0, 0.2);">
        <h4 style="margin: 0; color: #1a202c; font-weight: 700;">Einstellungen</h4>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
    <div style="padding: 12px 16px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-left: 4px solid #ff8c00; border-radius: 10px; margin-bottom: 16px; box-shadow: 0 10px 14px rgba(0, 0, 0, 0.2);">
        <h4 style="margin: 0; color: #1a202c; font-weight: 700;">Account-Informationen</h4>
    </div>
    """, unsafe_allow_html=True)

    # Account-Details (robust gegen fehlende Werte)
    created_at = user_data.get('created_at')
    updated_at = user_data.get('updated_at')
    last_login = user_data.get('last_login')

    def _fmt_date(val: str, default: str = 'N/A') -> str:
        return str(val)[:10] if val else default

    st.markdown(f"**Erstellt am:** {_fmt_date(created_at)}")
    st.markdown(f"**Letztes Update:** {_fmt_date(updated_at)}")

    if last_login:
        st.markdown(f"**Letzter Login:** {str(last_login)[:19]}")
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
        status_emoji = "aktiv" if status == 'active' else ""
        st.metric("Status", status_emoji)

    # Berechtigungen
    st.markdown("---")
    st.markdown("""
    <div style="padding: 12px 16px; background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%); border-left: 4px solid #ff8c00; border-radius: 10px; margin-bottom: 16px; box-shadow: 0 10px 14px rgba(0, 0, 0, 0.2);">
        <h4 style="margin: 0; color: #1a202c; font-weight: 700;">Berechtigungen</h4>
    </div>
    """, unsafe_allow_html=True)

    is_super = user_data.get('is_super_admin', 0) == 1
    permissions = user_data.get('permissions', {})

    if is_super or permissions.get('all') or permissions.get('super_admin'):
        st.success("Alle Berechtigungen (General Admin)")

        # Untergruppen mit Expander
        with st.expander("**Hauptfunktionen**", expanded=False):
            for perm in [
                "Bedarfsanalyse",
                "Solar Kalkulation",
                "Wärmepumpe",
                    "Wirtschaftlichkeit"]:
                st.markdown(f"{perm}")

        with st.expander("**Business**", expanded=False):
            for perm in ["CRM", "PDF Generator"]:
                st.markdown(f"{perm}")

        with st.expander("**Administration**", expanded=False):
            for perm in [
                "Administration",
                "Benutzerverwaltung",
                "Rangverwaltung",
                "Berechtigungsverwaltung",
                    "Provisionsverwaltung"]:
                st.markdown(f"{perm}")

        with st.expander("**System**", expanded=False):
            for perm in [
                "Unternehmensverwaltung",
                "Datenbankzugriff",
                "Einstellungen",
                    "Systemkonfiguration"]:
                st.markdown(f"{perm}")
    else:
        perm_list = [k for k, v in permissions.items() if v]
        if perm_list:
            for perm in perm_list:
                st.markdown(f"{perm}")
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

    # Globale CSS-Styles für den gesamten Profil-Editor
    st.markdown("""
    <style>
    /* TABS: Schwarzen Hintergrund entfernen */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid rgba(0, 0, 0, 0.1) !important;
        gap: 10px !important;
    }
    
    /* Tab-Buttons mit orangen Akzenten */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #333333 !important;
        font-weight: 500 !important;
        padding: 12px 24px !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        background-color: rgba(255, 140, 0, 0.1) !important;
        color: #ff8c00 !important;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(255, 140, 0, 0.15) !important;
        color: #ff8c00 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #ff8c00 !important;
    }
    
    /* BUTTONS: Alle Primary Buttons orange */
    button[kind="primary"],
    [data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #ff8c00 0%, #ff6600 100%) !important;
        color: #000000 !important;
        border: 2px solid #ff8c00 !important;
        font-weight: 600 !important;
        box-shadow: 0 10px 12px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ff9900 0%, #ff7700 100%) !important;
        box-shadow: 0 10px 18px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 140, 0, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* EINGABEFELDER: Schattierungen */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] > div > div {
        box-shadow: 0 10px 8px rgba(0, 0, 0, 0.15), inset 0 10px 10px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        background-color: #ffffff !important;
    }
    
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3), inset 0 10px 10px rgba(0, 0, 0, 0.1) !important;
        border-color: #ff8c00 !important;
        outline: none !important;
    }
    
    /* Selectbox Schattierung */
    [data-testid="stSelectbox"] > div > div:hover {
        box-shadow: 0 10px 12px rgba(255, 140, 0, 0.2), inset 0 10px 10px rgba(0, 0, 0, 0.1) !important;
        border-color: #ff8c00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    if user_id is None:
        user_id = 0  # Owner/guest fallback

    um = UserManagement()
    user_data = um.get_user(user_id) if user_id else None

    # Fallback, wenn kein Eintrag in der DB existiert (z. B. Owner)
    if not user_data:
        user_data = {
            'id': user_id,
            'username': st.session_state.get('username', 'Unbekannt'),
            'full_name': st.session_state.get('username', 'Unbekannt'),
            'email': st.session_state.get('email', ''),
            'phone': '',
            'phone_extension': '',
            'user_status': st.session_state.get('user_status', 'Verfügbar'),
            'about_me': '',
            'permissions': st.session_state.get('user_permissions', {}),
            'is_super_admin': 1 if st.session_state.get('is_owner') else 0,
        }
        can_save_profile = False
    else:
        can_save_profile = True

    def ensure_persisted_user(full_name_value: str = None,
                              email_value: str = None,
                              phone_mobile_value: str = None) -> bool:
        """Stellt sicher, dass ein DB-Datensatz existiert (Owner-Fallbacks)."""
        nonlocal user_id, user_data, can_save_profile

        if can_save_profile and user_id:
            return True

        username = (user_data.get('username') or 'owner').strip() or 'owner'

        # Falls der Benutzer bereits existiert, reuse statt IntegrityError zu triggern
        existing_user = um.get_user_by_username(username)
        if existing_user:
            user_id = existing_user['id']
            user_data.update(existing_user)
            st.session_state['user_id'] = user_id
            can_save_profile = True
            return True

        temp_password = secrets.token_hex(8)
        created_user_id = um.create_user(
            username=username,
            password=temp_password,
            full_name=full_name_value or user_data.get('full_name', 'Owner'),
            email=email_value or user_data.get('email', ''),
            phone=phone_mobile_value or user_data.get('phone', ''),
            rank=user_data.get('rank', 'Owner'),
            role=user_data.get('role', 'owner'),
            permissions=user_data.get('permissions', {}),
            commission_rate=0.0
        )

        if created_user_id:
            user_id = created_user_id
            user_data['id'] = created_user_id
            st.session_state['user_id'] = created_user_id
            can_save_profile = True
            return True

        st.error("Profil konnte nicht angelegt werden.")
        return False

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
                    " Speichern",
                    use_container_width=True,
                        type="primary"):

                    # Sicherstellen, dass ein persistenter Datensatz existiert
                    if not ensure_persisted_user(full_name, email, phone_mobile):
                        st.stop()

                    if um.update_user(
                        user_id,
                        full_name=full_name,
                        email=email,
                        phone_mobile=phone_mobile,
                        phone_extension=phone_extension,
                        user_status=user_status,
                        about_me=about_me
                    ):
                        st.success("Profil aktualisiert!")
                        st.session_state['show_profile_editor'] = False
                        st.rerun()
                    else:
                        st.error("Fehler beim Speichern")

            with col_cancel:
                if st.form_submit_button(
                        "Abbrechen", use_container_width=True):
                    st.session_state['show_profile_editor'] = False
                    st.rerun()

    # Tab 2: Passwort ändern (Punkt 1)
    with tab2:
        st.markdown("###  Passwort ändern")

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
                " Passwort ändern",
                use_container_width=True,
                    type="primary"):
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
                        import base64

                        if not ensure_persisted_user(
                                user_data.get('full_name'),
                                user_data.get('email'),
                                user_data.get('phone')):
                            st.stop()

                        bytes_data = uploaded_file.getvalue()
                        base64_image = base64.b64encode(bytes_data).decode()

                        # Update user mit Profilbild
                        if um.update_user(user_id, profile_image=base64_image):
                            st.success("Profilbild erfolgreich hochgeladen!")
                            st.rerun()
                        else:
                            st.error("Fehler beim Hochladen")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}")

            st.markdown("---")
            st.info(
                "Tipp: Verwenden Sie ein quadratisches Bild für beste Ergebnisse")

    # Zurück-Button unten
    st.markdown("---")
    if st.button(" Zurück zum Profil", use_container_width=True):
        st.session_state['show_profile_editor'] = False
        st.rerun()
