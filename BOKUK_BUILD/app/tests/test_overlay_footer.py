from pdf_template_engine import build_dynamic_data, generate_custom_offer_pdf
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
print("Footer Company:", dyn.get("footer_company"))
print("Footer Date:", dyn.get("footer_date"))

pdf_bytes = generate_custom_offer_pdf(
    coords_dir, bg_dir, dyn, additional_pdf=None)
out_path = base_dir / "out_main6_footer_test.pdf"
with open(out_path, "wb") as f:
    f.write(pdf_bytes)
print("Wrote:", out_path)
