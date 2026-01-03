"""
Standalone Tests für Task 7.4 & 7.5: Move Preview & Keyboard Shortcuts

Diese Tests validieren die Implementierung von:
- Task 7.4: Vorschau bei Verschieben (Move Preview)
- Task 7.5: Tastatur-Shortcuts (Keyboard Shortcuts)

Requirements:
- 5.4: Vorschau bei Verschieben
- 5.5: Tastatur-Shortcuts
"""

import sys
from typing import Dict, Any, List, Tuple
from unittest.mock import MagicMock

# Mock Streamlit
sys.modules['streamlit'] = MagicMock()
import streamlit as st

# Import functions to test
from utils.pv3d_placement_handler import (
    create_move_preview,
    handle_keyboard_move,
    handle_keyboard_rotate,
    handle_keyboard_delete
)


def setup_session_state():
    """Setup mock session state for testing."""
    st.session_state = {
        "placed_module_positions": [
            (0.0, 0.0, 0.3),
            (2.0, 0.0, 0.3),
            (4.0, 0.0, 0.3)
        ],
        "module_orientations": ["portrait", "portrait", "portrait"]
    }


# ============================================================================
# TASK 7.4: MOVE PREVIEW TESTS
# ============================================================================

def test_create_move_preview_success():
    """Test 1: Erfolgreiche Vorschau-Erstellung ohne Kollision."""
    setup_session_state()
    
    # Use position (1.5, 2.0) which is safely away from existing modules
    # Existing modules are at (0.0, 0.0), (2.0, 0.0), (4.0, 0.0)
    # Module is 1.05m x 1.75m in portrait, needs >1.1m spacing
    result = create_move_preview(
        module_index=0,
        new_x=1.5,
        new_y=2.0,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Vorschau sollte erfolgreich sein"
    assert result["preview_position"] is not None, "Vorschau-Position sollte existieren"
    assert result["has_collision"] == False, f"Keine Kollision erwartet, aber: {result['collision_message']}"
    assert result["collision_type"] == "none", "Kollisionstyp sollte 'none' sein"
    assert result["color"] == "green", "Farbe sollte grün sein (keine Kollision)"
    print("✓ Test 1 passed: Erfolgreiche Vorschau ohne Kollision")


def test_create_move_preview_with_module_collision():
    """Test 2: Vorschau mit Modul-Kollision."""
    setup_session_state()
    
    # Versuche Modul 0 auf Position von Modul 1 zu verschieben
    result = create_move_preview(
        module_index=0,
        new_x=2.0,
        new_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Vorschau sollte erstellt werden"
    assert result["has_collision"] == True, "Kollision erwartet"
    assert result["collision_type"] == "module", "Kollisionstyp sollte 'module' sein"
    assert result["color"] == "red", "Farbe sollte rot sein (Kollision)"
    print("✓ Test 2 passed: Vorschau mit Modul-Kollision")


def test_create_move_preview_with_boundary_collision():
    """Test 3: Vorschau mit Dach-Grenz-Kollision."""
    setup_session_state()
    
    # Versuche Modul außerhalb des Dachs zu platzieren
    result = create_move_preview(
        module_index=0,
        new_x=15.0,  # Außerhalb des 10m Dachs
        new_y=0.0,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Vorschau sollte erstellt werden"
    assert result["has_collision"] == True, "Kollision erwartet"
    assert result["collision_type"] == "boundary", "Kollisionstyp sollte 'boundary' sein"
    assert result["color"] == "red", "Farbe sollte rot sein (Kollision)"
    print("✓ Test 3 passed: Vorschau mit Dach-Grenz-Kollision")


def test_create_move_preview_invalid_index():
    """Test 4: Vorschau mit ungültigem Modul-Index."""
    setup_session_state()
    
    result = create_move_preview(
        module_index=99,  # Ungültiger Index
        new_x=5.0,
        new_y=5.0,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == False, "Vorschau sollte fehlschlagen"
    assert result["preview_position"] is None, "Keine Vorschau-Position erwartet"
    assert "Ungültiger Modul-Index" in result["collision_message"], "Fehlermeldung erwartet"
    print("✓ Test 4 passed: Vorschau mit ungültigem Index")


# ============================================================================
# TASK 7.5: KEYBOARD SHORTCUTS TESTS
# ============================================================================

def test_handle_keyboard_move_right():
    """Test 5: Verschieben nach rechts (0.5m)."""
    setup_session_state()
    
    result = handle_keyboard_move(
        module_index=0,
        direction="right",
        step_size=0.5,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Verschiebung sollte erfolgreich sein"
    assert result["old_position"] == (0.0, 0.0, 0.3), "Alte Position korrekt"
    assert result["new_position"][0] == 0.5, "X-Position sollte um 0.5 erhöht sein"
    assert result["direction"] == "right", "Richtung korrekt"
    assert result["step_size"] == 0.5, "Schrittweite korrekt"
    print("✓ Test 5 passed: Verschieben nach rechts")


def test_handle_keyboard_move_left():
    """Test 6: Verschieben nach links (0.5m)."""
    setup_session_state()
    
    result = handle_keyboard_move(
        module_index=1,
        direction="left",
        step_size=0.5,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Verschiebung sollte erfolgreich sein"
    assert result["old_position"] == (2.0, 0.0, 0.3), "Alte Position korrekt"
    assert result["new_position"][0] == 1.5, "X-Position sollte um 0.5 reduziert sein"
    print("✓ Test 6 passed: Verschieben nach links")


def test_handle_keyboard_move_up():
    """Test 7: Verschieben nach hinten/oben (0.5m)."""
    setup_session_state()
    
    result = handle_keyboard_move(
        module_index=0,
        direction="up",
        step_size=0.5,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Verschiebung sollte erfolgreich sein"
    assert result["new_position"][1] == 0.5, "Y-Position sollte um 0.5 erhöht sein"
    print("✓ Test 7 passed: Verschieben nach hinten")


def test_handle_keyboard_move_down():
    """Test 8: Verschieben nach vorne/unten (0.5m)."""
    setup_session_state()
    
    result = handle_keyboard_move(
        module_index=0,
        direction="down",
        step_size=0.5,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == True, "Verschiebung sollte erfolgreich sein"
    assert result["new_position"][1] == -0.5, "Y-Position sollte um 0.5 reduziert sein"
    print("✓ Test 8 passed: Verschieben nach vorne")


def test_handle_keyboard_move_with_collision():
    """Test 9: Verschieben mit Kollision wird verhindert."""
    setup_session_state()
    
    # Versuche Modul 0 auf Position von Modul 1 zu verschieben
    result = handle_keyboard_move(
        module_index=0,
        direction="right",
        step_size=2.0,  # Würde auf Modul 1 kollidieren
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == False, "Verschiebung sollte fehlschlagen"
    assert "Kollision erkannt" in result["message"], "Kollisions-Meldung erwartet"
    # Position sollte unverändert bleiben
    assert st.session_state["placed_module_positions"][0] == (0.0, 0.0, 0.3), "Position sollte unverändert sein"
    print("✓ Test 9 passed: Verschieben mit Kollision verhindert")


def test_handle_keyboard_move_invalid_direction():
    """Test 10: Verschieben mit ungültiger Richtung."""
    setup_session_state()
    
    result = handle_keyboard_move(
        module_index=0,
        direction="diagonal",  # Ungültige Richtung
        step_size=0.5,
        roof_type="Flachdach",
        roof_pitch=0,
        roof_width=10.0,
        roof_length=10.0,
        orientation="portrait"
    )
    
    assert result["success"] == False, "Verschiebung sollte fehlschlagen"
    assert "Ungültige Richtung" in result["message"], "Fehlermeldung erwartet"
    print("✓ Test 10 passed: Ungültige Richtung abgefangen")


def test_handle_keyboard_rotate():
    """Test 11: Rotation um 90° (portrait ↔ landscape)."""
    setup_session_state()
    
    result = handle_keyboard_rotate(module_index=0)
    
    assert result["success"] == True, "Rotation sollte erfolgreich sein"
    assert result["old_orientation"] == "portrait", "Alte Orientierung korrekt"
    assert result["new_orientation"] == "landscape", "Neue Orientierung korrekt"
    assert st.session_state["module_orientations"][0] == "landscape", "Orientierung gespeichert"
    
    # Zweite Rotation zurück zu portrait
    result2 = handle_keyboard_rotate(module_index=0)
    assert result2["new_orientation"] == "portrait", "Zurück zu portrait"
    print("✓ Test 11 passed: Rotation funktioniert")


def test_handle_keyboard_rotate_invalid_index():
    """Test 12: Rotation mit ungültigem Index."""
    setup_session_state()
    
    result = handle_keyboard_rotate(module_index=99)
    
    assert result["success"] == False, "Rotation sollte fehlschlagen"
    assert "Ungültiger Modul-Index" in result["message"], "Fehlermeldung erwartet"
    print("✓ Test 12 passed: Ungültiger Index bei Rotation abgefangen")


def test_handle_keyboard_delete():
    """Test 13: Löschen von Modulen."""
    setup_session_state()
    
    initial_count = len(st.session_state["placed_module_positions"])
    
    result = handle_keyboard_delete(module_indices=[0, 2])
    
    assert result["success"] == True, "Löschen sollte erfolgreich sein"
    assert result["deleted_count"] == 2, "2 Module sollten gelöscht sein"
    assert result["remaining_count"] == 1, "1 Modul sollte verbleiben"
    assert len(st.session_state["placed_module_positions"]) == 1, "Nur 1 Modul verbleibend"
    # Modul 1 sollte verbleiben (Index 0 und 2 gelöscht)
    assert st.session_state["placed_module_positions"][0] == (2.0, 0.0, 0.3), "Modul 1 verbleibt"
    print("✓ Test 13 passed: Löschen von Modulen")


def test_handle_keyboard_delete_invalid_indices():
    """Test 14: Löschen mit ungültigen Indizes."""
    setup_session_state()
    
    result = handle_keyboard_delete(module_indices=[99, 100])
    
    # Debug output
    if result["success"]:
        print(f"DEBUG: Expected failure but got success!")
        print(f"  Message: {result['message']}")
        print(f"  Deleted count: {result['deleted_count']}")
    else:
        print(f"DEBUG: Got expected failure with message: {result['message']}")
    
    assert result["success"] == False, "Löschen sollte fehlschlagen"
    assert "Ungültige" in result["message"] or "ungültige" in result["message"].lower(), f"Fehlermeldung erwartet, aber bekam: {result['message']}"
    print("✓ Test 14 passed: Ungültige Indizes beim Löschen abgefangen")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Führt alle Tests aus und gibt Zusammenfassung aus."""
    print("\n" + "="*70)
    print("TASK 7.4 & 7.5 STANDALONE TESTS")
    print("="*70 + "\n")
    
    tests = [
        # Task 7.4: Move Preview
        ("Task 7.4.1", test_create_move_preview_success),
        ("Task 7.4.2", test_create_move_preview_with_module_collision),
        ("Task 7.4.3", test_create_move_preview_with_boundary_collision),
        ("Task 7.4.4", test_create_move_preview_invalid_index),
        
        # Task 7.5: Keyboard Shortcuts
        ("Task 7.5.1", test_handle_keyboard_move_right),
        ("Task 7.5.2", test_handle_keyboard_move_left),
        ("Task 7.5.3", test_handle_keyboard_move_up),
        ("Task 7.5.4", test_handle_keyboard_move_down),
        ("Task 7.5.5", test_handle_keyboard_move_with_collision),
        ("Task 7.5.6", test_handle_keyboard_move_invalid_direction),
        ("Task 7.5.7", test_handle_keyboard_rotate),
        ("Task 7.5.8", test_handle_keyboard_rotate_invalid_index),
        ("Task 7.5.9", test_handle_keyboard_delete),
        ("Task 7.5.10", test_handle_keyboard_delete_invalid_indices),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST SUMMARY: {passed}/{len(tests)} passed, {failed}/{len(tests)} failed")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Tasks 7.4 & 7.5 sind vollständig implementiert.")
        return True
    else:
        print(f"❌ {failed} TESTS FAILED. Bitte Fehler beheben.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
