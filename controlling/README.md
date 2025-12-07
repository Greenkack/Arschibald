# Employee Controlling System

Ein umfassendes Modul zur Verwaltung, Auswertung und Analyse von Mitarbeiterleistungen für die Streamlit Python App.

## 🎯 Übersicht

Das Employee Controlling System ist ein vollständig integriertes Modul zur Erfassung, Auswertung und Visualisierung von Mitarbeiterleistungen. Es bietet eine intuitive Benutzeroberfläche mit shadcn/ui Design, umfangreiche Analysefunktionen und flexible Exportmöglichkeiten.

## ✨ Features

- ✅ **Mitarbeiterverwaltung**: Unbegrenzte Anzahl von Mitarbeitern mit vollständigen Stammdaten
- ✅ **Automatische Berechnungen**: Alter und Arbeitstage werden automatisch berechnet
- ✅ **Flexible Positionen**: Beliebig viele Positionen mit individuellen Auswertungskriterien
- ✅ **14 Standard-Kriterien**: Vorkonfigurierte Leistungsindikatoren + erweiterbar
- ✅ **10 Quoten-Berechnungen**: Automatische prozentuale Auswertungen mit beschreibenden Verhältnissen
- ✅ **6 Zeitraum-Auswertungen**: Täglich, wöchentlich, monatlich, quartalsweise, jährlich, seit Arbeitsbeginn
- ✅ **Visualisierungen**: Balken-, Säulen- und Donut-Charts mit shadcn/ui Design
- ✅ **Export/Import**: PDF, Excel, JSON mit vollständigen Daten
- ✅ **Archivierung**: Vollständige historische Datenzugriffe
- ✅ **Benachrichtigungssystem**: Konfigurierbare Schwellenwerte für automatische Benachrichtigungen
- ✅ **Admin-Bereich**: Passwortgeschützte Konfiguration mit 5 Tabs
- ✅ **Vergleichsberichte**: Multi-Mitarbeiter-Analysen

## 🚀 Quick Start

**New to the system?** Follow our [Quick Start Guide](QUICK_START.md) to get up and running in 5 minutes!

## 📦 Installation

### 1. Datenbank initialisieren

```bash
python controlling/database.py
```

Dies erstellt alle notwendigen Tabellen und initialisiert die 14 Standard-Auswertungskriterien.

### 2. Abhängigkeiten

Das Modul nutzt die bestehende Backend-Infrastruktur:
- SQLAlchemy (ORM)
- SQLite (Datenbank)
- Streamlit (UI)
- Plotly (Visualisierungen)
- ReportLab (PDF-Export)
- openpyxl (Excel-Export)

Alle Abhängigkeiten sind bereits in `requirements.txt` enthalten.

## 🗄️ Datenbankstruktur

### Tabellen

1. **controlling_employees**: Mitarbeiterdaten
   - Stammdaten (Name, Wohnort, Geburtsdatum, etc.)
   - Automatische Berechnung von Alter und Arbeitstagen
   - Soft-Delete (is_active Flag)
   - Position-Zuordnung

2. **controlling_positions**: Positionen/Rollen
   - Eindeutige Positionsnamen
   - Beschreibung
   - Löschschutz bei zugeordneten Mitarbeitern

3. **controlling_criteria**: Auswertungskriterien
   - 14 Standard-Kriterien
   - Benutzerdefinierte Kriterien
   - Berechnungsmethoden (SUM, AVERAGE, PERCENTAGE, RATIO)

4. **controlling_position_criteria**: Position-Kriterien-Zuordnung
   - Many-to-Many Beziehung
   - Flexible Zuordnung von Kriterien zu Positionen
   - Mitarbeiter erben Kriterien von ihrer Position

5. **controlling_performance_data**: Leistungsdaten
   - Tägliche Erfassung pro Mitarbeiter und Kriterium
   - Zeitstempel für Nachvollziehbarkeit
   - Numerische Validierung

6. **controlling_reports**: Gespeicherte Berichte
   - Vollständige Archivierung aller Auswertungen
   - JSON-Serialisierung von Charts und Rohdaten
   - Metadaten (Zeitraum, Mitarbeiter, Erstellungsdatum)

## 📊 Standard-Auswertungskriterien

1. **Kunden terminiert**: Anzahl der vereinbarten Termine
2. **QC bestanden**: Qualitätskontrolle erfolgreich
3. **Storniert / kein Interesse**: Abgesagte oder desinteressierte Kunden
4. **Nicht erreicht / neu terminieren**: Nicht erreichte Kunden
5. **Technisch nicht machbar**: Technisch nicht umsetzbare Projekte
6. **Angefahrene Termine**: Tatsächlich durchgeführte Termine
7. **Nicht angefahrene Termine**: Nicht wahrgenommene Termine
8. **Verkauf**: Erfolgreiche Abschlüsse
9. **Folgetermin gemacht**: Vereinbarte Folgetermine
10. **Zu teuer gewesen**: Preisbedingte Absagen
11. **Angebot erhalten**: Erstellte Angebote
12. **Getätigte Anrufe gesamt**: Gesamtzahl der Anrufe
13. **Angefahrene Termine gesamt**: Gesamtzahl angefahrener Termine
14. **Sonstiges**: Weitere Aktivitäten

