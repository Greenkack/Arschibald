import os

import fitz  # PyMuPDF

# === KONFIGURATION ===
input_ordner = r"C:\123456\12345\PDF\input"
output_ordner = r"C:\123456\12345\PDF\output"

# === Funktion: PDF-Seiten als PNG speichern ===
def pdfs_zu_bildern(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    for datei in os.listdir(input_path):
        if not datei.lower().endswith(".pdf"):
            continue

        pdf_pfad = os.path.join(input_path, datei)
        doc = fitz.open(pdf_pfad)
        basisname = os.path.splitext(datei)[0]

        for seite_nummer in range(len(doc)):
            seite = doc.load_page(seite_nummer)
            bild = seite.get_pixmap(dpi=150)  # dpi=150 = gute Qualität

            bild_name = f"{basisname}_S{seite_nummer + 1}.png"
            bild_pfad = os.path.join(output_path, bild_name)
            bild.save(bild_pfad)

            print(f"✅ Seite {seite_nummer + 1} von {datei} gespeichert als Bild.")

        doc.close()

    print("\n🎉 Alle PDFs wurden erfolgreich in PNGs umgewandelt.")

# === AUSFÜHRUNG ===
pdfs_zu_bildern(input_ordner, output_ordner)
