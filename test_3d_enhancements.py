"""
Test für 3D-Visualisierung Verbesserungen

Testet ob alle neuen Module korrekt importiert werden können.
"""

import sys

def test_export_buttons():
    """Test Export-Buttons Modul"""
    try:
        from utils.pv3d_export_buttons import render_export_action_buttons
        print("✅ Export-Buttons Modul erfolgreich importiert")
        return True
    except ImportError as e:
        print(f"❌ Export-Buttons Modul fehlt: {e}")
        return False


def test_mounting_logic():
    """Test Aufständerungs-Logik Modul"""
    try:
        from utils.pv3d_mounting_logic import (
            is_flat_roof,
            is_pitched_roof,
            get_allowed_mounting_types,
            validate_mounting_selection
        )
        
        # Test Flachdach-Erkennung
        assert is_flat_roof("Flachdach") == True
        assert is_flat_roof("Satteldach") == False
        
        # Test Schrägdach-Erkennung
        assert is_pitched_roof("Satteldach") == True
        assert is_pitched_roof("Flachdach") == False
        
        # Test erlaubte Montagetypen
        flat_types = get_allowed_mounting_types("Flachdach")
        assert "Aufständerung" in str(flat_types)
        
        pitched_types = get_allowed_mounting_types("Satteldach")
        assert "Aufdach" in str(pitched_types)
        
        # Test Validierung
        result = validate_mounting_selection("Satteldach", "Aufständerung Süd")
        assert result["valid"] == False
        
        result = validate_mounting_selection("Flachdach", "Aufständerung Süd")
        assert result["valid"] == True
        
        print("✅ Aufständerungs-Logik Modul erfolgreich getestet")
        return True
    except ImportError as e:
        print(f"❌ Aufständerungs-Logik Modul fehlt: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Aufständerungs-Logik Test fehlgeschlagen: {e}")
        return False


def test_wow_features():
    """Test WOW-Features Modul"""
    try:
        from utils.pv3d_wow_features import (
            render_sun_path_animation,
            render_yield_heatmap_overlay,
            render_module_inspector,
            render_realtime_performance_sim,
            render_ar_preview_mode,
            render_comparison_mode,
            render_timelapse_simulation,
            render_ai_optimization_assistant,
            render_weather_integration,
            render_presentation_mode
        )
        print("✅ WOW-Features Modul erfolgreich importiert (10 Funktionen)")
        return True
    except ImportError as e:
        print(f"❌ WOW-Features Modul fehlt: {e}")
        return False


def test_integration():
    """Test Integration in Hauptdatei"""
    try:
        # Prüfe ob solar_3d_view_module.py die neuen Imports hat
        with open("solar_3d_view_module.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("pv3d_export_buttons", "Export-Buttons Import"),
            ("pv3d_mounting_logic", "Mounting-Logik Import"),
            ("pv3d_wow_features", "WOW-Features Import"),
            ("render_export_action_buttons", "Export-Buttons Aufruf"),
            ("validate_mounting_selection", "Mounting-Validierung Aufruf"),
            ("Erweiterte Features", "WOW-Features UI")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} gefunden")
            else:
                print(f"❌ {description} NICHT gefunden")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Integration-Test fehlgeschlagen: {e}")
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("3D-Visualisierung Verbesserungen - Tests")
    print("="*60 + "\n")
    
    results = []
    
    print("Test 1: Export-Buttons Modul")
    print("-" * 60)
    results.append(test_export_buttons())
    print()
    
    print("Test 2: Aufständerungs-Logik Modul")
    print("-" * 60)
    results.append(test_mounting_logic())
    print()
    
    print("Test 3: WOW-Features Modul")
    print("-" * 60)
    results.append(test_wow_features())
    print()
    
    print("Test 4: Integration in Hauptdatei")
    print("-" * 60)
    results.append(test_integration())
    print()
    
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 Alle Tests bestanden! Die Integration ist vollständig.")
        return 0
    else:
        print("⚠️ Einige Tests fehlgeschlagen. Bitte prüfen Sie die Fehler oben.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
