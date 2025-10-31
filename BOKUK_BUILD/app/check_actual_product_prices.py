#!/usr/bin/env python3
"""Prüft die tatsächlichen Produktpreise in der Datenbank"""

import os
import sqlite3


def check_product_prices():
    """Zeigt Produktpreise direkt aus der SQLite-Datenbank"""

    # Die richtige Datenbank verwenden
    db_path = os.path.join('data', 'app_data.db')
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return

    print(f"📂 Verwende Datenbank: {db_path}\n")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Module
    print("=" * 120)
    print("MODULE (mit Preisen)")
    print("=" * 120)
    cursor.execute("""
        SELECT id, brand, model_name, price_euro, capacity_w
        FROM products
        WHERE category='module' AND price_euro IS NOT NULL AND price_euro > 0
        ORDER BY brand, capacity_w
        LIMIT 20
    """)

    rows = cursor.fetchall()
    if rows:
        print(
            f"{
                'ID':<6} {
                'Marke':<20} {
                'Modell':<45} {
                    'Preis':>12} {
                        'Leistung':>10}")
        print("-" * 120)
        for row in rows:
            print(
                f"{row[0]:<6} {row[1][:19]:<20} {row[2][:44]:<45} {row[3]:>11.2f} € {row[4]:>10} W")
    else:
        print("⚠️  KEINE Module mit Preisen gefunden!")

    # Alle Module (auch ohne Preis)
    print("\n" + "=" * 120)
    print("ALLE MODULE (auch ohne Preis)")
    print("=" * 120)
    cursor.execute("""
        SELECT id, brand, model_name, price_euro, capacity_w
        FROM products
        WHERE category='module'
        ORDER BY id
        LIMIT 20
    """)

    rows = cursor.fetchall()
    print(
        f"{
            'ID':<6} {
            'Marke':<20} {
                'Modell':<45} {
                    'Preis':>12} {
                        'Leistung':>10}")
    print("-" * 120)
    for row in rows:
        price_str = f"{row[3]:.2f} €" if row[3] else "KEIN PREIS"
        print(
            f"{row[0]:<6} {row[1][:19]:<20} {row[2][:44]:<45} {price_str:>12} {row[4]:>10} W")

    # Statistik
    print("\n" + "=" * 120)
    print("STATISTIK")
    print("=" * 120)

    cursor.execute("SELECT COUNT(*) FROM products WHERE category='module'")
    total_modules = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE category='module' AND price_euro IS NOT NULL AND price_euro > 0")
    modules_with_price = cursor.fetchone()[0]

    cursor.execute(
        "SELECT MIN(price_euro), MAX(price_euro), AVG(price_euro) FROM products WHERE category='module' AND price_euro > 0")
    stats = cursor.fetchone()

    print(f"Gesamt Module:        {total_modules}")
    print(f"Module mit Preis:     {modules_with_price}")
    print(f"Module OHNE Preis:    {total_modules - modules_with_price}")

    if stats[0]:
        print("\nPreis-Bereich:")
        print(f"  Min:  {stats[0]:>10.2f} €")
        print(f"  Max:  {stats[1]:>10.2f} €")
        print(f"  Ø:    {stats[2]:>10.2f} €")

    # Prüfe die spezifischen IDs aus dem Test
    print("\n" + "=" * 120)
    print("TEST-PRODUKTE (IDs aus test_multi_offer_workflow.py)")
    print("=" * 120)

    # Aiko, Solarfabrik, Trina, Viessmann, Aiko 445W
    test_ids = [1, 11, 16, 6, 151]

    for pid in test_ids:
        cursor.execute("""
            SELECT id, brand, model_name, price_euro, capacity_w
            FROM products
            WHERE category='module' AND id=?
        """, (pid,))
        row = cursor.fetchone()

        if row:
            price_str = f"{row[3]:.2f} €" if row[3] else "⚠️  KEIN PREIS!"
            print(
                f"ID {
                    row[0]:>3}: {
                    row[1]:<20} {
                    row[2]:<45} {
                    price_str:>15} ({
                        row[4]} W)")
        else:
            print(f"ID {pid:>3}: ❌ NICHT GEFUNDEN")

    conn.close()


if __name__ == "__main__":
    check_product_prices()
