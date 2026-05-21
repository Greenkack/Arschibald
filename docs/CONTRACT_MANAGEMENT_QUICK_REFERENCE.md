# Vertrags- und Garantieverwaltung - Quick Reference

## Schnellstart

```python
from database import get_db_connection
from crm.features import contract_manager

conn = get_db_connection()

# Vertrag erstellen
contract_id = contract_manager.create_contract(
    conn,
    customer_id=1,
    contract_type="Wartungsvertrag",
    title="PV-Wartung 2025",
    start_date="2025-01-01",
    end_date="2025-12-31",
    value=1200.0
)

# Garantie erstellen
warranty_id = contract_manager.create_warranty(
    conn,
    project_id=1,
    customer_id=1,
    warranty_type="Produktgarantie",
    title="PV-Module Garantie",
    start_date="2025-01-01",
    duration_months=300  # 25 Jahre
)

conn.close()
```

## Häufige Aufgaben

### Vertrag anlegen
```python
contract_id = contract_manager.create_contract(
    conn,
    customer_id=1,
    contract_type="Wartungsvertrag",  # oder Kaufvertrag, Mietvertrag, etc.
    title="Vertragstitel",
    start_date="2025-01-01",
    end_date="2025-12-31",  # Optional
    value=1000.0,  # Optional
    description="Beschreibung"  # Optional
)
```

### Garantie anlegen
```python
warranty_id = contract_manager.create_warranty(
    conn,
    project_id=1,
    customer_id=1,
    warranty_type="Produktgarantie",
    title="Garantietitel",
    start_date="2025-01-01",
    duration_months=24,
    terms="Garantiebedingungen"  # Optional
)
```

### Verträge eines Kunden anzeigen
```python
contracts = contract_manager.get_contracts_by_customer(conn, customer_id)
for contract in contracts:
    print(f"{contract['title']} - {contract['status']}")
```

### Garantien eines Projekts anzeigen
```python
warranties = contract_manager.get_warranties_by_project(conn, project_id)
for warranty in warranties:
    print(f"{warranty['title']} - läuft bis {warranty['end_date']}")
```

### Ablaufende Verträge finden
```python
# Verträge die in 30 Tagen ablaufen
expiring = contract_manager.get_expiring_contracts(conn, days_ahead=30)
for contract in expiring:
    days_left = (datetime.strptime(contract['end_date'], '%Y-%m-%d') - datetime.now()).days
    print(f"{contract['title']} läuft in {days_left} Tagen ab")
```

### Erinnerungen abrufen
```python
reminders = contract_manager.get_pending_reminders(conn, days_ahead=7)
for reminder in reminders:
    print(f"Erinnerung: {reminder['message']} am {reminder['reminder_date']}")
```

### Statistiken anzeigen
```python
# Vertrags-Statistiken
stats = contract_manager.get_contract_statistics(conn)
print(f"Gesamt: {stats['total']}")
print(f"Aktiv: {stats['by_status'].get('active', 0)}")
print(f"Ablaufend (30 Tage): {stats['expiring_30_days']}")

# Garantie-Statistiken
stats = contract_manager.get_warranty_statistics(conn)
print(f"Gesamt: {stats['total']}")
print(f"Aktiv: {stats['by_status'].get('active', 0)}")
```

## UI-Integration

### In Streamlit App
```python
from crm.features.contract_ui import render_contract_management_ui

# Vollständige Verwaltungs-UI
render_contract_management_ui()
```

### In Kundendetailansicht
```python
from crm.features.contract_ui import show_customer_contracts_warranties

# Zeige Verträge und Garantien eines Kunden
show_customer_contracts_warranties(customer_id)
```

## Vertragstypen

- **Wartungsvertrag** - Regelmäßige Wartung
- **Kaufvertrag** - Einmaliger Kauf
- **Mietvertrag** - Langfristige Miete
- **Servicevertrag** - Service-Leistungen
- **Leasingvertrag** - Leasing-Vereinbarung

## Garantietypen

- **Produktgarantie** - Garantie auf Produkte
- **Leistungsgarantie** - Garantie auf Leistung (z.B. kWh)
- **Herstellergarantie** - Vom Hersteller
- **Erweiterte Garantie** - Zusätzliche Garantie

## Status-Werte

### Verträge
- `active` - Aktiv und gültig
- `expired` - Abgelaufen
- `cancelled` - Gekündigt

### Garantien
- `active` - Aktiv und gültig
- `expired` - Abgelaufen

## Automatische Erinnerungen

Das System erstellt automatisch Erinnerungen **30 Tage vor Ablauf** für:
- Verträge mit Enddatum
- Alle Garantien

