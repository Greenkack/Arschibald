from pdf_template_engine import build_dynamic_data, generate_custom_offer_pdf
from pypdf import PdfReader
import io
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))


coords_dir = base_dir / "coords"
bg_dir = base_dir / "pdf_templates_static" / "notext"

project_data = {}
analysis_results = {}
company_info = {
    "name": "DING Solar GmbH",
    "short_name": "DING",
    "city": "Hamburg",
    "zip_code": "22359"}

dyn = build_dynamic_data(project_data, analysis_results, company_info)

# Zusatz-PDF erzeugen (1 Seite)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception as e:
    raise SystemExit(f"ReportLab erforderlich für diesen Test: {e}")

buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=A4)
c.setFont("Helvetica", 12)
c.drawString(72, 800, "Zusatzseite Test")
c.showPage()
c.save()
additional_pdf = buf.getvalue()

# Mit Zusatzseiten
pdf_with = generate_custom_offer_pdf(
    coords_dir, bg_dir, dyn, additional_pdf=additional_pdf)
with_path = base_dir / "out_numbering_with.pdf"
with open(with_path, "wb") as f:
    f.write(pdf_with)
reader_with = PdfReader(io.BytesIO(pdf_with))
print("with_additional_pages_count:", len(reader_with.pages))

# Ohne Zusatzseiten
pdf_without = generate_custom_offer_pdf(
    coords_dir, bg_dir, dyn, additional_pdf=None)
without_path = base_dir / "out_numbering_without.pdf"
with open(without_path, "wb") as f:
    f.write(pdf_without)
reader_without = PdfReader(io.BytesIO(pdf_without))
print("without_additional_pages_count:", len(reader_without.pages))

print("OK: wrote", with_path, "and", without_path)
