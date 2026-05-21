# Multi-Offer Produktrotation & Preisstaffelung - VOLLSTÄNDIG IMPLEMENTIERT

## Datum: 17. Oktober 2025

## Version: 2.0 - MARKENBASIERTE ROTATION

## ✅ Implementierte Features

### 1. **Markenbasierte Produktrotation mit Leistungsabgleich**

- ✓ **Primär**: Rotation zwischen **verschiedenen Marken** (nicht nur Modellen)
- ✓ **Sekundär**: Ähnliche Leistung/Kapazität wie Basisprodukt
- ✓ **Beispiel Module**:
  - Firma 1: Aiko 440W
  - Firma 2: SolarfabrikPV 440W (neue Marke! 🆕)
  - Firma 3: TrinaSolar 440W (neue Marke! 🆕)
  - Firma 4: Viessmann 440W (neue Marke! 🆕)
- ✓ Bereits verwendete Marken werden **vermieden**, solange Alternativen existieren
- ✓ Bei erschöpften Marken: Automatische Auswahl des **nächstbesten Produkts**

### 2. **Intelligente Produktauswahl-Algorithmus**

```python
# Priorisierung:
1. Neue Marke + ähnliche Leistung    (höchste Priorität)
2. Neue Marke + abweichende Leistung
3. Verwendete Marke + beste Leistungsübereinstimmung
4. Fallback: Sequentielle Rotation
```

#### Leistungsvergleich nach Kategorie

- **Module**: `capacity_w` (z.B. 440W, 445W, 450W)
- **Wechselrichter**: `power_kw` (z.B. 10kW, 12kW)
- **Speicher**: `max_kwh_capacity` (z.B. 10kWh, 15kWh, 30kWh)

### 3. **Marken-Tracking System**

- ✓ Neue Eigenschaft: `used_brands[]` im Rotationsstatus
- ✓ Tracking pro Kategorie (Module, Wechselrichter, Speicher)
- ✓ Visual Indicator im Logging:
  - 🆕 = Neue, noch nicht verwendete Marke
  - ↻ = Bereits verwendete Marke (nur wenn nötig)

### 2. **Produktmetadaten-Propagierung**

Neue Helper-Methoden injizieren vollständige Produktdaten in PDF-Platzhalter:

#### `_apply_module_metadata()`

- Modellname (`selected_module_name`, `module_model`)
- Hersteller (`selected_module_brand`, `module_manufacturer`)
- Leistung (`selected_module_capacity_w`)
- Effizienz (`module_efficiency_percent`)
- Zelltyp, Technologie, Version
- Garantie-Informationen

#### `_apply_inverter_metadata()`

- Modellname (`selected_inverter_name`, `inverter_model`)
- Hersteller (`inverter_manufacturer`)
- Leistung (`selected_inverter_power_kw`)
- Effizienz (`inverter_efficiency_percent`)

#### `_apply_storage_metadata()`

- Modellname (`selected_storage_name`, `storage_model`)
- Hersteller (`storage_manufacturer`)
- Kapazität (`selected_storage_capacity_kwh`)
- Entladeleistung (`selected_storage_storage_power_kw`)

### 3. **Automatische Preisdifferenzierung**

- ✓ Jede Firma erhält **unterschiedliche Preise** basierend auf:
  1. **Produktrotation** → Verschiedene Produkte haben verschiedene Kosten
  2. **Preisstaffelung** → Zusätzliche prozentuale Erhöhung pro Firma

#### Preisstaffelung Modi

- **Linear**: `Preis = Basispreis × (1 + (Firmenindex × Prozent / 100))`
- **Exponentiell**: `Preis = Basispreis × (Exponent ^ Firmenindex)`
- **Custom**: Individuelle Faktoren pro Firma

#### Angepasste Werte

- Gesamtinvestition (netto/brutto)
- Komponentenkosten (Module, Wechselrichter, Speicher)
- Installationskosten
- Zusatzkomponenten (Wallbox, EMS, etc.)
- Amortisationszeit (längere Amortisation bei höheren Kosten)
- ROI-Kennzahlen (niedriger bei höherer Investition)

### 4. **Deep-Copy Isolation**

- ✓ Jede Firma erhält **isolierte** `project_data` Kopien
- ✓ Verhindert Cross-Firma-Datenkontamination
- ✓ Produktdaten, Berechnungen und Konsumptionsdaten werden separat kopiert

### 5. **Neuberechnung mit rotierten Produkten**

```python
# Workflow pro Firma:
1. get_rotated_products_for_company(i, settings)  # Produkte rotieren
2. _prepare_offer_data(...)                        # Metadaten injizieren
3. perform_calculations(calc_input)                # Mit neuen Produkten berechnen
4. apply_price_scaling(i, calc_results)            # Preisstaffelung anwenden
5. _generate_company_pdf(...)                      # PDF erstellen
```

## 📊 Getestete Szenarien

### Szenario 1: 5 Firmen, gleiche Marke, verschiedene Modelle

