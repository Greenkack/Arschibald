# Team-Management im Controlling-System

## Übersicht

Das Team-Management-System ermöglicht die Organisation von Mitarbeitern in Teams für bessere Struktur und team-basierte Auswertungen.

## Features

### 1. Team-Verwaltung
- **Teams erstellen**: Organisieren Sie Mitarbeiter in logischen Gruppen
- **Teamleiter festlegen**: Optional kann ein Teamleiter definiert werden
- **Beschreibungen**: Fügen Sie detaillierte Team-Beschreibungen hinzu
- **Aktiv/Inaktiv**: Steuern Sie die Sichtbarkeit von Teams

### 2. Mitarbeiter-Zuordnung
- Mitarbeiter können einem Team zugeordnet werden
- Flexible Zuordnung: Mitarbeiter können auch ohne Team existieren
- Einfache Neuorganisation möglich
- Automatische Team-Statistiken

### 3. Team-Auswertungen
- **Team-Berichte**: Gemeinsame Leistungsauswertung aller Team-Mitglieder
- **Vergleichsberichte**: Vergleich der Mitarbeiter innerhalb eines Teams
- **Visualisierungen**: Diagramme für Team-Performance
- **PDF-Export**: Professionelle Team-Reports zum Download

### 4. Hierarchische Auswertungen
- **Mitarbeiter-Ebene**: Individuelle Leistung
- **Team-Ebene**: Team-Performance
- **Unternehmens-Ebene**: Alle Teams zusammen auswerten

## Verwendung

### Teams verwalten

1. **Navigation**: Admin Panel → Controlling Einstellungen → Tab "👥 Team"

2. **Team erstellen**:
   ```
   - Team-Name eingeben (z.B. "Vertrieb Nord", "Call Center Team A")
   - Optional: Beschreibung hinzufügen
   - Optional: Teamleiter auswählen
   - "Team erstellen" klicken
   ```

3. **Team bearbeiten**:
   - Team in der Liste aufklappen
   - "✏️ Bearbeiten" klicken
   - Änderungen vornehmen
   - "💾 Speichern"

4. **Team löschen**:
   - Nur möglich, wenn keine aktiven Mitglieder zugeordnet sind
   - Team aufklappen
   - "🗑️ Löschen" klicken

### Mitarbeiter zu Team zuordnen

**Beim Erstellen eines neuen Mitarbeiters**:
1. Admin Panel → Controlling Einstellungen → "👤 Mitarbeiter"
2. Formular ausfüllen
3. Im Dropdown "Team (optional)" das gewünschte Team wählen
4. "Mitarbeiter hinzufügen"

**Bestehenden Mitarbeiter zuordnen**:
1. Aktuell über direkte Datenbankbearbeitung oder
2. Mitarbeiter löschen und neu erstellen mit Team-Zuordnung

### Team-Auswertungen erstellen

1. **Navigation**: Controlling → Tab "🏢 Team-Auswertung"

2. **Team auswählen**:
   - Im Dropdown das gewünschte Team wählen
   - Anzahl der Mitglieder wird angezeigt

3. **Team-Statistiken anzeigen** (optional):
   - Button "📊 Team-Statistiken anzeigen"
   - Zeigt Mitgliederanzahl, Positionen, Teamleiter

4. **Bericht erstellen**:
   - Zeitraum wählen (Täglich, Monatlich, etc.)
   - Referenzdatum festlegen
   - "📊 Team-Bericht erstellen"

5. **Bericht ansehen**:
   - Mitarbeiter-Übersicht mit allen Quoten
   - Visualisierungen (Diagramme)
   - PDF-Export möglich

## Datenbank-Schema

### Tabelle: `controlling_teams`
```sql
- id (INTEGER PRIMARY KEY)
- name (VARCHAR(100) UNIQUE)
- description (TEXT)
- team_leader_id (INTEGER FK → controlling_employees.id)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- is_active (BOOLEAN)
```

### Erweiterte Tabelle: `controlling_employees`
```sql
-- Neu hinzugefügt:
- team_id (INTEGER FK → controlling_teams.id)
```

## API / Python-Verwendung

### TeamManager

```python
from controlling.team_manager import TeamManager
from backend.core.database import SessionLocal

db = SessionLocal()
team_manager = TeamManager(db)

# Team erstellen
team = team_manager.create_team(
    name="Vertrieb Süd",
    description="Vertriebsteam für die Südregion",
    team_leader_id=5  # Optional
)

# Teams auflisten
teams = team_manager.list_teams(
    active_only=True,
    include_employee_count=True
)

# Team aktualisieren
team_manager.update_team(
    team_id=1,
    name="Neuer Name",
    is_active=True
)

# Mitarbeiter zu Team zuordnen
team_manager.assign_employee_to_team(
    employee_id=10,
    team_id=1
)

# Team-Mitglieder abrufen
members = team_manager.get_team_members(team_id=1)

# Team-Statistiken
stats = team_manager.get_team_statistics(team_id=1)
print(f"Aktive Mitglieder: {stats['active_members']}")
print(f"Positionen: {stats['positions']}")

db.close()
```

