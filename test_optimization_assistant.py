"""
Test für Optimierungs-Assistent (Task 17)

Testet die Funktionen:
- generate_south_config()
- generate_east_west_config()
- generate_south_east_config()
- generate_mixed_config()
- evaluate_config()
- optimize_layout()
"""

import sys
import os

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    BuildingDims,
    AdvancedLayoutConfig,
    generate_south_config,
    generate_east_west_config,
    generate_south_east_config,
    generate_mixed_config,
    evaluate_config,
    optimize_layout
)


def test_generate_south_config():
    """Test Süd-Aufständerungs-Konfiguration"""
    print("\n=== Test: generate_south_config ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    config = generate_south_config(dims, 20)
    
    assert isinstance(config, AdvancedLayoutConfig)
    assert config.mounting_mode == "south"
    assert config.mode == "auto"
    assert config.use_garage == False
    assert config.use_facade == False
    
    print("✓ Süd-Konfiguration erfolgreich generiert")
    print(f"  - Mounting Mode: {config.mounting_mode}")
    print(f"  - Custom Tilt: {config.custom_tilt}°")


def test_generate_east_west_config():
    """Test Ost-West-Aufständerungs-Konfiguration"""
    print("\n=== Test: generate_east_west_config ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    config = generate_east_west_config(dims, 20)
    
    assert isinstance(config, AdvancedLayoutConfig)
    assert config.mounting_mode == "east-west"
    assert config.custom_tilt == 10.0
    
    print("✓ Ost-West-Konfiguration erfolgreich generiert")
    print(f"  - Mounting Mode: {config.mounting_mode}")
    print(f"  - Custom Tilt: {config.custom_tilt}°")


def test_generate_south_east_config():
    """Test Süd-Ost-Aufständerungs-Konfiguration"""
    print("\n=== Test: generate_south_east_config ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    config = generate_south_east_config(dims, 20)
    
    assert isinstance(config, AdvancedLayoutConfig)
    assert config.mounting_mode == "south-east"
    assert config.custom_azimuth == 45.0
    assert config.custom_tilt == 15.0
    
    print("✓ Süd-Ost-Konfiguration erfolgreich generiert")
    print(f"  - Mounting Mode: {config.mounting_mode}")
    print(f"  - Custom Azimuth: {config.custom_azimuth}°")
    print(f"  - Custom Tilt: {config.custom_tilt}°")


def test_generate_mixed_config():
    """Test gemischte Konfiguration"""
    print("\n=== Test: generate_mixed_config ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    config = generate_mixed_config(dims, 50)
    
    assert isinstance(config, AdvancedLayoutConfig)
    assert config.use_garage == True
    assert config.use_facade == True
    
    print("✓ Gemischte Konfiguration erfolgreich generiert")
    print(f"  - Garage: {config.use_garage}")
    print(f"  - Fassade: {config.use_facade}")


def test_evaluate_config():
    """Test Konfigurations-Bewertung"""
    print("\n=== Test: evaluate_config ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Teste verschiedene Konfigurationen
    configs = [
        ("Süd", generate_south_config(dims, 20)),
        ("Ost-West", generate_east_west_config(dims, 20)),
        ("Süd-Ost", generate_south_east_config(dims, 20)),
        ("Gemischt", generate_mixed_config(dims, 50))
    ]
    
    print("\nBewertung mit Ziel 'max_modules':")
    for name, config in configs:
        score = evaluate_config(
            config, dims, 20, "Flachdach", "max_modules"
        )
        assert 0.0 <= score <= 100.0
        print(f"  - {name}: {score:.1f}/100")
    
    print("\nBewertung mit Ziel 'max_yield':")
    for name, config in configs:
        score = evaluate_config(
            config, dims, 20, "Flachdach", "max_yield"
        )
        assert 0.0 <= score <= 100.0
        print(f"  - {name}: {score:.1f}/100")
    
    print("\nBewertung mit Ziel 'balanced':")
    for name, config in configs:
        score = evaluate_config(
            config, dims, 20, "Flachdach", "balanced"
        )
        assert 0.0 <= score <= 100.0
        print(f"  - {name}: {score:.1f}/100")
    
    print("\n✓ Konfigurations-Bewertung erfolgreich")


def test_optimize_layout():
    """Test Optimierungs-Workflow"""
    print("\n=== Test: optimize_layout ===")
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Teste verschiedene Optimierungsziele
    goals = ["max_modules", "max_yield", "balanced"]
    
    for goal in goals:
        print(f"\nOptimierung mit Ziel '{goal}':")
        
        top_configs = optimize_layout(
            building_dims=dims,
            target_modules=20,
            roof_type="Flachdach",
            optimization_goal=goal
        )
        
        # Prüfe dass 3 Konfigurationen zurückgegeben werden
        assert len(top_configs) == 3
        
        # Prüfe dass Scores absteigend sortiert sind
        scores = [score for _, score in top_configs]
        assert scores == sorted(scores, reverse=True)
        
        # Zeige Top 3
        for i, (config, score) in enumerate(top_configs, 1):
            print(f"  {i}. {config.mounting_mode}: {score:.1f}/100")
        
        print(f"✓ Optimierung mit Ziel '{goal}' erfolgreich")


def main():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("TEST: OPTIMIERUNGS-ASSISTENT (TASK 17)")
    print("=" * 60)
    
    try:
        test_generate_south_config()
        test_generate_east_west_config()
        test_generate_south_east_config()
        test_generate_mixed_config()
        test_evaluate_config()
        test_optimize_layout()
        
        print("\n" + "=" * 60)
        print("✓ ALLE TESTS ERFOLGREICH")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
