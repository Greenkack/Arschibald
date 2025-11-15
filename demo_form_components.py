"""
Demo für shadcn/ui Form-Komponenten

Dieses Skript demonstriert alle erweiterten Formular-Komponenten.
"""

import streamlit as st
from datetime import date, timedelta
from components.form_components import (
    Input, DatePicker, Calendar, InputOTP,
    input_field, date_picker, calendar, input_otp
)
from theming import ThemeManager

# Seiten-Konfiguration
st.set_page_config(
    page_title="Form Components Demo",
    page_icon="📝",
    layout="wide"
)

# Theme Manager initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# Titel
st.title("📝 shadcn/ui Form Components Demo")
st.markdown("---")

# Tabs für verschiedene Komponenten
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Input Fields",
    "DatePicker",
    "Calendar",
    "Input OTP",
    "Complete Form"
])

# Tab 1: Input Fields
with tab1:
    st.header("Input Fields mit Floating Labels")

    st.subheader("1. Basic Text Input")
    input_comp = Input(theme_manager=theme_manager)
    text_value = input_comp.render(
        label="Name",
        placeholder="Ihr vollständiger Name",
        help_text="Geben Sie Ihren Vor- und Nachnamen ein",
        key="demo_text_input"
    )
    if text_value:
        st.info(f"Eingabe: {text_value}")

    st.markdown("---")

    st.subheader("2. Email Input mit Icon")
    email_value = input_field(
        label="E-Mail-Adresse",
        type="email",
        placeholder="ihre@email.de",
        prefix_icon="📧",
        help_text="Wir werden Ihre E-Mail niemals weitergeben",
        required=True,
        key="demo_email_input",
        theme_manager=theme_manager
    )
    if email_value:
        if "@" in email_value and "." in email_value:
            st.success(f"✓ Gültige E-Mail: {email_value}")
        else:
            st.error("✗ Ungültige E-Mail-Adresse")

    st.markdown("---")

    st.subheader("3. Password Input")
    password_value = input_field(
        label="Passwort",
        type="password",
        placeholder="Mindestens 8 Zeichen",
        prefix_icon="🔒",
        help_text="Verwenden Sie ein sicheres Passwort",
        required=True,
        key="demo_password_input",
        theme_manager=theme_manager
    )
    if password_value:
        if len(password_value) >= 8:
            st.success("✓ Passwort ist stark genug")
        else:
            st.warning("⚠ Passwort sollte mindestens 8 Zeichen haben")

    st.markdown("---")

    st.subheader("4. Number Input")
    number_value = input_field(
        label="Alter",
        type="number",
        placeholder="18",
        suffix_icon="🎂",
        help_text="Ihr Alter in Jahren",
        key="demo_number_input",
        theme_manager=theme_manager
    )
    if number_value:
        st.info(f"Alter: {number_value} Jahre")

    st.markdown("---")

    st.subheader("5. Input mit Error State")
    error_input = Input(theme_manager=theme_manager)
    error_value = error_input.render(
        label="Benutzername",
        placeholder="username",
        error="Dieser Benutzername ist bereits vergeben",
        key="demo_error_input"
    )

    st.markdown("---")

    st.subheader("6. Input mit Success State")
    success_input = Input(theme_manager=theme_manager)
    success_value = success_input.render(
        label="Verfügbarer Benutzername",
        value="john_doe_2024",
        success="✓ Dieser Benutzername ist verfügbar",
        key="demo_success_input"
    )

# Tab 2: DatePicker
with tab2:
    st.header("DatePicker Component")

    st.subheader("1. Basic DatePicker")
    picker1 = DatePicker(theme_manager=theme_manager)
    selected_date1 = picker1.render(
        label="Geburtsdatum",
        help_text="Wählen Sie Ihr Geburtsdatum",
        max_date=date.today(),
        key="demo_datepicker_1"
    )
    if selected_date1:
        age = (date.today() - selected_date1).days // 365
        st.info(f"Ausgewähltes Datum: {selected_date1} (ca. {age} Jahre alt)")

    st.markdown("---")

    st.subheader("2. DatePicker mit Einschränkungen")
    picker2 = DatePicker(theme_manager=theme_manager)
    selected_date2 = picker2.render(
        label="Termin",
        help_text="Wählen Sie einen Termin in den nächsten 30 Tagen",
        min_date=date.today(),
        max_date=date.today() + timedelta(days=30),
        required=True,
        key="demo_datepicker_2"
    )
    if selected_date2:
        days_until = (selected_date2 - date.today()).days
        st.success(f"Termin in {days_until} Tagen: {selected_date2}")

    st.markdown("---")

    st.subheader("3. DatePicker mit Error")
    picker3 = DatePicker(theme_manager=theme_manager)
    selected_date3 = picker3.render(
        label="Ablaufdatum",
        error="Das Datum muss in der Zukunft liegen",
        required=True,
        key="demo_datepicker_3"
    )

