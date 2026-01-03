"""
Test-Skript für das PV3D Optimierungs-Modul

Dieses Skript testet alle Funktionen des Optimierungs-Moduls:
- optimize_layout()
- evaluate_configuration()
- generate_layout_variants()
- select_best_configuration()
"""

import sys
from typing import Dict, Any

# Importiere Module
from utils.pv3d import BuildingDims, AdvancedLayoutConfig
from utils.pv3d_optimization import (
    optimize_layout,
    evaluate_configuration,
    generate_layout_variants,
    select_best_configuration,
    ConfigurationScore
)


def test_generate_layout_variants():
    """Test: Generierung von Layout-Varianten"""
    print("\n" + "="*80)
    print("TEST 1: Generierung von Layout-Varianten")
    print("="*80)
    
    dims = BuildingDims(length_m=12.0, width_m=10.0, wall_height_m=6.0)
    constraints = {
        "target_modules": 30,
        "use_garage": None,  # Beide Optionen erlaubt
        "use_facade": None
    }
    
    variants = generate_layout_variants(
        dims=dims,
        roof_type="Flachdach",
        constraints=constraints
    )
    
    print(f"\nGenerierte {len(variants)} Varianten")
    print(f"  Erwartet: >= 6 Varianten")
    
    # Prüfe dass mindestens 6 Varianten generiert wurden
    assert len(variants) >= 6, f"Zu wenige Varianten: {len(variants)}"
    
    # Prüfe dass alle Varianten AdvancedLayoutConfig sind
    for i, variant in enumerate(variants):
        assert isinstance(variant, AdvancedLayoutConfig), \
            f"Variante {i} ist kein AdvancedLayoutConfig"
    
    # Zeige Details der ersten 3 Varianten
    print("\n  Details der ersten 3 Varianten:")
    for i, variant in enumerate(variants[:3]):
        print(f"\n  Variante {i+1}:")
        print(f"    - Mounting Mode: {variant.mounting_mode}")
        print(f"    - Azimuth: {variant.custom_azimuth}°")
        print(f"    - Tilt: {variant.custom_tilt}°")
        print(f"    - Garage: {variant.use_garage}")
        print(f"    - Fassade: {variant.use_facade}")
    
    print("\nTEST 1 BESTANDEN")
    return True


def test_evaluate_configuration():
    """Test: Bewertung einer Konfiguration"""
    print("\n" + "="*80)
    print("TEST 2: Bewertung einer Konfiguration")
    print("="*80)
    
    dims = BuildingDims(length_m=12.0, width_m=10.0, wall_height_m=6.0)
    
    # Erstelle Test-Konfiguration (Süd-Aufständerung, optimal)
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        mounting_mode="south",
        custom_azimuth=0.0,  # Süd
        custom_tilt=30.0,
        enable_collision_detection=True
    )
    
    constraints = {"target_modules": 30}
    
    score = evaluate_configuration(
        config=config,
        dims=dims,
        goal="max_yield",
        constraints=constraints,
        latitude=51.0
    )
    
    print(f"\nKonfiguration bewertet")
    print(f"\n  Scores:")
    print(f"    - Gesamt-Score: {score.total_score:.2f}/100")
    print(f"    - Modulanzahl-Score: {score.module_count_score:.2f}/100")
    print(f"    - Ertrags-Score: {score.yield_score:.2f}/100")
    print(f"    - Flächennutzungs-Score: {score.space_efficiency_score:.2f}/100")
    print(f"    - Ausrichtungs-Score: {score.orientation_score:.2f}/100")
    print(f"    - Neigungs-Score: {score.tilt_score:.2f}/100")
    print(f"    - Kollisions-Penalty: {score.collision_penalty:.2f}/100")
    
    print(f"\n  Metriken:")
    print(f"    - Geschätzte Module: {score.metrics['estimated_modules']}")
    print(f"    - Ziel-Module: {score.metrics['target_modules']}")
    print(f"    - Dachfläche: {score.metrics['roof_area_m2']:.2f} m²")
    print(f"    - Belegungsgrad: {score.metrics['coverage_ratio']:.2%}")
    
    # Prüfe dass Score im gültigen Bereich ist
    assert 0.0 <= score.total_score <= 100.0, \
        f"Ungültiger Gesamt-Score: {score.total_score}"
    
    # Prüfe dass alle Teil-Scores im gültigen Bereich sind
    assert 0.0 <= score.module_count_score <= 100.0
    assert 0.0 <= score.yield_score <= 100.0
    assert 0.0 <= score.space_efficiency_score <= 100.0
    assert 0.0 <= score.orientation_score <= 100.0
    assert 0.0 <= score.tilt_score <= 100.0
    assert 0.0 <= score.collision_penalty <= 100.0
    
    # Prüfe dass Metriken vorhanden sind
    assert "estimated_modules" in score.metrics
    assert "target_modules" in score.metrics
    assert score.metrics["estimated_modules"] > 0
    
    print("\nTEST 2 BESTANDEN")
    return True


