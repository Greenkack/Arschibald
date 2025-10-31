"""
pdf_payment_summary.py
----------------------

Dieses Modul erzeugt eine zusätzliche PDF‑Seite, auf der die
Kostenzusammenstellung und die ausgewählten Zahlungsmodalitäten
dargestellt werden. Die Seite kann als `additional_pdf` an
`generate_main_template_pdf_bytes` übergeben oder separat an eine
bestehende PDF angehängt werden.

Die Funktion `create_payment_summary_page` erwartet die Analyseergebnisse
(`analysis_results`), sowie die ausgewählte Zahlungsvariante. Sie
verwendet die Funktionen aus `payment_terms.py`, um den Zahlungsplan
und den erläuternden Text zu berechnen.

Wichtig: Die erzeugte Seite ist bewusst minimal gehalten und nutzt
einfache Zeichnungsbefehle. Bei Bedarf kann die Gestaltung erweitert
werden (z.B. Tabellen, Farben oder Icons). Sollte `reportlab` nicht
installiert sein, liefert die Funktion `None` zurück.
"""

from __future__ import annotations

import io
from typing import Any

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    _REPORTLAB_AVAILABLE = True
except Exception:
    _REPORTLAB_AVAILABLE = False

from payment_terms import compute_payment_schedule, get_payment_terms_text


def _format_currency(value: float) -> str:
    """Hilfsfunktion zur Formatierung eines Eurobetrags.

    Einfache Formatierung mit zwei Dezimalstellen und Punkt als
    Dezimaltrennzeichen (deutsches Format ohne Tausendertrennzeichen).

    Args:
        value: Betrag.

    Returns:
        formatierter String
    """
    try:
        return f"{value:,.2f} €".replace(",", ".")
    except Exception:
        return f"{value} €"


def _collect_additional_costs(analysis_results: dict[str, Any]) -> tuple[list[tuple[str, float]], float]:
    """Extrahiert Zusatzkosten aus den Analyseergebnissen.

    Bestimmte Schlüssel werden interpretiert und als Aufpreis
    aufgelistet. Die Summe der so gefundenen Werte wird ebenfalls
    zurückgegeben.

    Args:
        analysis_results: Analyseergebnisse aus der Berechnung.

    Returns:
        (Liste[(Label, Betrag)], Summe)
    """
    cost_keys = {
        'cost_modules_aufpreis_netto': 'Modul‑Aufpreis',
        'cost_inverter_aufpreis_netto': 'Wechselrichter‑Aufpreis',
        'cost_storage_aufpreis_product_db_netto': 'Speicher‑Aufpreis',
        'total_optional_components_cost_netto': 'Optionale Komponenten',
        'cost_accessories_aufpreis_netto': 'Zubehör',
        'cost_scaffolding_netto': 'Gerüstkosten',
        'cost_misc_netto': 'Sonstige Kosten',
        'cost_custom_netto': 'Individuelle Kosten',
    }
    items: list[tuple[str, float]] = []
    total = 0.0
    for key, label in cost_keys.items():
        val = analysis_results.get(key)
        if val is None:
            continue
        try:
            amount = float(val)
        except Exception:
            continue
        # Nur relevante Kosten > 0 anzeigen
        if amount <= 0:
            continue
        items.append((label, amount))
        total += amount
    return items, total


