# CRM Calendar UI – Logik-Extraktion (crm_calendar_ui.py)

Stand: 2025-09-12

## Zweck und Überblick

Das Modul `crm_calendar_ui.py` stellt eine Kalenderoberfläche für Termine und Erinnerungen bereit:

- Monatsansicht mit Tages-Grid und Terminzusammenfassung pro Tag
- Formular zur Erstellung neuer Termine
- Listenansicht mit Filtern (Typ, Zeitraum, Status)
- CRM-Verknüpfung: optionaler Bezug zu Kunden (crm_customers)

## Datenmodell: crm_appointments

Die Tabelle wird on-demand erstellt:

- id INTEGER PRIMARY KEY AUTOINCREMENT
- title TEXT NOT NULL
- type TEXT NOT NULL (z. B. consultation, site_visit, installation, follow_up, reminder, maintenance)
- appointment_date TIMESTAMP NOT NULL (ISO-String)
- duration_minutes INTEGER DEFAULT 60
- customer_id INTEGER NULL (FK auf crm_customers.id)
- location TEXT, notes TEXT
- reminder_minutes INTEGER DEFAULT 60
- status TEXT DEFAULT 'scheduled' (scheduled|completed|cancelled)
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Kernklassen und -Methoden

- Klasse CRMCalendar
  - appointment_types: Mapping der Termintypen auf Name, Farbe, Icon
  - render_calendar_interface(texts)
    - Rendert Tabs: Kalenderansicht, Neuer Termin, Terminliste
    - Prüft DB-Verfügbarkeit
  - _render_calendar_view()
    - Monatliche Navigation (vorheriger/nächster Monat, Heute)
    - _render_calendar_grid(current_date)
  - _render_calendar_grid(current_date)
    - Lädt Monats-Termine via _get_appointments_for_month
    - Rendert Wochentage-Header, Wochen und Tageszellen
    - Zeigt pro Tag bis zu zwei Termine mit Typ-Icon und gekürztem Titel
  - _render_new_appointment_form()
    - Formular: Titel, Typ, Datum, Uhrzeit, Dauer, Kunde (optional), Ort, Erinnerung, Notizen
    - Kundenliste via database.get_all_active_customers() (falls verfügbar)
    - Speichert per _create_appointment
  - _render_appointment_list()
    - Filter: Typ, Zeitraum (upcoming|today|this_week|this_month|all), Status
    - Listet gefilterte Termine mit _render_appointment_card
  - _render_appointment_card(appointment)
    - Zeigt Titel, Kunde, Ort, Datum/Uhrzeit, Status, Dauer
    - Buttons: Bearbeiten (Platzhalter), Löschen → _delete_appointment
  - _get_appointments_for_month(year, month) -> List[Dict]
  - _get_filtered_appointments(filter_type, filter_period, filter_status) -> List[Dict]
  - _create_appointment(appointment_data) -> bool
  - _delete_appointment(appointment_id) -> bool

## Contracts

- appointment_data-Eingaben: title:str, type:str, appointment_date:datetime, duration_minutes:int,
  customer_id:Optional[int], location:str, notes:str, reminder_minutes:int, status:str
- Persistenz: appointment_date wird als ISO-String gespeichert/geladen (datetime.fromisoformat)
- Rückgabe-Objekte (Termine) enthalten zusätzlich 'customer_name' (First+Last), falls verknüpft

## Edge Cases und Fehlerbehandlung

- DATABASE_AVAILABLE False → UI zeigt Fehler, keine Aktionen möglich
- create/select/joins in Funktionen sind try/except-geschützt; bei Fehlern wird geloggt und leere Liste/False zurückgegeben
- Kalender-Rendering: Tage ohne Termine werden als leeres Feld mit Day-Header gerendert

## Migration (Electron/TypeScript)

- Lead/Termin Service vorschlagen:
  - AppointmentService: listByMonth(year,month), filter({type,period,status}), create, delete
  - Optionaler CustomerService: listActive für Kunden-Auswahl
- Datum/Zeit: Speicherung als ISO-Strings; Frontend wandelt in Date-Objekte
- Kanban/Drag&Drop für Termine als Erweiterung (später)
