#!/usr/bin/env python3
"""
Erstellt PNG-Testbilder für Produktdatenbank
"""
from product_db import list_products, update_product_image
import base64
import io
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_png_test_image():
    """Erstellt ein PNG-Testbild programmatisch"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Erstelle ein 200x150 Bild
        img = Image.new('RGB', (200, 150), color='#E3F2FD')
        draw = ImageDraw.Draw(img)

        # Rahmen
        draw.rectangle([(0, 0), (199, 149)], outline='#1976D2', width=2)

        # Text
        try:
            # Versuche eine Standard-Schriftart zu laden
            font = ImageFont.truetype("arial.ttf", 14)
        except BaseException:
            # Fallback auf Default-Font
            font = ImageFont.load_default()

        draw.text((100, 75), "Solar Produkt",
                  fill='#1976D2', anchor='mm', font=font)

        # Einfache Formen
        draw.ellipse([(35, 25), (65, 55)], fill='#FFC107')  # Sonne
        draw.rectangle([(80, 100), (120, 125)], fill='#4CAF50')  # Modul
        draw.polygon([(150, 120), (170, 100), (170, 140)],
                     fill='#FF5722')  # Dreiecks-Symbol

        # In Bytes umwandeln
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()

        return base64.b64encode(png_bytes).decode('utf-8')

    except ImportError:
        print("PIL/Pillow nicht verfügbar, erstelle minimales PNG")
        # Minimales 1x1 PNG wenn PIL nicht verfügbar
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(png_data).decode('utf-8')


def update_products_with_png():
    """Aktualisiert alle Produkte mit PNG-Testbildern"""
    try:
        png_b64 = create_png_test_image()
        print(f"PNG-Testbild erstellt: {len(png_b64)} Zeichen")

        products = list_products()
        updated = 0

        for product in products[:5]:  # Nur erste 5 für Test
            product_id = product.get('id')
            model_name = product.get('model_name', 'Unbekannt')

            print(f"Aktualisiere Produkt {product_id}: {model_name}")
            success = update_product_image(product_id, png_b64)
            if success:
                updated += 1
                print("  ✓ PNG-Bild gesetzt")
            else:
                print("  ✗ Fehler")

        print(f"\nErgebnis: {updated} Produkte mit PNG-Bildern aktualisiert")

    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    update_products_with_png()
