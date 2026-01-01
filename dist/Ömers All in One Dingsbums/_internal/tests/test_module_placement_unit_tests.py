"""
Unit Tests für Task 10.1: Modul-Platzierungs-System

Dieser Test prüft die Kern-Funktionalität des Modul-Platzierungs-Systems:
- Grid-Berechnung
- Kollisionserkennung
- Positionierung

Requirements: 10.1 - Zuverlässigkeit
"""

import sys
import pytest
from typing import List, Tuple

# Import der zu testenden Module
from utils.pv3d_grid_calculator import (
    calculate_module_grid,
    calculate_max_modules,
    get_module_dimensions,
    _calculate_modules_per_line,
    _validate_inputs,
    PV_W,
    PV_H,
    PV_T,
    DEFAULT_SPACING,
    DEFAULT_MARGIN
)

from utils.pv3d_placement_handler import (
    check_module_collision,
    calculate_z_position,
    calculate_tilt_angle,
    handle_auto_placement,
    handle_reset_placement
)


class TestGridCalculation:
    """
    Test-Suite für Grid-Berechnung
    
    Requirements:
        - 10.1: Teste Grid-Berechnung
        - 3.1: Grid-Berechnung korrigieren
        - 3.2: Platzierungs-Algorithmus optimieren
    """
    
    def test_calculate_module_grid_basic(self):
        """Test: Basis Grid-Berechnung mit Standard-Parametern"""
        positions = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20
        )
        
        assert isinstance(positions, list), "Rückgabe muss Liste sein"
        assert len(positions) > 0, "Mindestens ein Modul sollte platziert werden"
        assert len(positions) <= 20, "Nicht mehr als gewünscht platzieren"
        
        # Prüfe Format der Positionen
        for pos in positions:
            assert isinstance(pos, tuple), "Position muss Tuple sein"
            assert len(pos) == 2, "Position muss (x, y) sein"
            assert isinstance(pos[0], (int, float)), "X muss Zahl sein"
            assert isinstance(pos[1], (int, float)), "Y muss Zahl sein"
    
    def test_calculate_module_grid_empty_roof(self):
        """Test: Leeres Dach (zu klein für Module)"""
        positions = calculate_module_grid(
            roof_length=0.5,  # Zu klein
            roof_width=0.5,
            module_quantity=10
        )
        
        assert len(positions) == 0, "Keine Module auf zu kleinem Dach"
    
    def test_calculate_module_grid_invalid_inputs(self):
        """Test: Ungültige Eingaben"""
        # Negative Dimensionen
        positions = calculate_module_grid(
            roof_length=-10.0,
            roof_width=8.0,
            module_quantity=20
        )
        assert len(positions) == 0, "Negative Länge sollte leere Liste ergeben"
        
        # Negative Breite
        positions = calculate_module_grid(
            roof_length=10.0,
            roof_width=-8.0,
            module_quantity=20
        )
        assert len(positions) == 0, "Negative Breite sollte leere Liste ergeben"
        
        # Null Module
        positions = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=0
        )
        assert len(positions) == 0, "Null Module sollte leere Liste ergeben"
    
    def test_calculate_module_grid_exceeds_capacity(self):
        """Test: Mehr Module gewünscht als passen"""
        positions = calculate_module_grid(
            roof_length=5.0,
            roof_width=4.0,
            module_quantity=100  # Viel zu viele
        )
        
        # Sollte nur so viele platzieren wie passen
        max_possible = calculate_max_modules(5.0, 4.0)
        assert len(positions) == max_possible, \
            f"Sollte maximal {max_possible} Module platzieren"
    
    def test_calculate_module_grid_landscape_orientation(self):
        """Test: Landscape-Orientierung"""
        positions_portrait = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            orientation="portrait"
        )
        
        positions_landscape = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            orientation="landscape"
        )
        
        # Landscape sollte andere Anzahl ergeben (Module sind gedreht)
        # Nicht unbedingt gleich viele Module
        assert isinstance(positions_landscape, list)
        assert len(positions_landscape) > 0
    
    def test_calculate_module_grid_spacing_and_margin(self):
        """Test: Custom Spacing und Margin"""
        positions_default = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20
        )
        
        positions_large_spacing = calculate_module_grid(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            spacing=0.20,  # Größerer Abstand
            margin=0.50    # Größerer Rand
        )
        
        # Mit größerem Spacing/Margin sollten weniger Module passen
        assert len(positions_large_spacing) <= len(positions_default), \
            "Größerer Spacing/Margin sollte weniger Module ergeben"
    
    def test_calculate_max_modules(self):
        """Test: Maximale Modulanzahl berechnen"""
        max_modules = calculate_max_modules(10.0, 8.0)
        
        assert isinstance(max_modules, int), "Rückgabe muss Integer sein"
        assert max_modules > 0, "Sollte mindestens ein Modul passen"
        
        # Prüfe ob tatsächlich so viele passen
        positions = calculate_module_grid(10.0, 8.0, max_modules)
        assert len(positions) == max_modules, \
            "Berechnete Maximalzahl sollte tatsächlich passen"
    
    def test_get_module_dimensions(self):
        """Test: Modul-Dimensionen abrufen"""
        # Portrait
        w, h, t = get_module_dimensions("portrait")
        assert w == PV_W, f"Portrait Breite sollte {PV_W}m sein"
        assert h == PV_H, f"Portrait Höhe sollte {PV_H}m sein"
        assert t == PV_T, f"Dicke sollte {PV_T}m sein"
        
        # Landscape
        w, h, t = get_module_dimensions("landscape")
        assert w == PV_H, f"Landscape Breite sollte {PV_H}m sein"
        assert h == PV_W, f"Landscape Höhe sollte {PV_W}m sein"
        assert t == PV_T, f"Dicke sollte {PV_T}m sein"
    
    def test_validate_inputs(self):
        """Test: Eingabe-Validierung"""
        # Gültige Eingaben
        result = _validate_inputs(10.0, 8.0, 20, 0.05, 0.30)
        assert result["valid"] is True, "Gültige Eingaben sollten akzeptiert werden"
        
        # Ungültige Länge
        result = _validate_inputs(-10.0, 8.0, 20, 0.05, 0.30)
        assert result["valid"] is False, "Negative Länge sollte abgelehnt werden"
        
        # Ungültige Breite
        result = _validate_inputs(10.0, -8.0, 20, 0.05, 0.30)
        assert result["valid"] is False, "Negative Breite sollte abgelehnt werden"
        
        # Zu große Margins
        result = _validate_inputs(10.0, 8.0, 20, 0.05, 6.0)
        assert result["valid"] is False, "Zu große Margins sollten abgelehnt werden"
    
    def test_calculate_modules_per_line(self):
        """Test: Module pro Linie berechnen"""
        # Genug Platz für 5 Module (1.05m breit + 0.05m Spacing)
        # 5 * 1.05 + 4 * 0.05 = 5.25 + 0.20 = 5.45m
        modules = _calculate_modules_per_line(
            available_space=5.5,
            module_size=1.05,
            spacing=0.05
        )
        assert modules == 5, f"Sollte 5 Module sein, ist {modules}"
        
        # Zu wenig Platz
        modules = _calculate_modules_per_line(
            available_space=0.5,
            module_size=1.05,
            spacing=0.05
        )
        assert modules == 0, "Sollte 0 Module sein bei zu wenig Platz"


