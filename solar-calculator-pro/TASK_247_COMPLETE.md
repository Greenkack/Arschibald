# Task 247: Customer Data CRM Integration - COMPLETE

## Übersicht

Dieses Task implementiert eine vollständige Kundendaten-Verwaltung mit CRM-Integration, PDF-Platzhaltern und Import/Export-Funktionalität.

## Erstellte Dateien

### 1. Backend Service

**Datei:** `solar-calculator-pro/backend/services/customer_data_service.py`

Der CustomerDataService bietet:

**CRUD-Operationen:**
- `create_customer()` - Neuen Kunden anlegen
- `get_customer()` - Kunde nach ID abrufen
- `update_customer()` - Kundendaten aktualisieren
- `delete_customer()` - Kunde löschen
- `get_all_customers()` - Alle Kunden mit Paginierung
- `search_customers()` - Volltextsuche mit Filtern

**Datenbank-Schema:**
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salutation TEXT,           -- Anrede (Herr/Frau)
    title TEXT,                -- Titel (Dr., Prof.)
    first_name TEXT,           -- Vorname
    last_name TEXT,            -- Nachname
    company TEXT,              -- Firma
    street TEXT,               -- Straße
    house_number TEXT,         -- Hausnummer
    postal_code TEXT,          -- PLZ
    city TEXT,                 -- Ort
    bundesland TEXT,           -- Bundesland
    email TEXT,                -- E-Mail
    phone TEXT,                -- Telefon
    mobile TEXT,               -- Mobil
    notes TEXT,                -- Notizen
    tags TEXT,                 -- Tags (JSON)
    source TEXT,               -- Quelle (manual, import, api)
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 2. API Endpoints

**Datei:** `solar-calculator-pro/backend/api/v1/customer_data.py`

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| POST | `/api/v1/customer-data/` | Kunde erstellen |
| GET | `/api/v1/customer-data/{id}` | Kunde abrufen |
| PUT | `/api/v1/customer-data/{id}` | Kunde aktualisieren |
| DELETE | `/api/v1/customer-data/{id}` | Kunde löschen |
| GET | `/api/v1/customer-data/` | Alle Kunden (paginiert) |
| GET | `/api/v1/customer-data/search/` | Kunden suchen |
| GET | `/api/v1/customer-data/{id}/placeholders` | PDF-Platzhalter |
| GET | `/api/v1/customer-data/placeholders/list` | Platzhalter-Liste |
| GET | `/api/v1/customer-data/export/csv` | CSV Export |
| GET | `/api/v1/customer-data/export/json` | JSON Export |
| POST | `/api/v1/customer-data/import/csv` | CSV Import |
| POST | `/api/v1/customer-data/import/json` | JSON Import |

### 3. Frontend Service

**Datei:** `solar-calculator-pro/frontend/src/services/customerDataService.ts`

TypeScript-Service mit:
- Typisierte Interfaces für Customer, CustomerCreate, etc.
- Alle CRUD-Methoden
- Import/Export-Funktionen mit Blob-Download
- Utility-Methoden für Formatierung

## PDF-Platzhalter System

Das System stellt 18 Platzhalter für PDF-Templates bereit:

| Platzhalter | Beschreibung |
|-------------|--------------|
| `{{KUNDE_NAME}}` | Vollständiger Name (Vorname Nachname) |
| `{{KUNDE_VORNAME}}` | Vorname |
| `{{KUNDE_NACHNAME}}` | Nachname |
| `{{KUNDE_FIRMA}}` | Firmenname |
| `{{KUNDE_STRASSE}}` | Straße |
| `{{KUNDE_HAUSNUMMER}}` | Hausnummer |
| `{{KUNDE_PLZ}}` | Postleitzahl |
| `{{KUNDE_ORT}}` | Ort |
| `{{KUNDE_BUNDESLAND}}` | Bundesland |
| `{{KUNDE_ADRESSE_KOMPLETT}}` | Vollständige Adresse |
| `{{KUNDE_EMAIL}}` | E-Mail-Adresse |
| `{{KUNDE_TELEFON}}` | Telefonnummer |
| `{{KUNDE_MOBIL}}` | Mobilnummer |
| `{{KUNDE_ANREDE}}` | Anrede (Herr/Frau) |
| `{{KUNDE_TITEL}}` | Titel (Dr., Prof., etc.) |
| `{{KUNDE_ID}}` | Kunden-ID |
| `{{KUNDE_ERSTELLT_AM}}` | Erstellungsdatum |
| `{{KUNDE_NOTIZEN}}` | Notizen |

