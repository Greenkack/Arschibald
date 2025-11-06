# project_data Schema Erweiterung: Dynamischer Stromtarif
"""
Dokumentation der neuen project_data Felder für Dynamischer Stromtarif & Stromcloud

Version: 1.0
Date: 2025-01-13
Author: GitHub Copilot
"""

## Neue Felder für project_data dict:

### 1. Dynamischer Stromtarif
```python
project_data = {
    # ... Existing fields (anlage_kwp, electricity_price_eur_per_kwh, etc.) ...
    
    # ========================================================================
    # DYNAMISCHER STROMTARIF (NEU)
    # ========================================================================
    
    # Aktivierung
    "dynamic_tariff_enabled": bool,  # True wenn dynamischer Tarif genutzt wird
    
    # Anbieter
    "tariff_provider": str,  # "Tibber", "aWATTar", "Ostrom", "Rabot.Charge"
    "tariff_provider_base_fee_eur_month": float,  # Grundgebühr EUR/Monat (z.B. 3.99)
    "tariff_provider_markup_eur_kwh": float,  # Aufschlag auf Börsenpreis (z.B. 0.06)
    
    # Smart Meter
    "smart_meter_installed": bool,  # True wenn Smart Meter vorhanden
    "smart_meter_installation_cost_eur": float,  # Einmalkosten (Standard: 400)
    "smart_meter_annual_fee_eur": float,  # Jahresgebühr (Standard: 50)
    
    # Verbrauchsprofil
    "annual_household_consumption_kwh": float,  # Haushaltsstrom ohne WP (z.B. 4500)
    "annual_wp_consumption_kwh": float,  # WP-Jahresverbrauch (aus heatpump_data)
    
    # Einspar-Ergebnisse
    "dynamic_tariff_annual_savings_eur": float,  # Jährliche Einsparung
    "dynamic_tariff_savings_percent": float,  # Einsparung in %
    "dynamic_tariff_avg_price_eur_kwh": float,  # Durchschnittspreis dynamisch
    
    
    # ========================================================================
    # STROMCLOUD (NEU)
    # ========================================================================
    
    # Aktivierung
    "stromcloud_enabled": bool,  # True wenn Stromcloud genutzt wird
    
    # Anbieter & Plan
    "stromcloud_provider": str,  # "E.ON", "SENEC", "sonnen"
    "stromcloud_plan": str,  # z.B. "E.ON SolarCloud 4500", "SENEC.Cloud 6000"
    "stromcloud_monthly_fee_eur": float,  # Monatliche Grundgebühr (z.B. 19.90)
    "stromcloud_freimenge_kwh": float,  # Inkludierte Freimenge/Jahr (z.B. 4500)
    
    # PV-Daten (für Cloud-Berechnung)
    "stromcloud_pv_production_kwh": float,  # PV-Jahresertrag
    "stromcloud_direct_consumption_kwh": float,  # Direktverbrauch ohne Cloud
    "stromcloud_feed_in_tariff_eur_kwh": float,  # Einspeisevergütung (z.B. 0.08)
    
    # Ergebnisse
    "stromcloud_autarkie_without_percent": float,  # Autarkie ohne Cloud (%)
    "stromcloud_autarkie_with_percent": float,  # Autarkie mit Cloud (%)
    "stromcloud_annual_savings_eur": float,  # Jährliche Einsparung
    "stromcloud_net_cost_eur": float,  # Netto-Kosten mit Cloud
    
    
    # ========================================================================
    # ENERGIEMANAGEMENT-SYSTEM (EMS) (NEU)
    # ========================================================================
    
    # System
    "ems_enabled": bool,  # True wenn EMS installiert
    "ems_type": str,  # "SolarEdge", "SMA", "Fronius", "SENEC"
    "ems_price_eur": float,  # Anschaffungskosten EMS (z.B. 1500)
    "ems_efficiency": float,  # Wirkungsgrad (z.B. 0.95)
    
    # Batterie
    "ems_battery_size_kwh": float,  # Batteriegröße in kWh (z.B. 10.0)
    "ems_battery_cost_eur": float,  # Batteriekosten (z.B. 10000)
    
    # Ergebnisse
    "ems_load_shifted_kwh": float,  # Load-Shifting Potenzial/Jahr
    "ems_autarkie_increase_percent": float,  # Autarkie-Steigerung in %
    "ems_annual_savings_eur": float,  # Jährliche Einsparung
    "ems_payback_years": float,  # Amortisationszeit in Jahren
    
    
    # ========================================================================
    # SMART-HOME-INTEGRATION (NEU)
    # ========================================================================
    
    # Aktivierung & Level
    "smart_home_enabled": bool,  # True wenn Smart-Home genutzt wird
    "smart_home_automation_level": str,  # "low", "medium", "high"
    
    # Geräte (Liste der aktiven Geräte)
    "smart_home_devices": list[str],  # ["heatpump", "battery", "wallbox", "washing_machine", ...]
    
    # Kosten & Einsparung
    "smart_home_setup_cost_eur": float,  # Gesamt-Setup-Kosten
    "smart_home_annual_savings_eur": float,  # Jährliche Einsparung
    "smart_home_comfort_score": float,  # Komfort-Score 0-10
    "smart_home_payback_years": float,  # Amortisationszeit
    
    
    # ========================================================================
    # JAHRES-SIMULATION (NEU)
    # ========================================================================
    
    # 8760h Simulation
    "annual_simulation_performed": bool,  # True wenn Simulation durchgeführt
    "annual_simulation_total_consumption_kwh": float,  # Jahresverbrauch gesamt
    "annual_simulation_avg_price_eur_kwh": float,  # Durchschnittspreis
    "annual_simulation_total_cost_eur": float,  # Jahreskosten
    
    # Peak-Hours
    "annual_simulation_most_expensive_hour": int,  # Teuerste Stunde (0-8759)
    "annual_simulation_cheapest_hour": int,  # Günstigste Stunde
    "annual_simulation_highest_consumption_hour": int,  # Höchster Verbrauch Stunde
}
```

