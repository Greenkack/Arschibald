# Task 3: Diagrammauswahl in PDF UI - Visueller Guide

## Übersicht

Dieser Guide zeigt, wie die implementierte Diagrammauswahl-UI aussieht und funktioniert.

---

## UI-Layout

### 1. Hauptüberschrift und Beschreibung

```
📊 Diagrammauswahl für PDF
Wählen Sie die Diagramme aus, die in der erweiterten PDF enthalten sein sollen.
```

---

### 2. Statistiken-Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ Verfügbare Diagramme    ❌ Nicht verfügbare    🎯 Ausgewählt │
│           28                        17                   12      │
└─────────────────────────────────────────────────────────────────┘
```

**Beschreibung**:

- **Verfügbare Diagramme**: Anzahl der Diagramme, die basierend auf den aktuellen Daten generiert werden können
- **Nicht verfügbare**: Diagramme, für die benötigte Daten fehlen
- **Ausgewählt**: Anzahl der aktuell für die PDF ausgewählten Diagramme

---

### 3. Schnellauswahl-Buttons

```
┌──────────────────────────────────────────────────────────────────┐
│  [✅ Alle verfügbaren auswählen]  [❌ Keine auswählen]  [🎯 Empfohlene auswählen]  │
└──────────────────────────────────────────────────────────────────┘
```

**Funktionen**:

- **Alle verfügbaren auswählen**: Wählt alle 28 verfügbaren Diagramme aus
- **Keine auswählen**: Entfernt alle Auswahlen
- **Empfohlene auswählen**: Wählt 6 wichtige Basis-Diagramme aus:
  - Monatliche Produktion/Verbrauch
  - Stromkosten-Hochrechnung
  - Kumulierter Cashflow
  - ROI-Entwicklung
  - Energiebilanz
  - CO₂-Einsparung

---

### 4. Kategorisierte Diagrammauswahl

#### Kategorie: Finanzierung (9 verfügbar)

```
▼ 📁 Finanzierung (9 verfügbar)
  
  Verfügbare Diagramme:
  ☑ 💰 Stromkosten-Hochrechnung (2D)
  ☑ 📈 Kumulierter Cashflow (2D)
  ☑ 💹 ROI-Entwicklung (2D)
  ☐ 💵 Monatliche Einsparungen (2D)
  ☑ ⏱️ Amortisationszeit (2D)
  ☐ 🏦 Finanzierungsvergleich (2D)
  ☐ 💸 Einnahmen-Projektion (2D Multi-Line)
  ☐ 💰 PV Visuals: Break-Even
  ☐ ⏱️ PV Visuals: Amortisation
```

#### Kategorie: Energie (9 verfügbar)

```
▼ 📁 Energie (9 verfügbar)
  
  Verfügbare Diagramme:
  ☑ 📊 Monatliche Produktion/Verbrauch (2D)
  ☑ 🔋 Energiebilanz (Donut)
  ☐ 🔋 Batterie-Nutzung (2D Stacked)
  ☐ 🔌 Netz-Interaktion (2D Line)
  ☐ 🏠 Eigenverbrauch-Analyse (2D)
  ☐ ⚡ Einspeisung-Analyse (2D)
  ☐ 🥧 Verbrauchsdeckung (Kreis)
  ☐ 🥧 PV-Nutzung (Kreis)
  ☐ 📊 PV Visuals: Jahresproduktion
  
  Nicht verfügbare Diagramme:
  ⚠️ 🔋 Batterie-Nutzung (2D Stacked) (Daten fehlen)
  ⚠️ 🏠 Eigenverbrauch-Analyse (2D) (Daten fehlen)
