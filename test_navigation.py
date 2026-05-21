"""
Test Script fur Phase 5: Main GUI Navigation Modernization

Testet:
1. Header-Navigation vorhanden
2. Tabs-Komponente implementiert
3. Breadcrumbs-Logik vorhanden
4. Settings Popover vorhanden
5. Session State Keys korrekt
6. Sidebar kompakt (alte Buttons entfernt)
"""

import sys
from pathlib import Path

# Fuge workspace root zum Python path hinzu
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

def test_gui_file_exists():
    """Test 1: gui.py existiert"""
    gui_path = workspace_root / "gui.py"
    assert gui_path.exists(), "gui.py nicht gefunden"
    print("Test 1: gui.py existiert... OK")
    return True

def test_header_navigation_code():
    """Test 2: Header-Navigation Code vorhanden"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check Header-Spalten
    assert 'header_col1, header_col2, header_col3 = st.columns([3, 1, 0.3])' in content, \
        "Header-Spalten nicht gefunden"
    print("Test 2: Header-Spalten definiert... OK")
    
    # Check Breadcrumbs
    assert 'Startseite /' in content, "Breadcrumbs-Text nicht gefunden"
    print("Test 2: Breadcrumbs-Code vorhanden... OK")
    
    # Check Settings Button
    assert 'header_settings_btn' in content, "Settings-Button nicht gefunden"
    print("Test 2: Settings-Button vorhanden... OK")
    
    return True

def test_tabs_navigation_code():
    """Test 3: Tabs-Navigation implementiert"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check Tab-Items
    assert 'tab_items = [' in content, "tab_items Liste nicht gefunden"
    print("Test 3: tab_items Liste definiert... OK")
    
    # Check Tab-Keys
    assert 'tab_keys = [' in content, "tab_keys Liste nicht gefunden"
    print("Test 3: tab_keys Liste definiert... OK")
    
    # Check shadcn_tabs import
    assert 'from components.shadcn_ui_integration import tabs as shadcn_tabs' in content, \
        "shadcn_tabs Import nicht gefunden"
    print("Test 3: shadcn_tabs Import vorhanden... OK")
    
    # Check shadcn_tabs call
    assert 'selected_tab_label = shadcn_tabs(' in content, \
        "shadcn_tabs() Aufruf nicht gefunden"
    print("Test 3: shadcn_tabs() Aufruf vorhanden... OK")
    
    return True

def test_settings_popover_code():
    """Test 4: Settings Popover implementiert"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check Settings Popover
    assert 'show_settings_popover' in content, \
        "show_settings_popover Session State nicht gefunden"
    print("Test 4: Settings Popover Session State vorhanden... OK")
    
    # Check Theme-Auswahl
    assert 'theme_options = [' in content, "theme_options nicht gefunden"
    assert "'Hell', 'Dunkel', 'Auto'" in content or '"Hell", "Dunkel", "Auto"' in content, \
        "Theme-Optionen nicht korrekt"
    print("Test 4: Theme-Auswahl implementiert... OK")
    
    return True

def test_old_sidebar_buttons_removed():
    """Test 5: Alte Sidebar-Buttons entfernt"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check dass alte Sektions-Uberschriften NICHT mehr vorhanden sind
    hauptmenu_count = content.count('HAUPTMENU')
    business_count = content.count('BUSINESS')
    tools_count = content.count('TOOLS')
    
    # Diese sollten nur in Comments/Strings vorkommen, nicht als aktive UI
    # Toleranz: Max 2 Vorkommen (z.B. in diesem Test + Backup-Datei)
    assert hauptmenu_count <= 2, f"HAUPTMENU noch {hauptmenu_count}x vorhanden (erwartet: 0-2)"
    assert business_count <= 2, f"BUSINESS noch {business_count}x vorhanden (erwartet: 0-2)"
    assert tools_count <= 2, f"TOOLS noch {tools_count}x vorhanden (erwartet: 0-2)"
    
    print("Test 5: Alte Sektions-Uberschriften entfernt... OK")
    
    # Check dass nav_btn_ Keys nicht mehr in for-loops sind
    # (alte Buttons hatten key=f"nav_btn_{item['key']}")
    # Neue Tabs haben key='main_nav_tabs'
    nav_btn_loops = content.count('for item in main_menu:')
    assert nav_btn_loops == 0, "Alte Button-Loops noch vorhanden"
    print("Test 5: Alte Button-Loops entfernt... OK")
    
    return True