## Integration in bestehende Systeme:

### 1. heatpump_ui.py
- Alle Werte werden in `st.session_state.building_data` gespeichert
- Bei Berechnung werden Ergebnisse in `project_data` übertragen
- Format: `project_data.update(st.session_state.building_data)`

### 2. pdf_generator.py (Todo 19)
- Neue Funktion: `add_dynamic_tariff_section(pdf, project_data)`
- Liest alle `dynamic_tariff_*`, `stromcloud_*`, `ems_*`, `smart_home_*` Felder
- Rendert Tabellen, Charts (als PNG), Pros/Cons, Anbieter-Vergleich

### 3. calculations.py
- `perform_calculations()` ruft optional neue Berechnungen auf
- Bei `project_data.get("dynamic_tariff_enabled", False) == True`
- Speichert Ergebnisse zurück in `project_data`

### 4. database.py
- Bestehende `project_data` JSON-Spalte erweitert sich automatisch
- Keine Schema-Migration nötig (PostgreSQL JSONB)
- Neue Felder werden beim nächsten Save gespeichert

### 5. Abwärtskompatibilität
- Alle neuen Felder sind **optional**
- Default-Werte: `project_data.get("dynamic_tariff_enabled", False)`
- Alte Projekte ohne diese Felder funktionieren weiterhin

## Beispiel: Komplettes project_data mit allen Feldern

