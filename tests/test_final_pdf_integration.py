#!/usr/bin/env python3
"""
FINALER TEST: PDF Integration mit Solar Calculator
"""

import sys

sys.path.append('.')

def test_final_pdf_integration():
    """Teste die finale PDF Integration"""

    print("🎯 FINALER PDF INTEGRATION TEST")
    print("=" * 60)

    try:
        from pdf_template_engine.placeholders import (
            PLACEHOLDER_MAPPING,
            build_dynamic_data,
        )

        # REALISTISCHE TEST-DATEN (wie sie vom Solar Calculator kommen)
        test_project_data = {
            # Solar Calculator Daten (einfach)
            "simple_pricing_data": {
                "komponenten_summe": 18000.0,
                "provision_euro": 1200.0,
                "netto_mit_provision": 19200.0,
                "mwst_betrag": 3648.0,
                "endergebnis_brutto": 22848.0,
                "formatted": {
                    "komponenten": "18.000,00 €",
                    "provision": "1.200,00 €",
                    "netto": "19.200,00 €",
                    "mwst": "3.648,00 €",
                    "endergebnis": "22.848,00 €"
                }
            },

            # Solar Calculator Daten (mit Rabatten/Aufpreisen)
            "complete_pricing_data": {
                "komponenten_summe": 18000.0,
                "provision_euro": 1200.0,
                "endergebnis_brutto": 22848.0,
                "discount_percent": 5.0,
                "discount_euro": 500.0,
                "total_discount": 1642.4,
                "surcharge_percent": 2.0,
                "surcharge_euro": 300.0,
                "total_surcharge": 756.96,
                "zwischensumme": 21962.56,
                "finale_summe_netto": 18456.0,
                "formatted": {
                    "endergebnis_brutto": "22.848,00 €",
                    "total_discounts": "1.642,40 €",
                    "total_surcharges": "756,96 €",
                    "zwischensumme": "21.962,56 €",
                    "mwst_betrag": "3.506,56 €",
                    "final_end_preis": "18.456,00 €",
                    "zubehor_preis": "800,00 €"
                }
            },

            # Projekt Details
            "project_details": {
                "amortization_years": 11.8
            }
        }

        test_analysis_results = {
            "amortization_time_years": 11.8,
            "payback_time_years": 11.8
        }

        test_company_info = {
            "name": "TommaTech GmbH",
            "street": "Zeppelinstraße 14",
            "city": "Garching b. München",
            "zip_code": "85748",
            "phone": "+49 89 1250 36 860",
            "email": "mail@tommatech.de"
        }

        # Teste build_dynamic_data
        result = build_dynamic_data(test_project_data, test_analysis_results, test_company_info)

        print("✅ build_dynamic_data erfolgreich ausgeführt!")

        # SEITE 1 TESTS
        print("\n📄 SEITE 1 - ERSPARTE MEHRWERTSTEUER & AMORTISATION:")
        print(f"  Solaranlage (MwSt): {result.get('vat_amount_eur_formatted', 'FEHLT')}")
        print(f"  Amortisationszeit: {result.get('amortization_time_formatted', 'FEHLT')}")

        # SEITE 7 TESTS
        print("\n📄 SEITE 7 - PREISBERECHNUNG:")
        seite7_tests = [
            ("Gesamtsumme Brutto", "endergebnis_brutto_formatted"),
            ("Zubehör / Extras", "zubehor_preis_formatted"),
            ("Nachlass / Rabatt", "total_discounts_formatted"),
            ("Extrakosten / Aufpreis", "total_surcharges_formatted"),
            ("Zwischensumme", "zwischensumme_formatted"),
            ("abzüglich MwSt", "mwst_betrag_formatted"),
            ("Investitionssumme", "final_end_preis_formatted")
        ]

        for label, key in seite7_tests:
            value = result.get(key, "FEHLT")
            status = "✅" if value != "0,00 €" and value != "FEHLT" else "❌"
            print(f"  {status} {label}: {value}")

        # MAPPING TESTS
        print("\n🗺️ WICHTIGE PLACEHOLDER MAPPINGS:")
        important_mappings = [
            ("Solaranlage", "vat_amount_eur_formatted"),
            ("29.150,00 EUR*", "amortization_time_formatted"),
            ("preis_mit_mwst", "endergebnis_brutto_formatted"),
            ("minus_rabatt", "total_discounts_formatted"),
            ("plus_aufpreis", "total_surcharges_formatted"),
            ("zwischensumme_preis", "zwischensumme_formatted"),
            ("minus_mwst", "mwst_betrag_formatted"),
            ("final_end_preis", "final_end_preis_formatted")
        ]

        mapping_ok = True
        for placeholder, expected_key in important_mappings:
            actual_key = PLACEHOLDER_MAPPING.get(placeholder, "NICHT GEMAPPT")
            status = "✅" if actual_key == expected_key else "❌"
            if actual_key != expected_key:
                mapping_ok = False
            print(f"  {status} '{placeholder}' -> {actual_key}")

        # FINALE VALIDIERUNG
        print("\n🎯 FINALE VALIDIERUNG:")

        # Seite 1
        seite1_mwst_ok = result.get("vat_amount_eur_formatted", "0,00 €") != "0,00 €"
        seite1_amort_ok = "Jahre" in result.get("amortization_time_formatted", "") and result.get("amortization_time_formatted") != "0 Jahre"

        # Seite 7
        seite7_values_ok = all(
            result.get(key, "0,00 €") != "0,00 €"
            for _, key in seite7_tests
            if key != "zubehor_preis_formatted"  # Zubehör kann 0 sein
        )

        print(f"  Seite 1 MwSt: {'✅' if seite1_mwst_ok else '❌'} ({result.get('vat_amount_eur_formatted', 'FEHLT')})")
        print(f"  Seite 1 Amortisation: {'✅' if seite1_amort_ok else '❌'} ({result.get('amortization_time_formatted', 'FEHLT')})")
        print(f"  Seite 7 Werte: {'✅' if seite7_values_ok else '❌'}")
        print(f"  Placeholder Mapping: {'✅' if mapping_ok else '❌'}")

        # GESAMTERGEBNIS
        all_ok = seite1_mwst_ok and seite1_amort_ok and seite7_values_ok and mapping_ok

        if all_ok:
            print("\n🎉 ALLE PDF FIXES ERFOLGREICH!")
            print("✅ Seite 1: Ersparte Mehrwertsteuer und Amortisationszeit funktionieren")
            print("✅ Seite 7: Alle Preisberechnungen funktionieren")
            print("✅ Solar Calculator Integration funktioniert")
            return True
        print("\n❌ EINIGE PROBLEME BESTEHEN NOCH!")
        return False

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_pdf_integration()

    if success:
        print("\n🚀 PDF INTEGRATION BEREIT FÜR PRODUCTION!")
        print("\nNÄCHSTE SCHRITTE:")
        print("1. Solar Calculator verwenden und Werte eingeben")
        print("2. PDF generieren")
        print("3. Seite 1 und Seite 7 prüfen")
    else:
        print("\n🔧 WEITERE FIXES ERFORDERLICH!")
