# === AUTO-GENERATED INSERT PATCH ===
# target_module: pdf_template_engine/merger.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import io

from pypdf import PdfReader, PdfWriter


# --- DEF BLOCK START: func merge_first_seven_pages ---
def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))

    for i in range(1, 8):
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i - 1])    # Overlay drüber
        writer.add_page(base)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
# --- DEF BLOCK END ---
