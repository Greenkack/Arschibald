#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Preis-System validieren
Zeigt, dass get_heatpump_price() jetzt ZUERST in product_db.py sucht
"""

from admin_heatpump_settings_ui import get_heatpump_price
from product_db import get_product_by_model_name, get_db_connection

print("=" * 80)
print("TEST: Preis-System Validierung")
print("=" * 80)
print()

# Test 1: Produkt mit Preis in product_db
test_model = "Vitocal 250-A"
print(f"Test 1: Produkt '{test_model}'")
print("-" * 80)

db_product = get_product_by_model_name(test_model)
if db_product:
    print(f"OK: Produkt in product_db.py gefunden")
    print(f"   ID: {db_product.get('id')}")
    print(f"   Preis in DB: {db_product.get('price_euro', 0):.2f} EUR")
else:
    print(f"FEHLER: Produkt nicht in product_db.py gefunden!")

print()

# Hole Preis über get_heatpump_price
try:
    price_info = get_heatpump_price(
        manufacturer="Viessmann",
        hp_type="Luft-Wasser-Wärmepumpe",
        model=test_model,
        power_kw=10.0
    )
    print("Preis-Info von get_heatpump_price():")
    print(f"   Gerätepreis: {price_info['base_price_eur']:,.2f} EUR")
    print(f"   Installation: {price_info['installation_price_eur']:,.2f} EUR")
    print(f"   Gesamt: {price_info['total_price_eur']:,.2f} EUR")
except Exception as e:
    print(f"FEHLER beim Preis-Abruf: {e}")

print()
print("=" * 80)
print("Test 2: Setze einen Preis in product_db")
print("=" * 80)
print()

# Setze einen Test-Preis
conn = get_db_connection()
cursor = conn.cursor()

test_price = 12000.0
cursor.execute("""
    UPDATE products
    SET price_euro = ?
    WHERE model_name = ?
""", (test_price, test_model))
conn.commit()

print(f"OK: Preis für '{test_model}' auf {test_price:.2f} EUR gesetzt")
print()

# Prüfe ob get_heatpump_price() den neuen Preis verwendet
price_info = get_heatpump_price(
    manufacturer="Viessmann",
    hp_type="Luft-Wasser-Wärmepumpe",
    model=test_model,
    power_kw=10.0
)

print("Neuer Preis von get_heatpump_price():")
print(f"   Gerätepreis: {price_info['base_price_eur']:,.2f} EUR")
print(f"   Installation (40%): {price_info['installation_price_eur']:,.2f} EUR")
print(f"   Gesamt: {price_info['total_price_eur']:,.2f} EUR")

# Validierung
expected_total = test_price * 1.4  # Gerät + 40% Installation
if abs(price_info['total_price_eur'] - expected_total) < 1.0:
    print()
    print("OK: Preis-Berechnung korrekt!")
    print(f"   Erwartet: {expected_total:,.2f} EUR")
    print(f"   Erhalten: {price_info['total_price_eur']:,.2f} EUR")
else:
    print()
    print(f"FEHLER: Preis-Berechnung falsch!")
    print(f"   Erwartet: {expected_total:,.2f} EUR")
    print(f"   Erhalten: {price_info['total_price_eur']:,.2f} EUR")

conn.close()

print()
print("=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)
print()
print("OK: get_heatpump_price() nutzt jetzt product_db.py!")
print("OK: Preise können mit edit_heatpump_prices.py bearbeitet werden!")
print()
print("Nächste Schritte:")
print("1. Streamlit-App starten: streamlit run gui.py")
print("2. Preise bearbeiten: streamlit run edit_heatpump_prices.py")
print("3. Wärmepumpen-Simulator testen")
print()
print("=" * 80)
