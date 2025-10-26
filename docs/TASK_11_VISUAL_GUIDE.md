# Task 11: UI-Theme-Einstellungen - Visual Guide

**Visueller Leitfaden für die implementierte Funktionalität**

---

## UI-Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚙️ PDF & Design Einstellungen                                      │
├─────────────────────────────────────────────────────────────────────┤
│  [🎨 PDF-Design] [📊 Diagramm-Farben] [🖼️ UI-Themes] [📄 Templates] │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🖼️ UI-Theme-System                                                 │
│  Wählen Sie ein Theme für die Benutzeroberfläche oder erstellen    │
│  Sie ein eigenes.                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐   │
│  │  EINSTELLUNGEN (2/3)         │  │  VORSCHAU (1/3)          │   │
│  │                              │  │                          │   │
│  │  🎨 Theme-Auswahl            │  │  👁️ Theme-Vorschau       │   │
│  │  ┌────────────────────────┐  │  │  ┌────────────────────┐ │   │
│  │  │ Verfügbare Themes ▼    │  │  │  │ ┌────────────────┐ │ │   │
│  │  │ • Light Theme          │  │  │  │ │ Header         │ │ │   │
│  │  │ • Dark Theme           │  │  │  │ └────────────────┘ │ │   │
│  │  │ • Corporate Theme      │  │  │  │                    │ │   │
│  │  │ • High Contrast Theme  │  │  │  │ Hauptüberschrift   │ │   │
│  │  │ • Custom Theme         │  │  │  │                    │ │   │
│  │  └────────────────────────┘  │  │  │ Dies ist Text...   │ │   │
│  │                              │  │  │                    │ │   │
│  │  ℹ️ Helles Standard-Theme    │  │  │ ┌────────────────┐ │ │   │
│  │                              │  │  │ │ Secondary Box  │ │ │   │
│  │  [✓ Theme aktivieren]        │  │  │ └────────────────┘ │ │   │
│  │                              │  │  │                    │ │   │
│  │  ─────────────────────────   │  │  │ [Action Button]    │ │   │
│  │                              │  │  │                    │ │   │
│  │  ✏️ Theme-Editor             │  │  │ Footer             │ │   │
│  │  (nur bei Custom Theme)      │  │  └────────────────────┘ │   │
│  │                              │  │                          │   │
│  │  Farben konfigurieren:       │  │  🎨 Farbübersicht ▼      │   │
│  │  ┌──────────┬──────────┐     │  │  • Primärfarbe: #1E3A8A  │   │
│  │  │ 🎨 Primär│ 🎨 Sekund│     │  │  • Sekundärfarbe: #3B82F6│   │
│  │  │ #1E3A8A │ #3B82F6  │     │  │  • Hintergrund: #FFFFFF  │   │
│  │  ├──────────┼──────────┤     │  │  • Textfarbe: #1F2937    │   │
│  │  │ 🎨 Hintgr│ 🎨 Text  │     │  │  • Akzentfarbe: #10B981  │   │
│  │  │ #FFFFFF │ #1F2937  │     │  │                          │   │
│  │  ├──────────┴──────────┤     │  │                          │   │
│  │  │ 🎨 Akzent           │     │  │                          │   │
│  │  │ #10B981             │     │  │                          │   │
│  │  └─────────────────────┘     │  │                          │   │
│  │                              │  │                          │   │
│  │  Theme-Name:                 │  │                          │   │
│  │  [Mein Custom Theme____]     │  │                          │   │
│  │                              │  │                          │   │
│  │  [💾 Theme speichern]        │  │                          │   │
│  │  [🔄 Zurücksetzen]           │  │                          │   │
│  └──────────────────────────────┘  └──────────────────────────┘   │
│                                                                      │
│  📌 Aktuell aktives Theme                                           │
│  ┌──────────────┬──────────────┬──────────────┐                    │
│  │ Theme        │ Typ          │ Farben       │                    │
│  │ Light Theme  │ Vordefiniert │ 🟦🔵🟢       │                    │
│  └──────────────┴──────────────┴──────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Workflow-Diagramme

### Workflow 1: Vordefiniertes Theme aktivieren

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Öffne UI-Themes Tab │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────┐
│ Wähle Theme aus      │
│ Dropdown             │
│ (z.B. Dark Theme)    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Vorschau wird        │
│ automatisch          │
│ aktualisiert         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Klicke "Theme        │
│ aktivieren"          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Theme wird in DB     │
│ gespeichert          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Success-Message      │
│ wird angezeigt       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ UI wird neu geladen  │
│ (st.rerun())         │
└──────┬───────────────┘
       │
       ▼
