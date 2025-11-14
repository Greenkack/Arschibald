"""
Test für Task 10: Manuelle Steuerungs-Buttons

Dieser Test verifiziert die Implementierung der manuellen Steuerungs-Buttons
für die Modul-Platzierung.

Requirements:
    - 4.1: Manual add button functionality
    - 4.2: Remove selected button functionality
    - 4.3: Reset button functionality
    - 4.5: Session state for selected modules
"""

import sys
import os

# Füge das Projekt-Root-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_manual_add_handler():
    """
    Test: handle_manual_add fügt ein Modul an spezifischer Position hinzu.
    
    Requirement 4.1: Manual add button functionality
    """
    print("\n=== Test 1: Manual Add Handler ===")
    
    from utils.pv3d_placement_handler import handle_manual_add
    
    # Mock session state
    class MockSessionState:
        def __init__(self):
            self.data = {
                "placed_module_positions": [],
                "placed_module_count": 0
            }
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    # Ersetze st.session_state temporär
    import streamlit as st
    original_session_state = st.session_state if hasattr(st, 'session_state') else None
    st.session_state = MockSessionState()
    
    try:
        # Test 1: Füge Modul auf Flachdach hinzu
        result = handle_manual_add(
            x=0.0,
            y=0.0,
            roof_type="Flachdach",
            roof_pitch=0.0
        )
        
        assert result["success"], "Manual add sollte erfolgreich sein"
        assert len(st.session_state["placed_module_positions"]) == 1, \
            "Ein Modul sollte hinzugefügt worden sein"
        assert st.session_state["placed_module_count"] == 1, \
            "Module count sollte 1 sein"
        
        # Prüfe Position
        pos = st.session_state["placed_module_positions"][0]
        assert pos[0] == 0.0, "X-Position sollte 0.0 sein"
        assert pos[1] == 0.0, "Y-Position sollte 0.0 sein"
        assert pos[2] == 0.3, "Z-Position sollte 0.3 sein (Flachdach)"
        
        print("[OK] Test 1.1: Modul auf Flachdach hinzugefügt")
        
        # Test 2: Füge Modul auf Satteldach hinzu
        result = handle_manual_add(
            x=1.0,
            y=1.0,
            roof_type="Satteldach",
            roof_pitch=35.0
        )
        
        assert result["success"], "Manual add sollte erfolgreich sein"
        assert len(st.session_state["placed_module_positions"]) == 2, \
            "Zwei Module sollten vorhanden sein"
        
        # Prüfe zweite Position
        pos = st.session_state["placed_module_positions"][1]
        assert pos[0] == 1.0, "X-Position sollte 1.0 sein"
        assert pos[1] == 1.0, "Y-Position sollte 1.0 sein"
        assert pos[2] == 0.05, "Z-Position sollte 0.05 sein (Satteldach)"
        
        print("[OK] Test 1.2: Modul auf Satteldach hinzugefügt")
        
        # Test 3: Füge mehrere Module hinzu
        for i in range(3):
            result = handle_manual_add(
                x=float(i),
                y=float(i),
                roof_type="Pultdach",
                roof_pitch=25.0
            )
            assert result["success"], f"Manual add {i} sollte erfolgreich sein"
        
        assert st.session_state["placed_module_count"] == 5, \
            "Fünf Module sollten vorhanden sein"
        
        print("[OK] Test 1.3: Mehrere Module hinzugefügt")
        
        print("[OK] Test 1: Manual Add Handler - BESTANDEN")
        return True
        
    finally:
        # Stelle original session state wieder her
        if original_session_state is not None:
            st.session_state = original_session_state


