# Offer Tracker Tests - Reference Documentation

## Overview

Comprehensive test suite for the Offer Tracking (Angebotsverfolgung) functionality in the CRM system.

**Test File:** `crm/features/test_offer_tracker.py`

**Status:** ✅ All tests passing

**Requirements Covered:** 7.1, 7.2, 7.3

---

## Test Coverage

### 1. Status-Workflow Tests ✅

**Requirement:** 7.1 - WHEN ein Angebot versendet wird THEN soll der Status auf "Versendet" gesetzt werden

**Tests:**
- ✅ Status transition: draft → sent
- ✅ Status transition: sent → accepted
- ✅ Status transition: sent → rejected
- ✅ Automatic timestamp recording for each status
- ✅ Offer value tracking
- ✅ Rejection reason and notes capture

**Key Assertions:**
```python
# Test 1: Status auf "sent" setzen
assert offer['offer_status'] == 'sent'
assert offer['offer_sent_date'] is not None
assert offer['follow_up_date'] is not None  # Automatic 7-day follow-up
assert offer['offer_value'] == 25000.0

# Test 2: Status auf "accepted" setzen
assert offer['offer_status'] == 'accepted'
assert offer['offer_accepted_date'] is not None

# Test 3: Status auf "rejected" setzen
assert offer['offer_status'] == 'rejected'
assert offer['rejection_reason'] == 'Preis zu hoch'
assert offer['rejection_notes'] is not None
```

---

### 2. Automatic Reminder Tests ✅

**Requirement:** 7.2 - WHEN ein Angebot 7 Tage alt ist THEN soll eine Nachfass-Erinnerung erstellt werden

**Tests:**
- ✅ Automatic follow-up creation when offer is sent
- ✅ Follow-up date set to 7 days after sending
- ✅ Pending follow-ups retrieval (overdue items)
- ✅ Follow-up completion marking
- ✅ Filtering of completed vs. pending follow-ups

**Key Assertions:**
```python
# Automatic follow-up when status = 'sent'
result = update_offer_status(conn, project_id, 'sent', offer_value=25000.0)
offer = get_offer_status(conn, project_id)
assert offer['follow_up_date'] is not None  # Auto-set to +7 days

# Pending follow-ups (overdue)
pending = get_pending_follow_ups(conn)
assert len(pending) == 1
assert pending[0]['project_name'] == "Projekt mit fälligem Follow-up"

# Mark as completed
result = mark_follow_up_completed(conn, project_id_1)
pending_after = get_pending_follow_ups(conn)
assert len(pending_after) == 0
```

---

### 3. Lead Status Integration Tests ✅

**Requirement:** 7.3 - WHEN ein Angebot angenommen wird THEN soll der Lead-Status auf "Won" gesetzt werden

**Tests:**
- ✅ Offer accepted → Lead status = "won"
- ✅ Offer rejected → Lead status = "lost"
- ✅ Lead lookup by company name and contact person
- ✅ Timestamp updates for lead stage changes

**Key Assertions:**
```python
# Test 1: Angebot angenommen -> Lead auf "won"
update_offer_status(conn, project_id, 'accepted')
result = update_lead_status_from_offer(conn, project_id, 'accepted')
assert result == True

cursor.execute("SELECT stage FROM crm_leads WHERE id = ?", (lead_id,))
lead_stage = cursor.fetchone()[0]
assert lead_stage == 'won'

# Test 2: Angebot abgelehnt -> Lead auf "lost"
update_offer_status(conn, project_id_2, 'rejected')
result = update_lead_status_from_offer(conn, project_id_2, 'rejected')
assert result == True

cursor.execute("SELECT stage FROM crm_leads WHERE id = ?", (lead_id_2,))
lead_stage = cursor.fetchone()[0]
assert lead_stage == 'lost'
```

---

## Additional Test Coverage

### 4. Offer Retrieval and Filtering ✅

**Tests:**
- ✅ Get all offers
- ✅ Filter by status (draft, sent, accepted, rejected)
- ✅ Include customer information in results
- ✅ Proper JOIN with customers table

**Key Assertions:**
```python
# All offers
all_offers = get_all_offers(conn)
assert len(all_offers) == 4

# Filter by status
sent_offers = get_all_offers(conn, status_filter='sent')
assert len(sent_offers) == 1
assert sent_offers[0]['offer_status'] == 'sent'

# With customer info
offers_with_customer = get_all_offers(conn, include_customer_info=True)
assert 'customer_first_name' in offers_with_customer[0]
assert offers_with_customer[0]['customer_company_name'] == 'Test GmbH'
```

---

### 5. Statistics and Reporting ✅

**Tests:**
- ✅ Total offer count
- ✅ Count by status (draft, sent, accepted, rejected)
- ✅ Average offer value calculation
- ✅ Conversion rate calculation (accepted / (accepted + rejected))
- ✅ Pending follow-ups count

**Key Assertions:**
```python
stats = get_offer_statistics(conn)

assert stats['total_offers'] == 7
assert stats['draft'] == 1
assert stats['sent'] == 3
assert stats['accepted'] == 2
assert stats['rejected'] == 1

# Conversion Rate: 2 accepted / (2 accepted + 1 rejected) = 66.67%
expected_conversion = 2 / 3 * 100
assert abs(stats['conversion_rate'] - expected_conversion) < 0.1

# Average value: 165000 / 6 = 27500
expected_avg = 165000 / 6
assert abs(stats['avg_offer_value'] - expected_avg) < 1

assert stats['pending_follow_ups'] == 1
```

