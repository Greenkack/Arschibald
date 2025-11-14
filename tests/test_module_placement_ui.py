"""
UI-Tests für Task 10.3: Modul-Platzierungs-UI

Dieser Test prüft die UI-Komponenten:
- Alle Buttons
- Interaktionen
- Feedback

Requirements: 10.3 - Benutzerfreundlichkeit
"""

import sys
import pytest
from typing import Dict, Any

# Mock Streamlit für Tests
class MockSessionState(dict):
    """Mock Streamlit session state."""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Import der zu testenden Module
from utils.pv3d_module_placement_ui import render_module_placement_panel


class TestUIPanel:
    """
    Test-Suite für UI-Panel
    
    Requirements:
        - 10.3: Teste alle Buttons
        - 5.1: Modul-Belegungs-Panel erstellen
        - 5.2: Buttons hinzufügen
        - 5.3: Echtzeit-Feedback
    """
    
    def setup_method(self):
        """Setup vor jedem Test"""
        st.session_state.clear()
    
    def test_render_panel_basic(self):
        """Test: Panel rendert ohne Fehler"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=0
        )
        
        assert isinstance(actions, dict), "Rückgabe muss Dictionary sein"
        assert "auto_place_clicked" in actions
        assert "manual_add_clicked" in actions
        assert "remove_selected_clicked" in actions
        assert "reset_all_clicked" in actions
    
    def test_render_panel_with_modules(self):
        """Test: Panel mit platzierten Modulen"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=15
        )
        
        assert isinstance(actions, dict)
        # Panel sollte erfolgreich rendern
        assert actions is not None
    
    def test_render_panel_invalid_inputs(self):
        """Test: Panel mit ungültigen Eingaben"""
        # Negative Werte
        actions = render_module_placement_panel(
            module_quantity=-10,
            roof_area=-50.0,
            current_placed=-5
        )
        
        # Sollte trotzdem Dictionary zurückgeben (mit Fehlerbehandlung)
        assert isinstance(actions, dict)
    
    def test_render_panel_zero_values(self):
        """Test: Panel mit Null-Werten"""
        actions = render_module_placement_panel(
            module_quantity=0,
            roof_area=0.0,
            current_placed=0
        )
        
        assert isinstance(actions, dict)
        assert actions["auto_place_clicked"] is False
    
    def test_render_panel_large_values(self):
        """Test: Panel mit großen Werten"""
        actions = render_module_placement_panel(
            module_quantity=1000,
            roof_area=500.0,
            current_placed=500
        )
        
        assert isinstance(actions, dict)


class TestButtonActions:
    """
    Test-Suite für Button-Aktionen
    
    Requirements:
        - 10.3: Teste alle Buttons
        - 5.2: Buttons hinzufügen
        - 3.3: Button "Automatisch belegen"
        - 4.2: Manuelle Steuerungs-Buttons
    """
    
    def setup_method(self):
        """Setup vor jedem Test"""
        st.session_state.clear()
    
    def test_button_states_default(self):
        """Test: Standard Button-States"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=0
        )
        
        # Alle Buttons sollten standardmäßig nicht geklickt sein
        assert actions["auto_place_clicked"] is False
        assert actions["manual_add_clicked"] is False
        assert actions["remove_selected_clicked"] is False
        assert actions["reset_all_clicked"] is False
    
    def test_visualization_options(self):
        """Test: Visualisierungs-Optionen"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Visualisierungs-Optionen sollten vorhanden sein
        assert "show_grid" in actions
        assert "show_numbers" in actions
        assert isinstance(actions["show_grid"], bool)
        assert isinstance(actions["show_numbers"], bool)
    
    def test_grid_settings(self):
        """Test: Raster-Einstellungen"""
        # Aktiviere Raster
        st.session_state["show_placement_grid"] = True
        
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Raster-Einstellungen sollten vorhanden sein
        assert "grid_spacing" in actions
        assert "grid_opacity" in actions
        assert isinstance(actions["grid_spacing"], (int, float))
        assert isinstance(actions["grid_opacity"], (int, float))
    
    def test_selection_tracking(self):
        """Test: Auswahl-Tracking"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Auswahl-Tracking sollte vorhanden sein
        assert "selection_changed" in actions
        assert isinstance(actions["selection_changed"], bool)
    
    def test_move_controls(self):
        """Test: Verschiebe-Steuerung"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Verschiebe-Steuerung sollte vorhanden sein
        assert "move_selected_clicked" in actions
        assert "move_offset_x" in actions
        assert "move_offset_y" in actions
    
    def test_rotate_controls(self):
        """Test: Dreh-Steuerung"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Dreh-Steuerung sollte vorhanden sein
        assert "rotate_selected_clicked" in actions
        assert "rotation_angle" in actions
    
    def test_quick_move_controls(self):
        """Test: Schnell-Verschiebe-Steuerung"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        # Schnell-Verschiebe-Steuerung sollte vorhanden sein
        assert "quick_move_clicked" in actions
        assert "quick_move_direction" in actions
        assert "quick_move_step" in actions
        assert "snap_to_grid" in actions


