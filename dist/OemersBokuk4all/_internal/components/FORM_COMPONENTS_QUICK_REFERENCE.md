# Form Components Quick Reference

Schnellreferenz für shadcn/ui Form-Komponenten.

## Komponenten-Übersicht

| Komponente | Beschreibung | Key Features |
|------------|--------------|--------------|
| **Input** | Erweiterte Input-Felder | Floating Labels, Icons, Validierung |
| **DatePicker** | Datumsauswahl | Min/Max Datum, Validierung |
| **Calendar** | Kalender-Ansicht | Monatsansicht, Datumsauswahl |
| **InputOTP** | OTP-Eingabe | Mehrere Ziffern, Auto-Focus |

## Quick Start

### Input Field

```python
from components.form_components import input_field

# Basic
value = input_field(label="Name", placeholder="Ihr Name")

# Mit Icon
email = input_field(
    label="E-Mail",
    type="email",
    prefix_icon="📧"
)

# Mit Validierung
password = input_field(
    label="Passwort",
    type="password",
    error="Passwort zu kurz" if len(password) < 8 else None
)
```

### DatePicker

```python
from components.form_components import date_picker
from datetime import date

# Basic
selected = date_picker(label="Geburtsdatum")

# Mit Einschränkungen
appointment = date_picker(
    label="Termin",
    min_date=date.today(),
    max_date=date.today() + timedelta(days=30)
)
```

### Calendar

```python
from components.form_components import calendar

# Basic
selected = calendar(selected_date=date.today())

# Mit Einschränkungen
selected = calendar(
    min_date=date.today() - timedelta(days=7),
    max_date=date.today() + timedelta(days=7)
)
```

### Input OTP

```python
from components.form_components import input_otp

# 6-Digit Code
code = input_otp(
    label="Bestätigungscode",
    length=6,
    help_text="Code aus E-Mail"
)

# 4-Digit PIN
pin = input_otp(label="PIN", length=4)
```

## Parameter-Übersicht

### Input

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `label` | str | - | Label-Text (erforderlich) |
| `value` | str | "" | Aktueller Wert |
| `placeholder` | str | None | Placeholder-Text |
| `type` | str | "text" | Input-Typ (text, email, password, number, tel, url) |
| `prefix_icon` | str | None | Icon vor Input |
| `suffix_icon` | str | None | Icon nach Input |
| `help_text` | str | None | Hilfetext |
| `error` | str | None | Error-Nachricht |
| `success` | str | None | Success-Nachricht |
| `required` | bool | False | Pflichtfeld |
| `disabled` | bool | False | Deaktiviert |
| `max_length` | int | None | Max. Zeichenlänge |
| `key` | str | None | Eindeutiger Key |

### DatePicker

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `label` | str | - | Label-Text (erforderlich) |
| `value` | date | None | Aktuelles Datum |
| `min_date` | date | None | Minimales Datum |
| `max_date` | date | None | Maximales Datum |
| `help_text` | str | None | Hilfetext |
| `error` | str | None | Error-Nachricht |
| `required` | bool | False | Pflichtfeld |
| `disabled` | bool | False | Deaktiviert |
| `key` | str | None | Eindeutiger Key |

### Calendar

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `selected_date` | date | None | Ausgewähltes Datum |
| `min_date` | date | None | Minimales Datum |
| `max_date` | date | None | Maximales Datum |
| `key` | str | None | Eindeutiger Key |

### InputOTP

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `label` | str | - | Label-Text (erforderlich) |
| `length` | int | 6 | Anzahl Ziffern |
| `help_text` | str | None | Hilfetext |
| `error` | str | None | Error-Nachricht |
| `key` | str | None | Eindeutiger Key |

## Validierungs-Beispiele

### Email-Validierung

```python
email = input_field(label="E-Mail", type="email")

if email and "@" not in email:
    st.error("Ungültige E-Mail-Adresse")
```

### Passwort-Validierung

```python
password = input_field(label="Passwort", type="password")

if password:
    if len(password) < 8:
        st.error("Mindestens 8 Zeichen erforderlich")
    elif not any(c.isupper() for c in password):
        st.warning("Mindestens 1 Großbuchstabe empfohlen")
    elif not any(c.isdigit() for c in password):
        st.warning("Mindestens 1 Zahl empfohlen")
    else:
        st.success("✓ Starkes Passwort")
```

### Datums-Validierung

```python
selected = date_picker(label="Termin")

if selected and selected < date.today():
    st.error("Datum muss in der Zukunft liegen")
```

### OTP-Validierung

```python
code = input_otp(label="Code", length=6)

if code:
    if len(code) != 6:
        st.warning(f"Bitte alle 6 Ziffern eingeben ({len(code)}/6)")
    elif not code.isdigit():
        st.error("Nur Zahlen erlaubt")
    else:
        st.success("✓ Code vollständig")
```