def test_select_best_configuration():
    """Test: Auswahl der besten Konfigurationen"""
    print("\n" + "="*80)
    print("TEST 3: Auswahl der besten Konfigurationen")
    print("="*80)
    
    # Erstelle Test-Konfigurationen mit unterschiedlichen Scores
    config1 = AdvancedLayoutConfig(mounting_mode="south", custom_azimuth=0.0, custom_tilt=30.0)
    score1 = ConfigurationScore(
        total_score=85.0,
        module_count_score=80.0,
        yield_score=90.0,
        space_efficiency_score=85.0,
        orientation_score=95.0,
        tilt_score=85.0,
        collision_penalty=0.0,
        metrics={"estimated_modules": 30}
    )
    
    config2 = AdvancedLayoutConfig(mounting_mode="east-west", custom_azimuth=90.0, custom_tilt=15.0)
    score2 = ConfigurationScore(
        total_score=75.0,
        module_count_score=85.0,
        yield_score=70.0,
        space_efficiency_score=80.0,
        orientation_score=60.0,
        tilt_score=80.0,
        collision_penalty=5.0,
        metrics={"estimated_modules": 32}
    )
    
    config3 = AdvancedLayoutConfig(mounting_mode="south-east", custom_azimuth=45.0, custom_tilt=25.0)
    score3 = ConfigurationScore(
        total_score=80.0,
        module_count_score=82.0,
        yield_score=85.0,
        space_efficiency_score=82.0,
        orientation_score=85.0,
        tilt_score=82.0,
        collision_penalty=2.0,
        metrics={"estimated_modules": 31}
    )
    
    scored_variants = [
        (config1, score1),
        (config2, score2),
        (config3, score3)
    ]
    
    # Wähle Top 2 aus
    best_configs = select_best_configuration(
        scored_variants=scored_variants,
        goal="max_yield",
        top_n=2
    )
    
    print(f"\n{len(best_configs)} beste Konfigurationen ausgewählt")
    
    # Prüfe dass 2 Konfigurationen zurückgegeben wurden
    assert len(best_configs) == 2, f"Falsche Anzahl: {len(best_configs)}"
    
    # Prüfe dass die beste Konfiguration zuerst kommt
    assert best_configs[0].mounting_mode == "south", \
        f"Falsche Reihenfolge: {best_configs[0].mounting_mode}"
    
    assert best_configs[1].mounting_mode == "south-east", \
        f"Falsche Reihenfolge: {best_configs[1].mounting_mode}"
    
    print(f"\n  Beste Konfiguration:")
    print(f"    - Mounting Mode: {best_configs[0].mounting_mode}")
    print(f"    - Score: 85.0/100")
    
    print(f"\n  Zweitbeste Konfiguration:")
    print(f"    - Mounting Mode: {best_configs[1].mounting_mode}")
    print(f"    - Score: 80.0/100")
    
    print("\nTEST 3 BESTANDEN")
    return True


def test_optimize_layout_max_modules():
    """Test: Layout-Optimierung mit Ziel 'max_modules'"""
    print("\n" + "="*80)
    print("TEST 4: Layout-Optimierung (Ziel: max_modules)")
    print("="*80)
    
    dims = BuildingDims(length_m=12.0, width_m=10.0, wall_height_m=6.0)
    constraints = {
        "target_modules": 30,
        "use_garage": None,
        "use_facade": None
    }
    
    best_configs = optimize_layout(
        dims=dims,
        goal="max_modules",
        constraints=constraints,
        roof_type="Flachdach",
        latitude=51.0
    )
    
    print(f"\nOptimierung abgeschlossen")
    print(f"  Gefunden: {len(best_configs)} beste Konfigurationen")
    
    # Prüfe dass 3 Konfigurationen zurückgegeben wurden
    assert len(best_configs) == 3, f"Falsche Anzahl: {len(best_configs)}"
    
    # Zeige Details
    print(f"\n  Top 3 Konfigurationen:")
    for i, config in enumerate(best_configs):
        print(f"\n  Platz {i+1}:")
        print(f"    - Mounting Mode: {config.mounting_mode}")
        print(f"    - Azimuth: {config.custom_azimuth}°")
        print(f"    - Tilt: {config.custom_tilt}°")
        print(f"    - Garage: {config.use_garage}")
        print(f"    - Fassade: {config.use_facade}")
    
    print("\nTEST 4 BESTANDEN")
    return True


