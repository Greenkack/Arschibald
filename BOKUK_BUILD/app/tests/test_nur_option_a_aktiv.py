"""
FINAL TEST: Nur OPTION A Keys aktiv? (UPPERCASE)
Prüft ob ALLE alten lowercase Keys auskommentiert sind
"""

from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING
import sys

sys.path.insert(0, 'c:/Users/win10/Desktop/Bokuk2')


print("=" * 100)
print("FINAL TEST: NUR OPTION A KEYS AKTIV?")
print("=" * 100)

# ALTE Keys die NICHT mehr im PLACEHOLDER_MAPPING sein dürfen
alte_keys_lowercase = [
    "preis_mit_mwst",
    "zubehor_preis",
    "minus_rabatt",
    "plus_aufpreis",
    "zwischensumme_preis",
    "minus_mwst",
    "final_end_preis",  # lowercase!
]

# NEUE Keys die VORHANDEN sein müssen (OPTION A)
neue_keys_uppercase = [
    "SIMPLE_KOMPONENTEN_SUMME",
    "SIMPLE_KOMPONENTEN_SUMME_FORMATTED",
    "SIMPLE_ENDERGEBNIS_BRUTTO",
    "SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED",
    "SIMPLE_MWST_FORMATTED",
    "CALC_TOTAL_DISCOUNTS",
    "CALC_TOTAL_DISCOUNTS_FORMATTED",
    "CALC_TOTAL_SURCHARGES",
    "CALC_TOTAL_SURCHARGES_FORMATTED",
    "FINAL_ZUBEHOR_TOTAL",
    "FINAL_ZUBEHOR_TOTAL_FORMATTED",
    "FINAL_ZWISCHENSUMME_FINAL",
    "FINAL_ZWISCHENSUMME_FINAL_FORMATTED",
    "FINAL_MWST_IN_ZWISCHENSUMME",
    "FINAL_MWST_IN_ZWISCHENSUMME_FORMATTED",
    "FINAL_END_PREIS",  # UPPERCASE!
    "FINAL_END_PREIS_FORMATTED",
    "ERSPARTE_MEHRWERTSTEUER",
    "ERSPARTE_MEHRWERTSTEUER_FORMATTED",
    "VAT_SAVINGS",
    "VAT_SAVINGS_FORMATTED",
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

print("\n❌ TEST 1: Alte lowercase Keys MÜSSEN WEG sein!")
print("-" * 100)

fehler_alte = 0
for key in alte_keys_lowercase:
    if key in PLACEHOLDER_MAPPING:
        print(f"❌ FEHLER: {key:40} NOCH VORHANDEN! (muss auskommentiert sein)")
        fehler_alte += 1
    else:
        print(f"✅ OK: {key:40} korrekt auskommentiert")

print("\n✅ TEST 2: Neue UPPERCASE Keys MÜSSEN DA sein!")
print("-" * 100)

fehler_neue = 0
for key in neue_keys_uppercase:
    if key in PLACEHOLDER_MAPPING:
        print(f"✅ {key:50} -> {PLACEHOLDER_MAPPING[key]}")
    else:
        print(f"❌ FEHLER: {key:50} FEHLT!")
        fehler_neue += 1

print("\n" + "=" * 100)
print("ERGEBNIS:")
print("=" * 100)

if fehler_alte == 0:
    print(
        f"✅ Alle {
            len(alte_keys_lowercase)} alten lowercase Keys korrekt auskommentiert")
else:
    print(f"❌ {fehler_alte} alte Keys noch vorhanden!")

if fehler_neue == 0:
    print(f"✅ Alle {len(neue_keys_uppercase)} neuen UPPERCASE Keys vorhanden")
else:
    print(f"❌ {fehler_neue} neue Keys fehlen!")

print()

if fehler_alte == 0 and fehler_neue == 0:
    print("🎊 PERFEKT! NUR OPTION A KEYS AKTIV!")
    print("   ✅ Alle alten lowercase Keys auskommentiert")
    print("   ✅ Alle neuen UPPERCASE Keys aktiv")
    print("   ✅ Keine Duplikate mehr!")
else:
    print("⚠️ ES GIBT NOCH PROBLEME!")
    if fehler_alte > 0:
        print(
            f"   ❌ {fehler_alte} alte Keys müssen noch auskommentiert werden")
    if fehler_neue > 0:
        print(f"   ❌ {fehler_neue} neue Keys fehlen noch")

print("=" * 100)
