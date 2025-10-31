"""
Test für die korrekte Integration der Zusatzkosten-Berechnung.

Testet die Anforderungen aus Task 8:
- Matrixpreis als Basis verwendet wird
- Korrekte Formel: Matrixpreis + Zubehör - Rabatte
- Echtzeit-Aktualisierung bei Änderungen
- Endpreis-Berechnung mit verschiedenen Szenarien
"""

from calculations import (
    _calculate_final_price_with_correct_formula,
    _collect_pricing_modifications_from_session,
)
from price_matrix import PriceMatrix
import os
import sys
from unittest.mock import patch

import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAdditionalCostsIntegration:
    """Test-Suite für die Zusatzkosten-Integration"""

    def setup_method(self):
        """Setup für jeden Test"""
        # Test-Matrix erstellen
        self.test_matrix_data = {
            'Speicher A': [15000.0, 18000.0, 21000.0],
            'Speicher B': [16000.0, 19000.0, 22000.0],
            'Ohne Speicher': [12000.0, 14000.0, 16000.0]
        }
        self.test_matrix_df = pd.DataFrame(
            self.test_matrix_data,
            index=[10, 15, 20]
        )
        self.test_matrix_df.index.name = 'Anzahl Module'

        # Test-Projektdaten
        self.test_project_data = {
            'customer_data': {'type': 'privat'},
            'project_details': {
                'module_quantity': 15,
                'selected_module_id': 'test_module_1',
                'include_storage': True,
                'selected_storage_id': 'test_storage_1',
                'selected_storage_storage_power_kw': 10.0,
                'annual_consumption_kwh_yr': 4000.0,
                'electricity_price_kwh': 0.30
            },
            'economic_data': {
                'custom_costs_netto': 500.0
            }
        }

        self.test_texts = {}

    def test_collect_pricing_modifications_from_session(self):
        """Test: Sammeln von Preismodifikationen aus Session State"""

        # Mock Streamlit Session State
        mock_session_state = {
            'pricing_modifications': {
                'discount_percent': 5.0,
                'surcharge_percent': 2.0,
                'special_discount': 200.0,
                'additional_costs': 300.0
            },
            'pricing_modifications_discount_slider': 7.0,  # Höher als im Dict
            'pricing_modifications_rebates_slider': 150.0,
            'pricing_modifications_surcharge_slider': 1.0,
            'pricing_modifications_special_costs_slider': 100.0,
            'pricing_modifications_miscellaneous_slider': 50.0
        }

        with patch('streamlit.session_state', mock_session_state):
            with patch('calculations.st') as mock_st:
                mock_st.session_state = mock_session_state
                mock_st.session_state.get = mock_session_state.get

                modifications = _collect_pricing_modifications_from_session()

                # Slider-Werte sollten Priorität haben (höhere Werte)
                assert modifications['discount_percent'] == 7.0  # Slider-Wert
                # Dict-Wert (höher)
                assert modifications['surcharge_percent'] == 2.0
                # Dict-Wert (höher)
                assert modifications['special_discount'] == 200.0
                # Dict-Wert (höher als Slider-Summe)
                assert modifications['additional_costs'] == 300.0

    def test_calculate_final_price_with_correct_formula_basic(self):
        """Test: Grundlegende Preisberechnung mit korrekter Formel"""

        base_matrix_price = 15000.0
        additional_costs = 2000.0  # Zubehör
        pricing_modifications = {
            'discount_percent': 5.0,  # 5% Rabatt
            'surcharge_percent': 0.0,
            'special_discount': 500.0,  # 500€ Sonderrabatt
            'additional_costs': 200.0   # 200€ Zusatzkosten
        }
        vat_rate_percent = 19.0
        one_time_bonus = 300.0

        result = _calculate_final_price_with_correct_formula(
            base_matrix_price=base_matrix_price,
            additional_costs=additional_costs,
            pricing_modifications=pricing_modifications,
            vat_rate_percent=vat_rate_percent,
            one_time_bonus=one_time_bonus,
            debug_mode=True
        )

        # Erwartete Berechnung:
        # 1. Subtotal: 15000 + 2000 = 17000€
        # 2. Nach Bonus: 17000 - 300 = 16700€
        # 3. Nach 5% Rabatt: 16700 * 0.95 = 15865€
        # 4. Nach Sonderrabatt: 15865 - 500 = 15365€
        # 5. Nach Zusatzkosten: 15365 + 200 = 15565€
        # 6. Brutto: 15565 * 1.19 = 18522.35€

        assert result['subtotal_netto'] == 17000.0
        assert result['subtotal_after_bonus'] == 16700.0
        assert abs(result['final_price_netto'] - 15565.0) < 0.01
        assert abs(result['final_price_brutto'] - 18522.35) < 0.01
        assert result['one_time_bonus_applied'] == 300.0

    def test_calculate_final_price_no_modifications(self):
        """Test: Preisberechnung ohne Modifikationen"""

        base_matrix_price = 12000.0
        additional_costs = 1500.0
        pricing_modifications = {
            'discount_percent': 0.0,
            'surcharge_percent': 0.0,
            'special_discount': 0.0,
            'additional_costs': 0.0
        }
        vat_rate_percent = 19.0

        result = _calculate_final_price_with_correct_formula(
            base_matrix_price=base_matrix_price,
            additional_costs=additional_costs,
            pricing_modifications=pricing_modifications,
            vat_rate_percent=vat_rate_percent
        )

        # Erwartete Berechnung: 12000 + 1500 = 13500€ (netto)
        assert result['final_price_netto'] == 13500.0
        assert abs(
            result['final_price_brutto'] -
            16065.0) < 0.01  # 13500 * 1.19

    def test_calculate_final_price_negative_prevention(self):
        """Test: Verhinderung negativer Preise"""

        base_matrix_price = 1000.0
        additional_costs = 500.0
        pricing_modifications = {
            'discount_percent': 50.0,  # 50% Rabatt
            'surcharge_percent': 0.0,
            'special_discount': 2000.0,  # Sehr hoher Sonderrabatt
            'additional_costs': 0.0
        }
        vat_rate_percent = 19.0

        result = _calculate_final_price_with_correct_formula(
            base_matrix_price=base_matrix_price,
            additional_costs=additional_costs,
            pricing_modifications=pricing_modifications,
            vat_rate_percent=vat_rate_percent
        )

        # Preis sollte nicht negativ werden
        assert result['final_price_netto'] == 0.0
        assert result['final_price_brutto'] == 0.0

    def test_matrix_price_as_base_scenario(self):
        """Test: Verschiedene Szenarien mit Matrixpreis als Basis"""

        # Szenario 1: Mit Speicher
        price_matrix = PriceMatrix(self.test_matrix_df)
        price_with_storage, errors = price_matrix.get_price(
            15, "Speicher A", True)

        assert price_with_storage == 18000.0
        assert len(errors) == 0

        # Szenario 2: Ohne Speicher
        price_without_storage, errors = price_matrix.get_price(15, None, False)

        assert price_without_storage == 14000.0
        assert len(errors) == 0

        # Szenario 3: Unbekannter Speicher (Fallback auf "Ohne Speicher")
        price_unknown_storage, errors = price_matrix.get_price(
            15, "Unbekannter Speicher", True)

        assert price_unknown_storage == 14000.0  # Fallback
        assert len(errors) == 1  # Sollte Warnung geben

    def test_real_time_update_simulation(self):
        """Test: Simulation der Echtzeit-Aktualisierung"""

        base_matrix_price = 15000.0
        additional_costs = 1000.0
        vat_rate_percent = 19.0

        # Szenario 1: Keine Modifikationen
        mods_1 = {
            'discount_percent': 0.0,
            'surcharge_percent': 0.0,
            'special_discount': 0.0,
            'additional_costs': 0.0}
        result_1 = _calculate_final_price_with_correct_formula(
            base_matrix_price, additional_costs, mods_1, vat_rate_percent
        )

        # Szenario 2: Rabatt hinzugefügt
        mods_2 = {
            'discount_percent': 10.0,
            'surcharge_percent': 0.0,
            'special_discount': 0.0,
            'additional_costs': 0.0}
        result_2 = _calculate_final_price_with_correct_formula(
            base_matrix_price, additional_costs, mods_2, vat_rate_percent
        )

        # Szenario 3: Zusätzliche Kosten hinzugefügt
        mods_3 = {
            'discount_percent': 10.0,
            'surcharge_percent': 0.0,
            'special_discount': 0.0,
            'additional_costs': 500.0}
        result_3 = _calculate_final_price_with_correct_formula(
            base_matrix_price, additional_costs, mods_3, vat_rate_percent
        )

        # Preise sollten sich entsprechend ändern
        assert result_1['final_price_netto'] == 16000.0  # 15000 + 1000
        assert result_2['final_price_netto'] == 14400.0  # (15000 + 1000) * 0.9
        # (15000 + 1000) * 0.9 + 500
        assert result_3['final_price_netto'] == 14900.0

        # Jeder Schritt sollte eine Änderung bewirken
        assert result_1['final_price_netto'] != result_2['final_price_netto']
        assert result_2['final_price_netto'] != result_3['final_price_netto']

    def test_various_calculation_scenarios(self):
        """Test: Verschiedene Berechnungsszenarien"""

        scenarios = [
            {
                'name': 'Kleines System ohne Speicher',
                'base_price': 10000.0,
                'additional_costs': 500.0,
                'modifications': {'discount_percent': 2.0, 'surcharge_percent': 0.0, 'special_discount': 0.0, 'additional_costs': 0.0},
                'expected_netto': 10290.0  # (10000 + 500) * 0.98
            },
            {
                'name': 'Großes System mit Speicher und Rabatt',
                'base_price': 25000.0,
                'additional_costs': 3000.0,
                'modifications': {'discount_percent': 8.0, 'surcharge_percent': 0.0, 'special_discount': 1000.0, 'additional_costs': 0.0},
                'expected_netto': 24760.0  # (25000 + 3000) * 0.92 - 1000
            },
            {
                'name': 'System mit Aufpreis und Zusatzkosten',
                'base_price': 15000.0,
                'additional_costs': 2000.0,
                'modifications': {'discount_percent': 0.0, 'surcharge_percent': 5.0, 'special_discount': 0.0, 'additional_costs': 800.0},
                'expected_netto': 18650.0  # (15000 + 2000) * 1.05 + 800
            }
        ]

        for scenario in scenarios:
            result = _calculate_final_price_with_correct_formula(
                base_matrix_price=scenario['base_price'],
                additional_costs=scenario['additional_costs'],
                pricing_modifications=scenario['modifications'],
                vat_rate_percent=19.0
            )

            assert abs(
                result['final_price_netto'] - scenario['expected_netto']) < 0.01, f"Szenario '{
                scenario['name']}' fehlgeschlagen: erwartet {
                scenario['expected_netto']}, erhalten {
                result['final_price_netto']}"

    def test_integration_with_matrix_lookup(self):
        """Test: Integration mit Matrix-Lookup"""

        # Erstelle PriceMatrix
        price_matrix = PriceMatrix(self.test_matrix_df)

        # Verschiedene Lookup-Szenarien
        test_cases = [{'modules': 10,
                       'storage': 'Speicher A',
                       'include_storage': True,
                       'expected': 15000.0},
                      {'modules': 15,
                       'storage': 'Speicher B',
                       'include_storage': True,
                       'expected': 19000.0},
                      {'modules': 20,
                       'storage': None,
                       'include_storage': False,
                       'expected': 16000.0},
                      ]

        for case in test_cases:
            # Matrix-Lookup
            matrix_price, errors = price_matrix.get_price(
                case['modules'],
                case['storage'],
                case['include_storage']
            )

            assert matrix_price == case['expected']

            # Zusatzkosten-Berechnung
            additional_costs = 1500.0  # Beispiel-Zubehör
            modifications = {
                'discount_percent': 5.0,
                'surcharge_percent': 0.0,
                'special_discount': 0.0,
                'additional_costs': 0.0}

            result = _calculate_final_price_with_correct_formula(
                base_matrix_price=matrix_price,
                additional_costs=additional_costs,
                pricing_modifications=modifications,
                vat_rate_percent=19.0
            )

            # Erwarteter Preis: (matrix_price + additional_costs) * 0.95
            expected_final = (matrix_price + additional_costs) * 0.95
            assert abs(result['final_price_netto'] - expected_final) < 0.01


