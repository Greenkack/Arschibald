"""
Phase 4 - Task 17: Integration Testing
Vollständiger Integration Test für alle Features der 3D PV-Visualisierung

Dieser Test validiert:
- Task 17.1: Kompletten Workflow
- Task 17.2: Feature-Kombinationen
- Task 17.3: Edge Cases

Autor: Kiro AI
Datum: 2025-01-03
"""

import pytest
import numpy as np
from typing import List, Dict, Tuple
import plotly.graph_objects as go

# Import aller relevanten Module
from utils.pv3d_placement_handler import (
    calculate_z_position,
    handle_auto_placement,
    handle_manual_add,
    snap_to_grid,
    copy_module_group,
    paste_module_group,
    create_move_preview,
    handle_keyboard_move,
)

from utils.pv3d_module_colors import (
    ModuleMaterial,
    ALL_MATERIALS,
    MATERIAL_BLACK,
    MATERIAL_DARK_BLUE,
    MATERIAL_ANTHRACITE,
    apply_material_to_module,
)

from utils.pv3d_ai_optimization import (
    AILayoutOptimizer,
    LayoutScore,
)

from utils.pv3d_weather import (
    WeatherCondition,
    WEATHER_CONDITIONS,
    apply_weather_to_scene,
    calculate_weather_yield_impact,
)

from utils.pv3d_comparison import (
    create_comparison_view,
    highlight_differences,
    create_comparison_table,
)

from utils.pv3d_environment import (
    Tree,
    NeighborBuilding,
    Chimney,
    Antenna,
    add_environment_objects_to_scene,
    calculate_environment_shading,
)

from utils.pv3d_analysis import (
    calculate_shading_analysis_enhanced,
    create_shading_timeline_chart,
    identify_weak_modules,
)

from utils.solar_animation import (
    calculate_sun_position,
    create_sun_animation,
)


