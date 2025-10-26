# PDF Seite 7: Moduldetails hinzugefügt

## 🎯 Aufgabe

Modulaufbau und PV-Zellentechnologie von Seite 5 auch auf Seite 7 anzeigen.

## 🔍 Analyse PDF Seite 5

### Gefundene Placeholder in `coords/seite5.yml`

1. **PV-Zellentechnologie**:
   - Placeholder: `PV-Zellentechnologie1`
   - Position: (350.0, 263.32257080078125, 500.0, 286.48712158203125)
   - Beispiel: "TOPCon", "PERC", "HJT"

2. **Modulaufbau**:
   - Placeholder: `Modulaufbau1`
   - Position: (350.0, 279.0479431152344, 500.0, 302.2124938964844)
   - Beispiel: "Glas-Glas", "Glas-Folie"

### Zugeordnete Keys aus `placeholders.py`

```python
"PV-Zellentechnologie1": "module_cell_technology",  # Zeile 399
"Modulaufbau1": "module_structure",                  # Zeile 400
```

## ✅ Implementierung

### 1. Neue Placeholder in `coords/seite7.yml` hinzugefügt

**Position im PV-MODULE Bereich nach "Anlagenleistung gesamt":**

```yaml
Text: - Modulaufbau
Position: (335.0, 188.0, 410.0, 198.0)
Schriftart: Helvetica-Regular
Schriftgröße: 9.0
Farbe: 3487029
---------------------------------------
Text: aufbau_modul
Position: (415.0, 188.0, 540.0, 198.0)
Schriftart: Helvetica-Bold
Schriftgröße: 9.0
Farbe: 3487029
---------------------------------------
Text: - PV-Zellentechnologie
Position: (335.0, 198.0, 430.0, 208.0)
Schriftart: Helvetica-Regular
Schriftgröße: 9.0
Farbe: 3487029
---------------------------------------
Text: technik_modul
Position: (435.0, 198.0, 540.0, 208.0)
Schriftart: Helvetica-Bold
Schriftgröße: 9.0
Farbe: 3487029
```

### 2. Placeholder-Mappings in `placeholders.py` hinzugefügt

**Zeile 403-404:**

```python
# Seite 7: Kompakte Darstellung von Moduldetails
"aufbau_modul": "module_structure",
"technik_modul": "module_cell_technology",
```

## 📊 Datenquellen für die Keys

### `module_cell_technology` (PV-Zellentechnologie)

**Quellen in Priorität** (aus placeholders.py Zeile 1960-1961):

```python
"module_cell_technology": [
    "technology", "celltech", "pv_cell_technology", "pvcelltechnology",
    "zelltechnologie", "pv-zellentechnologie", "pv zellentechnologie",
    "PV-Zellentechnologie", "PV Zellentechnologie",
    "n-type", "p-type", "TOPCon", "Heterojunction", "PERC"
]
```

**Typische Werte**:

- "TOPCon" (Tunnel Oxide Passivated Contact)
- "PERC" (Passivated Emitter Rear Cell)
- "HJT" (Heterojunction)
- "n-type" / "p-type"

### `module_structure` (Modulaufbau)

**Quellen**:

- Direkt aus Produkt-DB: `module_structure`
- Alternative Felder: `construction`, `aufbau`, `structure`

**Typische Werte**:

- "Glas-Glas"
- "Glas-Folie"
- "Bifazial Glas-Glas"

## 🎨 Layout PDF Seite 7

### Vorher

```
PV - MODULE:
  X Stück [Modulname]
  - Anlagenleistung gesamt    12.45 kWp
  - mehr Details siehe Produktdatenblatt
```

### Nachher

```
PV - MODULE:
  X Stück [Modulname]
  - Anlagenleistung gesamt       12.45 kWp
  - Modulaufbau                  Glas-Glas
  - PV-Zellentechnologie         TOPCon
  - mehr Details siehe Produktdatenblatt
```

## 📝 Beispiel-Werte

Für ein **Trina Solar Vertex S+ 450W Modul**:

- `aufbau_modul`: **"Glas-Glas"**
- `technik_modul`: **"TOPCon n-type"**

Für ein **Jinko Tiger Neo 440W Modul**:

- `aufbau_modul`: **"Glas-Folie"**
- `technik_modul`: **"TOPCon"**

## 🔧 Technische Details

### Koordinaten-System (von oben nach unten)

- Y=168: Modulanzahl
- Y=178: Anlagenleistung gesamt
- Y=188: **Modulaufbau** (NEU)
- Y=198: **PV-Zellentechnologie** (NEU)
- Y=208: Details siehe Produktdatenblatt

### Text-Alignment

- **Labels (links)**: Beginnen bei X=335
- **Werte (rechts)**: Beginnen bei X=415-435
- **Schriftgröße**: 9pt (kompakte Darstellung)
- **Farbe**: 3487029 (dunkel) für Labels, 3487029 für Werte

## ✅ Änderungen zusammengefasst

### Dateien geändert

1. **`coords/seite7.yml`**:
   - 2 neue Label-Einträge hinzugefügt
   - 2 neue Placeholder-Einträge hinzugefügt
   - Layout angepasst (Y-Positionen verschoben)

2. **`pdf_template_engine/placeholders.py`** (Zeile 403-404):
   - Mapping `aufbau_modul` → `module_structure`
   - Mapping `technik_modul` → `module_cell_technology`

## 🎯 Erwartetes Ergebnis

Auf PDF Seite 7 werden jetzt im PV-MODULE Bereich zusätzlich angezeigt:

- ✅ Modulaufbau (z.B. "Glas-Glas")
- ✅ PV-Zellentechnologie (z.B. "TOPCon")

Diese Informationen stammen aus der gleichen Datenquelle wie auf Seite 5, sind aber kompakter dargestellt.

## 🔍 Fallback-Verhalten

Falls Werte nicht verfügbar sind:

- Zeile 2171 in placeholders.py: Fallback auf "k.A." (keine Angabe)
- Leere Werte werden nicht angezeigt

## 📋 Konsistenz geprüft

- ✅ Seite 5: Detaillierte Darstellung mit allen Modulspezifikationen
- ✅ Seite 7: Kompakte Übersicht mit den wichtigsten 2 Parametern
- ✅ Beide Seiten verwenden die gleichen Datenquellen (`module_cell_technology`, `module_structure`)
- ✅ Keine Duplikate in den Mappings

Die Moduldetails werden jetzt konsistent auf beiden Seiten angezeigt! 🎉
