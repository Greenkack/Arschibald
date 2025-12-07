# Agentname-Integration im Controlling-System

## Übersicht
Die Agentname-Funktionalität ermöglicht es, Vertriebsmitarbeitern einen optionalen "Agentname" zuzuweisen, der in PDF-Dokumenten erscheinen kann.

## Implementierung

### 1. Datenbank-Erweiterung
- **Tabelle**: `controlling_employees`
- **Neue Spalte**: `agent_name` (VARCHAR(100), nullable)
- **Migration**: Automatisch beim nächsten App-Start über SQLAlchemy

### 2. Model-Änderungen
**Datei**: `controlling/models.py`
```python
class Employee(Base):
    # ... existing fields ...
    agent_name = Column(String(100), nullable=True)  # Agentname für PDF-Generierung
```

### 3. Manager-Änderungen
**Datei**: `controlling/managers.py`
- `create_employee()` akzeptiert optionalen `agent_name` Parameter
- `update_employee()` kann `agent_name` aktualisieren
- Beide Funktionen validieren und trimmen den Input

### 4. UI-Änderungen
**Datei**: `admin_controlling_settings_ui.py`
- Neues Eingabefeld "Agentname (optional)" im Formular "Mitarbeiter hinzufügen"
- Anzeige des Agentnames in der Mitarbeiterliste
- Fallback: "Nicht angegeben" wenn leer

### 5. PDF-Integration

#### Placeholder-System
**Datei**: `pdf_template_engine/placeholders.py`
```python
PLACEHOLDER_MAPPING.update({
    "agent_name": "agent_name",
    "Agentname": "agent_name",
})
```

#### PDF-Generator
**Datei**: `pdf_generator.py`
- Neuer Platzhalter: `[Agentname]`
- Wird in `_replace_placeholders()` aufgelöst
- Kann in Anschreiben, Deckblättern und allen PDF-Texten verwendet werden

#### Utility-Funktionen
**Datei**: `controlling/utils.py`
```python
# Agent-Name aus Datenbank laden
agent_name = get_agent_name_by_employee_id(employee_id=1)

# Customer-Data anreichern
enriched_data = enrich_customer_data_with_agent_name(
    customer_data={'name': 'Max Mustermann'},
    employee_id=1
)
```

## Verwendung

### 1. Mitarbeiter mit Agentname anlegen
1. Navigiere zu: **Admin Panel** → **Controlling Einstellungen** → **Mitarbeiter**
2. Klicke auf "Neuen Mitarbeiter hinzufügen"
3. Fülle alle Pflichtfelder aus (Vorname, Nachname, Wohnort, etc.)
4. Optional: Gib einen **Agentname** ein (z.B. "Agent Schmidt", "Verkaufsberater Müller")
5. Klicke auf "Mitarbeiter hinzufügen"

### 2. PDF-Platzhalter verwenden
In PDF-Textvorlagen (Anschreiben, etc.):
```
Sehr geehrter Kunde,

Ihr persönlicher Ansprechpartner: [Agentname]

Mit freundlichen Grüßen,
[Ihr Name/Firmenname]
```

### 3. Programmtische Integration
```python
from controlling.utils import enrich_customer_data_with_agent_name

# Vor PDF-Generierung
customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com'
}

# Anreichern mit Agentname
customer_data = enrich_customer_data_with_agent_name(
    customer_data,
    employee_id=session_state.get('selected_employee_id')
)

# Jetzt enthält customer_data['agent_name'] den Wert
generate_offer_pdf(customer_data=customer_data, ...)
```

## Migration bestehender Daten

### Automatische Migration
Wenn die `agent_name` Spalte noch nicht existiert, führe das Migrations-Script aus:

```bash
python migrate_add_agent_name.py
```

Das Script führt automatisch aus:
1. **Methode 1 (SQL)**: Fügt die Spalte mit `ALTER TABLE` hinzu
2. **Methode 2 (SQLAlchemy)**: Aktualisiert alle Tabellen-Strukturen

### Manuelle Migration (falls erforderlich)
Falls das Script nicht funktioniert, kannst du die Migration manuell durchführen:

```sql
ALTER TABLE controlling_employees ADD COLUMN agent_name VARCHAR(100);
```

### Nach der Migration
- ✅ Spalte `agent_name` ist in `controlling_employees` verfügbar
- ✅ Alle bestehenden Mitarbeiter haben `agent_name = NULL`
- ✅ Die UI zeigt "Nicht angegeben" für NULL-Werte
- ✅ PDF-Platzhalter `[Agentname]` wird als leerer String ersetzt
- ✅ Keine Funktionalität wird beeinträchtigt

