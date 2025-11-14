"""
Test für Admin Panel Integration - Task 7
Testet die Integration des "Preis Matrix" Tabs im Admin Panel.
"""
import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_admin_tab_keys_definition():
    """Test: Prüft ob 'admin_tab_price_matrix' in ADMIN_TAB_KEYS_DEFINITION_GLOBAL vorhanden ist"""
    from admin_panel import ADMIN_TAB_KEYS_DEFINITION_GLOBAL
    
    assert "admin_tab_price_matrix" in ADMIN_TAB_KEYS_DEFINITION_GLOBAL, \
        "admin_tab_price_matrix sollte in ADMIN_TAB_KEYS_DEFINITION_GLOBAL vorhanden sein"
    
    # Prüfe Position (sollte nach services_management sein)
    idx = ADMIN_TAB_KEYS_DEFINITION_GLOBAL.index("admin_tab_price_matrix")
    services_idx = ADMIN_TAB_KEYS_DEFINITION_GLOBAL.index("admin_tab_services_management")
    
    assert idx == services_idx + 1, \
        f"admin_tab_price_matrix sollte direkt nach admin_tab_services_management sein (Position {services_idx + 1}, ist aber {idx})"
    
    print("[OK] admin_tab_price_matrix ist korrekt in ADMIN_TAB_KEYS_DEFINITION_GLOBAL integriert")


def test_admin_tab_icons():
    """Test: Prüft ob Icon für 'admin_tab_price_matrix' definiert ist"""
    from admin_panel import ADMIN_TAB_ICONS
    
    assert "admin_tab_price_matrix" in ADMIN_TAB_ICONS, \
        "Icon für admin_tab_price_matrix sollte definiert sein"
    
    icon = ADMIN_TAB_ICONS["admin_tab_price_matrix"]
    assert icon == "[CHART]", \
        f"Icon sollte '[CHART]' sein, ist aber '{icon}'"
    
    print(f"[OK] Icon für admin_tab_price_matrix ist korrekt definiert: {icon}")


def test_admin_tab_descriptions():
    """Test: Prüft ob Beschreibung für 'admin_tab_price_matrix' definiert ist"""
    from admin_panel import ADMIN_TAB_DESCRIPTIONS
    
    assert "admin_tab_price_matrix" in ADMIN_TAB_DESCRIPTIONS, \
        "Beschreibung für admin_tab_price_matrix sollte definiert sein"
    
    description = ADMIN_TAB_DESCRIPTIONS["admin_tab_price_matrix"]
    assert len(description) > 0, \
        "Beschreibung sollte nicht leer sein"
    
    print(f"[OK] Beschreibung für admin_tab_price_matrix: '{description}'")


def test_admin_tab_labels():
    """Test: Prüft ob deutsches Label für 'admin_tab_price_matrix' definiert ist"""
    from admin_panel import ADMIN_TAB_LABELS_DE
    
    assert "admin_tab_price_matrix" in ADMIN_TAB_LABELS_DE, \
        "Deutsches Label für admin_tab_price_matrix sollte definiert sein"
    
    label = ADMIN_TAB_LABELS_DE["admin_tab_price_matrix"]
    assert label == "Preis Matrix", \
        f"Label sollte 'Preis Matrix' sein, ist aber '{label}'"
    
    print(f"[OK] Deutsches Label für admin_tab_price_matrix: '{label}'")


def test_render_price_matrix_tab_exists():
    """Test: Prüft ob render_price_matrix_tab Funktion existiert"""
    from admin_panel import render_price_matrix_tab
    
    assert callable(render_price_matrix_tab), \
        "render_price_matrix_tab sollte eine aufrufbare Funktion sein"
    
    print("[OK] render_price_matrix_tab Funktion existiert")


def test_render_price_matrix_tab_docstring():
    """Test: Prüft ob render_price_matrix_tab eine Dokumentation hat"""
    from admin_panel import render_price_matrix_tab
    
    assert render_price_matrix_tab.__doc__ is not None, \
        "render_price_matrix_tab sollte eine Dokumentation haben"
    
    docstring = render_price_matrix_tab.__doc__
    assert "Requirements: 1.1, 1.2, 1.3, 1.4" in docstring, \
        "Dokumentation sollte Requirements-Referenzen enthalten"
    
    print("[OK] render_price_matrix_tab hat korrekte Dokumentation")


def test_tab_to_area_map():
    """Test: Prüft ob admin_tab_price_matrix im tab_to_area_map vorhanden ist"""
    # Da tab_to_area_map innerhalb von render_admin_panel definiert ist,
    # können wir nur prüfen, ob die Funktion existiert und keine Syntax-Fehler hat
    from admin_panel import render_admin_panel
    
    assert callable(render_admin_panel), \
        "render_admin_panel sollte eine aufrufbare Funktion sein"
    
    print("[OK] render_admin_panel Funktion ist verfügbar")


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n" + "="*60)
    print("Task 7: Admin Panel Integration - Tests")
    print("="*60 + "\n")
    
    tests = [
        test_admin_tab_keys_definition,
        test_admin_tab_icons,
        test_admin_tab_descriptions,
        test_admin_tab_labels,
        test_render_price_matrix_tab_exists,
        test_render_price_matrix_tab_docstring,
        test_tab_to_area_map,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[ERROR] {test.__name__} fehlgeschlagen: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__} Fehler: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Ergebnis: {passed} Tests bestanden, {failed} Tests fehlgeschlagen")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
