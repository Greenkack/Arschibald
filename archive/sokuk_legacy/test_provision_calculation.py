#!/usr/bin/env python3
"""
Test der Provisionsberechnung im Solar Calculator
"""


def _format_german_currency(amount: float) -> str:
    """Format currency in German format: 1.234,56 €"""
    # Format with 2 decimal places
    formatted = f"{amount:.2f}"

    # Split into integer and decimal parts
    if '.' in formatted:
        integer_part, decimal_part = formatted.split('.')
    else:
        integer_part, decimal_part = formatted, "00"

    # Add thousand separators (dots) to integer part
    if len(integer_part) > 3:
        # Reverse, add dots every 3 digits, then reverse back
        reversed_int = integer_part[::-1]
        grouped = '.'.join(reversed_int[i:i + 3]
                           for i in range(0, len(reversed_int), 3))
        integer_part = grouped[::-1]

    return f"{integer_part},{decimal_part} €"


def test_provision_calculation():
    """Test der kompletten Provisionsberechnung"""

    # Test-Daten
    net_total_amount = 15970.0  # Basis
    provision_percent = 0.0     # 0%
    provision_euro = 3000.0     # 3000€

    # Berechnung wie im Solar Calculator
    provision_percent_amount = net_total_amount * (provision_percent / 100.0)
    total_provision_amount = provision_percent_amount + provision_euro
    final_price_with_provision = net_total_amount + total_provision_amount

    # Zusätzliche Berechnung (wie im Code)
    final_endpreis = net_total_amount + total_provision_amount

    # Formatierung
    formatted_net_total = _format_german_currency(net_total_amount)
    formatted_total_provision = _format_german_currency(total_provision_amount)
    formatted_final_endpreis = _format_german_currency(final_endpreis)

    print('=== VOLLSTÄNDIGER PROVISIONSTEST ===')
    print(f'Basis: {formatted_net_total}')
    print(f'Provision: {formatted_total_provision}')
    print(f'Endpreis: {formatted_final_endpreis}')
    print()
    print('=== ERWARTETES ERGEBNIS ===')
    print('Basis: 15.970,00 €')
    print('Provision: 3.000,00 €')
    print('Endpreis: 18.970,00 €')
    print()
    print('=== VERGLEICH ===')
    print(f'Basis korrekt: {formatted_net_total == "15.970,00 €"}')
    print(f'Provision korrekt: {formatted_total_provision == "3.000,00 €"}')
    print(f'Endpreis korrekt: {formatted_final_endpreis == "18.970,00 €"}')

    # Zusätzliche Tests mit verschiedenen Werten
    print()
    print('=== ZUSÄTZLICHE TESTS ===')

    # Test 1: Nur Prozent-Provision
    test_net = 10000.0
    test_percent = 5.0
    test_euro = 0.0

    test_percent_amount = test_net * (test_percent / 100.0)
    test_total_provision = test_percent_amount + test_euro
    test_final = test_net + test_total_provision

    print(
        f'Test 1 - 10.000€ + 5%: {_format_german_currency(test_final)} (erwartet: 10.500,00 €)')

    # Test 2: Prozent + Euro
    test_net = 20000.0
    test_percent = 3.0
    test_euro = 1000.0

    test_percent_amount = test_net * (test_percent / 100.0)
    test_total_provision = test_percent_amount + test_euro
    test_final = test_net + test_total_provision

    print(
        f'Test 2 - 20.000€ + 3% + 1.000€: {
            _format_german_currency(test_final)} (erwartet: 21.600,00 €)')

    return formatted_final_endpreis == "18.970,00 €"


if __name__ == "__main__":
    success = test_provision_calculation()
    print('\n=== ERGEBNIS ===')
    print(f'Test erfolgreich: {"✅ JA" if success else "❌ NEIN"}')
