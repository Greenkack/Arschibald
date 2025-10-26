# === AUTO-GENERATED INSERT PATCH ===
# target_module: simple_logo_test.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from brand_logo_db import get_logos_for_brands
from pdf_template_engine.placeholders import build_dynamic_data


# --- DEF BLOCK START: func test_logo_data_preparation ---
def test_logo_data_preparation():
    """Testet die Vorbereitung der Logo-Daten"""
    print("🔍 TESTE LOGO-DATEN-VORBEREITUNG")
    print("=" * 50)

    # Simuliere Projektdaten mit Produkten von Herstellern, die Logos haben
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann"
        },
        "project_details": {},
        "selected_products": {
            "module": {
                "product_id": 1,
                "brand_name": "Huawei",  # Hat ein Logo
                "product_name": "SUN2000-8KTL-M1"
            },
            "inverter": {
                "product_id": 2,
                "brand_name": "GoodWe",  # Hat ein Logo
                "product_name": "GW8K-ET"
            },
            "storage": {
                "product_id": 3,
                "brand_name": "BYD",  # Hat ein Logo
                "product_name": "Battery-Box Premium HVM"
            }
        }
    }

    analysis_results = {
        "total_investment_netto": 15000,
        "anlage_kwp": 8.5
    }

    company_info = {
        "name": "Solar GmbH"
    }

    # Baue dynamic_data auf
    dynamic_data = build_dynamic_data(
        project_data, analysis_results, company_info)

    print("📊 Dynamic Data Ergebnis:")
    logo_keys = [k for k in dynamic_data.keys() if 'logo' in k.lower()]
    print(f"  Logo-bezogene Keys gefunden: {len(logo_keys)}")

    for key in logo_keys:
        value = dynamic_data[key]
        value_preview = value[:50] + "..." if len(str(value)) > 50 else value
        print(f"    {key}: {value_preview}")

    # Prüfe spezifisch die Brand-Logo Keys
    brand_logo_keys = [
        "module_brand_logo_b64",
        "inverter_brand_logo_b64",
        "storage_brand_logo_b64"]

    print("\n🎯 Spezifische Brand-Logo Checks:")
    for key in brand_logo_keys:
        if key in dynamic_data and dynamic_data[key]:
            print(
                f"  ✅ {key}: LOGO VORHANDEN ({len(dynamic_data[key])} Zeichen)")
        else:
            print(f"  ❌ {key}: LEER ODER FEHLT")

    return len([k for k in brand_logo_keys if dynamic_data.get(k)])
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_direct_logo_fetch ---
def test_direct_logo_fetch():
    """Testet direkten Logo-Abruf"""
    print("\n🔗 TESTE DIREKTEN LOGO-ABRUF")
    print("=" * 50)

    brands = ["Huawei", "GoodWe", "BYD"]
    logos = get_logos_for_brands(brands)

    for brand in brands:
        if brand in logos:
            logo_data = logos[brand]
            b64_length = len(logo_data.get('logo_base64', ''))
            print(f"  ✅ {brand}: Logo gefunden ({b64_length} Zeichen)")
        else:
            print(f"  ❌ {brand}: Kein Logo gefunden")

    return len(logos)
# --- DEF BLOCK END ---
