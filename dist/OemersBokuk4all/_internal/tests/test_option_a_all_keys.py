"""
Test: Option A - Alle fehlenden Keys hinzugefügt?
Prüft ob alle 8 fehlenden Keys jetzt in PLACEHOLDER_MAPPING sind
"""

from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING
import sys

sys.path.insert(0, 'c:/Users/win10/Desktop/Bokuk2')


print("=" * 100)
print("TEST: OPTION A - ALLE KEYS VORHANDEN?")
print("=" * 100)

# Die 8 Keys die vorher fehlten
fehlende_keys = [
    "SIMPLE_KOMPONENTEN_SUMME",
    "FINAL_ZUBEHOR_TOTAL",
    "FINAL_ZWISCHENSUMME_FINAL",
    "FINAL_MWST_IN_ZWISCHENSUMME",
    "PRICING_NET_TOTAL",
    "PRICING_GROSS_TOTAL",
    "PRICING_HARDWARE_TOTAL",
    "PRICING_SERVICES_TOTAL",
]

# Plus ihre _FORMATTED Versionen
alle_keys = []
for key in fehlende_keys:
    alle_keys.append(key)
    alle_keys.append(f"{key}_FORMATTED")

print("\nTEST 1: Alle Keys im PLACEHOLDER_MAPPING?")
print("-" * 100)

erfolg = 0
fehler = 0

for key in alle_keys:
    if key in PLACEHOLDER_MAPPING:
        print(f"{key:50} -> {PLACEHOLDER_MAPPING[key]}")
        erfolg += 1
    else:
        print(f"{key:50} FEHLT!")
        fehler += 1

print("\n" + "=" * 100)
print(f"ERGEBNIS: {erfolg}/{len(alle_keys)} Keys vorhanden")
if fehler == 0:
    print(" ALLE KEYS ERFOLGREICH HINZUGEFÜGT!")
else:
    print(f"ACHTUNG: {fehler} Keys fehlen noch!")
print("=" * 100)

# Zusätzliche Prüfung: Alle PRICING-Keys
print("\nTEST 2: Vollständige PRICING-System Keys")
print("-" * 100)

pricing_keys = [
    "PRICING_NET_TOTAL",
    "PRICING_NET_TOTAL_FORMATTED",
    "PRICING_GROSS_TOTAL",
    "PRICING_GROSS_TOTAL_FORMATTED",
    "PRICING_HARDWARE_TOTAL",
    "PRICING_HARDWARE_TOTAL_FORMATTED",
    "PRICING_SERVICES_TOTAL",
    "PRICING_SERVICES_TOTAL_FORMATTED",
    "PRICING_VAT_AMOUNT",
    "PRICING_VAT_AMOUNT_FORMATTED",
]

pricing_erfolg = 0
for key in pricing_keys:
    if key in PLACEHOLDER_MAPPING:
        print(f"{key}")
        pricing_erfolg += 1
    else:
        print(f"{key} FEHLT!")

print(f"\nPRICING System: {pricing_erfolg}/{len(pricing_keys)} vollständig")

# Test 3: Alle FINAL_* Duplikate
print("\nTEST 3: FINAL_* Duplikate hinzugefügt?")
print("-" * 100)

final_duplikate = [
    "FINAL_ZUBEHOR_TOTAL",
    "FINAL_ZUBEHOR_TOTAL_FORMATTED",
    "FINAL_ZWISCHENSUMME_FINAL",
    "FINAL_ZWISCHENSUMME_FINAL_FORMATTED",
    "FINAL_MWST_IN_ZWISCHENSUMME",
    "FINAL_MWST_IN_ZWISCHENSUMME_FORMATTED",
]

final_erfolg = 0
for key in final_duplikate:
    if key in PLACEHOLDER_MAPPING:
        print(f"{key}")
        final_erfolg += 1
    else:
        print(f"{key} FEHLT!")

print(f"\nFINAL_* Duplikate: {final_erfolg}/{len(final_duplikate)} vorhanden")

print("\n" + "=" * 100)
print("GESAMT-STATISTIK:")
print("=" * 100)
print(f"Basis-Keys:         {erfolg}/{len(alle_keys)}")
print(f"PRICING System:     {pricing_erfolg}/{len(pricing_keys)}")
print(f"FINAL_* Duplikate:  {final_erfolg}/{len(final_duplikate)}")
print()

if fehler == 0 and pricing_erfolg == len(
        pricing_keys) and final_erfolg == len(final_duplikate):
    print(" PERFEKT! OPTION A VOLLSTÄNDIG IMPLEMENTIERT!")
else:
    print("Es fehlen noch einige Keys!")
