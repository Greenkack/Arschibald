#!/usr/bin/env python3
"""
Test Script: Teste die PDF Platzhalter Fixes
"""

import sys

sys.path.append('.')

def test_pdf_fixes():
    """Teste die PDF Platzhalter Fixes"""

    print("🔧 TESTE PDF PLATZHALTER FIXES")
    print("=" * 50)

    try:
        from pdf_template_engine.placeholders import (
            PLACEHOLDER_MAPPING,
            build_dynamic_data,
        )

        # Test Daten erstellen (simuliert Solar Calculator Session State)
        test_project_data = {
            "simple_pricing_data": {
                "komponenten_summe": 20000.0,
                "provision_euro": 1000.0,
                "endergebnis_brutto": 21000.0,
                "total_discounts": 1500.0,
                "total_surcharges": 700.0,
                "zubehor_preis": 800.0,
                "extra_dienstleistungen": 500.0,
                "zwischensumme": 20500.0,
                "mwst_betrag": 3273.11,
                "final_end_preis": 17226.89,
                "formatted": {
                    "endergebnis_brutto": "21.000,00 €",
                    "total_discounts": "1.500,00 €",
                    "total_surcharges": "700,00 €",
                    "zubehor_preis": "800,00 €",
                    "extra_dienstleistungen": "500,00 €",
                    "zwischensumme": "20.500,00 €",
                    "mwst_betrag": "3.273,11 €",
                    "final_end_preis": "17.226,89 €"
                }
            }
        }

        test_analysis_results = {
            "amortization_time_years": 12.5
        }

        test_company_info = {
            "name": "Test GmbH"
        }

        # Teste build_dynamic_data
        result = build_dynamic_data(test_project_data, test_analysis_results, test_company_info)

        print("✅ build_dynamic_data erfolgreich ausgeführt!")

        # Teste Seite 1 Fixes
        print("\n📄 SEITE 1 FIXES:")
        seite1_keys = ["vat_amount_eur_formatted", "amortization_time_formatted"]
        for key in seite1_keys:
            value = result.get(key, "FEHLT")
            print(f"  {key}: {value}")

        # Teste Seite 7 Fixes
        print("\n📄 SEITE 7 FIXES:")
        seite7_keys = [
            "endergebnis_brutto_formatted",
            "zubehor_preis_formatted",
            "total_discounts_formatted",
            "total_surcharges_formatted",
            "zwischensumme_formatted",
            "mwst_betrag_formatted",
            "final_end_preis_formatted"
        ]
        for key in seite7_keys:
            value = result.get(key, "FEHLT")
            print(f"  {key}: {value}")

        # Teste PLACEHOLDER_MAPPING
        print("\n🗺️ PLACEHOLDER_MAPPING TESTS:")
        test_placeholders = [
            "ersparte Mehrwertsteuer",
            "29.150,00 EUR*",
            "preis_mit_mwst",
            "zubehor_preis",
            "minus_rabatt",
            "plus_aufpreis",
            "zwischensumme_preis",
            "minus_mwst",
            "final_end_preis"
        ]

        for placeholder in test_placeholders:
            mapped_key = PLACEHOLDER_MAPPING.get(placeholder, "NICHT GEMAPPT")
            print(f"  '{placeholder}' -> {mapped_key}")

        # Validierung
        print("\n✅ VALIDIERUNG:")

        # Seite 1 Validierung
        vat_ok = result.get("vat_amount_eur_formatted") != "0,00 €"
        amort_ok = "Jahre" in result.get("amortization_time_formatted", "")
        print(f"  Seite 1 MwSt: {'✅' if vat_ok else '❌'}")
        print(f"  Seite 1 Amortisation: {'✅' if amort_ok else '❌'}")

        # Seite 7 Validierung
        seite7_ok = all(result.get(key, "0,00 €") != "0,00 €" for key in seite7_keys)
        print(f"  Seite 7 Werte: {'✅' if seite7_ok else '❌'}")

        # Mapping Validierung
        mapping_ok = all(PLACEHOLDER_MAPPING.get(p) for p in test_placeholders)
        print(f"  Placeholder Mapping: {'✅' if mapping_ok else '❌'}")

        if vat_ok and amort_ok and seite7_ok and mapping_ok:
            print("\n🎉 ALLE TESTS ERFOLGREICH!")
            return True
        print("\n❌ EINIGE TESTS FEHLGESCHLAGEN!")
        return False

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_fixes()
    if success:
        print("\n✅ PDF FIXES BEREIT FÜR PRODUCTION!")
    else:
        print("\n❌ PDF FIXES BENÖTIGEN WEITERE ARBEIT!")