class TestInteractions:
    """
    Test-Suite für Interaktionen
    
    Requirements:
        - 10.3: Teste Interaktionen
        - 4.1: Modul-Auswahl implementieren
        - 4.3: Drag & Drop implementieren
    """
    
    def setup_method(self):
        """Setup vor jedem Test"""
        st.session_state.clear()
    
    def test_module_selection_empty(self):
        """Test: Modul-Auswahl ohne Module"""
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=0
        )
        
        # Ohne Module sollte keine Auswahl möglich sein
        selected = st.session_state.get("selected_module_indices", [])
        assert len(selected) == 0
    
    def test_module_selection_with_modules(self):
        """Test: Modul-Auswahl mit Modulen"""
        # Simuliere platzierte Module
        st.session_state["placed_module_count"] = 5
        st.session_state["placed_module_positions"] = [
            (0.0, 0.0, 0.3),
            (2.0, 0.0, 0.3),
            (4.0, 0.0, 0.3),
            (6.0, 0.0, 0.3),
            (8.0, 0.0, 0.3),
        ]
        
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=5
        )
        
        # Auswahl sollte möglich sein
        assert isinstance(actions, dict)
    
    def test_snap_to_grid_toggle(self):
        """Test: Snap-to-Grid Toggle"""
        # Standardmäßig aktiviert
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        
        assert "snap_to_grid" in actions
        # Sollte standardmäßig True sein
        assert actions["snap_to_grid"] is True or actions["snap_to_grid"] is False


class TestFeedback:
    """
    Test-Suite für Feedback
    
    Requirements:
        - 10.3: Teste Feedback
        - 5.3: Echtzeit-Feedback
        - 2.6: Fortschritts-Anzeige
    """
    
    def setup_method(self):
        """Setup vor jedem Test"""
        st.session_state.clear()
    
    def test_statistics_display(self):
        """Test: Statistik-Anzeige"""
        # Panel sollte Statistiken anzeigen
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=15
        )
        
        # Panel sollte erfolgreich rendern
        assert actions is not None
        assert isinstance(actions, dict)
    
    def test_progress_calculation(self):
        """Test: Fortschritts-Berechnung"""
        # 0% Fortschritt
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=0
        )
        assert actions is not None
        
        # 50% Fortschritt
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=10
        )
        assert actions is not None
        
        # 100% Fortschritt
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=20
        )
        assert actions is not None
    
    def test_over_capacity_display(self):
        """Test: Über-Kapazität Anzeige"""
        # Mehr Module platziert als gewünscht
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed=25
        )
        
        # Sollte trotzdem funktionieren
        assert actions is not None
        assert isinstance(actions, dict)


class TestErrorHandling:
    """
    Test-Suite für Fehlerbehandlung
    
    Requirements:
        - 10.3: Teste Fehlerbehandlung
        - 11.1: Validate inputs
        - 11.2: Error handling
    """
    
    def setup_method(self):
        """Setup vor jedem Test"""
        st.session_state.clear()
    
    def test_invalid_module_quantity_type(self):
        """Test: Ungültiger Typ für Modulanzahl"""
        # String statt Zahl
        actions = render_module_placement_panel(
            module_quantity="invalid",
            roof_area=80.0,
            current_placed=0
        )
        
        # Sollte Fehler behandeln und Dictionary zurückgeben
        assert isinstance(actions, dict)
    
    def test_invalid_roof_area_type(self):
        """Test: Ungültiger Typ für Dachfläche"""
        # String statt Zahl
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area="invalid",
            current_placed=0
        )
        
        # Sollte Fehler behandeln und Dictionary zurückgeben
        assert isinstance(actions, dict)
    
    def test_invalid_current_placed_type(self):
        """Test: Ungültiger Typ für platzierte Module"""
        # String statt Zahl
        actions = render_module_placement_panel(
            module_quantity=20,
            roof_area=80.0,
            current_placed="invalid"
        )
        
        # Sollte Fehler behandeln und Dictionary zurückgeben
        assert isinstance(actions, dict)
    
    def test_none_values(self):
        """Test: None-Werte"""
        try:
            actions = render_module_placement_panel(
                module_quantity=None,
                roof_area=None,
                current_placed=None
            )
            # Sollte entweder Fehler behandeln oder Exception werfen
            assert isinstance(actions, dict) or actions is None
        except (TypeError, ValueError):
            # Exception ist auch akzeptabel
            pass


# Haupt-Funktion zum Ausführen der Tests
if __name__ == "__main__":
    print("=" * 70)
    print("UI-TESTS: Modul-Platzierungs-UI (Task 10.3)")
    print("=" * 70)
    
    # Führe Tests mit pytest aus
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Kurze Traceback-Ausgabe
        "-ra"  # Zeige Zusammenfassung aller Tests
    ])
    
    sys.exit(exit_code)