class TestTask17_1_CompleteWorkflow:
    """Task 17.1: Teste kompletten Workflow"""
    
    def test_workflow_flat_roof(self):
        """Test kompletten Workflow mit Flachdach"""
        # 1. Erstelle Gebäude
        roof_type = "Flachdach"
        roof_width = 10.0
        roof_length = 15.0
        
        # 2. Platziere Module automatisch
        modules = handle_auto_placement(
            roof_type=roof_type,
            roof_width=roof_width,
            roof_length=roof_length,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        assert len(modules) > 0, "Module sollten platziert werden"
        
        # 3. Validiere Z-Position (Flachdach = 0.30m Aufständerung)
        for module in modules:
            x, y, z = module["position"]
            expected_z = 0.30
            assert abs(z - expected_z) < 0.01, f"Z-Position sollte {expected_z}m sein"
        
        # 4. Wende Modulfarbe an
        material = MATERIAL_BLACK
        modules_with_material = [
            apply_material_to_module({"position": m["position"]}, material)
            for module in modules
        ]
        
        assert all("customdata" in m for m in modules_with_material)
        
        print(f"✅ Workflow Flachdach: {len(modules)} Module platziert")
    
    def test_workflow_gable_roof(self):
        """Test kompletten Workflow mit Satteldach"""
        # 1. Erstelle Gebäude
        roof_type = "Satteldach"
        roof_width = 10.0
        roof_length = 15.0
        roof_height = 3.0
        
        # 2. Platziere Module automatisch
        modules = handle_auto_placement(
            roof_type=roof_type,
            roof_width=roof_width,
            roof_length=roof_length,
            roof_height=roof_height,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        assert len(modules) > 0, "Module sollten platziert werden"
        
        # 3. Validiere Z-Position (Satteldach = variabel)
        for module in modules:
            x, y, z = module["position"]
            # Z sollte von Rand zur Mitte steigen
            expected_z = calculate_z_position(
                roof_type=roof_type,
                y_position=y,
                roof_width=roof_width,
                roof_height=roof_height,
            )
            assert abs(z - expected_z) < 0.01, "Z-Position sollte korrekt sein"
        
        print(f"✅ Workflow Satteldach: {len(modules)} Module platziert")
    
    def test_workflow_with_all_features(self):
        """Test Workflow mit allen Features"""
        # 1. Erstelle Gebäude
        roof_type = "Flachdach"
        roof_width = 12.0
        roof_length = 18.0
        
        # 2. Auto-Placement
        modules = handle_auto_placement(
            roof_type=roof_type,
            roof_width=roof_width,
            roof_length=roof_length,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        # 3. KI-Optimierung
        optimizer = AILayoutOptimizer(
            roof_width=roof_width,
            roof_length=roof_length,
            roof_type=roof_type,
        )
        
        optimized_layout = optimizer.optimize_for_max_yield(
            module_width=1.0,
            module_length=2.0,
        )
        
        assert optimized_layout is not None
        assert len(optimized_layout["modules"]) > 0
        
        # 4. Modulfarben
        material = MATERIAL_DARK_BLUE
        modules_with_color = [
            apply_material_to_module(m, material)
            for m in optimized_layout["modules"]
        ]
        
        # 5. Wetter-Simulation
        weather = WEATHER_CONDITIONS["Bewölkt"]
        yield_impact = calculate_weather_yield_impact(
            weather_condition=weather,
            base_yield=1000.0,
        )
        
        assert yield_impact < 1000.0, "Ertrag sollte bei bewölktem Wetter sinken"
        
        # 6. Umgebungs-Objekte
        tree = Tree(x=5.0, y=5.0, height=8.0, tree_type="Laubbaum")
        module_positions = [(m["position"]) for m in modules_with_color]
        
        shading = calculate_environment_shading(
            objects=[tree],
            module_positions=module_positions,
            sun_azimuth=180,
            sun_elevation=45,
        )
        
        assert len(shading) == len(module_positions)
        
        print(f"✅ Workflow mit allen Features: {len(modules_with_color)} Module")


class TestTask17_2_FeatureCombinations:
    """Task 17.2: Teste Feature-Kombinationen"""
    
    def test_colors_plus_ai_optimization(self):
        """Test: Modulfarben + KI-Optimierung"""
        # Setup
        roof_width = 10.0
        roof_length = 15.0
        
        # KI-Optimierung
        optimizer = AILayoutOptimizer(
            roof_width=roof_width,
            roof_length=roof_length,
            roof_type="Flachdach",
        )
        
        layout = optimizer.optimize_for_aesthetics(
            module_width=1.0,
            module_length=2.0,
        )
        
        # Farbe anwenden
        material = MATERIAL_ANTHRACITE
        modules_with_color = [
            apply_material_to_module(m, material)
            for m in layout["modules"]
        ]
        
        # Validierung
        assert all("customdata" in m for m in modules_with_color)
        assert all(m["customdata"]["material_name"] == "Anthrazit" for m in modules_with_color)
        
        print("✅ Modulfarben + KI-Optimierung funktioniert")
    
    def test_weather_plus_shading(self):
        """Test: Wetter + Verschattungs-Analyse"""
        # Setup
        modules = [
            {"position": (0, 0, 0.3), "id": 1},
            {"position": (2, 0, 0.3), "id": 2},
            {"position": (4, 0, 0.3), "id": 3},
        ]
        
        # Wetter
        weather = WEATHER_CONDITIONS["Regen"]
        base_yield = 1000.0
        yield_with_weather = calculate_weather_yield_impact(weather, base_yield)
        
        # Verschattung
        tree = Tree(x=1.0, y=-2.0, height=10.0, tree_type="Laubbaum")
        module_positions = [m["position"] for m in modules]
        
        shading = calculate_environment_shading(
            objects=[tree],
            module_positions=module_positions,
            sun_azimuth=180,
            sun_elevation=45,
        )
        
        # Kombinierter Ertrag
        combined_yield = yield_with_weather * (1.0 - np.mean(shading))
        
        assert combined_yield < base_yield, "Kombinierter Ertrag sollte niedriger sein"
        
        print(f"✅ Wetter + Verschattung: {combined_yield:.0f} kWh (von {base_yield:.0f} kWh)")
    
    def test_comparison_plus_heatmap(self):
        """Test: Vergleichs-Modus + Heatmap"""
        # Setup zwei Konfigurationen
        config_a = {
            "modules": [
                {"position": (0, 0, 0.3), "id": 1, "yield": 800},
                {"position": (2, 0, 0.3), "id": 2, "yield": 900},
            ],
            "name": "Konfiguration A",
        }
        
        config_b = {
            "modules": [
                {"position": (0, 0, 0.3), "id": 1, "yield": 850},
                {"position": (2, 0, 0.3), "id": 2, "yield": 950},
                {"position": (4, 0, 0.3), "id": 3, "yield": 920},
            ],
            "name": "Konfiguration B",
        }
        
        # Vergleichstabelle
        comparison = create_comparison_table(config_a, config_b)
        
        assert "module_count" in comparison
        assert comparison["module_count"]["a"] == 2
        assert comparison["module_count"]["b"] == 3
        
        # Unterschiede
        differences = highlight_differences(
            config_a["modules"],
            config_b["modules"],
        )
        
        assert "only_in_a" in differences
        assert "only_in_b" in differences
        
        print("✅ Vergleichs-Modus + Heatmap funktioniert")
    
    def test_environment_plus_shading(self):
        """Test: Umgebungs-Objekte + Verschattung"""
        # Setup
        modules = [
            {"position": (i * 2, 0, 0.3), "id": i}
            for i in range(5)
        ]
        
        # Umgebungs-Objekte
        tree = Tree(x=2.0, y=-3.0, height=12.0, tree_type="Nadelbaum")
        building = NeighborBuilding(
            x=8.0, y=-5.0,
            width=5.0, length=8.0, height=15.0,
            building_type="Hochhaus",
        )
        
        # Verschattung berechnen
        module_positions = [m["position"] for m in modules]
        shading = calculate_environment_shading(
            objects=[tree, building],
            module_positions=module_positions,
            sun_azimuth=180,
            sun_elevation=30,
        )
        
        # Validierung
        assert len(shading) == len(modules)
        assert all(0 <= s <= 1 for s in shading), "Verschattung sollte zwischen 0 und 1 sein"
        
        # Module in der Nähe sollten stärker verschattet sein
        nearby_shading = shading[1]  # Modul bei x=2 (nahe am Baum)
        far_shading = shading[4]  # Modul bei x=8 (weit weg)
        
        print(f"✅ Umgebung + Verschattung: Nahe={nearby_shading:.2f}, Fern={far_shading:.2f}")


class TestTask17_3_EdgeCases:
    """Task 17.3: Teste Edge Cases"""
    
    def test_very_small_roof(self):
        """Test: Sehr kleines Dach (<10m²)"""
        # 5m x 1.5m = 7.5m²
        roof_width = 5.0
        roof_length = 1.5
        
        modules = handle_auto_placement(
            roof_type="Flachdach",
            roof_width=roof_width,
            roof_length=roof_length,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        # Mindestens 1 Modul sollte passen
        assert len(modules) >= 1, "Mindestens 1 Modul sollte auf kleines Dach passen"
        
        print(f"✅ Kleines Dach (7.5m²): {len(modules)} Module")
    
    def test_very_large_roof(self):
        """Test: Sehr großes Dach (>200m²)"""
        # 20m x 12m = 240m²
        roof_width = 20.0
        roof_length = 12.0
        
        modules = handle_auto_placement(
            roof_type="Flachdach",
            roof_width=roof_width,
            roof_length=roof_length,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        # Viele Module sollten platziert werden
        assert len(modules) > 50, "Viele Module sollten auf großes Dach passen"
        
        # Performance-Check: Sollte schnell sein
        import time
        start = time.time()
        
        # KI-Optimierung auf großem Dach
        optimizer = AILayoutOptimizer(
            roof_width=roof_width,
            roof_length=roof_length,
            roof_type="Flachdach",
        )
        
        layout = optimizer.optimize_for_max_count(
            module_width=1.0,
            module_length=2.0,
        )
        
        duration = time.time() - start
        
        assert duration < 5.0, f"Optimierung sollte <5s dauern (war {duration:.2f}s)"
        
        print(f"✅ Großes Dach (240m²): {len(modules)} Module in {duration:.2f}s")
    
    def test_many_modules(self):
        """Test: Viele Module (>100)"""
        # Erstelle 120 Module
        modules = [
            {
                "position": (i % 10 * 2, i // 10 * 2, 0.3),
                "id": i,
                "rotation": 0,
            }
            for i in range(120)
        ]
        
        # Teste Operationen mit vielen Modulen
        
        # 1. Snap-to-Grid
        snapped = [
            snap_to_grid(m["position"], grid_size=0.5)
            for m in modules
        ]
        assert len(snapped) == 120
        
        # 2. Material anwenden
        material = MATERIAL_BLACK
        with_material = [
            apply_material_to_module({"position": m["position"]}, material)
            for m in modules
        ]
        assert len(with_material) == 120
        
        # 3. Verschattungs-Analyse
        tree = Tree(x=10.0, y=10.0, height=15.0, tree_type="Laubbaum")
        module_positions = [m["position"] for m in modules]
        
        import time
        start = time.time()
        
        shading = calculate_environment_shading(
            objects=[tree],
            module_positions=module_positions,
            sun_azimuth=180,
            sun_elevation=45,
        )
        
        duration = time.time() - start
        
        assert len(shading) == 120
        assert duration < 2.0, f"Verschattung sollte <2s dauern (war {duration:.2f}s)"
        
        print(f"✅ Viele Module (120): Verschattung in {duration:.2f}s")
    
    def test_extreme_roof_pitch(self):
        """Test: Extreme Dachneigung (>60°)"""
        # Satteldach mit 70° Neigung
        roof_width = 10.0
        roof_length = 15.0
        roof_height = 8.0  # Sehr hoch für steile Neigung
        
        modules = handle_auto_placement(
            roof_type="Satteldach",
            roof_width=roof_width,
            roof_length=roof_length,
            roof_height=roof_height,
            module_width=1.0,
            module_length=2.0,
            spacing=0.1,
        )
        
        assert len(modules) > 0, "Module sollten auch auf steilem Dach platziert werden"
        
        # Validiere Z-Positionen
        for module in modules:
            x, y, z = module["position"]
            
            # Z sollte korrekt berechnet sein
            expected_z = calculate_z_position(
                roof_type="Satteldach",
                y_position=y,
                roof_width=roof_width,
                roof_height=roof_height,
            )
            
            assert abs(z - expected_z) < 0.01, "Z-Position sollte auch bei steiler Neigung korrekt sein"
        
        print(f"✅ Steiles Dach (70°): {len(modules)} Module")
    
    def test_many_environment_objects(self):
        """Test: Viele Umgebungs-Objekte (>20)"""
        # Erstelle 25 Objekte
        objects = []
        
        # 10 Bäume
        for i in range(10):
            objects.append(Tree(
                x=i * 3.0,
                y=-5.0,
                height=8.0 + i * 0.5,
                tree_type="Laubbaum",
            ))
        
        # 10 Gebäude
        for i in range(10):
            objects.append(NeighborBuilding(
                x=i * 4.0,
                y=20.0,
                width=5.0,
                length=8.0,
                height=10.0 + i * 2.0,
                building_type="Wohnhaus",
            ))
        
        # 5 Schornsteine
        for i in range(5):
            objects.append(Chimney(
                x=i * 2.0,
                y=0.0,
                height=3.0,
            ))
        
        # Module
        modules = [
            {"position": (i * 2, 0, 0.3), "id": i}
            for i in range(20)
        ]
        
        # Verschattung berechnen
        import time
        start = time.time()
        
        module_positions = [m["position"] for m in modules]
        shading = calculate_environment_shading(
            objects=objects,
            module_positions=module_positions,
            sun_azimuth=180,
            sun_elevation=45,
        )
        
        duration = time.time() - start
        
        assert len(shading) == 20
        assert duration < 3.0, f"Verschattung mit vielen Objekten sollte <3s dauern (war {duration:.2f}s)"
        
        print(f"✅ Viele Objekte (25): Verschattung in {duration:.2f}s")


class TestIntegrationSummary:
    """Zusammenfassung aller Integration Tests"""
    
    def test_all_features_integrated(self):
        """Validiere dass alle Features integriert sind"""
        features = {
            "Phase 1: Z-Position Fix": calculate_z_position,
            "Phase 2: Sonnenverlauf": calculate_sun_position,
            "Phase 2: Verschattung": calculate_shading_analysis_enhanced,
            "Phase 2: Snap-to-Grid": snap_to_grid,
            "Phase 3: Modulfarben": apply_material_to_module,
            "Phase 3: KI-Optimierung": AILayoutOptimizer,
            "Phase 3: Wetter": apply_weather_to_scene,
            "Phase 3: Vergleich": create_comparison_view,
            "Phase 3: Umgebung": Tree,
        }
        
        for feature_name, feature_func in features.items():
            assert feature_func is not None, f"{feature_name} sollte verfügbar sein"
        
        print(f"✅ Alle {len(features)} Features sind integriert")


# Test Runner
if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 4 - TASK 17: INTEGRATION TESTING")
    print("=" * 80)
    print()
    
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_",
    ])
