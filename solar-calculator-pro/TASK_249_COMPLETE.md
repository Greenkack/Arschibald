# Task 249: Inverter Selection and Sizing - COMPLETE

## Übersicht

Dieses Task implementiert ein vollständiges Wechselrichter-Auswahlsystem mit automatischer Dimensionierung, Kompatibilitätsprüfung und Multi-Wechselrichter-Konfiguration für große Anlagen.

## Erstellte Dateien

### 1. Backend API Endpoints

**Datei:** `solar-calculator-pro/backend/api/v1/inverters.py`

Neue REST API mit folgenden Endpoints:

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/api/v1/inverters/` | Alle Wechselrichter (mit Filtern) |
| GET | `/api/v1/inverters/manufacturers` | Hersteller-Liste |
| GET | `/api/v1/inverters/{id}` | Einzelner Wechselrichter |
| POST | `/api/v1/inverters/calculate-sizing` | Dimensionierung berechnen |
| POST | `/api/v1/inverters/select` | Optimalen WR auswählen |
| POST | `/api/v1/inverters/check-compatibility` | Kompatibilität prüfen |
| POST | `/api/v1/inverters/multi-inverter` | Multi-WR-Konfiguration |

**Vorinstallierte Wechselrichter (12 Stück):**

| Hersteller | Modell | Leistung | Wirkungsgrad | Typ |
|------------|--------|----------|--------------|-----|
| Fronius | Symo 10.0-3-M | 10 kW | 98.0% | Standard |
| Fronius | Symo GEN24 10.0 Plus | 10 kW | 98.4% | Hybrid |
| SMA | Sunny Tripower 10.0 | 10 kW | 98.3% | Standard |
| SMA | Sunny Tripower 8.0 Smart Energy | 8 kW | 97.5% | Hybrid |
| Huawei | SUN2000-10KTL-M1 | 10 kW | 98.6% | Standard |
| Huawei | SUN2000-8KTL-M1 (Hybrid) | 8 kW | 98.4% | Hybrid |
| Kostal | PLENTICORE plus 10 | 10 kW | 98.5% | Hybrid |
| GoodWe | GW10K-ET | 10 kW | 98.0% | Hybrid |
| Sungrow | SG10RT | 10 kW | 98.5% | Standard |
| Sungrow | SH10RT (Hybrid) | 10 kW | 97.8% | Hybrid |
| Fronius | Primo 5.0-1 | 5 kW | 98.0% | Standard |
| SMA | Sunny Tripower 15.0 | 15 kW | 98.4% | Standard |

### 2. Frontend Service

**Datei:** `solar-calculator-pro/frontend/src/services/inverterService.ts`

TypeScript-Service mit:
- Typisierte Interfaces für alle Datenstrukturen
- API-Methoden für alle Endpoints
- Utility-Funktionen für Formatierung und Berechnungen

**Wichtige Interfaces:**
```typescript
interface Inverter {
  id: number;
  manufacturer: string;
  model_name: string;
  power_kw: number;
  efficiency_percent: number;
  max_dc_voltage: number;
  mppt_count: number;
  max_dc_current: number;
  price_net: number;
  price_gross: number;
  warranty_years: number;
  features: string[];
  is_hybrid: boolean;
}

interface InverterSizingResult {
  required_power_kw: number;
  recommended_power_range: { min_kw, optimal_kw, max_kw };
  dc_specifications: { string_voltage, total_current, ... };
  mppt_configuration: { recommended_mppt_count, ... };
}
```

### 3. React Komponente

**Datei:** `solar-calculator-pro/frontend/src/components/solar/InverterSelector.tsx`

Features:
- Automatische Dimensionierung basierend auf PV-Leistung
- Hersteller-Filter und Hybrid-Filter
- Automatische Wechselrichter-Empfehlung
- Detaillierte Spezifikationsanzeige
- Kompatibilitätsprüfung mit visueller Darstellung
- Wechselrichter-Liste mit Sortierung
- Detail-Dialog für vollständige Spezifikationen

**Datei:** `solar-calculator-pro/frontend/src/components/solar/InverterSelector.css`

Styling mit:
- Grid-Layouts für Spezifikationen
- Farbcodierte Kompatibilitätsprüfung
- Responsive Design für alle Bildschirmgrößen

## Berechnungsformeln

### Wechselrichter-Dimensionierung

```
Empfohlene WR-Leistung = PV-Leistung × 0.9
Minimale WR-Leistung = PV-Leistung × 0.8
Maximale WR-Leistung = PV-Leistung × 1.0

