#!/usr/bin/env python3
"""
Hilfsskript: Erzeugt ein "normales" 8‑seitiges Einzel‑PDF mit dem vorhandenen PDFGenerator.

Dieses Skript baut minimale Angebotsdaten auf, wählt die Kernmodule (Deckblatt,
Anschreiben, Angebotspositionen, Preisaufstellung, Wirtschaftlichkeit, Technische Daten
und eine benutzerdefinierte Seite) und rendert das PDF nach data/pdf_output/single.pdf.

Zweck: Reproduzierbarer, schlanker Einstiegspunkt für Tracing und Tests.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys

# Ensure project root on sys.path for imports
ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "tools" / "_stubs"
# Ensure stub overrides come first to avoid Streamlit side-effects
if str(STUBS) not in sys.path:
    sys.path.insert(0, str(STUBS))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pdf_generator import PDFGenerator


def main() -> None:
    root = ROOT
    out_dir = root / "data" / "pdf_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Minimale Angebotsdaten (keine externen DBs, nur Dummy‑Werte)
    offer_data = {
        "customer": {"name": "Max Mustermann"},
        "date": "2025-10-26",
        "offer_id": "TEST-0001",
        "items": [
            {"name": "PV‑Module (x8)", "quantity": 8, "unit_price": 250.0, "total_price": 2000.0},
            {"name": "Wechselrichter", "quantity": 1, "unit_price": 900.0, "total_price": 900.0},
        ],
        "net_total": 2900.0,
        "vat": 551.0,
        "grand_total": 3451.0,
    }

    # Kernmodule für ~8 Seiten
    module_order = [
        {"id": "deckblatt"},
        {"id": "anschreiben"},
        {"id": "angebotspositionen"},
        {"id": "preisaufstellung"},
        {"id": "wirtschaftlichkeit"},
        {"id": "technische_daten"},
        # Eine zusätzliche benutzerdefinierte Seite für die Seitenanzahl
        {"id": "benutzerdefiniert", "content": {"title": "Zusatzseite", "text": "Weitere Hinweise."}},
    ]

    pdf_path = out_dir / "single.pdf"
    gen = PDFGenerator(
        offer_data=offer_data,
        module_order=module_order,
        theme_name="Classic Light",
        filename=str(pdf_path),
        pricing_data={},
    )
    gen.create_pdf()
    print(f"PDF erzeugt: {pdf_path}")


if __name__ == "__main__":
    main()
