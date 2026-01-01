# Contract Manager - Technische Referenz

## Übersicht

Das Contract Manager Modul bietet vollständige Verwaltung von Verträgen und Garantien mit automatischen Ablauf-Erinnerungen.

**Modul:** `crm/features/contract_manager.py`  
**UI:** `crm/features/contract_ui.py`  
**Tests:** `crm/features/test_contract_manager.py`  
**Version:** 1.0  
**Datum:** 2025-01-14

## Datenbank-Schema

### Tabelle: contracts

```sql
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    contract_type TEXT NOT NULL,
    contract_number TEXT,
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    value REAL,
    currency TEXT DEFAULT 'EUR',
    status TEXT DEFAULT 'active',
    document_id INTEGER,
    renewal_type TEXT,
    notice_period_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (document_id) REFERENCES customer_documents(id)
)
```

### Tabelle: warranties

```sql
CREATE TABLE warranties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    warranty_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    duration_months INTEGER NOT NULL,
    end_date DATE,
    terms TEXT,
    coverage_details TEXT,
    provider TEXT,
    provider_contact TEXT,
    document_id INTEGER,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (document_id) REFERENCES customer_documents(id)
)
```

### Tabelle: contract_reminders

```sql
CREATE TABLE contract_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER,
    warranty_id INTEGER,
    reminder_type TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    status TEXT DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified_at TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (warranty_id) REFERENCES warranties(id)
)
```

## API-Funktionen

### Vertrags-CRUD

#### create_contract()
```python
contract_id = contract_manager.create_contract(
    conn,
    customer_id=1,
    contract_type="Wartungsvertrag",
    title="PV-Anlage Wartung 2025",
    start_date="2025-01-01",
    end_date="2025-12-31",
    value=1200.0,
    description="Jährliche Wartung"
)
```

#### get_contract_by_id()
```python
contract = contract_manager.get_contract_by_id(conn, contract_id)
```

#### get_contracts_by_customer()
```python
contracts = contract_manager.get_contracts_by_customer(conn, customer_id)
```

#### update_contract()
```python
success = contract_manager.update_contract(
    conn,
    contract_id,
    title="Neuer Titel",
    value=1500.0,
    status="expired"
)
```

#### delete_contract()
```python
success = contract_manager.delete_contract(conn, contract_id)
```

### Garantie-CRUD

#### create_warranty()
```python
warranty_id = contract_manager.create_warranty(
    conn,
    project_id=1,
    customer_id=1,
    warranty_type="Produktgarantie",
    title="PV-Module Garantie",
    start_date="2025-01-01",
    duration_months=120,
    description="25 Jahre Leistungsgarantie"
)
```

#### get_warranty_by_id()
```python
warranty = contract_manager.get_warranty_by_id(conn, warranty_id)
```

#### get_warranties_by_project()
```python
warranties = contract_manager.get_warranties_by_project(conn, project_id)
```

#### update_warranty()
```python
success = contract_manager.update_warranty(
    conn,
    warranty_id,
    title="Aktualisiert",
    duration_months=36
)
```

#### delete_warranty()
```python
success = contract_manager.delete_warranty(conn, warranty_id)
```

### Erinnerungen

#### get_pending_reminders()
```python
reminders = contract_manager.get_pending_reminders(conn, days_ahead=30)
```

#### mark_reminder_notified()
```python
success = contract_manager.mark_reminder_notified(conn, reminder_id)
```

### Ablaufende Verträge/Garantien

#### get_expiring_contracts()
```python
expiring = contract_manager.get_expiring_contracts(conn, days_ahead=30)
```

#### get_expired_contracts()
```python
expired = contract_manager.get_expired_contracts(conn)
```

#### get_expiring_warranties()
```python
expiring = contract_manager.get_expiring_warranties(conn, days_ahead=30)
```

#### get_expired_warranties()
```python
expired = contract_manager.get_expired_warranties(conn)
```

### Statistiken

#### get_contract_statistics()
```python
stats = contract_manager.get_contract_statistics(conn)
# Returns: {
#     'total': 10,
#     'by_status': {'active': 8, 'expired': 2},
#     'by_type': {'Wartungsvertrag': 5, 'Kaufvertrag': 5},
#     'expiring_30_days': 2,
#     'expired': 2,
#     'total_value': 50000.0
# }
```

#### get_warranty_statistics()
```python
stats = contract_manager.get_warranty_statistics(conn)
```

## UI-Integration

### Hauptfunktion
```python
from crm.features.contract_ui import render_contract_management_ui

# In Streamlit App
render_contract_management_ui()
```

