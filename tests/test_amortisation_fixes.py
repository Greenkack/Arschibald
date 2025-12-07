"""
TEST: Alle 3 Amortisations-Fixes
Prüft ob die Änderungen korrekt sind
"""

print("=" * 100)
print("TEST: AMORTISATIONS-FIXES")
print("=" * 100)

print("\nFIX 1: Alte Preis-Keys in calculations.py auskommentiert")
print("-" * 100)
print("Überprüfe calculations.py Zeile 3669-3691...")

with open('c:/Users/win10/Desktop/Bokuk2/calculations.py', encoding='utf-8') as f:
    lines = f.readlines()

# Check ob alte Keys auskommentiert sind
alte_keys_auskommentiert = True
for i, line in enumerate(lines[3668:3692], start=3669):
    if 'final_modified_price_net' in line and not line.strip().startswith('#'):
        print(f"Zeile {i}: final_modified_price_net NICHT auskommentiert!")
        alte_keys_auskommentiert = False
    if 'final_price_with_provision' in line and not line.strip().startswith('#'):
        print(f"Zeile {i}: final_price_with_provision NICHT auskommentiert!")
        alte_keys_auskommentiert = False
    if 'final_offer_price_net' in line and not line.strip().startswith('#'):
        print(f"Zeile {i}: final_offer_price_net NICHT auskommentiert!")
        alte_keys_auskommentiert = False

if alte_keys_auskommentiert:
    print("Alle alten Preis-Keys korrekt auskommentiert!")
else:
    print("Einige alte Keys noch aktiv!")

print("\nFIX 2: Fallback auf 'amortisationszeit_jahre' entfernt")
print("-" * 100)
print("Überprüfe placeholders.py Zeile 892-900...")

with open('c:/Users/win10/Desktop/Bokuk2/pdf_template_engine/placeholders.py', encoding='utf-8') as f:
    lines = f.readlines()

fallback_entfernt = True
for i, line in enumerate(lines[891:902], start=892):
    if 'amortisationszeit_jahre' in line and not line.strip().startswith('#'):
        print(f"Zeile {i}: amortisationszeit_jahre NOCH AKTIV!")
        fallback_entfernt = False

if fallback_entfernt:
    print("Fallback auf alten Key korrekt entfernt!")
else:
    print("Fallback noch aktiv!")

print("\nFIX 3: _calculate_amortization_time() Funktion ersetzt")
print("-" * 100)
print("Überprüfe analysis.py Zeile 403...")

with open('c:/Users/win10/Desktop/Bokuk2/analysis.py', encoding='utf-8') as f:
    lines = f.readlines()

funktion_gefixt = False
for i, line in enumerate(lines[400:410], start=401):
    if '_calculate_amortization_time' in line:
        if line.strip().startswith('#'):
            print(f"Zeile {i}: Alte Funktion korrekt auskommentiert")
            funktion_gefixt = True
        else:
            print(f"Zeile {i}: Alte Funktion NOCH AKTIV!")
            funktion_gefixt = False
            break
    if 'final_price / annual_savings' in line:
        print(f"Zeile {i}: Neue Direktberechnung gefunden!")
        funktion_gefixt = True

if funktion_gefixt:
    print("Funktion korrekt durch Direktberechnung ersetzt!")
else:
    print("Funktion noch aktiv oder Direktberechnung fehlt!")

print("\n" + "=" * 100)
print("GESAMT-ERGEBNIS:")
print("=" * 100)

alle_fixes_ok = alte_keys_auskommentiert and fallback_entfernt and funktion_gefixt

if alle_fixes_ok:
    print("\n ALLE 3 FIXES ERFOLGREICH!")
    print("\nFix 1: Alte Preis-Keys auskommentiert")
    print("Fix 2: Fallback auf alten Key entfernt")
    print("Fix 3: Nicht-existierende Funktion ersetzt")
    print("\nJETZT SOLLTE AMORTISATIONSZEIT KORREKT SEIN:")
    print("   → Verwendet nur noch FINAL_END_PREIS")
    print("   → Keine alten Keys mehr als Fallback")
    print("   → Keine nicht-existierende Funktion mehr")
else:
    print("\nEINIGE FIXES FEHLEN NOCH!")
    if not alte_keys_auskommentiert:
        print("   Fix 1 unvollständig")
    if not fallback_entfernt:
        print("   Fix 2 unvollständig")
    if not funktion_gefixt:
        print("   Fix 3 unvollständig")

print("\n" + "=" * 100)
