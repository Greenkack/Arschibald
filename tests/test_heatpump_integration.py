"""
Integration Tests für Wärmepumpen-Workflow
Testet den kompletten End-to-End-Flow: Building → WP → Economics → PDF
"""

import pytest
from calculations_heatpump import (
    calculate_heat_load_with_climate_zone,
    check_radiator_compatibility,
    calculate_required_flow_temperature,
    calculate_beg_subsidy,
    compare_heating_systems_20_years,
    calculate_pv_self_consumption_heatpump
)


class TestCompleteWorkflow:
    """Integration Tests für den kompletten Wärmepumpen-Workflow"""
    
    def test_complete_workflow_new_building(self):
        """Test: Kompletter Workflow für Neubau"""
        
        # 1. GEBÄUDEANALYSE
        building_data = calculate_heat_load_with_climate_zone(
            building_type="Neubau KFW55",
            living_area_m2=150,
            climate_zone="Gemäßigt",
            insulation_quality="Gut",
            persons=4
        )
        
        assert "heating_load_kw" in building_data
        assert "total_load_kw" in building_data
        assert building_data["heating_load_kw"] > 0
        
        # 2. RADIATOR-CHECK (Neubau → Fußbodenheizung)
        flow_temp = calculate_required_flow_temperature(
            heat_load_kw=building_data["heating_load_kw"],
            radiator_area_m2=150,  # Große Fläche (Fußboden)
            room_temperature_c=20,
            radiator_exponent=1.3
        )
        
        radiator_check = check_radiator_compatibility(flow_temp, 70)
        assert radiator_check["recommendation"] == "Optimal"
        assert radiator_check["compatible"] == True
        
        # 3. BEG-FÖRDERUNG
        investment = 25000
        subsidy = calculate_beg_subsidy(
            investment_cost_eur=investment,
            replaces_gas_oil=True,
            household_income_below_threshold=False
        )
        
        assert subsidy["total_subsidy_percent"] == 45
        assert subsidy["subsidy_amount_eur"] > 0
        
        # 4. WIRTSCHAFTLICHKEITSVERGLEICH
        heatpump_data = {
            "investment_cost_eur": investment,
            "jaz": 4.2,  # Sehr gut bei Neubau
            "electricity_price_kwh": 0.30
        }
        
        comparison = compare_heating_systems_20_years(
            building_data={"annual_heat_demand_kwh": building_data["total_annual_demand_kwh"]},
            heatpump_data=heatpump_data,
            fossil_heating_type="Gasheizung"
        )
        
        assert "heatpump" in comparison
        assert "fossil_heating" in comparison
        assert "comparison" in comparison
        assert comparison["comparison"]["savings_20years_eur"] > 0
        
        # 5. VALIDIERUNG: Amortisation < 10 Jahre bei Neubau
        assert comparison["comparison"]["payback_years"] < 10
    
    def test_complete_workflow_old_building(self):
        """Test: Kompletter Workflow für Altbau mit Sanierungsbedarf"""
        
        # 1. GEBÄUDEANALYSE (Altbau, schlechte Dämmung)
        building_data = calculate_heat_load_with_climate_zone(
            building_type="Altbau unsaniert",
            living_area_m2=180,
            climate_zone="Kalt",  # Ungünstige Lage
            insulation_quality="Schlecht",
            persons=4
        )
        
        # Altbau → höhere Heizlast
        assert building_data["heating_load_kw"] > 15
        
        # 2. RADIATOR-CHECK (kleine alte Radiatoren)
        flow_temp = calculate_required_flow_temperature(
            heat_load_kw=building_data["heating_load_kw"],
            radiator_area_m2=15,  # Kleine Fläche
            room_temperature_c=20,
            radiator_exponent=1.3
        )
        
        radiator_check = check_radiator_compatibility(flow_temp, 70)
        
        # Altbau → oft Upgrade nötig
        assert radiator_check["recommendation"] in ["Grenzwertig", "Upgrade nötig"]
        
        # 3. BEG-FÖRDERUNG (höher wegen Öl-Ersatz)
        investment = 35000  # Höher wegen Sanierung
        subsidy = calculate_beg_subsidy(
            investment_cost_eur=investment,
            replaces_gas_oil=True,
            household_income_below_threshold=False
        )
        
        assert subsidy["total_subsidy_percent"] >= 45
        
        # 4. WIRTSCHAFTLICHKEIT (niedrigerer JAZ im Altbau)
        heatpump_data = {
            "investment_cost_eur": investment,
            "jaz": 3.0,  # Niedriger wegen hoher Vorlauftemperatur
            "electricity_price_kwh": 0.32
        }
        
        comparison = compare_heating_systems_20_years(
            building_data={"annual_heat_demand_kwh": building_data["total_annual_demand_kwh"]},
            heatpump_data=heatpump_data,
            fossil_heating_type="Heizöl"  # Oft Öl im Altbau
        )
        
        # Altbau → längere Amortisation, aber immer noch lohnend
        assert comparison["comparison"]["payback_years"] < 15
        assert comparison["comparison"]["savings_20years_eur"] > 0
    
    def test_workflow_with_pv_integration(self):
        """Test: Workflow mit PV-Integration"""
        
        # 1. Basis-Gebäudedaten
        building_data = calculate_heat_load_with_climate_zone(
            building_type="Einfamilienhaus",
            living_area_m2=160,
            climate_zone="Gemäßigt",
            insulation_quality="Gut",
            persons=4
        )
        
        # 2. WP-Strombedarf berechnen (JAZ 3.8)
        jaz = 3.8
        wp_consumption = building_data["total_annual_demand_kwh"] / jaz
        
        # 3. PV-Integration (10 kWp Anlage)
        pv_integration = calculate_pv_self_consumption_heatpump(
            heatpump_annual_consumption_kwh=wp_consumption,
            pv_system_size_kwp=10,
            pv_annual_yield_kwh_per_kwp=1000,
            self_consumption_rate_percent=30,
            electricity_price_kwh=0.30,
            feed_in_tariff_kwh=0.08
        )
        
        # 4. VALIDIERUNGEN
        assert pv_integration["heatpump_from_pv_kwh"] > 0
        assert pv_integration["cost_savings_eur"] > 0
        
        # PV sollte 20-40% der WP decken (realistischer)
        coverage = pv_integration["pv_coverage_of_hp_percent"]
        assert 15 < coverage < 45
        
        # Eigenverbrauch sollte durch WP steigen
        assert pv_integration["self_consumption_rate_with_hp_percent"] > 30


