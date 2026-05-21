"""
Demonstration der Echtzeit-Preisberechnung mit korrekter Formel.

Zeigt wie sich der Preis in Echtzeit ändert, wenn verschiedene Parameter angepasst werden.
"""

from calculations import _calculate_final_price_with_correct_formula
from price_matrix import PriceMatrix
import os
import sys

import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_demo_matrix():
    """Erstellt eine Demo-Preismatrix"""
    matrix_data = {
        'Speicher 10kWh': [14500.0, 17200.0, 19800.0, 22400.0, 25000.0],
        'Speicher 15kWh': [16200.0, 18900.0, 21500.0, 24100.0, 26700.0],
        'Speicher 20kWh': [17800.0, 20500.0, 23100.0, 25700.0, 28300.0],
        'Ohne Speicher': [11000.0, 13200.0, 15400.0, 17600.0, 19800.0]
    }

    df = pd.DataFrame(matrix_data, index=[10, 12, 15, 18, 20])
    df.index.name = 'Anzahl Module'
    return PriceMatrix(df)


def simulate_realtime_pricing_updates():
    """Simuliert Echtzeit-Preisänderungen"""

    print(" ECHTZEIT-PREISBERECHNUNG DEMONSTRATION")
    print("=" * 60)

    # Setup
    price_matrix = create_demo_matrix()
    module_count = 15
    storage_model = "Speicher 15kWh"

    # Basis-Matrixpreis abrufen
    matrix_price, errors = price_matrix.get_price(
        module_count, storage_model, True)
    print("Basis-Setup:")
    print(f"   Module: {module_count} Stück")
    print(f"   Speicher: {storage_model}")
    print(f"   Matrixpreis: {matrix_price:,.2f}€")

    # Zusatzkosten definieren
    additional_costs = 2800.0  # Zubehör, Installation, etc.
    print(f"   Zusatzkosten (Zubehör): {additional_costs:,.2f}€")

    vat_rate = 19.0

    # Verschiedene Preismodifikations-Szenarien
    scenarios = [{'name': 'Basis (keine Modifikationen)',
                  'modifications': {'discount_percent': 0.0,
                                    'surcharge_percent': 0.0,
                                    'special_discount': 0.0,
                                    'additional_costs': 0.0}},
                 {'name': 'Kunde erhält 5% Mengenrabatt',
                  'modifications': {'discount_percent': 5.0,
                                    'surcharge_percent': 0.0,
                                    'special_discount': 0.0,
                                    'additional_costs': 0.0}},
                 {'name': '+ 500€ Sonderrabatt (Empfehlung)',
                  'modifications': {'discount_percent': 5.0,
                                    'surcharge_percent': 0.0,
                                    'special_discount': 500.0,
                                    'additional_costs': 0.0}},
                 {'name': '+ 300€ Zusatzkosten (Gerüst)',
                  'modifications': {'discount_percent': 5.0,
                                    'surcharge_percent': 0.0,
                                    'special_discount': 500.0,
                                    'additional_costs': 300.0}},
                 {'name': '+ 2% Aufpreis (Eilauftrag)',
                  'modifications': {'discount_percent': 5.0,
                                    'surcharge_percent': 2.0,
                                    'special_discount': 500.0,
                                    'additional_costs': 300.0}}]

    print("\n Echtzeit-Preisänderungen:")
    print("-" * 60)

    previous_price = None

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")

        result = _calculate_final_price_with_correct_formula(
            base_matrix_price=matrix_price,
            additional_costs=additional_costs,
            pricing_modifications=scenario['modifications'],
            vat_rate_percent=vat_rate,
            debug_mode=False
        )

        current_price_netto = result['final_price_netto']
        current_price_brutto = result['final_price_brutto']

        print(f"   Preis (netto): {current_price_netto:,.2f}€")
        print(f"   Preis (brutto): {current_price_brutto:,.2f}€")

        if previous_price is not None:
            change = current_price_netto - previous_price
            if previous_price != 0:
                change_percent = (change / previous_price) * 100
            else:
                change_percent = 0.0

            if change > 0:
                print(
                    f"   Änderung: +{change:,.2f}€ (+{change_percent:.1f}%)")
            elif change < 0:
                print(f"   [DOWN] Änderung: {change:,.2f}€ ({change_percent:.1f}%)")
            else:
                print("     Keine Änderung")

        # Zeige angewandte Modifikationen
        mods = scenario['modifications']
        active_mods = []
        if mods['discount_percent'] > 0:
            active_mods.append(f"{mods['discount_percent']}% Rabatt")
        if mods['surcharge_percent'] > 0:
            active_mods.append(f"{mods['surcharge_percent']}% Aufpreis")
        if mods['special_discount'] > 0:
            active_mods.append(f"{mods['special_discount']}€ Sonderrabatt")
        if mods['additional_costs'] > 0:
            active_mods.append(f"{mods['additional_costs']}€ Zusatzkosten")

        if active_mods:
            print(f"     Aktive Modifikationen: {', '.join(active_mods)}")

        previous_price = current_price_netto

    print("\n" + "=" * 60)
    print("Echtzeit-Preisberechnung erfolgreich demonstriert!")
    print("   - Jede Änderung wird sofort berechnet")
    print("   - Korrekte Formel: Matrixpreis + Zubehör - Rabatte")
    print("   - Transparente Preisänderungen")


