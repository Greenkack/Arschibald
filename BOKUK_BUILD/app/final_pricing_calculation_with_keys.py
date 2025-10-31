#!/usr/bin/env python3
"""
FINALE PREISBERECHNUNG MIT ALLEN KEYS FÜR PDF INTEGRATION

Berechnung:
SIMPLE_ENDERGEBNIS_BRUTTO
+ CALC__TOTAL_DISCOUNTS_FORMATTED
+ CALC__TOTAL_SURCHARGES_FORMATTED
+ Key_für_zubehör_im_solarcalcutor
+ key_für_extra_dienstleistungen
= key_für_zwischensumme
- SIMPLE_MWST_FORMATTED
= final_end_preis
"""

import sys

sys.path.append('.')


def create_final_pricing_calculation():
    """Erstelle die finale Preisberechnung mit allen notwendigen Keys"""

    try:
        from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory

        # Key Manager initialisieren
        key_manager = DynamicKeyManager()

        # BEISPIEL-WERTE FÜR DIE BERECHNUNG
        endergebnis_brutto = 20000.0  # SIMPLE_ENDERGEBNIS_BRUTTO
        total_discounts = -1500.0    # CALC__TOTAL_DISCOUNTS (negativ = Abzug)
        # CALC__TOTAL_SURCHARGES (positiv = Aufschlag)
        total_surcharges = 700.0
        zubehor_preis = 800.0        # Key für Zubehör im Solar Calculator
        extra_dienstleistungen = 500.0  # Key für Extra-Dienstleistungen

        # ZWISCHENSUMME BERECHNEN
        zwischensumme = (endergebnis_brutto +
                         total_discounts +
                         total_surcharges +
                         zubehor_preis +
                         extra_dienstleistungen)

        # MWST BERECHNEN (19%)
        mwst_betrag = zwischensumme * 0.19 / 1.19  # MwSt aus Bruttobetrag

        # FINAL END PREIS (NETTO)
        final_end_preis = zwischensumme - mwst_betrag

        # FORMATIERUNG
        def format_currency(amount):
            return f"{
                amount:,.2f} €".replace(
                ",",
                "X").replace(
                ".",
                ",").replace(
                "X",
                ".")

        # ALLE KEYS ERSTELLEN
        final_pricing_keys = {
            # BASIS WERTE
            "SIMPLE_ENDERGEBNIS_BRUTTO": endergebnis_brutto,
            "SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED": format_currency(endergebnis_brutto),

            # RABATTE UND AUFPREISE
            "CALC_TOTAL_DISCOUNTS": total_discounts,
            # Positiv anzeigen
            "CALC_TOTAL_DISCOUNTS_FORMATTED": format_currency(abs(total_discounts)),
            "CALC_TOTAL_SURCHARGES": total_surcharges,
            "CALC_TOTAL_SURCHARGES_FORMATTED": format_currency(total_surcharges),

            # ZUBEHÖR UND DIENSTLEISTUNGEN
            "SOLAR_CALC_ZUBEHOR_PREIS": zubehor_preis,
            "SOLAR_CALC_ZUBEHOR_PREIS_FORMATTED": format_currency(zubehor_preis),
            "SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN": extra_dienstleistungen,
            "SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN_FORMATTED": format_currency(extra_dienstleistungen),

            # ZWISCHENSUMME
            "CALC_ZWISCHENSUMME": zwischensumme,
            "CALC_ZWISCHENSUMME_FORMATTED": format_currency(zwischensumme),

            # MWST
            "SIMPLE_MWST_BETRAG": mwst_betrag,
            "SIMPLE_MWST_FORMATTED": format_currency(mwst_betrag),

            # FINAL END PREIS
            "FINAL_END_PREIS": final_end_preis,
            "FINAL_END_PREIS_FORMATTED": format_currency(final_end_preis),
        }

        # Keys mit Key Manager generieren
        generated_keys = key_manager.generate_keys(
            final_pricing_keys, prefix='PDF_', category=KeyCategory.PRICING)

        print("🧮 FINALE PREISBERECHNUNG:")
        print("=" * 50)
        print(
            f"SIMPLE_ENDERGEBNIS_BRUTTO:     {
                format_currency(endergebnis_brutto)}")
        print(
            f"- Rabatte:                     -{format_currency(abs(total_discounts))}")
        print(
            f"+ Aufpreise:                   +{format_currency(total_surcharges)}")
        print(
            f"+ Zubehör:                     +{format_currency(zubehor_preis)}")
        print(
            f"+ Extra Dienstleistungen:      +{format_currency(extra_dienstleistungen)}")
        print("-" * 50)
        print(
            f"= ZWISCHENSUMME:               {
                format_currency(zwischensumme)}")
        print(
            f"- MwSt (19%):                  -{format_currency(mwst_betrag)}")
        print("=" * 50)
        print(
            f"= FINAL END PREIS (NETTO):     {
                format_currency(final_end_preis)}")

        print("\n🔑 GENERIERTE KEYS FÜR PDF:")
        print("=" * 50)
        for key, value in generated_keys.items():
            print(f"{key}: {value}")

        # PDF BYTES ERSTELLEN
        import json
        pdf_data = {
            "calculation_type": "final_pricing_with_discounts_surcharges",
            "timestamp": "2024-01-01T00:00:00",
            "values": final_pricing_keys,
            "keys": generated_keys,
            "formula": "ENDERGEBNIS_BRUTTO + DISCOUNTS + SURCHARGES + ZUBEHOR + DIENSTLEISTUNGEN = ZWISCHENSUMME - MWST = FINAL_END_PREIS"
        }

        pdf_bytes = json.dumps(
            pdf_data,
            ensure_ascii=False,
            indent=2).encode('utf-8')

        print(f"\n📄 PDF BYTES ERSTELLT: {len(pdf_bytes)} bytes")

        # SESSION STATE FORMAT FÜR SOLAR CALCULATOR
        session_state_data = {
            "endergebnis_brutto": endergebnis_brutto,
            "total_discounts": abs(total_discounts),  # Positiv für Anzeige
            "total_surcharges": total_surcharges,
            "zubehor_preis": zubehor_preis,
            "extra_dienstleistungen": extra_dienstleistungen,
            "zwischensumme": zwischensumme,
            "mwst_betrag": mwst_betrag,
            "final_end_preis": final_end_preis,
            "formatted": {
                "endergebnis_brutto": format_currency(endergebnis_brutto),
                "total_discounts": format_currency(abs(total_discounts)),
                "total_surcharges": format_currency(total_surcharges),
                "zubehor_preis": format_currency(zubehor_preis),
                "extra_dienstleistungen": format_currency(extra_dienstleistungen),
                "zwischensumme": format_currency(zwischensumme),
                "mwst_betrag": format_currency(mwst_betrag),
                "final_end_preis": format_currency(final_end_preis)
            }
        }

        return generated_keys, pdf_bytes, session_state_data

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        return None, None, None


