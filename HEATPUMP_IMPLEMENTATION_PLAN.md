# 🔥 Wärmepumpen-Simulator - Vollständiger Implementierungsplan

**Status:** In Bearbeitung  
**Basierend auf:** WP_implementierung.pdf (28 Seiten) + 5 Excel-Dateien + Bestehender Code  
**Ziel:** 100% vollständige, dynamische und vielseitige Wärmepumpen-Analyse mit WOW-Funktionen

---

## 📊 Quellenanalyse - ABGESCHLOSSEN ✅

### PDF-Manual (28 Seiten)

- ✅ Produktspezifikationen: Vitocal 250-A, 13kW, COP 5.3, R290, 70°C max
- ✅ Heizlastberechnung: `heat_load_kw = annual_demand_kwh / 1800`
- ✅ Radiator-Check: `Q ~ (ΔT)^1.3` Formel
- ✅ BEG-Förderung: 35% base + 10% Gas-Ersatz-Bonus + 5% Einkommens-Bonus = bis 50%
- ✅ NPV-Berechnung: 20 Jahre, 3% Diskontrate
- ✅ PDF-Struktur: 16 Seiten mit Koordinaten-basierter Platzierung
- ✅ 360°-Visualisierung: 24-Frame-Animation Konzept

### Excel-Dateien (5 Stück)

- ✅ **1-3.xlsx:** Investitions- & Wartungskosten (I&W), Finanzierung & Folgekosten (Fi&Fo), Annuitätenrechnung, Barwertfaktoren
- ✅ **4.xlsx:** econ calc light - Kostenvergleich Öl/Gas/WP mit CO2-Preis, Amortisation
- ✅ **5.xlsx:** GEG-Regelungen, grüne Brennstoffe, CO2-Preis (2025: 55€/t → 2045: 85€/t), JAZ-Infos (3.3-5.2)

### Bestehender Code

- ✅ **heatpump_ui.py** (1603 Zeilen): 6 Tabs - Gebäudeanalyse, WP-Auswahl, Wirtschaftlichkeit, PV-Integration, Komponenten, Ergebnisse
- ✅ **calculations_heatpump.py** (303 Zeilen): Basis-Funktionen für Heizlast, WP-Empfehlung, JAZ, Wirtschaftlichkeit
- ✅ **heatpump_pricing.py** (1056+ Zeilen): HeatPumpPriceComponent-Klasse, COP-Anpassungen, Preisberechnung

---

## 🎯 Feature-Liste - Was NEU implementiert werden muss

### 1️⃣ Erweiterte Heizlastberechnung

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def calculate_domestic_hot_water_demand(
    living_area_m2: float,
    persons: int,
    daily_usage_liters_per_person: float = 50.0
) -> float:
    """
    Berechnet Warmwasserbedarf in kWh/Jahr
    Formel: persons * daily_usage * 365 * 0.04 kWh/Liter
    """
    pass

def calculate_heat_load_with_climate_zone(
    building_type: str,
    living_area_m2: float,
    climate_zone: str,  # "Kalt", "Gemäßigt", "Mild"
    insulation_quality: str
) -> dict:
    """
    Erweiterte Heizlastberechnung mit Klimazone
    Returns: {
        "heating_load_kw": float,
        "dhw_load_kw": float,
        "total_load_kw": float,
        "annual_heating_demand_kwh": float,
        "annual_dhw_demand_kwh": float
    }
    """
    pass
```

**Basis aus Excel:**

- Heizlast = Jahresbedarf / 1800 Volllaststunden
- Warmwasser = 12-15% von Gesamt-Wärmebedarf
- Klimafaktor: Kalt 1.2, Gemäßigt 1.0, Mild 0.8

---

### 2️⃣ Radiator-Kompatibilitätsprüfung

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def calculate_required_flow_temperature(
    heat_load_kw: float,
    radiator_area_m2: float,
    room_temperature_c: float = 20.0,
    radiator_exponent: float = 1.3  # n in Q ~ ΔT^n
) -> float:
    """
    Berechnet erforderliche Vorlauftemperatur für bestehende Radiatoren
    Formel: Q = k * A * ΔT^n → ΔT = (Q / (k * A))^(1/n)
    """
    pass

def check_radiator_compatibility(
    required_flow_temp: float,
    heatpump_max_temp: float = 70.0
) -> dict:
    """
    Prüft ob Radiatoren für Wärmepumpe geeignet sind
    Returns: {
        "compatible": bool,
        "recommendation": str,  # "Optimal", "Grenzwertig", "Upgrade nötig"
        "efficiency_impact": float,  # COP-Reduktion in %
        "upgrade_cost_estimate": float  # Falls Upgrade empfohlen
    }
    """
    pass
```

