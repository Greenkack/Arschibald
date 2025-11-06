"""
Test für pv3d_ui_components Modul

Dieser Test prüft, ob alle UI-Komponenten-Funktionen korrekt importiert werden können.
"""

def test_imports():
    """Teste ob alle Funktionen importiert werden können"""
    try:
        from utils.pv3d_ui_components import (
            render_basis_settings,
            render_module_placement,
            render_advanced_controls,
            render_analysis_panel,
            render_export_options
        )
        
        print("✓ Alle UI-Komponenten-Funktionen erfolgreich importiert")
        print(f"  - render_basis_settings: {render_basis_settings.__name__}")
        print(f"  - render_module_placement: {render_module_placement.__name__}")
        print(f"  - render_advanced_controls: {render_advanced_controls.__name__}")
        print(f"  - render_analysis_panel: {render_analysis_panel.__name__}")
        print(f"  - render_export_options: {render_export_options.__name__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def test_function_signatures():
    """Teste ob Funktionen die erwarteten Signaturen haben"""
    try:
        from utils.pv3d_ui_components import (
            render_basis_settings,
            render_module_placement,
            render_advanced_controls,
            render_analysis_panel,
            render_export_options
        )
        import inspect
        
        # Prüfe render_basis_settings
        sig = inspect.signature(render_basis_settings)
        assert 'project_data' in sig.parameters, "render_basis_settings fehlt project_data Parameter"
        
        # Prüfe render_module_placement
        sig = inspect.signature(render_module_placement)
        assert 'project_data' in sig.parameters, "render_module_placement fehlt project_data Parameter"
        assert 'selected_roof_type' in sig.parameters, "render_module_placement fehlt selected_roof_type Parameter"
        
        # Prüfe render_advanced_controls
        sig = inspect.signature(render_advanced_controls)
        assert 'building_length' in sig.parameters, "render_advanced_controls fehlt building_length Parameter"
        assert 'building_width' in sig.parameters, "render_advanced_controls fehlt building_width Parameter"
        
        # Prüfe render_analysis_panel (keine Parameter)
        sig = inspect.signature(render_analysis_panel)
        assert len(sig.parameters) == 0, "render_analysis_panel sollte keine Parameter haben"
        
        # Prüfe render_export_options (keine Parameter)
        sig = inspect.signature(render_export_options)
        assert len(sig.parameters) == 0, "render_export_options sollte keine Parameter haben"
        
        print("✓ Alle Funktions-Signaturen sind korrekt")
        return True
        
    except AssertionError as e:
        print(f"❌ Signatur-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Test: pv3d_ui_components Modul")
    print("=" * 60)
    print()
    
    # Test 1: Imports
    print("Test 1: Import-Test")
    print("-" * 60)
    test1_passed = test_imports()
    print()
    
    # Test 2: Funktions-Signaturen
    print("Test 2: Funktions-Signaturen")
    print("-" * 60)
    test2_passed = test_function_signatures()
    print()
    
    # Zusammenfassung
    print("=" * 60)
    print("Zusammenfassung:")
    print(f"  Test 1 (Imports): {'✓ BESTANDEN' if test1_passed else '❌ FEHLGESCHLAGEN'}")
    print(f"  Test 2 (Signaturen): {'✓ BESTANDEN' if test2_passed else '❌ FEHLGESCHLAGEN'}")
    print()
    
    if test1_passed and test2_passed:
        print("✓ ALLE TESTS BESTANDEN")
        exit(0)
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN")
        exit(1)
