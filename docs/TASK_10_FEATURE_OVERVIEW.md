# Task 10: Diagramm-Farbeinstellungen UI - Feature Overview

## 🎨 Was wurde implementiert?

Eine vollständige Admin-UI zur Konfiguration von Diagrammfarben mit drei Hauptbereichen:

---

## 1️⃣ Globale Farbeinstellungen (Task 10.1)

### Features

- **6 Color Picker** für globale Diagrammfarben
- **Live-Vorschau** mit Color Swatches
- **Speichern & Zurücksetzen** Buttons

### Standard-Farben

```
🔵 #1E3A8A - Dark Blue
🔵 #3B82F6 - Blue
🟢 #10B981 - Green
🟠 #F59E0B - Amber
🔴 #EF4444 - Red
🟣 #8B5CF6 - Purple
```

### Verwendung

1. Öffne "📊 Diagramm-Farben" → "🌐 Globale Farben"
2. Wähle 6 Farben mit den Color Pickern
3. Vorschau wird live aktualisiert
4. Klicke "💾 Speichern" zum Persistieren

---

## 2️⃣ Farbpaletten-Bibliothek (Task 10.2)

### Vordefinierte Paletten

#### 🏢 Corporate

*Professionelle Blau-Grau-Töne*

```
#1E3A8A  #3B82F6  #60A5FA  #6B7280  #9CA3AF  #1F2937
```

#### 🌱 Eco

*Nachhaltige Grün-Töne*

```
#065F46  #10B981  #34D399  #6EE7B7  #A7F3D0  #D1FAE5
```

#### ⚡ Energy

*Energiegeladene Orange-Gelb-Töne*

```
#DC2626  #F59E0B  #FBBF24  #FCD34D  #FDE68A  #FEF3C7
```

#### ♿ Accessible

*Farbenblind-freundliche Palette*

```
#0173B2  #DE8F05  #029E73  #CC78BC  #CA9161  #949494
```

### Features

- **Vorschau** jeder Palette mit Color Swatches
- **Farbcode-Anzeige** für jede Palette
- **"Palette anwenden"** Button
- **Aktuelle Palette** wird angezeigt

### Verwendung

1. Öffne "📊 Diagramm-Farben" → "🎨 Farbpaletten"
2. Wähle eine Palette aus
3. Klicke "✓ Palette anwenden"
4. Globale Farben werden sofort aktualisiert

---

## 3️⃣ Individuelle Diagramm-Konfiguration (Task 10.3)

### Kategorien & Diagramme

#### 💰 Wirtschaftlichkeit (6 Diagramme)

- Kumulierter Cashflow
- Stromkosten-Hochrechnung
- Break-Even-Analyse
- Amortisationsdiagramm
- Projektrendite-Matrix
- ROI-Vergleich

#### ⚡ Produktion & Verbrauch (5 Diagramme)

- Monatliche Produktion vs. Verbrauch
- Jahresproduktion
- Tagesproduktion
- Wochenproduktion
- Produktion vs. Verbrauch

#### 🔋 Eigenverbrauch & Autarkie (5 Diagramme)

- Verbrauchsdeckung
- PV-Nutzung
- Speicherwirkung
- Eigenverbrauch vs. Einspeisung
- Eigenverbrauchsgrad

#### 💵 Finanzielle Analyse (5 Diagramme)

- Einspeisevergütung
- Einnahmenprognose
- Tarifvergleich (3D)
- Tarifvergleich
- Stromkostensteigerung

#### 🌍 CO2 & Umwelt (1 Diagramm)

- CO2-Ersparnis vs. Wert

#### 📊 Vergleiche & Szenarien (2 Diagramme)

- Szenarienvergleich
- Investitionsnutzwert

**Gesamt: 24 Diagramme konfigurierbar**

### Features

- **Kategorie-Auswahl** Dropdown
- **Diagramm-Auswahl** Dropdown
- **"Globale Farben verwenden"** Toggle
- **3 Custom-Color-Picker** (Primär, Sekundär, Akzent)
- **Live-Vorschau** der Custom-Farben
- **"Auf Global zurücksetzen"** Button
- **Übersicht** konfigurierter Diagramme

### Verwendung

1. Öffne "📊 Diagramm-Farben" → "⚙️ Individuelle Konfiguration"
2. Wähle eine Kategorie (z.B. "Wirtschaftlichkeit")
3. Wähle ein Diagramm (z.B. "Kumulierter Cashflow")
4. Deaktiviere "Globale Farben verwenden"
5. Wähle 3 Custom-Farben
6. Klicke "💾 Speichern"

