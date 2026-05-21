# PDF Seite 7: Wechselrichter & Batteriespeicher Details hinzugefügt

## 🎯 Aufgabe

Wechselrichter- und Batteriespeicher-Details von Seite 5 auch auf Seite 7 anzeigen.

## 🔍 Analyse PDF Seite 5

### WECHSELRICHTER - Gefundene Placeholder in `coords/seite5.yml`

1. **Wechselrichterleistung**:
   - Placeholder: `WR-Leistung`
   - Position: (350.0, 434.2735290527344, 500.0, 457.4380798339844)
   - Beispiel: "10 kW", "15000 W"

2. **Typ Wechselrichter**:
   - Placeholder: `WR-Typ`
   - Position: (350.0, 449.9989013671875, 500.0, 473.1634521484375)
   - Beispiel: "Hybrid", "String", "Mikro"

### BATTERIESPEICHER - Gefundene Placeholder in `coords/seite5.yml`

1. **Speicherkapazität**:
   - Placeholder: `Größe des Batteriespeichers`
   - Position: (350.0, 625.2479248046875, 500.0, 648.4124755859375)
   - Beispiel: "10.0 kWh", "15.5 kWh"

2. **Zellentechnologie**:
   - Placeholder: `Speicherzellentechnologie`
   - Position: (350.0, 641.0, 500.0, 664.0)
   - Beispiel: "LiFePO4", "Li-Ion", "NMC"

### Zugeordnete Keys aus `placeholders.py`

```python
# WECHSELRICHTER
"WR-Leistung": "inverter_power_watt",      # Zeile 358
"WR-Typ": "inverter_type",                 # Zeile 359

# BATTERIESPEICHER
"Größe des Batteriespeichers": "storage_size_battery_kwh_star",  # Zeile 375
"Speicherzellentechnologie": "storage_cell_technology",           # Zeile 374
```

## ✅ Implementierung

### 1. Neue Bereiche in `coords/seite7.yml` hinzugefügt

#### WECHSELRICHTER-Bereich (Y-Position: 235-293)

```yaml
Text: WECHSELRICHTER:
Position: (320.0, 235.0, 420.0, 245.0)
Schriftart: Helvetica-Bold
Schriftgröße: 11.0
---------------------------------------
Text: X_PROD_INVERTER
Position: (335.0, 253.0, 540.0, 263.0)
Schriftart: Helvetica-Regular
Schriftgröße: 9.0
---------------------------------------
Text: - Wechselrichterleistung
Position: (335.0, 263.0, 450.0, 273.0)
Text: leistung_wr
Position: (455.0, 263.0, 540.0, 273.0)
---------------------------------------
Text: - Typ Wechselrichter
Position: (335.0, 273.0, 440.0, 283.0)
Text: typ_wr
Position: (445.0, 273.0, 540.0, 283.0)
---------------------------------------
Text: -  mehr Details siehe Produktdatenblatt
Position: (335.0, 283.0, 540.0, 293.0)
```

#### BATTERIESPEICHER-Bereich (Y-Position: 306-364)

```yaml
Text: BATTERIESPEICHER:
Position: (320.0, 306.0, 440.0, 316.0)
Schriftart: Helvetica-Bold
Schriftgröße: 11.0
---------------------------------------
Text: X_PROD_STORAGE
Position: (335.0, 324.0, 540.0, 334.0)
Schriftart: Helvetica-Regular
Schriftgröße: 9.0
---------------------------------------
Text: - Speicherkapazität
Position: (335.0, 334.0, 435.0, 344.0)
Text: kapazitaet_speicher
Position: (440.0, 334.0, 540.0, 344.0)
---------------------------------------
Text: - Zellentechnologie
Position: (335.0, 344.0, 435.0, 354.0)
Text: technologie_speicher
Position: (440.0, 344.0, 540.0, 354.0)
---------------------------------------
Text: -  mehr Details siehe Produktdatenblatt
Position: (335.0, 354.0, 540.0, 364.0)
```

### 2. Placeholder-Mappings in `placeholders.py` hinzugefügt