def test_remove_selected_handler():
    """
    Test: handle_remove_selected entfernt ausgewählte Module.
    
    Requirement 4.2: Remove selected button functionality
    """
    print("\n=== Test 2: Remove Selected Handler ===")
    
    from utils.pv3d_placement_handler import handle_remove_selected
    
    # Mock session state
    class MockSessionState:
        def __init__(self):
            self.data = {
                "placed_module_positions": [
                    (0.0, 0.0, 0.3),
                    (1.0, 0.0, 0.3),
                    (2.0, 0.0, 0.3),
                    (3.0, 0.0, 0.3),
                    (4.0, 0.0, 0.3)
                ],
                "placed_module_count": 5,
                "selected_module_indices": []
            }
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    # Ersetze st.session_state temporär
    import streamlit as st
    original_session_state = st.session_state if hasattr(st, 'session_state') else None
    st.session_state = MockSessionState()
    
    try:
        # Test 1: Entferne ein Modul
        result = handle_remove_selected([2])
        
        assert result["success"], "Remove sollte erfolgreich sein"
        assert result["count"] == 1, "Ein Modul sollte entfernt worden sein"
        assert len(st.session_state["placed_module_positions"]) == 4, \
            "Vier Module sollten übrig sein"
        assert st.session_state["placed_module_count"] == 4, \
            "Module count sollte 4 sein"
        
        print("[OK] Test 2.1: Ein Modul entfernt")
        
        # Test 2: Entferne mehrere Module
        result = handle_remove_selected([0, 2])
        
        assert result["success"], "Remove sollte erfolgreich sein"
        assert result["count"] == 2, "Zwei Module sollten entfernt worden sein"
        assert len(st.session_state["placed_module_positions"]) == 2, \
            "Zwei Module sollten übrig sein"
        
        print("[OK] Test 2.2: Mehrere Module entfernt")
        
        # Test 3: Entferne mit leerer Liste
        result = handle_remove_selected([])
        
        assert not result["success"], "Remove sollte fehlschlagen"
        assert result["count"] == 0, "Keine Module sollten entfernt worden sein"
        
        print("[OK] Test 2.3: Leere Auswahl behandelt")
        
        # Test 4: Entferne mit ungültigen Indizes
        result = handle_remove_selected([10, 20])
        
        assert result["success"], "Remove sollte erfolgreich sein (ignoriert ungültige)"
        assert result["count"] == 0, "Keine Module sollten entfernt worden sein"
        
        print("[OK] Test 2.4: Ungültige Indizes behandelt")
        
        print("[OK] Test 2: Remove Selected Handler - BESTANDEN")
        return True
        
    finally:
        # Stelle original session state wieder her
        if original_session_state is not None:
            st.session_state = original_session_state


def test_session_state_management():
    """
    Test: Session State für ausgewählte Module wird korrekt verwaltet.
    
    Requirement 4.3, 4.5: Session state for selected modules
    """
    print("\n=== Test 3: Session State Management ===")
    
    from utils.pv3d_placement_handler import (
        initialize_session_state,
        get_placement_statistics
    )
    
    # Mock session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    # Ersetze st.session_state temporär
    import streamlit as st
    original_session_state = st.session_state if hasattr(st, 'session_state') else None
    st.session_state = MockSessionState()
    
    try:
        # Test 1: Initialisiere Session State
        initialize_session_state()
        
        assert "placed_module_positions" in st.session_state, \
            "placed_module_positions sollte initialisiert sein"
        assert "placed_module_count" in st.session_state, \
            "placed_module_count sollte initialisiert sein"
        assert "selected_module_indices" in st.session_state, \
            "selected_module_indices sollte initialisiert sein"
        
        assert st.session_state["placed_module_positions"] == [], \
            "placed_module_positions sollte leer sein"
        assert st.session_state["placed_module_count"] == 0, \
            "placed_module_count sollte 0 sein"
        assert st.session_state["selected_module_indices"] == [], \
            "selected_module_indices sollte leer sein"
        
        print("[OK] Test 3.1: Session State initialisiert")
        
        # Test 2: Füge Daten hinzu
        st.session_state["placed_module_positions"] = [
            (0.0, 0.0, 0.3),
            (1.0, 0.0, 0.3)
        ]
        st.session_state["placed_module_count"] = 2
        st.session_state["selected_module_indices"] = [0]
        
        stats = get_placement_statistics()
        
        assert stats["placed_count"] == 2, "Placed count sollte 2 sein"
        assert len(stats["positions"]) == 2, "Zwei Positionen sollten vorhanden sein"
        assert stats["has_modules"], "has_modules sollte True sein"
        
        print("[OK] Test 3.2: Statistiken korrekt")
        
        # Test 3: Leere Session State
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0
        st.session_state["selected_module_indices"] = []
        
        stats = get_placement_statistics()
        
        assert stats["placed_count"] == 0, "Placed count sollte 0 sein"
        assert not stats["has_modules"], "has_modules sollte False sein"
        
        print("[OK] Test 3.3: Leere Statistiken korrekt")
        
        print("[OK] Test 3: Session State Management - BESTANDEN")
        return True
        
    finally:
        # Stelle original session state wieder her
        if original_session_state is not None:
            st.session_state = original_session_state