def create_payment_summary_page(
    analysis_results: dict[str, Any],
    variant_id: str,
    schedule: list[dict[str, Any]] | None = None,
    title: str = "Kostenzusammenstellung & Zahlungsmodalitäten",
) -> bytes | None:
    """Erstellt eine einzelne PDF‑Seite mit Kostenübersicht und Zahlungsplan.

    Args:
        analysis_results: Ergebnisse der Kostenberechnung (u.a. Netto‑ und Bruttobeträge).
        variant_id: ID der ausgewählten Zahlungsvariante.
        schedule: Optional kann der bereits berechnete Zahlungsplan übergeben werden.
        title: Überschrift der Seite.

    Returns:
        bytes: PDF‑Bytes einer einzelnen Seite oder None, wenn ReportLab nicht
        verfügbar ist.
    """
    if not _REPORTLAB_AVAILABLE:
        return None
    total_brutto = float(analysis_results.get('total_investment_brutto', 0.0) or 0.0)
    total_netto = float(analysis_results.get('total_investment_netto', 0.0) or 0.0)
    vat_rate = float(analysis_results.get('vat_rate_percent', 0.0) or 0.0)
    # MwSt.‑Betrag errechnen (Brutto - Netto)
    vat_amount = total_brutto - total_netto
    # Rabatt / Bonus
    discount = float(analysis_results.get('one_time_bonus_eur', 0.0) or 0.0)
    # Zusatzkosten auflisten
    items, additional_sum = _collect_additional_costs(analysis_results)
    # Zahlungsplan berechnen, falls nicht übergeben
    if schedule is None:
        schedule = compute_payment_schedule(variant_id, total_brutto)
    terms_text = get_payment_terms_text(variant_id, schedule)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2.5 * cm
    # Überschrift
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, title)
    y -= 1.0 * cm
    # Kostenübersicht
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Kostenübersicht")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    # Gesamtbetrag inkl. MwSt.
    c.drawString(2 * cm, y, "Gesamtbetrag (inkl. MwSt.):")
    c.drawRightString(width - 2 * cm, y, _format_currency(total_brutto))
    y -= 0.5 * cm
    # MwSt.
    c.drawString(2 * cm, y, f"- Mehrwertsteuer ({vat_rate:.0f} %):")
    c.drawRightString(width - 2 * cm, y, _format_currency(vat_amount))
    y -= 0.5 * cm
    # Zwischensumme (netto)
    c.drawString(2 * cm, y, "Zwischensumme (netto):")
    c.drawRightString(width - 2 * cm, y, _format_currency(total_netto + discount))
    y -= 0.5 * cm
    # Zusatzkosten auflisten
    if items:
        c.drawString(2 * cm, y, "+ Zusatzkosten:")
        c.drawRightString(width - 2 * cm, y, _format_currency(additional_sum))
        y -= 0.5 * cm
        # Einzelne Zusatzpositionen
        for label, amount in items:
            c.drawString(2.5 * cm, y, f"{label}:")
            c.drawRightString(width - 2 * cm, y, _format_currency(amount))
            y -= 0.4 * cm
    # Rabatt / Bonus
    if discount:
        c.drawString(2 * cm, y, "- Rabatt/Nachlass:")
        c.drawRightString(width - 2 * cm, y, _format_currency(discount))
        y -= 0.5 * cm
    # Endbetrag netto
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Endbetrag (netto):")
    c.drawRightString(width - 2 * cm, y, _format_currency(total_netto))
    y -= 0.6 * cm
    # Endbetrag brutto
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Endbetrag (inkl. MwSt.):")
    c.drawRightString(width - 2 * cm, y, _format_currency(total_brutto))
    y -= 1.0 * cm
    # Horizontaler Strich
    c.setLineWidth(0.5)
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 0.8 * cm
    # Zahlungsmodalitäten Abschnitt
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Zahlungsmodalitäten")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    # Zahlungsplan tabellarisch darstellen
    for seg in schedule:
        label = seg.get("label", seg.get("key"))
        amount = seg.get("amount", 0.0)
        percent = seg.get("percent", 0.0)
        # Zeilenformat: Label – Betrag (Prozent)
        line = f"{label}:"
        c.drawString(2.5 * cm, y, line)
        value_str = _format_currency(amount) + f" ({percent:.0f} %)"
        c.drawRightString(width - 2 * cm, y, value_str)
        y -= 0.5 * cm
    # erläuternder Text darunter
    y -= 0.3 * cm
    c.setFont("Helvetica-Oblique", 9)
    text_lines = c.beginText()
    text_lines.setTextOrigin(2.5 * cm, y)
    text_lines.setLeading(12)
    for line in terms_text.split("\n"):
        text_lines.textLine(line)
        y -= 0.4 * cm
    c.drawText(text_lines)
    # Footer: Seite
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawRightString(width - 2 * cm, 1.5 * cm, "")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
