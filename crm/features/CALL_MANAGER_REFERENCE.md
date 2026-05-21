# Call Manager - Developer Reference

## Modul: `crm/features/call_manager.py`

Dieses Modul verwaltet die Anruf-Protokollierung im CRM-System.

## Funktionen

### `ensure_call_fields() -> bool`

Stellt sicher, dass die `crm_activities` Tabelle alle benötigten Felder für Anrufe hat.

**Returns:**
- `True` bei Erfolg
- `False` bei Fehler

**Hinzugefügte Felder:**
- `call_direction` (TEXT): 'incoming' oder 'outgoing'
- `call_phone_number` (TEXT): Telefonnummer
- `call_duration_seconds` (INTEGER): Dauer in Sekunden
- `call_notes` (TEXT): Zusätzliche Notizen

---

### `create_call(customer_id, phone_number, direction, duration_seconds=0, notes="", created_by="System") -> Optional[int]`

Erstellt einen neuen Anruf-Eintrag.

**Parameters:**
- `customer_id` (int): ID des Kunden
- `phone_number` (str): Telefonnummer
- `direction` (str): 'incoming' oder 'outgoing'
- `duration_seconds` (int): Dauer in Sekunden (default: 0)
- `notes` (str): Notizen zum Anruf (default: "")
- `created_by` (str): Name des Erstellers (default: "System")

**Returns:**
- `int`: ID des erstellten Anrufs
- `None`: Bei Fehler oder ungültiger Richtung

**Beispiel:**
```python
call_id = create_call(
    customer_id=123,
    phone_number="+43 123 456789",
    direction="outgoing",
    duration_seconds=300,
    notes="Angebot besprochen",
    created_by="Max Mustermann"
)
```

---

### `get_call(call_id) -> Optional[Dict[str, Any]]`

Ruft einen einzelnen Anruf ab.

**Parameters:**
- `call_id` (int): ID des Anrufs

**Returns:**
- `Dict`: Anrufdaten mit allen Feldern
- `None`: Wenn Anruf nicht gefunden

**Rückgabe-Dictionary:**
```python
{
    "id": 1,
    "customer_id": 123,
    "activity_type": "call",
    "title": "Ausgehender Anruf - +43 123 456789",
    "content": "Dauer: 5:00\n\nNotizen:\nAngebot besprochen",
    "created_by": "Max Mustermann",
    "created_at": "2024-01-15 10:30:00",
    "is_important": False,
    "archived": False,
    "call_direction": "outgoing",
    "call_direction_display": "Ausgehend",
    "call_phone_number": "+43 123 456789",
    "call_duration_seconds": 300,
    "call_duration_formatted": "5:00",
    "call_notes": "Angebot besprochen"
}
```

---

### `get_customer_calls(customer_id, direction=None, include_archived=False, limit=100) -> List[Dict[str, Any]]`

Ruft alle Anrufe eines Kunden ab.

**Parameters:**
- `customer_id` (int): ID des Kunden
- `direction` (Optional[str]): Filter nach Richtung ('incoming' oder 'outgoing')
- `include_archived` (bool): Archivierte Anrufe einschließen (default: False)
- `limit` (int): Maximale Anzahl (default: 100)

**Returns:**
- `List[Dict]`: Liste von Anruf-Dictionaries (sortiert nach Datum, neueste zuerst)

**Beispiel:**
```python
# Alle Anrufe
calls = get_customer_calls(customer_id=123)

# Nur ausgehende
outgoing = get_customer_calls(customer_id=123, direction="outgoing")

# Mit archivierten
all_calls = get_customer_calls(customer_id=123, include_archived=True, limit=50)
```

---

### `update_call(call_id, phone_number=None, direction=None, duration_seconds=None, notes=None) -> bool`

Aktualisiert einen Anruf.

**Parameters:**
- `call_id` (int): ID des Anrufs
- `phone_number` (Optional[str]): Neue Telefonnummer
- `direction` (Optional[str]): Neue Richtung
- `duration_seconds` (Optional[int]): Neue Dauer
- `notes` (Optional[str]): Neue Notizen

**Returns:**
- `True`: Bei Erfolg
- `False`: Bei Fehler

**Hinweis:** Title und Content werden automatisch aktualisiert.

---

### `delete_call(call_id) -> bool`

Löscht einen Anruf.

**Parameters:**
- `call_id` (int): ID des Anrufs

**Returns:**
- `True`: Bei Erfolg
- `False`: Bei Fehler oder Anruf nicht gefunden

---

### `get_call_statistics(customer_id) -> Dict[str, Any]`

Ruft Statistiken über Anrufe eines Kunden ab.

**Parameters:**
- `customer_id` (int): ID des Kunden

