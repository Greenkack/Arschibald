"""
admin_intro_settings_ui.py
Zweck: Admin-UI für Intro-Bildschirm-Einstellungen
"""
from pathlib import Path

import streamlit as st

from intro_screen import load_intro_settings, save_intro_settings


def render_intro_settings_tab():
    """Rendert den Admin-Tab für Intro-Einstellungen"""

    st.markdown("### 🎨 Intro-Bildschirm Einstellungen")
    st.markdown(
        "Konfigurieren Sie den Willkommensbildschirm, der beim Start der Anwendung angezeigt wird.")

    # Lade aktuelle Einstellungen
    settings = load_intro_settings()

    # Session State für temporäre Pfade initialisieren
    if 'temp_image_path' not in st.session_state:
        st.session_state.temp_image_path = settings.get(
            'image_path', 'data/company_logos/default_company_logo.png')
    if 'temp_image_left_path' not in st.session_state:
        st.session_state.temp_image_left_path = settings.get(
            'image_left_path', 'data/company_logos/left_logo.png')
    if 'temp_image_right_path' not in st.session_state:
        st.session_state.temp_image_right_path = settings.get(
            'image_right_path', 'data/company_logos/right_logo.png')

    with st.form("intro_settings_form"):
        st.markdown("#### Grundeinstellungen")

        col1, col2 = st.columns(2)

        with col1:
            enabled = st.checkbox(
                "Intro-Bildschirm aktivieren",
                value=settings.get('enabled', True),
                help="Wenn deaktiviert, wird die Anwendung direkt gestartet"
            )

        with col2:
            require_login = st.checkbox(
                "Login erzwingen (EMPFOHLEN)",
                value=settings.get('require_login', True),
                help="Benutzer müssen sich anmelden - Schnellstart deaktiviert"
            )

        st.markdown("---")
        st.markdown("#### Registrierungs-Einstellungen")

        col3, col4 = st.columns(2)

        with col3:
            allow_registration = st.checkbox(
                "Registrierung erlauben",
                value=settings.get('allow_registration', True),
                help="Neue Benutzer können sich selbst registrieren"
            )

        with col4:
            require_company_info = st.checkbox(
                "Firmeninfo bei Registrierung",
                value=settings.get('require_company_info', True),
                help="Benutzer müssen Kontotyp wählen (Privat/Firma)"
            )

        st.markdown("---")
        st.markdown("#### Legacy-Zugangsoptionen (Nicht empfohlen)")

        col5, col6 = st.columns(2)

        with col5:
            allow_quick_start = st.checkbox(
                "Schnellstart erlauben",
                value=settings.get('allow_quick_start', False),
                help="Ermöglicht direkten Start ohne Login (UNSICHER)"
            )

        with col6:
            allow_guest = st.checkbox(
                "Gastmodus erlauben",
                value=settings.get('allow_guest', False),
                help="Benutzer können als Gast fortfahren (UNSICHER)"
            )

        st.markdown("---")
        st.markdown("#### Medien-Anzeige")

        media_type = st.selectbox(
            "Medien-Typ",
            options=[
                'none',
                'image',
                'video'],
            format_func=lambda x: {
                'none': 'Keine',
                'image': 'Bild',
                'video': 'Video'}[x],
            index=[
                'none',
                'image',
                'video'].index(
                    settings.get(
                        'media_type',
                        'image')),
            help="Wählen Sie, ob ein Bild oder Video angezeigt werden soll")

        if media_type == 'image':
            st.markdown("##### Hauptbild (Mitte)")

            col_img1, col_img2 = st.columns([2, 1])

            with col_img1:
                image_path = st.text_input(
                    "Hauptbild-Pfad",
                    value=settings.get(
                        'image_path',
                        'data/company_logos/default_company_logo.png'),
                    help="Relativer Pfad zum Hauptbild (z.B. data/company_logos/logo.png)")

            with col_img2:
                main_image_upload = st.file_uploader(
                    "Hauptbild hochladen",
                    type=['png', 'jpg', 'jpeg'],
                    key="main_image_upload",
                    help="PNG oder JPG, max. 5MB"
                )

            # Hauptbild hochladen und speichern
            if main_image_upload:
                if main_image_upload.size > 5 * 1024 * 1024:
                    st.error("Hauptbild ist zu groß (max. 5MB)")
                else:
                    # Erstelle Verzeichnis falls nicht vorhanden
                    Path("data/company_logos").mkdir(parents=True, exist_ok=True)

                    # Speichere Datei
                    main_image_filename = f"intro_main_{
                        main_image_upload.name}"
                    main_image_path = Path(
                        "data/company_logos") / main_image_filename

                    with open(main_image_path, "wb") as f:
                        f.write(main_image_upload.getbuffer())

                    image_path = str(main_image_path)
                    st.success(f"Hauptbild hochgeladen: {main_image_filename}")

            # Vorschau Hauptbild
            if Path(image_path).exists():
                st.image(image_path, caption="Hauptbild-Vorschau", width=300)
            else:
                st.warning(f"Hauptbild nicht gefunden: {image_path}")

            st.markdown("---")
            st.markdown("##### Seitenbilder (Optional)")

            show_side_images = st.checkbox(
                "Seitenbilder aktivieren",
                value=settings.get(
                    'show_side_images',
                    False),
                help="Zeigt zwei kleine Bilder links und rechts vom Hauptbild an")

            if show_side_images:
                # Linkes Seitenbild
                st.markdown("**Linkes Seitenbild:**")
                col_left1, col_left2 = st.columns([2, 1])

                with col_left1:
                    image_left_path = st.text_input(
                        "Linkes Bild-Pfad",
                        value=settings.get(
                            'image_left_path',
                            'data/company_logos/left_logo.png'),
                        help="Relativer Pfad zum linken Seitenbild")

                with col_left2:
                    left_image_upload = st.file_uploader(
                        "Linkes Bild hochladen",
                        type=['png', 'jpg', 'jpeg'],
                        key="left_image_upload",
                        help="PNG oder JPG, max. 2MB"
                    )

                # Linkes Bild hochladen und speichern
                if left_image_upload:
                    if left_image_upload.size > 2 * 1024 * 1024:
                        st.error("Linkes Bild ist zu groß (max. 2MB)")
                    else:
                        Path("data/company_logos").mkdir(parents=True, exist_ok=True)
                        left_image_filename = f"intro_left_{
                            left_image_upload.name}"
                        left_image_path_obj = Path(
                            "data/company_logos") / left_image_filename

                        with open(left_image_path_obj, "wb") as f:
                            f.write(left_image_upload.getbuffer())

                        image_left_path = str(left_image_path_obj)
                        st.success(
                            f"✅ Linkes Bild hochgeladen: {left_image_filename}")

                # Vorschau linkes Bild
                if Path(image_left_path).exists():
                    st.image(
                        image_left_path,
                        caption="Linkes Seitenbild-Vorschau",
                        width=150)
                else:
                    st.info(
                        f"ℹ️ Linkes Bild nicht gefunden: {image_left_path}")

                st.markdown("---")

                # Rechtes Seitenbild
                st.markdown("**Rechtes Seitenbild:**")
                col_right1, col_right2 = st.columns([2, 1])

                with col_right1:
                    image_right_path = st.text_input(
                        "Rechtes Bild-Pfad",
                        value=settings.get(
                            'image_right_path',
                            'data/company_logos/right_logo.png'),
                        help="Relativer Pfad zum rechten Seitenbild")

                with col_right2:
                    right_image_upload = st.file_uploader(
                        "Rechtes Bild hochladen",
                        type=['png', 'jpg', 'jpeg'],
                        key="right_image_upload",
                        help="PNG oder JPG, max. 2MB"
                    )

                # Rechtes Bild hochladen und speichern
                if right_image_upload:
                    if right_image_upload.size > 2 * 1024 * 1024:
                        st.error("Rechtes Bild ist zu groß (max. 2MB)")
                    else:
                        Path("data/company_logos").mkdir(parents=True, exist_ok=True)
                        right_image_filename = f"intro_right_{
                            right_image_upload.name}"
                        right_image_path_obj = Path(
                            "data/company_logos") / right_image_filename

                        with open(right_image_path_obj, "wb") as f:
                            f.write(right_image_upload.getbuffer())

                        image_right_path = str(right_image_path_obj)
                        st.success(
                            f"✅ Rechtes Bild hochgeladen: {right_image_filename}")

                # Vorschau rechtes Bild
                if Path(image_right_path).exists():
                    st.image(
                        image_right_path,
                        caption="Rechtes Seitenbild-Vorschau",
                        width=150)
                else:
                    st.info(
                        f"ℹ️ Rechtes Bild nicht gefunden: {image_right_path}")

                st.markdown("---")
                st.markdown("##### 👁️ Layout-Vorschau (3-Bilder-Ansicht)")

                # Zeige Vorschau wie die 3 Bilder angeordnet werden
                preview_col1, preview_col2, preview_col3 = st.columns([
                                                                      1, 2, 1])

                with preview_col1:
                    if Path(image_left_path).exists():
                        st.image(
                            image_left_path,
                            caption="Klein (Links)",
                            use_container_width=True)
                    else:
                        st.info("Linkes Bild\n(150px)")

                with preview_col2:
                    if Path(image_path).exists():
                        st.image(
                            image_path,
                            caption="Groß (Mitte)",
                            use_container_width=True)
                    else:
                        st.info("Hauptbild\n(400px)")

                with preview_col3:
                    if Path(image_right_path).exists():
                        st.image(
                            image_right_path,
                            caption="Klein (Rechts)",
                            use_container_width=True)
                    else:
                        st.info("Rechtes Bild\n(150px)")

                st.caption(
                    "💡 So werden die Bilder im Intro-Bildschirm angezeigt (mit Float-Animation)")
            else:
                # Standardwerte wenn Seitenbilder deaktiviert
                image_left_path = settings.get(
                    'image_left_path', 'data/company_logos/left_logo.png')
                image_right_path = settings.get(
                    'image_right_path', 'data/company_logos/right_logo.png')

        elif media_type == 'video':
            video_url = st.text_input(
                "Video-URL",
                value=settings.get('video_url', ''),
                help="YouTube-URL oder direkter Video-Link"
            )

            if video_url:
                st.info(f"Video: {video_url}")

        st.markdown("---")
        st.markdown("#### Texte anpassen")

        title = st.text_input(
            "Titel",
            value=settings.get('title', 'Bokuk2'),
            help="Haupttitel des Intro-Bildschirms"
        )

        subtitle = st.text_input(
            "Untertitel",
            value=settings.get(
                'subtitle',
                'Photovoltaik & Wärmepumpen Kalkulationssystem'),
            help="Untertitel unterhalb des Haupttitels")

        description = st.text_area(
            "Beschreibung",
            value=settings.get(
                'description',
                ''),
            height=150,
            help="HTML ist erlaubt (z.B. <br> für Zeilenumbruch, • für Aufzählungen)")

        st.markdown("---")

        # Speichern-Button
        col_save1, col_save2, col_save3 = st.columns([2, 1, 1])

        with col_save1:
            save_button = st.form_submit_button(
                "Einstellungen speichern",
                type="primary",
                use_container_width=True
            )

        with col_save2:
            reset_button = st.form_submit_button(
                "Zurücksetzen",
                use_container_width=True
            )

        with col_save3:
            preview_button = st.form_submit_button(
                "👁 Vorschau",
                use_container_width=True
            )

        if save_button:
            new_settings = {
                'enabled': enabled,
                'media_type': media_type,
                'image_path': image_path if media_type == 'image' else settings.get(
                    'image_path',
                    ''),
                'image_left_path': image_left_path if media_type == 'image' else settings.get(
                    'image_left_path',
                    ''),
                'image_right_path': image_right_path if media_type == 'image' else settings.get(
                    'image_right_path',
                    ''),
                'show_side_images': show_side_images if media_type == 'image' else settings.get(
                    'show_side_images',
                    False),
                'video_url': video_url if media_type == 'video' else settings.get(
                    'video_url',
                    ''),
                'require_login': require_login,
                'allow_registration': allow_registration,
                'require_company_info': require_company_info,
                'allow_guest': allow_guest,
                'allow_quick_start': allow_quick_start,
                'title': title,
                'subtitle': subtitle,
                'description': description}

            if save_intro_settings(new_settings):
                st.success("✅ Einstellungen erfolgreich gespeichert!")
                st.info("ℹ️ Die Änderungen werden beim nächsten App-Start wirksam.")

                # Zeige gespeicherte Bildpfade an
                if media_type == 'image':
                    st.markdown("**Gespeicherte Bildpfade:**")
                    st.code(f"Hauptbild: {image_path}")
                    if show_side_images:
                        st.code(f"Linkes Bild: {image_left_path}")
                        st.code(f"Rechtes Bild: {image_right_path}")
            else:
                st.error("❌ Fehler beim Speichern der Einstellungen")

        if reset_button:
            st.session_state['intro_completed'] = False
            st.success(
                "Intro-Status zurückgesetzt - beim nächsten Laden wird der Intro-Bildschirm angezeigt")
            st.info("Laden Sie die Seite neu (F5), um den Intro-Bildschirm zu sehen")

        if preview_button:
            st.info(
                "Tipp: Setzen Sie den Intro-Status zurück und laden Sie die Seite neu (F5), um eine Vorschau zu sehen")

    # Hilfe-Sektion
    with st.expander("📖 Hilfe zu den Einstellungen"):
        st.markdown("""
        **Intro-Bildschirm aktivieren:**
        - Wenn aktiviert: Benutzer sehen beim Start den Willkommensbildschirm
        - Wenn deaktiviert: Anwendung startet direkt

        **Login erzwingen (EMPFOHLEN):**
        - Benutzer müssen sich mit Benutzername/Passwort anmelden
        - Schnellstart und Gastmodus werden deaktiviert
        - Höhere Sicherheit

        **Registrierung erlauben:**
        - Neue Benutzer können sich selbst registrieren
        - Pflichtfelder: Benutzername, Passwort, Name, E-Mail, Telefon
        - Optionale Felder: Adresse, Notizen

        **Firmeninfo bei Registrierung:**
        - Benutzer wählen Kontotyp: Privatkunde oder Firmenkunde
        - Bei Firmenkunde: Firmenname ist Pflicht
        - Zusätzliche Felder: Position, Abteilung

        **Medien-Typen:**
        - **Keine**: Nur Text wird angezeigt
        - **Bild**: Zeigt ein Logo oder Bild an (PNG, JPG)
        - **Video**: Eingebettetes YouTube-Video oder direkter Video-Link

        **Hauptbild & Seitenbilder (NEU):**
        - **Hauptbild**: Großes Logo in der Mitte (max. 5MB)
        - **Seitenbilder**: Zwei kleine Logos links und rechts (max. 2MB je Bild)
        - **Seitenbilder aktivieren**: Checkbox aktivieren, um die 3-Bilder-Ansicht zu nutzen
        - **Upload-Funktion**: Laden Sie Bilder direkt hoch - sie werden automatisch in `data/company_logos/` gespeichert
        - **Bildformate**: PNG, JPG, JPEG werden unterstützt
        - **Dateinamenmuster**:
          - Hauptbild: `intro_main_[originaler_name]`
          - Linkes Bild: `intro_left_[originaler_name]`
          - Rechtes Bild: `intro_right_[originaler_name]`

        **Legacy-Zugangsoptionen (NICHT EMPFOHLEN):**
        - **Schnellstart**: Sofortiger Zugang ohne Login (UNSICHER)
        - **Gastmodus**: Zugang ohne Registrierung (UNSICHER)

        **Texte anpassen:**
        - HTML-Tags sind in der Beschreibung erlaubt
        - Verwenden Sie `<br>` für Zeilenumbrüche

        **Standard-Login:**
        - Benutzername: `admin`
        - Passwort: `admin`

        **Tipps für Seitenbilder:**
        - Verwenden Sie quadratische Bilder für beste Ergebnisse
        - Empfohlene Größe für Seitenbilder: 300x300px oder 500x500px
        - Empfohlene Größe für Hauptbild: 800x800px oder größer
        - Transparente PNGs funktionieren besonders gut
        - Die Bilder werden mit CSS-Animationen angezeigt (float-Effekt)
        """)

    # Aktuelle Konfiguration anzeigen
    with st.expander("Aktuelle Konfiguration (JSON)"):
        st.json(settings)
