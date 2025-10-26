"""
payment_terms_ui.py
-------------------

Erweiterte Streamlit-UI-Komponenten für die Verwaltung und Auswahl von
Zahlungsmodalitäten in der PDF-Generierung. Diese Komponenten wurden
erheblich erweitert um die neuen umfassenden Zahlungsoptionen zu unterstützen.

Das Modul bietet jetzt:
- Interaktive Auswahl von erweiterten Zahlungsoptionen (Bar, Raten, Finanzierung, Leasing)
- Live-Vorschau der Zahlungsberechnungen mit Rabatten
- Rabattvorschau und -simulation
- Integration mit dem erweiterten PDF-Generator
- Validierung und Fehlerbehandlung
- Rückwärtskompatibilität mit bestehenden Systemen

Die UI-Komponenten können in bestehende PDF-Workflows integriert werden
und erweitern diese um umfassende Zahlungsmodalitäten-Funktionalität.

Legacy-Funktionen bleiben für Rückwärtskompatibilität erhalten.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

# Import der erweiterten Zahlungsmodalitäten-Module
from payment_terms import (
    calculate_comprehensive_payment,
    compute_payment_schedule,
    ensure_comprehensive_config_exists,
    get_comprehensive_payment_options,
    get_discount_summary,
    get_payment_manager,
    get_payment_terms_config,
    get_payment_terms_text,
)

# Import der PDF-Integration (neu und legacy)
try:
    from pdf_payment_integration import (
        create_enhanced_payment_summary_page,
        generate_comprehensive_offer_pdf,
    )
    _PDF_INTEGRATION_AVAILABLE = True
except ImportError:
    _PDF_INTEGRATION_AVAILABLE = False

# Legacy PDF-Integration
from pdf_payment_summary import create_payment_summary_page

try:
    from pdf_generator import generate_main_template_pdf_bytes
    _PDF_GEN_AVAILABLE = True
except Exception:
    _PDF_GEN_AVAILABLE = False


class PaymentTermsUI:
    """
    Erweiterte Hauptklasse für die Zahlungsmodalitäten-UI-Komponenten.
    Unterstützt sowohl das neue umfassende System als auch Legacy-Kompatibilität.
    """

    def __init__(self):
        self.payment_manager = get_payment_manager()
        ensure_comprehensive_config_exists()

    def render_payment_selection_widget(
        self,
        total_amount: float,
        key_prefix: str = "payment",
        show_preview: bool = True,
        use_legacy: bool = False
    ) -> dict[str, Any]:
        """
        Rendert erweiterte Widget zur Auswahl von Zahlungsoptionen.

        Args:
            total_amount: Gesamtbetrag für Berechnungen
            key_prefix: Präfix für Streamlit-Keys (Eindeutigkeit)
            show_preview: Ob Vorschau angezeigt werden soll
            use_legacy: Falls True, verwendet Legacy-System

        Returns:
            Dict mit ausgewählter Zahlungsoption und Berechnungen
        """
        st.subheader("💳 Zahlungsmodalitäten")

        if use_legacy:
            return self._render_legacy_payment_selection(
                total_amount, key_prefix, show_preview)

        # Verfügbare Zahlungsoptionen laden
        payment_options = get_comprehensive_payment_options()
        enabled_options = [
            opt for opt in payment_options if opt.get(
                "enabled", True)]

        if not enabled_options:
            st.error(
                "Keine Zahlungsoptionen verfügbar. Bitte konfigurieren Sie zuerst die Zahlungsmodalitäten im Admin-Bereich.")
            return {}

        # Auswahl der Zahlungsoption
        option_names = [
            f"{opt['name']} ({opt['payment_type']})" for opt in enabled_options]
        selected_index = st.selectbox(
            "Zahlungsart auswählen:",
            range(len(enabled_options)),
            format_func=lambda x: option_names[x],
            key=f"{key_prefix}_option_select"
        )

        selected_option = enabled_options[selected_index]

        # Zusätzliche Parameter für Rabattberechnung
        col1, col2 = st.columns(2)

        with col1:
            use_quantity_discount = st.checkbox(
                "Mengenrabatt anwenden",
                value=True,
                key=f"{key_prefix}_quantity_discount",
                help="Berücksichtigt Rabatte basierend auf dem Auftragswert"
            )

        with col2:
            use_seasonal_discount = st.checkbox(
                "Saisonrabatt anwenden",
                value=True,
                key=f"{key_prefix}_seasonal_discount",
                help="Berücksichtigt saisonale Rabatte"
            )

        # Berechnung durchführen
        quantity_amount = total_amount if use_quantity_discount else None
        current_month = datetime.now().month if use_seasonal_discount else None

        payment_calculation = calculate_comprehensive_payment(
            total_amount,
            selected_option["id"],
            quantity_amount,
            current_month
        )

        # Vorschau anzeigen falls gewünscht
        if show_preview and "error" not in payment_calculation:
            self._render_payment_preview(payment_calculation, total_amount)

        # Rückgabewerte
        return {
            "selected_option": selected_option,
            "payment_calculation": payment_calculation,
            "total_amount": total_amount,
            "settings": {
                "use_quantity_discount": use_quantity_discount,
                "use_seasonal_discount": use_seasonal_discount
            }
        }

    def _render_legacy_payment_selection(
        self,
        total_amount: float,
        key_prefix: str,
        show_preview: bool
    ) -> dict[str, Any]:
        """Rendert Legacy-Zahlungsauswahl für Rückwärtskompatibilität."""
        config = get_payment_terms_config()
        variants = config.get("variants", [])

        if not variants:
            st.error("Keine Zahlungsvarianten konfiguriert.")
            return {}

        # Varianten-Auswahl
        variant_names = [v.get("name", v.get("id", "Unbekannt"))
                         for v in variants]
        selected_index = st.selectbox(
            "Zahlungsvariante auswählen:",
            range(len(variants)),
            format_func=lambda x: variant_names[x],
            key=f"{key_prefix}_legacy_variant"
        )

        selected_variant = variants[selected_index]
        variant_id = selected_variant.get("id", "")

        # Zahlungsplan berechnen
        schedule = compute_payment_schedule(variant_id, total_amount)
        terms_text = get_payment_terms_text(variant_id, schedule)

        if show_preview:
            st.markdown("### 📊 Zahlungsplan (Legacy)")

            for segment in schedule:
                label = segment.get("label", "")
                amount = segment.get("amount", 0)
                percent = segment.get("percent", 0)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(label)
                with col2:
                    st.write(f"{amount:,.2f}€".replace(",", "."))
                with col3:
                    st.write(f"{percent:.1f}%")

            st.info(terms_text)

        return {
            "selected_variant": selected_variant,
            "variant_id": variant_id,
            "schedule": schedule,
            "terms_text": terms_text,
            "total_amount": total_amount,
            "legacy_mode": True
        }

    def _render_payment_preview(
            self, payment_calculation: dict[str, Any], total_amount: float):
        """Rendert die erweiterte Zahlungsvorschau."""
        st.markdown("### 📊 Zahlungsvorschau")

        # Grunddaten
        original_amount = payment_calculation.get(
            "original_amount", total_amount)
        final_amount = payment_calculation.get("final_amount", total_amount)
        total_savings = original_amount - final_amount

        # Metriken anzeigen
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Ursprungsbetrag",
                f"{original_amount:,.2f}€".replace(",", "."),
                help="Brutto-Angebotssumme vor Rabatten"
            )

        with col2:
            st.metric(
                "Finaler Betrag",
                f"{final_amount:,.2f}€".replace(",", "."),
                delta=f"-{total_savings:,.2f}€".replace(",", ".") if total_savings > 0 else None,
                delta_color="inverse" if total_savings > 0 else "normal"
            )

        with col3:
            if total_savings > 0:
                savings_percent = (total_savings / original_amount) * 100
                st.metric(
                    "Ersparnis",
                    f"{savings_percent:.1f}%",
                    f"{total_savings:,.2f}€".replace(",", "."),
                    delta_color="inverse"
                )
            else:
                st.metric("Ersparnis", "0%", "0€")

        # Angewandte Rabatte
        discounts = payment_calculation.get("discounts_applied", [])
        if discounts:
            st.markdown("**Angewandte Rabatte:**")
            for discount in discounts:
                discount_amount = original_amount * discount["percent"] / 100
                st.success(
                    f"✅ {
                        discount['description']}: -{
                        discount['percent']:.1f}% (-{
                        discount_amount:,.2f}€)".replace(
                        ",", "."))

        # Zahlungsdetails
        payment_option = payment_calculation.get("payment_option", {})
        payment_type = payment_option.get("payment_type", "")

        st.markdown("**Zahlungsdetails:**")

        if payment_type == "immediate":
            st.info(
                f"💰 **Sofortzahlung**: {
                    final_amount:,.2f}€ fällig bei Vertragsabschluss".replace(
                    ",", "."))

        elif payment_type == "installments":
            schedule = payment_option.get("installment_schedule", [])
            st.info("📅 **Ratenzahlung**:")
            for i, installment in enumerate(schedule, 1):
                amount = final_amount * installment["percentage"] / 100
                due_days = installment.get("due_days", 0)
                description = installment.get("description", f"Rate {i}")
                st.write(
                    f"• {description}: {
                        amount:,.2f}€ (fällig nach {due_days} Tagen)".replace(
                        ",", "."))

        elif payment_type == "financing":
            financing_options = payment_option.get("financing_options", [])
            if financing_options:
                st.info("🏦 **Finanzierungsoptionen**:")
                for option in financing_options:
                    years = option.get("duration_years", 0)
                    rate = option.get("interest_rate", 0)
                    # Vereinfachte monatliche Rate
                    monthly_rate = rate / 100 / 12
                    num_payments = years * 12
                    if monthly_rate > 0:
                        monthly_payment = final_amount * \
                            (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                    else:
                        monthly_payment = final_amount / num_payments
                    st.write(
                        f"• {years} Jahre zu {
                            rate:.1f}% p.a.: ~{
                            monthly_payment:,.2f}€/Monat".replace(
                            ",", "."))

        elif payment_type == "leasing":
            leasing_options = payment_option.get("leasing_options", [])
            if leasing_options:
                st.info("🚗 **Leasingoptionen**:")
                for option in leasing_options:
                    years = option.get("duration_years", 0)
                    factor = option.get("monthly_rate_factor", 0)
                    monthly_rate = final_amount * factor
                    st.write(
                        f"• {years} Jahre Laufzeit: {monthly_rate:,.2f}€/Monat".replace(",", "."))

    def render_advanced_payment_settings(
            self, key_prefix: str = "advanced") -> dict[str, Any]:
        """
        Rendert erweiterte Zahlungseinstellungen.

        Args:
            key_prefix: Präfix für Streamlit-Keys

        Returns:
            Dict mit erweiterten Einstellungen
        """
        with st.expander("⚙️ Erweiterte Zahlungseinstellungen"):

            # Rabatt-Simulation
            st.markdown("**Rabatt-Simulation**")

            col1, col2 = st.columns(2)
            with col1:
                test_amount = st.number_input(
                    "Test-Betrag für Rabattberechnung:",
                    min_value=1000.0,
                    max_value=1000000.0,
                    value=50000.0,
                    step=1000.0,
                    key=f"{key_prefix}_test_amount"
                )

            with col2:
                test_month = st.selectbox(
                    "Test-Monat für Saisonrabatt:",
                    range(1, 13),
                    index=datetime.now().month - 1,
                    format_func=lambda x: datetime(2024, x, 1).strftime("%B"),
                    key=f"{key_prefix}_test_month"
                )

            # Rabattübersicht generieren
            discount_summary = get_discount_summary(
                test_amount, test_amount, test_month)

            if discount_summary.get("best_option"):
                st.success(
                    f"📈 Beste Zahlungsoption für {
                        test_amount:,.2f}€:".replace(
                        ",", "."))
                best_option = discount_summary["best_option"]
                savings = discount_summary.get("maximum_savings", 0)
                savings_percent = discount_summary.get("savings_percent", 0)

                option_name = best_option["payment_option"]["name"]
                st.write(f"• **{option_name}**")
                st.write(
                    f"• Ersparnis: {
                        savings:,.2f}€ ({
                        savings_percent:.1f}%)".replace(
                        ",", "."))

                for discount in best_option.get("discounts_applied", []):
                    st.write(
                        f"• {
                            discount['description']}: {
                            discount['percent']:.1f}%")

            # PDF-Optionen
            st.markdown("**PDF-Generierungsoptionen**")

            include_payment_page = st.checkbox(
                "Zahlungsseite in PDF einbinden",
                value=True,
                key=f"{key_prefix}_include_payment",
                help="Fügt eine detaillierte Zahlungsübersichtsseite zum PDF hinzu")

            show_discount_details = st.checkbox(
                "Rabattdetails anzeigen",
                value=True,
                key=f"{key_prefix}_show_discounts",
                help="Zeigt detaillierte Rabattaufschlüsselung im PDF"
            )

            show_legal_terms = st.checkbox(
                "Rechtliche Bedingungen einbinden",
                value=True,
                key=f"{key_prefix}_show_legal",
                help="Fügt rechtliche Zahlungsbedingungen hinzu"
            )

            return {
                "test_settings": {
                    "amount": test_amount,
                    "month": test_month
                },
                "pdf_options": {
                    "include_payment_page": include_payment_page,
                    "show_discount_details": show_discount_details,
                    "show_legal_terms": show_legal_terms
                },
                "discount_summary": discount_summary
            }


# Convenience-Funktionen für Integration in bestehende PDFs

def render_payment_selection_for_pdf(
    total_amount: float,
    container=None,
    key_prefix: str = "pdf_payment",
    use_legacy: bool = False
) -> dict[str, Any] | None:
    """
    Rendert Zahlungsauswahl für PDF-Integration.

    Args:
        total_amount: Gesamtbetrag
        container: Streamlit-Container (optional)
        key_prefix: Key-Präfix
        use_legacy: Ob Legacy-System verwendet werden soll

    Returns:
        Zahlungsdaten oder None
    """
    ui = PaymentTermsUI()

    if container:
        with container:
            return ui.render_payment_selection_widget(
                total_amount, key_prefix, use_legacy=use_legacy)
    else:
        return ui.render_payment_selection_widget(
            total_amount, key_prefix, use_legacy=use_legacy)


def get_payment_pdf_data(
    payment_selection: dict[str, Any],
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> bytes | None:
    """
    Generiert PDF-Daten für ausgewählte Zahlungsoption.

    Args:
        payment_selection: Ausgewählte Zahlungsoption
        project_data: Projektdaten
        analysis_results: Analyseergebnisse

    Returns:
        PDF-Bytes oder None
    """
    # Legacy-Mode prüfen
    if payment_selection.get("legacy_mode", False):
        variant_id = payment_selection.get("variant_id", "")
        if variant_id:
            return create_payment_summary_page(analysis_results, variant_id)
        return None

    # Erweiterte PDF-Integration
    if not _PDF_INTEGRATION_AVAILABLE:
        st.warning(
            "Erweiterte PDF-Integration nicht verfügbar. Verwende Legacy-System.")
        return None

    if "error" in payment_selection.get("payment_calculation", {}):
        st.error("Fehler in der Zahlungsberechnung.")
        return None

    selected_option = payment_selection.get("selected_option", {})
    option_id = selected_option.get("id", "")

    if not option_id:
        st.error("Keine Zahlungsoption ausgewählt.")
        return None

    try:
        return create_enhanced_payment_summary_page(
            analysis_results,
            option_id,
            project_data
        )
    except Exception as e:
        st.error(f"Fehler bei der PDF-Generierung: {str(e)}")
        return None


def render_payment_terms_tab():
    """
    Rendert kompletten Tab für Zahlungsmodalitäten.
    Kann in bestehende Streamlit-Apps integriert werden.
    """
    ui = PaymentTermsUI()

    st.header("💳 Zahlungsmodalitäten verwalten")

    # System-Auswahl
    use_legacy = st.toggle(
        "Legacy-Modus verwenden",
        value=False,
        help="Aktiviert das alte Varianten-basierte System für Kompatibilität"
    )

    # Test-Bereich
    with st.expander("🧪 Test & Vorschau"):
        test_amount = st.number_input(
            "Test-Betrag:",
            min_value=1000.0,
            value=50000.0,
            step=1000.0
        )

        payment_data = ui.render_payment_selection_widget(
            test_amount, "test", show_preview=True, use_legacy=use_legacy
        )

        if payment_data and st.button("PDF-Vorschau generieren"):
            try:
                # Dummy-Daten für Vorschau
                dummy_analysis = {"total_cost_incl_tax": test_amount}
                dummy_project = {"customer_name": "Test-Kunde"}

                pdf_data = get_payment_pdf_data(
                    payment_data, dummy_project, dummy_analysis)
                if pdf_data:
                    st.download_button(
                        "📄 PDF herunterladen",
                        pdf_data,
                        "zahlungsmodalitaeten_vorschau.pdf",
                        "application/pdf"
                    )
            except Exception as e:
                st.error(f"Fehler bei PDF-Generierung: {str(e)}")

    # Erweiterte Einstellungen (nur im neuen System)
    if not use_legacy:
        ui.render_advanced_payment_settings("main")


# Legacy-Funktionen für Rückwärtskompatibilität

def render_payment_terms_ui(
    analysis_results: dict[str, Any],
    company_info: dict[str, Any] = None
) -> bytes | None:
    """
    Legacy-Funktion: Rendert Zahlungsmodalitäten-UI und gibt PDF zurück.
    Für Rückwärtskompatibilität mit bestehenden Systemen.
    """
    st.header("Zahlungsmodalitäten (Legacy-Modus)")

    # Gesamtbetrag ermitteln
    total_amount = analysis_results.get("total_cost_incl_tax", 0.0)
    if total_amount <= 0:
        total_amount = analysis_results.get("total_amount", 50000.0)

    # Legacy-UI verwenden
    payment_data = render_payment_selection_for_pdf(
        total_amount,
        key_prefix="legacy",
        use_legacy=True
    )

    if not payment_data:
        return None

    # PDF erstellen
    variant_id = payment_data.get("variant_id", "")
    if variant_id:
        return create_payment_summary_page(analysis_results, variant_id)

    return None


def select_payment_variant_and_generate_pdf(
    analysis_results: dict[str, Any],
    project_data: dict[str, Any] = None,
    company_info: dict[str, Any] = None
) -> bytes | None:
    """
    Legacy-Wrapper: Auswahl einer Zahlungsvariante und PDF-Generierung.
    """
    # Ermittle Gesamtbetrag
    total_amount = analysis_results.get("total_cost_incl_tax", 0.0)
    if total_amount <= 0:
        for key in ["total_amount", "gesamtkosten", "total_cost"]:
            if key in analysis_results:
                try:
                    total_amount = float(analysis_results[key])
                    break
                except (ValueError, TypeError):
                    continue

    if total_amount <= 0:
        st.error("Kein gültiger Gesamtbetrag gefunden.")
        return None

    st.write(f"**Gesamtbetrag:** {total_amount:,.2f}€".replace(",", "."))

    # Zahlungsauswahl
    payment_data = render_payment_selection_for_pdf(total_amount)

    if not payment_data:
        return None

    # PDF generieren
    return get_payment_pdf_data(
        payment_data,
        project_data or {},
        analysis_results
    )


# Streamlit-App für Testing (falls direkt ausgeführt)
if __name__ == "__main__":
    st.set_page_config(
        page_title="Zahlungsmodalitäten UI",
        page_icon="💳",
        layout="wide"
    )

    st.title("💳 Zahlungsmodalitäten Test-UI")

    # Tab-Navigation
    tab1, tab2, tab3 = st.tabs(
        ["🧪 Test", "⚙️ Konfiguration", "📚 Dokumentation"])

    with tab1:
        render_payment_terms_tab()

    with tab2:
        st.header("Konfigurationsmanagement")
        ui = PaymentTermsUI()
        ui.render_payment_configuration_manager("config_test")

    with tab3:
        st.header("Dokumentation")
        st.markdown("""
        ## Zahlungsmodalitäten-System

        ### Neue Features:
        - **Umfassende Zahlungsarten**: Bar, Raten, Finanzierung, Leasing
        - **Automatische Rabattberechnung**: Mengen-, Saison-, Zahlungsrabatte
        - **PDF-Integration**: Erweiterte Zahlungsseiten mit allen Details
        - **Live-Vorschau**: Sofortige Berechnung und Anzeige

        ### Verwendung:
        1. Zahlungsart auswählen
        2. Rabattoptionen konfigurieren
        3. Vorschau prüfen
        4. PDF mit Zahlungsdetails generieren

        ### Legacy-Kompatibilität:
        Das System unterstützt weiterhin alle bestehenden Zahlungsvarianten
        und kann nahtlos in bestehende Workflows integriert werden.
        """)


def render_payment_terms_selector(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    company_info: dict[str, Any],
    title: str = "Zahlungsvariante auswählen",
    show_pdf_button: bool = True,
) -> None:
    """Zeigt die Auswahl der Zahlungsvarianten und generiert bei Bedarf ein PDF.

    Args:
        project_data: Daten des Projekts (wird an PDF‑Generator weitergereicht).
        analysis_results: Berechnete Analyse (enthält Netto‑/Bruttowerte).
        company_info: Informationen zum Unternehmen (für PDF‑Generator).
        title: Überschrift im UI.
        show_pdf_button: Wenn True, wird eine Schaltfläche angezeigt, über die das
            vollständige Angebots‑PDF mit Kostenübersicht und Zahlungsplan
            heruntergeladen werden kann.
    """
    st.subheader(title)
    config = get_payment_terms_config()
    variants: list[dict[str, Any]] = config.get("variants", [])
    if not variants:
        st.warning("Es sind keine Zahlungsvarianten konfiguriert.")
        return
    variant_names = [v.get("name") or v.get("id") for v in variants]
    selected_name = st.selectbox("Variante", variant_names)
    variant = next(
        (v for v in variants if (
            v.get("name") or v.get("id")) == selected_name),
        variants[0])
    variant_id = variant.get("id")
    # Berechnung des Zahlungsplans anhand des Bruttobetrags
    total_brutto = float(
        analysis_results.get(
            "total_investment_brutto",
            0.0) or 0.0)
    schedule = compute_payment_schedule(variant_id, total_brutto)
    terms_text = get_payment_terms_text(variant_id, schedule)
    # Anzeige des Zahlungsplans
    st.markdown("**Zahlungsplan**")
    for seg in schedule:
        label = seg.get("label", seg.get("key"))
        amount = seg.get("amount", 0.0)
        percent = seg.get("percent", 0.0)
        st.write(f"{label}: {amount:,.2f} € ({percent:.0f} %)")
    st.markdown("**Erläuterung**")
    st.info(terms_text)
    if show_pdf_button:
        if not _PDF_GEN_AVAILABLE:
            st.error("PDF‑Generator nicht verfügbar.")
        else:
            if st.button(
                "PDF mit Zahlungsplan erstellen",
                    use_container_width=True):
                with st.spinner("Erzeuge PDF..."):
                    # Erstelle zusätzliche Seite
                    add_page = create_payment_summary_page(
                        analysis_results, variant_id, schedule=schedule)
                    # Generiere Haupt‑PDF
                    pdf_bytes = generate_main_template_pdf_bytes(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        company_info=company_info,
                        additional_pdf=add_page,
                    )
                    if pdf_bytes:
                        st.success("PDF erfolgreich erstellt.")
                        st.download_button(
                            label="Angebot herunterladen",
                            data=pdf_bytes,
                            file_name="angebot_mit_zahlungsplan.pdf",
                            mime="application/pdf",
                        )
                    else:
                        st.error(
                            "Es ist ein Fehler bei der PDF‑Erstellung aufgetreten.")
