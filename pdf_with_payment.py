"""
pdf_with_payment.py
-------------------

Dieses Modul stellt eine vereinfachte Schnittstelle bereit, um ein
Angebots‑PDF zu erzeugen, das neben den regulären Seiten auch eine
Zusammenstellung der Kosten und den ausgewählten Zahlungsplan enthält.

Die Funktion `generate_offer_pdf_with_payment_terms` baut auf
`generate_main_template_pdf_bytes` aus `pdf_generator` auf und hängt
eine zusätzliche Seite an, die mittels `create_payment_summary_page`
erstellt wird. Damit bleibt die bestehende Logik unangetastet und
erweiterbar.

"""

from __future__ import annotations

from typing import Any

from payment_terms import compute_payment_schedule
from pdf_payment_summary import create_payment_summary_page

try:
    from pdf_generator import generate_main_template_pdf_bytes
    _PDF_GEN_AVAILABLE = True
except Exception:
    _PDF_GEN_AVAILABLE = False


def generate_offer_pdf_with_payment_terms(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
    variant_id: str,
) -> bytes | None:
    """Erzeugt ein Angebots‑PDF mit angehängter Seite für Kosten und Zahlungsplan.

    Args:
        project_data: Projektinformationen, wie sie auch an den Standard
            PDF‑Generator übergeben werden.
        analysis_results: Ergebnisse aus den Kostenberechnungen.
        company_info: Firmeninformationen.
        variant_id: ID der auszuwählenden Zahlungsvariante.

    Returns:
        bytes oder None: PDF‑Bytes, wenn der Generator verfügbar ist.
    """
    if not _PDF_GEN_AVAILABLE:
        return None
    total_brutto = float(analysis_results.get('total_investment_brutto', 0.0) or 0.0)
    schedule = compute_payment_schedule(variant_id, total_brutto)
    add_pdf = create_payment_summary_page(
        analysis_results=analysis_results,
        variant_id=variant_id,
        schedule=schedule,
    )
    return generate_main_template_pdf_bytes(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        additional_pdf=add_pdf,
    )