def test_optimize_layout_max_yield():
    """Test: Layout-Optimierung mit Ziel 'max_yield'"""
    print("\n" + "="*80)
    print("TEST 5: Layout-Optimierung (Ziel: max_yield)")
    print("="*80)
    
    dims = BuildingDims(length_m=12.0, width_m=10.0, wall_height_m=6.0)
    constraints = {
        "target_modules": 30,
        "use_garage": False,  # Keine Garage für reinen Ertrags-Vergleich
        "use_facade": False
    }
    
    best_configs = optimize_layout(
        dims=dims,
        goal="max_yield",
        constraints=constraints,
        roof_type="Flachdach",
        latitude=51.0
    )
    
    print(f"\nOptimierung abgeschlossen")
    print(f"  Gefunden: {len(best_configs)} beste Konfigurationen")
    
    # Prüfe dass 3 Konfigurationen zurückgegeben wurden
    assert len(best_configs) == 3, f"Falsche Anzahl: {len(best_configs)}"
    
    # Prüfe dass die beste Konfiguration Süd-Ausrichtung hat
    # (optimal für Ertrag)
    best_config = best_configs[0]
    print(f"\n  Beste Konfiguration:")
    print(f"    - Mounting Mode: {best_config.mounting_mode}")
    print(f"    - Azimuth: {best_config.custom_azimuth}°")
    print(f"    - Tilt: {best_config.custom_tilt}°")
    
    # Für max_yield sollte Süd-Ausrichtung bevorzugt werden
    assert best_config.custom_azimuth == 0.0 or best_config.mounting_mode == "south", \
        f"Beste Konfiguration sollte Süd-Ausrichtung haben, ist aber: {best_config.mounting_mode}"
    
    print("\nTEST 5 BESTANDEN")
    return True


def test_optimize_layout_balanced():
    """Test: Layout-Optimierung mit Ziel 'balanced'"""
    print("\n" + "="*80)
    print("TEST 6: Layout-Optimierung (Ziel: balanced)")
    print("="*80)
    
    dims = BuildingDims(length_m=12.0, width_m=10.0, wall_height_m=6.0)
    constraints = {
        "target_modules": 30
    }
    
    best_configs = optimize_layout(
        dims=dims,
        goal="balanced",
        constraints=constraints,
        roof_type="Flachdach",
        latitude=51.0
    )
    
    print(f"\nOptimierung abgeschlossen")
    print(f"  Gefunden: {len(best_configs)} beste Konfigurationen")
    
    # Prüfe dass 3 Konfigurationen zurückgegeben wurden
    assert len(best_configs) == 3, f"Falsche Anzahl: {len(best_configs)}"
    
    # Zeige Details
    print(f"\n  Top 3 Konfigurationen:")
    for i, config in enumerate(best_configs):
        print(f"\n  Platz {i+1}:")
        print(f"    - Mounting Mode: {config.mounting_mode}")
        print(f"    - Azimuth: {config.custom_azimuth}°")
        print(f"    - Tilt: {config.custom_tilt}°")
    
    print("\nTEST 6 BESTANDEN")
    return True


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n" + "="*80)
    print("PV3D OPTIMIERUNGS-MODUL - TEST-SUITE")
    print("="*80)
    
    tests = [
        ("Generierung von Layout-Varianten", test_generate_layout_variants),
        ("Bewertung einer Konfiguration", test_evaluate_configuration),
        ("Auswahl der besten Konfigurationen", test_select_best_configuration),
        ("Layout-Optimierung (max_modules)", test_optimize_layout_max_modules),
        ("Layout-Optimierung (max_yield)", test_optimize_layout_max_yield),
        ("Layout-Optimierung (balanced)", test_optimize_layout_balanced)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\nTEST FEHLGESCHLAGEN: {test_name}")
            print(f"   Fehler: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*80)
    print(f"\n  Gesamt: {len(tests)} Tests")
    print(f"  Bestanden: {passed}")
    print(f"  Fehlgeschlagen: {failed}")
    
    if failed == 0:
        print("\n ALLE TESTS BESTANDEN!")
        return True
    else:
        print(f"\n{failed} TEST(S) FEHLGESCHLAGEN")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