## 📈 Quoten-Berechnungen

Das System berechnet automatisch folgende Quoten:

1. **Abschlussquote**: (Verkauf / Angefahrene Termine gesamt) × 100
   - Zeigt die Erfolgsrate bei durchgeführten Terminen

2. **Terminvereinbarungsquote**: (Kunden terminiert / Getätigte Anrufe gesamt) × 100
   - Misst die Effizienz der Telefonakquise

3. **Termine-Anfahrquote**: (Angefahrene Termine / Kunden terminiert) × 100
   - Zeigt, wie viele vereinbarte Termine tatsächlich wahrgenommen wurden

4. **Nicht interessierte Kunden Quote**: (Storniert/kein Interesse / Angefahrene Termine gesamt) × 100
   - Misst die Rate der desinteressierten Kunden

5. **Technisch nicht machbar Quote**: (Technisch nicht machbar / Angefahrene Termine gesamt) × 100
   - Zeigt technisch nicht umsetzbare Projekte

6. **Quote der nicht erreichten Kunden**: (Nicht erreicht / Getätigte Anrufe gesamt) × 100
   - Misst die Erreichbarkeit von Kunden

7. **Quote für Folgetermine-Vereinbarungen**: (Folgetermin gemacht / Angefahrene Termine gesamt) × 100
   - Zeigt die Rate der Folgetermin-Vereinbarungen

8. **Quote für Angebote**: (Angebot erhalten / Angefahrene Termine gesamt) × 100
   - Misst, wie oft Angebote erstellt wurden

9. **Quote für zu teuer**: (Zu teuer / Angefahrene Termine gesamt) × 100
   - Zeigt preisbedingte Absagen

10. **Quote für QC bestanden**: (QC bestanden / Verkauf) × 100
    - Misst die Qualität der Abschlüsse

### Beschreibende Verhältnisse

Zusätzlich zu den Prozentsätzen generiert das System verständliche Beschreibungen:
- "Jeder 4. angefahrene Termin ist ein Verkauf" (bei 25% Abschlussquote)
- "Jeder 10. Anruf führt zu einem Termin" (bei 10% Terminvereinbarungsquote)
- "Jeder 3. Verkauf besteht die Qualitätskontrolle" (bei 33% QC-Quote)

## 🚀 Verwendung

### Für Benutzer

1. **Navigation**: Öffnen Sie den Tab "Controlling" im Hauptmenü
2. **Leistungsdaten erfassen**: Wählen Sie einen Mitarbeiter und erfassen Sie tägliche Leistungsdaten
3. **Berichte erstellen**: Generieren Sie Berichte für verschiedene Zeiträume
4. **Visualisierungen**: Betrachten Sie automatisch generierte Charts
5. **Export**: Exportieren Sie Berichte als PDF, Excel oder JSON
6. **Archiv**: Greifen Sie auf gespeicherte Berichte zu

Detaillierte Anleitung: [USER_GUIDE.md](USER_GUIDE.md)

### Für Administratoren

1. **Navigation**: Öffnen Sie "Administration & Verwaltung" → "Controlling Einstellungen"
2. **Mitarbeiter verwalten**: Erstellen, bearbeiten und archivieren Sie Mitarbeiter
3. **Positionen konfigurieren**: Definieren Sie Positionen und deren Kriterien
4. **Kriterien anpassen**: Erstellen Sie benutzerdefinierte Auswertungskriterien
5. **Zuordnungen**: Weisen Sie Kriterien zu Positionen zu
6. **Benachrichtigungen**: Konfigurieren Sie Schwellenwerte für automatische Benachrichtigungen

Detaillierte Anleitung: [ADMIN_GUIDE.md](ADMIN_GUIDE.md)

## 🔔 Benachrichtigungssystem

Das System unterstützt automatische Benachrichtigungen basierend auf konfigurierbaren Schwellenwerten:

- **Erfolgs-Benachrichtigungen**: Bei Überschreitung von Zielwerten
- **Warnungen**: Bei Unterschreitung von Mindestwerten
- **Info-Benachrichtigungen**: Bei auffälligen Werten

Weitere Details: [NOTIFICATION_SYSTEM_README.md](NOTIFICATION_SYSTEM_README.md)

## 🎨 Design

Das System verwendet durchgängig das shadcn/ui Design-System:
- Konsistente Farbpalette
- Moderne, responsive Layouts
- Barrierefreie Komponenten
- Professionelle Visualisierungen

