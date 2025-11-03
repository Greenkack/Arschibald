"""
DIAGNOSE: Warum zeigt PDF nicht die richtigen Ergebnisse?
"""

import os
import re

print("=" * 100)
print("DIAGNOSE: PDF DATEN-PROBLEM")
print("=" * 100)
print()

# 1. Prüfe wo final_pricing_data gesetzt wird
print("🔍 PRÜFUNG 1: Wo wird 'final_pricing_data' gesetzt?")
print("-" * 100)

def find_in_file(filepath, pattern):
    """Sucht Pattern in Datei"""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
            matches = re.finditer(pattern, content, re.IGNORECASE)
            results = []
            for match in matches:
                # Finde Zeilen nummer
                line_num = content[:match.start()].count('\n') + 1
                # Hole die Zeile
                lines = content.split('\n')
                line_content = lines[line_num - 1].strip()
                results.append((line_num, line_content))
            return results
    except Exception:
        return []

# Suche in wichtigen Dateien
files_to_check = [
    'solar_calculator.py',
    'calculations.py',
    'pdf_template_engine/placeholders.py',
]

for filename in files_to_check:
    if os.path.exists(filename):
        print(f"\n📄 {filename}:")
        # Suche nach session_state['final_pricing_data'] =
        pattern = r"session_state\[['\"](final_pricing_data)['\"]]\s*="
        matches = find_in_file(filename, pattern)
        if matches:
            for line_num, line_content in matches:
                print(f"   Zeile {line_num:4d}: {line_content}")
        else:
            print("   ❌ NICHT GEFUNDEN!")

print()
print("=" * 100)
print("🔍 PRÜFUNG 2: Wo wird 'final_pricing_data' gelesen?")
print("-" * 100)

for filename in files_to_check:
    if os.path.exists(filename):
        print(f"\n📄 {filename}:")
        # Suche nach session_state.get('final_pricing_data') oder session_state['final_pricing_data']
        pattern = r"session_state\[?\.?['\"]final_pricing_data['\"]?\]?"
        matches = find_in_file(filename, pattern)
        if matches:
            count = 0
            for line_num, line_content in matches[:5]:  # Nur erste 5
                print(f"   Zeile {line_num:4d}: {line_content}")
                count += 1
            if len(matches) > 5:
                print(f"   ... und {len(matches) - 5} weitere")
        else:
            print("   ❌ NICHT GEFUNDEN!")

print()
print("=" * 100)
print("🔍 PRÜFUNG 3: Was wird in solar_calculator.py gespeichert?")
print("-" * 100)

if os.path.exists('solar_calculator.py'):
    print("\n📄 solar_calculator.py:")
    # Suche nach allen session_state Zuweisungen für pricing
    pattern = r"session_state\[['\"]([^'\"]*pricing[^'\"]*)['\"]]\s*="
    matches = find_in_file('solar_calculator.py', pattern)
    if matches:
        for line_num, line_content in matches:
            print(f"   Zeile {line_num:4d}: {line_content}")
    else:
        print("   ❌ KEINE PRICING DATEN GEFUNDEN!")

print()
print("=" * 100)
print("💡 DIAGNOSE ABGESCHLOSSEN")
print("=" * 100)
print()
print("📊 ZUSAMMENFASSUNG:")
print()
print("Problem: placeholders.py liest aus 'final_pricing_data',")
print("         aber solar_calculator.py speichert nur:")
print("         - simple_pricing_data")
print("         - complete_pricing_data")
print()
print("Lösung: solar_calculator.py muss AUCH 'final_pricing_data' speichern!")
print("        mit den finalen UPPERCASE Keys (FINAL_END_PREIS, etc.)")
print()
print("=" * 100)