class TestDataFlowValidation:
    """Tests für korrekten Datenfluss zwischen Funktionen"""
    
    def test_radiator_data_flow(self):
        """Test: Daten fließen korrekt durch Radiator-Berechnung"""
        
        # Input
        heat_load = 12.5
        radiator_area = 20
        
        # Schritt 1: Vorlauftemperatur berechnen
        flow_temp = calculate_required_flow_temperature(
            heat_load_kw=heat_load,
            radiator_area_m2=radiator_area,
            room_temperature_c=20,
            radiator_exponent=1.3
        )
        
        # Schritt 2: Kompatibilität prüfen
        compatibility = check_radiator_compatibility(flow_temp, 70)
        
        # Validierung: Output enthält Input-Daten
        assert compatibility["required_flow_temp"] == flow_temp
        assert compatibility["compatible"] in [True, False]
        assert "recommendation" in compatibility
    
    def test_economics_data_flow(self):
        """Test: Wirtschaftsdaten fließen korrekt durch Vergleich"""
        
        # Basis-Daten
        annual_demand = 15000
        investment = 28000
        
        # BEG-Förderung berechnen
        subsidy = calculate_beg_subsidy(investment, True, False)
        net_investment = subsidy["net_investment_eur"]
        
        # Systemvergleich
        building = {"annual_heat_demand_kwh": annual_demand}
        heatpump = {
            "investment_cost_eur": investment,
            "jaz": 3.6,
            "electricity_price_kwh": 0.31
        }
        
        comparison = compare_heating_systems_20_years(
            building_data=building,
            heatpump_data=heatpump,
            fossil_heating_type="Erdgas"
        )
        
        # Validierung: Förderung ist eingerechnet
        assert comparison["heatpump"]["subsidy_eur"] == subsidy["subsidy_amount_eur"]
        assert comparison["heatpump"]["investment_net_eur"] == net_investment


