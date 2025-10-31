#!/usr/bin/env python3
"""
FIX PDF PLATZHALTER PROBLEME

1. Seite 1: Ersparte Mehrwertsteuer - falscher Key
2. Seite 1: Amortisationszeit - falscher Key  
3. Seite 7: Alle Beträge zeigen 0,00 € - Keys nicht verknüpft
"""

import sys

sys.path.append('.')

def fix_pdf_placeholder_problems():
    """Behebt alle 3 PDF-Platzhalter Probleme"""

    print("🔧 BEHEBE PDF PLATZHALTER PROBLEME")
    print("=" * 60)

    # 1. SEITE 1 PROBLEME ANALYSIEREN
    print("\n1. 📄 SEITE 1 PROBLEME:")
    print("   - Ersparte Mehrwertsteuer: falscher Key")
    print("   - Amortisationszeit: falscher Key")

    # Aus coords/seite1.yml:
    # "ersparte Mehrwertsteuer" Position: (394.12188720703125, 648.8770751953125, 437.10577392578125, 664.68994140625)
    # "29.150,00 EUR*" Position: (458.7808532714844, 393.9034423828125, 533.526123046875, 409.9840087890625) - Das ist die Amortisationszeit

    print("   ✅ Identifiziert: 'ersparte Mehrwertsteuer' braucht MwSt-Key")
    print("   ✅ Identifiziert: '29.150,00 EUR*' braucht Amortisationszeit-Key")

    # 2. SEITE 7 PROBLEME ANALYSIEREN
    print("\n2. 📄 SEITE 7 PROBLEME:")
    print("   - Alle Beträge zeigen 0,00 €")
    print("   - Keys nicht mit Solar Calculator verknüpft")

    # Aus coords/seite7.yml:
    seite7_placeholders = {
        "preis_mit_mwst": "Gesamtsumme Brutto",
        "zubehor_preis": "Zubehör / Extras",
        "minus_rabatt": "Nachlass / Rabatt",
        "plus_aufpreis": "Extrakosten / Aufpreis",
        "zwischensumme_preis": "Zwischensumme / Listenpreis",
        "minus_mwst": "abzüglich 19,00 % MwSt",
        "final_end_preis": "gesamte Investitionssumme"
    }

    print("   ✅ Identifiziert: 7 Platzhalter brauchen Solar Calculator Keys")
    for key, label in seite7_placeholders.items():
        print(f"      - {key} -> {label}")

    # 3. SOLAR CALCULATOR KEYS ANALYSIEREN
    print("\n3. 🧮 SOLAR CALCULATOR KEYS:")

    # Aus final_pricing_calculation_with_keys.py:
    solar_calc_keys = {
        "PDF__SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED": "20.000,00 €",
        "PDF__CALC_TOTAL_DISCOUNTS_FORMATTED": "1.500,00 €",
        "PDF__CALC_TOTAL_SURCHARGES_FORMATTED": "700,00 €",
        "PDF__SOLAR_CALC_ZUBEHOR_PREIS_FORMATTED": "800,00 €",
        "PDF__SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN_FORMATTED": "500,00 €",
        "PDF__CALC_ZWISCHENSUMME_FORMATTED": "20.500,00 €",
        "PDF__SIMPLE_MWST_FORMATTED": "3.273,11 €",
        "PDF__FINAL_END_PREIS_FORMATTED": "17.226,89 €"
    }

    print("   ✅ Verfügbare Solar Calculator Keys:")
    for key, value in solar_calc_keys.items():
        print(f"      - {key}: {value}")

    # 4. MAPPING ERSTELLEN
    print("\n4. 🗺️ KEY MAPPING:")

    # Seite 1 Mapping
    seite1_mapping = {
        "ersparte Mehrwertsteuer": "PDF__SIMPLE_MWST_FORMATTED",
        "29.150,00 EUR*": "amortization_time_years"  # Braucht separaten Key
    }

    # Seite 7 Mapping
    seite7_mapping = {
        "preis_mit_mwst": "PDF__SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED",
        "zubehor_preis": "PDF__SOLAR_CALC_ZUBEHOR_PREIS_FORMATTED",
        "minus_rabatt": "PDF__CALC_TOTAL_DISCOUNTS_FORMATTED",
        "plus_aufpreis": "PDF__CALC_TOTAL_SURCHARGES_FORMATTED",
        "zwischensumme_preis": "PDF__CALC_ZWISCHENSUMME_FORMATTED",
        "minus_mwst": "PDF__SIMPLE_MWST_FORMATTED",
        "final_end_preis": "PDF__FINAL_END_PREIS_FORMATTED"
    }

    print("   ✅ SEITE 1 MAPPING:")
    for placeholder, key in seite1_mapping.items():
        print(f"      - '{placeholder}' -> {key}")

    print("   ✅ SEITE 7 MAPPING:")
    for placeholder, key in seite7_mapping.items():
        print(f"      - '{placeholder}' -> {key}")

    # 5. PLACEHOLDERS.PY UPDATE VORBEREITEN
    print("\n5. 📝 PLACEHOLDERS.PY UPDATE:")

    placeholder_updates = {
        # Seite 1 Updates
        "ersparte Mehrwertsteuer": "vat_amount_eur_formatted",
        "29.150,00 EUR*": "amortization_time_formatted",

        # Seite 7 Updates - Mapping zu Solar Calculator Keys
        "preis_mit_mwst": "endergebnis_brutto_formatted",
        "zubehor_preis": "zubehor_preis_formatted",
        "minus_rabatt": "total_discounts_formatted",
        "plus_aufpreis": "total_surcharges_formatted",
        "zwischensumme_preis": "zwischensumme_formatted",
        "minus_mwst": "mwst_betrag_formatted",
        "final_end_preis": "final_end_preis_formatted"
    }

    print("   ✅ Placeholder Updates bereit:")
    for placeholder, key in placeholder_updates.items():
        print(f"      - PLACEHOLDER_MAPPING['{placeholder}'] = '{key}'")

    # 6. DYNAMIC DATA BUILDER UPDATE VORBEREITEN
    print("\n6. 🏗️ DYNAMIC DATA BUILDER UPDATE:")

    dynamic_data_updates = {
        # Seite 1
        "vat_amount_eur_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('mwst_betrag', '0,00 €')",
        "amortization_time_formatted": "analysis_results.get('amortization_time_years', '0') + ' Jahre'",

        # Seite 7 - Verknüpfung zu Solar Calculator Session State
        "endergebnis_brutto_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('endergebnis_brutto', '0,00 €')",
        "zubehor_preis_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('zubehor_preis', '0,00 €')",
        "total_discounts_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('total_discounts', '0,00 €')",
        "total_surcharges_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('total_surcharges', '0,00 €')",
        "zwischensumme_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('zwischensumme', '0,00 €')",
        "mwst_betrag_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('mwst_betrag', '0,00 €')",
        "final_end_preis_formatted": "session_state.get('simple_pricing_data', {}).get('formatted', {}).get('final_end_preis', '0,00 €')"
    }

    print("   ✅ Dynamic Data Updates bereit:")
    for key, source in dynamic_data_updates.items():
        print(f"      - result['{key}'] = {source}")

    print("\n" + "=" * 60)
    print("✅ ALLE PROBLEME ANALYSIERT UND LÖSUNGEN VORBEREITET!")
    print("✅ Bereit für Implementation in placeholders.py")

    return {
        "seite1_mapping": seite1_mapping,
        "seite7_mapping": seite7_mapping,
        "placeholder_updates": placeholder_updates,
        "dynamic_data_updates": dynamic_data_updates
    }