### Kunden-spezifische Anzeige
```python
from crm.features.contract_ui import show_customer_contracts_warranties

# In Kundendetailansicht
show_customer_contracts_warranties(customer_id)
```

## Automatische Erinnerungen

Das System erstellt automatisch Erinnerungen:

- **Verträge:** 30 Tage vor Ablauf
- **Garantien:** 30 Tage vor Ablauf

Erinnerungen werden automatisch erstellt bei:
- Neuanlage eines Vertrags/Garantie mit Enddatum
- Änderung des Enddatums

## Status-Werte

### Verträge
- `active` - Aktiv
- `expired` - Abgelaufen
- `cancelled` - Gekündigt

### Garantien
- `active` - Aktiv
- `expired` - Abgelaufen

### Erinnerungen
- `pending` - Ausstehend
- `notified` - Benachrichtigt

## Vertragstypen (Beispiele)

- Wartungsvertrag
- Kaufvertrag
- Mietvertrag
- Servicevertrag
- Leasingvertrag

## Garantietypen (Beispiele)

- Produktgarantie
- Leistungsgarantie
- Herstellergarantie
- Erweiterte Garantie

## Best Practices

### 1. Verträge mit Dokumenten verknüpfen
```python
# Erst Dokument hochladen
document_id = add_customer_document(...)

# Dann Vertrag mit Dokument verknüpfen
contract_id = create_contract(
    conn,
    customer_id=1,
    contract_type="Kaufvertrag",
    title="Kaufvertrag PV-Anlage",
    start_date="2025-01-01",
    document_id=document_id
)
```

### 2. Garantien zu Projekten hinzufügen
```python
# Nach Projektabschluss Garantien anlegen
warranty_id = create_warranty(
    conn,
    project_id=project_id,
    customer_id=customer_id,
    warranty_type="Produktgarantie",
    title="PV-Module Garantie",
    start_date=installation_date,
    duration_months=300  # 25 Jahre
)
```

### 3. Regelmäßige Erinnerungs-Checks
```python
# Täglich ausführen
reminders = get_pending_reminders(conn, days_ahead=7)
for reminder in reminders:
    # Benachrichtigung senden
    send_notification(reminder)
    mark_reminder_notified(conn, reminder['id'])
```

### 4. Abgelaufene Verträge archivieren
```python
expired = get_expired_contracts(conn)
for contract in expired:
    if contract['status'] == 'active':
        update_contract(conn, contract['id'], status='expired')
```

## Fehlerbehandlung

Alle Funktionen geben `None` oder `False` bei Fehlern zurück:

```python
contract_id = create_contract(conn, ...)
if contract_id is None:
    print("Fehler beim Erstellen des Vertrags")
    # Fehlerbehandlung
```

## Performance-Tipps

1. **Indizes nutzen:** Alle wichtigen Felder sind indiziert
2. **Batch-Updates:** Mehrere Updates in einer Transaktion
3. **Filterung:** Nutze Status- und Typ-Filter für große Datenmengen

## Integration mit anderen Modulen

### Mit Benachrichtigungssystem
```python
from crm.utils.notification_manager import create_reminder

# Erstelle CRM-Erinnerung für ablaufenden Vertrag
reminders = get_expiring_contracts(conn, 30)
for contract in reminders:
    create_reminder(
        conn,
        reminder_type='contract_expiry',
        related_id=contract['id'],
        related_type='contract',
        due_date=contract['end_date'],
        message=f"Vertrag '{contract['title']}' läuft ab"
    )
```

### Mit Dokumenten-System
```python
from database import add_customer_document

# Vertragsdokument hochladen und verknüpfen
doc_id = add_customer_document(
    conn,
    customer_id=customer_id,
    file_path=contract_pdf_path,
    doc_type='contract'
)

create_contract(
    conn,
    customer_id=customer_id,
    contract_type="Kaufvertrag",
    title="Kaufvertrag",
    start_date="2025-01-01",
    document_id=doc_id
)
```

## Testen

```bash
# Alle Tests ausführen
python -m pytest crm/features/test_contract_manager.py -v

# Spezifische Tests
python -m pytest crm/features/test_contract_manager.py::test_create_contract -v

# Mit Coverage
python -m pytest crm/features/test_contract_manager.py --cov=crm.features.contract_manager
```

## Changelog

### Version 1.0 (2025-01-14)
- Initiale Implementierung
- Vertrags-CRUD-Operationen
- Garantie-CRUD-Operationen
- Automatische Ablauf-Erinnerungen
- Statistiken und Reporting
- Vollständige UI-Integration
- 23 Unit Tests (100% Pass-Rate)