**Basis aus PDF Seite 11:**

- Q ~ (ΔT)^1.3 Beziehung zwischen Wärmeleistung und Temperaturdifferenz
- Ideal: Vorlauf ≤55°C (hoher COP)
- Grenzwertig: 55-65°C (mittlerer COP)
- Kritisch: >65°C (niedriger COP, Upgrade empfohlen)

---

### 3️⃣ CO2-Preis & GEG-Konformität

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def calculate_co2_costs_fossil_heating(
    fuel_type: str,  # "Heizöl", "Erdgas"
    annual_consumption_kwh: float,
    co2_price_per_ton: float = 85.0,  # Durchschnitt nächste 20 Jahre
    green_fuel_share: float = 0.0  # GEG: 2029: 15%, 2035: 30%, 2040: 60%
) -> dict:
    """
    Berechnet CO2-Kosten für fossile Heizung mit GEG-Regelung
    Returns: {
        "annual_co2_cost_eur": float,
        "co2_emissions_tons": float,
        "green_fuel_cost_premium": float,
        "total_annual_cost": float
    }
    """
    # CO2-Emission: Heizöl 0.266 kg/kWh, Erdgas 0.201 kg/kWh
    pass

def calculate_green_fuel_premium(
    fuel_type: str,
    kwh_consumed: float,
    green_share: float
) -> float:
    """
    Berechnet Mehrkosten für grüne Brennstoffe (GEG-Pflicht ab 2029)
    Basis Excel 5.xlsx: Industriestrom 0.17€/kWh, Wirkungsgradverluste 40-60%
    """
    pass
```

**Basis aus Excel 5.xlsx:**

- CO2-Preis 2025: 55€/t → 2045: 85€/t (Durchschnitt)
- GEG-Pflicht grüne Brennstoffe: 2029: 15%, 2035: 30%, 2040: 60%, 2045: 100%
- Mehrkosten grüne Brennstoffe: +42.5% (Öl), +28.3% (Gas)

---

### 4️⃣ BEG-Förderung & NPV-Berechnung

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def calculate_beg_subsidy(
    investment_cost_eur: float,
    replaces_gas_oil: bool = True,
    household_income_below_threshold: bool = False
) -> dict:
    """
    Berechnet BEG-Förderung für Wärmepumpen
    Returns: {
        "base_subsidy_percent": 35,
        "gas_replacement_bonus_percent": 10,
        "income_bonus_percent": 5,
        "total_subsidy_percent": int,  # max 70%
        "subsidy_amount_eur": float,  # max 60k € förderfähige Kosten
        "net_investment_eur": float
    }
    """
    pass

def calculate_npv_20_years(
    investment_eur: float,
    annual_operating_cost_eur: float,
    annual_cost_increase_percent: float = 2.0,
    discount_rate_percent: float = 3.0,
    residual_value_eur: float = 0.0
) -> dict:
    """
    NPV-Berechnung über 20 Jahre mit Diskontrate
    Returns: {
        "npv_eur": float,
        "total_cost_undiscounted": float,
        "payback_years": float,
        "irr_percent": float
    }
    """
    pass
```

**Basis aus PDF Seite 13:**

- BEG-Förderung: 35% base + 10% Gas/Öl-Ersatz + 5% Einkommensbonus (< €40k Bruttojahreseinkommen)
- Max. förderfähige Kosten: €60.000
- Diskontrate: 3% (Nominalzins Land Vorarlberg laut Excel)

---

### 5️⃣ Erweiterte Wirtschaftlichkeitsanalyse

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def compare_heating_systems_20_years(
    building_data: dict,
    heatpump_data: dict,
    fossil_heating_type: str = "Gasheizung"
) -> dict:
    """
    Vollständiger Kostenvergleich: WP vs. Öl/Gas über 20 Jahre
    Berücksichtigt:
    - Anschaffungskosten (nach BEG-Förderung)
    - Betriebskosten (Strom vs. Öl/Gas)
    - CO2-Kosten
    - GEG-Pflicht grüne Brennstoffe
    - Wartungs- & Reparaturkosten
    - NPV mit 3% Diskontrate
    
    Returns: {
        "heatpump": {...},  # NPV, Gesamt, jährliche Kosten
        "fossil_heating": {...},
        "savings_eur": float,
        "payback_years": float,
        "co2_savings_tons": float
    }
    """
    pass