┌─────────────┐
│    Ende     │
└─────────────┘
```

### Workflow 2: Custom Theme erstellen

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Wähle "Custom Theme"│
│ aus Dropdown         │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────┐
│ Theme-Editor wird    │
│ angezeigt            │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Passe Farben mit     │
│ Color Pickern an     │
│ (5 Farben)           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Vorschau             │
│ aktualisiert sich    │
│ live                 │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Gib Theme-Namen ein  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Klicke "Theme        │
│ speichern"           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Custom Theme wird    │
│ gespeichert &        │
│ aktiviert            │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Success-Message      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ UI wird neu geladen  │
└──────┬───────────────┘
       │
       ▼
┌─────────────┐
│    Ende     │
└─────────────┘
```

---

## Theme-Vorschau Beispiele

### Light Theme (Standard)

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │ 🔵 Header (Primary: #1E3A8A)   │ │
│ └────────────────────────────────┘ │
│                                    │
│ 🔵 Hauptüberschrift (Primary)      │
│                                    │
│ 🔷 Unterüberschrift (Secondary)    │
│                                    │
│ ⬛ Dies ist Fließtext in der       │
│    Textfarbe #1F2937               │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ 🔷 Sekundäres Element          │ │
│ │    (Secondary: #3B82F6)        │ │
│ └────────────────────────────────┘ │
│                                    │
│ [🟢 Action Button (Accent)]        │
│                                    │
│ ────────────────────────────────── │
│ Footer / Zusatzinformationen       │
└────────────────────────────────────┘
```

### Dark Theme

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │ 🔵 Header (Primary: #60A5FA)   │ │
│ └────────────────────────────────┘ │
│                                    │
│ 🔵 Hauptüberschrift (Primary)      │
│                                    │
│ 🔷 Unterüberschrift (Secondary)    │
│                                    │
│ ⬜ Dies ist Fließtext in der       │
│    Textfarbe #F9FAFB (hell)        │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ 🔷 Sekundäres Element          │ │
│ │    (Secondary: #3B82F6)        │ │
│ └────────────────────────────────┘ │
│                                    │
│ [🟢 Action Button (Accent)]        │
│                                    │
│ ────────────────────────────────── │
│ Footer / Zusatzinformationen       │
└────────────────────────────────────┘
Hintergrund: #1F2937 (dunkel)
```

### Corporate Theme

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │ 🔵 Header (Primary: #1E40AF)   │ │
│ └────────────────────────────────┘ │
│                                    │
│ 🔵 Hauptüberschrift (Navy Blue)    │
│                                    │
│ ⬛ Unterüberschrift (Gray)          │
│                                    │
│ ⬛ Dies ist Fließtext in der       │
│    Textfarbe #111827               │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ ⬛ Sekundäres Element (Gray)    │ │
│ └────────────────────────────────┘ │
│                                    │
│ [🟢 Action Button (Teal)]          │
│                                    │
│ ────────────────────────────────── │
│ Footer / Zusatzinformationen       │
└────────────────────────────────────┘
Hintergrund: #F9FAFB (hellgrau)
```

### High Contrast Theme

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │ ⬛ Header (Primary: #000000)    │ │
│ └────────────────────────────────┘ │
│                                    │
│ ⬛ Hauptüberschrift (Schwarz)       │
│                                    │
│ ⬛ Unterüberschrift (Dunkelgrau)    │
│                                    │
│ ⬛ Dies ist Fließtext in der       │
│    Textfarbe #000000 (schwarz)     │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ ⬛ Sekundäres Element           │ │
│ └────────────────────────────────┘ │
│                                    │
│ [🔴 Action Button (Rot)]           │
│                                    │
│ ────────────────────────────────── │
│ Footer / Zusatzinformationen       │
└────────────────────────────────────┘
Hintergrund: #FFFFFF (weiß)
```

---

## Color Picker Interface

```
┌─────────────────────────────────────┐
│  Farben konfigurieren:              │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┬──────────────┐   │
│  │ Primärfarbe  │ Sekundärfarbe│   │
│  │              │              │   │
│  │  ┌────────┐  │  ┌────────┐  │   │
│  │  │ 🎨     │  │  │ 🎨     │  │   │
│  │  │#1E3A8A │  │  │#3B82F6 │  │   │
│  │  └────────┘  │  └────────┘  │   │
│  │              │              │   │
│  │ Hauptfarbe   │ Sekundäre    │   │
│  │ für wichtige │ Farbe für    │   │
│  │ UI-Elemente  │ UI-Elemente  │   │
│  └──────────────┴──────────────┘   │
│                                     │
│  ┌──────────────┬──────────────┐   │
│  │ Hintergrund  │ Textfarbe    │   │
│  │              │              │   │
│  │  ┌────────┐  │  ┌────────┐  │   │
│  │  │ 🎨     │  │  │ 🎨     │  │   │
│  │  │#FFFFFF │  │  │#1F2937 │  │   │
│  │  └────────┘  │  └────────┘  │   │
│  │              │              │   │
│  │ Hintergrund- │ Haupttext-   │   │
│  │ farbe der    │ farbe        │   │
│  │ Anwendung    │              │   │
│  └──────────────┴──────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Akzentfarbe                 │   │
│  │                             │   │
│  │  ┌────────┐                 │   │
│  │  │ 🎨     │                 │   │
│  │  │#10B981 │                 │   │
│  │  └────────┘                 │   │
│  │                             │   │
│  │ Farbe für Hervorhebungen    │   │
│  │ und Aktionen                │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Farbübersicht-Expander

```
┌─────────────────────────────────────┐
│  🎨 Farbübersicht ▼                 │
├─────────────────────────────────────┤
│                                     │
│  Primärfarbe: #1E3A8A               │
│  ████████████████████████           │
│                                     │
│  Sekundärfarbe: #3B82F6             │
│  ████████████████████████           │
│                                     │
│  Hintergrundfarbe: #FFFFFF          │
│  ░░░░░░░░░░░░░░░░░░░░░░░░           │
│                                     │
│  Textfarbe: #1F2937                 │
│  ████████████████████████           │
│                                     │
│  Akzentfarbe: #10B981               │
│  ████████████████████████           │
│                                     │
└─────────────────────────────────────┘
```

---

## Aktuell aktives Theme Info

```
┌─────────────────────────────────────────────────────────┐
│  📌 Aktuell aktives Theme                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │ Theme        │ Typ          │ Farben           │    │
│  ├──────────────┼──────────────┼──────────────────┤    │
│  │ Light Theme  │ Vordefiniert │ 🟦 🔵 🟢        │    │
│  └──────────────┴──────────────┴──────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Buttons und Aktionen

### Theme aktivieren

```
┌─────────────────────────┐
│ ✓ Theme aktivieren      │
└─────────────────────────┘
```

**Aktion:**

- Speichert ausgewähltes Theme in Datenbank
- Zeigt Success-Message
- Lädt UI neu

### Theme speichern (Custom)

```
┌─────────────────────────┐
│ 💾 Theme speichern      │
└─────────────────────────┘
```

**Aktion:**

- Speichert Custom Theme in Datenbank
- Aktiviert Custom Theme
- Zeigt Success-Message
- Lädt UI neu

### Zurücksetzen

```
┌─────────────────────────┐
│ 🔄 Zurücksetzen         │
└─────────────────────────┘
```

**Aktion:**

- Setzt auf Light Theme zurück
- Zeigt Success-Message
- Lädt UI neu

---

## Success/Error Messages

### Success

```
┌─────────────────────────────────────────┐
│ ✅ Theme 'Dark Theme' erfolgreich       │
│    aktiviert!                           │
└─────────────────────────────────────────┘
```

### Error

```
┌─────────────────────────────────────────┐
│ ❌ Fehler beim Aktivieren des Themes.   │
└─────────────────────────────────────────┘
```

---

## Verwendungsbeispiel

### Schritt-für-Schritt: Dark Theme aktivieren

1. **Öffne Admin-Panel**

   ```
   Navigiere zu: Admin-Panel → PDF & Design Einstellungen
   ```

2. **Wähle UI-Themes Tab**

   ```
   Klicke auf: 🖼️ UI-Themes
   ```

3. **Wähle Dark Theme**

   ```
   Dropdown: Verfügbare Themes ▼
   Auswahl: Dark Theme
   ```

4. **Prüfe Vorschau**

   ```
   Rechtes Panel zeigt Dark Theme Vorschau
   ```

5. **Aktiviere Theme**

   ```
   Klicke: ✓ Theme aktivieren
   ```

6. **Bestätigung**

   ```
   ✅ Theme 'Dark Theme' erfolgreich aktiviert!
   ```

---

## Technische Details

### Datenfluss

```
┌─────────────┐
│ UI Input    │
│ (Streamlit) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ render_ui_theme_    │
│ settings()          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ save_setting()      │
│ (Database)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ admin_settings      │
│ Tabelle             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ st.rerun()          │
│ (UI Reload)         │
└─────────────────────┘
```

### Datenbankstruktur

```
admin_settings
├─ setting_key: "ui_theme_settings"
└─ setting_value: {
     "active_theme": "light",
     "theme_config": {
       "name": "Light Theme",
       "primary_color": "#1E3A8A",
       "secondary_color": "#3B82F6",
       "background_color": "#FFFFFF",
       "text_color": "#1F2937",
       "accent_color": "#10B981"
     }
   }
```

---

**Erstellt am:** 2025-01-09  
**Für:** Task 11 Implementation  
**Version:** 1.0
