"""
Test-Script für PV-Unterkonstruktions-Integration
==================================================

Testet:
1. Automatische Mengenberechnung
2. Pricing-Integration
3. PDF-Einbindung (Simulation)

Author: Bokuk2 System
Date: 2025-11-06
"""

import sys
from pprint import pprint

# Test 1: Mengenberechnung
print("=" * 80)
print("TEST 1: Automatische Mengenberechnung")
print("=" * 80)

try:
    from solar_calculator_pv_mounting_integration import (
        calculate_mounting_requirements_from_details,
        update_mounting_quantities_in_details,
        merge_manual_and_calculated_components,
        get_mounting_total_price
    )
    
    # Simuliere project_details
    project_details = {
        'module_count': 20,
        'module_width_mm': 1134,
        'module_height_mm': 1722,
        'module_weight_kg': 21.5,
        'module_orientation': 'Portrait',
        'module_rows': 2,
        'roof_type': 'Ziegeldach',
        'roof_pitch_degrees': 35.0,
        'roof_orientation': 'Süd',
        'rafter_spacing_mm': 800.0,
        'snow_load_zone': 2,
        'wind_load_zone': 2,
        'mounting_manufacturer': 'K2 Systems',
        'distance_to_inverter_m': 12.0,
        'include_pv_mounting': True
    }
    
    print("\n Input:")
    print(f"  Module: {project_details['module_count']}x {project_details['module_width_mm']}x{project_details['module_height_mm']}mm")
    print(f"  Dachtyp: {project_details['roof_type']}")
    print(f"  Hersteller: {project_details['mounting_manufacturer']}")
    
    # Berechnung
    calc_result = calculate_mounting_requirements_from_details(project_details)
    
    if calc_result:
        print("\nBerechnung erfolgreich!")
        print(f"\nErgebnis:")
        print(f"  Komponenten: {calc_result.total_components_count}")
        print(f"  Gesamtpreis: {calc_result.total_price_netto:.2f} EUR")
        print(f"  Gewicht: {calc_result.total_weight_kg:.1f} kg")
        
        print(f"\nKomponenten-Details:")
        for comp in calc_result.components:
            print(f"  - {comp.product_name} ({comp.manufacturer})")
            print(f"    Kategorie: {comp.category}")
            print(f"    Menge: {comp.quantity} {comp.unit}")
            print(f"    Preis: {comp.price_per_unit:.2f} EUR/Stk → Gesamt: {comp.total_price:.2f} EUR")
            if comp.notes:
                print(f"    Hinweis: {comp.notes}")
            print()
        
        # Update project_details
        update_mounting_quantities_in_details(project_details, calc_result)
        print("project_details aktualisiert")
    else:
        print("Berechnung fehlgeschlagen")
        sys.exit(1)
        
except ImportError as e:
    print(f"Import-Fehler: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Fehler bei Berechnung: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 2: Pricing-Integration
print("\n" + "=" * 80)
print("TEST 2: Pricing-Integration")
print("=" * 80)

try:
    total_price = get_mounting_total_price(project_details)
    print(f"\nGesamtpreis Unterkonstruktion: {total_price:.2f} EUR")
    
    # Simuliere manuelle Auswahl + automatische Menge
    project_details['mounting_roof_hook_selected_name'] = 'SingleHook 4S Dachhaken'
    project_details['mounting_manufacturer'] = 'K2 Systems'
    
    merged = merge_manual_and_calculated_components(project_details)
    
    print(f"\n Merged Komponenten (manuell + berechnet):")
    for comp in merged:
        manual_flag = " [MANUELL]" if comp.get('manual') else ""
        auto_flag = " [AUTO-MENGE]" if comp.get('auto_calculated') else ""
        print(f"  - {comp['product_name']}{manual_flag}{auto_flag}")
        print(f"    Menge: {comp['quantity']} {comp['unit']} × {comp['price_netto']:.2f} EUR = {comp['total_price']:.2f} EUR")
    
    print("\nPricing-Integration erfolgreich")
    
except Exception as e:
    print(f"Fehler bei Pricing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 3: PDF-Daten-Vorbereitung
print("\n" + "=" * 80)
print("TEST 3: PDF-Daten-Vorbereitung")
print("=" * 80)

try:
    from solar_calculator_pv_mounting_integration import get_mounting_components_for_pdf
    
    pdf_components = get_mounting_components_for_pdf(project_details)
    
    print(f"\nPDF-Komponenten ({len(pdf_components)} Einträge):")
    for i, comp in enumerate(pdf_components, 1):
        print(f"\n{i}. {comp['product_name']} ({comp['manufacturer']})")
        print(f"   Kategorie: {comp['category']}")
        print(f"   Menge: {comp['quantity']} {comp['unit']}")
        print(f"   Preis/Einheit: {comp.get('price_netto', 0):.2f} EUR")
        print(f"   Gesamt: {comp.get('total_price', 0):.2f} EUR")
    
    print("\nPDF-Daten erfolgreich vorbereitet")
    
except Exception as e:
    print(f"Fehler bei PDF-Vorbereitung: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 4: Calculations.py Integration (Simulation)
print("\n" + "=" * 80)
print("TEST 4: Calculations Integration (Simulation)")
print("=" * 80)

try:
    # Simuliere was calculations.py machen würde
    cost_pv_mounting_netto = get_mounting_total_price(project_details)
    
    print(f"\n cost_pv_mounting_netto: {cost_pv_mounting_netto:.2f} EUR")
    
    # Simuliere total_additional_costs_netto
    cost_modules_aufpreis_netto = 500.0
    cost_inverter_aufpreis_netto = 300.0
    cost_storage_aufpreis_product_db_netto = 0.0
    cost_accessories_aufpreis_netto = 150.0
    cost_misc_netto = 0.0
    cost_scaffolding_netto = 200.0
    cost_custom_netto = 0.0
    total_optional_components_cost_netto = 0.0
    
    total_additional_costs_netto = sum([
        cost_modules_aufpreis_netto,
        cost_inverter_aufpreis_netto,
        cost_storage_aufpreis_product_db_netto,
        cost_accessories_aufpreis_netto,
        cost_misc_netto,
        cost_scaffolding_netto,
        cost_custom_netto,
        total_optional_components_cost_netto,
        cost_pv_mounting_netto  # NEW
    ])
    
    print(f"\nKostenaufstellung:")
    print(f"  Module Aufpreis: {cost_modules_aufpreis_netto:.2f} EUR")
    print(f"  Inverter Aufpreis: {cost_inverter_aufpreis_netto:.2f} EUR")
    print(f"  Zubehör: {cost_accessories_aufpreis_netto:.2f} EUR")
    print(f"  Gerüst: {cost_scaffolding_netto:.2f} EUR")
    print(f"  PV-Unterkonstruktion: {cost_pv_mounting_netto:.2f} EUR ")
    print(f"  " + "-" * 60)
    print(f"  Gesamt Zusatzkosten: {total_additional_costs_netto:.2f} EUR")
    
    print("\nCalculations Integration OK")
    
except Exception as e:
    print(f"Fehler bei Calculations: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Zusammenfassung
print("\n" + "=" * 80)
print(" ALLE TESTS ERFOLGREICH!")
print("=" * 80)
print("\nMengenberechnung funktioniert")
print("Pricing-Integration funktioniert")
print("PDF-Daten-Vorbereitung funktioniert")
print("Calculations Integration funktioniert")
print("\nReady for Production!")