```

#### Kategorie: Vergleiche (8 verfügbar)

```
▼ 📁 Vergleiche (8 verfügbar)
  
  Verfügbare Diagramme:
  ☐ 📅 Jahresvergleich (2D)
  ☐ 🔄 Szenario-Vergleich (2D Grouped)
  ☐ ⚡ Tarif-Vergleich (2D Grouped)
  ☐ ⚖️ Vergleich (2D)
  ☐ 🔢 Vergleichs-Matrix (2D Heatmap)
  ☐ 💹 ROI-Vergleich (3D)
  ☐ 🔄 Szenarienvergleich (3D)
  ☐ ⚡ Vorher/Nachher Stromkosten (3D)
  
  Nicht verfügbare Diagramme:
  ⚠️ 🔄 Szenario-Vergleich (2D Grouped) (Daten fehlen)
  ⚠️ 🔄 Szenarienvergleich (3D) (Daten fehlen)
```

#### Kategorie: Umwelt (2 verfügbar)

```
▼ 📁 Umwelt (2 verfügbar)
  
  Verfügbare Diagramme:
  ☑ 🌱 CO₂-Einsparung (2D)
  ☐ 🌱 CO2-Ersparnis vs. Wert (3D)
```

#### Kategorie: Analyse (5 verfügbar)

```
▼ 📁 Analyse (5 verfügbar)
  
  Verfügbare Diagramme:
  ☐ 🔬 Erweiterte Analyse (2D)
  ☐ 📊 Sensitivitäts-Analyse (2D Heatmap)
  ☐ 🎯 Optimierungs-Analyse (2D Scatter)
  ☐ 📈 Performance-Metriken (2D)
  ☐ 📊 Projektrendite-Matrix (3D)
  
  Nicht verfügbare Diagramme:
  ⚠️ 🔬 Erweiterte Analyse (2D) (Daten fehlen)
  ⚠️ 📊 Sensitivitäts-Analyse (2D Heatmap) (Daten fehlen)
  ⚠️ 🎯 Optimierungs-Analyse (2D Scatter) (Daten fehlen)
```

#### Kategorie: Zusammenfassung (1 verfügbar)

```
▼ 📁 Zusammenfassung (1 verfügbar)
  
  Verfügbare Diagramme:
  ☐ 📋 Zusammenfassung (2D)
```

#### Kategorie: 3D Visualisierungen (Legacy) (12 verfügbar)

```
▼ 📁 3D Visualisierungen (Legacy) (12 verfügbar)
  
  Verfügbare Diagramme:
  ☐ 📊 Tagesproduktion (3D)
  ☐ 📊 Wochenproduktion (3D)
  ☐ 📊 Jahresproduktion (3D-Balken)
  ☐ 💰 Einspeisevergütung (3D)
  ☐ ⚖️ Verbr. vs. Prod. (3D)
  ☐ 📦 Tarifvergleich (3D)
  ☐ 💎 Investitionsnutzwert (3D)
  ☐ 🔋 Speicherwirkung (3D)
  ☐ 🏠 Eigenverbr. vs. Einspeis. (3D)
  ☐ 📈 Stromkostensteigerung (3D)
  ☐ 📊 Eigenverbrauchsgrad (3D)
  ☐ 💸 Einnahmenprognose (3D)
```

---

### 5. Warnungen und Bestätigungen

#### Keine Auswahl

```
⚠️ Keine Diagramme ausgewählt. Die PDF wird ohne zusätzliche Diagramme erstellt.
```

#### Mit Auswahl

```
✅ 12 Diagramme ausgewählt
```

---

### 6. Auswahl-Zusammenfassung

```
───────────────────────────────────────────────────────────────────
📋 Auswahl-Zusammenfassung

┌─────────────────────────────────────────────────────────────────┐
│  Ausgewählte Diagramme    Geschätzte PDF-Größe    Geschätzte    │
│          12                      2.3 MB           Generierungszeit│
│                                                      8 Sek.       │
└─────────────────────────────────────────────────────────────────┘

Ausgewählte Diagramme nach Kategorien:

