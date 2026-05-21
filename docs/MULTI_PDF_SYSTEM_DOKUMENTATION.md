# 🚀 Multi-PDF Angebotserstellungs-System

## 📋 Übersicht

Das Multi-PDF System ist das **Herzstück der App** und ermöglicht die automatische Erstellung mehrerer Angebote für verschiedene Firmen mit jeweils **unterschiedlichen Produktmarken** aber **gleichen Spezifikationen**.

### Hauptziel
Kunden erhalten mehrere vergleichbare Angebote auf einmal, müssen aber nur einmal ihre Daten eingeben. Der Preis wird dabei so kalkuliert, dass das **Standard-Angebot immer günstiger** ist als die Multi-PDFs, um Kunden zur Hauptfirma zu lenken.

---

## 🎯 Kernfunktionen

### 1. Automatische Produkt-Rotation
- **Marken-Rotation**: Jede Firma erhält automatisch andere Marken als das Standard-Angebot
- **Spezifikations-Erhaltung**: Gleiche Leistung/Kapazität (±10% Toleranz)
- **Fallback-Strategie**: Bei Marken-Erschöpfung werden Duplikate mit anderen Modellen erlaubt
- **Intelligente Paarung**: WR + Speicher bevorzugen gleiche Marke wenn verfügbar

### 2. Progressive Preis-Modifikation
- **Basis-Aufschlag**: Einstellbar (Standard: 15%)
- **Progressiver Anstieg**: Je mehr Firmen, desto höher der Aufschlag
- **Garantie**: Standard-Angebot bleibt immer am günstigsten
- **Beispiel**:
  - Standard: 17.533,00 €
  - Firma 1: 18.432,22 € (+15%)
  - Firma 2: 21.532,44 € (+20%)

### 3. Firma-spezifische Templates
- **Separate Koordinaten**: `coords_multi/seite1_f1.yml`, `seite1_f2.yml`, etc.
- **Separate Backgrounds**: `pdf_templates_static/multi/multi_nt_01_f1.pdf`, etc.
- **Individuelle Gestaltung**: Jedes Angebot sieht anders aus

---

## 📁 Dateistruktur

```
Bokuk2 - Kopie/
├── product_rotation_engine.py         # Produkt-Rotations-Logik
├── price_modification_engine.py       # Preis-Modifikations-Logik
├── pdf_template_engine/
│   └── dynamic_overlay.py             # generate_multi_offer_pdfs()
├── doc_output.py                      # UI Integration
├── coords_multi/                      # Firma-spezifische Koordinaten
│   ├── seite1_f1.yml                  # Firma 1, Seite 1
│   ├── seite2_f1.yml
│   ├── ...
│   ├── seite8_f1.yml
│   ├── seite1_f2.yml                  # Firma 2, Seite 1
│   └── ...
└── pdf_templates_static/multi/        # Firma-spezifische Templates
    ├── multi_nt_01_f1.pdf              # Firma 1, Seite 1
    ├── multi_nt_02_f1.pdf
    ├── ...
    ├── multi_nt_08_f1.pdf
    ├── multi_nt_01_f2.pdf              # Firma 2, Seite 1
    └── ...
```

---

## 🔧 Technische Implementierung

### Module

#### 1. `product_rotation_engine.py`

**Hauptfunktionen:**
- `load_all_products()` - Lädt Produkte aus Session State/Datenbank
- `get_available_brands(category, exclude_brands)` - Verfügbare Marken einer Kategorie
- `get_product_by_specs(category, brand, specs)` - Findet Produkt mit gleichen Specs
- `rotate_products(standard_products, used_brands, firm_index)` - Rotiert Produkte für eine Firma
- `track_used_brands(products)` - Extrahiert verwendete Marken
- `track_used_models(products)` - Extrahiert verwendete Modelle

**Logik-Fluss:**
```python
1. Standard-Angebot wählt Marken A, C, B
2. Firma 1:
   - PV Module: Wähle Marke != A (z.B. B) mit 450W
   - Wechselrichter: Wähle Marke != C (z.B. B) mit 10kW
   - Batteriespeicher: Prüfe ob B auch Speicher hat, sonst wähle E mit 7kWh
3. Firma 2:
   - PV Module: Wähle Marke != A,B (z.B. C) mit 450W
   - Wechselrichter: Wähle Marke != C,B (z.B. A) mit 10kW
   - Batteriespeicher: Prüfe ob A auch Speicher hat...
```

#### 2. `price_modification_engine.py`

**Hauptfunktionen:**
- `calculate_base_price(products, labor_costs, profit_margin)` - Basis-Preis berechnen
- `apply_modification(base_price, modifier_pct, firm_index, progression_pct)` - Modifikation anwenden
- `get_progressive_modifier(base_modifier, firm_count, firm_index)` - Progressiven Aufschlag berechnen