```python
complete_project_data = {
    # ---- EXISTING FIELDS ----
    "anlage_kwp": 12.5,
    "electricity_price_eur_per_kwh": 0.32,
    "annual_consumption_kwh": 4500,
    "storage_kwh": 10.0,
    "location": {"latitude": 50.0, "longitude": 10.0},
    "annual_pv_production_kwh": 12500,
    
    # ---- HEATPUMP FIELDS (existing) ----
    "heat_load_kw": 10.0,
    "cop": 3.5,
    "building_type": "Altbau saniert",
    "building_area_m2": 150,
    
    # ---- NEW: DYNAMIC TARIFF ----
    "dynamic_tariff_enabled": True,
    "tariff_provider": "Tibber",
    "tariff_provider_base_fee_eur_month": 3.99,
    "tariff_provider_markup_eur_kwh": 0.06,
    "smart_meter_installed": True,
    "smart_meter_installation_cost_eur": 400.0,
    "smart_meter_annual_fee_eur": 50.0,
    "annual_household_consumption_kwh": 4500.0,
    "annual_wp_consumption_kwh": 5142.86,  # (10 kW * 1800h) / 3.5 COP
    "dynamic_tariff_annual_savings_eur": 450.0,
    "dynamic_tariff_savings_percent": 15.3,
    "dynamic_tariff_avg_price_eur_kwh": 0.27,
    
    # ---- NEW: STROMCLOUD ----
    "stromcloud_enabled": True,
    "stromcloud_provider": "E.ON",
    "stromcloud_plan": "E.ON SolarCloud 4500",
    "stromcloud_monthly_fee_eur": 19.90,
    "stromcloud_freimenge_kwh": 4500.0,
    "stromcloud_pv_production_kwh": 12500.0,
    "stromcloud_direct_consumption_kwh": 3750.0,
    "stromcloud_feed_in_tariff_eur_kwh": 0.08,
    "stromcloud_autarkie_without_percent": 38.7,
    "stromcloud_autarkie_with_percent": 67.5,
    "stromcloud_annual_savings_eur": 320.0,
    "stromcloud_net_cost_eur": 1280.0,
    
    # ---- NEW: EMS ----
    "ems_enabled": True,
    "ems_type": "SolarEdge",
    "ems_price_eur": 1500.0,
    "ems_efficiency": 0.95,
    "ems_battery_size_kwh": 10.0,
    "ems_battery_cost_eur": 10000.0,
    "ems_load_shifted_kwh": 1800.0,
    "ems_autarkie_increase_percent": 12.5,
    "ems_annual_savings_eur": 380.0,
    "ems_payback_years": 7.9,
    
    # ---- NEW: SMART HOME ----
    "smart_home_enabled": True,
    "smart_home_automation_level": "high",
    "smart_home_devices": ["heatpump", "battery", "wallbox", "washing_machine"],
    "smart_home_setup_cost_eur": 960.0,
    "smart_home_annual_savings_eur": 645.0,
    "smart_home_comfort_score": 8.7,
    "smart_home_payback_years": 1.5,
    
    # ---- NEW: ANNUAL SIMULATION ----
    "annual_simulation_performed": True,
    "annual_simulation_total_consumption_kwh": 9642.86,
    "annual_simulation_avg_price_eur_kwh": 0.274,
    "annual_simulation_total_cost_eur": 2642.15,
    "annual_simulation_most_expensive_hour": 4315,  # Stunde 4315 (ca. Tag 180, 17 Uhr)
    "annual_simulation_cheapest_hour": 1825,  # Stunde 1825 (ca. Tag 76, 1 Uhr nachts)
    "annual_simulation_highest_consumption_hour": 145  # Stunde 145 (ca. Tag 6, 1 Uhr - WP-Heizung)
}
```

## Nutzung in Code:

```python
# In heatpump_ui.py - Speichern der Ergebnisse
if st.button("Tarife vergleichen"):
    comparison = calculate_dynamic_tariff_comparison(building_data, ...)
    
    # In session_state speichern
    st.session_state.building_data.update({
        "dynamic_tariff_enabled": True,
        "tariff_provider": "Tibber",
        "dynamic_tariff_annual_savings_eur": comparison["comparison"]["total_savings_eur"],
        # ... weitere Felder
    })
    
    # Später in project_data übertragen (beim PDF-Export)
    project_data.update(st.session_state.building_data)


# In pdf_generator.py - Auslesen der Daten
def add_dynamic_tariff_section(pdf, project_data):
    if not project_data.get("dynamic_tariff_enabled", False):
        return  # Feature nicht genutzt, Sektion überspringen
    
    provider = project_data.get("tariff_provider", "N/A")
    savings = project_data.get("dynamic_tariff_annual_savings_eur", 0)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Dynamischer Stromtarif - {provider}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Jährliche Einsparung: {savings:,.2f} EUR", ln=True)
    # ... weitere PDF-Inhalte


# In calculations.py - Optionale Berechnung
def perform_calculations(project_data, texts, errors):
    results = {}
    
    # ... Existing calculations ...
    
    # Dynamischer Tarif (optional)
    if project_data.get("dynamic_tariff_enabled", False):
        from heatpump_dynamic_tariff import calculate_dynamic_tariff_comparison
        
        tariff_result = calculate_dynamic_tariff_comparison(
            project_data,
            project_data.get("annual_household_consumption_kwh", 4500),
            project_data.get("electricity_price_eur_per_kwh", 0.32)
        )
        
        # Ergebnisse zurück in project_data
        project_data["dynamic_tariff_annual_savings_eur"] = tariff_result["comparison"]["total_savings_eur"]
        # ... weitere Updates
    
    return results
```

## Vorteile dieses Ansatzes:

1. **Abwärtskompatibel**: Alte Projekte ohne neue Felder funktionieren weiterhin
2. **Flexibel**: Alle Felder optional, nur wenn Feature genutzt wird
3. **PostgreSQL JSONB**: Keine Schema-Migration nötig
4. **Dokumentiert**: Dieses Dokument dient als zentrale Referenz
5. **Erweiterbar**: Weitere Felder können jederzeit hinzugefügt werden
