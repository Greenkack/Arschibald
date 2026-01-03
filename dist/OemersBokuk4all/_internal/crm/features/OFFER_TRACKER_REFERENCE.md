# Offer Tracker Module - Technical Reference

## Module Structure

```
crm/features/
├── offer_tracker.py      # Core business logic
├── offer_ui.py           # User interface
└── test_offer_tracker.py # Test suite
```

## Core Functions (offer_tracker.py)

### Database Management

#### `create_offer_tracking_tables(conn)`
Erstellt/erweitert die projects Tabelle mit Angebotsverfolgung-Feldern.

**Neue Felder:**
- offer_status, offer_sent_date, offer_accepted_date
- offer_rejected_date, offer_version, offer_value
- rejection_reason, rejection_notes
- follow_up_date, follow_up_completed

### Status Management

#### `update_offer_status(conn, project_id, new_status, **kwargs)`
Aktualisiert den Angebotsstatus mit automatischen Aktionen.

**Automatische Aktionen:**
- Bei 'sent': Setzt follow_up_date auf +7 Tage
- Bei 'accepted': Setzt offer_accepted_date
- Bei 'rejected': Speichert rejection_reason und rejection_notes

**Beispiel:**
```python
update_offer_status(
    conn, 
    project_id=123, 
    new_status='rejected',
    rejection_reason='Preis zu hoch',
    rejection_notes='Kunde hat günstigeres Angebot'
)
```

### Data Retrieval

#### `get_offer_status(conn, project_id)`
Lädt den vollständigen Angebotsstatus eines Projekts.

#### `get_all_offers(conn, status_filter=None, include_customer_info=True)`
Lädt alle Angebote mit optionalem Filter und Kundeninformationen.

#### `get_pending_follow_ups(conn)`
Lädt alle Angebote mit fälligen Follow-ups.

### Analytics

#### `get_offer_statistics(conn)`
Berechnet umfassende Statistiken:
- Anzahl nach Status
- Conversion Rate
- Durchschnittlicher Angebotswert
- Ausstehende Follow-ups

### Integration

#### `update_lead_status_from_offer(conn, project_id, offer_status)`
Synchronisiert Lead-Status mit Angebotsstatus:
- 'accepted' → Lead-Status 'won'
- 'rejected' → Lead-Status 'lost'

## UI Components (offer_ui.py)

### Main Interface

#### `render_offer_tracking_ui(conn, texts)`
Haupteinstiegspunkt mit 3 Tabs:
1. Übersicht (KPIs & Statistiken)
2. Alle Angebote (Liste mit Filter)
3. Follow-ups (Ausstehende Aktionen)

### Sub-Components

#### `render_offer_overview(conn, texts)`
Dashboard mit KPI-Cards und Status-Verteilung.

#### `render_all_offers(conn, texts)`
Filterable Liste aller Angebote mit Such- und Sortierfunktion.

#### `render_offer_card(conn, offer, texts)`
Einzelne Angebots-Karte mit Aktions-Buttons.

#### `render_follow_ups(conn, texts)`
Liste ausstehender Follow-ups mit Dringlichkeits-Kennzeichnung.

## Database Schema

### Extended projects Table

```sql
ALTER TABLE projects ADD COLUMN offer_status TEXT DEFAULT "draft";
ALTER TABLE projects ADD COLUMN offer_sent_date TEXT;
ALTER TABLE projects ADD COLUMN offer_accepted_date TEXT;
ALTER TABLE projects ADD COLUMN offer_rejected_date TEXT;
ALTER TABLE projects ADD COLUMN offer_version INTEGER DEFAULT 1;
ALTER TABLE projects ADD COLUMN offer_value REAL;
ALTER TABLE projects ADD COLUMN rejection_reason TEXT;
ALTER TABLE projects ADD COLUMN rejection_notes TEXT;
ALTER TABLE projects ADD COLUMN follow_up_date TEXT;
ALTER TABLE projects ADD COLUMN follow_up_completed INTEGER DEFAULT 0;
```

## Testing

### Test Coverage
- ✅ Table creation and migration
- ✅ Status workflow (draft → sent → accepted/rejected)
- ✅ Automatic follow-up creation
- ✅ Follow-up completion
- ✅ Lead status synchronization
- ✅ Statistics calculation
- ✅ Data filtering and retrieval

### Running Tests
```bash
python crm/features/test_offer_tracker.py
```

## Integration Points

### In database.py
```python
def ensure_offer_tracking_tables():
    from crm.features.offer_tracker import create_offer_tracking_tables
    conn = get_db_connection()
    create_offer_tracking_tables(conn)
    conn.close()
```

### In crm.py
```python
# Navigation
if st.button("📋 Angebote"):
    st.session_state['crm_view_mode'] = 'offer_tracking'

# View Rendering
if view_mode == 'offer_tracking':
    from crm.features.offer_ui import render_offer_tracking_ui
    render_offer_tracking_ui(conn, texts)
```

## Best Practices

1. **Always call `create_offer_tracking_tables(conn)` before using offer functions**
2. **Use `update_offer_status()` for all status changes** (handles automatic actions)
3. **Check `get_pending_follow_ups()` regularly** for customer engagement
4. **Use `get_offer_statistics()` for reporting** and analytics
5. **Enable Lead-Status sync** with `update_lead_status_from_offer()`