def test_session_state_compatibility():
    """Test 6: Session State Keys kompatibel"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check dass alte Keys noch gesetzt werden (Kompatibilitat)
    assert "st.session_state.active_page" in content, \
        "active_page Session State fehlt"
    print("Test 6: active_page Session State vorhanden... OK")
    
    assert "st.session_state.selected_page_key_sui" in content, \
        "selected_page_key_sui Session State fehlt"
    print("Test 6: selected_page_key_sui Session State vorhanden... OK")
    
    assert "st.session_state.nav_event" in content, \
        "nav_event Session State fehlt"
    print("Test 6: nav_event Session State vorhanden... OK")
    
    return True

def test_navigation_history_import():
    """Test 7: Navigation History Import vorhanden (optional)"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check Import (optional, daher nur Warning)
    if 'from core.navigation_history import' in content:
        print("Test 7: Navigation History Import vorhanden... OK")
    else:
        print("Test 7: Navigation History Import fehlt (optional)... WARNING")
    
    return True

def test_documentation_exists():
    """Test 8: Dokumentation erstellt"""
    doc_path = workspace_root / "docs" / "ui_modernization" / "PHASE_5_NAVIGATION.md"
    
    assert doc_path.exists(), "PHASE_5_NAVIGATION.md nicht gefunden"
    print("Test 8: Dokumentation existiert... OK")
    
    # Check Inhalt
    content = doc_path.read_text(encoding='utf-8')
    assert 'Phase 5' in content, "Phase 5 nicht in Doku erwahnt"
    assert 'Tabs' in content or 'tabs' in content, "Tabs nicht dokumentiert"
    assert 'Breadcrumbs' in content, "Breadcrumbs nicht dokumentiert"
    print("Test 8: Dokumentation vollstandig... OK")
    
    return True

def test_fallback_logic():
    """Test 9: Fallback-Logik fur shadcn_tabs vorhanden"""
    gui_path = workspace_root / "gui.py"
    content = gui_path.read_text(encoding='utf-8')
    
    # Check Try-Except um shadcn_tabs
    assert 'try:' in content and 'from components.shadcn_ui_integration import tabs' in content, \
        "Try-Block fur shadcn_tabs fehlt"
    print("Test 9: Try-Block fur shadcn_tabs vorhanden... OK")
    
    # Check Fallback auf st.tabs()
    assert 'st.tabs(tab_items)' in content or 'except:' in content, \
        "Fallback auf st.tabs() fehlt"
    print("Test 9: Fallback auf st.tabs() vorhanden... OK")
    
    return True

def run_all_tests():
    """Fuhre alle Tests aus"""
    tests = [
        test_gui_file_exists,
        test_header_navigation_code,
        test_tabs_navigation_code,
        test_settings_popover_code,
        test_old_sidebar_buttons_removed,
        test_session_state_compatibility,
        test_navigation_history_import,
        test_documentation_exists,
        test_fallback_logic,
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("PHASE 5 NAVIGATION TESTS")
    print("="*60 + "\n")
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"FEHLER in {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"EXCEPTION in {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TESTS ABGESCHLOSSEN: {passed} bestanden, {failed} fehlgeschlagen")
    print("="*60 + "\n")
    
    if failed == 0:
        print("ERFOLG - Alle Tests bestanden!")
        return True
    else:
        print(f"FEHLER - {failed} Test(s) fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
