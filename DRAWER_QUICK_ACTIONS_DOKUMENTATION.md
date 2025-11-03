# Drawer Quick Actions - Vollständige Dokumentation

## Übersicht

Der Drawer (rechts unten im Bildschirm) wurde mit 5 funktionalen Buttons erweitert, die Schnellzugriff auf wichtige Features bieten.

## Features

### 🎤 Button 1: Sprachbefehl
**Funktion:** Aktiviert Sprachsteuerung für den KI-Agent

**Wie es funktioniert:**
- Klick auf Button aktiviert Browser-basierte Spracherkennung
- Nutzer spricht Anfrage ins Mikrofon
- Text wird automatisch an Agent übergeben
- Agent führt Aufgabe aus

**Technische Details:**
- Nutzt Web Speech API (Browser-native)
- Fallback auf manuelle Eingabe wenn nicht verfügbar
- Unterstützt Deutsch (de-DE)
- Echtzeit-Transkription

**Module:**
- `voice_command.py` - Spracherkennungs-UI und Integration
- `drawer_actions.py::handle_drawer_action_voice_command()`
- Integration in `Agent/agent_ui.py`

---

### 🏠 Button 2: 3D Visualisierung
**Funktion:** Schnellzugriff zum 3D PV-Visualisierungs-Menü

**Wie es funktioniert:**
- Direkter Wechsel zum 3D-Menü
- Prüft ob PV-Berechnung aktiv
- Zeigt Warnung bei Wärmepumpen-Berechnungen

**Warnmeldung:**
> ⚠️ 3D-Visualisierung ist nur für PV-Berechnungen verfügbar, nicht für Wärmepumpen.

**Technische Details:**
- Prüft `st.session_state['active_page']`
- Warnung wird nur bei Wärmepumpen-Modus angezeigt
- Automatischer Page-Wechsel bei PV-Modus

**Module:**
- `drawer_actions.py::handle_drawer_action_3d_visualization()`
- Notification via `show_drawer_notifications()`

---

### 💾 Button 3: Kunde ins CRM speichern
**Funktion:** Speichert aktuellen Kunden direkt ins CRM

**Wie es funktioniert:**
- Sammelt alle Kundendaten aus Session
- Validiert Mindestanforderungen
- Speichert in CRM-Datenbank
- Verwendet identische Struktur wie manuell erstellte Kunden

**Erforderliche Daten:**
- Mindestens: Vorname ODER Nachname ODER E-Mail
- Optional: Telefon, Adresse, Firma, Notizen

**Session-State Keys:**
- `customer_first_name`
- `customer_last_name`
- `customer_email`
- `customer_phone`
- `customer_street`
- `customer_city`
- `customer_zip`
- `customer_company`
- `customer_notes`

**Feedback:**
- Erfolg: "Kunde erfolgreich gespeichert! (ID: XXX)"
- Fehler: "Bitte geben Sie mindestens Name oder E-Mail ein."

**Technische Details:**
- Nutzt `crm.save_customer()`
- Speichert in `customers` Tabelle
- Generiert automatisch Kunden-ID
- Alle Standard-CRM-Felder werden inkludiert

**Module:**
- `drawer_actions.py::handle_drawer_action_save_customer()`
- `crm.py::save_customer()`
- `database.py::get_connection()`

---

### ⚡ Button 4: Blitz-Angebot
**Funktion:** Erstellt Standard-PDF sofort ohne UI

**Wie es funktioniert:**
- Nutzt aktuelle Session-Daten
- Generiert PDF im Hintergrund
- Speichert in `data/pdf_output/blitz_angebot.pdf`
- Bietet direkten Download an

**Verwendete Daten:**
- `texts` - Textbausteine
- `customer_data` - Kundendaten
- `system_data` - Systemkonfiguration
- `prices` - Preisberechnung
- `economic_data` - Wirtschaftlichkeit
- `calculation_results` - Berechnungsergebnisse
- `heatpump_results` - Wärmepumpen-Daten (optional)
- `admin_settings` - Admin-Einstellungen

**Feedback:**
- Erfolg: Download-Button erscheint automatisch
- Fehler: "PDF-Generierung fehlgeschlagen (keine Daten)"

**Technische Details:**
- Nutzt `pdf_generator.generate_offer_pdf()`
- Standard-Layout (kein Custom-Layout)
- Alle verfügbaren Daten werden inkludiert
- PDF-Bytes werden in Session gespeichert für Download

**Module:**
- `drawer_actions.py::handle_drawer_action_quick_pdf()`
- `pdf_generator.py::generate_offer_pdf()`

---

### ❓ Button 5: Hilfe-Menü
**Funktion:** Umfassende Hilfe & Dokumentation

**Wie es funktioniert:**
- Sammelt ALLE .md Dateien aus:
  - Hauptordner (Root)
  - `docs/` Ordner
- Zeigt in übersichtlicher UI an
- Durchsuchbare Dokumentation

**Features:**
- **Tab 1: Übersicht** - FAQ, Quick Links, häufige Fragen
- **Tab 2: Hauptdokumentation** - Alle MD-Dateien aus Root
- **Tab 3: Detaillierte Docs** - Alle MD-Dateien aus docs/
- Suchfunktion für schnelles Finden
- Expandable-Viewer für jedes Dokument

**Nur über Drawer erreichbar!**
Kein regulärer Menüpunkt - exklusive Hilfe-Seite.

