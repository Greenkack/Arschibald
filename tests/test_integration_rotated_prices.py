#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRATIONS-TEST: Überprüfen dass ALLE Fixes funktionieren:
1. Category mapping
2. Product price calculations
3. Rotated products pro Firma
4. Unterschiedliche Preise pro Firma
"""

from calculations import perform_calculations
from product_db import list_products, get_product_by_id
from database import init_db
from multi_offer_generator import MultiCompanyOfferGenerator
import sys
import logging
from copy import deepcopy

# Logging konfigurieren
logging.basicConfig(level=logging.WARNING)

# Import der Hauptdateien

print("=" * 100)
print("INTEGRATIONS-TEST: Multi-Offer Generator mit unterschiedlichen Preisen pro Firma")
print("=" * 100)

# DB initialisieren
init_db()

# Generator erstellen
generator = MultiCompanyOfferGenerator()

# Basis-Settings
base_settings = {
    "selected_module_id": list_products("module")[0].get("id"),
    "selected_inverter_id": list_products("inverter")[0].get("id"),
    "selected_storage_id": list_products("storage")[0].get("id"),
    "module_quantity": 20,
    "include_storage": True,
}

# Persönliche Kundendata
customer_data = {
    "name": "Test Customer",
    "email": "test@example.com",
    "phone": "+49 123 456789",
    "address": "Teststraße 1, 12345 Teststadt",
}

# Projekt-Daten (gleich für alle Firmen)
project_data = {
    "project_name": "Einfamilienhaus Solaranlage",
    "roof_area": 100,
    "consumption_annual": 5000,
    "consumption_data": {
        "annual_consumption": 5000,
        "monthly_consumption": [
            400,
            420,
            450,
            420,
            450,
            480,
            500,
            480,
            450,
            420,
            380,
            400],
    },
    "project_details": {
        "module_quantity": 20,
        "include_storage": True,
    }}

# Firmen-Konfiguration (5 verschiedene Firmen)
companies = [
    {"id": f"company_{i}", "name": f"Company {i + 1}"}
    for i in range(5)
]

print(f"\nKundendata: {customer_data['name']}")
print(f"Projektdaten: {project_data['project_name']}")
print(f"Firmen: {len(companies)}")

print("\n" + "=" * 100)
print("TEST 1: ROTIERTE PRODUKTE PRO FIRMA")
print("=" * 100)

# Simuliere rotierte Produkte pro Firma
module_products = list_products("module")
inverter_products = list_products("inverter")
storage_products = list_products("storage")

print(f"\nVerfügbare Produkte:")
print(f"  - Module: {len(module_products)}")
print(f"  - Wechselrichter: {len(inverter_products)}")
print(f"  - Speicher: {len(storage_products)}")

# Speichere Angebotsdaten pro Firma
all_offers = {}

for i, company in enumerate(companies):
    print(f"\n--- Firma {i + 1} ({company['name']}) ---")

    # Rotierte Produkte für diese Firma
    rotated_settings = {
        "selected_module_id": module_products[i % len(module_products)].get("id"),
        "selected_inverter_id": inverter_products[i % len(inverter_products)].get("id"),
        "selected_storage_id": storage_products[i % len(storage_products)].get("id"),
        "module_quantity": 20,
        "include_storage": True,
    }

    # Rufe _prepare_offer_data auf
    offer_data = generator._prepare_offer_data(
        customer_data=customer_data,
        company=company,
        company_settings=rotated_settings,
        project_data=deepcopy(project_data),
        company_index=i
    )

    # Speichere offer_data
    all_offers[i] = offer_data

    # Zeige Produkte
    module = offer_data.get("selected_module", {})
    inverter = offer_data.get("selected_inverter", {})
    storage = offer_data.get("selected_storage", {})

    print(f"  Produkte:")
    print(
        f"    - Modul:  {module.get('model_name')} ({module.get('price_euro', 'N/A')}€)")
    print(
        f"    - WR:     {inverter.get('model_name')} ({inverter.get('price_euro', 'N/A')}€)")
    print(
        f"    - Speicher: {storage.get('model_name')} ({storage.get('price_euro', 'N/A')}€)")

print("\n" + "=" * 100)
print("TEST 2: BERECHNUNGEN PRO FIRMA")
print("=" * 100)

prices_per_company = {}

for i, company in enumerate(companies):
    print(f"\n--- Firma {i + 1} ({company['name']}) ---")

    offer_data = all_offers[i]

    # Führe Berechnungen durch
    try:
        # Projektdetails aus offer_data
        project_details = offer_data.get("project_details", {})
        module_id = project_details.get("selected_module_id")
        inverter_id = project_details.get("selected_inverter_id")
        storage_id = project_details.get("selected_storage_id")
        module_qty = project_details.get("module_quantity", 20)

        # Struktur für perform_calculations()
        project_data_for_calc = {
            "customer_data": customer_data,
            "project_details": {
                "module_quantity": module_qty,
                "include_storage": project_details.get(
                    "include_storage",
                    True),
                "selected_module_id": module_id,
                "selected_inverter_id": inverter_id,
                "selected_storage_id": storage_id,
            },
            "consumption_data": project_data.get(
                "consumption_data",
                {}),
            "economic_data": {},
        }

        # Führe Berechnung durch
        calc_results = perform_calculations(
            project_data=project_data_for_calc,
            texts={},
            errors_list=[]
        )        # Extrahiere Basis-Preis
        base_price = calc_results.get(
            "base_matrix_price_netto", calc_results.get(
                "total_investment_netto", 0))

        prices_per_company[i] = {
            "company_name": company["name"],
            "base_price": base_price,
            "module": offer_data.get(
                "selected_module",
                {}).get("model_name"),
            "inverter": offer_data.get(
                "selected_inverter",
                {}).get("model_name"),
            "storage": offer_data.get(
                "selected_storage",
                {}).get("model_name"),
        }

        print(f"  Basis-Preis: {base_price:,.2f}€")
        print(
            f"  Modul:  {
                offer_data.get(
                    'selected_module',
                    {}).get('model_name')}")
        print(
            f"  WR:     {
                offer_data.get(
                    'selected_inverter',
                    {}).get('model_name')}")
        print(
            f"  Speicher: {
                offer_data.get(
                    'selected_storage',
                    {}).get('model_name')}")

    except Exception as e:
        print(f"  ✗ Fehler bei Berechnung: {e}")

print("\n" + "=" * 100)
print("ERGEBNISSE: PREIS-VERGLEICH PRO FIRMA")
print("=" * 100)

sorted_prices = sorted(
    prices_per_company.items(),
    key=lambda x: x[1]["base_price"])

print(f"\nPreise pro Firma (aufsteigend sortiert):\n")
for i, (idx, data) in enumerate(sorted_prices, 1):
    print(f"{i}. {data['company_name']:15} - {data['base_price']:8,.2f}€")
    print(f"   Modul: {data['module']}")
    print(f"   WR:    {data['inverter']}")
    print(f"   Speicher: {data['storage']}\n")

# Überprüfe Unterschiede
if len(sorted_prices) > 1:
    min_price = sorted_prices[0][1]["base_price"]
    max_price = sorted_prices[-1][1]["base_price"]
    difference = max_price - min_price

    if difference > 0:
        print(f"✅ PREISE UNTERSCHEIDEN SICH!")
        print(f"   Min: {min_price:,.2f}€")
        print(f"   Max: {max_price:,.2f}€")
        print(
            f"   Differenz: {difference:,.2f}€ ({(difference / min_price) * 100:.1f}%)")
    else:
        print(f"❌ FEHLER: Alle Preise sind GLEICH!")
else:
    print(f"⚠️  Zu wenig Firmen für Vergleich")

print("\n" + "=" * 100)
print("INTEGRATIONS-TEST ABGESCHLOSSEN")
print("=" * 100)
