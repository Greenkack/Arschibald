# === AUTO-GENERATED INSERT PATCH ===
# target_module: check_product_image_details.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import base64
import sqlite3


# --- DEF BLOCK START: func check_product_image_details ---
def check_product_image_details():
    try:
        conn = sqlite3.connect('data/app_data.db')
        cursor = conn.cursor()

        # Prüfe spezifisches Produkt
        cursor.execute(
            'SELECT model_name, brand, image_base64 FROM products WHERE model_name = ?',
            ("Vitovolt 300-DG M440HC",
             ))
        result = cursor.fetchone()

        if result:
            print(f'Modell: {result[0]}')
            print(f'Marke: {result[1]}')
            img_data = result[2] or ""
            print(f'Bild-Daten: {len(img_data)} Zeichen')

            if img_data:
                print(f'Erste 100 Zeichen: {img_data[:100]}')
                if len(img_data) > 100:
                    print(f'Letzte 100 Zeichen: {img_data[-100:]}')

                # Prüfe ob gültiges Base64
                try:
                    decoded = base64.b64decode(img_data)
                    print(
                        f'Base64-Validierung: ERFOLG - {len(decoded)} Bytes dekodiert')

                    # Prüfe ob Bild-Header vorhanden
                    if decoded.startswith(b'\x89PNG'):
                        print('Bildformat: PNG')
                    elif decoded.startswith(b'\xff\xd8'):
                        print('Bildformat: JPEG')
                    elif decoded.startswith(b'GIF'):
                        print('Bildformat: GIF')
                    else:
                        print(
                            f'Bildformat: Unbekannt (erste 20 Bytes: {decoded[:20]})')

                except Exception as e:
                    print(f'Base64-Validierung: FEHLER - {e}')
            else:
                print('Keine Bilddaten vorhanden')
        else:
            print('Produkt nicht gefunden')

        # Zeige auch andere Produkte mit Bildern
        print("\nAndere Produkte mit Bilddaten:")
        cursor.execute('''
            SELECT model_name, brand,
                   CASE WHEN image_base64 IS NOT NULL AND image_base64 != '' THEN LENGTH(image_base64) ELSE 0 END as img_len
            FROM products
            WHERE image_base64 IS NOT NULL AND image_base64 != ''
            LIMIT 5
        ''')

        for row in cursor.fetchall():
            print(f'  {row[0]} ({row[1]}): {row[2]} Zeichen')

        conn.close()

    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
# --- DEF BLOCK END ---
