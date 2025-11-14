#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINALER TEST: Prüft ob die HAUPT-Dateien (nicht repair_pdf!) korrekt funktionieren
"""

print("=" * 100)
print("FINALE ÜBERPRÜFUNG: Verwende NUR die Haupt-Dateien (wie die echte App)")
print("=" * 100)

# Import aus HAUPT-Dateien (nicht repair_pdf!)
from product_db import list_products
from calculations import perform_calculations

print("\n[OK] Imports erfolgreich aus Haupt-Dateien\n")

# 1. TEST: Kategorie-Mapping
print("TEST 1: Kategorie-Mapping in product_db.py")
print("-" * 100)

modules = list_products('module')
inverters = list_products('inverter')
storage = list_products('storage')

print(f"[OK] list_products('module'):    {len(modules)} gefunden")
print(f"[OK] list_products('inverter'):  {len(inverters)} gefunden")
print(f"[OK] list_products('storage'):   {len(storage)} gefunden")

if len(modules) > 0 and len(inverters) > 0 and len(storage) > 0:
    print("\n[OK] KATEGORIE-MAPPING FUNKTIONIERT!")
else:
    print("\n[ERROR] KATEGORIE-MAPPING FEHLER!")
    exit(1)

# 2. TEST: Produktpreis-Berechnung
print("\n" + "=" * 100)
print("TEST 2: Produktpreis-Berechnung in calculations.py")
print("-" * 100)

# Konfiguration mit ersten 3 Modulen
test_configs = []
for i in [0, 5, 10]:
    if i < len(modules) and i < len(inverters) and i < len(storage):
        test_configs.append({
            "module": modules[i],
            "inverter": inverters[min(i*2, len(inverters)-1)],
            "storage": storage[min(i, len(storage)-1)]
        })

results = []

for idx, config in enumerate(test_configs):
    print(f"\nKonfiguration {idx+1}:")
    print(f"  Modul:  {config['module'].get('model_name')[:40]:40} ({config['module'].get('price_euro', 0):.2f} €)")
    print(f"  WR:     {config['inverter'].get('model_name')[:40]:40} ({config['inverter'].get('price_euro', 0):.2f} €)")
    print(f"  Speicher: {config['storage'].get('model_name')[:40]:40} ({config['storage'].get('price_euro', 0):.2f} €)")
    
    calc_input = {
        "project_details": {
            "selected_module_id": config['module']['id'],
            "selected_inverter_id": config['inverter']['id'],
            "selected_storage_id": config['storage']['id'],
            "module_quantity": 20,
            "include_storage": True,
            "annual_consumption_kwh": 4500,
        },
        "customer_data": {
            "electricity_price_ct_per_kwh": 30.0
        }
    }
    
    errors = []
    calc_results = perform_calculations(calc_input, {}, errors)
    
    if calc_results:
        total = calc_results.get('total_investment_netto', 0)
        base = calc_results.get('base_matrix_price_netto', 0)
        print(f"  → Basis-Preis: {base:>10.2f} €, Gesamt: {total:>10.2f} €")
        
        # Prüfe ob Produktpreise verwendet wurden
        product_logs = [e for e in errors if 'Preis aus DB' in e or 'Produktdatenbank' in e]
        if product_logs:
            print(f"  [OK] Produktpreise verwendet:")
            for log in product_logs[:2]:
                print(f"     {log[:80]}")
        
        results.append(total)
    else:
        print(f"  [ERROR] Berechnung fehlgeschlagen")
        results.append(0)

# 3. ANALYSE
print("\n" + "=" * 100)
print("FINALE ANALYSE")
print("=" * 100)

print(f"\nBerechnete Preise:")
for idx, price in enumerate(results):
    print(f"  Konfiguration {idx+1}: {price:>12.2f} €")

unique_prices = len(set(results))

if unique_prices == len(results) and all(p > 0 for p in results):
    print(f"\n[OK][OK][OK] PERFEKT! Alle {len(results)} Konfigurationen haben UNTERSCHIEDLICHE Preise!")
    print(f"    Spanne: {min(results):.2f} € bis {max(results):.2f} €")
    print(f"    Differenz: {max(results) - min(results):.2f} €")
    print("\n🎉 DIE APP SOLLTE JETZT FUNKTIONIEREN! 🎉")
elif unique_prices == 1:
    print(f"\n[ERROR] PROBLEM: Alle Preise sind GLEICH: {results[0]:.2f} €")
    print("   Die Produktpreise werden NICHT verwendet!")
else:
    print(f"\n[WARNING]  {unique_prices} verschiedene Preise bei {len(results)} Konfigurationen")

print("\n" + "=" * 100)