```

**Basis aus Excel 4.xlsx:**

- Vergleich: Ölheizung €12.8k, WP €30.5k (vor Förderung), Gasheizung €12.8k
- Förderung WP: 50% → Netto €15.3k
- Amortisation WP vs. Öl: ~4.7 Jahre
- Amortisation WP vs. Gas: ~4.0 Jahre

---

### 6️⃣ PV-Eigenverbrauch-Optimierung

**Datei:** `calculations_heatpump.py`

#### Neue Funktionen

```python
def calculate_pv_self_consumption_heatpump(
    heatpump_annual_consumption_kwh: float,
    pv_system_size_kwp: float,
    pv_annual_yield_kwh_per_kwp: float = 1000.0,
    self_consumption_rate_percent: float = 30.0
) -> dict:
    """
    Berechnet PV-Eigenverbrauch für Wärmepumpe
    Returns: {
        "pv_total_yield_kwh": float,
        "heatpump_from_pv_kwh": float,
        "heatpump_from_grid_kwh": float,
        "cost_savings_eur": float,
        "self_consumption_increased_percent": float
    }
    """
    pass
```

**Basis aus Excel 3.xlsx (PV-Einspeisung Sheet):**

- PV-Ertrag: ~1000 kWh/kWp/Jahr
- Eigenverbrauch ohne Speicher: ~30%
- Eigenverbrauch mit WP: ~50-60% (erhöht durch Tages-Lastprofil)

---

### 7️⃣ 360°-Visualisierung

**Datei:** `heatpump_ui.py` (neue Funktion)

#### Neue UI-Komponenten

```python
def render_energy_flow_visualization(heatpump_data: dict) -> None:
    """
    Zeigt animierte Energiefluss-Diagramme
    - Altes System (Öl/Gas): CO2-Emissionen, hohe Kosten
    - Neues System (WP): Erneuerbare Energie, niedrige Betriebskosten
    - 360°-Rotation mit Plotly 3D
    """
    pass

def render_cost_comparison_chart(comparison_data: dict) -> None:
    """
    Interaktives Chart: Kumulative Kosten über 20 Jahre
    - Linien: WP vs. Öl vs. Gas
    - Breakeven-Punkt hervorheben
    - Einsparungen visualisieren
    """
    pass
```

**Basis aus PDF Seite 16-17:**

- 24-Frame-Animation (360° / 15° pro Frame)
- Sankey-Diagramm für Energieflüsse
- Farbcodierung: Fossil (rot), Erneuerbar (grün), Strom (blau)

---

### 8️⃣ PDF-Generierung (16-seitiges Angebot)

**Datei:** `pdf_generator.py` (erweitern) + `heatpump_ui.py`

#### Template-Struktur

```
Seite 1: Deckblatt
  - Kundenname, Adresse
  - Datum, Angebotsnummer
  - Logo

Seite 2-3: Gebäudeanalyse
  - Heizlastberechnung
  - Warmwasserbedarf
  - Radiator-Check Ergebnis

Seite 4-5: Wärmepumpen-Empfehlung
  - Technische Daten (COP, JAZ, Leistung)
  - Produktdatenblatt
  - Installationshinweise

Seite 6-7: Komponentenliste
  - WP-Gerät
  - Pufferspeicher
  - Regelung
  - Hydraulik
  - Installation

Seite 8-10: Wirtschaftlichkeitsanalyse
  - Kostenvergleich-Tabelle (WP vs. Öl vs. Gas)
  - NPV-Berechnung über 20 Jahre
  - Amortisationsdiagramm
  - CO2-Einsparungen

Seite 11: BEG-Förderung
  - Förderantrag-Vorschau
  - Förderfähige Kosten
  - Zu erwartende Fördersumme

Seite 12-13: PV-Integration (optional)
  - Eigenverbrauch-Optimierung
  - Kostenreduktion durch PV

Seite 14-15: 360°-Visualisierung
  - Energiefluss-Diagramme
  - System-Schaltplan

Seite 16: Zusammenfassung & Konditionen
  - Gesamtpreis
  - Zahlungsbedingungen
  - Garantie
  - Kontaktdaten
```

#### Neue Funktionen

```python
def generate_heatpump_offer_pdf(
    customer_data: dict,
    building_data: dict,
    heatpump_data: dict,
    economics_data: dict,
    output_path: str
) -> str:
    """
    Generiert vollständiges 16-seitiges Angebot als PDF
    Verwendet: PyPDF2 + koordinatenbasierte Textplatzierung
    """
    pass
