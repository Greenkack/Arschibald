import os
import pathlib

import fitz  # PyMuPDF (Basis für Detailanalyse)
import pymupdf4llm

# Eingabedatei definieren
INPUT_PDF = "pdf_templates_static/06.pdf"
OUTPUT_DIR = "output"
MARKDOWN_OUTPUT = os.path.join(OUTPUT_DIR, "output.md")

# Output-Ordner erstellen, falls nötig
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Markdown-Text aus PDF erstellen (Basisversion mit pymupdf4llm)
md_text = pymupdf4llm.to_markdown(INPUT_PDF)

# Markdown-Datei speichern
pathlib.Path(MARKDOWN_OUTPUT).write_bytes(md_text.encode("utf-8"))

# Detaillierte PDF-Analyse mit fitz (PyMuPDF)
doc = fitz.open(INPUT_PDF)

# Analyse jeder einzelnen PDF-Seite (Detailtiefe 100%)
for page_num, page in enumerate(doc, start=1):

    # 1. Texte detailliert (Positionen, Schriftarten, Größen, Farben)
    textfile = os.path.join(OUTPUT_DIR, f"seite_{page_num}_texte.txt")
    with open(textfile, "w", encoding="utf-8") as tf:
        dict_text = page.get_text("dict")
        for block in dict_text["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        tf.write(
                            f"Text: {span['text']}\n"
                            f"Position: {span['bbox']}\n"
                            f"Schriftart: {span['font']}\n"
                            f"Schriftgröße: {span['size']}\n"
                            f"Farbe: {span['color']}\n"
                            f"{'-' * 40}\n"
                        )

    # 2. Bilder exakt extrahieren und Position speichern
    for img_index, img in enumerate(page.get_images(full=True), start=1):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        img_path = os.path.join(
            OUTPUT_DIR,
            f"seite_{page_num}_bild_{img_index}.{image_ext}")
        with open(img_path, "wb") as img_file:
            img_file.write(image_bytes)

        rects = page.get_image_rects(xref)
        rectfile = os.path.join(OUTPUT_DIR,
                                f"seite_{page_num}_bilder_positionen.txt")
        with open(rectfile, "a", encoding="utf-8") as rf:
            for rect in rects:
                rf.write(f"Bild {img_index}: {rect}\n")

    # 3. Diagramme, Linien, Rechtecke und Kurven exakt erfassen
    drawings = page.get_drawings()
    shape_file = os.path.join(OUTPUT_DIR, f"seite_{page_num}_formen.txt")
    with open(shape_file, "w", encoding="utf-8") as sf:
        for draw_index, drawing in enumerate(drawings, start=1):
            sf.write(f"Zeichnung {draw_index}\n")
            sf.write(f"Farbe: {drawing.get('color')}\n")
            sf.write(f"Linienstärke: {drawing.get('width')}\n")
            for item in drawing["items"]:
                typ, details = item[0], item[1:]
                if typ == "l":
                    sf.write(f"Linie von {details[0]} nach {details[1]}\n")
                elif typ == "re":
                    sf.write(f"Rechteck: {details}\n")
                elif typ == "qu":
                    sf.write(f"Quadratische Kurve: {details}\n")
                elif typ == "c":
                    sf.write(f"Bezier-Kurve: {details}\n")
            sf.write("-" * 40 + "\n")

    # 4. Annotationen & Markierungen exakt erfassen
    annots = page.annots()
    if annots:
        annotfile = os.path.join(
            OUTPUT_DIR, f"seite_{page_num}_annotationen.txt")
        with open(annotfile, "w", encoding="utf-8") as af:
            for annot in annots:
                af.write(
                    f"Typ: {annot.type[1]}\n"
                    f"Inhalt: {annot.info.get('content')}\n"
                    f"Position: {annot.rect}\n"
                    f"Farbe: {annot.colors}\n"
                    f"{'-' * 40}\n"
                )

    # 5. Exakte Seiteninformationen (Größe, Nummer, Rotation)
    pagefile = os.path.join(OUTPUT_DIR, f"seite_{page_num}_details.txt")
    with open(pagefile, "w", encoding="utf-8") as pf:
        pf.write(f"Seitengröße: {page.rect}\n")
        pf.write(f"Rotation: {page.rotation}\n")
        pf.write(f"Nummer: {page.number + 1}\n")
        pf.write(f"{'-' * 40}\n")

print(" Markdown-Datei und vollständige PDF-Auswertung 100% exakt abgeschlossen!")
