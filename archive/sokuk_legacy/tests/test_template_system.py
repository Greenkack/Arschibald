#!/usr/bin/env python
"""
Direkter Test des PDF-Template-Systems
=====================================
Prüft ob die Templates korrekt geladen werden
"""

import os
from pathlib import Path


def test_pdf_templates():
    """Teste ob die PDF-Templates verfügbar sind"""

    print("=== PDF-TEMPLATE-SYSTEM TEST ===")

    base_dir = os.path.dirname(__file__)
    template_dir = Path(base_dir) / "pdf_templates_static" / "notext"
    coords_dir = Path(base_dir) / "coords"

    print(f"Template-Verzeichnis: {template_dir}")
    print(f"Koordinaten-Verzeichnis: {coords_dir}")

    # Prüfe Template-Dateien
    pv_templates = []
    hp_templates = []

    for i in range(1, 8):
        pv_file = template_dir / f"nt_nt_{i:02d}.pdf"
        hp_file = template_dir / f"hp_nt_{i:02d}.pdf"

        if pv_file.exists():
            size = pv_file.stat().st_size
            pv_templates.append(f"✅ {pv_file.name} ({size:,} bytes)")
        else:
            pv_templates.append(f"❌ {pv_file.name} (fehlt)")

        if hp_file.exists():
            size = hp_file.stat().st_size
            hp_templates.append(f"✅ {hp_file.name} ({size:,} bytes)")
        else:
            hp_templates.append(f"❌ {hp_file.name} (fehlt)")

    print("\n📄 Photovoltaik-Templates (nt_nt_XX.pdf):")
    for template in pv_templates:
        print(f"  {template}")

    print("\n🔥 Wärmepumpen-Templates (hp_nt_XX.pdf):")
    for template in hp_templates:
        print(f"  {template}")

    # Prüfe YAML-Koordinaten
    yaml_files = []
    for i in range(1, 8):
        yaml_file = coords_dir / f"seite{i}.yml"
        if yaml_file.exists():
            size = yaml_file.stat().st_size
            yaml_files.append(f"✅ {yaml_file.name} ({size:,} bytes)")
        else:
            yaml_files.append(f"❌ {yaml_file.name} (fehlt)")

    print("\n📐 YAML-Koordinaten:")
    for yaml_file in yaml_files:
        print(f"  {yaml_file}")

    # Teste Template-Engine Import
    print("\n🔧 Template-Engine Test:")
    try:
        from pdf_template_engine import (
            merge_with_background,
        )
        print("  ✅ pdf_template_engine erfolgreich importiert")

        # Teste ob merge_with_background die Templates findet
        import io

        from PyPDF2 import PdfWriter

        # Erstelle ein Dummy-Overlay mit 7 Seiten
        writer = PdfWriter()
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        for i in range(7):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.drawString(100, 750, f"Test Overlay Seite {i + 1}")
            c.save()
            buffer.seek(0)

            from PyPDF2 import PdfReader
            reader = PdfReader(buffer)
            writer.add_page(reader.pages[0])

        # Speichere Dummy-Overlay
        overlay_buffer = io.BytesIO()
        writer.write(overlay_buffer)
        overlay_buffer.seek(0)
        overlay_bytes = overlay_buffer.getvalue()

        print(f"  ✅ Dummy-Overlay erstellt ({len(overlay_bytes):,} bytes)")

        # Teste merge_with_background
        result_bytes = merge_with_background(overlay_bytes, template_dir)

        if result_bytes and len(result_bytes) > 0:
            print(
                f"  ✅ Template-Merge erfolgreich ({len(result_bytes):,} bytes)")

            # Speichere Test-PDF
            test_output = Path(base_dir) / "test_template_merge.pdf"
            with open(test_output, 'wb') as f:
                f.write(result_bytes)
            print(f"  📁 Test-PDF gespeichert: {test_output}")

            return True
        print("  ❌ Template-Merge fehlgeschlagen (keine Ausgabe)")
        return False

    except Exception as e:
        print(f"  ❌ Template-Engine Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_templates()
    if success:
        print("\n🎉 TEMPLATE-SYSTEM FUNKTIONIERT!")
        print("Die PDF-Templates werden korrekt geladen und gemergt.")
    else:
        print("\n❌ TEMPLATE-SYSTEM DEFEKT!")
        print("Es gibt Probleme beim Laden der Templates.")
