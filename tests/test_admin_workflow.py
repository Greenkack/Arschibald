#!/usr/bin/env python3
"""
Simuliert den Admin-Panel Workflow zum Testen der Bild-Upload-Funktionalität
"""
from product_db import add_product, get_product_by_id, update_product
import base64
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def simulate_admin_panel_workflow():
    """Simuliert genau das, was im Admin-Panel passiert"""

    print("=== Simuliere Admin-Panel Workflow ===")

    # 1. Simuliere neues Produkt ohne Bild (wie im Admin-Panel)
    product_data_for_manual_form = {}  # Leere Daten für neues Produkt
    current_product_image_b64_form = product_data_for_manual_form.get(
        "image_base64")

    print(f"current_product_image_b64_form: {current_product_image_b64_form}")
    print(
        f"current_product_image_b64_form or '': {
            current_product_image_b64_form or ''}")

    # 2. Simuliere User-Input (wie im Formular)
    p_model_name_form = "Admin Test Produkt"
    p_category_form = "Modul"
    p_brand_form = "Test Brand"
    p_price_form = 500.0
    p_add_cost_form = 0.0
    p_warranty_form = 10
    p_description_form_val = "Test Beschreibung"

    # 3. Simuliere Bild-Upload
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    uploaded_product_image_b64 = base64.b64encode(png_data).decode('utf-8')
    # Simuliere dass ein File uploaded wurde
    uploaded_product_image_manual_file_form = True

    # 4. Simuliere Admin-Panel Logik (wie in der echten Funktion)
    product_data_to_save_db = {
        "model_name": p_model_name_form.strip(),
        "category": p_category_form,
        "brand": p_brand_form.strip(),
        "price_euro": p_price_form,
        "additional_cost_netto": p_add_cost_form,
        "warranty_years": p_warranty_form,
        "description": p_description_form_val.strip(),
        "image_base64": current_product_image_b64_form or "",  # Das war das Problem!
    }

    print(
        f"Initial product_data_to_save_db['image_base64']: '{
            product_data_to_save_db['image_base64']}'")

    # 5. Simuliere Bild-Verarbeitung
    if uploaded_product_image_manual_file_form:
        # In der echten App:
        # base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        new_image_b64 = uploaded_product_image_b64
        product_data_to_save_db["image_base64"] = new_image_b64
        print(
            f"Nach Bild-Upload: product_data_to_save_db['image_base64'] = {len(new_image_b64)} Zeichen")

    # 6. Simuliere Produkt-Erstellung
    print(
        f"Daten vor add_product: image_base64 = {
            len(
                product_data_to_save_db['image_base64'])} Zeichen")

    new_product_id = add_product(product_data_to_save_db)
    if new_product_id:
        print(f"✓ Neues Produkt erstellt mit ID: {new_product_id}")

        # 7. Überprüfe das gespeicherte Produkt
        saved_product = get_product_by_id(new_product_id)
        if saved_product:
            saved_image = saved_product.get('image_base64', '')
            print(f"✓ Gespeichertes Bild: {len(saved_image)} Zeichen")
            if len(saved_image) > 50:
                print("✓ Bild wurde erfolgreich gespeichert!")
            else:
                print("✗ Bild wurde nicht gespeichert")
        else:
            print("✗ Produkt konnte nicht abgerufen werden")
    else:
        print("✗ Produkt konnte nicht erstellt werden")


def test_existing_product_update():
    """Testet das Update eines bestehenden Produkts"""
    print("\n=== Test: Bestehendes Produkt aktualisieren ===")

    # Erstelle zuerst ein Produkt
    initial_product = {
        "model_name": "Update Test Produkt",
        "category": "Modul",
        "brand": "Test Brand",
        "price_euro": 400.0,
        "description": "Ursprüngliche Beschreibung"
    }

    product_id = add_product(initial_product)
    if not product_id:
        print("✗ Konnte kein Test-Produkt erstellen")
        return

    print(f"✓ Test-Produkt erstellt mit ID: {product_id}")

    # Simuliere Admin-Panel Update-Workflow
    product_data_for_manual_form = get_product_by_id(product_id)
    current_product_image_b64_form = product_data_for_manual_form.get(
        "image_base64")

    print(
        f"Aktuelles Bild: {
            len(current_product_image_b64_form) if current_product_image_b64_form else 0} Zeichen")

    # Simuliere neues Bild-Upload
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    new_image_b64 = base64.b64encode(png_data).decode('utf-8')

    # Update-Daten
    product_data_to_save_db = {
        "model_name": product_data_for_manual_form.get('model_name'),
        "category": product_data_for_manual_form.get('category'),
        "brand": product_data_for_manual_form.get('brand'),
        "price_euro": product_data_for_manual_form.get('price_euro'),
        "description": "AKTUALISIERTE Beschreibung",
        "image_base64": current_product_image_b64_form or "",
    }

    # Simuliere neues Bild
    product_data_to_save_db["image_base64"] = new_image_b64
    print(f"Neue Bild-Daten: {len(new_image_b64)} Zeichen")

    # Update ausführen
    success = update_product(product_id, product_data_to_save_db)
    if success:
        print("✓ Produkt-Update erfolgreich")

        # Überprüfung
        updated_product = get_product_by_id(product_id)
        if updated_product:
            updated_image = updated_product.get('image_base64', '')
            updated_desc = updated_product.get('description', '')
            print(f"✓ Aktualisiertes Bild: {len(updated_image)} Zeichen")
            print(f"✓ Aktualisierte Beschreibung: {updated_desc}")

            if len(updated_image) > 50 and "AKTUALISIERT" in updated_desc:
                print("✓ Update war vollständig erfolgreich!")
            else:
                print("✗ Update unvollständig")
        else:
            print("✗ Aktualisiertes Produkt konnte nicht abgerufen werden")
    else:
        print("✗ Produkt-Update fehlgeschlagen")


if __name__ == "__main__":
    simulate_admin_panel_workflow()
    test_existing_product_update()
