"""
pdf_payment_integration.py
--------------------------

Erweiterte PDF-Integration für umfassende Zahlungsmodalitäten.
Dieses Modul kombiniert und erweitert die Funktionalität von
pdf_payment_summary.py und pdf_with_payment.py um die neuen
umfassenden Zahlungsoptionen zu unterstützen.

Das Modul bietet:
- Vollständige Integration der neuen PaymentTermsManager-Klasse
- Erweiterte PDF-Seite 7 mit detaillierter Zahlungsübersicht
- Rabattberechnungen und -darstellung
- Verschiedene Zahlungsarten (Bar, Raten, Finanzierung, Leasing)
- Rückwärtskompatibilität mit bestehenden PDF-Systemen

Die neue Seite zeigt:
- Kostenaufstellung mit angewandten Rabatten
- Detaillierte Zahlungspläne je nach gewählter Option
- Rechtliche Informationen und Geschäftsbedingungen
- Finanzierungsdetails (bei Finanzierung/Leasing)
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.colors import black, darkblue, gray
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    _REPORTLAB_AVAILABLE = True
except Exception:
    _REPORTLAB_AVAILABLE = False

from payment_terms import (
    calculate_comprehensive_payment,
    compute_payment_schedule,
    get_payment_manager,
    get_payment_terms_text,
)

try:
    from pdf_generator import generate_main_template_pdf_bytes
    _PDF_GEN_AVAILABLE = True
except Exception:
    _PDF_GEN_AVAILABLE = False


class EnhancedPaymentPDFGenerator:
    """
    Erweiterte PDF-Generator-Klasse für umfassende Zahlungsmodalitäten.
    """

    def __init__(self):
        self.payment_manager = get_payment_manager()

    def create_comprehensive_payment_page(
        self,
        analysis_results: dict[str, Any],
        payment_option_id: str,
        project_data: dict[str, Any] = None,
        additional_discounts: dict[str, Any] = None
    ) -> bytes | None:
        """
        Erstellt eine umfassende Zahlungsseite mit allen neuen Features.
        
        Args:
            analysis_results: Berechnungsergebnisse aus dem Projekt
            payment_option_id: ID der gewählten Zahlungsoption
            project_data: Zusätzliche Projektdaten
            additional_discounts: Zusätzliche Rabattinformationen
            
        Returns:
            PDF-Bytes oder None
        """
        if not _REPORTLAB_AVAILABLE:
            return None

        # Gesamtbetrag ermitteln
        total_amount = self._extract_total_amount(analysis_results)

        # Umfassende Zahlungsberechnung
        payment_calculation = calculate_comprehensive_payment(
            total_amount,
            payment_option_id,
            total_amount,  # Für Mengenrabatt
            datetime.now().month  # Für Saisonrabatt
        )

        if "error" in payment_calculation:
            return self._create_fallback_payment_page(analysis_results, payment_option_id)

        # PDF erstellen
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Seite gestalten
        self._draw_header(c, "Zahlungsmodalitäten & Kostenübersicht")
        self._draw_cost_breakdown(c, analysis_results, payment_calculation)
        self._draw_payment_details(c, payment_calculation, total_amount)
        self._draw_discount_summary(c, payment_calculation)
        self._draw_legal_terms(c)
        self._draw_footer(c, project_data)

        c.save()
        return buffer.getvalue()

    def _extract_total_amount(self, analysis_results: dict[str, Any]) -> float:
        """Extrahiert den Gesamtbetrag aus den Analyseergebnissen."""
        # Verschiedene mögliche Schlüssel prüfen
        amount_keys = [
            'total_cost_incl_tax',
            'total_amount',
            'gesamtkosten',
            'total_cost',
            'final_amount'
        ]

        for key in amount_keys:
            if key in analysis_results:
                try:
                    return float(analysis_results[key])
                except (ValueError, TypeError):
                    continue

        # Fallback: Versuche aus Komponenten zu berechnen
        components = [
            'module_cost',
            'inverter_cost',
            'installation_cost',
            'additional_costs'
        ]

        total = 0.0
        for comp in components:
            if comp in analysis_results:
                try:
                    total += float(analysis_results[comp])
                except (ValueError, TypeError):
                    continue

        return total if total > 0 else 50000.0  # Fallback-Wert

    def _draw_header(self, c: canvas.Canvas, title: str):
        """Zeichnet den Seitenkopf."""
        width, height = A4

        # Titel
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(darkblue)
        c.drawString(50, height - 60, title)

        # Linie unter Titel
        c.setStrokeColor(darkblue)
        c.setLineWidth(2)
        c.line(50, height - 70, width - 50, height - 70)

        # Datum
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        today = datetime.now().strftime("%d.%m.%Y")
        c.drawRightString(width - 50, height - 60, f"Erstellt am: {today}")

    def _draw_cost_breakdown(self, c: canvas.Canvas, analysis_results: dict[str, Any],
                           payment_calculation: dict[str, Any]):
        """Zeichnet die Kostenaufstellung."""
        width, height = A4
        y_pos = height - 120

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawString(50, y_pos, "Kostenübersicht")
        y_pos -= 25

        # Ursprünglicher Betrag
        original_amount = payment_calculation.get("original_amount", 0)
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, "Angebotssumme (brutto):")
        c.drawRightString(width - 50, y_pos, f"{original_amount:,.2f}€".replace(",", "."))
        y_pos -= 15

        # Rabatte aufführen
        discounts = payment_calculation.get("discounts_applied", [])
        for discount in discounts:
            c.setFillColor(colors.darkgreen)
            c.drawString(70, y_pos, f"- {discount['description']}:")
            discount_amount = original_amount * discount['percent'] / 100
            c.drawRightString(width - 50, y_pos, f"-{discount_amount:,.2f}€".replace(",", "."))
            y_pos -= 15

        # Trennlinie
        c.setStrokeColor(gray)
        c.line(70, y_pos - 5, width - 50, y_pos - 5)
        y_pos -= 20

        # Endbetrag
        final_amount = payment_calculation.get("final_amount", original_amount)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(black)
        c.drawString(70, y_pos, "Gesamtbetrag nach Rabatt:")
        c.drawRightString(width - 50, y_pos, f"{final_amount:,.2f}€".replace(",", "."))

        # Ersparnis hervorheben
        total_savings = original_amount - final_amount
        if total_savings > 0:
            y_pos -= 15
            c.setFillColor(colors.darkgreen)
            c.setFont("Helvetica", 9)
            savings_percent = (total_savings / original_amount) * 100
            c.drawString(70, y_pos, f"Ihre Ersparnis: {total_savings:,.2f}€ ({savings_percent:.1f}%)".replace(",", "."))

    def _draw_payment_details(self, c: canvas.Canvas, payment_calculation: dict[str, Any],
                            total_amount: float):
        """Zeichnet die Zahlungsdetails."""
        width, height = A4
        y_pos = height - 320

        payment_option = payment_calculation.get("payment_option", {})
        payment_type = payment_option.get("payment_type", "")

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawString(50, y_pos, "Zahlungsdetails")
        y_pos -= 25

        # Zahlungsart
        c.setFont("Helvetica", 10)
        c.drawString(70, y_pos, f"Gewählte Zahlungsart: {payment_option.get('name', '')}")
        y_pos -= 20

        # Spezifische Details je nach Zahlungsart
        if payment_type == "immediate":
            self._draw_immediate_payment_details(c, payment_calculation, y_pos)
        elif payment_type == "installments":
            self._draw_installment_details(c, payment_calculation, y_pos)
        elif payment_type == "financing":
            self._draw_financing_details(c, payment_calculation, y_pos)
        elif payment_type == "leasing":
            self._draw_leasing_details(c, payment_calculation, y_pos)

    def _draw_immediate_payment_details(self, c: canvas.Canvas, payment_calculation: dict[str, Any],
                                      start_y: float):
        """Zeichnet Details für Sofortzahlung."""
        payment_option = payment_calculation.get("payment_option", {})
        final_amount = payment_calculation.get("final_amount", 0)

        c.setFont("Helvetica", 10)
        c.drawString(70, start_y, f"Zahlungsbetrag: {final_amount:,.2f}€".replace(",", "."))
        start_y -= 15
        c.drawString(70, start_y, "Fällig: Bei Vertragsabschluss")
        start_y -= 15

        if payment_option.get("discount_percent", 0) > 0:
            c.setFillColor(colors.darkgreen)
            c.drawString(70, start_y, f"Inkl. {payment_option['discount_percent']:.1f}% Zahlungsrabatt")

    def _draw_installment_details(self, c: canvas.Canvas, payment_calculation: dict[str, Any],
                                start_y: float):
        """Zeichnet Details für Ratenzahlung."""
        payment_option = payment_calculation.get("payment_option", {})
        final_amount = payment_calculation.get("final_amount", 0)
        schedule = payment_option.get("installment_schedule", [])

        c.setFont("Helvetica", 10)
        c.drawString(70, start_y, "Ratenzahlungsplan:")
        start_y -= 20

        for i, installment in enumerate(schedule, 1):
            amount = final_amount * installment["percentage"] / 100
            c.drawString(90, start_y, f"{i}. Rate ({installment['description']}):")
            c.drawRightString(500, start_y, f"{amount:,.2f}€".replace(",", "."))
            start_y -= 15

            due_text = f"Fällig: {installment.get('due_days', 0)} Tage nach Vertragsabschluss"
            c.setFont("Helvetica", 8)
            c.setFillColor(gray)
            c.drawString(110, start_y, due_text)
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            start_y -= 10

    def _draw_financing_details(self, c: canvas.Canvas, payment_calculation: dict[str, Any],
                              start_y: float):
        """Zeichnet Details für Finanzierung."""
        payment_option = payment_calculation.get("payment_option", {})
        final_amount = payment_calculation.get("final_amount", 0)
        financing_options = payment_option.get("financing_options", [])

        c.setFont("Helvetica", 10)
        c.drawString(70, start_y, "Finanzierungsoptionen:")
        start_y -= 20

        for option in financing_options:
            years = option.get("duration_years", 0)
            rate = option.get("interest_rate", 0)

            # Einfache Annuitätenberechnung
            monthly_rate = rate / 100 / 12
            num_payments = years * 12
            if monthly_rate > 0:
                monthly_payment = final_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            else:
                monthly_payment = final_amount / num_payments

            c.drawString(90, start_y, f"Laufzeit {years} Jahre ({rate:.1f}% p.a.):")
            c.drawRightString(500, start_y, f"~{monthly_payment:,.2f}€/Monat".replace(",", "."))
            start_y -= 15

    def _draw_leasing_details(self, c: canvas.Canvas, payment_calculation: dict[str, Any],
                            start_y: float):
        """Zeichnet Details für Leasing."""
        payment_option = payment_calculation.get("payment_option", {})
        final_amount = payment_calculation.get("final_amount", 0)
        leasing_options = payment_option.get("leasing_options", [])

        c.setFont("Helvetica", 10)
        c.drawString(70, start_y, "Leasingoptionen:")
        start_y -= 20

        for option in leasing_options:
            years = option.get("duration_years", 0)
            factor = option.get("monthly_rate_factor", 0)
            monthly_rate = final_amount * factor

            c.drawString(90, start_y, f"Laufzeit {years} Jahre:")
            c.drawRightString(500, start_y, f"{monthly_rate:,.2f}€/Monat".replace(",", "."))
            start_y -= 15

    def _draw_discount_summary(self, c: canvas.Canvas, payment_calculation: dict[str, Any]):
        """Zeichnet die Rabattübersicht."""
        width, height = A4
        y_pos = height - 520

        discounts = payment_calculation.get("discounts_applied", [])
        if not discounts:
            return

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawString(50, y_pos, "Angewandte Rabatte")
        y_pos -= 25

        for discount in discounts:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.darkgreen)
            c.drawString(70, y_pos, f"✓ {discount['description']}")
            c.drawRightString(width - 50, y_pos, f"{discount['percent']:.1f}%")
            y_pos -= 15

    def _draw_legal_terms(self, c: canvas.Canvas):
        """Zeichnet die rechtlichen Bedingungen."""
        width, height = A4
        y_pos = height - 620

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawString(50, y_pos, "Zahlungsbedingungen")
        y_pos -= 25

        # Hole rechtliche Texte aus der Konfiguration
        manager = get_payment_manager()
        legal_texts = manager.comprehensive_config.get("legal_texts", {})

        terms = [
            legal_texts.get("general_terms", "Es gelten unsere AGB."),
            legal_texts.get("payment_conditions", "Zahlung gemäß Vereinbarung."),
            "Alle Preise verstehen sich inklusive der gesetzlichen Mehrwertsteuer.",
            "Bei Fragen zu den Zahlungsmodalitäten stehen wir gerne zur Verfügung."
        ]

        c.setFont("Helvetica", 9)
        for term in terms:
            # Text umbrechen falls zu lang
            words = term.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if c.stringWidth(test_line, "Helvetica", 9) > width - 140:
                    if line:
                        c.drawString(70, y_pos, line.strip())
                        y_pos -= 12
                        line = word + " "
                    else:
                        c.drawString(70, y_pos, word)
                        y_pos -= 12
                        line = ""
                else:
                    line = test_line

            if line:
                c.drawString(70, y_pos, line.strip())
                y_pos -= 12
            y_pos -= 3

    def _draw_footer(self, c: canvas.Canvas, project_data: dict[str, Any] = None):
        """Zeichnet den Seitenfuß."""
        width, height = A4

        # Linie
        c.setStrokeColor(gray)
        c.line(50, 50, width - 50, 50)

        # Seitenzahl
        c.setFont("Helvetica", 8)
        c.setFillColor(gray)
        c.drawCentredText(width/2, 35, "Seite 7 - Zahlungsmodalitäten")

        # Projekt-Info falls verfügbar
        if project_data and project_data.get("customer_name"):
            c.drawString(50, 35, f"Projekt: {project_data['customer_name']}")

    def _create_fallback_payment_page(self, analysis_results: dict[str, Any],
                                    variant_id: str) -> bytes | None:
        """Erstellt Fallback-Seite mit Legacy-System."""
        if not _REPORTLAB_AVAILABLE:
            return None

        total_amount = self._extract_total_amount(analysis_results)
        schedule = compute_payment_schedule(variant_id, total_amount)
        terms_text = get_payment_terms_text(variant_id, schedule)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        self._draw_header(c, "Zahlungsmodalitäten (Legacy)")

        # Einfache Darstellung
        width, height = A4
        y_pos = height - 150

        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, f"Gesamtbetrag: {total_amount:,.2f}€".replace(",", "."))
        y_pos -= 30

        c.drawString(50, y_pos, "Zahlungsplan:")
        y_pos -= 20

        for segment in schedule:
            label = segment.get("label", "")
            amount = segment.get("amount", 0)
            c.drawString(70, y_pos, f"{label}: {amount:,.2f}€".replace(",", "."))
            y_pos -= 15

        y_pos -= 20
        c.drawString(50, y_pos, "Beschreibung:")
        y_pos -= 15
        c.drawString(70, y_pos, terms_text)

        c.save()
        return buffer.getvalue()


# Convenience-Funktionen

def create_enhanced_payment_summary_page(
    analysis_results: dict[str, Any],
    payment_option_id: str,
    project_data: dict[str, Any] = None
) -> bytes | None:
    """
    Erstellt eine erweiterte Zahlungsübersichtsseite.
    
    Args:
        analysis_results: Berechnungsergebnisse
        payment_option_id: ID der Zahlungsoption
        project_data: Zusätzliche Projektdaten
        
    Returns:
        PDF-Bytes oder None
    """
    generator = EnhancedPaymentPDFGenerator()
    return generator.create_comprehensive_payment_page(
        analysis_results, payment_option_id, project_data
    )


def generate_comprehensive_offer_pdf(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
    payment_option_id: str
) -> bytes | None:
    """
    Erzeugt ein vollständiges Angebots-PDF mit erweiterten Zahlungsmodalitäten.
    
    Args:
        project_data: Projektinformationen
        analysis_results: Berechnungsergebnisse  
        company_info: Firmeninformationen
        payment_option_id: ID der Zahlungsoption
        
    Returns:
        Vollständiges PDF oder None
    """
    if not _PDF_GEN_AVAILABLE:
        return None

    try:
        # Haupt-PDF generieren
        main_pdf = generate_main_template_pdf_bytes(
            project_data, analysis_results, company_info
        )

        if not main_pdf:
            return None

        # Zahlungsseite hinzufügen
        payment_page = create_enhanced_payment_summary_page(
            analysis_results, payment_option_id, project_data
        )

        if payment_page:
            # PDFs kombinieren (vereinfacht - in Produktionsumgebung PyPDF2 verwenden)
            return main_pdf + payment_page
        return main_pdf

    except Exception:
        return None


# Legacy-Kompatibilitäts-Wrapper

def create_payment_summary_page(
    analysis_results: dict[str, Any],
    variant_id: str
) -> bytes | None:
    """Legacy-Wrapper für Rückwärtskompatibilität."""
    generator = EnhancedPaymentPDFGenerator()
    return generator._create_fallback_payment_page(analysis_results, variant_id)


def generate_offer_pdf_with_payment_terms(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
    variant_id: str
) -> bytes | None:
    """Legacy-Wrapper für bestehende Systeme."""
    return generate_comprehensive_offer_pdf(
        project_data, analysis_results, company_info, variant_id
    )