def run_additional_costs_integration_tests():
    """Führt alle Tests für die Zusatzkosten-Integration aus"""

    print("🧪 Starte Tests für Zusatzkosten-Integration...")

    test_suite = TestAdditionalCostsIntegration()

    tests = [
        ('Sammeln von Preismodifikationen', test_suite.test_collect_pricing_modifications_from_session),
        ('Grundlegende Preisberechnung', test_suite.test_calculate_final_price_with_correct_formula_basic),
        ('Preisberechnung ohne Modifikationen', test_suite.test_calculate_final_price_no_modifications),
        ('Verhinderung negativer Preise', test_suite.test_calculate_final_price_negative_prevention),
        ('Matrixpreis als Basis', test_suite.test_matrix_price_as_base_scenario),
        ('Echtzeit-Aktualisierung', test_suite.test_real_time_update_simulation),
        ('Verschiedene Szenarien', test_suite.test_various_calculation_scenarios),
        ('Integration mit Matrix-Lookup', test_suite.test_integration_with_matrix_lookup),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_suite.setup_method()
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            failed += 1

    print(f"\n📊 Test-Ergebnisse: {passed} bestanden, {failed} fehlgeschlagen")

    if failed == 0:
        print("🎉 Alle Tests für die Zusatzkosten-Integration bestanden!")
        return True
    print("⚠️  Einige Tests sind fehlgeschlagen. Bitte überprüfen Sie die Implementierung.")
    return False


if __name__ == "__main__":
    success = run_additional_costs_integration_tests()
    exit(0 if success else 1)