def create_placeholder_fix_code():
    """Erstellt den Code für placeholders.py Fix"""

    print("\n🔧 ERSTELLE PLACEHOLDER FIX CODE:")
    print("=" * 50)

    # PLACEHOLDER_MAPPING Updates
    mapping_code = '''
# FIX: Seite 1 und Seite 7 Platzhalter
PLACEHOLDER_MAPPING.update({
    # Seite 1 Fixes
    "ersparte Mehrwertsteuer": "vat_amount_eur_formatted",
    "29.150,00 EUR*": "amortization_time_formatted",
    
    # Seite 7 Fixes - Solar Calculator Integration
    "preis_mit_mwst": "endergebnis_brutto_formatted",
    "zubehor_preis": "zubehor_preis_formatted", 
    "minus_rabatt": "total_discounts_formatted",
    "plus_aufpreis": "total_surcharges_formatted", 
    "zwischensumme_preis": "zwischensumme_formatted",
    "minus_mwst": "mwst_betrag_formatted",
    "final_end_preis": "final_end_preis_formatted"
})
'''

    # build_dynamic_data Updates
    dynamic_code = '''
    # FIX: Seite 1 und Seite 7 Werte aus Solar Calculator Session State
    
    # Seite 1 Fixes
    result["vat_amount_eur_formatted"] = fmt_number(
        project_data.get("simple_pricing_data", {}).get("mwst_betrag", 0), 
        2, "€"
    )
    
    amortization_years = parse_float(analysis_results.get("amortization_time_years", 0))
    result["amortization_time_formatted"] = f"{amortization_years:.1f} Jahre" if amortization_years else "0 Jahre"
    
    # Seite 7 Fixes - Solar Calculator Integration
    simple_pricing = project_data.get("simple_pricing_data", {})
    formatted_pricing = simple_pricing.get("formatted", {})
    
    result["endergebnis_brutto_formatted"] = formatted_pricing.get("endergebnis_brutto", "0,00 €")
    result["zubehor_preis_formatted"] = formatted_pricing.get("zubehor_preis", "0,00 €")
    result["total_discounts_formatted"] = formatted_pricing.get("total_discounts", "0,00 €")
    result["total_surcharges_formatted"] = formatted_pricing.get("total_surcharges", "0,00 €")
    result["zwischensumme_formatted"] = formatted_pricing.get("zwischensumme", "0,00 €")
    result["mwst_betrag_formatted"] = formatted_pricing.get("mwst_betrag", "0,00 €")
    result["final_end_preis_formatted"] = formatted_pricing.get("final_end_preis", "0,00 €")
'''

    print("✅ PLACEHOLDER_MAPPING UPDATE:")
    print(mapping_code)

    print("✅ build_dynamic_data UPDATE:")
    print(dynamic_code)

    return {
        "mapping_code": mapping_code,
        "dynamic_code": dynamic_code
    }

if __name__ == "__main__":
    # Analysiere Probleme
    analysis = fix_pdf_placeholder_problems()

    # Erstelle Fix Code
    fix_code = create_placeholder_fix_code()

    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("1. placeholders.py öffnen")
    print("2. PLACEHOLDER_MAPPING Update hinzufügen")
    print("3. build_dynamic_data Update hinzufügen")
    print("4. Solar Calculator Session State Verknüpfung testen")
    print("5. PDF generieren und Werte prüfen")
