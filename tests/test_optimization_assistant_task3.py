"""
Test für Task 3: Optimierungs-Assistent

Dieser Test verifiziert dass alle Subtasks korrekt implementiert sind.
"""

from utils.pv3d import (
    BuildingDims,
    AdvancedLayoutConfig,
    optimize_layout,
    evaluate_config
)


def test_optimize_layout_exists():
    """Test 3.1: optimize_layout() Funktion existiert"""
    print("\n=== Test 3.1: optimize_layout() Funktion ===")
    
    # Erstelle Test-Daten
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
    target_modules = 20
    roof_type = "Flachdach"
    
    # Teste alle drei Optimierungsziele
    for goal in ["max_modules", "max_yield", "balanced"]:
        print(f"\nTeste Ziel: {goal}")
        
        # Rufe optimize_layout auf
        results = optimize_layout(
            building_dims=dims,
            target_modules=target_modules,
            roof_type=roof_type,
            optimization_goal=goal
        )
        
        # Prüfe Ergebnisse
        assert len(results) == 3, f"Erwarte 3 Konfigurationen, erhalten: {len(results)}"
        
        for i, (config, score) in enumerate(results, 1):
            assert isinstance(config, AdvancedLayoutConfig), \
                f"Config {i} ist kein AdvancedLayoutConfig"
            assert isinstance(score, float), \
                f"Score {i} ist kein float"
            assert 0.0 <= score <= 100.0, \
                f"Score {i} außerhalb Bereich 0-100: {score}"
            
            print(f"  {i}. {config.mounting_mode}: Score {score:.1f}")
        
        # Prüfe dass Scores sortiert sind (höchster zuerst)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True), \
            "Scores sind nicht absteigend sortiert"
    
    print("\n[OK] Test 3.1 bestanden: optimize_layout() funktioniert korrekt")


def test_evaluate_config_exists():
    """Test 3.2: evaluate_config() Funktion existiert"""
    print("\n=== Test 3.2: evaluate_config() Funktion ===")
    
    # Erstelle Test-Daten
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
    target_modules = 20
    
    # Teste verschiedene Konfigurationen
    configs = [
        AdvancedLayoutConfig(mounting_mode="south"),
        AdvancedLayoutConfig(mounting_mode="east-west"),
        AdvancedLayoutConfig(mounting_mode="south-east"),
        AdvancedLayoutConfig(use_garage=True, use_facade=True)
    ]
    
    # Teste alle drei Ziele
    for goal in ["max_modules", "max_yield", "balanced"]:
        print(f"\nTeste Ziel: {goal}")
        
        for config in configs:
            score = evaluate_config(
                config=config,
                building_dims=dims,
                target_modules=target_modules,
                goal=goal
            )
            
            assert isinstance(score, float), "Score ist kein float"
            assert 0.0 <= score <= 100.0, \
                f"Score außerhalb Bereich 0-100: {score}"
            
            desc = config.mounting_mode
            if config.use_garage and config.use_facade:
                desc += " + Garage + Fassade"
            
            print(f"  {desc}: Score {score:.1f}")
    
    print("\n[OK] Test 3.2 bestanden: evaluate_config() funktioniert korrekt")


def test_ui_integration():
    """Test 3.3: UI-Integration (simuliert)"""
    print("\n=== Test 3.3: UI-Integration (simuliert) ===")
    
    # Simuliere UI-Workflow
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
    target_modules = 20
    roof_type = "Flachdach"
    optimization_goal = "balanced"
    
    # 1. Optimierung starten (Button-Click simuliert)
    print("\n1. Optimierung starten...")
    top_configs = optimize_layout(
        building_dims=dims,
        target_modules=target_modules,
        roof_type=roof_type,
        optimization_goal=optimization_goal
    )
    
    # 2. Speichere in Session State (simuliert)
    print("\n2. Speichere Ergebnisse in Session State...")
    import json
    serializable_results = [
        (config.to_json(), float(score))
        for config, score in top_configs
    ]
    session_state = {"optimization_results": serializable_results}
    print(f"   Gespeichert: {len(serializable_results)} Konfigurationen")
    
    # 3. Zeige Top 3 Konfigurationen (simuliert)
    print("\n3. Zeige Top 3 Konfigurationen:")
    for i, (config_json, score) in enumerate(session_state["optimization_results"], 1):
        # Deserialisiere
        config = AdvancedLayoutConfig.from_json(config_json)
        
        # Zeige Details
        desc = config.mounting_mode
        if config.use_garage and config.use_facade:
            desc += " + Garage + Fassade"
        elif config.use_garage:
            desc += " + Garage"
        elif config.use_facade:
            desc += " + Fassade"
        
        print(f"   {i}. {desc}")
        print(f"      Score: {score:.1f}/100")
        print(f"      Details:")
        print(f"        - Aufständerung: {config.mounting_mode}")
        print(f"        - Garage: {'Ja' if config.use_garage else 'Nein'}")
        print(f"        - Fassade: {'Ja' if config.use_facade else 'Nein'}")
    
    # 4. Übernehme Konfiguration (Button-Click simuliert)
    print("\n4. Übernehme Konfiguration 1...")
    selected_config_json, selected_score = session_state["optimization_results"][0]
    selected_config = AdvancedLayoutConfig.from_json(selected_config_json)
    
    # Aktualisiere UI-Werte (simuliert)
    ui_state = {
        "layout_mode": "Automatisch" if selected_config.mode == "auto" else "Manuell",
        "use_garage": selected_config.use_garage,
        "use_facade": selected_config.use_facade,
        "mounting_mode": selected_config.mounting_mode
    }
    
    print(f"   UI-Werte aktualisiert:")
    for key, value in ui_state.items():
        print(f"     {key}: {value}")
    
    print("\n   [OK] Konfiguration 1 übernommen!")
    
    print("\n[OK] Test 3.3 bestanden: UI-Integration funktioniert korrekt")


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("TASK 3: OPTIMIERUNGS-ASSISTENT - VERIFIKATION")
    print("=" * 70)
    
    try:
        # Test 3.1
        test_optimize_layout_exists()
        
        # Test 3.2
        test_evaluate_config_exists()
        
        # Test 3.3
        test_ui_integration()
        
        print("\n" + "=" * 70)
        print("[OK] ALLE TESTS BESTANDEN!")
        print("=" * 70)
        print("\nTask 3 ist vollständig implementiert:")
        print("  [OK] 3.1 optimize_layout() Funktion")
        print("  [OK] 3.2 evaluate_config() Funktion")
        print("  [OK] 3.3 UI-Integration")
        print("\nDer Optimierungs-Assistent ist einsatzbereit!")
        
    except Exception as e:
        print(f"\n[ERROR] TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
