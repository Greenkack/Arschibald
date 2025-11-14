"""
Analyse-Skript: Welche Pricing-Keys werden wo verwendet?
Untersucht PLACEHOLDER_MAPPING und Code-Verwendung
"""

from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING
import os
import sys

sys.path.insert(0, 'c:/Users/win10/Desktop/Bokuk2')


print("=" * 100)
print("ANALYSE: PRICING-KEYS VERWENDUNG")
print("=" * 100)

# 1. ALTE KEYS (lowercase)
alte_keys = [
    "preis_mit_mwst",
    "zubehor_preis",
    "minus_rabatt",
    "plus_aufpreis",
    "zwischensumme_preis",
    "minus_mwst",
    "final_end_preis",
]

# 2. NEUE KEYS (UPPERCASE)
neue_keys = [
    "SIMPLE_KOMPONENTEN_SUMME",
    "SIMPLE_ENDERGEBNIS_BRUTTO",
    "SIMPLE_MWST_FORMATTED",
    "CALC_TOTAL_DISCOUNTS",
    "CALC_TOTAL_SURCHARGES",
    "FINAL_ZUBEHOR_TOTAL",
    "FINAL_ZWISCHENSUMME_FINAL",
    "FINAL_MWST_IN_ZWISCHENSUMME",
    "FINAL_END_PREIS",
    "PRICING_NET_TOTAL",
    "PRICING_GROSS_TOTAL",
    "PRICING_HARDWARE_TOTAL",
    "PRICING_SERVICES_TOTAL",
]

print("\n1. ALTE KEYS (lowercase) im PLACEHOLDER_MAPPING:")
print("-" * 100)
for key in alte_keys:
    if key in PLACEHOLDER_MAPPING:
        mapped_to = PLACEHOLDER_MAPPING[key]
        print(f"[OK] {key:30} -> {mapped_to}")
    else:
        print(f"[ERROR] {key:30} NICHT GEFUNDEN!")

print("\n2. NEUE KEYS (UPPERCASE) im PLACEHOLDER_MAPPING:")
print("-" * 100)
for key in neue_keys:
    if key in PLACEHOLDER_MAPPING:
        mapped_to = PLACEHOLDER_MAPPING[key]
        print(f"[OK] {key:40} -> {mapped_to}")
    else:
        print(f"[ERROR] {key:40} NICHT GEFUNDEN!")

# 3. Suche in Code-Dateien nach Verwendung
print("\n" + "=" * 100)
print("3. CODE-VERWENDUNG ANALYSE")
print("=" * 100)

files_to_check = [
    'solar_calculator.py',
    'pdf_template_engine/placeholders.py',
    'pdf_template_engine/dynamic_overlay.py',
]


def search_in_file(filepath, search_terms):
    """Sucht nach search_terms in einer Datei"""
    results = {}
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        for term in search_terms:
            matches = []
            for i, line in enumerate(lines, 1):
                if term in line and not line.strip().startswith('#'):
                    matches.append((i, line.strip()[:80]))
            if matches:
                results[term] = matches
    except Exception:
        pass

    return results


# Suche nach alten Keys
print("\n[FOLDER] Suche nach ALTEN KEYS (lowercase) in Code:")
print("-" * 100)
for filepath in files_to_check:
    full_path = f'c:/Users/win10/Desktop/Bokuk2/{filepath}'
    if not os.path.exists(full_path):
        continue

    results = search_in_file(full_path, alte_keys)
    if results:
        print(f"\n[SEARCH] {filepath}:")
        for term, matches in results.items():
            print(f"  {term}: {len(matches)} Verwendungen")
            if len(matches) <= 3:
                for line_num, line_text in matches:
                    print(f"    Zeile {line_num}: {line_text}")

# Suche nach neuen Keys
print("\n[FOLDER] Suche nach NEUEN KEYS (UPPERCASE) in Code:")
print("-" * 100)
for filepath in files_to_check:
    full_path = f'c:/Users/win10/Desktop/Bokuk2/{filepath}'
    if not os.path.exists(full_path):
        continue

    results = search_in_file(full_path, neue_keys)
    if results:
        print(f"\n[SEARCH] {filepath}:")
        for term, matches in results.items():
            print(f"  {term}: {len(matches)} Verwendungen")
            if len(matches) <= 3:
                for line_num, line_text in matches:
                    print(f"    Zeile {line_num}: {line_text}")

# 4. ÜBERSCHNEIDUNGEN
print("\n" + "=" * 100)
print("4. ÜBERSCHNEIDUNGS-ANALYSE")
print("=" * 100)

ueberschneidungen = [
    ("minus_rabatt", "CALC_TOTAL_DISCOUNTS", "Rabatte"),
    ("plus_aufpreis", "CALC_TOTAL_SURCHARGES", "Aufschläge"),
    ("zwischensumme_preis", "FINAL_ZWISCHENSUMME_FINAL", "Zwischensumme"),
    ("minus_mwst", "FINAL_MWST_IN_ZWISCHENSUMME", "MwSt (herausrechnen)"),
    ("zubehor_preis", "FINAL_ZUBEHOR_TOTAL", "Zubehör"),
    ("final_end_preis", "FINAL_END_PREIS", "Finaler Endpreis"),
]

print("\nMögliche Überschneidungen (Alt vs. Neu):")
print("-" * 100)
for alt, neu, beschreibung in ueberschneidungen:
    alt_exists = alt in PLACEHOLDER_MAPPING
    neu_exists = neu in PLACEHOLDER_MAPPING

    status = "[WARNING] BEIDE VORHANDEN" if alt_exists and neu_exists else "[OK] Kein Konflikt"
    print(f"{status}: {beschreibung}")
    print(f"  Alt: {alt:30} {'[OK]' if alt_exists else '[ERROR]'}")
    print(f"  Neu: {neu:40} {'[OK]' if neu_exists else '[ERROR]'}")
    print()

# 5. EMPFEHLUNG
print("\n" + "=" * 100)
print("5. EMPFEHLUNG")
print("=" * 100)

alte_in_use = sum(1 for key in alte_keys if key in PLACEHOLDER_MAPPING)
neue_in_use = sum(1 for key in neue_keys if key in PLACEHOLDER_MAPPING)

print("\n[CHART] Statistik:")
print(f"  Alte Keys (lowercase): {alte_in_use}/{len(alte_keys)} vorhanden")
print(f"  Neue Keys (UPPERCASE): {neue_in_use}/{len(neue_keys)} vorhanden")

if alte_in_use > 0 and neue_in_use > 0:
    print("\n[WARNING] PROBLEM: Beide Key-Systeme sind aktiv!")
    print(f"   → {alte_in_use} alte Keys im PLACEHOLDER_MAPPING")
    print(f"   → {neue_in_use} neue Keys im PLACEHOLDER_MAPPING")
    print("\n[IDEA] EMPFEHLUNG:")
    print("   Option 1: Alte Keys zu neuen mappen (Aliases)")
    print("   Option 2: Nur neue Keys verwenden, alte entfernen")
    print("   Option 3: Klare Trennung: alte für alte Logik, neue für neue")
else:
    print("\n[OK] Nur ein Key-System aktiv - kein Konflikt")

print("\n" + "=" * 100)
print("ANALYSE ABGESCHLOSSEN")
print("=" * 100)
