"""
FORM COMPONENTS REFERENCE
=========================

Vollständige Referenz für shadcn/ui Form-Komponenten.

KOMPONENTEN-ÜBERSICHT
---------------------

1. Input - Erweiterte Input-Felder mit Floating Labels
2. DatePicker - Datumsauswahl-Komponente
3. Calendar - Kalender-Komponente
4. InputOTP - One-Time-Password Eingabe

FEATURES
--------

✓ Floating Labels
✓ Prefix/Suffix Icons
✓ Validierung mit visuellem Feedback
✓ Error/Success States
✓ Responsive Design
✓ Theme-Support
✓ Accessibility (WCAG 2.1 AA)

═══════════════════════════════════════════════════════════════════

1. INPUT COMPONENT
==================

Erweiterte Input-Komponente mit Floating Labels, Icons und Validierung.

BASIC USAGE
-----------

```python
from components.form_components import Input, input_field

# Klassen-basiert
input_comp = Input(theme_manager=theme_manager)
value = input_comp.render(
    label="Name",
    placeholder="Ihr Name",
    help_text="Geben Sie Ihren vollständigen Namen ein"
)

# Convenience Function
value = input_field(
    label="E-Mail",
    type="email",
    prefix_icon="📧",
    required=True
)
```

PARAMETER
---------

label: str
    Label-Text für das Input-Feld

value: str = ""
    Aktueller Wert des Feldes

placeholder: Optional[str] = None
    Placeholder-Text

type: Literal["text", "email", "password", "number", "tel", "url"] = "text"
    Input-Typ

prefix_icon: Optional[str] = None
    Icon vor dem Input (z.B. Emoji oder Unicode)

suffix_icon: Optional[str] = None
    Icon nach dem Input

help_text: Optional[str] = None
    Hilfetext unter dem Input

error: Optional[str] = None
    Error-Nachricht (zeigt Error-State)

success: Optional[str] = None
    Success-Nachricht (zeigt Success-State)

required: bool = False
    Ob Feld erforderlich ist

disabled: bool = False
    Ob Feld deaktiviert ist

max_length: Optional[int] = None
    Maximale Zeichenlänge

on_change: Optional[Callable] = None
    Callback-Funktion bei Änderung

key: Optional[str] = None
    Eindeutiger Key für die Komponente

RETURNS
-------

str: Eingegebener Wert

BEISPIELE
---------

# Text Input
name = input_field(
    label="Name",
    placeholder="Max Mustermann",
    help_text="Vor- und Nachname"
)

# Email Input mit Icon
email = input_field(
    label="E-Mail",
    type="email",
    prefix_icon="📧",
    placeholder="ihre@email.de",
    required=True
)

# Password Input
password = input_field(
    label="Passwort",
    type="password",
    prefix_icon="🔒",
    help_text="Mindestens 8 Zeichen"
)

# Number Input
age = input_field(
    label="Alter",
    type="number",
    suffix_icon="🎂"
)

# Input mit Error State
username = input_field(
    label="Benutzername",
    error="Dieser Benutzername ist bereits vergeben"
)

# Input mit Success State
username = input_field(
    label="Benutzername",
    value="john_doe",
    success="✓ Benutzername verfügbar"
)

# Input mit Validierung
def validate_email(email):
    if "@" in email and "." in email:
        return None  # Kein Error
    return "Ungültige E-Mail-Adresse"

email = input_field(
    label="E-Mail",
    type="email",
    error=validate_email(st.session_state.get('email', ''))
)

VALIDIERUNG
-----------

# Einfache Validierung
value = input_field(label="Name", required=True)
if not value:
    st.error("Name ist erforderlich")

# Email-Validierung
email = input_field(label="E-Mail", type="email")
if email and "@" not in email:
    st.error("Ungültige E-Mail")

# Längen-Validierung
password = input_field(label="Passwort", type="password")
if password and len(password) < 8:
    st.warning("Passwort zu kurz")

═══════════════════════════════════════════════════════════════════

2. DATEPICKER COMPONENT
========================

Moderne DatePicker-Komponente für Datumsauswahl.

BASIC USAGE
-----------

```python
from components.form_components import DatePicker, date_picker
from datetime import date

# Klassen-basiert
picker = DatePicker(theme_manager=theme_manager)
selected = picker.render(
    label="Geburtsdatum",
    max_date=date.today()
)

# Convenience Function
selected = date_picker(
    label="Termin",
    min_date=date.today(),
    help_text="Wählen Sie einen Termin"
)
```

PARAMETER
---------

label: str
    Label-Text für den DatePicker

value: Optional[date] = None
    Aktuell ausgewähltes Datum

min_date: Optional[date] = None
    Minimales auswählbares Datum

max_date: Optional[date] = None
    Maximales auswählbares Datum

help_text: Optional[str] = None
    Hilfetext unter dem DatePicker

error: Optional[str] = None
    Error-Nachricht

required: bool = False
    Ob Feld erforderlich ist

disabled: bool = False
    Ob Feld deaktiviert ist

key: Optional[str] = None
    Eindeutiger Key

RETURNS
-------

Optional[date]: Ausgewähltes Datum oder None

BEISPIELE
---------

# Basic DatePicker
birth_date = date_picker(
    label="Geburtsdatum",
    max_date=date.today()
)

# DatePicker mit Einschränkungen
from datetime import timedelta

appointment = date_picker(
    label="Termin",
    min_date=date.today(),
    max_date=date.today() + timedelta(days=30),
    help_text="Termin in den nächsten 30 Tagen"
)

# DatePicker mit Error
expiry = date_picker(
    label="Ablaufdatum",
    error="Datum muss in der Zukunft liegen",
    required=True
)

# DatePicker mit Validierung
selected = date_picker(label="Datum")
if selected and selected < date.today():
    st.error("Datum muss in der Zukunft liegen")

VALIDIERUNG
-----------

# Zukunftsdatum prüfen
selected = date_picker(label="Termin")
if selected and selected < date.today():
    st.error("Datum muss in der Zukunft liegen")

# Altersberechnung
birth_date = date_picker(label="Geburtsdatum", max_date=date.today())
if birth_date:
    age = (date.today() - birth_date).days // 365
    if age < 18:
        st.warning("Sie müssen mindestens 18 Jahre alt sein")

═══════════════════════════════════════════════════════════════════

3. CALENDAR COMPONENT
======================

Kalender-Komponente mit Monatsansicht für Datumsauswahl.

BASIC USAGE
-----------

```python
from components.form_components import Calendar, calendar
from datetime import date

# Klassen-basiert
cal = Calendar(theme_manager=theme_manager)
selected = cal.render(
    selected_date=date.today()
)

# Convenience Function
selected = calendar(
    selected_date=date.today(),
    min_date=date.today() - timedelta(days=7)
)
```

PARAMETER
---------

selected_date: Optional[date] = None
    Aktuell ausgewähltes Datum

min_date: Optional[date] = None
    Minimales auswählbares Datum

max_date: Optional[date] = None
    Maximales auswählbares Datum

key: Optional[str] = None
    Eindeutiger Key

RETURNS
-------

Optional[date]: Ausgewähltes Datum

BEISPIELE
---------

# Basic Calendar
selected = calendar(
    selected_date=date.today()
)

# Calendar mit Einschränkungen
from datetime import timedelta

selected = calendar(
    selected_date=date.today(),
    min_date=date.today() - timedelta(days=7),
    max_date=date.today() + timedelta(days=7)
)

# Calendar für Datumsbereich
start_date = calendar(
    selected_date=date.today(),
    key="start_date"
)
end_date = calendar(
    selected_date=date.today(),
    min_date=start_date,
    key="end_date"
)

═══════════════════════════════════════════════════════════════════

4. INPUT OTP COMPONENT
=======================

One-Time-Password (OTP) Eingabe-Komponente.

BASIC USAGE
-----------

```python
from components.form_components import InputOTP, input_otp

# Klassen-basiert
otp = InputOTP(theme_manager=theme_manager)
code = otp.render(
    label="Bestätigungscode",
    length=6
)

# Convenience Function
code = input_otp(
    label="SMS-Code",
    length=6,
    help_text="Code aus SMS"
)
```

PARAMETER
---------

label: str
    Label-Text für den OTP-Input

length: int = 6
    Anzahl der Ziffern

help_text: Optional[str] = None
    Hilfetext unter dem Input

error: Optional[str] = None
    Error-Nachricht

key: Optional[str] = None
    Eindeutiger Key

RETURNS
-------

str: Eingegebener OTP-Code als String

BEISPIELE
---------

# 6-Digit OTP
code = input_otp(
    label="Bestätigungscode",
    length=6,
    help_text="Code aus E-Mail"
)

# 4-Digit PIN
pin = input_otp(
    label="PIN",
    length=4,
    help_text="4-stelliger PIN"
)

# OTP mit Validierung
code = input_otp(
    label="Verifizierungscode",
    length=6
)

if code and len(code) == 6:
    if code.isdigit():
        st.success("✓ Code vollständig")
    else:
        st.error("Nur Zahlen erlaubt")
elif code:
    st.warning(f"Bitte alle 6 Ziffern eingeben ({len(code)}/6)")

# OTP mit Error
code = input_otp(
    label="Code",
    length=6,
    error="Ungültiger Code"
)

VALIDIERUNG
-----------

# Vollständigkeit prüfen
code = input_otp(label="Code", length=6)
if code and len(code) != 6:
    st.error("Bitte alle 6 Ziffern eingeben")

# Nur Zahlen prüfen
if code and not code.isdigit():
    st.error("Nur Zahlen erlaubt")

# Code verifizieren
VALID_CODE = "123456"
if code == VALID_CODE:
    st.success("✓ Code korrekt")
elif code and len(code) == 6:
    st.error("✗ Ungültiger Code")

═══════════════════════════════════════════════════════════════════

VOLLSTÄNDIGES FORMULAR-BEISPIEL
================================

```python
from components.form_components import (
    input_field, date_picker, input_otp
)
from datetime import date

# Formular mit allen Komponenten
with st.form("registration"):
    st.header("Registrierung")

    # Persönliche Daten
    col1, col2 = st.columns(2)
    with col1:
        first_name = input_field(
            label="Vorname",
            required=True,
            key="firstname"
        )
    with col2:
        last_name = input_field(
            label="Nachname",
            required=True,
            key="lastname"
        )

    # Kontaktdaten
    email = input_field(
        label="E-Mail",
        type="email",
        prefix_icon="📧",
        required=True,
        key="email"
    )

    phone = input_field(
        label="Telefon",
        type="tel",
        prefix_icon="📱",
        key="phone"
    )

    # Geburtsdatum
    birth_date = date_picker(
        label="Geburtsdatum",
        max_date=date.today(),
        required=True,
        key="birthdate"
    )

    # Account
    username = input_field(
        label="Benutzername",
        help_text="Mindestens 3 Zeichen",
        required=True,
        key="username"
    )

    password = input_field(
        label="Passwort",
        type="password",
        prefix_icon="🔒",
        help_text="Mindestens 8 Zeichen",
        required=True,
        key="password"
    )

    # Verifizierung
    code = input_otp(
        label="Bestätigungscode",
        length=6,
        help_text="Code aus E-Mail",
        key="verification"
    )

    # Submit
    submitted = st.form_submit_button("Registrieren")

    if submitted:
        # Validierung
        errors = []

        if not first_name or not last_name:
            errors.append("Name erforderlich")

        if not email or "@" not in email:
            errors.append("Gültige E-Mail erforderlich")

        if not username or len(username) < 3:
            errors.append("Benutzername zu kurz")

        if not password or len(password) < 8:
            errors.append("Passwort zu kurz")

        if not birth_date:
            errors.append("Geburtsdatum erforderlich")

        if not code or len(code) != 6:
            errors.append("6-stelliger Code erforderlich")

        # Ergebnis
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("✓ Registrierung erfolgreich!")
```

═══════════════════════════════════════════════════════════════════

STYLING UND THEMING
===================

Alle Form-Komponenten verwenden Theme-Tokens:

```python
# Theme-Tokens für Form-Komponenten
colors.background      # Hintergrundfarbe
colors.foreground      # Textfarbe
colors.border          # Border-Farbe
colors.input           # Input-Hintergrund
colors.primary         # Primärfarbe (Focus)
colors.error           # Error-Farbe
colors.success         # Success-Farbe
colors.muted_foreground # Muted Text

borders.border_radius_md # Border-Radius
spacing.spacing_2       # Kleiner Abstand
spacing.spacing_3       # Mittlerer Abstand
animations.transition_base # Transition-Dauer
```

Custom CSS hinzufügen:

```python
# Nicht direkt unterstützt, aber über Theme-Manager möglich
# Siehe theming/theme_manager.py für Details
```

═══════════════════════════════════════════════════════════════════

ACCESSIBILITY
=============

Alle Komponenten sind WCAG 2.1 AA konform:

✓ Keyboard-Navigation
✓ Screen-Reader-Support
✓ Focus-Indikatoren
✓ Ausreichender Kontrast
✓ ARIA-Labels
✓ Error-Announcements

Keyboard-Shortcuts:

- Tab: Nächstes Feld
- Shift+Tab: Vorheriges Feld
- Enter: Formular absenden
- Escape: Abbrechen

═══════════════════════════════════════════════════════════════════

BEST PRACTICES
==============

1. VALIDIERUNG
--------------

# Validierung während der Eingabe
value = input_field(label="E-Mail", type="email")
if value and "@" not in value:
    st.error("Ungültige E-Mail")

# Validierung beim Submit
with st.form("myform"):
    email = input_field(label="E-Mail")
    submitted = st.form_submit_button("Senden")

    if submitted:
        if not email or "@" not in email:
            st.error("Gültige E-Mail erforderlich")

2. ERROR HANDLING
-----------------

# Error-State direkt in Komponente
email = input_field(
    label="E-Mail",
    error="Diese E-Mail ist bereits registriert"
)

# Error-State mit Session State
if 'email_error' in st.session_state:
    email = input_field(
        label="E-Mail",
        error=st.session_state.email_error
    )

3. REQUIRED FIELDS
------------------

# Required-Flag verwenden
name = input_field(
    label="Name",
    required=True
)

# Validierung
if not name:
    st.error("Name ist erforderlich")

4. HELP TEXT
------------

# Hilfreiche Hinweise geben
password = input_field(
    label="Passwort",
    type="password",
    help_text="Mindestens 8 Zeichen, 1 Großbuchstabe, 1 Zahl"
)

5. ICONS
--------

# Icons für bessere UX
email = input_field(
    label="E-Mail",
    prefix_icon="📧"
)

phone = input_field(
    label="Telefon",
    prefix_icon="📱"
)

═══════════════════════════════════════════════════════════════════

TROUBLESHOOTING
===============

Problem: Floating Label funktioniert nicht
Lösung: Stelle sicher, dass Theme-Manager initialisiert ist

Problem: Icons werden nicht angezeigt
Lösung: Verwende Unicode-Emojis oder HTML-Entities

Problem: Validierung funktioniert nicht
Lösung: Verwende st.form() für Submit-basierte Validierung

Problem: DatePicker zeigt falsches Format
Lösung: Verwende datetime.date Objekte, nicht Strings

Problem: OTP-Felder nicht fokussierbar
Lösung: Verwende eindeutige Keys für jedes Feld

═══════════════════════════════════════════════════════════════════

WEITERE RESSOURCEN
==================

- Demo: demo_form_components.py
- Tests: tests/test_form_components.py
- Dokumentation: components/FORM_COMPONENTS_QUICK_REFERENCE.md
- Theme-System: theming/THEME_SELECTOR_REFERENCE.md

═══════════════════════════════════════════════════════════════════
"""