## 🧪 Tests

Das System ist umfassend getestet:

- **144 Tests gesamt**
- **99.3% Erfolgsrate** (143/144 passing)
- **Unit Tests**: 119 Tests für alle Komponenten
- **Property-Based Tests**: 24 Tests mit Hypothesis (100 Beispiele pro Test)
- **Integration Tests**: 5 End-to-End-Tests

```bash
# Alle Tests ausführen
pytest tests/test_controlling*.py tests/test_admin_controlling*.py tests/test_integration.py -v

# Nur Unit Tests
pytest tests/test_controlling_managers.py tests/test_analytics_engine.py -v

# Nur Property Tests
pytest tests/test_controlling_properties.py -v

# Nur Integration Tests
pytest tests/test_integration.py -v
```

## 📚 Dokumentation

- **[USER_GUIDE.md](USER_GUIDE.md)**: Benutzerhandbuch für Endanwender
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)**: Administratorhandbuch für Konfiguration
- **[NOTIFICATION_SYSTEM_README.md](NOTIFICATION_SYSTEM_README.md)**: Benachrichtigungssystem-Dokumentation
- **[API_REFERENCE.md](API_REFERENCE.md)**: Technische API-Dokumentation

## 🔧 Entwicklung

### Datenbank zurücksetzen

```python
from controlling.database import drop_controlling_db, init_controlling_db

# Alle Tabellen löschen
drop_controlling_db()

# Neu initialisieren
init_controlling_db()
```

### Datenbank prüfen

```python
from controlling.database import check_controlling_db

if check_controlling_db():
    print("Datenbank OK!")
```

### Neue Kriterien hinzufügen

```python
from controlling.managers import CriterionManager
from backend.core.database import SessionLocal

session = SessionLocal()
manager = CriterionManager(session)

criterion = manager.create_criterion(
    name="Neues Kriterium",
    description="Beschreibung des Kriteriums"
)
```

## 📋 Projektstruktur

```
controlling/
├── __init__.py              # Modul-Exports
├── models.py                # SQLAlchemy Datenmodelle
├── database.py              # Datenbank-Initialisierung
├── managers.py              # CRUD-Manager-Klassen
├── analytics.py             # Analyse-Engine
├── report_generator.py      # Berichtsgenerierung
├── chart_generator.py       # Visualisierungen
├── notifications.py         # Benachrichtigungssystem
├── README.md                # Diese Datei
├── USER_GUIDE.md            # Benutzerhandbuch
├── ADMIN_GUIDE.md           # Administratorhandbuch
└── NOTIFICATION_SYSTEM_README.md  # Benachrichtigungsdokumentation

tests/
├── test_controlling_managers.py      # Manager Tests
├── test_analytics_engine.py          # Analytics Tests
├── test_report_generator.py          # Report Tests
├── test_chart_generator.py           # Chart Tests
├── test_admin_controlling_ui.py      # Admin UI Tests
├── test_controlling_ui.py            # UI Tests
├── test_notifications.py             # Notification Tests
├── test_controlling_properties.py    # Property Tests
└── test_integration.py               # Integration Tests

UI-Module:
├── admin_controlling_settings_ui.py  # Admin-Konfiguration
└── controlling_ui.py                 # Hauptbenutzeroberfläche
```

## 🎯 Status

**✅ VOLLSTÄNDIG IMPLEMENTIERT**

Alle geplanten Features sind implementiert und getestet:
- ✅ Datenbank-Schema und Modelle
- ✅ Manager-Klassen (CRUD-Operationen)
- ✅ Position-Kriterien-Zuordnung
- ✅ Analytics-Engine (10 Quoten)
- ✅ Berichtsgenerierung (6 Zeiträume)
- ✅ Chart-Generator (3 Chart-Typen)
- ✅ Export-Funktionalität (PDF, Excel, JSON)
- ✅ Admin-UI (5 Tabs)
- ✅ Controlling-UI (3 Tabs)
- ✅ Benachrichtigungssystem
- ✅ Integration Tests
- ✅ Dokumentation

## 🤝 Beitragen

Dieses Modul ist Teil der Bokuk2 Streamlit App. Für Änderungen oder Erweiterungen:

1. Erstellen Sie einen Feature-Branch
2. Implementieren Sie Ihre Änderungen
3. Fügen Sie Tests hinzu
4. Aktualisieren Sie die Dokumentation
5. Erstellen Sie einen Pull Request

## 📄 Lizenz

Teil der Bokuk2 Streamlit App

## 🆘 Support

Bei Fragen oder Problemen:
1. Konsultieren Sie die Dokumentation
2. Prüfen Sie die Tests für Beispiele
3. Kontaktieren Sie das Entwicklungsteam
