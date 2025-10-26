#!/usr/bin/env python3
"""
Test Script: Erstelle nur die fehlenden Keys für Rabatte, Aufpreise und Zwischensumme
"""

import sys

sys.path.append('.')


def test_create_discount_surcharge_keys():
    """Erstelle nur die Keys für Rabatte, Aufpreise und Zwischensumme"""

    try:
        from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory

        # Key Manager initialisieren
        key_manager = DynamicKeyManager()

        # Test-Daten für Rabatte, Aufpreise und Zwischensumme
        test_data = {
            # RABATTE KEYS
            "DISCOUNT_PERCENT": 10.0,
            "DISCOUNT_EURO": 500.0,
            "DISCOUNT_PERCENT_AMOUNT": 1000.0,
            "TOTAL_DISCOUNTS": 1500.0,
            "TOTAL_DISCOUNTS_FORMATTED": "1.500,00 €",

            # AUFPREISE KEYS
            "SURCHARGE_PERCENT": 5.0,
            "SURCHARGE_EURO": 200.0,
            "SURCHARGE_PERCENT_AMOUNT": 500.0,
            "TOTAL_SURCHARGES": 700.0,
            "TOTAL_SURCHARGES_FORMATTED": "700,00 €",

            # ZWISCHENSUMME KEYS
            "ZWISCHENSUMME": 15000.0,
            "ZWISCHENSUMME_FORMATTED": "15.000,00 €",
            "ZWISCHENSUMME_BRUTTO": 15000.0,
            "ZWISCHENSUMME_BRUTTO_FORMATTED": "15.000,00 €",
        }

        # Keys generieren
        keys = key_manager.generate_keys(
            test_data, prefix='CALC_', category=KeyCategory.PRICING)

        print("✅ RABATTE KEYS ERSTELLT:")
        for key, value in keys.items():
            if 'DISCOUNT' in key:
                print(f"  {key}: {value}")

        print("\n✅ AUFPREISE KEYS ERSTELLT:")
        for key, value in keys.items():
            if 'SURCHARGE' in key:
                print(f"  {key}: {value}")

        print("\n✅ ZWISCHENSUMME KEYS ERSTELLT:")
        for key, value in keys.items():
            if 'ZWISCHENSUMME' in key:
                print(f"  {key}: {value}")

        print(f"\n✅ INSGESAMT {len(keys)} KEYS ERFOLGREICH ERSTELLT!")

        # Keys in Session State Format für Solar Calculator
        session_state_keys = {
            # Rabatte
            "discount_percent": test_data["DISCOUNT_PERCENT"],
            "discount_euro": test_data["DISCOUNT_EURO"],
            "discount_percent_amount": test_data["DISCOUNT_PERCENT_AMOUNT"],
            "total_discounts": test_data["TOTAL_DISCOUNTS"],
            "total_discounts_formatted": test_data["TOTAL_DISCOUNTS_FORMATTED"],

            # Aufpreise
            "surcharge_percent": test_data["SURCHARGE_PERCENT"],
            "surcharge_euro": test_data["SURCHARGE_EURO"],
            "surcharge_percent_amount": test_data["SURCHARGE_PERCENT_AMOUNT"],
            "total_surcharges": test_data["TOTAL_SURCHARGES"],
            "total_surcharges_formatted": test_data["TOTAL_SURCHARGES_FORMATTED"],

            # Zwischensumme
            "zwischensumme": test_data["ZWISCHENSUMME"],
            "zwischensumme_formatted": test_data["ZWISCHENSUMME_FORMATTED"],
            "zwischensumme_brutto": test_data["ZWISCHENSUMME_BRUTTO"],
            "zwischensumme_brutto_formatted": test_data["ZWISCHENSUMME_BRUTTO_FORMATTED"],
        }

        print("\n✅ SESSION STATE KEYS FÜR SOLAR CALCULATOR:")
        for key, value in session_state_keys.items():
            print(f"  {key}: {value}")

        return keys, session_state_keys

    except ImportError as e:
        print(f"❌ FEHLER: Kann Key Manager nicht importieren: {e}")
        return None, None
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        return None, None


if __name__ == "__main__":
    print("🔧 ERSTELLE NUR KEYS FÜR RABATTE, AUFPREISE UND ZWISCHENSUMME")
    print("=" * 60)

    keys, session_keys = test_create_discount_surcharge_keys()

    if keys:
        print("\n🎯 KEYS ERFOLGREICH ERSTELLT UND BEREIT FÜR INTEGRATION!")
    else:
        print("\n❌ KEYS KONNTEN NICHT ERSTELLT WERDEN!")
