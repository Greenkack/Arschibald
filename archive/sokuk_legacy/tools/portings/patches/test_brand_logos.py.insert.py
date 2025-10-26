# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_brand_logos.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import base64

from brand_logo_db import add_brand_logo, get_brand_logo, list_all_brand_logos


# --- DEF BLOCK START: func create_test_logo_png ---
def create_test_logo_png(
        brand_name: str,
        width: int = 120,
        height: int = 40) -> str:
    """Erstellt ein einfaches PNG-Logo mit Text für Testzwecke"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Einfaches Logo mit Marken-Namen
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # Versuche eine einfache Schrift zu finden
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except BaseException:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
            except BaseException:
                font = ImageFont.load_default()

        # Text zentriert zeichnen
        bbox = draw.textbbox((0, 0), brand_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Rahmen und Text
        draw.rectangle([2, 2, width - 2, height - 2], outline='black', width=2)
        draw.text((x, y), brand_name, fill='black', font=font)

        # Als Base64 konvertieren
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return img_base64

    except ImportError:
        print("PIL nicht verfügbar - erstelle minimales PNG")
        # Fallback: Minimales 1x1 PNG
        minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00x\x00\x00\x00(\x08\x02\x00\x00\x00\x15\xbf\xf7\x96\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0eIDATx\xdac\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(minimal_png).decode('utf-8')
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_logo_system ---
def test_logo_system():
    """Testet das Brand-Logo-System"""
    print("🔧 Teste Brand-Logo-System...")

    # Test-Marken
    test_brands = [
        "SunPower",
        "Huawei",
        "Fronius",
        "SolarEdge",
        "BYD",
        "Trina Solar",
        "Q CELLS",
        "Goodwe"
    ]

    print("\n1. Erstelle Test-Logos...")
    for brand in test_brands:
        try:
            logo_b64 = create_test_logo_png(brand)
            success = add_brand_logo(brand, logo_b64, "PNG")
            if success:
                print(f"✓ Logo für '{brand}' hinzugefügt")
            else:
                print(f"✗ Fehler beim Hinzufügen von '{brand}'")
        except Exception as e:
            print(f"✗ Fehler bei '{brand}': {e}")

    print("\n2. Liste alle Logos auf...")
    logos = list_all_brand_logos()
    print(f"Gefundene Logos: {len(logos)}")
    for logo in logos:
        print(f"  - {logo['brand_name']} ({logo['logo_format']})")

    print("\n3. Teste Logo-Abruf...")
    for brand in ["Huawei", "Fronius", "Nicht-Existierend"]:
        logo_data = get_brand_logo(brand)
        if logo_data:
            print(
                f"✓ Logo für '{brand}' gefunden (Format: {
                    logo_data['logo_format']})")
        else:
            print(f"✗ Kein Logo für '{brand}' gefunden")

    print("\n✅ Test abgeschlossen!")
# --- DEF BLOCK END ---