---

## Test Database Setup

Each test uses an in-memory SQLite database with the following tables:

```sql
-- customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    company_name TEXT,
    email TEXT,
    phone_mobile TEXT
)

-- projects table (base)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    project_name TEXT,
    project_status TEXT,
    creation_date TEXT,
    last_updated TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)

-- crm_leads table (for integration tests)
CREATE TABLE crm_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    contact_person TEXT,
    stage TEXT,
    stage_changed_at TEXT,
    updated_at TEXT
)
```

The `create_offer_tracking_tables()` function then adds the following columns to `projects`:
- `offer_status` (TEXT DEFAULT "draft")
- `offer_sent_date` (TEXT)
- `offer_accepted_date` (TEXT)
- `offer_rejected_date` (TEXT)
- `offer_version` (INTEGER DEFAULT 1)
- `offer_value` (REAL)
- `rejection_reason` (TEXT)
- `rejection_notes` (TEXT)
- `follow_up_date` (TEXT)
- `follow_up_completed` (INTEGER DEFAULT 0)

---

## Running the Tests

```bash
# Run all offer tracker tests
python crm/features/test_offer_tracker.py

# Expected output:
# ============================================================
# ANGEBOTSVERFOLGUNG (OFFER TRACKING) - TEST SUITE
# ============================================================
# 
# === Test: Tabellen-Erstellung ===
# ✅ Alle erforderlichen Spalten wurden hinzugefügt
# 
# === Test: Status-Workflow ===
# ✅ Status 'sent' erfolgreich gesetzt mit automatischem Follow-up
# ✅ Status 'accepted' erfolgreich gesetzt
# ✅ Status 'rejected' erfolgreich gesetzt mit Ablehnungsgrund
# 
# === Test: Angebote laden ===
# ✅ 4 Angebote geladen
# ✅ Filter funktioniert korrekt
# ✅ Kundeninformationen werden korrekt geladen
# 
# === Test: Follow-up-Erinnerungen ===
# ✅ 1 ausstehendes Follow-up gefunden
# ✅ Follow-up erfolgreich als erledigt markiert
# 
# === Test: Lead-Status-Aktualisierung ===
# ✅ Lead-Status erfolgreich auf 'won' aktualisiert
# ✅ Lead-Status erfolgreich auf 'lost' aktualisiert
# 
# === Test: Angebots-Statistiken ===
# ✅ Alle Statistiken korrekt berechnet
# 
# ============================================================
# ✅ ALLE TESTS ERFOLGREICH BESTANDEN!
# ============================================================
```

---

## Test Results Summary

| Test Category | Tests | Status | Coverage |
|--------------|-------|--------|----------|
| Status Workflow | 3 | ✅ Pass | 100% |
| Automatic Reminders | 2 | ✅ Pass | 100% |
| Lead Status Integration | 2 | ✅ Pass | 100% |
| Offer Retrieval | 3 | ✅ Pass | 100% |
| Statistics | 1 | ✅ Pass | 100% |
| **TOTAL** | **11** | **✅ Pass** | **100%** |

---

## Requirements Traceability

| Requirement | Acceptance Criteria | Test Coverage | Status |
|-------------|-------------------|---------------|--------|
| 7.1 | Angebot erstellt → erscheint in Verfolgung | ✅ `test_update_offer_status` | ✅ Pass |
| 7.1 | Angebot versendet → Status "Versendet" | ✅ `test_update_offer_status` | ✅ Pass |
| 7.2 | Angebot 7 Tage alt → Nachfass-Erinnerung | ✅ `test_follow_up_reminders` | ✅ Pass |
| 7.3 | Angebot angenommen → Lead "Won" | ✅ `test_lead_status_update` | ✅ Pass |
| 7.3 | Angebot abgelehnt → Ablehnungsgrund | ✅ `test_update_offer_status` | ✅ Pass |

---

## Integration Points

The offer tracker integrates with:

1. **Projects Table** - Stores offer data as extended fields
2. **Customers Table** - Links offers to customers
3. **CRM Leads Table** - Syncs offer status with lead pipeline
4. **PDF Generator** - Auto-saves PDFs to customer documents
5. **Dashboard** - Displays pending follow-ups and statistics

---

## Next Steps

Task 6.1 is now complete. The next task in the implementation plan is:

**Task 7: Automatische Erinnerungen und Follow-ups implementieren**
- Erstelle `crm/utils/notification_manager.py`
- Implementiere Regel-Engine für automatische Erinnerungen
- Erstelle Dashboard-Widget für fällige Erinnerungen

---

## Notes

- All tests use in-memory databases for isolation
- Tests are independent and can run in any order
- No external dependencies or mocks required
- Tests validate real functionality, not mocked behavior
- 100% coverage of requirements 7.1, 7.2, and 7.3

**Last Updated:** 2025-01-14
**Test Suite Version:** 1.0
**Status:** ✅ Complete and Passing