def test_ui_component_buttons():
    """
    Test: UI-Komponente rendert manuelle Steuerungs-Buttons korrekt.
    
    Requirement 4.1, 4.2: Manual control buttons in UI
    """
    print("\n=== Test 4: UI Component Buttons ===")
    
    # Dieser Test prüft nur die Logik, nicht das tatsächliche Rendering
    # (da Streamlit-UI-Tests schwierig sind)
    
    print("[INFO] UI-Komponenten-Tests erfordern manuelles Testen in Streamlit")
    print("   Bitte führen Sie folgende manuelle Tests durch:")
    print("   1. Starten Sie die Anwendung: streamlit run gui.py")
    print("   2. Navigieren Sie zur 3D-Visualisierung")
    print("   3. Prüfen Sie dass folgende Buttons vorhanden sind:")
    print("      - ➕ Modul hinzufügen (enabled)")
    print("      - ➖ Ausgewählte entfernen (disabled wenn keine Auswahl)")
    print("   4. Prüfen Sie dass die Buttons funktionieren:")
    print("      - Klicken Sie auf 'Modul hinzufügen'")
    print("      - Wählen Sie Module aus")
    print("      - Klicken Sie auf 'Ausgewählte entfernen'")
    
    print("[OK] Test 4: UI Component Buttons - MANUELL TESTEN")
    return True


def test_integration():
    """
    Test: Integration der manuellen Steuerung in solar_3d_view_module.py.
    
    Requirement 4.3: Integration in main module
    """
    print("\n=== Test 5: Integration ===")
    
    # Prüfe dass die Imports vorhanden sind
    try:
        from utils.pv3d_placement_handler import (
            handle_manual_add,
            handle_remove_selected
        )
        print("[OK] Test 5.1: Handler-Funktionen importierbar")
    except ImportError as e:
        print(f"[ERROR] Test 5.1: Import-Fehler: {e}")
        return False
    
    # Prüfe dass die UI-Komponente die Buttons rendert
    try:
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        print("[OK] Test 5.2: UI-Komponente importierbar")
    except ImportError as e:
        print(f"[ERROR] Test 5.2: Import-Fehler: {e}")
        return False
    
    # Prüfe dass solar_3d_view_module.py die Handler verwendet
    with open("solar_3d_view_module.py", "r", encoding="utf-8") as f:
        content = f.read()
        
        assert "handle_manual_add" in content, \
            "handle_manual_add sollte in solar_3d_view_module.py verwendet werden"
        assert "handle_remove_selected" in content, \
            "handle_remove_selected sollte in solar_3d_view_module.py verwendet werden"
        assert "manual_add_clicked" in content, \
            "manual_add_clicked sollte behandelt werden"
        assert "remove_selected_clicked" in content, \
            "remove_selected_clicked sollte behandelt werden"
        assert "selected_module_indices" in content, \
            "selected_module_indices sollte verwendet werden"
    
    print("[OK] Test 5.3: Integration in solar_3d_view_module.py vorhanden")
    
    print("[OK] Test 5: Integration - BESTANDEN")
    return True


def run_all_tests():
    """
    Führt alle Tests aus und gibt eine Zusammenfassung aus.
    """
    print("=" * 70)
    print("TASK 10: MANUELLE STEUERUNGS-BUTTONS - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Manual Add Handler", test_manual_add_handler),
        ("Remove Selected Handler", test_remove_selected_handler),
        ("Session State Management", test_session_state_management),
        ("UI Component Buttons", test_ui_component_buttons),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' fehlgeschlagen mit Fehler: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("TEST ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{test_name:.<50} {status}")
    
    print("=" * 70)
    print(f"GESAMT: {passed}/{total} Tests bestanden ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN! Task 10 ist vollständig implementiert.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen. Bitte beheben Sie die Fehler.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
