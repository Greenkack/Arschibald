# Task 7: Visual Preview - Admin Panel Integration

## Was der Benutzer sehen wird

### 1. Admin Panel Menü

Wenn der Administrator das Admin Panel öffnet, sieht er jetzt einen neuen Menüpunkt:

```
🏢 Firmenverwaltung
👥 Benutzerverwaltung
📦 Produktverwaltung
🖼️ Logo-Verwaltung
🗄️ Produktdatenbank
🔧 PV-Unterkonstruktionen
🛠️ Dienstleistungen Management
📊 Preis Matrix                    ← NEU!
⚙️ Allgemeine Einstellungen
🎬 Intro-Einstellungen
💡 Einspeisung Tarifverwaltung
🔥 Wärmepumpen-Einstellungen
📝 PDF-Design Einstellungen
💳 Zahlungsbedingungen Einstellungen
📊 Anzeigeeinstellungen
📋 Build Infos
🔐 Sicherheitseinstellungen
🧠 Erweiterte Einstellungen
```

### 2. Tooltip beim Hover

Wenn der Benutzer mit der Maus über "Preis Matrix" fährt:

```
📊 Preis Matrix
Excel-ähnliche Preismatrizen erstellen und verwalten
```

### 3. Platzhalter-Ansicht (bis Task 8 implementiert ist)

Wenn der Benutzer auf "Preis Matrix" klickt, sieht er:

```
📊 Preis Matrix Verwaltung

ℹ️ Die Excel-Grid-Oberfläche wird in einer späteren Phase implementiert.
   Hier können Sie zukünftig Excel-ähnliche Preismatrizen erstellen und verwalten.

Geplante Features:
✅ Excel-ähnliche Grid-Oberfläche
✅ Formel-Unterstützung (SUM, AVERAGE, VLOOKUP, etc.)
✅ Import/Export (CSV, XLS, XLSX)
✅ Dynamische Tabellengröße
✅ Undo/Redo Funktionalität
✅ Integration mit Produktpreisen

───────────────────────────────────────────────────────────
Modul: excel_grid_ui.py (wird in Task 8 implementiert)
```

### 4. Nach Task 8 (Excel Grid UI)

Nach Implementierung von Task 8 wird der Benutzer sehen:

```
📊 Preis Matrix Verwaltung

┌─────────────────────────────────────────────────────────┐
│ Matrix auswählen: [Dropdown ▼]                          │
│                                                          │
│ [Neue Matrix] [Speichern] [Laden] [Import] [Export]    │
│                                                          │
│ Formelleiste: =                                         │
│                                                          │
│ ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐             │
│ │   │ A │ B │ C │ D │ E │ F │ G │ H │ I │             │
│ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤             │
│ │ 1 │   │   │   │   │   │   │   │   │   │             │
│ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤             │
│ │ 2 │   │   │   │   │   │   │   │   │   │             │
│ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤             │
│ │ 3 │   │   │   │   │   │   │   │   │   │             │
│ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘             │
└─────────────────────────────────────────────────────────┘
```

## Navigation Flow

```
Hauptmenü
    │
    ├─ A) Wirtschaftlichkeit
    ├─ B) Wärmepumpe
    ├─ C) Angebote
    ├─ D) Finanztools
    ├─ E) CRM
    └─ F) Administration ← Hier
           │
           ├─ Firmenverwaltung
           ├─ Benutzerverwaltung
           ├─ Produktverwaltung
           ├─ Logo-Verwaltung
           ├─ Produktdatenbank
           ├─ PV-Unterkonstruktionen
           ├─ Dienstleistungen Management
           ├─ Preis Matrix ← NEU! Task 7
           │     │
           │     └─ Excel Grid UI (Task 8)
           │           │
           │           ├─ Formelleiste (Task 9)
           │           ├─ Grid Features (Task 10)
           │           ├─ Matrix-Verwaltung (Task 11)
           │           ├─ Speichern/Laden (Task 12)
           │           ├─ Import (Task 13-14)
           │           └─ Export (Task 15)
           │
           ├─ Allgemeine Einstellungen
           ├─ Intro-Einstellungen
           └─ ... weitere Tabs
```

## State-Management

Der Tab-Zustand wird in `st.session_state` gespeichert:

```python
st.session_state = {
    'admin_active_tab_key': 'admin_tab_price_matrix',  # Aktiver Tab
    'admin_active_tab_key_last_change': '2025-11-07T...',  # Zeitstempel
    # ... weitere Session-Daten
}
```

## Sicherheit

Der Tab ist über das Security-System geschützt:

```python
# In render_admin_panel()
area_id = "price_matrix"  # Aus tab_to_area_map
if not require_admin_auth(area_id, "Preis Matrix"):
    return  # Zeige Passwort-Dialog
```

## Technische Details

### Rendering-Reihenfolge

1. `render_admin_panel()` wird aufgerufen
2. `_render_horizontal_menu_selector()` zeigt Menü
3. Benutzer klickt auf "Preis Matrix"
4. `st.session_state['admin_active_tab_key']` = `'admin_tab_price_matrix'`
5. `tab_functions_map['admin_tab_price_matrix']()` wird aufgerufen
6. `render_price_matrix_tab()` wird ausgeführt
7. Versucht `excel_grid_ui.render_excel_grid_ui()` zu laden
8. Falls nicht verfügbar: Zeigt Platzhalter

### Fehlerbehandlung

```python
try:
    from excel_grid_ui import render_excel_grid_ui
    render_excel_grid_ui()
except ImportError:
    # Zeige Platzhalter
    st.info("Modul wird in Task 8 implementiert...")
except Exception as e:
    # Zeige Fehler
    st.error(f"Fehler: {e}")
    st.text(traceback.format_exc())
```

## Zusammenfassung

Task 7 schafft die **Grundlage** für die Excel-Integration:

✅ **Navigation**: Neuer Tab im Admin Panel  
✅ **Struktur**: Alle Konfigurationen (Icons, Labels, Descriptions)  
✅ **Render-Funktion**: Bereit für Excel-Grid-UI  
✅ **State-Management**: Session-State-Integration  
✅ **Sicherheit**: Security-Mapping  
✅ **Fehlerbehandlung**: Graceful Fallback  

Die eigentliche Excel-Funktionalität wird in den folgenden Tasks implementiert.
