# pdf_chart_renderer.py
"""
UNIVERSAL CHART RENDERER für PDF-Export
Fügt ALLE ausgewählten Charts dynamisch ins PDF ein
"""

from __future__ import annotations

from io import BytesIO
from typing import Any


def render_all_selected_charts_to_pdf(
    pdf: Any,  # FPDF instance
    selected_charts: list[str],
    analysis_results: dict[str, Any],
    chart_friendly_names: dict[str, str],
    max_charts_per_page: int = 2
) -> int:
    """
    Rendert ALLE ausgewählten Charts ins PDF

    Args:
        pdf: FPDF-Instance
        selected_charts: Liste der ausgewählten Chart-Keys
        analysis_results: Alle Analyse-Ergebnisse mit Chart-Bytes
        chart_friendly_names: Mapping Chart-Key → Freundlicher Name
        max_charts_per_page: Max. Anzahl Charts pro Seite

    Returns:
        Anzahl der hinzugefügten Charts
    """
    charts_added = 0
    charts_on_current_page = 0

    for chart_key in selected_charts:
        # Chart-Bytes holen
        chart_bytes = analysis_results.get(chart_key)

        if chart_bytes is None:
            # Chart nicht verfügbar, überspringen
            continue

        # Freundlichen Namen holen
        chart_title = chart_friendly_names.get(
            chart_key, chart_key.replace('_', ' ').title())

        # Neue Seite wenn nötig
        if charts_on_current_page >= max_charts_per_page:
            pdf.add_page()
            charts_on_current_page = 0

        # Chart-Titel
        if charts_on_current_page == 0:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, chart_title, ln=True)
        else:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, chart_title, ln=True)

        # Chart einfügen
        try:
            # BytesIO erstellen falls nötig
            if isinstance(chart_bytes, bytes):
                chart_io = BytesIO(chart_bytes)
            else:
                chart_io = chart_bytes

            # Position berechnen
            if charts_on_current_page == 0:
                y_position = pdf.get_y()
            else:
                y_position = pdf.get_y() + 5

            # Chart einfügen
            pdf.image(chart_io, x=10, y=y_position, w=190)

            charts_added += 1
            charts_on_current_page += 1

        except Exception as e:
            # Fehler beim Chart-Rendering
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Fehler beim Laden: {str(e)[:50]}", ln=True)

    return charts_added


def create_chart_overview_page(
    pdf: Any,
    selected_charts: list[str],
    chart_friendly_names: dict[str, str],
    analysis_results: dict[str, Any]
) -> None:
    """
    Erstellt eine Übersichtsseite mit allen Charts

    Args:
        pdf: FPDF-Instance
        selected_charts: Liste der ausgewählten Charts
        chart_friendly_names: Mapping Chart-Key → Name
        analysis_results: Analyse-Ergebnisse
    """
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Diagramm-Übersicht", ln=True, align="C")
    pdf.ln(5)

    # Zähle verfügbare vs. nicht verfügbare
    available_count = sum(
        1 for key in selected_charts if analysis_results.get(key) is not None)
    unavailable_count = len(selected_charts) - available_count

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Ausgewählte Diagramme: {len(selected_charts)}", ln=True)
    pdf.cell(0, 8, f"Verfügbar: {available_count}", ln=True)

    if unavailable_count > 0:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, f"Nicht verfügbar: {unavailable_count}", ln=True)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(5)

    # Liste der Charts
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Enthaltene Diagramme:", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    for idx, chart_key in enumerate(selected_charts, 1):
        chart_name = chart_friendly_names.get(chart_key, chart_key)
        is_available = analysis_results.get(chart_key) is not None

        if is_available:
            pdf.set_text_color(0, 100, 0)
            status = "✓"
        else:
            pdf.set_text_color(200, 0, 0)
            status = "✗"

        pdf.cell(10, 6, status)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, f"{idx}. {chart_name}", ln=True)