**Zeilen 407-412:**

```python
# Seite 7: Kompakte Darstellung von Wechselrichter-Details
"leistung_wr": "inverter_power_watt",
"typ_wr": "inverter_type",
# Seite 7: Kompakte Darstellung von Batteriespeicher-Details
"kapazitaet_speicher": "storage_size_battery_kwh_star",
"technologie_speicher": "storage_cell_technology",
```

## 📊 Datenquellen für die Keys

### Wechselrichter

#### `inverter_power_watt` (Wechselrichterleistung)

**Typische Werte**:

- "10000 W" (10 kW String-Wechselrichter)
- "15 kW" (15 kW Hybrid-Wechselrichter)
- "5000 W" (5 kW Mikro-Wechselrichter)

**Quellen**:

- Direkt aus Produkt-DB: `power_output`, `nominal_power`, `rated_power`
- Alternative Felder: `inverter_power`, `output_power_w`

#### `inverter_type` (Typ Wechselrichter)

**Typische Werte**:

- "Hybrid" (mit Batterie-Anschluss)
- "String" (nur PV)
- "Mikro" (Modul-Wechselrichter)
- "Zentral" (große Anlagen)

**Quellen**:

- Direkt aus Produkt-DB: `inverter_type`, `type`, `kategorie`
- Fallback: "String" (Standard)

### Batteriespeicher

#### `storage_size_battery_kwh_star` (Speicherkapazität)

**Typische Werte**:

- "10.0 kWh*" (nutzbare Kapazität mit Stern)
- "15.5 kWh*" (bei Erweiterungsmodulen)
- "5.0 kWh*" (Einstiegsgröße)

**Hinweis**: Der `_star` Suffix bedeutet, dass ein `*` für Fußnoten angehängt wird.

**Quellen**:

- Priorität 1: `storage_power_kw` (häufig als kWh gepflegt)
- Priorität 2: `capacity_kwh`, `usable_capacity_kwh`
- Priorität 3: `nominal_capacity_kwh`

#### `storage_cell_technology` (Zellentechnologie)

**Typische Werte**:

- "LiFePO4" (Lithium-Eisenphosphat, sicher)
- "Li-Ion" (Lithium-Ionen, allgemein)
- "NMC" (Nickel-Mangan-Cobalt)
- "LTO" (Lithium-Titanat-Oxid)

**Quellen**:

- Direkt aus Produkt-DB: `cell_technology`, `battery_cell_technology`
- Alternative Felder: `chemistry`, `cell_type`

## 🎨 Layout PDF Seite 7

### Vorher

```
PV - MODULE:
  X Stück [Modulname]
  - Anlagenleistung gesamt    12.45 kWp
  - Modulaufbau               Glas-Glas
  - PV-Zellentechnologie      TOPCon
  - mehr Details siehe Produktdatenblatt
```

### Nachher

```
PV - MODULE:
  X Stück [Modulname]
  - Anlagenleistung gesamt    12.45 kWp
  - Modulaufbau               Glas-Glas
  - PV-Zellentechnologie      TOPCon
  - mehr Details siehe Produktdatenblatt

WECHSELRICHTER:
  Huawei Sun2000 10KTL-M1
  - Wechselrichterleistung    10000 W
  - Typ Wechselrichter        Hybrid
  - mehr Details siehe Produktdatenblatt

BATTERIESPEICHER:
  BYD Battery-Box Premium HVS 10.2
  - Speicherkapazität         10.0 kWh*
  - Zellentechnologie         LiFePO4
  - mehr Details siehe Produktdatenblatt
```

## 📝 Beispiel-Werte

### Beispiel 1: Huawei System

**Wechselrichter**: Huawei Sun2000 10KTL-M1

- `leistung_wr`: **"10000 W"**
- `typ_wr`: **"Hybrid"**

**Batteriespeicher**: Huawei LUNA2000-10-S0

- `kapazitaet_speicher`: **"10.0 kWh*"**
- `technologie_speicher`: **"LiFePO4"**

### Beispiel 2: BYD System

**Wechselrichter**: Fronius Symo GEN24 10.0 Plus