class TestCollisionDetection:
    """
    Test-Suite für Kollisionserkennung
    
    Requirements:
        - 10.1: Teste Kollisionserkennung
        - 7.1: Modul-Modul Kollision
        - 7.2: Modul-Dach Kollision
    """
    
    def test_check_module_collision_no_collision(self):
        """Test: Keine Kollision (Module weit auseinander)"""
        result = check_module_collision(
            new_position=(0.0, 0.0, 1.0),
            existing_positions=[(5.0, 5.0, 1.0)],
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is False, "Sollte keine Kollision erkennen"
        assert result["type"] == "none", "Typ sollte 'none' sein"
    
    def test_check_module_collision_module_overlap(self):
        """Test: Modul-Modul Überlappung"""
        result = check_module_collision(
            new_position=(0.0, 0.0, 1.0),
            existing_positions=[(0.5, 0.5, 1.0)],  # Sehr nah
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is True, "Sollte Kollision erkennen"
        assert result["type"] == "module", "Typ sollte 'module' sein"
        assert result["colliding_index"] == 0, "Sollte Index 0 zurückgeben"
    
    def test_check_module_collision_boundary_left(self):
        """Test: Linke Dachkante überschritten"""
        result = check_module_collision(
            new_position=(-6.0, 0.0, 1.0),  # Weit links
            existing_positions=[],
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is True, "Sollte Grenz-Kollision erkennen"
        assert result["type"] == "boundary", "Typ sollte 'boundary' sein"
    
    def test_check_module_collision_boundary_right(self):
        """Test: Rechte Dachkante überschritten"""
        result = check_module_collision(
            new_position=(6.0, 0.0, 1.0),  # Weit rechts
            existing_positions=[],
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is True, "Sollte Grenz-Kollision erkennen"
        assert result["type"] == "boundary", "Typ sollte 'boundary' sein"
    
    def test_check_module_collision_boundary_top(self):
        """Test: Obere Dachkante überschritten"""
        result = check_module_collision(
            new_position=(0.0, 5.0, 1.0),  # Weit oben
            existing_positions=[],
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is True, "Sollte Grenz-Kollision erkennen"
        assert result["type"] == "boundary", "Typ sollte 'boundary' sein"
    
    def test_check_module_collision_boundary_bottom(self):
        """Test: Untere Dachkante überschritten"""
        result = check_module_collision(
            new_position=(0.0, -5.0, 1.0),  # Weit unten
            existing_positions=[],
            roof_length=10.0,
            roof_width=8.0
        )
        
        assert result["collision"] is True, "Sollte Grenz-Kollision erkennen"
        assert result["type"] == "boundary", "Typ sollte 'boundary' sein"
    
    def test_check_module_collision_landscape_orientation(self):
        """Test: Kollision mit Landscape-Orientierung"""
        # In Landscape sind Module breiter (1.76m statt 1.05m)
        result = check_module_collision(
            new_position=(0.0, 0.0, 1.0),
            existing_positions=[(1.0, 0.0, 1.0)],  # 1m Abstand
            roof_length=10.0,
            roof_width=8.0,
            orientation="landscape"
        )
        
        # Mit Landscape sollte 1m Abstand zu Kollision führen
        # (1.76m / 2 + 1.76m / 2 = 1.76m > 1.0m)
        assert result["collision"] is True, \
            "Landscape-Module sollten bei 1m Abstand kollidieren"


class TestPositioning:
    """
    Test-Suite für Positionierung
    
    Requirements:
        - 10.1: Teste Positionierung
        - 2.2: Modul-Positionierung korrigieren
        - 6.1-6.4: Dachtyp-spezifische Logik
    """
    
    def test_calculate_z_position_flat_roof(self):
        """Test: Z-Position für Flachdach"""
        z = calculate_z_position("Flachdach", 0.0, 10.0)
        
        assert z == 0.30, f"Flachdach sollte 0.30m sein, ist {z}m"
    
    def test_calculate_z_position_gable_roof(self):
        """Test: Z-Position für Satteldach"""
        z = calculate_z_position("Satteldach", 35.0, 10.0)
        
        assert z == 0.15, f"Satteldach sollte 0.15m sein, ist {z}m"
    
    def test_calculate_z_position_shed_roof(self):
        """Test: Z-Position für Pultdach"""
        z = calculate_z_position("Pultdach", 20.0, 10.0)
        
        assert z == 0.15, f"Pultdach sollte 0.15m sein, ist {z}m"
    
    def test_calculate_z_position_hip_roof(self):
        """Test: Z-Position für Walmdach"""
        z = calculate_z_position("Walmdach", 30.0, 10.0)
        
        assert z == 0.15, f"Walmdach sollte 0.15m sein, ist {z}m"
    
    def test_calculate_tilt_angle_flat_roof(self):
        """Test: Neigungswinkel für Flachdach"""
        tilt = calculate_tilt_angle("Flachdach", 0.0)
        
        assert tilt == 30.0, f"Flachdach sollte 30° Neigung haben, ist {tilt}°"
    
    def test_calculate_tilt_angle_gable_roof(self):
        """Test: Neigungswinkel für Satteldach"""
        tilt = calculate_tilt_angle("Satteldach", 35.0)
        
        assert tilt == 35.0, \
            f"Satteldach sollte Dachneigung folgen (35°), ist {tilt}°"
    
    def test_calculate_tilt_angle_shed_roof(self):
        """Test: Neigungswinkel für Pultdach"""
        tilt = calculate_tilt_angle("Pultdach", 20.0)
        
        assert tilt == 20.0, \
            f"Pultdach sollte Dachneigung folgen (20°), ist {tilt}°"


# Haupt-Funktion zum Ausführen der Tests
if __name__ == "__main__":
    print("=" * 70)
    print("UNIT TESTS: Modul-Platzierungs-System (Task 10.1)")
    print("=" * 70)
    
    # Führe Tests mit pytest aus
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Kurze Traceback-Ausgabe
        "-ra"  # Zeige Zusammenfassung aller Tests
    ])
    
    sys.exit(exit_code)
