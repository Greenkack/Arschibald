import zipfile
import os
from pathlib import Path

# Pfad zu deinem Ordner
root = Path(r"C:\Users\win10\Desktop\Bokuk2 - Kopie\pdf_templates_static")

firmen = [f"Firma {i}" for i in range(1, 7)]

def merge_zips(zip_a, zip_b, out_zip):
    with zipfile.ZipFile(zip_a, 'r') as zip1, \
         zipfile.ZipFile(zip_b, 'r') as zip2, \
         zipfile.ZipFile(out_zip, 'w') as merged:

        # 1) Inhalte aus ZIP A übernehmen
        for item in zip1.infolist():
            merged.writestr(item, zip1.read(item.filename))

        # 2) Inhalte aus ZIP B hinzufügen oder ersetzen
        for item in zip2.infolist():
            merged.writestr(item, zip2.read(item.filename))

    print(f"✔ {out_zip.name} erstellt")

for firma in firmen:
    zip_a = root / f"{firma} Koordinaten.zip"
    zip_b = root / f"{firma} Templates.zip"
    out_zip = root / f"{firma} Merged.zip"

    if zip_a.exists() and zip_b.exists():
        merge_zips(zip_a, zip_b, out_zip)
    else:
        print(f"⚠ Dateien für {firma} fehlen")
