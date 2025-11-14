"""
VOLLSTÄNDIGE DUPLIKAT-ANALYSE
Sucht nach doppelten Berechnungen und Keys in der gesamten App
"""

import os
import re
from collections import defaultdict

print("=" * 120)
print("VOLLSTÄNDIGE DUPLIKAT-ANALYSE")
print("=" * 120)

# Alle Python-Dateien scannen
dateien = []
for root, dirs, files in os.walk('c:/Users/win10/Desktop/Bokuk2'):
    # Überspringe bestimmte Verzeichnisse
    if any(
        skip in root for skip in [
            '.git',
            '__pycache__',
            'venv',
            'env',
            'node_modules']):
        continue
    for file in files:
        if file.endswith('.py'):
            dateien.append(os.path.join(root, file))

print(f"\n[FOLDER] Analysiere {len(dateien)} Python-Dateien...")

# Suche nach verschiedenen Berechnungsmustern
berechnungsmuster = {
    'Endpreis': [
        r'final_end_preis\s*=',
        r'FINAL_END_PREIS\s*=',
        r'final_price\s*=',
        r'end_preis\s*=',
        r'endergebnis\s*=',
    ],
    'MwSt': [
        r'mwst\s*=.*\*\s*0\.19',
        r'vat\s*=.*\*\s*0\.19',
        r'tax\s*=.*\*\s*0\.19',
        r'mehrwertsteuer\s*=.*\*\s*0\.19',
    ],
    'Amortisation': [
        r'amortization.*=.*\/',
        r'amortisation.*=.*\/',
        r'payback.*=.*\/',
    ],
    'Rabatt': [
        r'discount\s*=',
        r'rabatt\s*=',
        r'minus_rabatt\s*=',
        r'DISCOUNT\s*=',
    ],
    'Aufschlag': [
        r'surcharge\s*=',
        r'aufschlag\s*=',
        r'plus_aufpreis\s*=',
        r'SURCHARGE\s*=',
    ],
    'Zwischensumme': [
        r'zwischensumme\s*=',
        r'subtotal\s*=',
        r'ZWISCHENSUMME\s*=',
    ],
    'Netto-Gesamt': [
        r'net_total\s*=',
        r'netto_total\s*=',
        r'komponenten_summe\s*=',
        r'NET_TOTAL\s*=',
    ],
    'Brutto-Gesamt': [
        r'gross_total\s*=',
        r'brutto_total\s*=',
        r'GROSS_TOTAL\s*=',
    ],
}

# Funde pro Kategorie
funde = defaultdict(list)

for datei in dateien:
    try:
        with open(datei, encoding='utf-8') as f:
            inhalt = f.read()
            zeilen = inhalt.split('\n')

            for kategorie, muster_liste in berechnungsmuster.items():
                for muster in muster_liste:
                    matches = re.finditer(muster, inhalt, re.IGNORECASE)
                    for match in matches:
                        # Finde Zeilennummer
                        zeile_nr = inhalt[:match.start()].count('\n') + 1
                        zeile_text = zeilen[zeile_nr - 1].strip()

                        # Überspringe Kommentare
                        if zeile_text.startswith('#'):
                            continue

                        rel_pfad = datei.replace(
                            'c:/Users/win10/Desktop/Bokuk2/', '')
                        funde[kategorie].append({
                            'datei': rel_pfad,
                            'zeile': zeile_nr,
                            'code': zeile_text[:100]
                        })
    except Exception:
        pass

# Ausgabe der Funde
print("\n" + "=" * 120)
print("ERGEBNISSE - DUPLIKATE PRO KATEGORIE")
print("=" * 120)

gesamt_duplikate = 0

for kategorie in sorted(berechnungsmuster.keys()):
    anzahl = len(funde[kategorie])
    if anzahl > 1:  # Nur wenn es Duplikate gibt
        gesamt_duplikate += anzahl
        print(f"\n[SEARCH] {kategorie.upper()}: {anzahl} Berechnungen gefunden")
        print("-" * 120)

        # Gruppiere nach Datei
        nach_datei = defaultdict(list)
        for fund in funde[kategorie]:
            nach_datei[fund['datei']].append(fund)

        for datei, fund_liste in sorted(nach_datei.items()):
            print(f"\n[FILE] {datei}:")
            for fund in fund_liste[:5]:  # Max 5 pro Datei
                print(f"   Zeile {fund['zeile']:5}: {fund['code']}")
            if len(fund_liste) > 5:
                print(f"   ... und {len(fund_liste) - 5} weitere")

# Suche nach doppelten Keys in session_state
print("\n" + "=" * 120)
print("SESSION STATE KEYS ANALYSE")
print("=" * 120)

session_state_keys = defaultdict(list)