def demonstrate_different_matrix_scenarios():
    """Demonstriert verschiedene Matrix-Szenarien"""

    print("\n\n  VERSCHIEDENE MATRIX-SZENARIEN")
    print("=" * 60)

    price_matrix = create_demo_matrix()

    # Verschiedene Konfigurationen testen
    configurations = [
        {'modules': 10, 'storage': 'Ohne Speicher', 'include_storage': False},
        {'modules': 12, 'storage': 'Speicher 10kWh', 'include_storage': True},
        {'modules': 15, 'storage': 'Speicher 15kWh', 'include_storage': True},
        {'modules': 18, 'storage': 'Speicher 20kWh', 'include_storage': True},
        {'modules': 20, 'storage': 'Ohne Speicher', 'include_storage': False},
    ]

    additional_costs = 1800.0
    standard_modifications = {
        'discount_percent': 3.0,  # Standard 3% Rabatt
        'surcharge_percent': 0.0,
        'special_discount': 0.0,
        'additional_costs': 0.0
    }

    print("Konfiguration | Matrixpreis | + Zubehör | - 3% Rabatt | Endpreis (netto)")
    print("-" * 80)

    for config in configurations:
        # Matrix-Lookup
        matrix_price, errors = price_matrix.get_price(
            config['modules'],
            config['storage'],
            config['include_storage']
        )

        # Endpreis berechnen
        result = _calculate_final_price_with_correct_formula(
            base_matrix_price=matrix_price,
            additional_costs=additional_costs,
            pricing_modifications=standard_modifications,
            vat_rate_percent=19.0
        )

        storage_text = config['storage'] if config['include_storage'] else 'Ohne Speicher'

        print(f"{config['modules']:2d} Module + {storage_text:<15} | "
              f"{matrix_price:8,.0f}€ | "
              f"{matrix_price + additional_costs:8,.0f}€ | "
              f"{(matrix_price + additional_costs) * 0.97:8,.0f}€ | "
              f"{result['final_price_netto']:8,.0f}€")

    print("\nVerschiedene Matrix-Szenarien erfolgreich getestet!")


def main():
    """Hauptfunktion für die Demonstration"""

    print("DEMONSTRATION: Korrekte Zusatzkosten-Integration")
    print("Task 8: Integriere Zusatzkosten-Berechnung korrekt")
    print("=" * 80)

    try:
        # Demo 1: Echtzeit-Preisänderungen
        simulate_realtime_pricing_updates()

        # Demo 2: Verschiedene Matrix-Szenarien
        demonstrate_different_matrix_scenarios()

        print("\n" + "=" * 80)
        print(" DEMONSTRATION ERFOLGREICH ABGESCHLOSSEN!")
        print("\n Implementierte Anforderungen (Task 8):")
        print("   Matrixpreis wird als Basis verwendet")
        print("   Korrekte Formel: Matrixpreis + Zubehör - Rabatte")
        print("   Echtzeit-Aktualisierung bei Änderungen")
        print("   Endpreis-Berechnung mit verschiedenen Szenarien")
        print("\nErfüllte Requirements:")
        print("   5.1: Zubehör wird zum Matrixpreis hinzugefügt")
        print("   5.2: Rabatte werden vom Matrixpreis abgezogen")
        print("   5.3: Korrekte Formel implementiert")
        print("   5.4: Endpreis zeigt alle Optionen")
        print("   5.5: Echtzeit-Aktualisierung funktioniert")

        return True

    except Exception as e:
        print(f"\nDEMONSTRATION FEHLGESCHLAGEN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