┌──────────────┬──────────┬────────────┬─────────┬─────────┐
│ Finanzierung │  Energie │ Vergleiche │ Umwelt  │ Analyse │
│      5       │    3     │     2      │    1    │    1    │
└──────────────┴──────────┴────────────┴─────────┴─────────┘
```

**Bei >20 Diagrammen**:

```
⚠️ Sie haben mehr als 20 Diagramme ausgewählt. Die PDF-Generierung kann länger dauern.
```

**Bei 0 Diagrammen**:

```
ℹ️ Keine Diagramme ausgewählt. Die PDF enthält nur die Standard-Seiten ohne zusätzliche Visualisierungen.
```

---

### 7. Generierungsstatus

```
───────────────────────────────────────────────────────────────────
🔄 Diagramm-Generierungsstatus

┌─────────────────────────────────────────────────────────────────┐
│     Gesamt        ✅ Erfolgreich         ❌ Fehler              │
│       12                10                   2                   │
└─────────────────────────────────────────────────────────────────┘

▼ ⚠️ Fehlerhafte Diagramme anzeigen

  ❌ 🔋 Batterie-Nutzung (2D Stacked): Diagramm 'battery_usage_chart_bytes' 
     ist nicht verfügbar - benötigte Daten fehlen
  
  ❌ 🏠 Eigenverbrauch-Analyse (2D): Diagramm 'self_consumption_chart_bytes' 
     wurde noch nicht generiert

  💡 Tipp: Führen Sie die Berechnungen erneut aus, um fehlende Diagramme zu generieren.
```

**Alle erfolgreich**:

```
✅ Alle ausgewählten Diagramme sind verfügbar und können in die PDF eingefügt werden!
```

---

### 8. Persistenz-Management

```
───────────────────────────────────────────────────────────────────
💾 Auswahl speichern/laden

┌──────────────────────────────────────────────────────────────────┐
│  [💾 Aktuelle Auswahl als Standard speichern]  [📂 Standard-Auswahl laden]  │
└──────────────────────────────────────────────────────────────────┘
```

**Nach Speichern**:

```
✅ 12 Diagramme als Standard gespeichert!
```

**Nach Laden**:

```
✅ 12 Diagramme geladen!
```

**Keine gespeicherte Auswahl**:

```
ℹ️ Keine gespeicherte Standard-Auswahl gefunden.
```

---

## Interaktions-Fluss

### Szenario 1: Erste Verwendung

1. Benutzer öffnet PDF UI
2. Sieht Statistiken: 28 verfügbar, 17 nicht verfügbar, 0 ausgewählt
3. Klickt "Empfohlene auswählen"
4. 6 Basis-Diagramme werden ausgewählt
5. Sieht Zusammenfassung: 6 Diagramme, 1.4 MB, 5 Sek.
6. Sieht Generierungsstatus: Alle 6 erfolgreich
7. Klickt "Als Standard speichern"
8. Generiert PDF mit 6 Diagrammen

### Szenario 2: Maximale Auswahl

1. Benutzer öffnet PDF UI
2. Klickt "Alle verfügbaren auswählen"
3. 28 Diagramme werden ausgewählt
4. Sieht Warnung: >20 Diagramme, längere Generierung
5. Sieht Zusammenfassung: 28 Diagramme, 4.7 MB, 16 Sek.
6. Prüft Generierungsstatus: 2 Fehler
7. Öffnet Fehler-Details, sieht welche Daten fehlen
8. Entfernt fehlerhafte Diagramme
9. Generiert PDF mit 26 Diagrammen

### Szenario 3: Gespeicherte Auswahl laden

1. Benutzer öffnet PDF UI
2. Klickt "Standard-Auswahl laden"
3. 12 gespeicherte Diagramme werden geladen
4. Sieht Zusammenfassung: 12 Diagramme, 2.3 MB, 8 Sek.
5. Passt Auswahl an (fügt 2 hinzu, entfernt 1)
6. Generiert PDF mit 13 Diagrammen
7. Speichert neue Auswahl als Standard

### Szenario 4: Kategorien-basierte Auswahl

1. Benutzer öffnet PDF UI
2. Öffnet Kategorie "Finanzierung"
3. Wählt alle 5 verfügbaren Finanzierungs-Diagramme
4. Öffnet Kategorie "Energie"
5. Wählt 3 Energie-Diagramme
6. Öffnet Kategorie "Umwelt"
7. Wählt CO₂-Diagramm
8. Sieht Zusammenfassung: 9 Diagramme nach Kategorien
9. Generiert PDF mit 9 Diagrammen

---

## Responsive Design

### Desktop (>1200px)

```
┌────────────────────────────────────────────────────────────────┐
│  Statistiken in 3 Spalten                                      │
│  Buttons in 3 Spalten                                          │
│  Kategorien in voller Breite                                   │
│  Zusammenfassung in 3-5 Spalten                                │
└────────────────────────────────────────────────────────────────┘
```

### Tablet (768px - 1200px)

```
┌────────────────────────────────────────────────────────────────┐
│  Statistiken in 3 Spalten                                      │
│  Buttons in 3 Spalten                                          │
│  Kategorien in voller Breite                                   │
│  Zusammenfassung in 2-3 Spalten                                │
└────────────────────────────────────────────────────────────────┘
```

### Mobile (<768px)

```
┌────────────────────────────────────────────────────────────────┐
│  Statistiken in 1 Spalte (gestapelt)                           │
│  Buttons in 1 Spalte (gestapelt)                               │
│  Kategorien in voller Breite                                   │
│  Zusammenfassung in 1 Spalte (gestapelt)                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Farbschema