## Migration

### Automatische Migration

```powershell
# Migration ausführen
python controlling/migrations/add_teams.py
```

### Manuelle Schritte (falls erforderlich)

```sql
-- Teams-Tabelle erstellen
CREATE TABLE controlling_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    team_leader_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (team_leader_id) REFERENCES controlling_employees(id)
);

-- Indices
CREATE INDEX ix_controlling_teams_id ON controlling_teams(id);
CREATE INDEX ix_controlling_teams_name ON controlling_teams(name);

-- Team-ID zu Employees hinzufügen
ALTER TABLE controlling_employees ADD COLUMN team_id INTEGER;
CREATE INDEX ix_controlling_employees_team_id ON controlling_employees(team_id);
```

## Best Practices

### Team-Organisation

1. **Sinnvolle Team-Namen**: Verwenden Sie klare, beschreibende Namen
   - ✅ "Call Center Team A", "Vertrieb Norddeutschland"
   - ❌ "Team 1", "Gruppe X"

2. **Team-Größe**: 
   - Optimal: 5-15 Mitarbeiter pro Team
   - Zu klein: Wenig aussagekräftige Auswertungen
   - Zu groß: Unübersichtlich

3. **Teamleiter**:
   - Sollte selbst Mitglied des Teams sein
   - Idealerweise erfahrenster Mitarbeiter

### Auswertungen

1. **Regelmäßige Team-Berichte**:
   - Wöchentlich oder monatlich
   - Vergleich mit vorherigen Perioden
   - Trends erkennen

2. **Vergleichs-Ansichten**:
   - Teams untereinander vergleichen
   - Best Practices identifizieren
   - Schulungsbedarf erkennen

3. **Export**:
   - PDF-Reports für Management
   - Archivierung wichtiger Auswertungen

## Fehlerbehebung

### "Team-Funktionen konnten nicht geladen werden"

**Problem**: ImportError beim Laden des TeamManagers

**Lösung**:
```powershell
# Migration ausführen
python controlling/migrations/add_teams.py

# App neu starten
streamlit run gui.py
```

### Team kann nicht gelöscht werden

**Problem**: "Team hat X aktive Mitarbeiter"

**Lösung**:
1. Alle Mitarbeiter einem anderen Team zuordnen ODER
2. Mitarbeiter aus Team entfernen (team_id = NULL)
3. Dann Team löschen

### Team-Auswertung zeigt keine Daten

**Mögliche Ursachen**:
1. Team hat keine aktiven Mitglieder
2. Mitarbeiter haben keine Leistungsdaten im gewählten Zeitraum
3. Kriterien sind der Position nicht zugeordnet

**Lösung**:
1. Prüfen: Sind aktive Mitarbeiter im Team?
2. Prüfen: Gibt es Leistungsdaten für den Zeitraum?
3. Admin → Zuordnungen: Position-Kriterium-Verknüpfungen prüfen

## Beispiel-Workflow

### Szenario: Neues Vertriebsteam aufbauen

1. **Team erstellen**:
   ```
   Name: "Vertrieb Ost"
   Beschreibung: "Verantwortlich für Berlin, Brandenburg, Sachsen"
   Teamleiter: Max Mustermann (erfahrener Vertriebsmitarbeiter)
   ```

2. **Mitarbeiter zuordnen**:
   - 10 Call Agents dem Team zuordnen
   - 2 Closer dem Team zuordnen
   - Teamleiter ist selbst auch Closer

3. **Erste Auswertung** (nach 1 Monat):
   ```
   Zeitraum: Monatlich
   Referenzdatum: 31.01.2025
   ```

4. **Ergebnisse analysieren**:
   - Welche Mitarbeiter haben die besten Quoten?
   - Wo gibt es Schulungsbedarf?
   - Vergleich mit anderen Teams

5. **Maßnahmen ableiten**:
   - Top-Performer als Mentoren einsetzen
   - Schwächere Mitarbeiter schulen
   - Best Practices dokumentieren

## Zukunfts-Features (geplant)

- [ ] Team-basierte Ranglisten
- [ ] Team-Ziele und KPIs
- [ ] Automatische Team-Benachrichtigungen
- [ ] Team-Performance-Trends
- [ ] Inter-Team-Wettbewerbe
- [ ] Team-Dashboard mit Live-Daten
- [ ] Export nach Excel für Team-Berichte
- [ ] Team-Kalender für Auswertungsperioden

## Support

Bei Fragen oder Problemen:
1. Logs prüfen: `logs/app_YYYY-MM-DD.log`
2. Admin Panel → Core Status → System-Checks
3. Dokumentation konsultieren
4. Entwickler kontaktieren
