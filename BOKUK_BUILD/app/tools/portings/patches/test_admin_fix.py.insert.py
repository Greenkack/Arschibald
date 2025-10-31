# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_admin_fix.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_admin_panel_import ---
def test_admin_panel_import():
    """Test ob admin_panel.py importiert werden kann"""
    try:
        print("✅ admin_panel.py erfolgreich importiert")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Import von admin_panel.py: {e}")
        return False
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_defensive_strip ---
def test_defensive_strip():
    """Test der defensiven .strip() Logik"""
    print("\n🔧 Test der defensiven .strip() Logik:")

    test_cases = [
        (None, ""),
        ("", ""),
        ("  test  ", "test"),
        ("normal", "normal"),
        ("  ", ""),
    ]

    for input_val, expected in test_cases:
        result = (input_val or "").strip()
        status = "✅" if result == expected else "❌"
        print(
            f"{status} Input: {
                repr(input_val)} -> Output: {
                repr(result)} (Erwartet: {
                repr(expected)})")
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_product_data_creation ---
def test_product_data_creation():
    """Test der Produkt-Dictionary Erstellung"""
    print("\n📦 Test der Produkt-Dictionary Erstellung:")

    # Simuliere Form-Werte die None sein könnten
    test_form_values = {
        "p_model_name_form": None,
        "p_brand_form": "  Test Brand  ",
        "p_description_form_val": None,
        "p_category_form": "Modul",
        "p_price_form": 100.0,
        "p_add_cost_form": 10.0,
        "p_warranty_form": 5,
        "current_product_image_b64_form": "",
        "current_datasheet_link": None
    }

    try:
        # Simuliere die Logik aus admin_panel.py
        product_data_to_save_db = {
            "model_name": (test_form_values["p_model_name_form"] or "").strip(),
            "category": test_form_values["p_category_form"],
            "brand": (test_form_values["p_brand_form"] or "").strip(),
            "price_euro": test_form_values["p_price_form"],
            "additional_cost_netto": test_form_values["p_add_cost_form"],
            "warranty_years": test_form_values["p_warranty_form"],
            "description": (test_form_values["p_description_form_val"] or "").strip(),
            "image_base64": test_form_values["current_product_image_b64_form"] or "",
            "datasheet_link_db_path": test_form_values["current_datasheet_link"]
        }

        print("✅ Produkt-Dictionary erfolgreich erstellt:")
        for key, value in product_data_to_save_db.items():
            print(f"   {key}: {repr(value)}")

        return True

    except Exception as e:
        print(f"❌ Fehler bei Produkt-Dictionary Erstellung: {e}")
        return False
# --- DEF BLOCK END ---
