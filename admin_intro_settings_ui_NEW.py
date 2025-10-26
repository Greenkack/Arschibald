"""
admin_intro_settings_ui.py
Zweck: Admin-UI für Intro-Bildschirm-Einstellungen mit SOFORTIGER Upload-Funktionalität
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

    # ===================================================================
    # BILD-UPLOADS AUSSERHALB DES FORMULARS (SOFORTIGE SPEICHERUNG)
    # ===================================================================

    st.markdown("---")
    st.markdown("#### 📸 Bild-Uploads (Sofortige Speicherung)")
    st.info("💡 Bilder werden sofort nach dem Upload gespeichert. Klicken Sie dann 'Einstellungen speichern' unten, um die Pfade zu übernehmen.")

    # Medien-Typ Auswahl (außerhalb des Formulars)
    media_type = st.selectbox(
        "Medien-Typ",
        options=['none', 'image', 'video'],
        format_func=lambda x: {'none': 'Keine', 'image': 'Bild', 'video': 'Video'}[x],
        index=['none', 'image', 'video'].index(settings.get('media_type', 'image')),
        help="Wählen Sie, ob ein Bild oder Video angezeigt werden soll",
        key="media_type_select_outside"
    )

    # Session State für Bildpfade
    if 'uploaded_main_image_path' not in st.session_state:
        st.session_state.uploaded_main_image_path = settings.get(
            'image_path', 'data/company_logos/default_company_logo.png')
    if 'uploaded_left_image_path' not in st.session_state:
        st.session_state.uploaded_left_image_path = settings.get(
            'image_left_path', 'data/company_logos/left_logo.png')
    if 'uploaded_right_image_path' not in st.session_state:
        st.session_state.uploaded_right_image_path = settings.get(
            'image_right_path', 'data/company_logos/right_logo.png')

    if media_type == 'image':
        st.markdown("##### 🖼️ Hauptbild (Mitte) - Sofort-Upload")

        col_main1, col_main2 = st.columns([1, 1])

        with col_main1:
            main_image_upload = st.file_uploader(
                "📤 Hauptbild jetzt hochladen",
                type=['png', 'jpg', 'jpeg'],
                key="main_image_upload_instant",
                help="PNG oder JPG, max. 5MB - wird SOFORT gespeichert!"
            )

            if main_image_upload:
                if main_image_upload.size > 5 * 1024 * 1024:
                    st.error("❌ Hauptbild ist zu groß (max. 5MB)")
                else:
                    try:
                        # Erstelle Verzeichnis
                        Path("data/company_logos").mkdir(parents=True, exist_ok=True)

                        # Speichere Datei SOFORT
                        main_image_filename = f"intro_main_{
                            main_image_upload.name}"
                        main_image_path_obj = Path(
                            "data/company_logos") / main_image_filename

                        with open(main_image_path_obj, "wb") as f:
                            f.write(main_image_upload.getbuffer())

                        # Speichere Pfad in Session State
                        st.session_state.uploaded_main_image_path = str(
                            main_image_path_obj)

                        st.success(
                            f"✅ Hauptbild gespeichert: `{main_image_filename}`")
                        st.info(
                            f"📍 Pfad: `{
                                st.session_state.uploaded_main_image_path}`")

                        # Automatisch in Settings speichern
                        settings['image_path'] = str(main_image_path_obj)
                        save_intro_settings(settings)
                        st.success("✅ Einstellungen automatisch aktualisiert!")

                    except Exception as e:
                        st.error(f"❌ Fehler beim Speichern: {e}")

        with col_main2:
            # Vorschau Hauptbild
            if Path(st.session_state.uploaded_main_image_path).exists():
                st.image(
                    st.session_state.uploaded_main_image_path,
                    caption="Hauptbild-Vorschau",
                    use_container_width=True)
                st.caption(
                    f"Aktuell: `{
                        Path(
                            st.session_state.uploaded_main_image_path).name}`")
            else:
                st.warning("⚠️ Kein Hauptbild vorhanden")
                st.caption(
                    f"Pfad: `{
                        st.session_state.uploaded_main_image_path}`")

        st.markdown("---")

        # Seitenbilder aktivieren Checkbox
        show_side_images = st.checkbox(
            "🔄 Seitenbilder aktivieren (3-Bilder-Layout)",
            value=settings.get('show_side_images', False),
            help="Zeigt zwei kleine Bilder links und rechts vom Hauptbild an",
            key="show_side_images_checkbox"
        )

        if show_side_images:
            st.markdown("##### 🖼️ Seitenbilder - Sofort-Upload")

            # Linkes Seitenbild
            st.markdown("**👈 Linkes Seitenbild:**")
            col_left1, col_left2 = st.columns([1, 1])

            with col_left1:
                left_image_upload = st.file_uploader(
                    "📤 Linkes Bild jetzt hochladen",
                    type=['png', 'jpg', 'jpeg'],
                    key="left_image_upload_instant",
                    help="PNG oder JPG, max. 2MB - wird SOFORT gespeichert!"
                )

                if left_image_upload:
                    if left_image_upload.size > 2 * 1024 * 1024:
                        st.error("❌ Linkes Bild ist zu groß (max. 2MB)")
                    else:
                        try:
                            Path("data/company_logos").mkdir(parents=True,
                                                             exist_ok=True)
                            left_image_filename = f"intro_left_{
                                left_image_upload.name}"
                            left_image_path_obj = Path(
                                "data/company_logos") / left_image_filename

                            with open(left_image_path_obj, "wb") as f:
                                f.write(left_image_upload.getbuffer())

                            st.session_state.uploaded_left_image_path = str(
                                left_image_path_obj)

                            st.success(
                                f"✅ Linkes Bild gespeichert: `{left_image_filename}`")
                            st.info(
                                f"📍 Pfad: `{
                                    st.session_state.uploaded_left_image_path}`")

                            # Automatisch in Settings speichern
                            settings['image_left_path'] = str(
                                left_image_path_obj)
                            save_intro_settings(settings)
                            st.success(
                                "✅ Einstellungen automatisch aktualisiert!")

                        except Exception as e:
                            st.error(f"❌ Fehler beim Speichern: {e}")

            with col_left2:
                if Path(st.session_state.uploaded_left_image_path).exists():
                    st.image(
                        st.session_state.uploaded_left_image_path,
                        caption="Linkes Bild-Vorschau",
                        use_container_width=True)
                    st.caption(
                        f"Aktuell: `{
                            Path(
                                st.session_state.uploaded_left_image_path).name}`")
                else:
                    st.info("ℹ️ Kein linkes Bild vorhanden")
                    st.caption(
                        f"Pfad: `{
                            st.session_state.uploaded_left_image_path}`")

            st.markdown("---")

            # Rechtes Seitenbild
            st.markdown("**👉 Rechtes Seitenbild:**")
            col_right1, col_right2 = st.columns([1, 1])

            with col_right1:
                right_image_upload = st.file_uploader(
                    "📤 Rechtes Bild jetzt hochladen",
                    type=['png', 'jpg', 'jpeg'],
                    key="right_image_upload_instant",
                    help="PNG oder JPG, max. 2MB - wird SOFORT gespeichert!"
                )

                if right_image_upload:
                    if right_image_upload.size > 2 * 1024 * 1024:
                        st.error("❌ Rechtes Bild ist zu groß (max. 2MB)")
                    else:
                        try:
                            Path("data/company_logos").mkdir(parents=True,
                                                             exist_ok=True)
                            right_image_filename = f"intro_right_{
                                right_image_upload.name}"
                            right_image_path_obj = Path(
                                "data/company_logos") / right_image_filename

                            with open(right_image_path_obj, "wb") as f:
                                f.write(right_image_upload.getbuffer())

                            st.session_state.uploaded_right_image_path = str(
                                right_image_path_obj)

                            st.success(
                                f"✅ Rechtes Bild gespeichert: `{right_image_filename}`")
                            st.info(
                                f"📍 Pfad: `{
                                    st.session_state.uploaded_right_image_path}`")

                            # Automatisch in Settings speichern
                            settings['image_right_path'] = str(
                                right_image_path_obj)
                            save_intro_settings(settings)
                            st.success(
                                "✅ Einstellungen automatisch aktualisiert!")

                        except Exception as e:
                            st.error(f"❌ Fehler beim Speichern: {e}")

            with col_right2:
                if Path(st.session_state.uploaded_right_image_path).exists():
                    st.image(
                        st.session_state.uploaded_right_image_path,
                        caption="Rechtes Bild-Vorschau",
                        use_container_width=True)
                    st.caption(
                        f"Aktuell: `{
                            Path(
                                st.session_state.uploaded_right_image_path).name}`")
                else:
                    st.info("ℹ️ Kein rechtes Bild vorhanden")
                    st.caption(
                        f"Pfad: `{
                            st.session_state.uploaded_right_image_path}`")

            st.markdown("---")
            st.markdown("##### 👁️ Layout-Vorschau (3-Bilder-Ansicht)")

            # Zeige Vorschau wie die 3 Bilder angeordnet werden
            preview_col1, preview_col2, preview_col3 = st.columns([1, 2, 1])

            with preview_col1:
                if Path(st.session_state.uploaded_left_image_path).exists():
                    st.image(
                        st.session_state.uploaded_left_image_path,
                        caption="Klein (Links)",
                        use_container_width=True)
                else:
                    st.info("Linkes Bild\n(150px)")

            with preview_col2:
                if Path(st.session_state.uploaded_main_image_path).exists():
                    st.image(
                        st.session_state.uploaded_main_image_path,
                        caption="Groß (Mitte)",
                        use_container_width=True)
                else:
                    st.info("Hauptbild\n(400px)")

            with preview_col3:
                if Path(st.session_state.uploaded_right_image_path).exists():
                    st.image(
                        st.session_state.uploaded_right_image_path,
                        caption="Klein (Rechts)",
                        use_container_width=True)
                else:
                    st.info("Rechtes Bild\n(150px)")

            st.caption(
                "💡 So werden die Bilder im Intro-Bildschirm angezeigt (mit Float-Animation)")

    elif media_type == 'video':
        st.markdown("##### 📹 Video-URL")
        video_url_input = st.text_input(
            "Video-URL eingeben",
            value=settings.get('video_url', ''),
            help="YouTube-URL oder direkter Video-Link",
            key="video_url_input_outside"
        )

        if video_url_input:
            st.info(f"🎬 Video: {video_url_input}")

    # ===================================================================
    # FORMULAR FÜR RESTLICHE EINSTELLUNGEN
    # ===================================================================

    st.markdown("---")

    with st.form("intro_settings_form"):
        st.markdown("#### ⚙️ Grund einstellungen")

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
        st.markdown("#### 📝 Registrierungs-Einstellungen")

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
        st.markdown("#### ⚠️ Legacy-Zugangsoptionen (Nicht empfohlen)")

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
        st.markdown("#### ✏️ Texte anpassen")

        title = st.text_input(
            "Titel",
            value=settings.get('title', 'Ömers All in One Machine'),
            help="Haupttitel des Intro-Bildschirms"
        )

        subtitle = st.text_input(
            "Untertitel",
            value=settings.get('subtitle', ''),
            help="Untertitel unterhalb des Haupttitels"
        )

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
                "💾 Einstellungen speichern",
                type="primary",
                use_container_width=True
            )

        with col_save2:
            reset_button = st.form_submit_button(
                "🔄 Zurücksetzen",
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
                'image_path': st.session_state.uploaded_main_image_path,
                'image_left_path': st.session_state.uploaded_left_image_path if show_side_images else settings.get(
                    'image_left_path',
                    ''),
                'image_right_path': st.session_state.uploaded_right_image_path if show_side_images else settings.get(
                    'image_right_path',
                    ''),
                'show_side_images': show_side_images,
                'video_url': video_url_input if media_type == 'video' else '',
                'require_login': require_login,
                'allow_registration': allow_registration,
                'require_company_info': require_company_info,
                'allow_guest': allow_guest,
                'allow_quick_start': allow_quick_start,
                'title': title,
                'subtitle': subtitle,
                'description': description}

            if save_intro_settings(new_settings):
                st.success("✅ Alle Einstellungen erfolgreich gespeichert!")
                st.info("ℹ️ Die Änderungen werden beim nächsten App-Start wirksam.")

                # Zeige gespeicherte Bildpfade an
                if media_type == 'image':
                    st.markdown("**📁 Gespeicherte Bildpfade:**")
                    st.code(
                        f"Hauptbild: {
                            st.session_state.uploaded_main_image_path}",
                        language="text")
                    if show_side_images:
                        st.code(
                            f"Linkes Bild: {
                                st.session_state.uploaded_left_image_path}",
                            language="text")
                        st.code(
                            f"Rechtes Bild: {
                                st.session_state.uploaded_right_image_path}",
                            language="text")
            else:
                st.error("❌ Fehler beim Speichern der Einstellungen")

        if reset_button:
            st.session_state['intro_completed'] = False
            st.success("✅ Intro-Status zurückgesetzt")
            st.info(
                "💡 Laden Sie die Seite neu (F5), um den Intro-Bildschirm zu sehen")

        if preview_button:
            st.info(
                "💡 Tipp: Setzen Sie den Intro-Status zurück und laden Sie die Seite neu (F5), um eine Vorschau zu sehen")

    # Hilfe-Sektion
    with st.expander("📖 Hilfe & Dokumentation"):
        st.markdown("""
        ### 🎯 Schnellstart

        **So laden Sie Bilder hoch:**
        1. Wählen Sie "Bild" als Medien-Typ
        2. Klicken Sie auf "Hauptbild jetzt hochladen" → Bild wird SOFORT gespeichert
        3. Optional: Aktivieren Sie "Seitenbilder" und laden Sie links/rechts Bilder hoch
        4. Klicken Sie "Einstellungen speichern" um alle Änderungen zu übernehmen
        5. Starten Sie die App neu (F5) um die Änderungen zu sehen

        ### 📸 Bildanforderungen

        **Hauptbild (Mitte):**
        - Max. Größe: 5MB
        - Formate: PNG, JPG, JPEG
        - Empfohlen: 800x800px oder größer, quadratisch

        **Seitenbilder (Links/Rechts):**
        - Max. Größe: 2MB je Bild
        - Formate: PNG, JPG, JPEG
        - Empfohlen: 300x300px oder 500x500px, quadratisch

        ### 💡 Tipps

        - Verwenden Sie transparente PNGs für beste Ergebnisse
        - Quadratische Bilder sehen am besten aus
        - Bilder werden automatisch mit Float-Animation angezeigt
        - Die Uploads speichern sofort - kein Warten auf "Speichern" nötig

        ### 🔐 Sicherheit

        **Empfohlen:**
        - ✅ "Login erzwingen" aktivieren
        - ✅ "Registrierung erlauben" für neue Benutzer
        - ❌ "Schnellstart" und "Gastmodus" deaktivieren

        ### 🆘 Problembehebung

        **Bild wird nicht angezeigt:**
        1. Prüfen Sie ob die Datei hochgeladen wurde (grünes Häkchen)
        2. Klicken Sie "Einstellungen speichern"
        3. Laden Sie die Seite neu (F5)
        4. Prüfen Sie den Pfad: `data/company_logos/intro_main_[dateiname]`

        **Uploads funktionieren nicht:**
        - Prüfen Sie die Dateigröße (Hauptbild max. 5MB, Seitenbilder max. 2MB)
        - Prüfen Sie das Format (nur PNG, JPG, JPEG erlaubt)
        - Prüfen Sie Schreibrechte im `data/company_logos/` Ordner
        """)

    # Aktuelle Konfiguration anzeigen
    with st.expander("🔍 Aktuelle Konfiguration (JSON)"):
        current_settings = load_intro_settings()
        st.json(current_settings)

        st.markdown("**📁 Gespeicherte Dateien:**")
        logos_dir = Path("data/company_logos")
        if logos_dir.exists():
            intro_files = list(logos_dir.glob("intro_*"))
            if intro_files:
                for file in intro_files:
                    file_size = file.stat().st_size / 1024  # KB
                    st.code(f"{file.name} ({file_size:.1f} KB)",
                            language="text")
            else:
                st.info("Keine Intro-Bilder gefunden")
        else:
            st.warning("Verzeichnis `data/company_logos` existiert nicht")
