#!/usr/bin/env python3
"""
DEBUG-Test: Überprüfe, welche Produktdetails in den Berechnungen verwendet werden
"""

from product_db import list_products
from multi_offer_generator import MultiCompanyOfferGenerator
from database import init_db
import logging
from copy import deepcopy

# Logging SEHR verbose konfigurieren
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Import der Funktionen

# DB initialisieren
init_db()

print("=" * 100)
print("DEBUG-TEST: Überprüfe Produktdetails in _prepare_offer_data()")
print("=" * 100)

# Generator erstellen
generator = MultiCompanyOfferGenerator()

# Basis-Daten
customer_data = {
    "name": "Test Customer",
    "email": "test@example.com",
}

company = {"id": "company_1", "name": "Company 1"}

# Project Data
project_data = {
    "project_details": {
        "module_quantity": 20,
        "include_storage": True,
    },
    "consumption_data": {"annual_consumption": 5000},
}

# Rotierte Settings für diese Firma
module_products = list_products("module")
inverter_products = list_products("inverter")
storage_products = list_products("storage")

# Firma 2 (Index 1) sollte ANDERE Produkte als Firma 1 haben
company_index = 1

rotated_settings = {
    "selected_module_id": module_products[company_index % len(module_products)].get("id"),
    "selected_inverter_id": inverter_products[company_index % len(inverter_products)].get("id"),
    "selected_storage_id": storage_products[company_index % len(storage_products)].get("id"),
    "module_quantity": 20,
    "include_storage": True,
}

print(f"\nFirma {company_index + 1}: {company['name']}")
print(f"  Rotierte Modul-ID:       {rotated_settings['selected_module_id']}")
print(f"  Rotierte WR-ID:          {rotated_settings['selected_inverter_id']}")
print(f"  Rotierte Speicher-ID:    {rotated_settings['selected_storage_id']}")

# Rufe _prepare_offer_data auf
print("\n>>> Rufe _prepare_offer_data() auf...")
offer_data = generator._prepare_offer_data(
    customer_data=customer_data,
    company=company,
    company_settings=rotated_settings,
    project_data=deepcopy(project_data),
    company_index=company_index
)

# Überprüfe, was in offer_data ist
print("\nOffer Data - project_details:")
project_details_out = offer_data.get("project_details", {})
print(f"  Modul-ID:       {project_details_out.get('selected_module_id')}")
print(f"  WR-ID:          {project_details_out.get('selected_inverter_id')}")
print(f"  Speicher-ID:    {project_details_out.get('selected_storage_id')}")

# Überprüfe, was in offer_data["project_data"] ist
print("\nOffer Data - project_data.project_details:")
if "project_data" in offer_data and "project_details" in offer_data.get(
    "project_data",
        {}):
    project_details_in_pd = offer_data["project_data"]["project_details"]
    print(
        f"  Modul-ID:       {project_details_in_pd.get('selected_module_id')}")
    print(
        f"  WR-ID:          {project_details_in_pd.get('selected_inverter_id')}")
    print(
        f"  Speicher-ID:    {project_details_in_pd.get('selected_storage_id')}")
else:
    print("  (project_data nicht vorhanden)")

print("\n" + "=" * 100)
print("TEST ABGESCHLOSSEN")
print("=" * 100)
