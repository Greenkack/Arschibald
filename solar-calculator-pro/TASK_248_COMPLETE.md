# Task 248: PV Module Selection with Product Database - COMPLETE

## Übersicht

Dieses Task implementiert ein vollständiges PV-Modul-Auswahlsystem mit Produktdatenbank, Leistungsberechnung, Modulvergleich und Ertragsschätzung.

## Erstellte Dateien

### 1. Backend Service

**Datei:** `solar-calculator-pro/backend/services/pv_module_service.py`

Der PVModuleService bietet:

**Datenbank-Schema:**
```sql
CREATE TABLE pv_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,      -- Hersteller
    model TEXT NOT NULL,             -- Modellbezeichnung
    power_wp INTEGER NOT NULL,       -- Leistung in Watt peak
    efficiency REAL NOT NULL,        -- Wirkungsgrad in %
    width_mm INTEGER NOT NULL,       -- Breite in mm
    height_mm INTEGER NOT NULL,      -- Höhe in mm
    weight_kg REAL NOT NULL,         -- Gewicht in kg
    cell_type TEXT NOT NULL,         -- Zelltyp
    warranty_years INTEGER,          -- Garantie in Jahren
    price_net REAL NOT NULL,         -- Nettopreis
    price_gross REAL NOT NULL,       -- Bruttopreis
    datasheet_url TEXT,              -- Link zum Datenblatt
    image_url TEXT,                  -- Produktbild
    is_active INTEGER DEFAULT 1,
    UNIQUE(manufacturer, model)
);
```

**Vorinstallierte Module (15 Stück):**

| Hersteller | Modell | Leistung | Wirkungsgrad | Zelltyp |
|------------|--------|----------|--------------|---------|
| Trina Solar | Vertex S+ TSM-440NEG9R.28 | 440 Wp | 22.0% | Mono N-Type |
| Trina Solar | Vertex S TSM-425DE09R.08 | 425 Wp | 21.3% | Mono PERC |
| JA Solar | JAM54S30-415/MR | 415 Wp | 21.0% | Mono PERC |
| JA Solar | JAM72S30-545/MR | 545 Wp | 21.2% | Mono PERC |
| Longi | Hi-MO 5 LR5-54HTH-430M | 430 Wp | 21.5% | Mono PERC |
| Longi | Hi-MO 6 LR5-72HTH-570M | 570 Wp | 22.3% | Mono N-Type |
| Canadian Solar | HiKu6 CS6R-420MS | 420 Wp | 21.0% | Mono PERC |
| Canadian Solar | HiKu7 CS7N-665TB-AG | 665 Wp | 21.8% | Bifacial |
| Jinko Solar | Tiger Neo N-type | 440 Wp | 22.02% | Mono N-Type |
| Jinko Solar | Tiger Pro | 545 Wp | 21.13% | Mono PERC |
| Meyer Burger | White 395 | 395 Wp | 21.7% | Heterojunction |
| SunPower | Maxeon 6 AC | 440 Wp | 22.8% | IBC |
| REC | Alpha Pure-R 430 | 430 Wp | 22.3% | Heterojunction |
| Q CELLS | Q.PEAK DUO ML-G11S+ 410 | 410 Wp | 20.6% | Mono PERC |
| Solarwatt | Panel vision AM 4.0 pure 420 | 420 Wp | 21.5% | Mono PERC |

### 2. API Endpoints