# Tab 3: Calendar
with tab3:
    st.header("Calendar Component")

    st.subheader("1. Basic Calendar")
    cal1 = Calendar(theme_manager=theme_manager)
    selected_cal1 = cal1.render(
        selected_date=date.today(),
        key="demo_calendar_1"
    )
    if selected_cal1:
        st.info(f"Ausgewähltes Datum: {selected_cal1}")

    st.markdown("---")

    st.subheader("2. Calendar mit Einschränkungen")
    cal2 = Calendar(theme_manager=theme_manager)
    selected_cal2 = cal2.render(
        selected_date=date.today(),
        min_date=date.today() - timedelta(days=7),
        max_date=date.today() + timedelta(days=7),
        key="demo_calendar_2"
    )
    if selected_cal2:
        st.success(f"Datum innerhalb der letzten/nächsten 7 Tage: "
                   f"{selected_cal2}")

    st.markdown("---")

    st.subheader("3. Convenience Function")
    selected_cal3 = calendar(
        selected_date=date.today(),
        key="demo_calendar_3",
        theme_manager=theme_manager
    )

# Tab 4: Input OTP
with tab4:
    st.header("Input OTP Component")

    st.subheader("1. 6-Digit OTP")
    otp1 = InputOTP(theme_manager=theme_manager)
    code1 = otp1.render(
        label="Bestätigungscode",
        length=6,
        help_text="Geben Sie den 6-stelligen Code aus der E-Mail ein",
        key="demo_otp_1"
    )
    if code1 and len(code1) == 6:
        st.success(f"✓ Code eingegeben: {code1}")
    elif code1:
        st.warning(f"⚠ Bitte alle {6} Ziffern eingeben (aktuell: "
                   f"{len(code1)})")

    st.markdown("---")

    st.subheader("2. 4-Digit PIN")
    otp2 = InputOTP(theme_manager=theme_manager)
    code2 = otp2.render(
        label="PIN-Code",
        length=4,
        help_text="Geben Sie Ihren 4-stelligen PIN ein",
        key="demo_otp_2"
    )
    if code2 and len(code2) == 4:
        st.success(f"✓ PIN eingegeben: {'*' * 4}")

    st.markdown("---")

    st.subheader("3. OTP mit Error")
    otp3 = InputOTP(theme_manager=theme_manager)
    code3 = otp3.render(
        label="Verifizierungscode",
        length=6,
        error="Der eingegebene Code ist ungültig",
        key="demo_otp_3"
    )

    st.markdown("---")

    st.subheader("4. Convenience Function")
    code4 = input_otp(
        label="SMS-Code",
        length=6,
        help_text="Code aus SMS eingeben",
        key="demo_otp_4",
        theme_manager=theme_manager
    )