class TestEdgeCases:
    """Tests für Grenzfälle und fehlerhafte Inputs"""
    
    def test_minimal_building(self):
        """Test: Sehr kleines Gebäude (50m²)"""
        
        result = calculate_heat_load_with_climate_zone(
            building_type="Wohnung",
            living_area_m2=50,
            climate_zone="Mild",
            insulation_quality="Gut",
            persons=1
        )
        
        assert result["heating_load_kw"] > 0
        assert result["heating_load_kw"] < 5  # Sollte unter 5 kW sein
    
    def test_large_building(self):
        """Test: Sehr großes Gebäude (400m²)"""
        
        result = calculate_heat_load_with_climate_zone(
            building_type="Mehrfamilienhaus",
            living_area_m2=400,
            climate_zone="Kalt",
            insulation_quality="Mittel",
            persons=8
        )
        
        assert result["heating_load_kw"] > 20  # Sollte über 20 kW sein
        assert result["total_load_kw"] > result["heating_load_kw"]
    
    def test_extreme_flow_temperature(self):
        """Test: Extreme Vorlauftemperatur (altes System)"""
        
        # Sehr hohe Last, kleine Fläche → hohe Temperatur
        flow_temp = calculate_required_flow_temperature(
            heat_load_kw=20,
            radiator_area_m2=10,
            room_temperature_c=20,
            radiator_exponent=1.3
        )
        
        # Sollte sehr hoch sein
        assert flow_temp > 70
        
        # Kompatibilitätscheck sollte "Upgrade nötig" sagen
        check = check_radiator_compatibility(flow_temp, 70)
        assert check["recommendation"] == "Upgrade nötig"
        assert check["upgrade_cost_estimate_eur"] > 5000


class TestConsistencyChecks:
    """Tests für Konsistenz zwischen verschiedenen Berechnungen"""
    
    def test_energy_conservation(self):
        """Test: Energieerhaltung bei PV-WP-System"""
        
        # WP-Verbrauch
        wp_consumption = 5000  # kWh
        
        # PV-Erzeugung
        pv_size = 8  # kWp
        pv_yield = 1000  # kWh/kWp
        
        pv_data = calculate_pv_self_consumption_heatpump(
            heatpump_annual_consumption_kwh=wp_consumption,
            pv_system_size_kwp=pv_size,
            pv_annual_yield_kwh_per_kwp=pv_yield
        )
        
        # Energieerhaltung: PV aus Netz + PV aus PV = Gesamt-WP-Verbrauch
        total_supply = (pv_data["heatpump_from_pv_kwh"] + 
                       pv_data["heatpump_from_grid_kwh"])
        
        assert total_supply == pytest.approx(wp_consumption, rel=0.01)
    
    def test_subsidy_limits(self):
        """Test: BEG-Förderung bleibt innerhalb Limits"""
        
        # Test mit sehr hoher Investition
        high_investment = 100000
        subsidy = calculate_beg_subsidy(high_investment, True, True)
        
        # Max. Förderbetrag: 70% von 60.000€ = 42.000€
        assert subsidy["subsidy_amount_eur"] <= 42000
        assert subsidy["eligible_costs_eur"] <= 60000
        
        # Prozentsatz sollte aber bei 50% bleiben
        assert subsidy["total_subsidy_percent"] == 50


class TestRealisticScenarios:
    """Tests mit realistischen Szenarien aus der Praxis"""
    
    def test_standard_einfamilienhaus_gas(self):
        """Test: Typisches EFH mit Gasheizung-Ersatz"""
        
        # Typisches 150m² EFH, 4 Personen, Baujahr 2000
        building = calculate_heat_load_with_climate_zone(
            "Einfamilienhaus", 150, "Gemäßigt", "Mittel", 4
        )
        
        # Radiator-Check (Standard-Radiatoren)
        flow_temp = calculate_required_flow_temperature(
            building["heating_load_kw"], 25, 20, 1.3
        )
        radiator = check_radiator_compatibility(flow_temp, 70)
        
        # BEG-Förderung
        subsidy = calculate_beg_subsidy(27000, True, False)
        
        # Wirtschaftlichkeit
        comparison = compare_heating_systems_20_years(
            {"annual_heat_demand_kwh": building["total_annual_demand_kwh"]},
            {"investment_cost_eur": 27000, "jaz": 3.5, "electricity_price_kwh": 0.30},
            "Gasheizung"
        )
        
        # Erwartungen für Standard-Szenario
        assert radiator["recommendation"] in ["Optimal", "Grenzwertig"]
        assert subsidy["total_subsidy_percent"] == 45
        assert 2 < comparison["comparison"]["payback_years"] < 15  # Breiter Bereich
        assert comparison["comparison"]["savings_20years_eur"] > 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