- `leistung_wr`: **"10000 W"**
- `typ_wr`: **"Hybrid"**

**Batteriespeicher**: BYD Battery-Box Premium HVS 10.2

- `kapazitaet_speicher`: **"10.24 kWh*"**
- `technologie_speicher`: **"LiFePO4"**

## 🔧 Technische Details

### Koordinaten-System (Y-Positionen von oben)

**PV-MODULE Bereich:**

- Y=148: Überschrift "PV - MODULE:"
- Y=168-178: Modulanzahl und Name
- Y=179-189: Anlagenleistung
- Y=190-200: Modulaufbau
- Y=201-211: PV-Zellentechnologie
- Y=212-222: Details-Hinweis

**WECHSELRICHTER Bereich: (NEU)**

- Y=235: Überschrift "WECHSELRICHTER:"
- Y=253-263: Produktname
- Y=263-273: Wechselrichterleistung
- Y=273-283: Typ Wechselrichter
- Y=283-293: Details-Hinweis

**BATTERIESPEICHER Bereich: (NEU)**

- Y=306: Überschrift "BATTERIESPEICHER:"
- Y=324-334: Produktname
- Y=334-344: Speicherkapazität
- Y=344-354: Zellentechnologie
- Y=354-364: Details-Hinweis

### Text-Alignment

- **Überschriften**: X=320, Bold 11pt, Farbe 866432
- **Produktnamen**: X=335, Regular 9pt, Farbe 3487029
- **Labels**: X=335, Regular 9pt, Farbe 3487029
- **Werte**: X=440-455, Bold 9pt, Farbe 3487029

### Abstand zwischen Bereichen

- Module → Wechselrichter: 23 Pixel (Y=212 → Y=235)
- Wechselrichter → Batteriespeicher: 23 Pixel (Y=283 → Y=306)

## ✅ Änderungen zusammengefasst

### Dateien geändert

1. **`coords/seite7.yml`**:
   - 2 neue Bereiche hinzugefügt (WECHSELRICHTER, BATTERIESPEICHER)
   - Je 2 Detail-Zeilen pro Bereich
   - Gesamt: ~40 neue Zeilen in YML

2. **`pdf_template_engine/placeholders.py`** (Zeilen 407-412):
   - Mapping `leistung_wr` → `inverter_power_watt`
   - Mapping `typ_wr` → `inverter_type`
   - Mapping `kapazitaet_speicher` → `storage_size_battery_kwh_star`
   - Mapping `technologie_speicher` → `storage_cell_technology`

## 🎯 Erwartetes Ergebnis

Auf PDF Seite 7 werden jetzt angezeigt:

**PV-MODULE:**

- ✅ Anlagenleistung gesamt
- ✅ Modulaufbau
- ✅ PV-Zellentechnologie

**WECHSELRICHTER:** (NEU)

- ✅ Wechselrichterleistung (z.B. "10000 W")
- ✅ Typ Wechselrichter (z.B. "Hybrid")

**BATTERIESPEICHER:** (NEU)

- ✅ Speicherkapazität (z.B. "10.0 kWh*")
- ✅ Zellentechnologie (z.B. "LiFePO4")

Alle Informationen stammen aus den gleichen Datenquellen wie auf Seite 5!

## 🔍 Fallback-Verhalten

Falls Werte nicht verfügbar sind:

- Wechselrichter ohne Typ → "k.A." oder leer
- Batteriespeicher ohne Kapazität → "0.0 kWh" oder leer
- Zellentechnologie unbekannt → "k.A." oder leer

## 📋 Konsistenz geprüft

- ✅ Seite 5: Detaillierte Darstellung mit allen Spezifikationen
- ✅ Seite 7: Kompakte Übersicht mit wichtigsten 2 Parametern pro Komponente
- ✅ Alle Seiten verwenden identische Datenquellen
- ✅ Keine Duplikate in den Mappings
- ✅ Einheitliches Layout für alle drei Komponentengruppen

Die Komponenten-Details werden jetzt vollständig auf Seite 7 angezeigt! 🎉