def render_financial_tools_to_pdf(
    pdf: Any,
    financial_tools_results: dict[str, Any]
) -> int:
    """
    Rendert Financial Tools Ergebnisse ins PDF

    Args:
        pdf: FPDF-Instance
        financial_tools_results: Dict mit Financial Tools Ergebnissen

    Returns:
        Anzahl der hinzugefügten Seiten
    """
    if not financial_tools_results:
        return 0

    pages_added = 0

    pdf.add_page()
    pages_added += 1

    pdf.set_font("Arial", "B", 16)
    pdf.cell(
        0,
        10,
        "Financial Tools - Detaillierte Finanzanalyse",
        ln=True,
        align="C")
    pdf.ln(5)

    # 1. Annuität
    if 'annuity_15y' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "1. Annuität-Berechnung (15 Jahre)", ln=True)
        pdf.ln(2)

        annuity = financial_tools_results['annuity_15y']
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Jährliche Rate: {annuity['value']:,.2f} €", ln=True)
        pdf.cell(
            0, 6, f"Monatliche Rate: {
                annuity['monthly']:,.2f} €", ln=True)
        pdf.cell(0, 6, f"Zinssatz: {annuity['interest_rate']:.2f}%", ln=True)
        pdf.cell(0, 6, f"Investition: {annuity['principal']:,.2f} €", ln=True)
        pdf.ln(5)

    if 'annuity_20y' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "Annuität-Berechnung (20 Jahre)", ln=True)
        pdf.ln(2)

        annuity = financial_tools_results['annuity_20y']
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Jährliche Rate: {annuity['value']:,.2f} €", ln=True)
        pdf.cell(
            0, 6, f"Monatliche Rate: {
                annuity['monthly']:,.2f} €", ln=True)
        pdf.ln(5)

    # 2. Leasing
    if 'leasing' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "2. Leasing-Kosten", ln=True)
        pdf.ln(2)

        leasing = financial_tools_results['leasing']
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"Monatliche Rate: {
                leasing['monthly_rate']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"Gesamtkosten: {
                leasing['total_cost']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"Laufzeit: {
                leasing.get(
                    'duration_months',
                    0)} Monate",
            ln=True)
        pdf.ln(5)

    # 3. Abschreibung
    if 'depreciation' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "3. Abschreibung (AfA)", ln=True)
        pdf.ln(2)

        depreciation = financial_tools_results['depreciation']
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"Jährliche Abschreibung: {
                depreciation['annual_depreciation']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"Restwert: {
                depreciation['residual_value']:,.2f} €",
            ln=True)
        pdf.cell(
            0, 6, f"Methode: {
                depreciation.get(
                    'method', 'N/A')}", ln=True)
        pdf.ln(5)

    # 4. Finanzierungs-Vergleich
    if 'financing_comparison' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "4. Finanzierungs-Vergleich", ln=True)
        pdf.ln(2)

        comparison = financial_tools_results['financing_comparison']

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Kredit:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"  Monatlich: {
                comparison['loan']['monthly_payment']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"  Gesamt: {
                comparison['loan']['total_cost']:,.2f} €",
            ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Leasing:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"  Monatlich: {
                comparison['leasing']['monthly_rate']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"  Gesamt: {
                comparison['leasing']['total_cost']:,.2f} €",
            ln=True)

        # Empfehlung
        diff = comparison['leasing']['total_cost'] - \
            comparison['loan']['total_cost']
        if diff > 0:
            pdf.set_text_color(0, 100, 0)
            pdf.cell(
                0, 7, f"Empfehlung: Kredit (Ersparnis: {
                    diff:,.2f} €)", ln=True)
        else:
            pdf.set_text_color(0, 100, 0)
            pdf.cell(
                0, 7, f"Empfehlung: Leasing (Ersparnis: {
                    abs(diff):,.2f} €)", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # 5. Kapitalertragssteuer
    if 'capital_gains_tax' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "5. Kapitalertragssteuer", ln=True)
        pdf.ln(2)

        capital_gains = financial_tools_results['capital_gains_tax']
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"Steuer: {
                capital_gains['tax_amount']:,.2f} €",
            ln=True)
        pdf.cell(0,
                 6,
                 f"Netto-Ertrag: {capital_gains['net_profit']:,.2f} €",
                 ln=True)
        pdf.ln(5)

    # 6. Contracting
    if 'contracting' in financial_tools_results:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "6. Contracting-Kosten", ln=True)
        pdf.ln(2)

        contracting = financial_tools_results['contracting']
        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0,
            6,
            f"Jährliche Kosten: {
                contracting['annual_cost']:,.2f} €",
            ln=True)
        pdf.cell(
            0,
            6,
            f"Gesamtkosten: {
                contracting['total_cost']:,.2f} €",
            ln=True)
        pdf.ln(5)

    return pages_added


def get_chart_statistics(
    selected_charts: list[str],
    analysis_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Erstellt Statistiken über Charts

    Returns:
        Dict mit Statistiken
    """
    total = len(selected_charts)
    available = sum(
        1 for key in selected_charts if analysis_results.get(key) is not None)
    unavailable = total - available

    # Nach Kategorie gruppieren (basierend auf Namensmustern)
    categories = {
        'Finanzierung': 0,
        'Energie': 0,
        'Analyse': 0,
        'Vergleich': 0,
        'Umwelt': 0,
        'Sonstiges': 0
    }

    for chart_key in selected_charts:
        if analysis_results.get(chart_key) is None:
            continue

        if any(
            keyword in chart_key for keyword in [
                'cost',
                'roi',
                'financing',
                'investment',
                'cashflow',
                'amort',
                'break_even']):
            categories['Finanzierung'] += 1
        elif any(keyword in chart_key for keyword in ['energy', 'production', 'consumption', 'pv', 'battery', 'storage']):
            categories['Energie'] += 1
        elif any(keyword in chart_key for keyword in ['analysis', 'sensitivity', 'optimization', 'performance', 'degradation', 'maintenance']):
            categories['Analyse'] += 1
        elif any(keyword in chart_key for keyword in ['comparison', 'tariff', 'scenario']):
            categories['Vergleich'] += 1
        elif any(keyword in chart_key for keyword in ['co2', 'savings']):
            categories['Umwelt'] += 1
        else:
            categories['Sonstiges'] += 1

    return {
        'total': total,
        'available': available,
        'unavailable': unavailable,
        'percentage_available': (available / total * 100) if total > 0 else 0,
        'categories': categories
    }
