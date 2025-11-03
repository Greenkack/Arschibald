#!/usr/bin/env python3
"""
Skript zum Hinzufügen von Test-Produktbildern zur Datenbank
"""
import base64
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_db import list_products, update_product_image


def create_test_image_base64():
    """Erstellt ein kleines Test-Bild als Base64-String"""
    # Erstelle ein minimales PNG (1x1 Pixel, transparent)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(png_data).decode('utf-8')

def create_simple_svg_image():
    """Erstellt ein einfaches SVG-Bild als Base64"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="150" fill="#E3F2FD" stroke="#1976D2" stroke-width="2"/>
  <text x="100" y="75" text-anchor="middle" font-family="Arial" font-size="14" fill="#1976D2">
    Solar Produkt
  </text>
  <circle cx="50" cy="40" r="15" fill="#FFC107"/>
  <rect x="80" y="100" width="40" height="25" fill="#4CAF50"/>
  <polygon points="150,120 170,100 170,140" fill="#FF5722"/>
</svg>'''
    return base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

def add_test_images_to_products():
    """Fügt Testbilder zu Produkten ohne Bilder hinzu"""
    try:
        products = list_products()  # Alle Produkte
        test_image_b64 = create_simple_svg_image()

        print(f"Testbild erstellt: {len(test_image_b64)} Zeichen")
        print(f"Erste 50 Zeichen: {test_image_b64[:50]}...")

        updated_count = 0
        for product in products:
            product_id = product.get('id')
            model_name = product.get('model_name', 'Unbekannt')
            current_image = product.get('image_base64', '')

            # Nur aktualisieren wenn kein gültiges Bild vorhanden
            if not current_image or len(current_image) < 100:
                print(f"Aktualisiere Produkt {product_id}: {model_name}")
                success = update_product_image(product_id, test_image_b64)
                if success:
                    updated_count += 1
                    print("  ✓ Bild hinzugefügt")
                else:
                    print("  ✗ Fehler beim Hinzufügen")
            else:
                print(f"Überspringe {model_name} (hat bereits Bild: {len(current_image)} Zeichen)")

        print(f"\nErgebnis: {updated_count} Produkte mit Testbildern aktualisiert")

    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

def verify_images():
    """Überprüft die Bilder in der Datenbank"""
    try:
        products = list_products()  # Alle Produkte

        with_images = 0
        without_images = 0

        print("Produktbilder-Status nach Update:")
        for product in products[:10]:  # Erste 10 zeigen
            model_name = product.get('model_name', 'Unbekannt')
            brand = product.get('brand', 'Unbekannt')
            image_data = product.get('image_base64', '')

            if image_data and len(image_data) > 50:
                status = f"✓ {len(image_data)} Zeichen"
                with_images += 1
            else:
                status = f"✗ {len(image_data) if image_data else 0} Zeichen"
                without_images += 1

            print(f"{model_name} ({brand}): {status}")

        total = len(products)
        print(f"\nGesamtstatistik: {with_images}/{total} Produkte haben gültige Bilder")

    except Exception as e:
        print(f"Fehler bei Verifikation: {e}")

if __name__ == "__main__":
    print("=== Test-Produktbilder hinzufügen ===")
    add_test_images_to_products()
    print("\n=== Verifikation ===")
    verify_images()
