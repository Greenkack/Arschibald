#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST: Überprüfe get_heatpump_database() - NUR Viessmann, Buderus, Vaillant
"""

import sys
sys.path.insert(0, '.')

from heatpump_ui import get_heatpump_database

def main():
    print("=" * 80)
    print("TEST: get_heatpump_database()")
    print("=" * 80)
    
    hp_db = get_heatpump_database()
    
    print(f"\nGefundene Wärmepumpen: {len(hp_db)}")
    
    # Gruppiere nach Hersteller
    manufacturers = {}
    for hp in hp_db:
        mfr = hp.get('manufacturer', 'Unknown')
        if mfr not in manufacturers:
            manufacturers[mfr] = []
        manufacturers[mfr].append(hp)
    
    print("\nHersteller:")
    for mfr, pumps in sorted(manufacturers.items()):
        print(f"  {mfr}: {len(pumps)} Modelle")
    
    # Prüfe: KEINE unerwünschten Hersteller
    forbidden = ['Daikin', 'Mitsubishi', 'LG', 'Samsung', 'Panasonic']
    bad_ones = [mfr for mfr in manufacturers.keys() if mfr in forbidden]
    
    if bad_ones:
        print(f"\nFEHLER: Unerwünschte Hersteller gefunden: {bad_ones}")
    else:
        print("\nOK: Keine unerwünschten Hersteller!")
    
    # Zeige Beispiele
    print("\nBeispiel-Modelle:")
    for mfr in ['Viessmann', 'Buderus', 'Vaillant']:
        if mfr in manufacturers:
            examples = manufacturers[mfr][:3]
            for ex in examples:
                print(f"  • {ex['manufacturer']} {ex['model']} ({ex['heating_power']}kW)")

if __name__ == "__main__":
    main()