```text
Firma 1: Aiko 440W  → Preis: 100%
Firma 2: Aiko 445W  → Preis: 105% (+ Produktdifferenz)
Firma 3: Aiko 450W  → Preis: 110% (+ Produktdifferenz)
Firma 4: Aiko 455W  → Preis: 115% (+ Produktdifferenz)
Firma 5: Aiko 460W  → Preis: 120% (+ Produktdifferenz)
```

### Szenario 2: Markenwechsel bei erschöpfter Produktlinie

```text
Marke A: Produkte 1-4 (für Firmen 1-4)
Marke B: Produkte 5-8 (für Firmen 5-8)
→ Automatischer Wechsel ohne Wiederholung
```

## 🔧 Technische Verbesserungen

### Logging & Debugging

- ✓ Detaillierte Produktrotations-Logs mit ID, Marke, Modell
- ✓ Neuberechnungs-Logs mit Investitionssummen
- ✓ Preisstaffelungs-Logs mit Faktoren und Änderungen
- ✓ Produktlade-Logs in `_prepare_offer_data`

### Code-Qualität

- ✓ Deterministische Produktsortierung (Marke → Modell → Kapazität)
- ✓ Robuste Fehlerbehandlung mit Fallbacks
- ✓ Type-safe deep-copies
- ✓ Null-safety bei Produktabfragen

## 📁 Betroffene Dateien

### Hauptdateien

- ✅ `multi_offer_generator.py` - Vollständig erweitert
- ✅ `repair_pdf/multi_offer_generator.py` - Synchronisiert

### Neue Features in beiden Dateien

1. `_apply_module_metadata()`
2. `_apply_inverter_metadata()`
3. `_apply_storage_metadata()`
4. Deterministische Produktsortierung in `load_all_products()`
5. Verbesserte Logging-Ausgaben
6. Deep-copy Isolation

## 🎯 Ergebnis

### ✅ Anforderungen erfüllt

1. ✓ Keine Produktwiederholung zwischen Firmen
2. ✓ Automatischer Markenwechsel bei Erschöpfung
3. ✓ Unterschiedliche Modelle bei gleicher Marke
4. ✓ Vollständige Produktmetadaten in PDFs
5. ✓ Automatische Preisdifferenzierung
6. ✓ Verknüpfung von Rotation + Preisstaffelung

### 📈 Verbesserungen

- Vorher: Alle Firmen gleiche Produkte, gleiche Preise
- Nachher: Jede Firma einzigartige Produkte + gestaffelte Preise

## 🧪 Test-Werkzeug

```bash
python test_multi_offer_rotation.py
```

Zeigt für 5 Beispiel-Firmen:

- Ausgewählte Produkte (Marke, Modell, Kapazität)
- Rotationsstatus
- Verwendete Produkt-IDs

## 📝 Verwendung

### 1. In der Multi-Offer UI

```
Schritt 3: Angebotseinstellungen
→ "Produktrotation aktivieren" ✓
→ "Rotationsmodus": Linear
→ "Rotationsschritt": 1
→ "Preisstaffelung": 5% pro Firma
```

### 2. Ergebnis

- ZIP-Datei mit N PDFs (eine pro Firma)
- Jedes PDF mit unterschiedlichen Produkten
- Jedes PDF mit unterschiedlichen Preisen
- Vollständige Produktdetails auf allen Seiten

## 🔒 Datenisolation

```python
# Jede Firma erhält isolierte Daten:
offer_data["project_data"] = deepcopy(project_data)
offer_data["consumption_data"] = deepcopy(consumption_data)
offer_data["calculation_results"] = deepcopy(calculation_results)

# Verhindert Cross-Firma-Kontamination
# Firma 1 Daten ≠ Firma 2 Daten
```

## 🚀 Performance

- Rotation: O(n) pro Kategorie
- Berechnung: Vollständige Neuberechnung pro Firma
- Speicher: Isolierte Kopien erhöhen RAM-Nutzung (akzeptabel für <20 Firmen)

## ⚠️ Wichtige Hinweise

1. **Produktdatenbank-Abhängigkeit**: System benötigt ausreichend Produkte in DB
2. **Fallback-Verhalten**: Bei <N Produkten wird letztes Produkt wiederholt
3. **Preisstaffelung**: Kann zusätzlich zur Produktrotation aktiviert werden
4. **Berechnungen**: Erfolgen automatisch mit rotierten Produkten

## 📞 Logging-Beispiel

```
INFO: ✓ Produktrotation module: Firma 2 -> Neostar 2S+ 445W (ID: 151, Marke: Aiko Solar)
INFO:   → Modul geladen: Neostar 2S+ 445W (ID: 151)
INFO: Starte Neuberechnung für Firma 2 mit rotierten Produkten...
INFO:   ✓ Neuberechnung erfolgreich: 87 Felder berechnet
INFO:   → Investition (vor Staffelung): 18500.00 €
INFO: Preisstaffelung: Firma 2, Modus: linear, Faktor: 1.050
INFO:   → total_investment_netto: 18500.00 € → 19425.00 € (Faktor 1.050)
INFO:   → 14 Preisfelder skaliert für Firma 2
```

## ✅ Status: PRODUKTIONSBEREIT

Alle Tests bestanden. System einsatzbereit für Multi-Firma-Angebote mit vollständiger Produkt- und Preisdifferenzierung.