for datei in dateien:
    try:
        with open(datei, encoding='utf-8') as f:
            inhalt = f.read()
            zeilen = inhalt.split('\n')

            # Suche nach session_state Zuweisungen
            matches = re.finditer(
                r'st\.session_state\[[\'"]([^\'"]+)[\'"]\]\s*=', inhalt)
            for match in matches:
                key = match.group(1)
                zeile_nr = inhalt[:match.start()].count('\n') + 1
                zeile_text = zeilen[zeile_nr - 1].strip()

                if not zeile_text.startswith('#'):
                    rel_pfad = datei.replace(
                        'c:/Users/win10/Desktop/Bokuk2/', '')
                    session_state_keys[key].append({
                        'datei': rel_pfad,
                        'zeile': zeile_nr,
                        'code': zeile_text[:80]
                    })
    except BaseException:
        pass

print(f"\n[CHART] Gefundene Session State Keys: {len(session_state_keys)}")

# Keys die mehrfach gesetzt werden
mehrfach_keys = {k: v for k, v in session_state_keys.items() if len(v) > 3}

if mehrfach_keys:
    print("\n[WARNING] Keys die in >3 Dateien gesetzt werden (potenzielle Konflikte):")
    print("-" * 120)
    for key, locations in sorted(
        mehrfach_keys.items(), key=lambda x: len(
            x[1]), reverse=True)[
            :10]:
        print(f"\n'{key}': {len(locations)} Zuweisungen")
        datei_set = set(loc['datei'] for loc in locations)
        for datei in sorted(datei_set)[:5]:
            count = sum(1 for loc in locations if loc['datei'] == datei)
            print(f"   • {datei} ({count}x)")
        if len(datei_set) > 5:
            print(f"   ... und {len(datei_set) - 5} weitere Dateien")

# Suche nach ähnlichen Berechnungsformeln
print("\n" + "=" * 120)
print("ÄHNLICHE FORMELN (POTENZIELLE DUPLIKATE)")
print("=" * 120)

formeln = []
for datei in dateien:
    try:
        with open(datei, encoding='utf-8') as f:
            zeilen = f.readlines()

            for i, zeile in enumerate(zeilen, 1):
                # Suche nach Division (Amortisation)
                if re.search(r'=.*\s*/\s*',
                             zeile) and not zeile.strip().startswith('#'):
                    if any(word in zeile.lower()
                           for word in ['amort', 'payback', 'jahre', 'years']):
                        rel_pfad = datei.replace(
                            'c:/Users/win10/Desktop/Bokuk2/', '')
                        formeln.append({
                            'typ': 'Division (Amortisation?)',
                            'datei': rel_pfad,
                            'zeile': i,
                            'code': zeile.strip()[:100]
                        })

                # Suche nach Multiplikation mit 0.19 (MwSt)
                if re.search(r'\*\s*0\.19',
                             zeile) and not zeile.strip().startswith('#'):
                    rel_pfad = datei.replace(
                        'c:/Users/win10/Desktop/Bokuk2/', '')
                    formeln.append({
                        'typ': 'MwSt (× 0.19)',
                        'datei': rel_pfad,
                        'zeile': i,
                        'code': zeile.strip()[:100]
                    })
    except BaseException:
        pass

# Gruppiere nach Typ
nach_typ = defaultdict(list)
for formel in formeln:
    nach_typ[formel['typ']].append(formel)

for typ, formel_liste in sorted(nach_typ.items()):
    if len(formel_liste) > 1:
        print(f"\n🔢 {typ}: {len(formel_liste)} Vorkommen")
        print("-" * 120)

        # Gruppiere nach Datei
        nach_datei = defaultdict(list)
        for formel in formel_liste:
            nach_datei[formel['datei']].append(formel)

        for datei, form_liste in sorted(nach_datei.items())[:10]:
            print(f"\n[FILE] {datei}: {len(form_liste)} Vorkommen")
            for form in form_liste[:3]:
                print(f"   Zeile {form['zeile']:5}: {form['code']}")
            if len(form_liste) > 3:
                print(f"   ... und {len(form_liste) - 3} weitere")

        if len(nach_datei) > 10:
            print(f"\n   ... und {len(nach_datei) - 10} weitere Dateien")

print("\n" + "=" * 120)
print("ZUSAMMENFASSUNG")
print("=" * 120)

print("\n[CHART] Statistik:")
print(f"   • Analysierte Dateien: {len(dateien)}")
print(f"   • Gefundene Berechnungs-Kategorien: {len(berechnungsmuster)}")
print(f"   • Gesamt potenzielle Duplikate: {gesamt_duplikate}")
print(f"   • Session State Keys: {len(session_state_keys)}")
print(f"   • Mehrfach gesetzte Keys (>3 Dateien): {len(mehrfach_keys)}")

print("\n[IDEA] EMPFEHLUNG:")
if gesamt_duplikate > 50:
    print("   [WARNING] VIELE DUPLIKATE GEFUNDEN!")
    print("   → Konsolidierung empfohlen")
elif gesamt_duplikate > 20:
    print("   [WARNING] Einige Duplikate vorhanden")
    print("   → Review empfohlen")
else:
    print("   [OK] Wenige Duplikate - akzeptabel")

print("\n" + "=" * 120)
print("ANALYSE ABGESCHLOSSEN")
print("=" * 120)