def create_pdf_placeholder_mapping():
    """Erstelle Mapping für PDF Platzhalter"""

    placeholder_mapping = {
        # SEITE 7 PLATZHALTER
        "preis_mit_mwst": "PDF__SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED",
        "minus_rabatt": "PDF__CALC_TOTAL_DISCOUNTS_FORMATTED",
        "plus_aufpreis": "PDF__CALC_TOTAL_SURCHARGES_FORMATTED",
        "zubehor_preis": "PDF__SOLAR_CALC_ZUBEHOR_PREIS_FORMATTED",
        "extra_dienstleistungen": "PDF__SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN_FORMATTED",
        "zwischensumme_preis": "PDF__CALC_ZWISCHENSUMME_FORMATTED",
        "minus_mwst": "PDF__SIMPLE_MWST_FORMATTED",
        "final_end_preis": "PDF__FINAL_END_PREIS_FORMATTED"
    }

    print("\n🗺️ PDF PLATZHALTER MAPPING:")
    print("=" * 50)
    for placeholder, key in placeholder_mapping.items():
        print(f"{placeholder} -> {key}")

    return placeholder_mapping


if __name__ == "__main__":
    print("🎯 FINALE PREISBERECHNUNG MIT ALLEN KEYS")
    print("=" * 60)

    # Berechnung erstellen
    keys, pdf_bytes, session_data = create_final_pricing_calculation()

    if keys:
        print("\n✅ BERECHNUNG ERFOLGREICH ERSTELLT!")

        # PDF Platzhalter Mapping
        mapping = create_pdf_placeholder_mapping()

        print("\n📊 SESSION STATE DATA FÜR SOLAR CALCULATOR:")
        print("=" * 50)
        if session_data:
            for key, value in session_data.items():
                if key != "formatted":
                    print(f"{key}: {value}")

        print("\n🎯 BEREIT FÜR PDF INTEGRATION!")
    else:
        print("\n❌ FEHLER BEI DER ERSTELLUNG!")
