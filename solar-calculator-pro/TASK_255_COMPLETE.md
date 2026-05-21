# Task 255: Heat Pump Model Selection - COMPLETE ✅

## 📋 Zusammenfassung

Task 255 implementiert die Wärmepumpen-Modellauswahl und -Dimensionierung:
- Wärmepumpen-Auswahl aus Produktdatenbank
- Anzeige von Spezifikationen (kW, COP, JAZ, Preis)
- Dimensionierung basierend auf Heizlast
- Wärmepumpen-Typ-Auswahl (Luft/Wasser, Sole/Wasser)
- Pufferspeicher-Empfehlung

---

## 📁 Erstellte Dateien (4)

| Datei | Typ | Beschreibung |
|-------|-----|--------------|
| `backend/api/v1/heatpump_models.py` | Python | REST API mit 10 Endpoints |
| `frontend/src/services/heatpumpModelService.ts` | TypeScript | Frontend Service |
| `frontend/src/components/heatpump/HeatPumpSelector.tsx` | React | Auswahl-Komponente |
| `frontend/src/components/heatpump/HeatPumpSelector.css` | CSS | Styling |

---

## 🔧 Bearbeitete Dateien (1)

| Datei | Änderung |
|-------|----------|
| `.kiro/specs/streamlit-to-electron-migration/tasks.md` | Task 255 als ✅ markiert |

---

## 📊 Statistiken

- **Neue Dateien:** 4
- **Bearbeitete Dateien:** 1
- **Gesamte Codezeilen:** ~1.200 Zeilen
- **API Endpoints:** 10 neue Endpoints
- **Sample Wärmepumpen:** 8 Modelle

---

## 🎯 Implementierte Features

### 1. Backend API (10 Endpoints)

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/heatpump/models/` | GET | Alle Wärmepumpen mit Filtern |
| `/api/v1/heatpump/models/{id}` | GET | Einzelnes Modell |
| `/api/v1/heatpump/models/sizing` | POST | Dimensionierung berechnen |
| `/api/v1/heatpump/models/types/list` | GET | Alle WP-Typen |
| `/api/v1/heatpump/models/categories/list` | GET | Alle Kategorien |
| `/api/v1/heatpump/models/manufacturers` | GET | Alle Hersteller |
| `/api/v1/heatpump/models/buffer-storage/calculate` | GET | Pufferspeicher berechnen |
| `/api/v1/heatpump/models/compare` | GET | Modelle vergleichen |
| `/api/v1/heatpump/models/health/check` | GET | Health Check |

### 2. Wärmepumpen-Typen (4)

| Typ | Label | Typischer COP |
|-----|-------|---------------|
| `air_water` | Luft/Wasser | 3.5-5.0 |
| `brine_water` | Sole/Wasser | 4.0-5.5 |
| `water_water` | Wasser/Wasser | 4.5-6.0 |
| `air_air` | Luft/Luft | 3.0-4.5 |

### 3. Kategorien (4)

| Kategorie | Label |
|-----------|-------|
| `monoblock` | Monoblock (Außenaufstellung) |
| `split` | Split-System |
| `indoor` | Innenaufstellung |
| `hybrid` | Hybrid (mit Gas-Backup) |

### 4. Sample Wärmepumpen (8)

| Hersteller | Modell | Leistung | COP | Preis |
|------------|--------|----------|-----|-------|
| Vaillant | aroTHERM plus 75/6 | 7 kW | 5.1 | 14.875 € |
| Vaillant | aroTHERM plus 105/6 | 10 kW | 4.9 | 17.255 € |
| Viessmann | Vitocal 250-A 08 | 8 kW | 5.0 | 15.708 € |
| Viessmann | Vitocal 250-A 13 | 13 kW | 4.7 | 19.635 € |
| Bosch | Compress 7400i 9 | 9 kW | 4.8 | 14.042 € |
| Stiebel Eltron | WPL 17 ACS | 17 kW | 4.5 | 22.015 € |
| Daikin | Altherma 3 H 11 | 11 kW | 4.6 | 16.898 € |
| Wolf | CHA-10 Monoblock | 10 kW | 4.7 | 15.232 € |

### 5. Dimensionierung

#### Sizing-Faktor
```
Faktor = 1.0 + 0.15 (wenn Warmwasser)
Empfohlene Leistung = Heizlast × Faktor
```

#### Pufferspeicher
```
Min. Volumen = Leistung × 20 L/kW
Optimal = Leistung × 25 L/kW
Warmwasser = Bewohner × 50 L
```

---

## 🔗 Integration

### Backend Integration

```python
from api.v1.heatpump_models import router as heatpump_models_router
app.include_router(heatpump_models_router, prefix="/api/v1")
```

### Frontend Integration

```tsx
import HeatPumpSelector from '../components/heatpump/HeatPumpSelector';
import heatpumpModelService from '../services/heatpumpModelService';

// Komponente verwenden
<HeatPumpSelector
  heatingLoadKw={10.5}
  hotWaterIncluded={true}
  flowTemperatureC={35}
  onModelSelect={(model) => console.log('Selected:', model)}
  onSizingComplete={(result) => console.log('Sizing:', result)}
/>

// Service direkt verwenden
const sizing = await heatpumpModelService.calculateSizing({
  heating_load_kw: 10.5,
  hot_water_included: true,
  preferred_type: HeatPumpType.AIR_WATER,
  max_price_eur: 20000,
  min_cop: 4.5
});
```

---

## 🧪 Test-Beispiele

### API Test

```bash
# Alle Wärmepumpen
curl http://localhost:8000/api/v1/heatpump/models/

# Gefiltert nach Typ
curl "http://localhost:8000/api/v1/heatpump/models/?heat_pump_type=air_water&sort_by=cop"

# Dimensionierung
curl -X POST http://localhost:8000/api/v1/heatpump/models/sizing \
  -H "Content-Type: application/json" \
  -d '{
    "heating_load_kw": 10.5,
    "hot_water_included": true,
    "min_cop": 4.5
  }'

# Pufferspeicher berechnen
curl "http://localhost:8000/api/v1/heatpump/models/buffer-storage/calculate?heating_power_kw=10&hot_water_included=true&number_of_residents=4"

# Modelle vergleichen
curl "http://localhost:8000/api/v1/heatpump/models/compare?model_ids=vaillant-arotherm-plus-7,viessmann-vitocal-250-a-8"
```

---

## ✅ Erfüllte Anforderungen

- [x] Wärmepumpen-Auswahl aus Produktdatenbank
- [x] Anzeige von Spezifikationen (kW, COP, JAZ, Preis)
- [x] Dimensionierung basierend auf Heizlast
- [x] Wärmepumpen-Typ-Auswahl (4 Typen)
- [x] Pufferspeicher-Empfehlung
- [x] Filter nach Typ, Preis, COP, Lautstärke
- [x] Sortierung nach verschiedenen Kriterien
- [x] Modellvergleich
- [x] Deutsche Lokalisierung

---

**Status: COMPLETE** ✅  
**Datum:** 28. November 2025  
**Nächster Task:** 256. Heat Pump Financing Options
