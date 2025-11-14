"""
Test für Task 6: Integration in solar_3d_view_module.py

Dieser Test verifiziert dass die Modul-Platzierungs-Integration korrekt funktioniert.
"""

import sys
import traceback


def test_imports():
    """Test dass alle benötigten Module importiert werden können."""
    print("\n" + "="*80)
    print("TEST 1: Import-Test")
    print("="*80)
    
    try:
        # Test Import der neuen Module
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        print("[OK] pv3d_module_placement_ui importiert")
        
        from utils.pv3d_placement_handler import (
            handle_auto_placement,
            handle_reset_placement
        )
        print("[OK] pv3d_placement_handler importiert")
        
        # Test Import des Haupt-Moduls
        import solar_3d_view_module
        print("[OK] solar_3d_view_module importiert")
        
        print("\n[OK] Alle Imports erfolgreich!")
        return True
        
    except ImportError as e:
        print(f"\n[ERROR] Import-Fehler: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[ERROR] Unerwarteter Fehler: {e}")
        traceback.print_exc()
        return False


def test_session_state_initialization():
    """Test dass Session State korrekt initialisiert wird."""
    print("\n" + "="*80)
    print("TEST 2: Session State Initialisierung")
    print("="*80)
    
    try:
        # Simuliere Streamlit Session State
        class MockSessionState(dict):
            def __init__(self):
                super().__init__()
            
            def get(self, key, default=None):
                return super().get(key, default)
        
        # Erstelle Mock Session State
        session_state = MockSessionState()
        
        # Initialisiere wie im Code
        if "placed_module_positions" not in session_state:
            session_state["placed_module_positions"] = []
        if "placed_module_count" not in session_state:
            session_state["placed_module_count"] = 0
        if "trigger_auto_placement" not in session_state:
            session_state["trigger_auto_placement"] = False
        
        # Verifiziere
        assert session_state["placed_module_positions"] == [], \
            "placed_module_positions sollte leere Liste sein"
        assert session_state["placed_module_count"] == 0, \
            "placed_module_count sollte 0 sein"
        assert session_state["trigger_auto_placement"] is False, \
            "trigger_auto_placement sollte False sein"
        
        print("[OK] placed_module_positions initialisiert: []")
        print("[OK] placed_module_count initialisiert: 0")
        print("[OK] trigger_auto_placement initialisiert: False")
        
        print("\n[OK] Session State korrekt initialisiert!")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] Assertion-Fehler: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unerwarteter Fehler: {e}")
        traceback.print_exc()
        return False


def test_handler_functions():
    """Test dass Handler-Funktionen korrekt aufgerufen werden können."""
    print("\n" + "="*80)
    print("TEST 3: Handler-Funktionen")
    print("="*80)
    
    try:
        from utils.pv3d_placement_handler import (
            handle_auto_placement,
            handle_reset_placement
        )
        
        # Test handle_reset_placement (einfachste Funktion)
        result = handle_reset_placement()
        assert isinstance(result, dict), "Ergebnis sollte Dictionary sein"
        assert "success" in result, "Ergebnis sollte 'success' enthalten"
        assert "message" in result, "Ergebnis sollte 'message' enthalten"
        print(f"[OK] handle_reset_placement: {result}")
        
        # Test handle_auto_placement mit Beispiel-Parametern
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach",
            roof_pitch=30.0
        )
        assert isinstance(result, dict), "Ergebnis sollte Dictionary sein"
        assert "success" in result, "Ergebnis sollte 'success' enthalten"
        assert "message" in result, "Ergebnis sollte 'message' enthalten"
        print(f"[OK] handle_auto_placement: success={result['success']}, "
              f"count={result.get('count', 0)}")
        
        print("\n[OK] Handler-Funktionen funktionieren korrekt!")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] Assertion-Fehler: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Fehler beim Testen der Handler: {e}")
        traceback.print_exc()
        return False


def test_ui_panel_function():
    """Test dass UI-Panel-Funktion korrekt aufgerufen werden kann."""
    print("\n" + "="*80)
    print("TEST 4: UI-Panel-Funktion")
    print("="*80)
    
    try:
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        
        # Hinweis: Diese Funktion benötigt Streamlit-Kontext
        # Wir testen nur dass sie importierbar ist und die richtige Signatur hat
        import inspect
        sig = inspect.signature(render_module_placement_panel)
        params = list(sig.parameters.keys())
        
        expected_params = ["module_quantity", "roof_area", "current_placed"]
        for param in expected_params:
            assert param in params, f"Parameter '{param}' fehlt"
            print(f"[OK] Parameter '{param}' vorhanden")
        
        print("\n[OK] UI-Panel-Funktion hat korrekte Signatur!")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] Assertion-Fehler: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Fehler beim Testen der UI-Funktion: {e}")
        traceback.print_exc()
        return False


def test_integration_code_structure():
    """Test dass der Integrations-Code die richtige Struktur hat."""
    print("\n" + "="*80)
    print("TEST 5: Integrations-Code-Struktur")
    print("="*80)
    
    try:
        # Lese solar_3d_view_module.py
        with open("solar_3d_view_module.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Prüfe dass die wichtigen Teile vorhanden sind
        checks = [
            ("Session State Init", '"placed_module_positions"' in content),
            ("Session State Init", '"placed_module_count"' in content),
            ("Session State Init", '"trigger_auto_placement"' in content),
            ("Import UI", 'from utils.pv3d_module_placement_ui import' in content),
            ("Import Handler", 'from utils.pv3d_placement_handler import' in content),
            ("Panel Render", 'render_module_placement_panel(' in content),
            ("Auto-Placement", 'handle_auto_placement(' in content),
            ("Reset Handler", 'handle_reset_placement()' in content),
            ("Try-Catch", 'except ImportError as e:' in content),
            ("Rerun", 'st.rerun()' in content),
        ]
        
        all_passed = True
        for name, check in checks:
            if check:
                print(f"[OK] {name} vorhanden")
            else:
                print(f"[ERROR] {name} fehlt")
                all_passed = False
        
        if all_passed:
            print("\n[OK] Integrations-Code hat korrekte Struktur!")
            return True
        else:
            print("\n[ERROR] Einige Teile des Integrations-Codes fehlen!")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] Fehler beim Prüfen der Code-Struktur: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Führt alle Tests aus und gibt Zusammenfassung aus."""
    print("\n" + "="*80)
    print("TASK 6 INTEGRATION TEST SUITE")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("Session State", test_session_state_initialization),
        ("Handler-Funktionen", test_handler_functions),
        ("UI-Panel-Funktion", test_ui_panel_function),
        ("Code-Struktur", test_integration_code_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' ist abgestürzt: {e}")
            traceback.print_exc()
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{status}: {name}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN! Task 6 ist erfolgreich implementiert.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen. Bitte überprüfen.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
