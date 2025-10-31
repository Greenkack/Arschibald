# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_admin_upload.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import base64

from product_db import add_product, get_product_by_id, update_product


# --- DEF BLOCK START: func test_product_update ---
def test_product_update():
    """Testet das Hinzufügen und Aktualisieren von Produkten mit Bildern"""

    # Erstelle ein minimales PNG-Bild
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    test_image_b64 = base64.b64encode(png_data).decode('utf-8')

    print("=== Test: Produkt mit Bild hinzufügen ===")

    # Neues Testprodukt erstellen
    test_product = {
        "model_name": "Test Produkt Upload",
        "category": "Modul",
        "brand": "Test Brand",
        "price_euro": 500.0,
        "image_base64": test_image_b64,
        "description": "Test Produkt für Upload-Test"
    }

    # Produkt hinzufügen
    new_id = add_product(test_product)
    if new_id:
        print(f"✓ Neues Produkt erstellt mit ID: {new_id}")

        # Produkt abrufen und prüfen
        retrieved = get_product_by_id(new_id)
        if retrieved:
            image_data = retrieved.get('image_base64', '')
            print(f"✓ Produkt abgerufen: {retrieved.get('model_name')}")
            print(f"✓ Bild-Daten: {len(image_data)} Zeichen")
            if image_data and len(image_data) > 50:
                print("✓ Bild erfolgreich gespeichert")
            else:
                print("✗ Bild nicht gespeichert oder zu kurz")
        else:
            print("✗ Produkt konnte nicht abgerufen werden")

        print("\n=== Test: Produkt-Bild aktualisieren ===")

        # Neues Bild (länger)
        larger_png_data = png_data + b'\x00' * 100  # Mache das Bild "größer"
        new_image_b64 = base64.b64encode(larger_png_data).decode('utf-8')

        # Update testen
        update_data = {
            "image_base64": new_image_b64,
            "description": "Test Produkt für Upload-Test - AKTUALISIERT"
        }

        success = update_product(new_id, update_data)
        if success:
            print("✓ Produkt-Update erfolgreich")

            # Erneut abrufen
            updated = get_product_by_id(new_id)
            if updated:
                new_image_data = updated.get('image_base64', '')
                new_desc = updated.get('description', '')
                print(
                    f"✓ Aktualisierte Bild-Daten: {len(new_image_data)} Zeichen")
                print(f"✓ Aktualisierte Beschreibung: {new_desc}")

                if len(new_image_data) > len(image_data):
                    print("✓ Bild wurde erfolgreich aktualisiert")
                else:
                    print("✗ Bild-Update fehlgeschlagen")
            else:
                print("✗ Aktualisiertes Produkt konnte nicht abgerufen werden")
        else:
            print("✗ Produkt-Update fehlgeschlagen")

    else:
        print("✗ Produkt konnte nicht erstellt werden")
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_admin_functions ---
def test_admin_functions():
    """Testet die Admin-Panel Funktionen direkt"""
    print("\n=== Test: Admin-Panel Funktionen ===")

    try:
        from admin_panel import render_product_management
        print("✓ Admin-Panel Modul importiert")

        # Teste, ob die Funktion callable ist
        if callable(render_product_management):
            print("✓ render_product_management ist aufrufbar")
        else:
            print("✗ render_product_management ist nicht aufrufbar")

    except ImportError as e:
        print(f"✗ Admin-Panel Import-Fehler: {e}")
    except Exception as e:
        print(f"✗ Allgemeiner Fehler: {e}")
# --- DEF BLOCK END ---