**Formel:**
```python
modified_price = base_price × (1 + (base_modifier + progression × firm_index) / 100)

Beispiel mit base_modifier=15%, progression=5%:
- Firma 0: 17.000€ × 1.15 = 19.550€
- Firma 1: 17.000€ × 1.20 = 20.400€
- Firma 2: 17.000€ × 1.25 = 21.250€
```

#### 3. `generate_multi_offer_pdfs()` in `dynamic_overlay.py`

**Hauptfunktion:**
```python
def generate_multi_offer_pdfs(
    selected_firms: list,
    standard_products: dict,
    project_data: dict,
    analysis_results: dict,
    company_info: dict,
    profit_margin: float = 0,
    modifier_pct: float = 15.0,
    progression_pct: float = 5.0,
    additional_pdf: bytes | None = None,
) -> list[tuple[str, bytes]]:
```

**Ablauf:**
1. Initialisiere `used_brands` und `used_models` mit Standard-Angebot
2. Für jede Firma:
   - Rotiere Produkte
   - Berechne modifizierten Preis
   - Baue Dynamic Data
   - Generiere PDF mit firma-spezifischen Templates
   - Aktualisiere `used_brands` und `used_models`
3. Returniere Liste von (firmenname, pdf_bytes)

---

## 🎨 Benutzeroberfläche

### Expander "🏢 MULTI-PDF ANGEBOTSERSTELLUNG"

**Position:** Nach Zahlungsmodalitäten in `doc_output.py`

**Komponenten:**

1. **Firmen-Auswahl**
   - Multi-Select Dropdown
   - Button "✅ Alle auswählen"
   - Mindestens 1 Firma erforderlich
   - Vorschau der ausgewählten Firmen

2. **Preis-Modifikation**
   - Slider "Basis-Aufschlag (%)" (0-50%, Standard: 15%)
   - Slider "Progressions-Faktor (%)" (0-20%, Standard: 5%)
   - Preis-Vorschau mit Beispiel-Berechnung

3. **Produkt-Rotation**
   - Info-Box zur automatischen Rotation
   - Checkbox "Strikte Rotation" (Standard: aus)

4. **PDF-Generierung**
   - Button "🚀 N Multi-PDF(s) generieren"
   - Progress-Spinner während Generierung
   - Download-Button für ZIP-Archiv
   - Optionale einzelne Download-Buttons

---

## 📝 Verwendungsbeispiel

### Szenario

**Standard-Angebot:**
- PV Module: Viessmann VM450, 450W → Preis: 120€ × 20 Module = 2.400€
- Wechselrichter: Huawei HW10K, 10kW → Preis: 2.500€
- Batteriespeicher: Huawei HW7K, 7kWh → Preis: 5.000€
- **Gesamt: 17.533,00 €**

**Multi-PDF für 3 Firmen:**

**Firma 1: "Solar Experte GmbH"**
- PV Module: TrinaSolar TS445, 445W → Preis: 115€ × 20 = 2.300€
- Wechselrichter: GoodWe GW10K, 10kW → Preis: 2.400€
- Batteriespeicher: GoodWe GW6.6K, 6.6kWh → Preis: 4.800€
- Basis-Preis: 17.111,34 €
- **Modifiziert (+15%): 19.678,04 €**

**Firma 2: "Energie Zukunft AG"**
- PV Module: AikoSolar AS450, 450W → Preis: 118€ × 20 = 2.360€
- Wechselrichter: Fronius FR10K, 10kW → Preis: 2.800€
- Batteriespeicher: Viessmann VM5K, 5kWh → Preis: 4.500€ (Fronius hat keine Speicher)
- Basis-Preis: 19.344,53 €
- **Modifiziert (+20%): 23.213,44 €**

**Firma 3: "Öko Power Solutions"**
- PV Module: Viessmann VM450, 450W (Marken erschöpft, Duplikat erlaubt)
- Wechselrichter: Solis S10K, 10kW
- Batteriespeicher: Solis SB10K, 10kWh
- Basis-Preis: 18.522,11 €
- **Modifiziert (+25%): 23.152,64 €**

---

## ⚙️ Konfiguration

### Preis-Modifikation

```python
# In doc_output.py UI
base_modifier = 15  # Basis-Aufschlag in %
progression = 5     # Progressions-Faktor in %

# Berechnung
for i, firma in enumerate(selected_firms):
    total_modifier = base_modifier + (progression * i)
    # Firma 0: 15%, Firma 1: 20%, Firma 2: 25%
```

### Produkt-Rotation

```python
# In product_rotation_engine.py
tolerance = 0.1  # ±10% Toleranz bei Spezifikationen

# Beispiel: 450W Module
min_power = 450 * 0.9 = 405W
max_power = 450 * 1.1 = 495W
# Akzeptiert: 405W - 495W
```

---

## 🐛 Fehlerbehandlung

### Marken-Erschöpfung
```python
if not available_brands:
    logger.warning("Marken erschöpft - erlaube Duplikate")
    available_brands = get_available_brands(category)  # Ohne Exclusion
```

