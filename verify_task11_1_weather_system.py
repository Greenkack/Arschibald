"""
Verification Script für Phase 3 Task 11.1 - Wetter-System

Führt manuelle Tests für das Wetter-System durch.

Author: PV3D Team
Date: 2025-01-03
"""

import sys
import traceback
import plotly.graph_objects as go
import numpy as np

# Import der zu testenden Module
from utils.pv3d_weather import (
    WeatherCondition,
    WEATHER_CONDITIONS,
    get_weather_condition,
    get_all_weather_conditions,
    apply_weather_to_scene,
    add_rain_particles,
    add_snow_particles,
    calculate_weather_yield_impact,
    calculate_weather_yield_impact_multiple,
    get_weather_statistics,
    simulate_annual_weather_distribution,
    calculate_annual_weather_adjusted_yield
)


class TestRunner:
    """Führt Tests aus und sammelt Ergebnisse."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test(self, test_name, test_func):
        """Führt einen einzelnen Test aus."""
        try:
            test_func()
            self.passed += 1
            print(f"✅ {test_name}")
            return True
        except AssertionError as e:
            self.failed += 1
            self.errors.append((test_name, str(e)))
            print(f"❌ {test_name}: {e}")
            return False
        except Exception as e:
            self.failed += 1
            error_msg = f"{type(e).__name__}: {e}"
            self.errors.append((test_name, error_msg))
            print(f"💥 {test_name}: {error_msg}")
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Gibt Test-Zusammenfassung aus."""
        total = self.passed + self.failed
        print("\n" + "="*70)
        print(f"TEST SUMMARY: {self.passed}/{total} Tests bestanden")
        print("="*70)
        
        if self.failed > 0:
            print("\n❌ Fehlgeschlagene Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        return self.failed == 0


def test_weather_condition_creation():
    """Test 1: WeatherCondition kann erstellt werden."""
    weather = WeatherCondition(
        name="Test",
        sky_color="#FFFFFF",
        ambient_light=0.5,
        sun_intensity=0.8,
        diffuse_factor=0.3,
        yield_factor=0.9
    )
    
    assert weather.name == "Test"
    assert weather.sky_color == "#FFFFFF"
    assert weather.ambient_light == 0.5
    assert weather.particles is False


def test_all_five_conditions_exist():
    """Test 2: Alle 5 Wetterbedingungen existieren."""
    expected_keys = ["sonnig", "bewoelkt", "regen", "schnee", "nebel"]
    
    for key in expected_keys:
        assert key in WEATHER_CONDITIONS, f"Wetterbedingung '{key}' fehlt"


def test_sonnig_condition():
    """Test 3: Sonnig Wetterbedingung hat korrekte Werte."""
    sonnig = WEATHER_CONDITIONS["sonnig"]
    
    assert "Sonnig" in sonnig.name
    assert sonnig.sky_color == "#87CEEB"
    assert sonnig.yield_factor == 1.0
    assert sonnig.particles is False


def test_regen_condition():
    """Test 4: Regen Wetterbedingung hat Partikel."""
    regen = WEATHER_CONDITIONS["regen"]
    
    assert "Regen" in regen.name
    assert regen.particles is True
    assert regen.yield_factor < 0.5


def test_schnee_condition():
    """Test 5: Schnee Wetterbedingung hat niedrigen Ertrag."""
    schnee = WEATHER_CONDITIONS["schnee"]
    
    assert "Schnee" in schnee.name
    assert schnee.particles is True
    assert schnee.yield_factor < 0.2


def test_get_weather_condition():
    """Test 6: get_weather_condition gibt korrekte Bedingung zurück."""
    weather = get_weather_condition("sonnig")
    
    assert isinstance(weather, WeatherCondition)
    assert weather.name == WEATHER_CONDITIONS["sonnig"].name


def test_get_all_weather_conditions():
    """Test 7: get_all_weather_conditions gibt alle Bedingungen zurück."""
    all_conditions = get_all_weather_conditions()
    
    assert len(all_conditions) == 5
    assert "sonnig" in all_conditions
    assert "regen" in all_conditions


def test_apply_weather_to_scene():
    """Test 8: apply_weather_to_scene ändert Hintergrundfarbe."""
    fig = go.Figure()
    fig.add_trace(go.Mesh3d(x=[0, 1], y=[0, 1], z=[0, 1]))
    
    result = apply_weather_to_scene(fig, "sonnig")
    
    assert result is not None
    assert result.layout.scene.bgcolor == "#87CEEB"


def test_add_rain_particles():
    """Test 9: add_rain_particles fügt Partikel hinzu."""
    fig = go.Figure()
    initial_count = len(fig.data)
    
    result = add_rain_particles(fig)
    
    assert len(result.data) == initial_count + 1
    rain_trace = result.data[-1]
    assert isinstance(rain_trace, go.Scatter3d)
    assert len(rain_trace.x) == 200


def test_add_snow_particles():
    """Test 10: add_snow_particles fügt Partikel hinzu."""
    fig = go.Figure()
    initial_count = len(fig.data)
    
    result = add_snow_particles(fig)
    
    assert len(result.data) == initial_count + 1
    snow_trace = result.data[-1]
    assert isinstance(snow_trace, go.Scatter3d)
    assert len(snow_trace.x) == 150


def test_calculate_yield_impact_sonnig():
    """Test 11: Ertrags-Berechnung bei sonnigem Wetter."""
    result = calculate_weather_yield_impact(1000.0, "sonnig")
    
    assert result["base_yield"] == 1000.0
    assert result["weather_factor"] == 1.0
    assert result["actual_yield"] == 1000.0
    assert result["loss_kwh"] == 0.0


def test_calculate_yield_impact_bewoelkt():
    """Test 12: Ertrags-Berechnung bei bewölktem Wetter."""
    result = calculate_weather_yield_impact(1000.0, "bewoelkt")
    
    assert result["base_yield"] == 1000.0
    assert result["weather_factor"] == 0.6
    assert result["actual_yield"] == 600.0
    assert result["loss_kwh"] == 400.0


def test_calculate_yield_impact_multiple():
    """Test 13: Ertrags-Berechnung für mehrere Module."""
    base_yields = [1000.0, 800.0, 1200.0]
    
    results = calculate_weather_yield_impact_multiple(base_yields, "bewoelkt")
    
    assert len(results) == 3
    assert results[0]["actual_yield"] == 600.0
    assert results[1]["actual_yield"] == 480.0
    assert results[2]["actual_yield"] == 720.0


def test_get_weather_statistics():
    """Test 14: get_weather_statistics gibt Statistiken zurück."""
    stats = get_weather_statistics("sonnig")
    
    assert "name" in stats
    assert "description" in stats
    assert "sky_color" in stats
    assert stats["yield_factor_percent"] == 100.0


def test_simulate_annual_weather_distribution():
    """Test 15: simulate_annual_weather_distribution gibt realistische Verteilung."""
    distribution = simulate_annual_weather_distribution()
    
    assert len(distribution) == 5
    assert "sonnig" in distribution
    
    total_days = sum(distribution.values())
    assert 360 <= total_days <= 370


def test_calculate_annual_weather_adjusted_yield():
    """Test 16: calculate_annual_weather_adjusted_yield berechnet Jahresertrag."""
    base_yield = 10000.0
    
    result = calculate_annual_weather_adjusted_yield(base_yield)
    
    assert "base_annual_yield" in result
    assert "weather_adjusted_yield" in result
    assert "total_loss_kwh" in result
    
    # Adjustierter Ertrag sollte niedriger sein
    assert result["weather_adjusted_yield"] < result["base_annual_yield"]
    assert result["total_loss_kwh"] > 0


def test_weather_factors_valid_range():
    """Test 17: Alle Wetter-Faktoren liegen zwischen 0 und 1."""
    for weather in WEATHER_CONDITIONS.values():
        assert 0.0 <= weather.ambient_light <= 1.0
        assert 0.0 <= weather.sun_intensity <= 1.0
        assert 0.0 <= weather.diffuse_factor <= 1.0
        assert 0.0 <= weather.yield_factor <= 1.0


def test_worse_weather_has_lower_yield():
    """Test 18: Schlechteres Wetter hat niedrigeren Ertrag."""
    sonnig = WEATHER_CONDITIONS["sonnig"]
    bewoelkt = WEATHER_CONDITIONS["bewoelkt"]
    regen = WEATHER_CONDITIONS["regen"]
    schnee = WEATHER_CONDITIONS["schnee"]
    
    assert sonnig.yield_factor > bewoelkt.yield_factor
    assert bewoelkt.yield_factor > regen.yield_factor
    assert regen.yield_factor > schnee.yield_factor


def test_particles_only_for_precipitation():
    """Test 19: Partikel nur bei Niederschlag."""
    sonnig = WEATHER_CONDITIONS["sonnig"]
    bewoelkt = WEATHER_CONDITIONS["bewoelkt"]
    nebel = WEATHER_CONDITIONS["nebel"]
    
    assert sonnig.particles is False
    assert bewoelkt.particles is False
    assert nebel.particles is False
    
    regen = WEATHER_CONDITIONS["regen"]
    schnee = WEATHER_CONDITIONS["schnee"]
    
    assert regen.particles is True
    assert schnee.particles is True


def test_yield_calculation_consistency():
    """Test 20: Ertrags-Berechnung ist konsistent."""
    base_yield = 1000.0
    
    for weather_key in WEATHER_CONDITIONS.keys():
        result = calculate_weather_yield_impact(base_yield, weather_key)
        
        # Tatsächlicher Ertrag = Basis * Faktor
        expected_actual = base_yield * result["weather_factor"]
        assert abs(result["actual_yield"] - expected_actual) < 0.01
        
        # Verlust = Basis - Tatsächlich
        expected_loss = base_yield - result["actual_yield"]
        assert abs(result["loss_kwh"] - expected_loss) < 0.01


def main():
    """Hauptfunktion - führt alle Tests aus."""
    print("="*70)
    print("VERIFICATION: Phase 3 Task 11.1 - Wetter-System")
    print("="*70)
    print()
    
    runner = TestRunner()
    
    # Führe alle Tests aus
    runner.run_test("Test 1: WeatherCondition erstellen", test_weather_condition_creation)
    runner.run_test("Test 2: Alle 5 Wetterbedingungen existieren", test_all_five_conditions_exist)
    runner.run_test("Test 3: Sonnig Wetterbedingung", test_sonnig_condition)
    runner.run_test("Test 4: Regen Wetterbedingung", test_regen_condition)
    runner.run_test("Test 5: Schnee Wetterbedingung", test_schnee_condition)
    runner.run_test("Test 6: get_weather_condition", test_get_weather_condition)
    runner.run_test("Test 7: get_all_weather_conditions", test_get_all_weather_conditions)
    runner.run_test("Test 8: apply_weather_to_scene", test_apply_weather_to_scene)
    runner.run_test("Test 9: add_rain_particles", test_add_rain_particles)
    runner.run_test("Test 10: add_snow_particles", test_add_snow_particles)
    runner.run_test("Test 11: Yield Impact - Sonnig", test_calculate_yield_impact_sonnig)
    runner.run_test("Test 12: Yield Impact - Bewölkt", test_calculate_yield_impact_bewoelkt)
    runner.run_test("Test 13: Yield Impact - Multiple", test_calculate_yield_impact_multiple)
    runner.run_test("Test 14: Weather Statistics", test_get_weather_statistics)
    runner.run_test("Test 15: Annual Weather Distribution", test_simulate_annual_weather_distribution)
    runner.run_test("Test 16: Annual Adjusted Yield", test_calculate_annual_weather_adjusted_yield)
    runner.run_test("Test 17: Weather Factors Valid Range", test_weather_factors_valid_range)
    runner.run_test("Test 18: Worse Weather Lower Yield", test_worse_weather_has_lower_yield)
    runner.run_test("Test 19: Particles Only Precipitation", test_particles_only_for_precipitation)
    runner.run_test("Test 20: Yield Calculation Consistency", test_yield_calculation_consistency)
    
    # Zusammenfassung
    success = runner.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
