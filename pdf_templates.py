"""
pdf_templates.py

Einfache Standard-Textvorlagen für den PDF-Generator.

Diese Datei stellt Fallback-Vorlagen bereit, damit der PDF-Generator
ohne externe Abhängigkeiten lauffähig ist. Die Funktionen liefern
schlichte, gut formatierte Standardtexte zurück.
"""
from __future__ import annotations

from typing import Any


def get_cover_letter_template(*, customer_name: str = "Kunde", offer_id: str | int | None = None, **_: Any) -> str:
    """Liefert einen einfachen Anschreiben-Text als Vorlage."""
    offer_line = f" (Angebots-Nr.: {offer_id})" if offer_id else ""
    return (
        f"Sehr geehrte Damen und Herren,\n\n"
        f"vielen Dank für Ihr Interesse an unserer Photovoltaik-Lösung{offer_line}. "
        f"Gerne unterbreiten wir Ihnen ein individuelles Angebot.\n\n"
        f"Mit freundlichen Grüßen\nIhr Beratungsteam"
    )


def get_project_summary_template(*, project_title: str | None = None, **_: Any) -> str:
    """Liefert einen einfachen Projekt-Zusammenfassungstext."""
    title = project_title or "Projektübersicht"
    return (
        f"{title}\n\n"
        "Dieses Dokument fasst die wichtigsten Eckdaten Ihres PV-Projekts zusammen.\n"
        "Es enthält Angebotspositionen, Preisübersicht und eine kurze Wirtschaftlichkeitsbetrachtung."
    )