**Returns:**
```python
{
    "total": 10,
    "by_direction": {"incoming": 4, "outgoing": 6},
    "incoming": 4,
    "outgoing": 6,
    "total_duration_seconds": 3600,
    "total_duration_formatted": "1:00:00",
    "average_duration_seconds": 360,
    "average_duration_formatted": "6:00",
    "last_call": {
        "date": "2024-01-15 10:30:00",
        "direction": "outgoing",
        "phone_number": "+43 123 456789"
    }
}
```

---

### `format_duration(seconds) -> str`

Formatiert eine Dauer in Sekunden zu einem lesbaren String.

**Parameters:**
- `seconds` (int): Dauer in Sekunden

**Returns:**
- `str`: Formatierter String
  - Unter 1 Stunde: "MM:SS" (z.B. "5:23")
  - Ab 1 Stunde: "H:MM:SS" (z.B. "1:05:30")

**Beispiele:**
```python
format_duration(45)    # "0:45"
format_duration(323)   # "5:23"
format_duration(3665)  # "1:01:05"
format_duration(0)     # "0:00"
format_duration(-100)  # "0:00" (negative werden zu 0)
```

---

### `parse_duration(duration_str) -> int`

Parst einen Dauer-String zu Sekunden.

**Parameters:**
- `duration_str` (str): String im Format "MM:SS" oder "HH:MM:SS"

**Returns:**
- `int`: Dauer in Sekunden
- `0`: Bei ungültigem Format

**Beispiele:**
```python
parse_duration("5:30")     # 330
parse_duration("1:30:00")  # 5400
parse_duration("invalid")  # 0
```

---

### `add_call(...)` 

Alias für `create_call()` - siehe oben.

---

## Konstanten

### `CALL_DIRECTIONS`

```python
CALL_DIRECTIONS = {
    "incoming": "Eingehend",
    "outgoing": "Ausgehend"
}
```

---

## Datenbankschema

### Erweiterte `crm_activities` Tabelle

```sql
CREATE TABLE crm_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_important BOOLEAN DEFAULT 0,
    archived BOOLEAN DEFAULT 0,
    -- Anruf-spezifische Felder:
    call_direction TEXT,
    call_phone_number TEXT,
    call_duration_seconds INTEGER DEFAULT 0,
    call_notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
```

---

## Integration mit anderen Modulen

### Mit `note_manager.py`

Anrufe sind ein Aktivitätstyp und werden in der Timeline angezeigt:

```python
from crm.features.note_manager import get_customer_activities

# Alle Aktivitäten (inkl. Anrufe)
activities = get_customer_activities(customer_id=123)

# Nur Anrufe
calls = get_customer_activities(customer_id=123, activity_type="call")
```

### Mit `database.py`

Verwendet `get_db_connection()` für Datenbankzugriff:

```python
from database import get_db_connection

conn = get_db_connection()
```

---

## Fehlerbehandlung

Alle Funktionen loggen Fehler mit `print()` und geben sichere Rückgabewerte:

- `create_call()`: Gibt `None` zurück bei Fehler
- `get_call()`: Gibt `None` zurück wenn nicht gefunden
- `get_customer_calls()`: Gibt leere Liste `[]` zurück bei Fehler
- `update_call()`: Gibt `False` zurück bei Fehler
- `delete_call()`: Gibt `False` zurück bei Fehler
- `get_call_statistics()`: Gibt leeres Dict `{}` zurück bei Fehler

**Beispiel:**
```python
call_id = create_call(customer_id=123, phone_number="+43 123", direction="invalid")
if call_id is None:
    print("Fehler beim Erstellen des Anrufs")
```

---

## Testing

Siehe `crm/features/test_call_manager.py` für umfassende Unit Tests.

**Test ausführen:**
```bash
python crm/features/test_call_manager.py
```

**Test-Coverage:**
- Anruf-Erstellung (eingehend/ausgehend)
- Timer-Funktionen (Formatierung, Parsing)
- Timeline-Integration (Abrufen, Filtern)
- Anruf-Aktualisierung
- Anruf-Löschung
- Statistiken
- Fehlerbehandlung

---

## Performance-Überlegungen

1. **Indizes**: Anrufe werden über `customer_id` und `activity_type` gefiltert
2. **Limit**: Verwenden Sie den `limit` Parameter für große Datenmengen
3. **Archivierung**: Standardmäßig werden archivierte Anrufe ausgeblendet
4. **Batch-Operations**: Für viele Anrufe, verwenden Sie Transaktionen

---

## Migration

Beim ersten Aufruf von `ensure_call_fields()` oder `create_call()` werden die Felder automatisch hinzugefügt.

**Manuelle Migration:**
```python
from crm.features.call_manager import ensure_call_fields

success = ensure_call_fields()
if success:
    print("Anruf-Felder erfolgreich hinzugefügt")
```

---

## Siehe auch

- `crm/features/call_ui.py` - UI-Komponenten
- `crm/features/note_manager.py` - Kommunikations-Timeline
- `crm/features/test_call_manager.py` - Unit Tests
- `docs/CALL_LOGGING_QUICK_REFERENCE.md` - Benutzer-Dokumentation
