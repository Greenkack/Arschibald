#!/usr/bin/env python3
import sqlite3


def check_product_images():
    try:
        conn = sqlite3.connect('data/app_data.db')
        cursor = conn.cursor()

        # Prüfe alle Produkte auf Bilder
        cursor.execute('''
            SELECT model_name, brand,
                   CASE WHEN image_base64 IS NOT NULL AND image_base64 != '' THEN 1 ELSE 0 END as has_image
            FROM products
            LIMIT 10
        ''')

        results = cursor.fetchall()
        print("Produktbilder-Status:")
        for r in results:
            status = "Ja" if r[2] else "Nein"
            print(f'{r[0]} ({r[1]}): {status}')

        # Zähle Produkte mit/ohne Bilder
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN image_base64 IS NOT NULL AND image_base64 != '' THEN 1 ELSE 0 END) as with_images
            FROM products
        ''')

        total, with_images = cursor.fetchone()
        print(f"\nStatistik: {with_images}/{total} Produkte haben Bilder")

        conn.close()

    except Exception as e:
        print(f"Fehler: {e}")


if __name__ == "__main__":
    check_product_images()