DC/AC-Verhältnis = PV-Leistung / WR-Leistung
Optimal: 0.9 - 1.1
Akzeptabel: 0.8 - 1.2
```

### String-Berechnung

```
String-Spannung = Modul-Spannung (Vmp) × Module pro String
Gesamtstrom = Modul-Strom (Imp) × Anzahl Strings
Strom pro MPPT = Gesamtstrom / Anzahl MPPTs
```

### Kompatibilitätsprüfung

1. **Leistungsprüfung:** DC/AC-Verhältnis zwischen 0.8 und 1.2
2. **Spannungsprüfung:** String-Spannung ≤ Max. DC-Spannung × 0.9
3. **Stromprüfung:** Strom pro MPPT ≤ Max. DC-Strom

## Verwendungsbeispiele

### Backend API

```python
# Dimensionierung berechnen
POST /api/v1/inverters/calculate-sizing
{
  "pv_power_kwp": 10.0,
  "module_voltage_vmp": 40.0,
  "module_current_imp": 10.0,
  "modules_per_string": 10,
  "number_of_strings": 2
}

# Optimalen Wechselrichter auswählen
POST /api/v1/inverters/select
{
  "pv_power_kwp": 10.0,
  "is_hybrid_required": true,
  "preferred_manufacturer": "Fronius"
}

# Kompatibilität prüfen
POST /api/v1/inverters/check-compatibility
{
  "inverter_id": 1,
  "pv_power_kwp": 10.0,
  "string_voltage": 400,
  "total_current": 20,
  "number_of_strings": 2
}
```

### Frontend React

```tsx
import InverterSelector from './components/solar/InverterSelector';

function SolarCalculator() {
  const [inverter, setInverter] = useState(null);
  const [sizing, setSizing] = useState(null);

  return (
    <InverterSelector
      pvPowerKwp={10.0}
      moduleVoltageVmp={40}
      moduleCurrentImp={10}
      modulesPerString={10}
      numberOfStrings={2}
      onChange={(inv, siz) => {
        setInverter(inv);
        setSizing(siz);
        console.log(`Ausgewählt: ${inv.manufacturer} ${inv.model_name}`);
        console.log(`Empfohlene Leistung: ${siz.recommended_power_range.optimal_kw} kW`);
      }}
    />
  );
}
```

### Frontend Service

```typescript
import { inverterService } from './services/inverterService';

// Alle Wechselrichter laden
const inverters = await inverterService.getAllInverters({
  activeOnly: true,
  hybridOnly: true
});

// Dimensionierung berechnen
const sizing = await inverterService.calculateSizing({
  pv_power_kwp: 10.0,
  modules_per_string: 10,
  number_of_strings: 2
});

// Kompatibilität prüfen
const compatibility = await inverterService.checkCompatibility({
  inverter_id: 1,
  pv_power_kwp: 10.0,
  string_voltage: 400,
  total_current: 20,
  number_of_strings: 2
});

if (compatibility.is_compatible) {
  console.log('Wechselrichter ist kompatibel!');
} else {
  console.log('Fehler:', compatibility.checks.filter(c => c.status === 'FEHLER'));
}
```

## Multi-Wechselrichter-Konfiguration

Für große Anlagen (>15 kWp) oder mehrere Dachflächen:

```typescript
const config = await inverterService.createMultiInverterConfig(
  30.0, // 30 kWp
  [
    { orientation: 'Süd', area_m2: 50 },
    { orientation: 'West', area_m2: 30 }
  ]
);

// Ergebnis:
// {
//   configuration_type: 'multi',
//   inverter_count: 3,
//   inverters: [...],
//   total_power_kw: 30,
//   reasoning: 'Multi-Wechselrichter: 3x für 30kWp'
// }
```

## Bestehender Backend-Service

Der Task nutzt den bereits vorhandenen `InverterService` in:
`solar-calculator-pro/backend/services/inverter_service.py`

Dieser Service bietet zusätzlich:
- Detaillierte Scoring-Algorithmen
- Monitoring-Integration
- Erweiterte Kompatibilitätsprüfungen

## Requirements Erfüllt

| Requirement | Status |
|-------------|--------|
| funktionen.txt - "Wechselrichter" | ✅ |
| Wechselrichter-Auswahl aus Produktdatenbank | ✅ |
| Spezifikationen anzeigen (AC-Leistung, Wirkungsgrad, Preis) | ✅ |
| Dimensionierung basierend auf PV-Systemgröße | ✅ |
| Multi-Wechselrichter-Konfiguration für große Anlagen | ✅ |
| Kompatibilitätsprüfung mit Modulen | ✅ |

## Technische Details

- **Backend:** Python mit FastAPI, Pydantic-Validierung
- **Frontend:** TypeScript, React, PrimeReact
- **API:** RESTful mit JSON
- **Daten:** 12 vorinstallierte Wechselrichter von 6 Herstellern

---

**Status: COMPLETE** ✅  
**Erstellt:** November 28, 2025

## Erstellte Dateien Zusammenfassung

| Datei | Typ | Beschreibung |
|-------|-----|--------------|
| `backend/api/v1/inverters.py` | Python | REST API Endpoints |
| `frontend/src/services/inverterService.ts` | TypeScript | Frontend Service |
| `frontend/src/components/solar/InverterSelector.tsx` | React | UI Komponente |
| `frontend/src/components/solar/InverterSelector.css` | CSS | Styling |
| `TASK_249_COMPLETE.md` | Markdown | Diese Dokumentation |