### Keine passenden Specs
```python
if not matching_product:
    logger.warning("Kein exaktes Match, nehme erstes verfügbares")
    return brand_products[0]
```

### Template-Dateien fehlen
```python
if not yml_file.exists():
    logger.warning(f"{yml_file} nicht gefunden, überspringe Seite")
    c.showPage()  # Leere Seite
    continue
```

---

## 📊 Logging

Alle Funktionen loggen umfangreich:

```python
logger.info(f"=== Produkt-Rotation für Firma {firm_index + 1} ===")
logger.info(f"Verwendete Marken bisher: {used_brands}")
logger.info(f"Gefunden: {brand} {model} mit {power}W (Ziel: {target_power}W)")
logger.info(f"✓ PV Module: {pv_brand}")
logger.info(f"Preis: {base_price:.2f}€ × {modifier:.3f} = {modified_price:.2f}€")
```

---

## 🔮 Zukünftige Erweiterungen

1. **Dynamische Template-Anzahl**: Nicht fest 8 Seiten
2. **Custom Marken-Präferenzen**: Firmen haben bevorzugte Marken
3. **Rabatt-Staffeln**: Automatische Rabatte bei mehr Firmen
4. **Email-Versand**: Direkt an Firmen verschicken
5. **Statistiken**: Tracking welche Firma am häufigsten gewählt wird

---

## 📚 API-Referenz

### `product_rotation_engine.py`

#### `rotate_products()`
```python
def rotate_products(
    standard_products: Dict[str, dict],
    used_brands: Set[str],
    firm_index: int = 0,
    used_models: Dict[str, Set[str]] = None
) -> Dict[str, dict]:
    """
    Rotiert Produkte für eine Firma
    
    Args:
        standard_products: Standard-Produkte {category: product_dict}
        used_brands: Bereits verwendete Marken
        firm_index: Index der Firma (0-basiert)
        used_models: Bereits verwendete Modelle pro Kategorie
    
    Returns:
        Rotierte Produkte {category: product_dict}
    
    Raises:
        ValueError: Wenn keine Produkte gefunden werden
    """
```

### `price_modification_engine.py`

#### `apply_modification()`
```python
def apply_modification(
    base_price: float,
    modifier_pct: float,
    firm_index: int = 0,
    progression_pct: float = 0
) -> float:
    """
    Wendet Preis-Modifikation an
    
    Args:
        base_price: Basis-Preis ohne Modifikation
        modifier_pct: Basis-Aufschlag in Prozent
        firm_index: Index der Firma (0-basiert)
        progression_pct: Progressions-Aufschlag pro Firma
    
    Returns:
        Modifizierter Preis in Euro
    
    Example:
        >>> apply_modification(17000, 15, 0, 5)
        19550.0  # 17000 × 1.15
        
        >>> apply_modification(17000, 15, 1, 5)
        20400.0  # 17000 × 1.20
    """
```

---

## ✅ Testing

### Manuelle Tests

1. **1 Firma Test**
   - Wähle 1 Firma
   - Prüfe Marken-Rotation
   - Prüfe Preis-Aufschlag

2. **3 Firmen Test**
   - Wähle 3 Firmen
   - Prüfe progressive Preis-Steigerung
   - Prüfe gleiche Marke bei WR + Speicher

3. **7 Firmen Test (Marken-Erschöpfung)**
   - Wähle 7 Firmen
   - Prüfe Fallback auf Duplikate
   - Prüfe unterschiedliche Modelle

### Automatische Tests

```python
# test_product_rotation.py
def test_rotate_products_basic():
    standard = {
        'pv_modules': {'brand': 'Viessmann', 'power_w': 450},
        'inverters': {'brand': 'Huawei', 'power_kw': 10}
    }
    used_brands = {'Viessmann', 'Huawei'}
    
    rotated = rotate_products(standard, used_brands, 0)
    
    assert rotated['pv_modules']['brand'] not in used_brands
    assert rotated['inverters']['brand'] not in used_brands
```

---

## 🎓 Best Practices

1. **Immer Standard-Angebot zuerst erstellen**
   - Multi-PDFs basieren auf Standard-Produkten

2. **Realistische Preis-Modifikation**
   - Nicht zu hoch (Kunden merken Manipulation)
   - Standard sollte 10-30% günstiger sein

3. **Template-Konsistenz**
   - Alle Firma-Templates müssen existieren (f1, f2, f3...)
   - Koordinaten-Dateien müssen zu PDFs passen

4. **Produktdatenbank-Pflege**
   - Genügend Marken pro Kategorie (mindestens 3-4)
   - Gleiche Specs über mehrere Marken verfügbar

---

## 📞 Support

Bei Fragen oder Problemen:
- Prüfe Logs: `print()` Ausgaben während Generierung
- Prüfe `used_brands` und `used_models` Sets
- Prüfe ob Template-Dateien existieren

---

**Version:** 1.0.0  
**Datum:** 2025-10-27  
**Status:** ✅ Produktionsbereit  
**Commit:** fc72dd2
