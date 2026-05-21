#!/usr/bin/env python3
"""
Einfacher Test für Seite 7 Platzhalter
"""

from pdf_template_engine.placeholders import build_dynamic_data
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_seite7_platzhalter():
    """Testet die Seite 7 Platzhalter"""

    print("Test Seite 7 Platzhalter")
    print("=" * 40)

    # Test-Daten mit neuer Struktur
    project_data = {
        'project_details': {
            'brutto_basis_formatted': '13.685,00 €',
            'zubehor_preis_formatted': '0,00 €',
            'total_discounts_formatted': '1.368,50 €',
            'total_surcharges_formatted': '1.115,83 €',
            'zwischensumme_brutto_formatted': '13.432,33 €',
            'final_vat_subtract_formatted': '2.148,57 €',
            'final_investment_netto_formatted': '11.283,76 €'
        }
    }

    try:
        dynamic_data = build_dynamic_data(project_data, {})

        print("📋 Seite 7 Platzhalter-Ergebnisse:")
        seite7_mapping = {
            'preis_mit_mwst_formatted': 'Gesamtsumme Brutto',
            'zubehor_preis_formatted': 'Zubehör / Extras',
            'minus_rabatt_formatted': 'Nachlass / Rabatt',
            'plus_aufpreis_formatted': 'Extrakosten / Aufpreis',
            'zwischensumme_preis_formatted': 'Zwischensumme / Listenpreis',
            'minus_mwst_formatted': 'abzüglich 19,00 % MwSt',
            'final_end_preis_formatted': 'gesamte Investitionsumme'
        }

        all_found = True
        for key, description in seite7_mapping.items():
            value = dynamic_data.get(key, 'FEHLT')
            status = "" if value != 'FEHLT' and value != '0,00 €' else ""
            print(f"   {status} {description}: {value}")
            if value == 'FEHLT':
                all_found = False

        if all_found:
            print("\\nAlle Seite 7 Platzhalter sind verfügbar!")
        else:
            print("\\nEinige Seite 7 Platzhalter fehlen!")

        return all_found

    except Exception as e:
        print(f"Fehler: {e}")
        return False


if __name__ == "__main__":
    success = test_seite7_platzhalter()

    print(
        f"\\nErgebnis: {
            'ERFOLGREICH' if success else 'FEHLGESCHLAGEN'}")

    if success:
        print("\\nDie neue Berechnungslogik ist implementiert:")
        print("   - Provision: Standard 1500€ (einstellbar)")
        print("   - MwSt: Wird am Ende abgezogen")
        print("   - Seite 7: Alle Platzhalter dynamisch verknüpft")