### Verifizierung
Prüfe ob die Migration erfolgreich war:

```python
python -c "from controlling.managers import EmployeeManager; from backend.core.database import SessionLocal; db = SessionLocal(); em = EmployeeManager(db); employees = em.list_employees(); print(f'Erfolg! {len(employees)} Mitarbeiter geladen'); db.close()"
```

Alle bestehenden Mitarbeiter haben `agent_name = NULL`. Dies ist kein Problem:
- Die UI zeigt "Nicht angegeben"
- PDF-Platzhalter `[Agentname]` wird als leerer String ersetzt
- Keine Funktionalität wird beeinträchtigt

## Sicherheit & Validierung
- ✅ **Nullable**: Agentname ist optional, kein Zwang zur Angabe
- ✅ **Validation**: Input wird getrimmt und bereinigt
- ✅ **Backward Compatible**: Bestehende PDFs ohne Agentname funktionieren weiterhin
- ✅ **Type Safe**: SQLAlchemy-Model mit korrekten Typen
- ✅ **Error Handling**: Robuste Fehlerbehandlung in utils.py

## Testen

### Manueller Test
1. Starte die App: `streamlit run gui.py`
2. Gehe zu Admin Panel → Controlling Einstellungen
3. Erstelle einen Testmitarbeiter mit Agentname
4. Prüfe Anzeige in der Mitarbeiterliste
5. Generiere ein PDF mit `[Agentname]` Platzhalter

### Automatisierter Test
```python
# Test Employee Model
from controlling.models import Employee
emp = Employee(
    first_name="Test",
    last_name="User",
    agent_name="Agent Test",
    city="Berlin",
    birth_date=date(1990, 1, 1),
    position_id=1,
    start_date=date(2024, 1, 1)
)
assert emp.agent_name == "Agent Test"

# Test Utils
from controlling.utils import get_agent_name_by_employee_id
name = get_agent_name_by_employee_id(1)
assert isinstance(name, (str, type(None)))
```

## Beispiel-Workflow

### Szenario: Vertriebsmitarbeiter im PDF anzeigen
1. **Setup**: Erstelle Mitarbeiter "Hans Müller" mit Agentname "Vertriebsberater Nord"
2. **Template**: Erstelle PDF-Textvorlage mit Platzhalter `[Agentname]`
3. **Zuordnung**: Speichere `employee_id` im Session State oder Projekt-Daten
4. **Generierung**: 
   ```python
   customer_data = enrich_customer_data_with_agent_name(
       customer_data,
       employee_id=1
   )
   pdf_bytes = generate_offer_pdf(customer_data=customer_data)
   ```
5. **Ergebnis**: PDF enthält "Vertriebsberater Nord" an allen `[Agentname]` Stellen

## Troubleshooting

### Problem: Agentname erscheint nicht im PDF
- ✅ Prüfe, ob `customer_data['agent_name']` gesetzt ist
- ✅ Prüfe, ob `[Agentname]` Platzhalter korrekt geschrieben ist
- ✅ Prüfe Logs: `logger.info(f"Added agent_name '{agent_name}' to customer_data")`

### Problem: Mitarbeiter ohne Agentname
- ✅ Normal: Agentname ist optional
- ✅ UI zeigt "Nicht angegeben"
- ✅ PDF-Platzhalter wird als "" ersetzt

### Problem: Datenbank-Migration
Falls `agent_name` Spalte fehlt:
```python
from controlling.database import init_controlling_db
init_controlling_db()  # Erstellt fehlende Spalten
```

## Dateien-Übersicht

| Datei | Änderung | Beschreibung |
|-------|----------|--------------|
| `controlling/models.py` | Modified | Neue `agent_name` Spalte |
| `controlling/managers.py` | Modified | CRUD-Operationen für `agent_name` |
| `admin_controlling_settings_ui.py` | Modified | UI-Formular + Anzeige |
| `pdf_template_engine/placeholders.py` | Modified | Placeholder-Mapping |
| `pdf_generator.py` | Modified | `[Agentname]` Platzhalter |
| `controlling/utils.py` | **NEW** | Utility-Funktionen für Integration |
| `AGENTNAME_INTEGRATION.md` | **NEW** | Diese Dokumentation |

## Version
- **Implementiert**: 2024-12-06
- **Author**: GitHub Copilot
- **Status**: ✅ Produktiv

## Weitere Informationen
Siehe auch:
- `controlling/models.py` - Employee Model
- `controlling/managers.py` - EmployeeManager
- `pdf_template_engine/placeholders.py` - Placeholder-System
- `.github/copilot-instructions.md` - Projekt-Dokumentation
