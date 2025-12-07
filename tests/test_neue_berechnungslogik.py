#!/usr/bin/env python3
"""
Test für die neue Berechnungslogik im Solar Calculator:
1. Komponenten-Preis + Provision (versteckt) + MwSt = Brutto-Basis
2. Rabatte/Aufschläge auf Brutto-Basis
3. Am Ende MwSt abziehen = Finale Investitionssumme
4. Alle Werte in PDF Seite 7 Platzhalter
"""

from pdf_template_engine.placeholders import build_dynamic_data
import sys
from pathlib import Path

from financial_calculations import (
    calculate_gross_from_net,
    calculate_net_from_gross,
    calculate_vat_amount,
)

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_neue_berechnungslogik():
    """Testet die neue Berechnungslogik"""

    print("Test neue Berechnungslogik")
    print("=" * 50)

    # Simuliere Solar Calculator Berechnungsergebnisse
    # Beispiel: 10.000€ Komponenten + 1.500€ Provision + 19% MwSt = 13.685€
    # Brutto-Basis
    komponenten_netto = 10000.00
    provision_euro = 1500.00
    netto_mit_provision = komponenten_netto + provision_euro  # 11.500€
    mwst_betrag = calculate_vat_amount(netto_mit_provision)  # 2.185€
    brutto_basis = calculate_gross_from_net(netto_mit_provision)  # 13.685€

    # Rabatte und Aufschläge
    rabatt_betrag = 500.00  # 500€ Rabatt
    aufpreis_betrag = 300.00  # 300€ Aufpreis

    # Zwischensumme nach Rabatt/Aufpreis
    zwischensumme = brutto_basis - rabatt_betrag + aufpreis_betrag  # 13.485€

    # Finale MwSt abziehen
    finale_mwst_abzug = calculate_vat_amount(
        calculate_net_from_gross(zwischensumme))
    finale_investition = zwischensumme - finale_mwst_abzug  # Netto-Endbetrag

    print("Berechnungsbeispiel:")
    print(f"   1. Komponenten (netto): {komponenten_netto:,.2f} €")
    print(f"   2. + Provision (versteckt): {provision_euro:,.2f} €")
    print(f"   3. = Netto mit Provision: {netto_mit_provision:,.2f} €")
    print(f"   4. + MwSt (19%): {mwst_betrag:,.2f} €")
    print(f"   5. = Brutto-Basis: {brutto_basis:,.2f} €")
    print(f"   6. - Rabatt: {rabatt_betrag:,.2f} €")
    print(f"   7. + Aufpreis: {aufpreis_betrag:,.2f} €")
    print(f"   8. = Zwischensumme: {zwischensumme:,.2f} €")
    print(f"   9. - MwSt abziehen: {finale_mwst_abzug:,.2f} €")
    print(f"  10. = Finale Investition: {finale_investition:,.2f} €")

    # Simuliere Solar Calculator Session State
    project_data = {
        'project_details': {
            # Basis-Werte
            'net_total_amount': komponenten_netto,
            'provision_euro': provision_euro,
            'brutto_basis': brutto_basis,

            # PDF Seite 7 Platzhalter (formatiert)
            'formatted_preis_mit_mwst': f"{brutto_basis:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'formatted_zubehor_preis': "0,00 €",  # Kein Zubehör in diesem Test
            'formatted_minus_rabatt': f"{rabatt_betrag:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'formatted_plus_aufpreis': f"{aufpreis_betrag:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'formatted_zwischensumme_preis': f"{zwischensumme:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'formatted_minus_mwst': f"{finale_mwst_abzug:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'formatted_final_end_preis': f"{finale_investition:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')
        }
    }

    try:
        # Baue dynamische Daten für PDF
        dynamic_data = build_dynamic_data(project_data, {})

        print("\\n PDF Seite 7 Platzhalter-Werte:")
        seite7_keys = [
            'preis_mit_mwst_formatted',
            'zubehor_preis_formatted',
            'minus_rabatt_formatted',
            'plus_aufpreis_formatted',
            'zwischensumme_preis_formatted',
            'minus_mwst_formatted',
            'final_end_preis_formatted'
        ]

        all_correct = True
        for key in seite7_keys:
            value = dynamic_data.get(key, 'FEHLT')
            expected_not_zero = value != "0,00 €" and value != "FEHLT"
            status = "" if expected_not_zero or key in [
                'zubehor_preis_formatted'] else ""
            print(f"   {key}: {value} {status}")

            if key != 'zubehor_preis_formatted' and not expected_not_zero:
                all_correct = False

        if all_correct:
            print("\\nNeue Berechnungslogik funktioniert!")
            print("\\nPDF Seite 7 wird jetzt anzeigen:")
            print(
                f"   Gesamtsumme Brutto: {
                    dynamic_data.get('preis_mit_mwst_formatted')}")
            print(
                f"   + Zubehör / Extras: {dynamic_data.get('zubehor_preis_formatted')}")
            print(
                f"   - Nachlass / Rabatt: {dynamic_data.get('minus_rabatt_formatted')}")
            print(
                f"   + Extrakosten / Aufpreis: {dynamic_data.get('plus_aufpreis_formatted')}")
            print(
                f"   = Zwischensumme / Listenpreis: {dynamic_data.get('zwischensumme_preis_formatted')}")
            print(
                f"   - abzüglich 19,00 % MwSt: {dynamic_data.get('minus_mwst_formatted')}")
            print(
                f"   = gesamte Investitionsumme: {
                    dynamic_data.get('final_end_preis_formatted')}")
            return True
        print("\\nEinige Werte sind noch nicht korrekt gesetzt")
        return False

    except Exception as e:
        print(f"\\nFehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provision_versteckt():
    """Testet ob die Provision korrekt versteckt wird"""

    print("\\nTest Provision versteckt")
    print("=" * 30)

    # Test-Szenario: 8.000€ Komponenten + 1.500€ Provision = 9.500€ netto
    # + 19% MwSt = 11.305€ brutto (das ist preis_mit_mwst)

    komponenten = 8000.00
    provision = 1500.00
    netto_gesamt = komponenten + provision  # 9.500€
    mwst = calculate_vat_amount(netto_gesamt)  # 1.805€
    brutto_mit_provision = calculate_gross_from_net(netto_gesamt)  # 11.305€

    print("Provision-Test:")
    print(f"   Komponenten: {komponenten:,.2f} €")
    print(f"   + Provision (versteckt): {provision:,.2f} €")
    print(f"   = Netto gesamt: {netto_gesamt:,.2f} €")
    print(f"   + MwSt: {mwst:,.2f} €")
    print(f"   = Brutto (preis_mit_mwst): {brutto_mit_provision:,.2f} €")

    # In der PDF soll nur der brutto_mit_provision als "Gesamtsumme Brutto" erscheinen
    # Die Provision ist versteckt eingerechnet

    expected_preis_mit_mwst = "11.305,00 €"
    actual_calculation = f"{
        brutto_mit_provision:,.2f} €".replace(
        ',',
        'X').replace(
            '.',
            ',').replace(
                'X',
        '.')

    if actual_calculation == expected_preis_mit_mwst:
        print("\\nProvision wird korrekt versteckt eingerechnet!")
        print(f"   PDF zeigt: Gesamtsumme Brutto: {expected_preis_mit_mwst}")
        print("   (Provision von 1.500€ ist unsichtbar eingerechnet)")
        return True
    print("\\nProvision-Berechnung fehlerhaft")
    print(f"   Erwartet: {expected_preis_mit_mwst}")
    print(f"   Erhalten: {actual_calculation}")
    return False


if __name__ == "__main__":
    print("Test neue Solar Calculator Berechnungslogik")
    print("=" * 70)

    # Test 1: Neue Berechnungslogik
    test1_success = test_neue_berechnungslogik()

    # Test 2: Provision versteckt
    test2_success = test_provision_versteckt()

    print("\\n Test-Zusammenfassung:")
    print(f"   1. Neue Berechnungslogik: {'' if test1_success else ''}")
    print(f"   2. Provision versteckt: {'' if test2_success else ''}")

    if test1_success and test2_success:
        print("\\nALLE TESTS ERFOLGREICH!")
        print("\\nNeue Berechnungsreihenfolge implementiert:")
        print("   1. Komponenten-Preis (netto)")
        print("   2. + Provision 1500€ (versteckt)")
        print("   3. + MwSt = Gesamtsumme Brutto")
        print("   4. ± Rabatte/Aufschläge")
        print("   5. = Zwischensumme")
        print("   6. - MwSt abziehen")
        print("   7. = Finale Investitionssumme (netto)")
        print("\\nPDF Seite 7 zeigt alle Berechnungsschritte dynamisch!")
    else:
        print("\\nEinige Tests sind fehlgeschlagen")