## Import/Export Funktionalität

### CSV Export
```csv
id,salutation,title,first_name,last_name,company,street,house_number,postal_code,city,bundesland,email,phone,mobile,notes,created_at
1,Herr,,Max,Mustermann,Muster GmbH,Musterstraße,123,12345,Berlin,BE,max@example.com,030-123456,,Wichtiger Kunde,2025-11-28
```

### CSV Import
Unterstützt deutsche und englische Spaltenbezeichnungen:
- `Vorname` oder `first_name`
- `Nachname` oder `last_name`
- `Straße` oder `street`
- `PLZ` oder `postal_code`
- etc.

### JSON Export/Import
```json
[
  {
    "id": 1,
    "salutation": "Herr",
    "first_name": "Max",
    "last_name": "Mustermann",
    "company": "Muster GmbH",
    "street": "Musterstraße",
    "house_number": "123",
    "postal_code": "12345",
    "city": "Berlin",
    "bundesland": "BE",
    "email": "max@example.com"
  }
]
```

## Verwendungsbeispiele

### Kunde erstellen (Backend)
```python
from services.customer_data_service import CustomerDataService

service = CustomerDataService()
customer_id = service.create_customer({
    'salutation': 'Herr',
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'street': 'Musterstraße',
    'house_number': '123',
    'postal_code': '12345',
    'city': 'Berlin',
    'email': 'max@example.com'
})
```

### Kunde erstellen (Frontend)
```typescript
import { customerDataService } from './services/customerDataService';

const result = await customerDataService.createCustomer({
  first_name: 'Max',
  last_name: 'Mustermann',
  street: 'Musterstraße',
  house_number: '123',
  postal_code: '12345',
  city: 'Berlin',
  email: 'max@example.com'
});

console.log('Kunde erstellt mit ID:', result.id);
```

### PDF-Platzhalter abrufen
```typescript
const placeholders = await customerDataService.getCustomerPlaceholders(customerId);
// { '{{KUNDE_NAME}}': 'Max Mustermann', '{{KUNDE_PLZ}}': '12345', ... }
```

### Kunden exportieren
```typescript
const blob = await customerDataService.exportCustomersCSV();
customerDataService.downloadBlob(blob, 'kunden.csv');
```

## Integration mit Project Wizard

Der CustomerDataService integriert sich nahtlos mit dem Project Wizard (Task 245):

1. **Kundendaten aus Wizard speichern:**
   ```typescript
   // Im Wizard nach Abschluss
   const customerId = await customerDataService.createCustomer(wizardData.customer);
   ```

2. **Bestehende Kunden im Wizard auswählen:**
   ```typescript
   const customers = await customerDataService.searchCustomers(searchQuery);
   // Dropdown mit Kundenauswahl anzeigen
   ```

3. **PDF mit Kundendaten generieren:**
   ```typescript
   const placeholders = await customerDataService.getCustomerPlaceholders(customerId);
   // Platzhalter an PDF-Generator übergeben
   ```

## Requirements Erfüllt

| Requirement | Status |
|-------------|--------|
| funktionen.txt - "CRM-System gespeichert" | ✅ |
| Automatische Speicherung aller Kundendaten | ✅ |
| PDF-Platzhalter für Templates | ✅ |
| Such- und Abruffunktionen | ✅ |
| Export-Funktionalität (CSV, JSON) | ✅ |
| Import aus externen Quellen | ✅ |

## Technische Details

- **Backend:** Python mit FastAPI
- **Datenbank:** SQLite mit optimierten Indizes
- **Frontend:** TypeScript mit Axios
- **API:** RESTful mit Pydantic-Validierung
- **Export:** CSV und JSON mit Streaming

---

**Status: COMPLETE** ✅  
**Erstellt:** November 28, 2025
