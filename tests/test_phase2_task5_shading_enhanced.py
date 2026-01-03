"""
Unit Tests für Task 5: Erweiterte Verschattungs-Analyse

Testet die neuen Funktionen:
- calculate_shading_analysis_enhanced()
- add_neighboring_buildings()
- create_shading_timeline_chart()
- identify_heavily_shaded_modules()
- generate_optimization_suggestions()
"""

import pytest
import sys
import os

# Füge Projekt-Root zum Python-Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pv3d_analysis import (
    calculate_shading_analysis_enhanced,
    add_neighboring_buildings,
    get_neighboring_buildings,
    clear_neighboring_buildings,
    calculate_building_shadow,
    create_shading_timeline_chart,
    identify_heavily_shaded_modules,
    generate_optimization_suggestions
)
from utils.pv3d import BuildingDims, ModuleTransform


class TestShadingAnalysisEnhanced:
    """Tests für erweiterte Verschattungs-Analyse."""
    
    def test_enhanced_analysis_basic(self):
        """Test: Basis-Funktionalität der erweiterten Analyse."""
        positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0), (4.0, 0.0, 6.0)]
        transforms = {i: ModuleTransform(index=i) for i in range(3)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        result = calculate_shading_analysis_enhanced(
            positions, transforms, 180.0, 45.0, dims
        )
        
        # Prüfe Struktur
        assert "direct_shading" in result
        assert "indirect_shading" in result
        assert "total_shading" in result
        assert "shading_sources" in result
        
        # Prüfe Längen
        assert len(result["direct_shading"]) == 3
        assert len(result["indirect_shading"]) == 3
        assert len(result["total_shading"]) == 3
        assert len(result["shading_sources"]) == 3
    
    def test_enhanced_analysis_night(self):
        """Test: Vollständige Verschattung bei Nacht."""
        positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        transforms = {i: ModuleTransform(index=i) for i in range(2)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        # Sonne unter Horizont
        result = calculate_shading_analysis_enhanced(
            positions, transforms, 180.0, -10.0, dims
        )
        
        # Alle Module sollten vollständig verschattet sein
        assert all(s == 1.0 for s in result["direct_shading"])
        assert all(s == 1.0 for s in result["total_shading"])
        assert all(src == "night" for src in result["shading_sources"])
    
    def test_enhanced_analysis_indirect_disabled(self):
        """Test: Indirekte Verschattung kann deaktiviert werden."""
        positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        transforms = {i: ModuleTransform(index=i) for i in range(2)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        result = calculate_shading_analysis_enhanced(
            positions, transforms, 180.0, 45.0, dims, include_indirect=False
        )
        
        # Indirekte Verschattung sollte 0 sein
        assert all(s == 0.0 for s in result["indirect_shading"])
    
    def test_enhanced_analysis_values_in_range(self):
        """Test: Verschattungswerte sind im Bereich [0, 1]."""
        positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0), (4.0, 0.0, 6.0)]
        transforms = {i: ModuleTransform(index=i) for i in range(3)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        result = calculate_shading_analysis_enhanced(
            positions, transforms, 180.0, 45.0, dims
        )
        
        # Alle Werte sollten zwischen 0 und 1 liegen
        for shading in result["direct_shading"]:
            assert 0.0 <= shading <= 1.0
        
        for shading in result["indirect_shading"]:
            assert 0.0 <= shading <= 1.0
        
        for shading in result["total_shading"]:
            assert 0.0 <= shading <= 1.0


class TestNeighboringBuildings:
    """Tests für Nachbargebäude-Integration."""
    
    def setup_method(self):
        """Setup vor jedem Test."""
        clear_neighboring_buildings()
    
    def test_add_neighboring_buildings(self):
        """Test: Nachbargebäude hinzufügen."""
        buildings = [
            {"x": 15.0, "y": 0.0, "width": 10.0, "length": 8.0, "height": 8.0},
            {"x": -15.0, "y": 5.0, "width": 12.0, "length": 10.0, "height": 10.0}
        ]
        
        add_neighboring_buildings(buildings)
        
        stored = get_neighboring_buildings()
        assert len(stored) == 2
        assert stored[0]["x"] == 15.0
        assert stored[1]["height"] == 10.0
    
    def test_clear_neighboring_buildings(self):
        """Test: Nachbargebäude löschen."""
        buildings = [
            {"x": 15.0, "y": 0.0, "width": 10.0, "length": 8.0, "height": 8.0}
        ]
        
        add_neighboring_buildings(buildings)
        assert len(get_neighboring_buildings()) == 1
        
        clear_neighboring_buildings()
        assert len(get_neighboring_buildings()) == 0
    
    def test_calculate_building_shadow(self):
        """Test: Schatten-Berechnung für Gebäude."""
        building = {
            "x": 10.0,
            "y": 0.0,
            "width": 8.0,
            "length": 6.0,
            "height": 10.0
        }
        
        # Sonne im Süden, 45° Elevation
        shadow = calculate_building_shadow(building, 180.0, 45.0)
        
        # Sollte 4 Eckpunkte haben
        assert len(shadow) == 4
        
        # Alle Punkte sollten Tupel sein
        assert all(isinstance(p, tuple) and len(p) == 2 for p in shadow)
    
    def test_calculate_building_shadow_night(self):
        """Test: Kein Schatten bei Nacht."""
        building = {
            "x": 10.0,
            "y": 0.0,
            "width": 8.0,
            "length": 6.0,
            "height": 10.0
        }
        
        # Sonne unter Horizont
        shadow = calculate_building_shadow(building, 180.0, -10.0)
        
        # Sollte leer sein
        assert len(shadow) == 0


class TestShadingTimelineChart:
    """Tests für Verschattungs-Verlauf Diagramm."""
    
    def test_create_timeline_chart(self):
        """Test: Diagramm-Erstellung."""
        positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        transforms = {i: ModuleTransform(index=i) for i in range(2)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        fig = create_shading_timeline_chart(
            0, positions, transforms, dims, "2024-06-21", 51.0
        )
        
        # Prüfe dass Figure erstellt wurde
        assert fig is not None
        assert len(fig.data) > 0
        
        # Prüfe Trace-Name
        assert fig.data[0].name == "Verschattung"
    
    def test_timeline_chart_data_points(self):
        """Test: Diagramm hat korrekte Anzahl Datenpunkte."""
        positions = [(0.0, 0.0, 6.0)]
        transforms = {0: ModuleTransform(index=0)}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        fig = create_shading_timeline_chart(
            0, positions, transforms, dims
        )
        
        # Sollte 15 Stunden haben (6:00 - 20:00)
        assert len(fig.data[0].x) == 15
        assert len(fig.data[0].y) == 15


class TestOptimizationSuggestions:
    """Tests für Optimierungsvorschläge."""
    
    def test_identify_heavily_shaded_modules(self):
        """Test: Identifikation stark verschatteter Module."""
        result = {
            "total_shading": [0.2, 0.7, 0.3, 0.8, 0.5],
            "shading_sources": ["none", "module", "none", "building", "module"],
            "direct_shading": [0.1, 0.7, 0.2, 0.8, 0.4]
        }
        
        heavily_shaded = identify_heavily_shaded_modules(result, 60.0)
        
        # Module 1 (70%) und 3 (80%) sollten identifiziert werden
        assert 1 in heavily_shaded
        assert 3 in heavily_shaded
        assert len(heavily_shaded) == 2
    
    def test_identify_heavily_shaded_custom_threshold(self):
        """Test: Benutzerdefinierter Schwellwert."""
        result = {
            "total_shading": [0.2, 0.7, 0.3, 0.8],
            "shading_sources": ["none", "module", "none", "building"],
            "direct_shading": [0.1, 0.7, 0.2, 0.8]
        }
        
        # Mit 50% Schwellwert
        heavily_shaded = identify_heavily_shaded_modules(result, 50.0)
        
        # Module 1 (70%) und 3 (80%) sollten identifiziert werden
        assert len(heavily_shaded) == 2
    
    def test_generate_optimization_suggestions(self):
        """Test: Generierung von Optimierungsvorschlägen."""
        heavily_shaded = [1, 3]
        positions = [(0, 0, 6), (2, 0, 6), (4, 0, 6), (6, 0, 6)]
        result = {
            "total_shading": [0.2, 0.7, 0.3, 0.8],
            "shading_sources": ["none", "module", "none", "building"],
            "direct_shading": [0.1, 0.7, 0.2, 0.8]
        }
        
        suggestions = generate_optimization_suggestions(
            heavily_shaded, positions, result
        )
        
        # Sollte 2 Vorschläge haben
        assert len(suggestions) == 2
        
        # Prüfe Struktur
        for suggestion in suggestions:
            assert "module_index" in suggestion
            assert "shading_percent" in suggestion
            assert "issue" in suggestion
            assert "suggestion" in suggestion
            assert "priority" in suggestion
            assert "current_position" in suggestion
    
    def test_suggestions_sorted_by_priority(self):
        """Test: Vorschläge sind nach Priorität sortiert."""
        heavily_shaded = [1, 2]
        positions = [(0, 0, 6), (2, 0, 6), (4, 0, 6)]
        result = {
            "total_shading": [0.2, 0.7, 0.85],
            "shading_sources": ["none", "module", "building"],
            "direct_shading": [0.1, 0.7, 0.85]
        }
        
        suggestions = generate_optimization_suggestions(
            heavily_shaded, positions, result
        )
        
        # Erste Vorschlag sollte höchste Priorität haben
        assert suggestions[0]["priority"] == "high"
        
        # Sollte nach Verschattungsgrad sortiert sein (bei gleicher Priorität)
        if len(suggestions) > 1 and suggestions[0]["priority"] == suggestions[1]["priority"]:
            assert suggestions[0]["shading_percent"] >= suggestions[1]["shading_percent"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
