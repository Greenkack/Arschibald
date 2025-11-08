# Telephony System - Quick Start Guide

## Schnelleinstieg in 5 Minuten

### 1. Bria Softphone verbinden

```python
bria_connect('sip.example.com', 'username', 'password')
```

### 2. Ersten Anruf starten

```python
bria_make_call('+49301234567', 'Beratungstermin vereinbaren')
```

### 3. Kontakt hinzufugen

```python
add_phone_contact(
    name='Max Mustermann',
    phone_number='+49301234567',
    company='Musterfirma GmbH',
    tags='lead,interessiert'
)
```

### 4. Anruf-Statistiken abrufen

```python
get_call_analytics(30)  # Letzte 30 Tage
```

### 5. Call-Skript verwenden

```python
# Skript abrufen
get_call_script('Verkauf')

# Oder neues Skript speichern
save_call_script(
    name='PV-Beratung',
    category='Verkauf',
    opening_statement='Guten Tag, hier ist KAI...',
    key_points='Kostenersparnis,Umweltschutz'
)
```

---

## Wichtigste Features

### Bulk-Import von Kontakten

**CSV-Datei erstellen:**

```csv
name,phone_number,email,company,tags
Max Mustermann,+49301234567,max@example.com,Firma A,"lead,vip"
Anna Schmidt,+49307654321,anna@example.com,Firma B,"customer,pv"
```

**Importieren:**

```python
bulk_import_phone_numbers('C:/contacts.csv')
```

### Auto-Dialer Kampagne

**Alle Kontakte mit Tag "lead" anrufen:**

```python
auto_dialer_campaign(
    contact_tag='lead',
    call_goal='Beratungstermin vereinbaren',
    max_calls=20
)
```

### Call Recording & Transcription

**Aufnahme starten:**

```python
start_call_recording('CALL-12345678')
```

**Transkribieren:**

```python
transcribe_call_recording('data/recordings/CALL-12345678.wav')
```

### Sentiment-Analyse

**Stimmung eines Anrufs bewerten:**

```python
analyze_call_sentiment('CALL-12345678')
```

Ergebnis:

- Positiv: Score > 0.1
- Neutral: Score -0.1 bis 0.1
- Negativ: Score < -0.1

### CRM Integration

**Anruf ins CRM protokollieren:**

```python
log_call_to_crm('CALL-12345678', 'CRM-001')
```

### Follow-up planen

**Wiedervorlage setzen:**

```python
schedule_follow_up(
    'CALL-12345678',
    '2024-02-15',
    'Angebot nachfassen'
)
```

---

## UI Nutzung

### Agent UI öffnen

1. A.G.E.N.T. starten
2. Expander "📞 Telephony System" aufklappen (ganz unten, vor Task Input)
3. Tabs durchgehen:
   - Bria Softphone
   - Kontakte
   - Analytics
   - Knowledge Base
   - Erweiterte Features

### Tool-Befehle generieren

Die UI generiert automatisch die richtigen Tool-Aufrufe. Einfach:

1. Felder ausfüllen
2. Button klicken
3. Generierten Code kopieren
4. Im Agent-Chat einfügen

**Beispiel:**

In UI:

- Name: "Max Mustermann"
- Telefon: "+49301234567"
- Button "Kontakt speichern"

Generierter Code:

```python
add_phone_contact(
    name='Max Mustermann',
    phone_number='+49301234567',
    ...
)
```

---

## Typische Workflows

### Workflow 1: Neuer Lead

1. **Kontakt anlegen:**

   ```python
   add_phone_contact(
       name='Neuer Kunde',
       phone_number='+49301234567',
       tags='lead,pv-interesse'
   )
   ```

2. **Anrufen:**

   ```python
   quick_dial_favorite('Neuer Kunde')
   ```

3. **Notizen machen (während Anruf):**

   ```python
   update_call_summary('Kunde interessiert an 10kW Anlage')
   ```

4. **Anruf beenden:**

   ```python
   end_call(
       outcome='Beratungstermin vereinbart',
       next_steps='Angebot erstellen und versenden'
   )
   ```

5. **Follow-up setzen:**

   ```python
   schedule_follow_up(
       'CALL-12345678',
       '2024-02-15',
       'Angebot nachfassen'
   )
   ```

### Workflow 2: Kampagne

1. **Kontakte importieren:**

   ```python
   bulk_import_phone_numbers('leads.csv')
   ```

2. **Kampagne starten:**

   ```python
   auto_dialer_campaign('lead', 'Beratungstermin', max_calls=50)
   ```

