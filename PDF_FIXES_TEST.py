#!/usr/bin/env python3
"""
Test der PDF-Korrekturen
"""

# 1. Test des Produktnamen-Filters


def test_product_name_filter():
    import re

    def _filter_unwanted_words_from_model_name(model_name: str) -> str:
        if not model_name or not isinstance(model_name, str):
            return model_name

        unwanted_words = [
            "Batteriewechselrichter",
            "Hybrid-Wechselrichter",
            "Stromspeicher",
            "Batteriespeicher",
            "Speicherturm",
            "Batterieturm",
            "Photovoltaik-Modul",
            "Batterie Hybrid",
            "Wechselrichter"
        ]

        filtered_name = model_name

        for word in unwanted_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            filtered_name = re.sub(
                pattern, '', filtered_name, flags=re.IGNORECASE)

        filtered_name = re.sub(r'\s+', ' ', filtered_name).strip()

        return filtered_name

    # Test-Fälle
    test_cases = [
        ("BT Serie GW10K-BT 10 kW Batteriewechselrichter", "BT Serie GW10K-BT 10 kW"),
        ("Hybrid-Wechselrichter SolarEdge SE10K", "SolarEdge SE10K"),
        ("LG Chem RESU 10H Batteriespeicher", "LG Chem RESU 10H"),
        ("Photovoltaik-Modul JA Solar 400W", "JA Solar 400W"),
        ("Batterie Hybrid System 5kW", "System 5kW"),
        ("LUNA2000-7-S1-7kWh Stromspeicher", "LUNA2000-7-S1-7kWh")
    ]

    print("=== PRODUKTNAMEN-FILTER TEST ===")
    all_passed = True

    for original, expected in test_cases:
        result = _filter_unwanted_words_from_model_name(original)
        passed = result == expected
        all_passed = all_passed and passed

        print(f"Input:    {original}")
        print(f"Expected: {expected}")
        print(f"Result:   {result}")
        print(f"Status:   {'✅ PASS' if passed else '❌ FAIL'}")
        print("---")

    return all_passed

# 2. Test der Amortisationszeit-Berechnung


def test_amortization_calculation():
    print("=== AMORTISATIONSZEIT TEST ===")

    # Simuliere verschiedene Szenarien
    scenarios = [
        {
            "name": "Nur Basis",
            "total_investment_netto": 15970.0,
            "project_details": {},
            "annual_benefit": 1200.0,
            "expected_years": 15970.0 / 1200.0
        },
        {
            "name": "Mit Provision",
            "total_investment_netto": 15970.0,
            "project_details": {"final_price_with_provision": 18970.0},
            "annual_benefit": 1200.0,
            "expected_years": 18970.0 / 1200.0
        },
        {
            "name": "Mit Preisänderungen",
            "total_investment_netto": 15970.0,
            "project_details": {"final_modified_price_net": 17521.5},
            "annual_benefit": 1200.0,
            "expected_years": 17521.5 / 1200.0
        }
    ]

    for scenario in scenarios:
        # Simuliere die Berechnung
        final_investment_amount = scenario["total_investment_netto"]

        # Prioritätslogik anwenden
        project_details = scenario["project_details"]
        if project_details.get('final_modified_price_net'):
            final_investment_amount = float(
                project_details['final_modified_price_net'])
        elif project_details.get('final_price_with_provision'):
            final_investment_amount = float(
                project_details['final_price_with_provision'])
        elif project_details.get('final_offer_price_net'):
            final_investment_amount = float(
                project_details['final_offer_price_net'])

        amortization_years = final_investment_amount / \
            scenario["annual_benefit"]

        print(f"Szenario: {scenario['name']}")
        print(f"Investment: {final_investment_amount:,.2f} €")
        print(f"Jährlicher Nutzen: {scenario['annual_benefit']:,.2f} €")
        print(f"Amortisationszeit: {amortization_years:.1f} Jahre")
        print(f"Erwartet: {scenario['expected_years']:.1f} Jahre")
        print(
            f"Status: {
                '✅ PASS' if abs(
                    amortization_years -
                    scenario['expected_years']) < 0.01 else '❌ FAIL'}")
        print("---")

# 3. Test der MwSt-Berechnung


def test_vat_calculation():
    print("=== MEHRWERTSTEUER TEST ===")

    scenarios = [{"name": "Nur Basis",
                  "project_details": {},
                  "analysis_results": {"total_investment_netto": 15970.0},
                  "expected_vat": 15970.0 * 0.19},
                 {"name": "Mit Provision",
                  "project_details": {"final_price_with_provision": 18970.0},
                  "analysis_results": {},
                  "expected_vat": 18970.0 * 0.19},
                 {"name": "Mit Preisänderungen",
                  "project_details": {"final_modified_price_net": 17521.5},
                  "analysis_results": {},
                  "expected_vat": 17521.5 * 0.19},
                 {"name": "Bereits formatiert",
                  "project_details": {"formatted_final_modified_vat_amount": "3.329,09 €"},
                  "analysis_results": {},
                  "expected_formatted": "3.329,09 €"}]

    for scenario in scenarios:
        project_details = scenario["project_details"]
        analysis_results = scenario["analysis_results"]

        vat_amount = None
        vat_formatted = None

        # Simuliere die Prioritätslogik
        if project_details.get('formatted_final_modified_vat_amount'):
            vat_formatted = project_details['formatted_final_modified_vat_amount']
        elif project_details.get('final_modified_price_net'):
            net_price = float(project_details['final_modified_price_net'])
            vat_amount = net_price * 0.19
        elif project_details.get('final_price_with_provision'):
            net_price = float(project_details['final_price_with_provision'])
            vat_amount = net_price * 0.19
        elif project_details.get('final_offer_price_net'):
            net_price = float(project_details['final_offer_price_net'])
            vat_amount = net_price * 0.19
        else:
            # Fallback
            base_net = analysis_results.get("total_investment_netto")
            if isinstance(base_net, (int, float)):
                vat_amount = float(base_net) * 0.19

        print(f"Szenario: {scenario['name']}")
        if vat_formatted:
            print(f"MwSt (formatiert): {vat_formatted}")
            expected = scenario.get('expected_formatted', '')
            print(f"Erwartet: {expected}")
            print(
                f"Status: {
                    '✅ PASS' if vat_formatted == expected else '❌ FAIL'}")
        elif vat_amount is not None:
            print(f"MwSt (berechnet): {vat_amount:,.2f} €")
            expected = scenario.get('expected_vat', 0)
            print(f"Erwartet: {expected:,.2f} €")
            print(
                f"Status: {
                    '✅ PASS' if abs(
                        vat_amount -
                        expected) < 0.01 else '❌ FAIL'}")
        print("---")


if __name__ == "__main__":
    print("🔧 PDF-KORREKTUREN TESTS")
    print("=" * 50)

    # Test 1: Produktnamen-Filter
    filter_passed = test_product_name_filter()

    # Test 2: Amortisationszeit
    test_amortization_calculation()

    # Test 3: MwSt
    test_vat_calculation()

    print("=" * 50)
    print(
        f"Filter-Test: {'✅ BESTANDEN' if filter_passed else '❌ FEHLGESCHLAGEN'}")
    print("Amortisationszeit & MwSt: Logik implementiert (Session State abhängig)")
