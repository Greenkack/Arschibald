#!/usr/bin/env python3
"""
Test mit realistischen Daten wie sie aus der App kommen
"""

import sys

sys.path.append('.')

def test_realistic_pdf_data():
    """Teste mit realistischen Daten aus Solar Calculator"""

    print("TEST MIT REALISTISCHEN DATEN")
    print("=" * 60)

    try:
        from pdf_template_engine.placeholders import (
            build_dynamic_data,
        )

        # REALISTISCHE DATEN wie sie aus Solar Calculator kommen
        test_project_data = {
            "simple_pricing_data": {
                "mwst_betrag": 3515.0,  # Für Seite 1 MwSt
                "formatted": {
                    "endergebnis_brutto": "21.420,00 €",
                    "zubehor_preis": "800,00 €",
                    "total_discounts": "1.500,00 €",
                    "total_surcharges": "700,00 €",
                    "zwischensumme": "21.420,00 €",
                    "mwst_betrag": "3.420,00 €",
                    "final_end_preis": "18.000,00 €"
                }
            },
            "project_details": {
                # Solar Calculator finale Preise
                "final_offer_price_net": 18500.0,
                "final_price_with_provision": 19500.0,
                "formatted_final_modified_vat_amount": "3.515,00 €",
            }
        }

        test_analysis_results = {
            # Basis für Seite 7
            "total_investment_netto": 17000.0,
            "provision_euro": 1000.0,

            # Seite 1 - Amortisationszeit
            "amortization_time_years": 12.5,
        }

        test_company_info = {
            "name": "Test GmbH"
        }

        # Teste build_dynamic_data
        result = build_dynamic_data(test_project_data, test_analysis_results, test_company_info)

        print("build_dynamic_data erfolgreich ausgeführt!")

        # Teste die 3 kritischen Werte
        print("\\nDIE 3 KRITISCHEN WERTE:")
        print(f"  1. vat_amount_eur: {result.get('vat_amount_eur', 'FEHLT')}")
        print(f"  2. amortization_time: {result.get('amortization_time', 'FEHLT')}")
        print(f"  3. preis_mit_mwst_formatted: {result.get('preis_mit_mwst_formatted', 'FEHLT')}")

        # Teste alle Seite 7 Werte
        print("\\nSEITE 7 ALLE WERTE:")
        seite7_keys = [
            "preis_mit_mwst_formatted",
            "minus_rabatt_formatted",
            "plus_aufpreis_formatted",
            "zubehor_preis_formatted",
            "zwischensumme_preis_formatted",
            "minus_mwst_formatted",
            "final_end_preis_formatted"
        ]

        for key in seite7_keys:
            value = result.get(key, "FEHLT")
            print(f"  {key}: {value}")

        # Validierung
        print("\\nVALIDIERUNG:")

        # 1. MwSt (sollte aus simple_pricing_data.mwst_betrag kommen)
        vat_ok = result.get("vat_amount_eur_formatted") == "3.515,00 €"
        print(f"  1. MwSt: {'' if vat_ok else ''} ({result.get('vat_amount_eur_formatted', 'FEHLT')})")

        # 2. Amortisationszeit (sollte aus amortization_time_years kommen)
        amort_ok = result.get("amortization_time") == "12,50 Jahre"
        print(f"  2. Amortisation: {'' if amort_ok else ''} ({result.get('amortization_time', 'FEHLT')})")

        # 3. Seite 7 Werte (sollten berechnet werden) - prüfe die gemappten Keys
        seite7_mapped_keys = [
            "endergebnis_brutto_formatted",
            "total_discounts_formatted",
            "total_surcharges_formatted",
            "zubehor_preis_formatted",
            "zwischensumme_formatted",
            "mwst_betrag_formatted",
            "final_end_preis_formatted"
        ]
        seite7_ok = all(result.get(key) and result.get(key) != "0,00 €" for key in seite7_mapped_keys)
        print(f"  3. Seite 7: {'' if seite7_ok else ''}")

        if vat_ok and amort_ok and seite7_ok:
            print("\\n ALLE 3 PROBLEME GELÖST!")
            return True
        print("\\nPROBLEME BESTEHEN NOCH!")
        return False

    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_realistic_pdf_data()
    if success:
        print("\\nPDF FIXES ERFOLGREICH!")
    else:
        print("\\nPDF FIXES BENÖTIGEN WEITERE ARBEIT!")