3. **Statistiken prüfen:**

   ```python
   get_call_analytics(7)  # Letzte Woche
   ```

### Workflow 3: Qualitätssicherung

1. **Anruf aufnehmen:**

   ```python
   start_call_recording('CALL-12345678')
   ```

2. **Nach Anruf transkribieren:**

   ```python
   transcribe_call_recording('data/recordings/CALL-12345678.wav')
   ```

3. **Sentiment prüfen:**

   ```python
   analyze_call_sentiment('CALL-12345678')
   ```

4. **Ins CRM protokollieren:**

   ```python
   log_call_to_crm('CALL-12345678')
   ```

---

## Datenbank-Zugriff

### Manueller Zugriff (optional)

**Datenbank-Pfad:**

```
data/telephony.db
```

**SQLite-Abfragen:**

```sql
-- Alle Kontakte
SELECT * FROM contacts;

-- Anruf-Historie
SELECT * FROM call_history ORDER BY started_at DESC LIMIT 10;

-- Call-Skripte
SELECT * FROM call_scripts WHERE category = 'Verkauf';
```

**Python-Zugriff:**

```python
import sqlite3
conn = sqlite3.connect('data/telephony.db')
cursor = conn.cursor()

# Alle Kontakte mit Tag "vip"
cursor.execute("""
    SELECT name, phone_number, call_count 
    FROM contacts 
    WHERE tags LIKE '%vip%'
    ORDER BY call_count DESC
""")

for row in cursor.fetchall():
    print(row)
```

---

## Troubleshooting

### Problem: Bria verbindet nicht

**Lösung:**

- SIP-Server-Adresse prüfen
- Credentials überprüfen
- Firewall-Einstellungen (Port 5060 UDP)

### Problem: Bulk-Import schlägt fehl

**Lösung:**

- CSV-Format überprüfen (UTF-8 encoding)
- Spaltenname genau "name" und "phone_number"
- Pandas installiert? `pip install pandas openpyxl`

### Problem: Whisper-Transkription fehlt

**Lösung:**

```bash
pip install openai-whisper
```

### Problem: Sentiment-Score immer 0

**Lösung:**

- Anruf muss Kundennachrichten enthalten
- Keywords werden nur in CUSTOMER-Nachrichten gesucht
- Mehr Konversation = bessere Analyse

---

## Keyboard Shortcuts (in UI)

**Keine definierten Shortcuts**, aber schnelle Navigation:

1. **Tab** - Zwischen Feldern wechseln
2. **Enter** - Button aktivieren (wenn fokussiert)
3. **Strg+C** - Generierten Code kopieren

---

## Best Practices

### 1. Kontakte taggen

Immer aussagekräftige Tags verwenden:

- `lead` - Neuer Lead
- `customer` - Bestandskunde
- `vip` - Wichtiger Kunde
- `hot` - Heißer Lead
- `pv` - PV-Interesse
- `wp` - Wärmepumpen-Interesse

### 2. Anrufe dokumentieren

Immer während/nach Anruf:

```python
update_call_summary('Wichtige Info hier')
```

### 3. Follow-ups setzen

Nie vergessen:

```python
schedule_follow_up(call_id, date, action)
```

### 4. Regelmäßig Analytics prüfen

Wöchentlich:

```python
get_call_analytics(7)
```

### 5. Call-Skripte nutzen

Für konsistente Qualität:

```python
get_call_script('Verkauf')
```

---

## Nächste Schritte

1. **Bria SDK integrieren** (aktuell Mock)
2. **Echte CRM-Integration** (crm.py anbinden)
3. **Calendar-Integration** (Follow-ups als Events)
4. **Email-Benachrichtigungen** bei Follow-ups
5. **Erweiterte Analytics** (Charts, Trends)
6. **IVR-System** für eingehende Anrufe
7. **Call-Queue** mit Priorisierung
8. **Team-Features** (Multi-Agent)

---

## Support

**Dokumentation:**

- `TELEPHONY_MEGA_EXTENSION.md` - Vollständige Doku
- `Agent/README.md` - A.G.E.N.T. Grundlagen

**Fragen?**

- Prüfe die Logs: `agent.logging_config`
- Teste mit kleinen Beispielen
- Prüfe Datenbank: `data/telephony.db`

---

**Version:** 2.0.0  
**Letzte Aktualisierung:** 2024-01-14  
**Features:** 36 Tools, 5 UI Tabs, 3 DB Tabellen
