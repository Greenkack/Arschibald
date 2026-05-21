#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test: Validierung der Wärmepumpen-Empfehlungen"""

from product_db import get_product_by_model_name
from heatpump_products_database import get_heatpump_models

print("=" * 80)
print("VALIDIERUNG: Nur echte Produkte werden empfohlen")
print("=" * 80)
print()

# Test 1: Viessmann Luft-Wasser
viessmann = get_heatpump_models('Viessmann', 'Luft-Wasser-Wärmepumpe')
print(f"Viessmann Luft-Wasser Modelle in heatpump_products_database: {len(viessmann)}")

# Test 2: Wie viele sind in product_db?
validated = [m for m in viessmann if get_product_by_model_name(m.get("model")) is not None]
print(f"Davon in product_db.py (echte Produkte): {len(validated)}")
print()

if len(validated) == len(viessmann):
    print("OK: ALLE Viessmann-Modelle sind in der Produktdatenbank!")
else:
    print(f"WARNUNG: {len(viessmann) - len(validated)} Modelle fehlen in product_db!")
    missing = [m.get("model") for m in viessmann if get_product_by_model_name(m.get("model")) is None]
    print("Fehlende Modelle:")
    for m in missing[:5]:
        print(f"  - {m}")
    if len(missing) > 5:
        print(f"  ... +{len(missing)-5} weitere")

print()
print("=" * 80)
print("Test: Empfehlungs-Funktion gibt nur echte Produkte zurück")
print("=" * 80)
print()

# Simuliere Empfehlung
from heatpump_products_database import HEATPUMP_PRODUCTS

recommendations = []
for manufacturer, types in HEATPUMP_PRODUCTS.items():
    for hp_type, models in types.items():
        for model in models:
            model_name = model.get("model", "")
            # VALIDIERUNG wie in heatpump_ui.py
            db_product = get_product_by_model_name(model_name)
            if db_product is not None:
                recommendations.append(model_name)

print(f"Total Modelle in heatpump_products_database: {sum(len(models) for m, types in HEATPUMP_PRODUCTS.items() for t, models in types.items())}")
print(f"Davon validiert (in product_db): {len(recommendations)}")
print()

if len(recommendations) > 0:
    print("OK: Empfehlungs-System kann echte Produkte empfehlen!")
    print()
    print("Beispiel-Empfehlungen:")
    for i, model in enumerate(recommendations[:5], 1):
        print(f"  {i}. {model}")
else:
    print("FEHLER: Keine Produkte validiert!")

print()
print("=" * 80)
