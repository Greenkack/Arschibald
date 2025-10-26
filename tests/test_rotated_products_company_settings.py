#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test, um zu überprüfen, dass _prepare_offer_data() die company_settings
(mit rotierten Produkten) korrekt verwendet!
"""

from product_db import list_products
from database import init_db
from multi_offer_generator import MultiCompanyOfferGenerator
import sys
import logging
from copy import deepcopy

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)

# Import der Hauptdateien

print("=" * 100)
print("TEST: Überprüfen dass rotierte Produkte in company_settings verwendet werden")
print("=" * 100)

# DB initialisieren
init_db()

# Generator erstellen
generator = MultiCompanyOfferGenerator()

# Basis-Settings (erste Produkte)
base_settings = {
    "selected_module_id": list_products("module")[0].get("id"),
    "selected_inverter_id": list_products("inverter")[0].get("id"),
    "selected_storage_id": list_products("storage")[0].get("id"),
    "module_quantity": 20,
    "include_storage": True,
}

print(f"\n✓ Basis-Settings:")
print(f"  - Modul ID:       {base_settings['selected_module_id']}")
print(f"  - Wechselrichter: {base_settings['selected_inverter_id']}")
print(f"  - Speicher:       {base_settings['selected_storage_id']}")

# Jetzt simulieren wir 5 Firmen mit rotierten Produkten
companies = [
    {"id": f"company_{i}", "name": f"Company {i}"}
    for i in range(5)
]

customer_data = {
    "name": "Test Customer",
    "email": "test@example.com",
}

project_data = {
    "project_details": {
        "module_quantity": 20,
        "include_storage": True,
    }
}

print(f"\n" + "=" * 100)
print("TEST: Rotierten Produktauswahl pro Firma")
print("=" * 100)

for i, company in enumerate(companies):
    print(f"\n--- Firma {i + 1} ({company['name']}) ---")

    # Hole rotierte Produkte für diese Firma (Simulation)
    # In der echten App kommt das von get_rotated_products_for_company()
    module_products = list_products("module")
    inverter_products = list_products("inverter")
    storage_products = list_products("storage")

    # Rotation: Jede Firma bekommt ein anderes Produkt
    rotated_settings = {
        "selected_module_id": module_products[i % len(module_products)].get("id"),
        "selected_inverter_id": inverter_products[i % len(inverter_products)].get("id"),
        "selected_storage_id": storage_products[i % len(storage_products)].get("id"),
        "module_quantity": 20,
        "include_storage": True,
    }

    print(f"  Rotierten Settings (company_settings):")
    print(f"    - Modul ID:       {rotated_settings['selected_module_id']}")
    print(f"    - WR ID:          {rotated_settings['selected_inverter_id']}")
    print(f"    - Speicher ID:    {rotated_settings['selected_storage_id']}")

    # Rufe _prepare_offer_data auf mit company_settings Parameter
    offer_data = generator._prepare_offer_data(
        customer_data=customer_data,
        company=company,
        company_settings=rotated_settings,
        # KRITISCH: Das ist der company_settings Parameter
        project_data=project_data,
        company_index=i
    )

    # Überprüfe, ob die richtigen Produkte in offer_data sind
    if "selected_module" in offer_data:
        selected_module = offer_data["selected_module"]
        print(
            f"  ✓ Modul geladen: {
                selected_module.get('model_name')} (ID: {
                selected_module.get('id')})")
    else:
        print(f"  ✗ FEHLER: selected_module nicht in offer_data!")

    if "selected_inverter" in offer_data:
        selected_inverter = offer_data["selected_inverter"]
        print(
            f"  ✓ WR geladen:    {
                selected_inverter.get('model_name')} (ID: {
                selected_inverter.get('id')})")
    else:
        print(f"  ✗ FEHLER: selected_inverter nicht in offer_data!")

    if "selected_storage" in offer_data:
        selected_storage = offer_data["selected_storage"]
        print(
            f"  ✓ Speicher:      {
                selected_storage.get('model_name')} (ID: {
                selected_storage.get('id')})")
    else:
        print(f"  ✗ FEHLER: selected_storage nicht in offer_data!")

print("\n" + "=" * 100)
print("✅ TEST ABGESCHLOSSEN")
print("=" * 100)
print("\nWenn oben unterschiedliche Produkte pro Firma angezeigt werden,")
print("dann funktioniert die company_settings Übergabe korrekt! ✅")
