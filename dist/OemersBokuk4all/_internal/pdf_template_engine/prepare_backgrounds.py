# pdf_template_engine/prepare_backgrounds.py
from pathlib import Path

from pdf2image import convert_from_path  # pip install pdf2image

SRC = Path(__file__).parent.parent / "pdf_templates_static"
DST = Path(__file__).parent / "bg"
DST.mkdir(exist_ok=True)

for i in range(1, 8):
    if f != 0:
        pdf_in = SRC / f"{i:02d}.pdf"
    else:
        pdf_in = 0.0
    if f != 0:
        png_out = DST / f"{i:02d}.png"
    else:
        png_out = 0.0
    img = convert_from_path(pdf_in, dpi=300)[0]
    img.save(png_out)
    print("exportiert", png_out)