---

## 📊 Datenstruktur

### Speicherung in Database

```python
# admin_settings Tabelle
{
    "visualization_settings": {
        "global_chart_colors": [
            "#1E3A8A",
            "#3B82F6",
            "#10B981",
            "#F59E0B",
            "#EF4444",
            "#8B5CF6"
        ],
        "individual_chart_colors": {
            "cumulative_cashflow_chart": {
                "use_global": False,
                "custom_colors": [
                    "#1E3A8A",
                    "#3B82F6",
                    "#10B981"
                ]
            },
            "monthly_prod_cons_chart": {
                "use_global": True
            }
        }
    }
}
```

---

## 🔧 Für Entwickler

### Farben abrufen

```python
from database import load_admin_setting

# Lade Einstellungen
viz_settings = load_admin_setting('visualization_settings', {})

# Globale Farben
global_colors = viz_settings.get('global_chart_colors', [
    '#1E3A8A', '#3B82F6', '#10B981',
    '#F59E0B', '#EF4444', '#8B5CF6'
])

# Farben für spezifisches Diagramm
def get_chart_colors(chart_key):
    individual = viz_settings.get('individual_chart_colors', {})
    chart_config = individual.get(chart_key, {})
    
    if chart_config.get('use_global', True):
        return global_colors
    else:
        return chart_config.get('custom_colors', global_colors)

# Beispiel
cashflow_colors = get_chart_colors('cumulative_cashflow_chart')
```

### In Plotly verwenden

```python
import plotly.graph_objects as go

colors = get_chart_colors('cumulative_cashflow_chart')

fig = go.Figure(data=[
    go.Bar(
        x=['Jan', 'Feb', 'Mar'],
        y=[100, 200, 300],
        marker_color=colors[0]  # Primärfarbe
    )
])

fig.update_layout(
    plot_bgcolor=colors[1],  # Sekundärfarbe als Hintergrund
    paper_bgcolor='white'
)
```

---

## 🎯 Use Cases

### Use Case 1: Corporate Branding

**Szenario:** Unternehmen möchte alle Diagramme in Firmenfarben

**Lösung:**

1. Erstelle Custom-Palette mit Firmenfarben
2. Wende Palette global an
3. Alle Diagramme verwenden automatisch die Firmenfarben

### Use Case 2: Spezielle Hervorhebung

**Szenario:** ROI-Diagramm soll besonders auffallen

**Lösung:**

1. Wähle ROI-Diagramm in individueller Konfiguration
2. Deaktiviere "Globale Farben"
3. Wähle auffällige Custom-Farben (z.B. Gold, Orange)
4. Speichern

### Use Case 3: Barrierefreiheit

**Szenario:** Präsentation für farbenblinde Personen

**Lösung:**

1. Wähle "Accessible" Palette
2. Wende global an
3. Alle Diagramme sind farbenblind-freundlich

### Use Case 4: Thematische Anpassung

**Szenario:** Nachhaltigkeits-Präsentation

**Lösung:**

1. Wähle "Eco" Palette (Grün-Töne)
2. Wende global an
3. Passt perfekt zum Nachhaltigkeitsthema

---

## ✅ Vorteile

### Für Administratoren

- ✅ Einfache Konfiguration ohne Code
- ✅ Live-Vorschau aller Änderungen
- ✅ Schnelle Anwendung vordefinierter Paletten
- ✅ Granulare Kontrolle über einzelne Diagramme

### Für Benutzer

- ✅ Konsistentes Design aller Diagramme
- ✅ Professionelles Erscheinungsbild
- ✅ Anpassung an Corporate Identity
- ✅ Barrierefreie Optionen verfügbar

### Für Entwickler

- ✅ Zentrale Farbverwaltung
- ✅ Einfache API zum Abrufen von Farben
- ✅ Keine Hardcoded-Farben mehr
- ✅ Flexibel erweiterbar

---

## 🚀 Nächste Schritte

Die Diagramm-Farbeinstellungen sind vollständig implementiert. Nächste Tasks:

- [ ] Task 11: UI-Theme-Einstellungen
- [ ] Task 12: PDF-Template-Verwaltung
- [ ] Task 13: Layout-Optionen-Verwaltung

---

**Implementiert:** 2025-01-09  
**Version:** 1.0  
**Status:** ✅ Production Ready