```

---

## 🛠️ Implementierungsreihenfolge

### Phase 1: Backend-Berechnungen (2-3 Stunden)

1. ✅ Erweiterte Heizlastberechnung (Warmwasser, Klimazone)
2. ✅ Radiator-Check (Vorlauftemperatur, Kompatibilität)
3. ✅ CO2-Kosten & GEG-Regelungen
4. ✅ BEG-Förderung & NPV
5. ✅ Vollständiger Kostenvergleich über 20 Jahre
6. ✅ PV-Eigenverbrauch-Optimierung

**Alle neuen Funktionen in `calculations_heatpump.py` hinzufügen**

### Phase 2: UI-Erweiterungen (1-2 Stunden)

1. ✅ Neuer Tab "Radiator-Check" in heatpump_ui.py
2. ✅ Erweiterte Wirtschaftlichkeits-Ansicht mit CO2-Kosten
3. ✅ Visualisierungen: Energiefluss, Kostenvergleich-Charts
4. ✅ 360°-Animation (Plotly 3D)

**UI in `heatpump_ui.py` erweitern, NICHT komplett neu schreiben**

### Phase 3: PDF-Generierung (2-3 Stunden)

1. ✅ Template-Struktur erstellen (16 Seiten)
2. ✅ Koordinatenbasierte Textplatzierung mit PyPDF2
3. ✅ Diagramme/Charts als Bilder einbetten
4. ✅ Download-Button in UI

**Bestehende `pdf_generator.py` erweitern**

### Phase 4: Testing & Integration (1 Stunde)

1. ✅ Unit-Tests für neue Berechnungsfunktionen
2. ✅ End-to-End-Test: Gebäudeanalyse → WP-Auswahl → PDF
3. ✅ Kompatibilität mit Rest der App prüfen
4. ✅ Performance-Optimierung

---

## 📋 Konkrete TODOs - Schritt für Schritt

### ✅ ERLEDIGT

- [x] PDF-Manual vollständig analysiert (28 Seiten)
- [x] Alle 5 Excel-Dateien extrahiert und verstanden
- [x] Bestehenden Code analysiert (heatpump_ui.py, calculations_heatpump.py)
- [x] Angebot-PDFs angeschaut (Struktur)
- [x] Implementierungsplan erstellt

### 🔄 IN ARBEIT

- [ ] **TODO 1:** Funktionen in calculations_heatpump.py erweitern
  - [ ] `calculate_domestic_hot_water_demand()`
  - [ ] `calculate_heat_load_with_climate_zone()`
  - [ ] `calculate_required_flow_temperature()`
  - [ ] `check_radiator_compatibility()`
  - [ ] `calculate_co2_costs_fossil_heating()`
  - [ ] `calculate_green_fuel_premium()`
  - [ ] `calculate_beg_subsidy()`
  - [ ] `calculate_npv_20_years()`
  - [ ] `compare_heating_systems_20_years()`
  - [ ] `calculate_pv_self_consumption_heatpump()`

- [ ] **TODO 2:** UI in heatpump_ui.py erweitern
  - [ ] Neuer Tab "Radiator-Check"
  - [ ] Erweiterte Wirtschaftlichkeits-Ansicht
  - [ ] Energiefluss-Visualisierung
  - [ ] 360°-Animation
  - [ ] Kostenvergleichs-Charts

- [ ] **TODO 3:** PDF-Generierung implementieren
  - [ ] 16-seitiges Template erstellen
  - [ ] `generate_heatpump_offer_pdf()` in pdf_generator.py
  - [ ] Download-Button in UI

- [ ] **TODO 4:** Testing & QA
  - [ ] Unit-Tests
  - [ ] Integration-Tests
  - [ ] Performance-Check

---

## 🎯 Erfolgskriterien

- ✅ **100% Vollständigkeit:** Alle Features aus PDF + Excel implementiert
- ✅ **Dynamische Berechnung:** Alle Formeln korrekt umgesetzt, live-berechnet
- ✅ **WOW-Funktionen:** 360°-Visualisierung, interaktive Charts, professionelles PDF
- ✅ **Keine Breaking Changes:** Rest der App funktioniert weiterhin einwandfrei
- ✅ **Benutzerfreundlichkeit:** Intuitive UI, verständliche Ergebnisse
- ✅ **Performance:** < 2 Sekunden für vollständige Berechnung + PDF-Generierung

---

**Nächster Schritt:** Beginne mit Phase 1 - Backend-Berechnungen in `calculations_heatpump.py`
