"""
intro_screen.py
Zweck: Intro-Bildschirm für die Bokuk2-Anwendung mit Video/Bild-Optionen
"""
import base64
import json
from pathlib import Path

import streamlit as st


def get_image_base64(image_path):
    """Konvertiert Bild zu Base64 für HTML-Einbettung"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except BaseException:
        return None


def load_intro_settings():
    """Lädt Intro-Einstellungen aus JSON oder gibt Standardwerte zurück"""
    settings_file = Path("data/intro_settings.json")
    default_settings = {
        "enabled": True,
        "media_type": "image",  # "none", "image", "video"
        "image_path": "data/company_logos/wppv.png",
        "image_left_path": "data/company_logos/left_logo.png",  # NEU: Linkes kleines Bild
        "image_right_path": "data/company_logos/right_logo.png",  # NEU: Rechtes kleines Bild
        "show_side_images": True,  # NEU: Seitenbilder aktivieren
        "video_url": "",
        "require_login": True,  # JETZT PFLICHT
        "allow_guest": False,  # DEAKTIVIERT
        "allow_quick_start": False,  # DEAKTIVIERT
        "allow_registration": True,  # NEU: Registrierung erlauben
        "require_company_info": True,  # NEU: Firmeninfo bei Registrierung
        "title": "Ömers All in One Machine",
        "subtitle": "",
        "description": ""
    }

    try:
        if settings_file.exists():
            with open(settings_file, encoding='utf-8') as f:
                return {**default_settings, **json.load(f)}
    except BaseException:
        pass
    return default_settings


def save_intro_settings(settings):
    """Speichert Intro-Einstellungen in JSON"""
    settings_file = Path("data/intro_settings.json")
    settings_file.parent.mkdir(exist_ok=True)
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False


def render_intro_screen():
    """
    Rendert den Intro-Bildschirm mit Login/Weiter-Optionen.

    Returns:
        bool: True wenn Benutzer fortfahren möchte, False sonst
    """

    # Lade Einstellungen
    settings = load_intro_settings()

    # Prüfe ob Intro deaktiviert ist
    if not settings.get('enabled', True):
        st.session_state['intro_completed'] = True
        st.session_state['user_mode'] = 'quick_start'
        st.session_state['username'] = 'Schnellstart-Benutzer'
        return True

    # Prüfe ob bereits eingeloggt/weitergegangen
    if st.session_state.get('intro_completed', False):
        return True

    # Zentriertes Layout mit CSS - OHNE EMOJIS
    st.markdown("""
        <style>
        /* Verstecke leere Streamlit-Container im Intro */
        .intro-container .element-container:empty {
            display: none !important;
        }
        .intro-container > div[data-testid="stImage"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 auto !important;
        }
        .intro-images-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
            padding: 0 20px;
            width: 100%;
        }
        .intro-logo {
            max-width: 750px !important;
            width: 700px !important;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: float 3s ease-in-out infinite;
            position: relative;
            z-index: 10;
            margin: 0 auto;
            display: block;
        }
        .intro-logo-side {
            width: 100%;
            max-width: 100px;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            animation: float 3.5s ease-in-out infinite;
            opacity: 0.75;
            transition: all 0.3s ease;
        }
        .intro-logo-side.left {
            grid-column: 1;
            max-width: 350px;
        }
        .intro-logo-side.right {
            grid-column: 3;
            max-width: 350px;
        }
        .intro-logo-side:hover {
            opacity: 1;
            transform: scale(1.1);
        }
        @media (max-width: 468px) {
            .intro-images-container {
                justify-content: center;
                padding: 0 10px;
            }
            .intro-logo {
                max-width: 450px !important;
                width: 400px !important;
                margin: 0 auto;
            }
            .intro-title {
                font-size: 3.2rem;
                text-align: center;
                -webkit-text-stroke: 2px #00ffff;
            }
            .intro-logo-side.left {
                max-width: 230px;
            }
            .intro-logo-side.right {
                max-width: 230px;
            }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        .intro-video {
            max-width: 800px;
            width: 100%;
            margin-bottom: 2rem;
            border-radius: 15px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .intro-title {
            font-size: 4.5rem;
            font-weight: 900;
            margin-bottom: 3rem;
            text-align: center;
            color: #ffffff;
            text-stroke: 3px #00ffff;
            -webkit-text-stroke: 3px #00ffff;
            text-shadow: 
                0 0 5px #00ffff,
                0 0 10px #00ffff,
                0 0 15px #00ffff,
                0 0 20px #00ffff;
            animation: shimmer 3s ease-in-out infinite;
        }
        @keyframes shimmer {
            0% { 
                text-shadow: 
                    0 0 5px #00ffff,
                    0 0 10px #00ffff,
                    0 0 15px #00ffff,
                    0 0 20px #00ffff;
                -webkit-text-stroke: 3px #00ffff;
            }
            50% { 
                text-shadow: 
                    0 0 10px #40e0d0,
                    0 0 20px #40e0d0,
                    0 0 30px #40e0d0,
                    0 0 40px #40e0d0;
                -webkit-text-stroke: 3px #40e0d0;
            }
            100% { 
                text-shadow: 
                    0 0 5px #00ffff,
                    0 0 10px #00ffff,
                    0 0 15px #00ffff,
                    0 0 20px #00ffff;
                -webkit-text-stroke: 3px #00ffff;
            }
        }
        /* ========================================
           INTRO BUTTON EFFEKTE: DYNAMISCH (10 Stile)
           ======================================== */

        /* Intro-spezifische Button-Basis-Styles */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            font-size: 1.3rem !important;
            padding: 1rem 2.5rem !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
        }

        /* Dynamische Effekte werden aus den globalen Einstellungen geladen */
        </style>
    """, unsafe_allow_html=True)

    # ============================================================================
    # DYNAMISCHE UI-EFFEKTE FÜR INTRO-SCREEN
    # ============================================================================
    try:
        from admin_ui_effects_settings import load_ui_effects_settings
        from ui_effects_library import get_effect_css

        ui_effects_settings = load_ui_effects_settings()
        effects_enabled = ui_effects_settings.get("enabled", True)
        active_effect = ui_effects_settings.get(
            "active_effect", "shimmer_pulse")

        if effects_enabled:
            effect_css = get_effect_css(active_effect)
            st.markdown(f"""
            <style>
            /* Intro-Screen Effekte: {active_effect.upper()} */
            {effect_css}
            </style>
            """, unsafe_allow_html=True)
    except Exception:
        pass  # Fallback: Keine zusätzlichen Effekte

    # Haupt-Container
    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:
        st.markdown('<div class="intro-container">', unsafe_allow_html=True)

        # Media-Anzeige (Video oder Bild)
        media_type = settings.get('media_type', 'image')

        if media_type == 'video' and settings.get('video_url'):
            # Video einbetten
            video_url = settings['video_url']
            if 'youtube.com' in video_url or 'youtu.be' in video_url:
                # YouTube-Video
                if 'youtu.be' in video_url:
                    video_id = video_url.split('/')[-1].split('?')[0]
                else:
                    video_id = video_url.split('v=')[-1].split('&')[0]
                st.markdown(f'''
                    <iframe class="intro-video" height="400"
                        src="https://www.youtube.com/embed/{video_id}"
                        frameborder="0" allowfullscreen>
                    </iframe>
                ''', unsafe_allow_html=True)
            else:
                # Direktes Video
                st.video(video_url)

        elif media_type == 'image':
            # Prüfe ob Seitenbilder aktiviert sind
            show_side_images = settings.get('show_side_images', False)

            if show_side_images:
                # 3 Bilder mit Grid Layout: klein links - groß mitte - klein
                # rechts
                st.markdown(
                    '<div class="intro-images-container">',
                    unsafe_allow_html=True)

                # Spalte 1: Linkes kleines Bild
               # image_left_path = Path(settings.get('image_left_path', ''))
              #  if image_left_path.exists():
               #     img_left_base64 = get_image_base64(image_left_path)
               #     if img_left_base64:
                #        st.markdown(
                  #          f'<img src="data:image/png;base64,{img_left_base64}" class="intro-logo-side left" style="grid-column: 1;">',
                  #          unsafe_allow_html=True)

                # Spalte 2: Hauptbild (groß in der Mitte)
                image_path = Path(
                    settings.get(
                        'image_path',
                        'data/company_logos/default_company_logo.png'))
                if image_path.exists():
                    img_base64 = get_image_base64(image_path)
                    if img_base64:
                        st.markdown(
                            f'<img src="data:image/png;base64,{img_base64}" class="intro-logo" style="grid-column: 2;">',
                            unsafe_allow_html=True)

                # Spalte 3: Rechtes kleines Bild
              #  image_right_path = Path(settings.get('image_right_path', ''))
             #   if image_right_path.exists():
              #      img_right_base64 = get_image_base64(image_right_path)
               #     if img_right_base64:
               #         st.markdown(
                #            f'<img src="data:image/png;base64,{img_right_base64}" class="intro-logo-side right" style="grid-column: 3;">',
                #            unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Nur Hauptbild (original)
                image_path = Path(
                    settings.get(
                        'image_path',
                        'data/company_logos/default_company_logo.png'))
                if image_path.exists():
                    img_base64 = get_image_base64(image_path)
                    if img_base64:
                        st.markdown(
                            f'<img src="data:image/png;base64,{img_base64}" class="intro-logo">',
                            unsafe_allow_html=True)

        # Titel - NUR DER TITEL, KEINE BESCHREIBUNG
        st.markdown(
            f'<h1 class="intro-title">{
                settings.get(
                    "title",
                    "Ömers All in One Machine")}</h1>',
            unsafe_allow_html=True)

        st.markdown("---")

        # PFLICHT-LOGIN: Nur Login & Registrierung
        tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

        # Tab 1: Login
        with tab1:
            st.markdown("#### Anmelden")

            with st.form("login_form"):
                username = st.text_input(
                    "Benutzername", placeholder="Ihr Benutzername")
                password = st.text_input(
                    "Passwort", type="password", placeholder="Ihr Passwort")

                login_button = st.form_submit_button(
                    "Anmelden", use_container_width=True, type="primary")

                if login_button:
                    if username and password:
                        # Authentifizierung mit UserManagement-System
                        try:
                            from user_management import UserManagement
                            um = UserManagement()
                            user = um.authenticate(username, password)

                            if user:
                                st.session_state['intro_completed'] = True
                                st.session_state['user_mode'] = user['role']
                                st.session_state['user_role'] = user['role']
                                st.session_state['username'] = user['full_name'] or user['username']
                                st.session_state['user_id'] = user['id']
                                st.session_state['user_rank'] = user['rank']
                                st.session_state['user_permissions'] = user['permissions']
                                st.success(
                                    f"Willkommen, {
                                        user['full_name'] or user['username']}!")
                                st.rerun()
                            else:
                                st.error("Ungültige Anmeldedaten")
                        except ImportError:
                            # Fallback auf altes System
                            if username == "admin" and password == "admin":
                                st.session_state['intro_completed'] = True
                                st.session_state['user_mode'] = 'admin'
                                st.session_state['username'] = username
                                st.success("Erfolgreich angemeldet!")
                                st.rerun()
                            else:
                                st.error("Ungültige Anmeldedaten")
                    else:
                        st.warning("Bitte Benutzername und Passwort eingeben")

        # Tab 2: Registrierung
        with tab2:
            render_registration_form(settings)

        st.markdown("---")

        # Keyboard-Shortcut Hinweis - OHNE EMOJI
        st.caption("Tipp: Drücken Sie Enter zum Anmelden")

        # Footer - OHNE EMOJIS - OHNE EMOJIS
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; color: #ffffff; font-size: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            Ömers All in One Machine v2.0 | 2025 | Powered by Streamlit, OpenAI & LangChain
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Keyboard-Shortcut mit JavaScript
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.target.matches('input, textarea')) {
            const quickStartButton = document.querySelector('[data-testid="baseButton-primary"]');
            if (quickStartButton) {
                quickStartButton.click();
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

    return False


def render_registration_form(settings: dict):
    """Registrierungsformular mit Pflichtfeldern"""

    st.markdown("#### Neuen Benutzer registrieren")

    # Account-Typ wählen
    account_type = st.radio(
        "Kontotyp",
        options=[
            "privat",
            "firma"],
        format_func=lambda x: "Privatkunde" if x == "privat" else "Firmenkunde",
        horizontal=True)

    with st.form("registration_form"):
        st.markdown("##### Pflichtangaben")

        col1, col2 = st.columns(2)

        with col1:
            # PFLICHTFELDER
            username = st.text_input(
                "Benutzername *", placeholder="max.mustermann")
            password = st.text_input(
                "Passwort *",
                type="password",
                placeholder="Mindestens 6 Zeichen")
            password_confirm = st.text_input(
                "Passwort bestätigen *", type="password")
            full_name = st.text_input(
                "Vollständiger Name *",
                placeholder="Max Mustermann")
            email = st.text_input("E-Mail *", placeholder="max@firma.de")

        with col2:
            phone = st.text_input(
                "Telefonnummer *",
                placeholder="+49 123 456789")

            if account_type == "firma":
                company_name = st.text_input(
                    "Firmenname *", placeholder="Mustermann GmbH")
                position = st.text_input(
                    "Position im Unternehmen",
                    placeholder="Geschäftsführer")
                department = st.text_input("Abteilung", placeholder="Vertrieb")
            else:
                company_name = ""
                position = "Privatkunde"
                department = ""

        st.markdown("##### Optionale Angaben")

        col3, col4 = st.columns(2)

        with col3:
            address = st.text_area(
                "Adresse", placeholder="Musterstraße 123\n12345 Musterstadt")

        with col4:
            notes = st.text_area("Anmerkungen",
                                 placeholder="Zusätzliche Informationen...")

        # Datenschutz
        st.markdown("---")
        privacy_accepted = st.checkbox(
            "Ich akzeptiere die Datenschutzbestimmungen *")

        # Submit
        submit_button = st.form_submit_button(
            "Registrieren", use_container_width=True, type="primary")

        if submit_button:
            # Validierung
            errors = []

            if not username:
                errors.append("Benutzername ist erforderlich")
            if not password:
                errors.append("Passwort ist erforderlich")
            elif len(password) < 6:
                errors.append("Passwort muss mindestens 6 Zeichen lang sein")
            if password != password_confirm:
                errors.append("Passwörter stimmen nicht überein")
            if not full_name:
                errors.append("Vollständiger Name ist erforderlich")
            if not email:
                errors.append("E-Mail ist erforderlich")
            elif '@' not in email:
                errors.append("Ungültige E-Mail-Adresse")
            if not phone:
                errors.append("Telefonnummer ist erforderlich")
            if account_type == "firma" and not company_name:
                errors.append("Firmenname ist erforderlich")
            if not privacy_accepted:
                errors.append(
                    "Datenschutzbestimmungen müssen akzeptiert werden")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Registrierung durchführen
                try:
                    from user_management import UserManagement
                    um = UserManagement()

                    # Firma erstellen falls Firmenkunde
                    company_id = None
                    if account_type == "firma" and company_name:
                        try:
                            from database import add_company
                            company_id = add_company({
                                'name': company_name,
                                'contact_person': full_name,
                                'email': email,
                                'phone': phone,
                                'address': address
                            })
                        except BaseException:
                            pass  # Firma-Erstellung optional

                    # Benutzer erstellen
                    user_id = um.create_user(
                        username=username,
                        password=password,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        company_id=company_id,
                        rank="Mitarbeiter" if account_type == "firma" else "Privatkunde",
                        role="user",
                        permissions={
                            "view_data": True,
                            "create_offers": True})

                    if user_id:
                        # Optional: Position/Abteilung in Notizen speichern
                        if position or department or notes:
                            note_parts = []
                            if position:
                                note_parts.append(f"Position: {position}")
                            if department:
                                note_parts.append(f"Abteilung: {department}")
                            if notes:
                                note_parts.append(f"Notizen: {notes}")
                            um.update_user(
                                user_id, notes=" | ".join(note_parts))

                        st.success(
                            f"Registrierung erfolgreich! Sie können sich jetzt mit '{username}' anmelden.")
                        st.info("Bitte wechseln Sie zum 'Anmelden'-Tab.")
                    else:
                        st.error(
                            "Registrierung fehlgeschlagen - Benutzername bereits vergeben")

                except Exception as e:
                    st.error(f"Fehler bei der Registrierung: {e}")


def show_user_info():
    """Zeigt Benutzer-Info in der Sidebar - OHNE EMOJIS"""
    if st.session_state.get('intro_completed', False):
        username = st.session_state.get('username', 'Unbekannt')
        user_mode = st.session_state.get('user_mode', 'guest')

        mode_labels = {
            'admin': 'Administrator',
            'quick_start': 'Schnellstart',
            'guest': 'Gastmodus',
            'user': 'Benutzer',
            'manager': 'Manager'
        }

        label = mode_labels.get(user_mode, 'Gast')

        st.markdown("---")
        st.markdown("**Angemeldet als:**")
        st.markdown(f"`{username}`")
        st.caption(f"Modus: {label}")

        if st.button("Abmelden", use_container_width=True):
            st.session_state['intro_completed'] = False
            st.session_state.pop('username', None)
            st.session_state.pop('user_mode', None)
            st.session_state.pop('user_id', None)
            st.session_state.pop('user_rank', None)
            st.session_state.pop('user_permissions', None)
            st.rerun()
