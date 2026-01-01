"""
create_app_icon.py
Erstellt ein einfaches App-Icon für die Anwendung

VERWENDUNG:
    python create_app_icon.py
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_icon():
    """Erstellt ein einfaches App-Icon mit Text"""
    
    # Icon-Größen für Windows .ico (mehrere Größen in einer Datei)
    sizes = [256, 128, 64, 48, 32, 16]
    
    # Erstelle Basis-Image (größte Größe)
    base_size = 256
    
    # Farben (anpassbar)
    bg_color = (41, 128, 185)  # Blau
    text_color = (255, 255, 255)  # Weiß
    accent_color = (52, 152, 219)  # Hellblau
    
    images = []
    
    for size in sizes:
        # Erstelle neues Image
        img = Image.new('RGBA', (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Zeichne Kreis/Rahmen
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=accent_color,
            outline=text_color,
            width=max(2, size // 40)
        )
        
        # Text hinzufügen (Initialen)
        text = "Ö"
        
        # Versuche Font zu laden, sonst default
        try:
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback auf default font
            font = ImageFont.load_default()
        
        # Text zentrieren
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = (
            (size - text_width) // 2,
            (size - text_height) // 2 - size // 20
        )
        
        # Zeichne Text mit Schatten
        shadow_offset = max(2, size // 60)
        draw.text(
            (position[0] + shadow_offset, position[1] + shadow_offset),
            text,
            fill=(0, 0, 0, 128),
            font=font
        )
        draw.text(position, text, fill=text_color, font=font)
        
        images.append(img)
    
    # Speichere als .ico
    output_dir = Path("data/company_logos")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "app_icon.ico"
    
    # Speichere als multi-size .ico
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    print(f"✓ Icon erstellt: {output_path}")
    print(f"  Größen: {', '.join(str(s) for s in sizes)}px")
    print(f"\nFühre nun aus: python build_exe_setup.py")
    
    return output_path

if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"✗ Fehler beim Erstellen des Icons: {e}")
        print("\nAlternative: Verwende ein Online-Tool wie:")
        print("  - https://icoconvert.com/")
        print("  - https://convertio.co/de/png-ico/")
        print("\nSpeichere das Icon dann unter: data/company_logos/app_icon.ico")