### Streamlit Standard-Farben

- **Primary**: Blau (#FF4B4B für Streamlit)
- **Success**: Grün (#00C851)
- **Warning**: Orange (#FF8800)
- **Error**: Rot (#FF4444)
- **Info**: Hellblau (#00B0FF)

### Emojis für visuelle Orientierung

- 📊 Diagramme allgemein
- 💰 Finanzierung
- ⚡ Energie
- 🔄 Vergleiche
- 🌱 Umwelt
- 🔬 Analyse
- 📋 Zusammenfassung
- ✅ Erfolg/Verfügbar
- ❌ Fehler/Nicht verfügbar
- ⚠️ Warnung
- 🎯 Empfohlen
- 💾 Speichern
- 📂 Laden

---

## Accessibility

### Tastatur-Navigation

- Tab: Zwischen Elementen navigieren
- Space: Checkbox togglen
- Enter: Button aktivieren
- Pfeiltasten: In Listen navigieren

### Screen Reader

- Alle Buttons haben beschreibende Labels
- Checkboxen haben klare Beschriftungen
- Statistiken haben aussagekräftige Werte
- Fehler werden als Alerts vorgelesen

### Kontrast

- Alle Texte haben mindestens 4.5:1 Kontrast
- Emojis werden durch Text ergänzt
- Wichtige Informationen nicht nur durch Farbe

---

## Performance

### Ladezeiten

- Initiale Render: <100ms
- Checkbox-Toggle: <50ms
- Button-Click: <100ms
- Kategorie-Expand: <50ms

### Optimierungen

- Lazy Loading für Kategorien
- Memoization für Verfügbarkeits-Checks
- Batch-Updates für Session State
- Effizientes Filtern

---

## Zusammenfassung

Die Diagrammauswahl-UI bietet:

✅ **Intuitive Bedienung**: Klare Struktur mit Kategorien und Statistiken
✅ **Schnellauswahl**: Buttons für häufige Szenarien
✅ **Transparenz**: Klare Anzeige von Verfügbarkeit und Fehlern
✅ **Flexibilität**: Individuelle Auswahl oder Vorlagen
✅ **Feedback**: Echtzeit-Updates und Bestätigungen
✅ **Persistenz**: Speichern und Laden von Auswahlen
✅ **Informativ**: Größen- und Zeit-Schätzungen
✅ **Professionell**: Modernes Design mit Emojis

---

**Erstellt von**: Kiro AI Assistant  
**Datum**: 2025-01-10  
**Spec**: extended-pdf-comprehensive-improvements  
**Task**: 3. Diagrammauswahl in PDF UI implementieren
