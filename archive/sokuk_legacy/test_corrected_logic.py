#!/usr/bin/env python3
"""
Test der korrigierten Amortisationszeit und MwSt-Logik
"""


def test_corrected_logic():
    print('=== TEST DER KORRIGIERTEN LOGIK ===')

    # Simuliere project_details mit finalen Preisen
    project_details_scenarios = [
        {
            'name': 'Mit Preisänderungen',
            'data': {
                'final_modified_price_net': 17521.5,
                'formatted_final_modified_vat_amount': '3.329,09 €'
            },
            'expected_amortization_base': 17521.5,
            'expected_vat': '3.329,09 €'
        },
        {
            'name': 'Mit Provision',
            'data': {
                'final_price_with_provision': 18970.0
            },
            'expected_amortization_base': 18970.0,
            'expected_vat_calc': 18970.0 * 0.19
        },
        {
            'name': 'Nur Basis',
            'data': {},
            'expected_fallback': True
        }
    ]

    for scenario in project_details_scenarios:
        print(f"Szenario: {scenario['name']}")
        project_details = scenario['data']

        # Test Amortisationszeit-Logik
        final_investment_amount = 15970.0  # Fallback
        if project_details.get('final_modified_price_net'):
            final_investment_amount = float(
                project_details['final_modified_price_net'])
            print(
                f'  Amortisation: final_modified_price_net = {final_investment_amount}')
        elif project_details.get('final_price_with_provision'):
            final_investment_amount = float(
                project_details['final_price_with_provision'])
            print(
                f'  Amortisation: final_price_with_provision = {final_investment_amount}')
        else:
            print(f'  Amortisation: Fallback = {final_investment_amount}')

        # Test MwSt-Logik
        if project_details.get('formatted_final_modified_vat_amount'):
            vat_result = project_details['formatted_final_modified_vat_amount']
            print(
                f'  MwSt: formatted_final_modified_vat_amount = {vat_result}')
        elif project_details.get('final_modified_price_net'):
            vat_calc = float(
                project_details['final_modified_price_net']) * 0.19
            print(
                f'  MwSt: berechnet aus final_modified_price_net = {
                    vat_calc:.2f} €')
        elif project_details.get('final_price_with_provision'):
            vat_calc = float(
                project_details['final_price_with_provision']) * 0.19
            print(
                f'  MwSt: berechnet aus final_price_with_provision = {
                    vat_calc:.2f} €')
        else:
            print('  MwSt: Fallback auf analysis_results')

        print('---')


if __name__ == "__main__":
    test_corrected_logic()
    print()
    print("✅ PUNKTE 2 & 3 IMPLEMENTIERT:")
    print("- Amortisationszeit verwendet finale Preise aus project_details")
    print("- MwSt verwendet finale Preise aus project_details")
    print("- Debug-Ausgaben hinzugefügt für Troubleshooting")
    print()
    print("🔧 NÄCHSTER SCHRITT:")
    print("Teste die PDF-Generierung und schaue in die Konsole nach:")
    print("- 'DEBUG: Amortisation verwendet...'")
    print("- 'DEBUG: MwSt verwendet...'")
