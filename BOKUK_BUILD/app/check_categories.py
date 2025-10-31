#!/usr/bin/env python3
"""Prüft welche Kategorien in der products-Tabelle existieren"""

import os
import sqlite3

db_path = os.path.join('data', 'app_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("KATEGORIEN IN PRODUCTS-TABELLE")
print("=" * 80)

# Unique categories
cursor.execute(
    "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
categories = cursor.fetchall()

for cat in categories:
    cursor.execute("SELECT COUNT(*) FROM products WHERE category=?", (cat[0],))
    count = cursor.fetchone()[0]
    print(f"  {cat[0]:<30} ({count} Produkte)")

print("\n" + "=" * 80)
print("BEISPIEL-PRODUKTE (erste 10)")
print("=" * 80)

cursor.execute("""
    SELECT id, category, model_name, price_euro, capacity_w
    FROM products
    LIMIT 10
""")

rows = cursor.fetchall()
print(
    f"{
        'ID':<6} {
            'Kategorie':<20} {
                'Modell':<35} {
                    'Preis':>12} {
                        'Leistung':>10}")
print("-" * 80)

for row in rows:
    price_str = f"{row[3]:.2f} €" if row[3] else "KEIN PREIS"
    capacity_str = f"{row[4]} W" if row[4] else "N/A"
    print(f"{row[0]:<6} {(row[1] or 'N/A'):<20} {(row[2] or 'N/A')[:34]:<35} {price_str:>12} {capacity_str:>10}")

conn.close()