**FAQ Inhalte:**
- Wie erstelle ich ein Angebot?
- Wie speichere ich einen Kunden?
- Wie funktioniert der Blitz-Angebot Button?
- Was macht der Sprachbefehl-Button?

**Technische Details:**
- Nutzt `glob` zum Sammeln aller MD-Dateien
- Rendering mit Streamlit Tabs
- Markdown wird direkt gerendert
- Session-State: `show_help_drawer`

**Module:**
- `drawer_actions.py::render_help_menu()`
- `drawer_actions.py::collect_help_content()`

---

### 🚪 Button 6: Abmelden (UNVERÄNDERT)
Logout-Funktion bleibt erhalten wie zuvor.

---

## Integration

### gui.py
```python
# Drawer-Erstellung mit aktualisierten Buttons
drawer.innerHTML = `
    <button class="drawer-btn" data-action="voice_command">🎤 Sprachbefehl</button>
    <button class="drawer-btn" data-action="3d_view">🏠 3D Visualisierung</button>
    <button class="drawer-btn" data-action="save_customer">💾 Kunde ins CRM</button>
    <button class="drawer-btn" data-action="quick_pdf">⚡ Blitz-Angebot</button>
    <button class="drawer-btn" data-action="help_menu">❓ Hilfe-Menü</button>
    <button class="drawer-btn" data-action="logout">🚪 Abmelden</button>
`;

# Action Handler
if drawer_action == 'voice_command':
    handle_drawer_action_voice_command()
elif drawer_action == '3d_view':
    handle_drawer_action_3d_visualization()
elif drawer_action == 'save_customer':
    handle_drawer_action_save_customer()
elif drawer_action == 'quick_pdf':
    handle_drawer_action_quick_pdf()
elif drawer_action == 'help_menu':
    st.session_state['show_help_drawer'] = True
```

### Neue Module
1. **drawer_actions.py** - Alle Handler-Funktionen
2. **voice_command.py** - Spracherkennungs-Integration

---

## Abhängigkeiten

### Erforderlich:
- `streamlit`
- `sqlite3` (Standard-Lib)
- `pathlib` (Standard-Lib)
- `glob` (Standard-Lib)

### Optional (für Spracherkennung):
- Browser mit Web Speech API Support
  - Chrome ✅
  - Edge ✅
  - Safari ✅ (macOS/iOS)
  - Firefox ❌ (noch nicht vollständig)

### Bestehende Module:
- `crm.py` - CRM-Funktionen
- `database.py` - Datenbankzugriff
- `pdf_generator.py` - PDF-Generierung
- `Agent/agent_ui.py` - Agent-Interface

---

## Fehlerbehandlung

Alle Funktionen haben robuste Fehlerbehandlung:

1. **Sprachbefehl**: Fallback bei fehlender Browser-Unterstützung
2. **3D Visualisierung**: Warnmeldung bei falschem Modus
3. **Kunde speichern**: Validierung vor dem Speichern
4. **Blitz-Angebot**: Fehler bei fehlenden Daten
5. **Hilfe-Menü**: Graceful handling wenn keine MD-Dateien gefunden

Feedback wird immer über `show_drawer_notifications()` angezeigt.

---

## Testing

### Manuelle Tests durchgeführt:
✅ Drawer öffnet/schließt korrekt
✅ Alle 5 neuen Buttons haben korrekte Labels
✅ Actions werden an Streamlit weitergeleitet
✅ Keine Syntax-Fehler in allen Modulen
✅ Import-Pfade korrekt
✅ Session-State wird nicht überschrieben
✅ Bestehende Features bleiben unberührt

### Test-Szenarien:
1. Button 1: Sprachbefehl aktiviert Agent
2. Button 2: Warnung bei Wärmepumpe, Wechsel bei PV
3. Button 3: Kunde wird gespeichert mit allen Daten
4. Button 4: PDF wird erstellt und Download angeboten
5. Button 5: Hilfe-Seite wird angezeigt
6. Button 6: Logout funktioniert wie zuvor

---

## Deployment

Dateien wurden in beide Locations kopiert:
- Root: `c:\Users\win10\Desktop\Bokuk2 - Kopie\`
- Build: `c:\Users\win10\Desktop\Bokuk2 - Kopie\BOKUK_BUILD\app\`

### Checklist für Deployment:
- [x] drawer_actions.py in Root & Build
- [x] voice_command.py in Root & Build
- [x] gui.py aktualisiert
- [x] Agent/agent_ui.py aktualisiert
- [x] Keine Syntax-Fehler
- [x] Alle Imports verfügbar
- [x] Session-State Keys dokumentiert

---

## Zukünftige Erweiterungen

### Mögliche Verbesserungen:
1. **Offline-Spracherkennung** (via Whisper lokal)
2. **PDF-Vorschau** im Blitz-Angebot
3. **CRM-Duplikat-Erkennung** vor Speicherung
4. **Hilfe-Suche** mit Highlighting
5. **Voice-Feedback** (Text-to-Speech)

---

## Support

Bei Problemen:
1. Prüfe Browser-Kompatibilität (Sprachbefehl)
2. Stelle sicher, dass alle Module importierbar sind
3. Überprüfe Session-State auf erforderliche Keys
4. Siehe Fehler-Log in Streamlit-Console

**Erstellt:** 31.10.2025
**Version:** 1.0.0
**Status:** ✅ Produktionsbereit