**Datei:** `solar-calculator-pro/backend/api/v1/pv_modules.py`

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/api/v1/pv-modules/` | Alle Module abrufen |
| GET | `/api/v1/pv-modules/manufacturers` | Hersteller-Liste |
| GET | `/api/v1/pv-modules/by-manufacturer/{m}` | Module nach Hersteller |
| GET | `/api/v1/pv-modules/{id}` | Einzelnes Modul |
| POST | `/api/v1/pv-modules/calculate-system` | Anlagenberechnung |
| POST | `/api/v1/pv-modules/recommend` | Empfehlungen |
| GET | `/api/v1/pv-modules/compare` | Modulvergleich |
| POST | `/api/v1/pv-modules/estimate-yield` | Ertragsschätzung |

### 3. Frontend Service

**Datei:** `solar-calculator-pro/frontend/src/services/pvModuleService.ts`

TypeScript-Service mit:
- Typisierte Interfaces (PVModule, SystemPowerResult, etc.)
- Alle API-Methoden
- Utility-Funktionen für Formatierung

### 4. React Komponente

**Datei:** `solar-calculator-pro/frontend/src/components/solar/PVModuleSelector.tsx`

Features:
- Hersteller-Dropdown mit Filter
- Modul-Dropdown mit Leistungsanzeige
- Modulanzahl-Eingabe mit +/- Buttons
- Spezifikations-Anzeige
- Anlagenleistungs-Berechnung
- Modulliste mit Vergleichsfunktion
- Vergleichs-Dialog

**Datei:** `solar-calculator-pro/frontend/src/components/solar/PVModuleSelector.css`

Styling mit:
- Grid-Layouts für Specs und System
- Highlight für beste Werte
- Responsive Design

## Berechnungsformeln

### Anlagenleistung
```
Gesamtleistung (Wp) = Modulanzahl × Modulleistung (Wp)
Gesamtleistung (kWp) = Gesamtleistung (Wp) / 1000
```

### Fläche und Gewicht
```
Modulfläche (m²) = (Breite_mm / 1000) × (Höhe_mm / 1000)
Gesamtfläche (m²) = Modulfläche × Modulanzahl
Gesamtgewicht (kg) = Modulgewicht × Modulanzahl
```

### Preisberechnung
```
Modulpreis (netto) = Einzelpreis_netto × Modulanzahl
Modulpreis (brutto) = Einzelpreis_brutto × Modulanzahl
Preis pro kWp = Modulpreis_netto / Gesamtleistung_kWp
```

### Ertragsschätzung
```
Jahresertrag (kWh) = kWp × Standortfaktor × Orientierungsfaktor

Standortfaktor (Deutschland): ~950-1100 kWh/kWp/Jahr
Orientierungsfaktor: 0.7 (Ost/West) bis 1.0 (Süd, 30°)

Degradation: 0.5% pro Jahr
Jahr n Ertrag = Jahr 1 Ertrag × (1 - 0.005 × (n-1))
```

## Verwendungsbeispiele

### Anlagenberechnung (Backend)
```python
from services.pv_module_service import pv_module_service

result = pv_module_service.calculate_system_power(
    module_id=1,
    module_count=20
)
print(f"Anlagenleistung: {result['total_power_kwp']} kWp")
print(f"Modulpreis: {result['price_gross']} €")
```

### Modul-Empfehlungen (Backend)
```python
recommendations = pv_module_service.recommend_modules_for_roof(
    roof_area_m2=50,
    target_kwp=10
)
for rec in recommendations:
    print(f"{rec['module']['manufacturer']} {rec['module']['model']}")
    print(f"  {rec['recommended_count']} Module = {rec['total_kwp']} kWp")
```

### React Komponente
```tsx
import PVModuleSelector from './components/solar/PVModuleSelector';

function SolarCalculator() {
  const [selection, setSelection] = useState(null);

  return (
    <PVModuleSelector
      value={{ moduleId: 1, moduleCount: 20 }}
      onChange={({ moduleId, moduleCount, systemPower }) => {
        setSelection({ moduleId, moduleCount, systemPower });
        console.log(`System: ${systemPower.total_power_kwp} kWp`);
        console.log(`Preis: ${systemPower.price_gross} €`);
      }}
      roofAreaM2={50}
      showRecommendations={true}
      showComparison={true}
    />
  );
}
```

## Modulvergleich

Der Vergleich zeigt bis zu 5 Module nebeneinander mit Hervorhebung der besten Werte:

| Kategorie | Beschreibung |
|-----------|--------------|
| Höchste Leistung | Modul mit höchster Wp-Zahl |
| Höchster Wirkungsgrad | Modul mit bester Effizienz |
| Niedrigster Preis | Günstigstes Modul |
| Bestes Preis-Leistungs-Verhältnis | Niedrigster €/Wp |
| Längste Garantie | Modul mit längster Garantie |
| Leichtestes | Modul mit geringstem Gewicht |

## Requirements Erfüllt

| Requirement | Status |
|-------------|--------|
| funktionen.txt - "PV-Module" | ✅ |
| Hersteller/Modell-Dropdown | ✅ |
| Modul-Spezifikationen anzeigen | ✅ |
| Gesamtleistung (kWp) berechnen | ✅ |
| Modulvergleich | ✅ |
| Empfehlungen basierend auf Dachgröße | ✅ |
| Ertragsschätzung | ✅ |

## Technische Details

- **Backend:** Python mit FastAPI, SQLite
- **Frontend:** TypeScript, React, PrimeReact
- **API:** RESTful mit Pydantic-Validierung
- **Datenbank:** SQLite mit Indizes auf manufacturer, power_wp

---

**Status: COMPLETE** ✅  
**Erstellt:** November 28, 2025