# Tab 5: Complete Form
with tab5:
    st.header("Vollständiges Registrierungsformular")

    st.markdown("""
    Dieses Beispiel zeigt, wie alle Komponenten zusammen in einem
    echten Formular verwendet werden können.
    """)

    with st.form("registration_form"):
        st.subheader("Persönliche Informationen")

        col1, col2 = st.columns(2)

        with col1:
            first_name = input_field(
                label="Vorname",
                placeholder="Max",
                required=True,
                key="form_firstname",
                theme_manager=theme_manager
            )

        with col2:
            last_name = input_field(
                label="Nachname",
                placeholder="Mustermann",
                required=True,
                key="form_lastname",
                theme_manager=theme_manager
            )

        email = input_field(
            label="E-Mail-Adresse",
            type="email",
            placeholder="max@example.com",
            prefix_icon="📧",
            required=True,
            key="form_email",
            theme_manager=theme_manager
        )

        phone = input_field(
            label="Telefonnummer",
            type="tel",
            placeholder="+49 123 456789",
            prefix_icon="📱",
            key="form_phone",
            theme_manager=theme_manager
        )

        birth_date = date_picker(
            label="Geburtsdatum",
            max_date=date.today(),
            required=True,
            key="form_birthdate",
            theme_manager=theme_manager
        )

        st.markdown("---")
        st.subheader("Account-Informationen")

        username = input_field(
            label="Benutzername",
            placeholder="maxmustermann",
            help_text="Mindestens 3 Zeichen, nur Buchstaben und Zahlen",
            required=True,
            key="form_username",
            theme_manager=theme_manager
        )

        password = input_field(
            label="Passwort",
            type="password",
            placeholder="Mindestens 8 Zeichen",
            prefix_icon="🔒",
            required=True,
            key="form_password",
            theme_manager=theme_manager
        )

        password_confirm = input_field(
            label="Passwort bestätigen",
            type="password",
            placeholder="Passwort wiederholen",
            prefix_icon="🔒",
            required=True,
            key="form_password_confirm",
            theme_manager=theme_manager
        )

        st.markdown("---")
        st.subheader("Verifizierung")

        verification_code = input_otp(
            label="E-Mail-Bestätigungscode",
            length=6,
            help_text="Code aus der Bestätigungs-E-Mail",
            key="form_verification",
            theme_manager=theme_manager
        )

        st.markdown("---")

        # Submit Button
        submitted = st.form_submit_button(
            "Registrierung abschließen",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Validierung
            errors = []

            if not first_name or not last_name:
                errors.append("Vor- und Nachname sind erforderlich")

            if not email or "@" not in email:
                errors.append("Gültige E-Mail-Adresse erforderlich")

            if not username or len(username) < 3:
                errors.append("Benutzername muss mindestens 3 Zeichen haben")

            if not password or len(password) < 8:
                errors.append("Passwort muss mindestens 8 Zeichen haben")

            if password != password_confirm:
                errors.append("Passwörter stimmen nicht überein")

            if not birth_date:
                errors.append("Geburtsdatum ist erforderlich")

            if not verification_code or len(verification_code) != 6:
                errors.append("6-stelliger Bestätigungscode erforderlich")

            # Ergebnis anzeigen
            if errors:
                st.error("**Fehler bei der Registrierung:**")
                for error in errors:
                    st.error(f"• {error}")
            else:
                st.success("✓ Registrierung erfolgreich!")
                st.balloons()
                st.json({
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "phone": phone,
                    "birth_date": str(birth_date),
                    "username": username,
                    "verification_code": verification_code
                })

# Sidebar mit Informationen
with st.sidebar:
    st.header("ℹ️ Informationen")

    st.markdown("""
    ### Form Components

    Diese Demo zeigt alle erweiterten Formular-Komponenten:

    **Input**
    - Floating Labels
    - Prefix/Suffix Icons
    - Validierung (Error/Success States)
    - Verschiedene Typen (text, email, password, number, tel, url)

    **DatePicker**
    - Datumsauswahl
    - Min/Max Einschränkungen
    - Validierung

    **Calendar**
    - Monatsansicht
    - Datumsauswahl
    - Einschränkungen

    **Input OTP**
    - One-Time-Password Eingabe
    - Mehrere Ziffern
    - Automatischer Focus

    ### Features

    ✓ Floating Labels
    ✓ Icon Support
    ✓ Validierung mit visuellem Feedback
    ✓ Error/Success States
    ✓ Responsive Design
    ✓ Theme-Support
    ✓ Accessibility
    """)

    st.markdown("---")

    st.markdown("""
    ### Verwendung

    ```python
    from components.form_components import input_field

    email = input_field(
        label="E-Mail",
        type="email",
        prefix_icon="📧",
        required=True
    )
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #71717a; font-size: 0.875rem;'>
    shadcn/ui Form Components für Streamlit | Demo
</div>
""", unsafe_allow_html=True)
