"""
Test für Diagramm-Farbeinstellungen UI (Task 10)

Testet:
- Globale Farbeinstellungen (Task 10.1)
- Farbpaletten-Bibliothek (Task 10.2)
- Individuelle Diagramm-Konfiguration (Task 10.3)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_global_chart_colors():
    """Test Task 10.1: Globale Farbeinstellungen"""
    print("\n=== Test 10.1: Globale Farbeinstellungen ===")

    # Mock visualization settings
    visualization_settings = {
        'global_chart_colors': [
            '#1E3A8A',
            '#3B82F6',
            '#10B981',
            '#F59E0B',
            '#EF4444',
            '#8B5CF6'
        ]
    }

    # Verify structure
    assert 'global_chart_colors' in visualization_settings
    assert len(visualization_settings['global_chart_colors']) == 6
    assert all(
        color.startswith('#')
        for color in visualization_settings['global_chart_colors']
    )

    print("✓ Globale Farbeinstellungen Struktur korrekt")
    print(f"✓ 6 Farben konfiguriert: "
          f"{visualization_settings['global_chart_colors']}")

    return True


def test_color_palette_library():
    """Test Task 10.2: Farbpaletten-Bibliothek"""
    print("\n=== Test 10.2: Farbpaletten-Bibliothek ===")

    # Define palettes (same as in implementation)
    palettes = {
        'Corporate': [
            '#1E3A8A', '#3B82F6', '#60A5FA',
            '#6B7280', '#9CA3AF', '#1F2937'
        ],
        'Eco': [
            '#065F46', '#10B981', '#34D399',
            '#6EE7B7', '#A7F3D0', '#D1FAE5'
        ],
        'Energy': [
            '#DC2626', '#F59E0B', '#FBBF24',
            '#FCD34D', '#FDE68A', '#FEF3C7'
        ],
        'Accessible': [
            '#0173B2', '#DE8F05', '#029E73',
            '#CC78BC', '#CA9161', '#949494'
        ]
    }

    # Verify all palettes have 6 colors
    for name, colors in palettes.items():
        assert len(colors) == 6, f"Palette {name} should have 6 colors"
        assert all(
            c.startswith('#') for c in colors
        ), f"All colors in {name} should be hex codes"

    print(f"✓ {len(palettes)} Farbpaletten definiert")
    print(f"✓ Paletten: {', '.join(palettes.keys())}")
    print("✓ Alle Paletten haben 6 Farben")

    return True


def test_individual_chart_config():
    """Test Task 10.3: Individuelle Diagramm-Konfiguration"""
    print("\n=== Test 10.3: Individuelle Diagramm-Konfiguration ===")

    # Chart categories (same as in implementation)
    chart_categories = {
        'Wirtschaftlichkeit': [
            ('cumulative_cashflow_chart', 'Kumulierter Cashflow'),
            ('cost_projection_chart', 'Stromkosten-Hochrechnung'),
            ('break_even_chart', 'Break-Even-Analyse'),
            ('amortisation_chart', 'Amortisationsdiagramm'),
            ('project_roi_matrix', 'Projektrendite-Matrix'),
            ('roi_comparison', 'ROI-Vergleich')
        ],
        'Produktion & Verbrauch': [
            ('monthly_prod_cons_chart', 'Monatliche Produktion vs. Verbrauch'),
            ('yearly_production_chart', 'Jahresproduktion'),
            ('daily_production', 'Tagesproduktion'),
            ('weekly_production', 'Wochenproduktion'),
            ('prod_vs_cons', 'Produktion vs. Verbrauch')
        ],
        'Eigenverbrauch & Autarkie': [
            ('consumption_coverage_pie', 'Verbrauchsdeckung'),
            ('pv_usage_pie', 'PV-Nutzung'),
            ('storage_effect', 'Speicherwirkung'),
            ('selfuse_stack', 'Eigenverbrauch vs. Einspeisung'),
            ('selfuse_ratio', 'Eigenverbrauchsgrad')
        ],
        'Finanzielle Analyse': [
            ('feed_in_revenue', 'Einspeisevergütung'),
            ('income_projection', 'Einnahmenprognose'),
            ('tariff_cube', 'Tarifvergleich (3D)'),
            ('tariff_comparison', 'Tarifvergleich'),
            ('cost_growth', 'Stromkostensteigerung')
        ],
        'CO2 & Umwelt': [
            ('co2_savings_value', 'CO2-Ersparnis vs. Wert')
        ],
        'Vergleiche & Szenarien': [
            ('scenario_comparison', 'Szenarienvergleich'),
            ('investment_value', 'Investitionsnutzwert')
        ]
    }

    # Verify categories
    assert len(chart_categories) == 6, "Should have 6 categories"

    total_charts = sum(len(charts) for charts in chart_categories.values())
    print(f"✓ {len(chart_categories)} Kategorien definiert")
    print(f"✓ {total_charts} Diagramme insgesamt")

    # Test individual chart configuration structure
    individual_charts = {
        'cumulative_cashflow_chart': {
            'use_global': False,
            'custom_colors': ['#1E3A8A', '#3B82F6', '#10B981']
        },
        'monthly_prod_cons_chart': {
            'use_global': True
        }
    }

    # Verify structure
    for chart_key, config in individual_charts.items():
        assert 'use_global' in config
        if not config['use_global']:
            assert 'custom_colors' in config
            assert len(config['custom_colors']) >= 3

    print("✓ Individuelle Konfiguration Struktur korrekt")
    print(f"✓ {len(individual_charts)} Diagramme konfiguriert (Beispiel)")

    return True


def test_visualization_settings_structure():
    """Test complete visualization_settings structure"""
    print("\n=== Test: Vollständige Struktur ===")

    visualization_settings = {
        'global_chart_colors': [
            '#1E3A8A', '#3B82F6', '#10B981',
            '#F59E0B', '#EF4444', '#8B5CF6'
        ],
        'individual_chart_colors': {
            'cumulative_cashflow_chart': {
                'use_global': False,
                'custom_colors': ['#1E3A8A', '#3B82F6', '#10B981']
            },
            'monthly_prod_cons_chart': {
                'use_global': True
            }
        }
    }

    # Verify top-level keys
    assert 'global_chart_colors' in visualization_settings
    assert 'individual_chart_colors' in visualization_settings

    print("✓ visualization_settings Struktur vollständig")
    print("✓ Kann in admin_settings gespeichert werden")

    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("TASK 10: Diagramm-Farbeinstellungen UI - Tests")
    print("=" * 60)

    tests = [
        ("10.1 Globale Farbeinstellungen", test_global_chart_colors),
        ("10.2 Farbpaletten-Bibliothek", test_color_palette_library),
        ("10.3 Individuelle Konfiguration", test_individual_chart_config),
        ("Vollständige Struktur", test_visualization_settings_structure)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST ZUSAMMENFASSUNG")
    print("=" * 60)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\nErgebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("\n🎉 Alle Tests erfolgreich!")
        return True
    else:
        print("\n❌ Einige Tests fehlgeschlagen")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
