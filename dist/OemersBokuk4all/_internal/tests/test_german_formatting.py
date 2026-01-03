"""
Testskript: Deutsche Zahlenformatierung
Testet die format_german_number Funktion
"""

def format_german_number(number, decimals=2):
    """
    Formatiert Zahlen nach deutscher Notation:
    - Tausender-Trennzeichen: Punkt (.)
    - Dezimal-Trennzeichen: Komma ()
    - Immer 2 Dezimalstellen für Geldbeträge
    
    Beispiel: 12345.67 -> "12.345,67"
    """
    if number is None:
        return "0,00" if decimals == 2 else "0"
    
    # Format mit englischer Notation
    if decimals == 0:
        formatted = f"{number:,.0f}"
    else:
        formatted = f"{number:,.{decimals}f}"
    
    # Tausche Trennzeichen: , -> TEMP, . -> , TEMP -> .
    formatted = formatted.replace(',', 'TEMP')
    formatted = formatted.replace('.', ',')
    formatted = formatted.replace('TEMP', '.')
    
    return formatted

# Teste verschiedene Werte
test_cases = [
    (12345.67, 2, "12.345,67"),
    (12345.67, 0, "12.346"),
    (1234567.89, 2, "1.234.567,89"),
    (100, 2, "100,00"),
    (0, 2, "0,00"),
    (5.6, 2, "5,60"),
    (1000000, 0, "1.000.000"),
    (999.99, 2, "999,99"),
]

print(" Teste format_german_number() Funktion\n")
print("=" * 70)

all_passed = True
for value, decimals, expected in test_cases:
    result = format_german_number(value, decimals)
    passed = result == expected
    status = "" if passed else ""
    
    if not passed:
        all_passed = False
    
    print(f"{status} {value:>12} (decimals={decimals}) -> {result:>15} {'(erwartet: ' + expected + ')' if not passed else ''}")

print("=" * 70)
if all_passed:
    print("\nAlle Tests bestanden! Die Formatierung funktioniert korrekt.")
else:
    print("\nEinige Tests sind fehlgeschlagen.")

# Zeige Beispiele für typische Anwendungsfälle
print("\n\nBeispiele für typische Anwendungsfälle:\n")
print(f"Investitionskosten:     {format_german_number(25000, 2)} €")
print(f"Jährliche Einsparung:   {format_german_number(1850.50, 2)} €")
print(f"Leistung:               {format_german_number(12, 0)} kW")
print(f"SCOP:                   {format_german_number(4.2, 2)}")
print(f"Prozent:                {format_german_number(85.5, 1)} %")
print(f"CO2-Einsparung:         {format_german_number(3456.78, 2)} kg")