Erinnerungen werden automatisch aktualisiert wenn:
- Das Enddatum geändert wird
- Die Laufzeit geändert wird

## Tipps & Tricks

### 1. Vertrag mit Dokument verknüpfen
```python
# Erst Dokument hochladen
from database import add_customer_document
doc_id = add_customer_document(conn, customer_id, file_path, doc_type='contract')

# Dann Vertrag erstellen
contract_id = contract_manager.create_contract(
    conn, customer_id=customer_id, ..., document_id=doc_id
)
```

### 2. Mehrere Garantien pro Projekt
```python
# Produktgarantie
contract_manager.create_warranty(
    conn, project_id=1, customer_id=1,
    warranty_type="Produktgarantie",
    title="Module Garantie", start_date="2025-01-01", duration_months=300
)

# Leistungsgarantie
contract_manager.create_warranty(
    conn, project_id=1, customer_id=1,
    warranty_type="Leistungsgarantie",
    title="Leistungsgarantie 80%", start_date="2025-01-01", duration_months=300
)
```

### 3. Vertrag verlängern
```python
# Lade aktuellen Vertrag
contract = contract_manager.get_contract_by_id(conn, contract_id)

# Verlängere um 1 Jahr
new_end_date = (datetime.strptime(contract['end_date'], '%Y-%m-%d') + 
                timedelta(days=365)).strftime('%Y-%m-%d')

contract_manager.update_contract(conn, contract_id, end_date=new_end_date)
```

### 4. Abgelaufene Verträge archivieren
```python
expired = contract_manager.get_expired_contracts(conn)
for contract in expired:
    if contract['status'] == 'active':
        contract_manager.update_contract(conn, contract['id'], status='expired')
```

### 5. Dashboard-Widget für Erinnerungen
```python
import streamlit as st

reminders = contract_manager.get_pending_reminders(conn, days_ahead=7)
if reminders:
    st.warning(f"⚠️ {len(reminders)} Erinnerungen fällig!")
    for reminder in reminders:
        st.write(f"- {reminder['message']}")
```

## Fehlerbehandlung

```python
# Alle Funktionen geben None/False bei Fehler zurück
contract_id = contract_manager.create_contract(conn, ...)
if contract_id is None:
    st.error("Fehler beim Erstellen des Vertrags")
else:
    st.success(f"Vertrag erstellt (ID: {contract_id})")
```

## Beispiel: Kompletter Workflow

```python
from database import get_db_connection
from crm.features import contract_manager
from datetime import datetime, timedelta

conn = get_db_connection()

# 1. Kaufvertrag erstellen
contract_id = contract_manager.create_contract(
    conn,
    customer_id=1,
    contract_type="Kaufvertrag",
    title="PV-Anlage Kaufvertrag",
    start_date=datetime.now().strftime('%Y-%m-%d'),
    value=25000.0,
    description="Kauf und Installation PV-Anlage"
)

# 2. Produktgarantie hinzufügen
warranty_id = contract_manager.create_warranty(
    conn,
    project_id=1,
    customer_id=1,
    warranty_type="Produktgarantie",
    title="PV-Module Produktgarantie",
    start_date=datetime.now().strftime('%Y-%m-%d'),
    duration_months=300,  # 25 Jahre
    provider="Trina Solar",
    terms="Garantie auf Materialfehler"
)

# 3. Leistungsgarantie hinzufügen
warranty_id2 = contract_manager.create_warranty(
    conn,
    project_id=1,
    customer_id=1,
    warranty_type="Leistungsgarantie",
    title="PV-Module Leistungsgarantie",
    start_date=datetime.now().strftime('%Y-%m-%d'),
    duration_months=300,
    provider="Trina Solar",
    terms="Mindestens 80% Leistung nach 25 Jahren"
)

# 4. Wartungsvertrag erstellen
maintenance_id = contract_manager.create_contract(
    conn,
    customer_id=1,
    project_id=1,
    contract_type="Wartungsvertrag",
    title="Jährliche Wartung",
    start_date=datetime.now().strftime('%Y-%m-%d'),
    end_date=(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
    value=500.0,
    renewal_type="Automatisch"
)

# 5. Statistiken anzeigen
stats = contract_manager.get_contract_statistics(conn)
print(f"Verträge: {stats['total']}, Wert: {stats['total_value']} EUR")

conn.close()
```

## Support

Bei Fragen oder Problemen:
- Siehe: `crm/features/CONTRACT_MANAGER_REFERENCE.md`
- Tests: `crm/features/test_contract_manager.py`
- Code: `crm/features/contract_manager.py`