## Vollständiges Formular

```python
from components.form_components import input_field, date_picker, input_otp
from datetime import date

with st.form("registration"):
    # Persönliche Daten
    col1, col2 = st.columns(2)
    with col1:
        first_name = input_field(label="Vorname", required=True)
    with col2:
        last_name = input_field(label="Nachname", required=True)

    # Kontakt
    email = input_field(
        label="E-Mail",
        type="email",
        prefix_icon="📧",
        required=True
    )

    # Geburtsdatum
    birth_date = date_picker(
        label="Geburtsdatum",
        max_date=date.today(),
        required=True
    )

    # Account
    username = input_field(
        label="Benutzername",
        help_text="Mindestens 3 Zeichen"
    )

    password = input_field(
        label="Passwort",
        type="password",
        prefix_icon="🔒",
        help_text="Mindestens 8 Zeichen"
    )

    # Verifizierung
    code = input_otp(
        label="Bestätigungscode",
        length=6
    )

    # Submit
    submitted = st.form_submit_button("Registrieren")

    if submitted:
        # Validierung hier
        if all([first_name, last_name, email, birth_date, username, password, code]):
            st.success("✓ Registrierung erfolgreich!")
        else:
            st.error("Bitte alle Felder ausfüllen")
```

## Error States

```python
# Input mit Error
email = input_field(
    label="E-Mail",
    error="Diese E-Mail ist bereits registriert"
)

# Input mit Success
username = input_field(
    label="Benutzername",
    success="✓ Benutzername verfügbar"
)

# DatePicker mit Error
date = date_picker(
    label="Datum",
    error="Datum muss in der Zukunft liegen"
)

# OTP mit Error
code = input_otp(
    label="Code",
    error="Ungültiger Code"
)
```

## Icons

Verwende Unicode-Emojis oder HTML-Entities:

```python
# Emojis
email = input_field(label="E-Mail", prefix_icon="📧")
phone = input_field(label="Telefon", prefix_icon="📱")
password = input_field(label="Passwort", prefix_icon="🔒")
search = input_field(label="Suche", prefix_icon="🔍")
user = input_field(label="Benutzer", prefix_icon="👤")

# HTML-Entities (in HTML-Kontext)
# &#128231; = 📧
# &#128241; = 📱
# &#128274; = 🔒
```

## Theming

Alle Komponenten verwenden Theme-Tokens:

```python
# Theme-Manager initialisieren
from theming import ThemeManager

theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# Komponenten mit Theme
email = input_field(
    label="E-Mail",
    theme_manager=theme_manager
)
```

## Accessibility

Alle Komponenten sind WCAG 2.1 AA konform:

- ✓ Keyboard-Navigation (Tab, Shift+Tab)
- ✓ Screen-Reader-Support
- ✓ Focus-Indikatoren
- ✓ Ausreichender Kontrast
- ✓ ARIA-Labels

## Best Practices

1. **Verwende aussagekräftige Labels**
   ```python
   # Gut
   email = input_field(label="E-Mail-Adresse")

   # Schlecht
   email = input_field(label="Email")
   ```

2. **Gib hilfreiche Hinweise**
   ```python
   password = input_field(
       label="Passwort",
       help_text="Mindestens 8 Zeichen, 1 Großbuchstabe, 1 Zahl"
   )
   ```

3. **Validiere während der Eingabe**
   ```python
   email = input_field(label="E-Mail", type="email")
   if email and "@" not in email:
       st.error("Ungültige E-Mail")
   ```

4. **Verwende Icons für bessere UX**
   ```python
   email = input_field(label="E-Mail", prefix_icon="📧")
   ```

5. **Markiere Pflichtfelder**
   ```python
   name = input_field(label="Name", required=True)
   ```

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Floating Label funktioniert nicht | Theme-Manager initialisieren |
| Icons werden nicht angezeigt | Unicode-Emojis verwenden |
| Validierung funktioniert nicht | `st.form()` für Submit-Validierung |
| DatePicker falsches Format | `datetime.date` Objekte verwenden |
| OTP-Felder nicht fokussierbar | Eindeutige Keys verwenden |

## Weitere Ressourcen

- **Demo**: `demo_form_components.py`
- **Vollständige Referenz**: `components/FORM_COMPONENTS_REFERENCE.py`
- **Tests**: `tests/test_form_components.py`
- **Theme-System**: `theming/THEME_SELECTOR_REFERENCE.md`

## Support

Bei Fragen oder Problemen:
1. Siehe vollständige Referenz: `FORM_COMPONENTS_REFERENCE.py`
2. Führe Demo aus: `streamlit run demo_form_components.py`
3. Prüfe Tests: `pytest tests/test_form_components.py`
