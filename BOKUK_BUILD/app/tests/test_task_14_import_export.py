"""
Test für Task 14: Import/Export für Design-Konfigurationen

Testet:
- Export-Funktion (Task 14.1)
- Import-Funktion (Task 14.2)
- Validierung
- Datenintegrität
"""

import json
import sys
from datetime import datetime


def test_collect_all_design_settings():
    """Test Task 14.1: Sammle alle Design-Einstellungen"""
    print("\n" + "=" * 70)
    print("TEST 1: Sammle alle Design-Einstellungen für Export")
    print("=" * 70)

    try:
        # Mock load_setting function
        def mock_load_setting(key, default=None):
            mock_data = {
                'pdf_design_settings': {
                    'primary_color': '#1E3A8A',
                    'secondary_color': '#3B82F6',
                    'font_family': 'Helvetica',
                    'font_size_h1': 18,
                    'font_size_h2': 14,
                    'font_size_body': 10,
                    'font_size_small': 8,
                    'logo_position': 'left',
                    'footer_format': 'with_page_number',
                    'custom_footer_text': '',
                    'watermark_enabled': False,
                    'watermark_text': 'ENTWURF',
                    'watermark_opacity': 0.1
                },
                'visualization_settings': {
                    'global_chart_colors': [
                        '#1E3A8A', '#3B82F6', '#10B981',
                        '#F59E0B', '#EF4444', '#8B5CF6'
                    ],
                    'individual_chart_colors': {}
                },
                'ui_theme_settings': {
                    'active_theme': 'light',
                    'custom_themes': {}
                },
                'pdf_templates': {
                    'active_template': 'standard',
                    'templates': []
                },
                'pdf_layout_options': {
                    'layouts': {
                        'standard': {'enabled': True, 'is_default': True},
                        'extended': {'enabled': True, 'is_default': False}
                    }
                }
            }
            return mock_data.get(key, default)

        # Import function from admin_pdf_settings_ui
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import _collect_all_design_settings

        # Collect settings
        config_data = _collect_all_design_settings(mock_load_setting)

        # Verify data
        assert isinstance(
            config_data, dict), "Config data should be a dictionary"
        assert 'pdf_design_settings' in config_data, "Should contain pdf_design_settings"
        assert 'visualization_settings' in config_data, "Should contain visualization_settings"
        assert 'ui_theme_settings' in config_data, "Should contain ui_theme_settings"
        assert 'pdf_templates' in config_data, "Should contain pdf_templates"
        assert 'pdf_layout_options' in config_data, "Should contain pdf_layout_options"

        print("✅ Alle Design-Einstellungen erfolgreich gesammelt")
        print(f"   - Anzahl Einstellungsbereiche: {len(config_data)}")
        print(f"   - Keys: {', '.join(config_data.keys())}")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Sammeln der Einstellungen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_with_metadata():
    """Test Task 14.1: Export mit Metadaten"""
    print("\n" + "=" * 70)
    print("TEST 2: Export mit Metadaten")
    print("=" * 70)

    try:
        # Mock load_setting function
        def mock_load_setting(key, default=None):
            mock_data = {
                'pdf_design_settings': {
                    'primary_color': '#1E3A8A',
                    'secondary_color': '#3B82F6'
                }
            }
            return mock_data.get(key, default)

        # Import function
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import _collect_all_design_settings

        # Collect settings
        config_data = _collect_all_design_settings(mock_load_setting)

        # Add metadata (simulating what the UI does)
        config_data['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'version': '1.0',
            'description': 'PDF & Design Konfiguration Export'
        }

        # Convert to JSON
        json_str = json.dumps(config_data, indent=2, ensure_ascii=False)

        # Verify JSON is valid
        parsed = json.loads(json_str)
        assert '_metadata' in parsed, "Should contain metadata"
        assert 'export_date' in parsed['_metadata'], "Should contain export_date"
        assert 'version' in parsed['_metadata'], "Should contain version"

        print("✅ Export mit Metadaten erfolgreich")
        print(f"   - Export-Datum: {parsed['_metadata']['export_date']}")
        print(f"   - Version: {parsed['_metadata']['version']}")
        print(f"   - JSON-Größe: {len(json_str)} Bytes")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Export: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validate_imported_config():
    """Test Task 14.2: Validierung importierter Konfiguration"""
    print("\n" + "=" * 70)
    print("TEST 3: Validierung importierter Konfiguration")
    print("=" * 70)

    try:
        # Import function
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import _validate_imported_config

        # Test 1: Valid configuration
        valid_config = {
            'pdf_design_settings': {
                'primary_color': '#1E3A8A',
                'secondary_color': '#3B82F6'
            },
            'visualization_settings': {
                'global_chart_colors': ['#1E3A8A', '#3B82F6']
            }
        }

        is_valid, errors = _validate_imported_config(valid_config)
        assert is_valid, f"Valid config should pass validation. Errors: {errors}"
        assert len(errors) == 0, "Valid config should have no errors"

        print("✅ Test 1: Gültige Konfiguration erfolgreich validiert")

        # Test 2: Invalid configuration (not a dict)
        invalid_config_1 = "not a dict"
        is_valid, errors = _validate_imported_config(invalid_config_1)
        assert not is_valid, "Invalid config should fail validation"
        assert len(errors) > 0, "Invalid config should have errors"

        print("✅ Test 2: Ungültige Konfiguration (kein Dict) korrekt abgelehnt")

        # Test 3: Empty configuration
        empty_config = {}
        is_valid, errors = _validate_imported_config(empty_config)
        assert not is_valid, "Empty config should fail validation"
        assert len(errors) > 0, "Empty config should have errors"

        print("✅ Test 3: Leere Konfiguration korrekt abgelehnt")

        # Test 4: Invalid color format
        invalid_colors = {
            'visualization_settings': {
                'global_chart_colors': "not a list"
            }
        }
        is_valid, errors = _validate_imported_config(invalid_colors)
        assert not is_valid, "Invalid colors should fail validation"

        print("✅ Test 4: Ungültiges Farbformat korrekt abgelehnt")

        return True

    except Exception as e:
        print(f"❌ Fehler bei der Validierung: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_design_settings():
    """Test Task 14.2: Import von Design-Einstellungen"""
    print("\n" + "=" * 70)
    print("TEST 4: Import von Design-Einstellungen")
    print("=" * 70)

    try:
        # Mock save_setting function
        saved_settings = {}

        def mock_save_setting(key, value):
            saved_settings[key] = value
            return True

        # Import function
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import _import_design_settings

        # Test configuration
        test_config = {
            'pdf_design_settings': {
                'primary_color': '#FF0000',
                'secondary_color': '#00FF00'
            },
            'visualization_settings': {
                'global_chart_colors': ['#FF0000', '#00FF00', '#0000FF']
            },
            'ui_theme_settings': {
                'active_theme': 'dark'
            }
        }

        # Import settings
        success = _import_design_settings(test_config, mock_save_setting)

        assert success, "Import should succeed"
        assert 'pdf_design_settings' in saved_settings, "Should save pdf_design_settings"
        assert 'visualization_settings' in saved_settings, "Should save visualization_settings"
        assert 'ui_theme_settings' in saved_settings, "Should save ui_theme_settings"

        # Verify data integrity
        assert saved_settings['pdf_design_settings']['primary_color'] == '#FF0000'
        assert saved_settings['visualization_settings']['global_chart_colors'][0] == '#FF0000'
        assert saved_settings['ui_theme_settings']['active_theme'] == 'dark'

        print("✅ Import erfolgreich")
        print(f"   - Gespeicherte Einstellungen: {len(saved_settings)}")
        print(f"   - Keys: {', '.join(saved_settings.keys())}")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_setting_friendly_name():
    """Test: Benutzerfreundliche Namen für Einstellungs-Keys"""
    print("\n" + "=" * 70)
    print("TEST 5: Benutzerfreundliche Namen")
    print("=" * 70)

    try:
        # Import function
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import _get_setting_friendly_name

        # Test known keys
        test_cases = {
            'pdf_design_settings': 'PDF-Design-Einstellungen',
            'visualization_settings': 'Diagramm-Farbkonfigurationen',
            'ui_theme_settings': 'UI-Theme-Einstellungen',
            'pdf_templates': 'PDF-Template-Einstellungen',
            'pdf_layout_options': 'Layout-Optionen',
            'custom_color_palettes': 'Custom-Farbpaletten'
        }

        for key, expected_name in test_cases.items():
            friendly_name = _get_setting_friendly_name(key)
            assert friendly_name == expected_name, \
                f"Expected '{expected_name}' for key '{key}', got '{friendly_name}'"

        # Test unknown key
        unknown_key = 'unknown_setting'
        friendly_name = _get_setting_friendly_name(unknown_key)
        assert friendly_name == unknown_key, "Unknown key should return itself"

        print("✅ Alle benutzerfreundlichen Namen korrekt")
        print(f"   - Getestete Keys: {len(test_cases)}")

        return True

    except Exception as e:
        print(f"❌ Fehler bei benutzerfreundlichen Namen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_export_import_cycle():
    """Test: Vollständiger Export-Import-Zyklus"""
    print("\n" + "=" * 70)
    print("TEST 6: Vollständiger Export-Import-Zyklus")
    print("=" * 70)

    try:
        # Import functions
        sys.path.insert(0, '.')
        from admin_pdf_settings_ui import (
            _collect_all_design_settings,
            _validate_imported_config,
            _import_design_settings
        )

        # Step 1: Create original settings
        original_settings = {
            'pdf_design_settings': {
                'primary_color': '#1E3A8A',
                'secondary_color': '#3B82F6',
                'font_family': 'Helvetica'
            },
            'visualization_settings': {
                'global_chart_colors': [
                    '#1E3A8A', '#3B82F6', '#10B981'
                ]
            }
        }

        # Mock load_setting
        def mock_load_setting(key, default=None):
            return original_settings.get(key, default)

        # Step 2: Export (collect settings)
        exported_config = _collect_all_design_settings(mock_load_setting)

        # Step 3: Add metadata
        exported_config['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'version': '1.0'
        }

        # Step 4: Convert to JSON and back (simulate file save/load)
        json_str = json.dumps(exported_config, indent=2)
        imported_config = json.loads(json_str)

        # Step 5: Validate imported config
        is_valid, errors = _validate_imported_config(imported_config)
        assert is_valid, f"Imported config should be valid. Errors: {errors}"

        # Step 6: Import settings
        saved_settings = {}

        def mock_save_setting(key, value):
            saved_settings[key] = value
            return True

        success = _import_design_settings(imported_config, mock_save_setting)
        assert success, "Import should succeed"

        # Step 7: Verify data integrity
        assert saved_settings['pdf_design_settings']['primary_color'] == \
            original_settings['pdf_design_settings']['primary_color']
        assert saved_settings['visualization_settings']['global_chart_colors'] == \
            original_settings['visualization_settings']['global_chart_colors']

        print("✅ Vollständiger Export-Import-Zyklus erfolgreich")
        print("   - Export ✓")
        print("   - JSON-Serialisierung ✓")
        print("   - Validierung ✓")
        print("   - Import ✓")
        print("   - Datenintegrität ✓")

        return True

    except Exception as e:
        print(f"❌ Fehler im Export-Import-Zyklus: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führt alle Tests aus"""
    print("\n" + "=" * 70)
    print("TASK 14: IMPORT/EXPORT FÜR DESIGN-KONFIGURATIONEN - TESTS")
    print("=" * 70)

    tests = [
        ("Sammle Design-Einstellungen", test_collect_all_design_settings),
        ("Export mit Metadaten", test_export_with_metadata),
        ("Validierung importierter Konfiguration", test_validate_imported_config),
        ("Import von Design-Einstellungen", test_import_design_settings),
        ("Benutzerfreundliche Namen", test_get_setting_friendly_name),
        ("Vollständiger Export-Import-Zyklus", test_full_export_import_cycle)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' fehlgeschlagen: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST-ZUSAMMENFASSUNG")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"ERGEBNIS: {passed}/{total} Tests bestanden")
    print("=" * 70)

    if passed == total:
        print("\n🎉 Alle Tests erfolgreich! Task 14 ist vollständig implementiert.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} Test(s) fehlgeschlagen.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
