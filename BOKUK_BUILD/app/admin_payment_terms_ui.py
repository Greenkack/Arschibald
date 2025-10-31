"""
admin_payment_terms_ui.py
--------------------------

Erweiterte Benutzeroberfläche für Administratoren zur umfassenden Konfiguration
der Zahlungsmodalitäten. Das Modul bietet:

1. Verwaltung verschiedener Zahlungsoptionen (Bar, Raten, Finanzierung)
2. Konfiguration von 4 spezifischen Zahlungsvarianten
3. Bearbeitung rechtlicher Texte und Bedingungen
4. Vorschau der konfigurierten Zahlungsmodalitäten
5. Import/Export von Zahlungskonfigurationen

Das UI folgt dem Stil anderer Admin‑Module im Projekt und verwendet
Tabs/Expander zur übersichtlichen Darstellung. Die Einstellungen werden
dauerhaft in der Admin‑Datenbank gespeichert.

Autor: System Integration für erweiterte Zahlungsmodalitäten
Version: 3.0 - Erweitert um spezifische Zahlungsvarianten mit Platzhaltern
"""

import copy
import json
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import streamlit as st

# Importiere bestehende Payment Terms falls verfügbar
try:
    from payment_terms import (
        get_payment_terms_config,
        save_payment_terms_config,
    )
    PAYMENT_TERMS_AVAILABLE = True
except ImportError:
    def get_payment_terms_config():
        return {}

    def save_payment_terms_config(config):
        return False


def _format_decimal_de(value: float, decimals: int = 2) -> str:
    """Format a number using German decimal separators."""
    try:
        formatted = f"{float(value):,.{decimals}f}"
    except Exception:
        formatted = f"{0.0:,.{decimals}f}"
    # Replace thousands and decimal separators to German style
    return formatted.replace(",", "#").replace(".", ",").replace("#", ".")


def format_percent_de(value: float) -> str:
    """Return a percent string formatted with comma and two decimals."""
    return f"{_format_decimal_de(value, 2)} %"


def format_currency_de(value: float) -> str:
    """Return a Euro string formatted with German separators."""
    return f"{_format_decimal_de(value, 2)} €"
    PAYMENT_TERMS_AVAILABLE = False


def get_default_payment_variants() -> dict[str, Any]:
    """Standard-Konfiguration für die 5 spezifischen Zahlungsvarianten."""
    base_labels = [
        "Anzahlung (%)",
        "Nach Lieferung & DC-Montage (%)",
        "Nach Inbetriebnahme (%)",
    ]
    base_amount_labels = [
        "Betrag Anzahlung (€)",
        "Betrag nach DC-Montage (€)",
        "Betrag nach Inbetriebnahme (€)",
    ]
    base_custom_labels = [
        "Anzahlung",
        "Nach DC-Montage",
        "Nach Inbetriebnahme",
    ]

    return {
        "variant_0": {
            "name": "Variante 0 (Keine Vorkasse)",
            "description": "Gesamtsumme erst nach Inbetriebnahme fällig",
            "enabled": True,
            "percents": [0.0, 0.0, 100.0],
            "percent_labels": base_labels,
            "amounts": [0.0, 0.0, 0.0],
            "amount_labels": base_amount_labels,
            "text_template": "Alle Zahlungen erfolgen gesammelt nach Inbetriebnahme: {p3_with_sign} bzw. {b3_with_sign}.",
            "validation_rule": "sum_100_percent",
            "is_static": True
        },
        "variant_1": {
            "name": "Variante 1 (Anzahlung/Raten)",
            "description": "Mit Anzahlung, Zwischenrate und Restzahlung",
            "enabled": True,
            "percents": [20.0, 60.0, 20.0],
            "percent_labels": base_labels,
            "amounts": [0.0, 0.0, 0.0],
            "amount_labels": base_amount_labels,
            "text_template": "Anzahlung {p1_with_sign} ({b1_with_sign}), nach DC-Montage {p2_with_sign} ({b2_with_sign}), nach Inbetriebnahme {p3_with_sign} ({b3_with_sign}).",
            "validation_rule": "sum_100_percent"
        },
        "variant_2": {
            "name": "Variante 2 (100% nach Fertigstellung)",
            "description": "Gesamte Zahlung nach Inbetriebnahme",
            "enabled": True,
            "percents": [0.0, 0.0, 100.0],
            "percent_labels": base_labels,
            "amounts": [0.0, 0.0, 0.0],
            "amount_labels": base_amount_labels,
            "text_template": "Keine Teilzahlungen: {p3_with_sign} ({b3_with_sign}) nach vollständiger Fertigstellung.",
            "is_static": True,
            "validation_rule": "sum_100_percent"
        },
        "variant_3": {
            "name": "Variante 3 (ohne Anzahlung)",
            "description": "Zwei Zahlungen nach Montage und Inbetriebnahme",
            "enabled": True,
            "percents": [0.0, 80.0, 20.0],
            "percent_labels": base_labels,
            "amounts": [0.0, 0.0, 0.0],
            "amount_labels": base_amount_labels,
            "text_template": "Nach DC-Montage {p2_with_sign} ({b2_with_sign}), nach Inbetriebnahme {p3_with_sign} ({b3_with_sign}).",
            "validation_rule": "sum_100_percent"
        },
        "variant_4": {
            "name": "Variante 4 (Individuell)",
            "description": "Drei konfigurierbare Teilzahlungen",
            "enabled": True,
            "percents": [40.0, 30.0, 30.0],
            "percent_labels": base_labels,
            "amounts": [0.0, 0.0, 0.0],
            "amount_labels": base_amount_labels,
            "custom_labels": base_custom_labels,
            "text_template": "{label1}: {p1_with_sign} ({b1_with_sign}), {label2}: {p2_with_sign} ({b2_with_sign}), {label3}: {p3_with_sign} ({b3_with_sign}).",
            "validation_rule": "sum_100_percent",
            "is_fully_customizable": True
        }
    }


def validate_payment_variant_percentages(
        variant_data: dict[str, Any]) -> tuple[bool, str]:
    """Validiert die Prozentwerte einer Zahlungsvariante."""
    percents = variant_data.get("percents", [])
    validation_rule = variant_data.get("validation_rule", "sum_100_percent")

    if validation_rule == "static_100_percent":
        return True, "OK"  # Statische Variante ist immer valide

    if validation_rule == "sum_100_percent_two_rates":
        if len(percents) >= 2:
            sum_percent = percents[0] + percents[1]
            if abs(sum_percent - 100.0) < 0.01:
                return True, "OK"
            return False, f"Summe der beiden Raten muss 100% sein (aktuell: {
                sum_percent:.1f}%)"
        return False, "Mindestens zwei Prozentangaben erforderlich"

    if validation_rule == "sum_100_percent":
        sum_percent = sum(p for p in percents if p > 0)
        if abs(sum_percent - 100.0) < 0.01:
            return True, "OK"
        return False, f"Summe aller Prozentangaben muss 100% sein (aktuell: {
            sum_percent:.1f}%)"

    return False, "Unbekannte Validierungsregel"


def format_payment_text_with_placeholders(
    text_template: str,
    percents: list[float],
    amounts: list[float],
    total_amount: float = 10000.0,
    custom_labels: list[str] | None = None
) -> str:
    """Ersetzt Platzhalter in Zahlungstext-Vorlagen."""

    # Beträge berechnen falls nicht explizit gesetzt
    calculated_amounts = []
    safe_percents = []
    for i in range(3):
        percent = percents[i] if i < len(percents) else 0.0
        safe_percents.append(percent)
        fixed_amount = amounts[i] if i < len(amounts) else 0.0
        if fixed_amount and fixed_amount > 0:
            calculated_amounts.append(round(float(fixed_amount), 2))
        else:
            calculated_amounts.append(round(percent / 100.0 * total_amount, 2))

    # Standard-Platzhalter ersetzen
    replacements: dict[str, Any] = {}
    for i in range(3):
        percent_value = safe_percents[i]
        amount_value = calculated_amounts[i] if i < len(
            calculated_amounts) else 0.0

        replacements[f"p{i + 1}"] = _format_decimal_de(percent_value, 2)
        replacements[f"p{i + 1}_with_sign"] = format_percent_de(percent_value)
        replacements[f"p{i + 1}_value"] = percent_value

        replacements[f"b{i + 1}"] = _format_decimal_de(amount_value, 2)
        replacements[f"b{i + 1}_with_sign"] = format_currency_de(amount_value)
        replacements[f"b{i + 1}_value"] = amount_value

    # Custom Labels für Variante 4
    if custom_labels:
        for i, label in enumerate(custom_labels):
            if i < 3:
                replacements[f"label{i + 1}"] = label

    try:
        return text_template.format(**replacements)
    except KeyError as e:
        return f"Fehler in Textvorlage: Unbekannter Platzhalter {e}"


def get_comprehensive_default_payment_terms() -> dict[str, Any]:
    """Umfassende Standard-Zahlungsmodalitäten zurückgeben."""
    return {"payment_options": [{"id": "cash_full",
                                 "name": "Vollzahlung bei Auftragserteilung",
                                 "description": "100% Zahlung bei Vertragsabschluss",
                                 "discount_percent": 3.0,
                                 "enabled": True,
                                 "icon": "💰",
                                 "payment_type": "immediate",
                                 "conditions": {"payment_due_days": 0,
                                                "early_payment_bonus": True}},
                                {"id": "cash_delivery",
                                 "name": "Barzahlung bei Lieferung",
                                 "description": "Zahlung bei Anlieferung der Komponenten",
                                 "discount_percent": 2.0,
                                 "enabled": True,
                                 "icon": "🚚",
                                 "payment_type": "on_delivery"},
                                {"id": "installments_2",
                                 "name": "2 Raten (50/50)",
                                 "description": "Zahlung in 2 gleichen Raten",
                                 "discount_percent": 1.0,
                                 "enabled": True,
                                 "icon": "📊",
                                 "payment_type": "installments",
                                 "installment_schedule": [{"percentage": 50.0,
                                                           "due_days": 0,
                                                           "description": "Bei Auftragserteilung",
                                                           "label": "Anzahlung"},
                                                          {"percentage": 50.0,
                                                           "due_days": 30,
                                                           "description": "Bei Fertigstellung",
                                                           "label": "Restzahlung"}]},
                                {"id": "installments_3",
                                 "name": "3 Raten",
                                 "description": "Zahlung in 3 gleichen Raten",
                                 "discount_percent": 0.0,
                                 "enabled": True,
                                 "icon": "📊",
                                 "payment_type": "installments",
                                 "installment_schedule": [{"percentage": 40.0,
                                                           "due_days": 0,
                                                           "description": "Bei Auftragserteilung",
                                                           "label": "Anzahlung"},
                                                          {"percentage": 40.0,
                                                           "due_days": 30,
                                                           "description": "Bei Lieferung",
                                                           "label": "Zwischenzahlung"},
                                                          {"percentage": 20.0,
                                                           "due_days": 60,
                                                           "description": "Nach Fertigstellung",
                                                           "label": "Restzahlung"}]},
                                {"id": "installments_custom",
                                 "name": "Individuelle Ratenzahlung",
                                 "description": "Kundenspezifische Zahlungsaufteilung",
                                 "discount_percent": 0.0,
                                 "enabled": False,
                                 "icon": "⚙️",
                                 "payment_type": "custom_installments",
                                 "customizable": True},
                                {"id": "financing_solar",
                                 "name": "Solarfinanzierung",
                                 "description": "Finanzierung über Partnerbank mit attraktiven Konditionen",
                                 "discount_percent": 0.0,
                                 "enabled": True,
                                 "icon": "🏦",
                                 "payment_type": "financing",
                                 "financing_options": [{"name": "Standard-Finanzierung",
                                                        "duration_months": 60,
                                                        "interest_rate": 2.9,
                                                        "monthly_fee": 0.0,
                                                        "min_amount": 5000.0,
                                                        "max_amount": 100000.0},
                                                       {"name": "Langzeit-Finanzierung",
                                                        "duration_months": 84,
                                                        "interest_rate": 3.4,
                                                        "monthly_fee": 0.0,
                                                        "min_amount": 10000.0,
                                                        "max_amount": 150000.0},
                                                       {"name": "Premium-Finanzierung",
                                                        "duration_months": 120,
                                                        "interest_rate": 3.9,
                                                        "monthly_fee": 5.0,
                                                        "min_amount": 15000.0,
                                                        "max_amount": 200000.0}]},
                                {"id": "leasing",
                                 "name": "Solar-Leasing",
                                 "description": "Keine Anschaffungskosten - monatliche Leasingrate",
                                 "discount_percent": 0.0,
                                 "enabled": False,
                                 "icon": "📋",
                                 "payment_type": "leasing",
                                 "leasing_options": [{"duration_months": 120,
                                                      "monthly_rate_factor": 0.012,
                                                      "buyout_option": True,
                                                      "buyout_percentage": 10.0}]}],
            "general_terms": {"warranty_years": 25,
                              "installation_warranty_years": 2,
                              "performance_warranty_years": 10,
                              "payment_due_days": 14,
                              "late_payment_fee_percent": 8.0,
                              "deposit_required": True,
                              "deposit_percentage": 30.0,
                              "min_deposit_amount": 1000.0,
                              "contract_validity_days": 30,
                              "price_validity_days": 14,
                              "installation_period_weeks": 8,
                              "completion_bonus_percent": 1.0,
                              "early_completion_bonus_days": 7},
            "discount_rules": {"volume_discounts": [{"min_kwp": 10.0,
                                                     "discount_percent": 1.0},
                                                    {"min_kwp": 20.0,
                                                     "discount_percent": 2.0},
                                                    {"min_kwp": 50.0,
                                                     "discount_percent": 3.0}],
                               "seasonal_discount": {"enabled": False,
                                                     "months": [11,
                                                                12,
                                                                1,
                                                                2],
                                                     "discount_percent": 2.0},
                               "referral_discount": {"enabled": True,
                                                     "discount_percent": 500.0,
                                                     "discount_type": "fixed_amount"}},
            "legal_texts": {"payment_terms": """Zahlungsbedingungen:
Die Zahlung erfolgt entsprechend der gewählten Zahlungsmodalität. Bei Verzug werden Verzugszinsen in gesetzlicher Höhe berechnet. Alle Preise verstehen sich inklusive der gesetzlichen Mehrwertsteuer.""",
                            "warranty_info": """Garantieleistungen:
- 25 Jahre Produktgarantie auf Solarmodule
- 10 Jahre Leistungsgarantie (min. 90% der Nennleistung)
- 2 Jahre Montagegarantie
- Herstellergarantie auf Wechselrichter gemäß Datenblatt""",
                            "delivery_info": """Lieferung und Installation:
Die Lieferzeit beträgt in der Regel 4-8 Wochen nach Auftragsbestätigung. Die Installation wird durch zertifizierte Fachbetriebe durchgeführt. Der Kunde wird rechtzeitig über den Installationstermin informiert.""",
                            "cancellation_policy": """Widerrufsrecht:
Verbrauchern steht ein gesetzliches Widerrufsrecht von 14 Tagen zu. Bei bereits begonnenen Arbeiten kann eine angemessene Entschädigung für erbrachte Leistungen berechnet werden.""",
                            "data_protection": """Datenschutz:
Die Verarbeitung personenbezogener Daten erfolgt gemäß DSGVO. Detaillierte Informationen finden Sie in unserer Datenschutzerklärung.""",
                            "general_conditions": """Allgemeine Geschäftsbedingungen:
Es gelten unsere aktuellen AGB. Änderungen bedürfen der Schriftform. Erfüllungsort und Gerichtsstand ist unser Firmensitz."""},
            "calculation_settings": {"currency": "EUR",
                                     "tax_rate_percent": 19.0,
                                     "payment_processing_fee_percent": 1.5,
                                     "financing_processing_fee": 50.0,
                                     "round_to_cents": True,
                                     "show_net_prices": False},
            "display_settings": {"show_discounts": True,
                                 "show_financing_details": True,
                                 "show_monthly_rates": True,
                                 "highlight_recommended": True,
                                 "recommended_option": "installments_3",
                                 "color_scheme": {"primary": "#1E88E5",
                                                  "success": "#43A047",
                                                  "warning": "#FB8C00",
                                                  "error": "#E53935"}}}


def render_payment_options_management(
        payment_options: list[dict[str, Any]], widget_suffix: str) -> list[dict[str, Any]]:
    """Erweiterte UI für die Verwaltung der Zahlungsoptionen."""
    st.subheader("💳 Zahlungsoptionen verwalten")
    st.markdown(
        "Konfigurieren Sie die verfügbaren Zahlungsmodalitäten für Ihre Kunden.")

    # Buttons für das Hinzufügen neuer Optionen
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Barzahlung", key=f"add_cash_{widget_suffix}"):
            new_option = {
                "id": f"cash_{
                    len(payment_options)}_{
                    datetime.now().strftime('%H%M%S')}",
                "name": "Neue Barzahlung",
                "description": "Sofortige Zahlung",
                "discount_percent": 2.0,
                "enabled": True,
                "icon": "💰",
                "payment_type": "immediate"}
            payment_options.append(new_option)
            st.rerun()

    with col2:
        if st.button("➕ Ratenzahlung", key=f"add_installment_{widget_suffix}"):
            new_option = {
                "id": f"installment_{len(payment_options)}_{datetime.now().strftime('%H%M%S')}",
                "name": "Neue Ratenzahlung",
                "description": "Zahlung in Raten",
                "discount_percent": 0.0,
                "enabled": True,
                "icon": "📊",
                "payment_type": "installments",
                "installment_schedule": [
                    {"percentage": 50.0, "due_days": 0, "description": "Anzahlung", "label": "Anzahlung"},
                    {"percentage": 50.0, "due_days": 30, "description": "Restzahlung", "label": "Restzahlung"}
                ]
            }
            payment_options.append(new_option)
            st.rerun()

    with col3:
        if st.button("➕ Finanzierung", key=f"add_financing_{widget_suffix}"):
            new_option = {
                "id": f"financing_{len(payment_options)}_{datetime.now().strftime('%H%M%S')}",
                "name": "Neue Finanzierung",
                "description": "Finanzierung über Bank",
                "discount_percent": 0.0,
                "enabled": True,
                "icon": "🏦",
                "payment_type": "financing",
                "financing_options": [
                    {"duration_months": 60, "interest_rate": 3.0, "monthly_fee": 0.0}
                ]
            }
            payment_options.append(new_option)
            st.rerun()

    with col4:
        if st.button("➕ Benutzerdefiniert", key=f"add_custom_{widget_suffix}"):
            new_option = {
                "id": f"custom_{
                    len(payment_options)}_{
                    datetime.now().strftime('%H%M%S')}",
                "name": "Benutzerdefinierte Option",
                "description": "Individuelle Zahlungsmodalität",
                "discount_percent": 0.0,
                "enabled": False,
                "icon": "⚙️",
                "payment_type": "custom"}
            payment_options.append(new_option)
            st.rerun()

    st.markdown("---")

    # Bestehende Optionen bearbeiten
    updated_options = []
    for i, option in enumerate(payment_options):
        option_id = option.get('id', f'option_{i}')

        with st.expander(f"{option.get('icon', '💳')} {option.get('name', 'Unbenannt')} ({'Aktiv' if option.get('enabled', True) else 'Inaktiv'})", expanded=False):

            # Grundeinstellungen
            col_basic1, col_basic2 = st.columns(2)

            with col_basic1:
                option['name'] = st.text_input(
                    "Name der Zahlungsoption",
                    value=option.get('name', ''),
                    key=f"option_name_{option_id}_{widget_suffix}"
                )

                option['icon'] = st.selectbox(
                    "Icon",
                    options=[
                        "💰",
                        "🚚",
                        "📊",
                        "🏦",
                        "📋",
                        "⚙️",
                        "💳",
                        "🎯",
                        "⭐",
                        "🔥"],
                    index=[
                        "💰",
                        "🚚",
                        "📊",
                        "🏦",
                        "📋",
                        "⚙️",
                        "💳",
                        "🎯",
                        "⭐",
                        "🔥"].index(
                        option.get(
                            'icon',
                            '💳')) if option.get(
                        'icon',
                        '💳') in [
                            "💰",
                            "🚚",
                            "📊",
                            "🏦",
                            "📋",
                            "⚙️",
                            "💳",
                            "🎯",
                            "⭐",
                            "🔥"] else 0,
                    key=f"option_icon_{option_id}_{widget_suffix}")

                option['discount_percent'] = st.number_input(
                    "Rabatt (%)",
                    value=float(option.get('discount_percent', 0.0)),
                    min_value=0.0,
                    max_value=50.0,
                    step=0.1,
                    key=f"option_discount_{option_id}_{widget_suffix}"
                )

            with col_basic2:
                option['description'] = st.text_area(
                    "Beschreibung",
                    value=option.get('description', ''),
                    height=80,
                    key=f"option_desc_{option_id}_{widget_suffix}"
                )

                option['enabled'] = st.checkbox(
                    "Option aktiviert",
                    value=option.get('enabled', True),
                    key=f"option_enabled_{option_id}_{widget_suffix}"
                )

                option['payment_type'] = st.selectbox(
                    "Zahlungstyp",
                    options=[
                        "immediate",
                        "on_delivery",
                        "installments",
                        "financing",
                        "leasing",
                        "custom"],
                    index=[
                        "immediate",
                        "on_delivery",
                        "installments",
                        "financing",
                        "leasing",
                        "custom"].index(
                        option.get(
                            'payment_type',
                            'immediate')) if option.get(
                        'payment_type',
                        'immediate') in [
                            "immediate",
                            "on_delivery",
                            "installments",
                            "financing",
                            "leasing",
                            "custom"] else 0,
                    key=f"option_type_{option_id}_{widget_suffix}")

            # Spezielle Konfigurationen je nach Zahlungstyp
            payment_type = option.get('payment_type', 'immediate')

            if payment_type == "installments":
                st.markdown("**📊 Ratenzahlungsplan konfigurieren:**")
                schedule = option.get('installment_schedule', [])

                # Button zum Hinzufügen einer neuen Rate
                if st.button(
                    "➕ Rate hinzufügen",
                        key=f"add_installment_{option_id}_{widget_suffix}"):
                    schedule.append({
                        "percentage": 20.0,
                        "due_days": len(schedule) * 30,
                        "description": f"Rate {len(schedule) + 1}",
                        "label": f"Rate {len(schedule) + 1}"
                    })
                    option['installment_schedule'] = schedule
                    st.rerun()

                updated_schedule = []
                for j, installment in enumerate(schedule):
                    st.markdown(f"**Rate {j + 1}:**")
                    col_inst1, col_inst2, col_inst3, col_inst4 = st.columns(4)

                    installment['percentage'] = col_inst1.number_input(
                        "Anteil (%)",
                        value=float(installment.get('percentage', 0.0)),
                        min_value=0.0,
                        max_value=100.0,
                        step=1.0,
                        key=f"installment_pct_{option_id}_{j}_{widget_suffix}"
                    )

                    installment['due_days'] = col_inst2.number_input(
                        "Fällig nach (Tagen)",
                        value=int(installment.get('due_days', 0)),
                        min_value=0,
                        max_value=365,
                        step=1,
                        key=f"installment_days_{option_id}_{j}_{widget_suffix}"
                    )

                    installment['label'] = col_inst3.text_input(
                        "Bezeichnung", value=installment.get(
                            'label', ''), key=f"installment_label_{option_id}_{j}_{widget_suffix}")

                    if col_inst4.button(
                        "🗑️",
                        key=f"del_installment_{option_id}_{j}_{widget_suffix}",
                            help="Rate löschen"):
                        continue  # Rate wird nicht zu updated_schedule hinzugefügt

                    installment['description'] = st.text_input(
                        f"Beschreibung Rate {j + 1}",
                        value=installment.get('description', ''),
                        key=f"installment_desc_{option_id}_{j}_{widget_suffix}"
                    )

                    updated_schedule.append(installment)

                option['installment_schedule'] = updated_schedule

                # Validierung der Prozentwerte
                total_percentage = sum(inst.get('percentage', 0)
                                       for inst in updated_schedule)
                if total_percentage != 100.0:
                    st.warning(
                        f"⚠️ Summe der Raten: {total_percentage}% (sollte 100% sein)")

            elif payment_type == "financing":
                st.markdown("**🏦 Finanzierungsoptionen konfigurieren:**")
                financing_opts = option.get('financing_options', [])

                # Button zum Hinzufügen einer neuen Finanzierungsoption
                if st.button(
                    "➕ Finanzierungsoption hinzufügen",
                        key=f"add_financing_{option_id}_{widget_suffix}"):
                    financing_opts.append({
                        "name": f"Option {len(financing_opts) + 1}",
                        "duration_months": 60,
                        "interest_rate": 3.0,
                        "monthly_fee": 0.0,
                        "min_amount": 5000.0,
                        "max_amount": 100000.0
                    })
                    option['financing_options'] = financing_opts
                    st.rerun()

                updated_financing = []
                for k, fin_opt in enumerate(financing_opts):
                    st.markdown(f"**Finanzierungsoption {k + 1}:**")
                    col_fin1, col_fin2, col_fin3, col_fin4 = st.columns(4)

                    fin_opt['name'] = col_fin1.text_input(
                        "Name",
                        value=fin_opt.get('name', ''),
                        key=f"fin_name_{option_id}_{k}_{widget_suffix}"
                    )

                    fin_opt['duration_months'] = col_fin2.number_input(
                        "Laufzeit (Monate)",
                        value=int(fin_opt.get('duration_months', 60)),
                        min_value=12,
                        max_value=240,
                        step=12,
                        key=f"fin_duration_{option_id}_{k}_{widget_suffix}"
                    )

                    fin_opt['interest_rate'] = col_fin3.number_input(
                        "Zinssatz (%)",
                        value=float(fin_opt.get('interest_rate', 3.0)),
                        min_value=0.0,
                        max_value=20.0,
                        step=0.1,
                        key=f"fin_rate_{option_id}_{k}_{widget_suffix}"
                    )

                    if col_fin4.button(
                        "🗑️",
                        key=f"del_financing_{option_id}_{k}_{widget_suffix}",
                            help="Finanzierungsoption löschen"):
                        continue  # Option wird nicht zu updated_financing hinzugefügt

                    col_fee1, col_fee2, col_fee3 = st.columns(3)

                    fin_opt['monthly_fee'] = col_fee1.number_input(
                        "Monatl. Gebühr (€)",
                        value=float(fin_opt.get('monthly_fee', 0.0)),
                        min_value=0.0,
                        max_value=100.0,
                        step=1.0,
                        key=f"fin_fee_{option_id}_{k}_{widget_suffix}"
                    )

                    fin_opt['min_amount'] = col_fee2.number_input(
                        "Min. Betrag (€)",
                        value=float(fin_opt.get('min_amount', 5000.0)),
                        min_value=0.0,
                        step=1000.0,
                        key=f"fin_min_{option_id}_{k}_{widget_suffix}"
                    )

                    fin_opt['max_amount'] = col_fee3.number_input(
                        "Max. Betrag (€)",
                        value=max(
                            float(
                                fin_opt.get(
                                    'max_amount',
                                    100000.0)),
                            1000.0),
                        min_value=1000.0,
                        step=1000.0,
                        key=f"fin_max_{option_id}_{k}_{widget_suffix}")

                    updated_financing.append(fin_opt)

                option['financing_options'] = updated_financing

            elif payment_type == "leasing":
                st.markdown("**📋 Leasing-Konfiguration:**")
                leasing_opts = option.get('leasing_options', [{}])

                if leasing_opts:
                    leasing_opt = leasing_opts[0]

                    col_lease1, col_lease2 = st.columns(2)

                    leasing_opt['duration_months'] = col_lease1.number_input(
                        "Laufzeit (Monate)",
                        value=int(leasing_opt.get('duration_months', 120)),
                        min_value=24,
                        max_value=240,
                        step=12,
                        key=f"lease_duration_{option_id}_{widget_suffix}"
                    )

                    leasing_opt['monthly_rate_factor'] = col_lease2.number_input(
                        "Monatsfaktor (%)",
                        value=max(
                            float(
                                leasing_opt.get(
                                    'monthly_rate_factor',
                                    1.2)),
                            0.5),
                        min_value=0.5,
                        max_value=5.0,
                        step=0.1,
                        key=f"lease_factor_{option_id}_{widget_suffix}",
                        help="Faktor zur Berechnung der monatlichen Leasingrate")

                    leasing_opt['buyout_option'] = st.checkbox(
                        "Kaufoption am Ende",
                        value=leasing_opt.get('buyout_option', True),
                        key=f"lease_buyout_{option_id}_{widget_suffix}"
                    )

                    if leasing_opt.get('buyout_option', True):
                        leasing_opt['buyout_percentage'] = st.number_input(
                            "Kaufpreis am Ende (%)",
                            value=max(
                                float(
                                    leasing_opt.get(
                                        'buyout_percentage',
                                        10.0)),
                                1.0),
                            min_value=1.0,
                            max_value=50.0,
                            step=1.0,
                            key=f"lease_buyout_pct_{option_id}_{widget_suffix}")

                    option['leasing_options'] = [leasing_opt]

            # Option löschen
            st.markdown("---")
            if st.button(
                f"🗑️ Zahlungsoption '{
                    option.get(
                        'name',
                        'Unbenannt')}' löschen",
                    key=f"delete_option_{option_id}_{widget_suffix}"):
                if st.session_state.get(f"confirm_delete_{option_id}", False):
                    # Option nicht zu updated_options hinzufügen = löschen
                    st.session_state[f"confirm_delete_{option_id}"] = False
                    st.success(
                        f"Option '{
                            option.get(
                                'name',
                                'Unbenannt')}' wurde gelöscht.")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{option_id}"] = True
                    st.warning("Erneut klicken um zu bestätigen!")
                    st.rerun()

            if not st.session_state.get(f"confirm_delete_{option_id}", False):
                updated_options.append(option)

    return updated_options


def render_general_terms_management(
        general_terms: dict[str, Any], widget_suffix: str) -> dict[str, Any]:
    """Erweiterte UI für allgemeine Zahlungsbedingungen."""
    st.subheader("⚖️ Allgemeine Geschäftsbedingungen")
    st.markdown(
        "Konfigurieren Sie die grundlegenden Bedingungen für alle Zahlungsmodalitäten.")

    # Hauptbedingungen
    st.markdown("**📋 Grundlegende Bedingungen:**")
    col1, col2, col3 = st.columns(3)

    with col1:
        general_terms['warranty_years'] = st.number_input(
            "Produktgarantie (Jahre)",
            value=int(general_terms.get('warranty_years', 25)),
            min_value=1,
            max_value=50,
            step=1,
            key=f"warranty_years_{widget_suffix}",
            help="Herstellergarantie auf Solarmodule"
        )

        general_terms['installation_warranty_years'] = st.number_input(
            "Montagegarantie (Jahre)",
            value=int(general_terms.get('installation_warranty_years', 2)),
            min_value=1,
            max_value=10,
            step=1,
            key=f"install_warranty_{widget_suffix}",
            help="Garantie auf Montage und Installation"
        )

        general_terms['performance_warranty_years'] = st.number_input(
            "Leistungsgarantie (Jahre)",
            value=int(general_terms.get('performance_warranty_years', 10)),
            min_value=1,
            max_value=30,
            step=1,
            key=f"performance_warranty_{widget_suffix}",
            help="Garantie auf Mindestleistung der Module"
        )

    with col2:
        general_terms['payment_due_days'] = st.number_input(
            "Standard-Zahlungsziel (Tage)",
            value=int(general_terms.get('payment_due_days', 14)),
            min_value=1,
            max_value=90,
            step=1,
            key=f"payment_due_{widget_suffix}",
            help="Standardfrist für Rechnungszahlung"
        )

        general_terms['contract_validity_days'] = st.number_input(
            "Angebotsgültigkeit (Tage)",
            value=int(general_terms.get('contract_validity_days', 30)),
            min_value=1,
            max_value=365,
            step=1,
            key=f"contract_validity_{widget_suffix}",
            help="Gültigkeitsdauer von Angeboten"
        )

        general_terms['price_validity_days'] = st.number_input(
            "Preisgültigkeit (Tage)",
            value=int(general_terms.get('price_validity_days', 14)),
            min_value=1,
            max_value=90,
            step=1,
            key=f"price_validity_{widget_suffix}",
            help="Gültigkeitsdauer der angegebenen Preise"
        )

    with col3:
        general_terms['late_payment_fee_percent'] = st.number_input(
            "Verzugszinsen (% p.a.)",
            value=float(general_terms.get('late_payment_fee_percent', 8.0)),
            min_value=0.0,
            max_value=20.0,
            step=0.1,
            key=f"late_fee_{widget_suffix}",
            help="Jährlicher Zinssatz bei verspäteter Zahlung"
        )

        general_terms['installation_period_weeks'] = st.number_input(
            "Installationsdauer (Wochen)",
            value=int(general_terms.get('installation_period_weeks', 8)),
            min_value=1,
            max_value=52,
            step=1,
            key=f"install_period_{widget_suffix}",
            help="Geschätzte Dauer von Auftrag bis Fertigstellung"
        )

        general_terms['completion_bonus_percent'] = st.number_input(
            "Fertigstellungsbonus (%)",
            value=float(general_terms.get('completion_bonus_percent', 1.0)),
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            key=f"completion_bonus_{widget_suffix}",
            help="Bonus bei termingerechter Fertigstellung"
        )

    # Anzahlungsregelungen
    st.markdown("**💰 Anzahlungsregelungen:**")
    col_deposit1, col_deposit2, col_deposit3 = st.columns(3)

    with col_deposit1:
        general_terms['deposit_required'] = st.checkbox(
            "Anzahlung erforderlich",
            value=general_terms.get('deposit_required', True),
            key=f"deposit_required_{widget_suffix}",
            help="Ist eine Anzahlung bei Auftragserteilung erforderlich?"
        )

    if general_terms.get('deposit_required', True):
        with col_deposit2:
            general_terms['deposit_percentage'] = st.number_input(
                "Anzahlung (%)",
                value=float(general_terms.get('deposit_percentage', 30.0)),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key=f"deposit_pct_{widget_suffix}",
                help="Prozentualer Anteil der Anzahlung"
            )

        with col_deposit3:
            general_terms['min_deposit_amount'] = st.number_input(
                "Mindest-Anzahlung (€)",
                value=float(general_terms.get('min_deposit_amount', 1000.0)),
                min_value=0.0,
                step=100.0,
                key=f"min_deposit_{widget_suffix}",
                help="Minimaler Betrag für die Anzahlung"
            )

    return general_terms


def render_discount_rules_management(
        discount_rules: dict[str, Any], widget_suffix: str) -> dict[str, Any]:
    """UI für die Verwaltung von Rabattregeln."""
    st.subheader("🎯 Rabatt- und Bonusregelungen")
    st.markdown(
        "Konfigurieren Sie automatische Rabatte basierend auf verschiedenen Kriterien.")

    # Mengenrabatte
    st.markdown("**📊 Mengenrabatte (nach kWp):**")
    volume_discounts = discount_rules.get('volume_discounts', [])

    if st.button("➕ Mengenstaffel hinzufügen",
                 key=f"add_volume_discount_{widget_suffix}"):
        volume_discounts.append({"min_kwp": 10.0, "discount_percent": 1.0})
        discount_rules['volume_discounts'] = volume_discounts
        st.rerun()

    updated_volume_discounts = []
    for i, vd in enumerate(volume_discounts):
        col_vd1, col_vd2, col_vd3 = st.columns([2, 2, 1])

        vd['min_kwp'] = col_vd1.number_input(
            "Ab kWp",
            value=float(vd.get('min_kwp', 10.0)),
            min_value=0.0,
            step=1.0,
            key=f"volume_kwp_{i}_{widget_suffix}"
        )

        vd['discount_percent'] = col_vd2.number_input(
            "Rabatt (%)",
            value=float(vd.get('discount_percent', 1.0)),
            min_value=0.0,
            max_value=50.0,
            step=0.1,
            key=f"volume_discount_{i}_{widget_suffix}"
        )

        if col_vd3.button(
            "🗑️",
            key=f"del_volume_{i}_{widget_suffix}",
                help="Mengenstaffel löschen"):
            continue  # Nicht zu updated_volume_discounts hinzufügen

        updated_volume_discounts.append(vd)

    discount_rules['volume_discounts'] = updated_volume_discounts

    # Saisonrabatt
    st.markdown("**🌟 Saisonaler Rabatt:**")
    seasonal = discount_rules.get('seasonal_discount', {})

    col_season1, col_season2, col_season3 = st.columns(3)

    with col_season1:
        seasonal['enabled'] = st.checkbox(
            "Saisonrabatt aktiviert",
            value=seasonal.get('enabled', False),
            key=f"seasonal_enabled_{widget_suffix}"
        )

    if seasonal.get('enabled', False):
        with col_season2:
            seasonal['discount_percent'] = st.number_input(
                "Saisonrabatt (%)",
                value=float(seasonal.get('discount_percent', 2.0)),
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                key=f"seasonal_discount_{widget_suffix}"
            )

        with col_season3:
            seasonal['months'] = st.multiselect(
                "Gültige Monate",
                options=list(range(1, 13)),
                default=seasonal.get('months', [11, 12, 1, 2]),
                format_func=lambda x: [
                    "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                    "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"
                ][x - 1],
                key=f"seasonal_months_{widget_suffix}"
            )

    discount_rules['seasonal_discount'] = seasonal

    # Empfehlungsrabatt
    st.markdown("**👥 Empfehlungsrabatt:**")
    referral = discount_rules.get('referral_discount', {})

    col_ref1, col_ref2, col_ref3 = st.columns(3)

    with col_ref1:
        referral['enabled'] = st.checkbox(
            "Empfehlungsrabatt aktiviert",
            value=referral.get('enabled', True),
            key=f"referral_enabled_{widget_suffix}"
        )

    if referral.get('enabled', True):
        with col_ref2:
            referral['discount_type'] = st.selectbox(
                "Rabatttyp",
                options=[
                    "percentage",
                    "fixed_amount"],
                index=0 if referral.get(
                    'discount_type',
                    'percentage') == 'percentage' else 1,
                format_func=lambda x: "Prozentual" if x == "percentage" else "Fester Betrag",
                key=f"referral_type_{widget_suffix}")

        with col_ref3:
            if referral.get('discount_type', 'percentage') == 'percentage':
                referral['discount_percent'] = st.number_input(
                    "Empfehlungsrabatt (%)",
                    value=float(referral.get('discount_percent', 5.0)),
                    min_value=0.0,
                    max_value=20.0,
                    step=0.1,
                    key=f"referral_discount_{widget_suffix}"
                )
            else:
                referral['discount_amount'] = st.number_input(
                    "Empfehlungsrabatt (€)",
                    value=float(referral.get('discount_amount', 500.0)),
                    min_value=0.0,
                    step=50.0,
                    key=f"referral_amount_{widget_suffix}"
                )

    discount_rules['referral_discount'] = referral

    return discount_rules


def render_legal_texts_management(
        legal_texts: dict[str, str], widget_suffix: str) -> dict[str, str]:
    """Erweiterte UI für rechtliche Texte und Bedingungen."""
    st.subheader("📋 Rechtliche Texte und Bedingungen")
    st.markdown(
        "Bearbeiten Sie die standardmäßigen rechtlichen Texte für Angebote und Verträge.")

    # Tab-Navigation für verschiedene Textbereiche
    text_tabs = st.tabs([
        "💳 Zahlungsbedingungen",
        "🛡️ Garantien",
        "🚚 Lieferung",
        "↩️ Widerruf",
        "🔒 Datenschutz",
        "📄 AGB"
    ])

    with text_tabs[0]:
        legal_texts['payment_terms'] = st.text_area(
            "Zahlungsbedingungen",
            value=legal_texts.get('payment_terms', ''),
            height=150,
            key=f"legal_payment_{widget_suffix}",
            help="Allgemeine Zahlungsbedingungen für alle Zahlungsarten"
        )

    with text_tabs[1]:
        legal_texts['warranty_info'] = st.text_area(
            "Garantieinformationen",
            value=legal_texts.get(
                'warranty_info',
                ''),
            height=150,
            key=f"legal_warranty_{widget_suffix}",
            help="Detaillierte Informationen zu Produkt- und Leistungsgarantien")

    with text_tabs[2]:
        legal_texts['delivery_info'] = st.text_area(
            "Lieferinformationen",
            value=legal_texts.get('delivery_info', ''),
            height=150,
            key=f"legal_delivery_{widget_suffix}",
            help="Informationen zu Lieferzeiten und Installationsablauf"
        )

    with text_tabs[3]:
        legal_texts['cancellation_policy'] = st.text_area(
            "Widerrufsbelehrung",
            value=legal_texts.get('cancellation_policy', ''),
            height=150,
            key=f"legal_cancellation_{widget_suffix}",
            help="Gesetzliche Widerrufsbelehrung für Verbraucher"
        )

    with text_tabs[4]:
        legal_texts['data_protection'] = st.text_area(
            "Datenschutzhinweise",
            value=legal_texts.get('data_protection', ''),
            height=150,
            key=f"legal_data_protection_{widget_suffix}",
            help="Hinweise zur Datenverarbeitung gemäß DSGVO"
        )

    with text_tabs[5]:
        legal_texts['general_conditions'] = st.text_area(
            "Allgemeine Geschäftsbedingungen",
            value=legal_texts.get('general_conditions', ''),
            height=150,
            key=f"legal_general_{widget_suffix}",
            help="Verweis auf die vollständigen AGB"
        )

    return legal_texts


def render_calculation_settings(
        calc_settings: dict[str, Any], widget_suffix: str) -> dict[str, Any]:
    """UI für Berechnungseinstellungen."""
    st.subheader("🧮 Berechnungseinstellungen")
    st.markdown(
        "Konfigurieren Sie die Parameter für Preisberechnungen und Darstellung.")

    col_calc1, col_calc2, col_calc3 = st.columns(3)

    with col_calc1:
        calc_settings['currency'] = st.selectbox(
            "Währung", options=[
                "EUR", "USD", "CHF"], index=[
                "EUR", "USD", "CHF"].index(
                calc_settings.get(
                    'currency', 'EUR')), key=f"calc_currency_{widget_suffix}")

        calc_settings['tax_rate_percent'] = st.number_input(
            "Mehrwertsteuersatz (%)",
            value=float(calc_settings.get('tax_rate_percent', 19.0)),
            min_value=0.0,
            max_value=30.0,
            step=0.1,
            key=f"calc_tax_rate_{widget_suffix}"
        )

    with col_calc2:
        calc_settings['payment_processing_fee_percent'] = st.number_input(
            "Zahlungsgebühr (%)",
            value=float(
                calc_settings.get(
                    'payment_processing_fee_percent',
                    1.5)),
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            key=f"calc_payment_fee_{widget_suffix}",
            help="Gebühr für Kartenzahlung o.ä.")

        calc_settings['financing_processing_fee'] = st.number_input(
            "Finanzierungsgebühr (€)",
            value=float(calc_settings.get('financing_processing_fee', 50.0)),
            min_value=0.0,
            step=10.0,
            key=f"calc_financing_fee_{widget_suffix}",
            help="Einmalige Bearbeitungsgebühr für Finanzierung"
        )

    with col_calc3:
        calc_settings['round_to_cents'] = st.checkbox(
            "Auf Cent runden",
            value=calc_settings.get('round_to_cents', True),
            key=f"calc_round_cents_{widget_suffix}"
        )

        calc_settings['show_net_prices'] = st.checkbox(
            "Nettopreise anzeigen",
            value=calc_settings.get('show_net_prices', False),
            key=f"calc_show_net_{widget_suffix}",
            help="Zusätzlich zu Bruttopreisen auch Nettopreise anzeigen"
        )

    return calc_settings


def render_display_settings(
        display_settings: dict[str, Any], widget_suffix: str) -> dict[str, Any]:
    """UI für Darstellungseinstellungen."""
    st.subheader("🎨 Darstellungseinstellungen")
    st.markdown(
        "Konfigurieren Sie das Aussehen der Zahlungsmodalitäten in Angeboten.")

    col_display1, col_display2 = st.columns(2)

    with col_display1:
        display_settings['show_discounts'] = st.checkbox(
            "Rabatte hervorheben",
            value=display_settings.get('show_discounts', True),
            key=f"display_discounts_{widget_suffix}"
        )

        display_settings['show_financing_details'] = st.checkbox(
            "Finanzierungsdetails anzeigen",
            value=display_settings.get('show_financing_details', True),
            key=f"display_financing_{widget_suffix}"
        )

        display_settings['show_monthly_rates'] = st.checkbox(
            "Monatsraten anzeigen",
            value=display_settings.get('show_monthly_rates', True),
            key=f"display_monthly_{widget_suffix}"
        )

    with col_display2:
        display_settings['highlight_recommended'] = st.checkbox(
            "Empfohlene Option hervorheben",
            value=display_settings.get('highlight_recommended', True),
            key=f"display_highlight_{widget_suffix}"
        )

        if display_settings.get('highlight_recommended', True):
            # Hier könnte eine Dropdown-Liste der verfügbaren Zahlungsoptionen
            # stehen
            display_settings['recommended_option'] = st.text_input(
                "ID der empfohlenen Option",
                value=display_settings.get(
                    'recommended_option',
                    'installments_3'),
                key=f"display_recommended_{widget_suffix}",
                help="ID der Zahlungsoption, die als empfohlen markiert werden soll")

    # Farbschema
    st.markdown("**🎨 Farbschema:**")
    color_scheme = display_settings.get('color_scheme', {})

    col_color1, col_color2, col_color3, col_color4 = st.columns(4)

    with col_color1:
        color_scheme['primary'] = st.color_picker(
            "Primärfarbe",
            value=color_scheme.get('primary', '#1E88E5'),
            key=f"color_primary_{widget_suffix}"
        )

    with col_color2:
        color_scheme['success'] = st.color_picker(
            "Erfolgsfarbe",
            value=color_scheme.get('success', '#43A047'),
            key=f"color_success_{widget_suffix}"
        )

    with col_color3:
        color_scheme['warning'] = st.color_picker(
            "Warnfarbe",
            value=color_scheme.get('warning', '#FB8C00'),
            key=f"color_warning_{widget_suffix}"
        )

    with col_color4:
        color_scheme['error'] = st.color_picker(
            "Fehlerfarbe",
            value=color_scheme.get('error', '#E53935'),
            key=f"color_error_{widget_suffix}"
        )

    display_settings['color_scheme'] = color_scheme

    return display_settings


def render_payment_preview_detailed(
        payment_terms: dict[str, Any], example_price: float = 25000.0) -> None:
    """Detaillierte Vorschau der konfigurierten Zahlungsmodalitäten."""
    st.subheader("👁️ Detaillierte Vorschau")
    st.markdown(
        f"Simulation für eine Beispielanlage im Wert von **{example_price:,.2f} €**")

    # Beispielpreis anpassbar machen
    example_price = st.slider(
        "Beispielpreis für Simulation (€)",
        min_value=5000.0,
        max_value=100000.0,
        value=example_price,
        step=1000.0,
        key="preview_example_price"
    )

    # Aktive Zahlungsoptionen filtern
    active_options = [
        opt for opt in payment_terms.get('payment_options', [])
        if opt.get('enabled', True)
    ]

    if not active_options:
        st.warning("⚠️ Keine aktiven Zahlungsoptionen konfiguriert!")
        return

    # Rabattregeln anwenden
    volume_discounts = payment_terms.get(
        'discount_rules', {}).get(
        'volume_discounts', [])
    system_kwp = example_price / 1500  # Annahme: 1500€/kWp
    volume_discount = 0.0

    for vd in sorted(
            volume_discounts,
            key=lambda x: x.get(
                'min_kwp',
                0),
            reverse=True):
        if system_kwp >= vd.get('min_kwp', 0):
            volume_discount = vd.get('discount_percent', 0)
            break

    # Saisonaler Rabatt (für Demo immer aktiv)
    seasonal_discount = 0.0
    seasonal = payment_terms.get(
        'discount_rules', {}).get(
        'seasonal_discount', {})
    if seasonal.get('enabled', False):
        current_month = datetime.now().month
        if current_month in seasonal.get('months', []):
            seasonal_discount = seasonal.get('discount_percent', 0)

    if volume_discount > 0:
        st.info(
            f"📊 Mengenrabatt: {volume_discount}% (ab {
                volume_discounts[0].get(
                    'min_kwp', 0)} kWp)")

    if seasonal_discount > 0:
        st.info(f"🌟 Saisonrabatt: {seasonal_discount}% (aktueller Monat)")

    # Zahlungsoptionen darstellen
    recommended_id = payment_terms.get(
        'display_settings', {}).get(
        'recommended_option', '')

    for i, option in enumerate(active_options):
        is_recommended = option.get('id') == recommended_id

        # Container für jede Zahlungsoption
        container = st.container()
        if is_recommended:
            container.markdown("🌟 **EMPFOHLEN**")

        with container:
            col_main1, col_main2 = st.columns([2, 3])

            with col_main1:
                # Header mit Icon und Name
                st.markdown(
                    f"### {
                        option.get(
                            'icon',
                            '💳')} {
                        option.get(
                            'name',
                            'Unbenannt')}")
                st.markdown(f"*{option.get('description', '')}*")

                # Gesamtrabatt berechnen
                total_discount = (
                    option.get('discount_percent', 0) +
                    volume_discount +
                    seasonal_discount
                )

                if total_discount > 0:
                    discount_amount = example_price * total_discount / 100
                    final_price = example_price - discount_amount
                    st.success(
                        f"💰 Gesamtrabatt: {total_discount:.1f}% (-{discount_amount:,.2f} €)")
                    st.markdown(f"**Endpreis: {final_price:,.2f} €**")
                else:
                    final_price = example_price
                    st.markdown(f"**Preis: {final_price:,.2f} €**")

            with col_main2:
                payment_type = option.get('payment_type', 'immediate')

                if payment_type == "installments":
                    st.markdown("**📊 Zahlungsplan:**")
                    schedule = option.get('installment_schedule', [])

                    for j, installment in enumerate(schedule):
                        amount = final_price * \
                            installment.get('percentage', 0) / 100
                        due_date = datetime.now() + timedelta(days=installment.get('due_days', 0))
                        label = installment.get('label', f'Rate {j + 1}')
                        description = installment.get('description', '')

                        st.markdown(
                            f"- **{label}**: {amount:,.2f} € "
                            f"({installment.get('percentage', 0):.0f}%) - "
                            f"{description} "
                            f"(fällig: {due_date.strftime('%d.%m.%Y')})"
                        )

                elif payment_type == "financing":
                    st.markdown("**🏦 Finanzierungsoptionen:**")
                    financing_opts = option.get('financing_options', [])

                    for fin_opt in financing_opts:
                        name = fin_opt.get('name', 'Standard')
                        months = fin_opt.get('duration_months', 60)
                        rate = fin_opt.get('interest_rate', 3.0)
                        fee = fin_opt.get('monthly_fee', 0.0)

                        # Vereinfachte Monatsrate berechnen
                        # (Annuitätendarlehen)
                        if rate > 0:
                            monthly_rate = rate / 100 / 12
                            factor = (monthly_rate * (1 + monthly_rate) **
                                      months) / ((1 + monthly_rate)**months - 1)
                            monthly_payment = final_price * factor + fee
                        else:
                            monthly_payment = final_price / months + fee

                        total_payment = monthly_payment * months
                        total_interest = total_payment - final_price

                        st.markdown(
                            f"- **{name}**: {monthly_payment:,.2f} €/Monat "
                            f"({months} Monate, {rate}% Zins)"
                        )
                        st.caption(
                            f"  Gesamtsumme: {
                                total_payment:,.2f} € (Zinsen: {
                                total_interest:,.2f} €)")

                elif payment_type == "leasing":
                    st.markdown("**📋 Leasing-Konditionen:**")
                    leasing_opts = option.get('leasing_options', [])

                    if leasing_opts:
                        leasing_opt = leasing_opts[0]
                        months = leasing_opt.get('duration_months', 120)
                        factor = leasing_opt.get(
                            'monthly_rate_factor', 1.2) / 100
                        monthly_rate = final_price * factor

                        st.markdown(
                            f"- Monatliche Leasingrate: {monthly_rate:,.2f} €")
                        st.markdown(
                            f"- Laufzeit: {months} Monate ({months / 12:.1f} Jahre)")

                        if leasing_opt.get('buyout_option', True):
                            buyout_price = final_price * \
                                leasing_opt.get('buyout_percentage', 10) / 100
                            st.markdown(
                                f"- Kaufoption am Ende: {buyout_price:,.2f} €")

                elif payment_type in ["immediate", "on_delivery"]:
                    if payment_type == "immediate":
                        st.markdown("**💰 Sofortige Vollzahlung**")
                        st.markdown("- Zahlung bei Vertragsabschluss")
                    else:
                        st.markdown("**🚚 Zahlung bei Lieferung**")
                        st.markdown(
                            "- Zahlung bei Anlieferung der Komponenten")

                    if total_discount > 0:
                        st.markdown("- Maximaler Rabatt durch Sofortzahlung")

            # Zusätzliche Informationen
            general_terms = payment_terms.get('general_terms', {})
            if general_terms:
                with st.expander("📋 Weitere Bedingungen", expanded=False):
                    col_terms1, col_terms2 = st.columns(2)

                    with col_terms1:
                        st.markdown(
                            f"- Produktgarantie: {general_terms.get('warranty_years', 25)} Jahre")
                        st.markdown(
                            f"- Montagegarantie: {general_terms.get('installation_warranty_years', 2)} Jahre")
                        st.markdown(
                            f"- Zahlungsziel: {general_terms.get('payment_due_days', 14)} Tage")

                    with col_terms2:
                        st.markdown(
                            f"- Angebotsgültigkeit: {general_terms.get('contract_validity_days', 30)} Tage")
                        st.markdown(
                            f"- Installationsdauer: ca. {
                                general_terms.get(
                                    'installation_period_weeks',
                                    8)} Wochen")
                        if general_terms.get('deposit_required', True):
                            st.markdown(
                                f"- Anzahlung: {general_terms.get('deposit_percentage', 30)}%")

        st.markdown("---")


def render_import_export_tools(widget_suffix: str) -> dict[str, Any] | None:
    """Tools für Import und Export von Zahlungskonfigurationen."""
    st.subheader("📁 Import/Export")
    st.markdown(
        "Exportieren Sie Ihre Konfiguration oder importieren Sie vorhandene Einstellungen.")

    col_ie1, col_ie2 = st.columns(2)

    with col_ie1:
        st.markdown("**📤 Export:**")
        if st.button(
            "💾 Konfiguration exportieren",
                key=f"export_config_{widget_suffix}"):
            # Hier würde die aktuelle Konfiguration exportiert werden
            config_json = json.dumps(
                get_comprehensive_default_payment_terms(),
                indent=2,
                ensure_ascii=False)

            # Download-Button anbieten
            st.download_button(
                label="📁 Konfiguration herunterladen",
                data=config_json,
                file_name=f"payment_terms_config_{
                    datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"download_config_{widget_suffix}")

    with col_ie2:
        st.markdown("**📥 Import:**")
        uploaded_file = st.file_uploader(
            "Konfigurationsdatei hochladen",
            type=["json"],
            key=f"import_config_{widget_suffix}",
            help="Laden Sie eine zuvor exportierte Konfigurationsdatei"
        )

        if uploaded_file is not None:
            try:
                config_data = json.loads(uploaded_file.getvalue().decode())
                st.success("✅ Konfiguration erfolgreich geladen!")

                if st.button(
                    "📥 Konfiguration übernehmen",
                        key=f"apply_import_{widget_suffix}"):
                    return config_data

                # Vorschau der importierten Konfiguration
                with st.expander("👁️ Vorschau der importierten Konfiguration"):
                    st.json(config_data)

            except json.JSONDecodeError:
                st.error("❌ Ungültige JSON-Datei!")
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der Datei: {str(e)}")

    return None


def render_admin_payment_terms_settings() -> None:
    """Legacy-Funktion für Rückwärtskompatibilität."""
    render_comprehensive_admin_payment_terms_ui()


def render_comprehensive_admin_payment_terms_ui(
    load_admin_setting_func: Callable | None = None,
    save_admin_setting_func: Callable | None = None,
    widget_key_suffix: str = "_comprehensive_payment_terms"
) -> None:
    """Umfassende Hauptfunktion für die Zahlungsmodalitäten-Verwaltung im Admin-Bereich."""

    # Header
    st.header("💳 Zahlungsmodalitäten - Umfassende Verwaltung")
    st.markdown("""
    Hier können Sie alle Aspekte der Zahlungsmodalitäten für Ihre Angebote konfigurieren:
    - Verschiedene Zahlungsoptionen (Bar, Raten, Finanzierung, Leasing)
    - Rabatt- und Bonusregelungen
    - Rechtliche Texte und Bedingungen
    - Berechnungs- und Darstellungseinstellungen
    """)

    # Fallback-Funktionen für Admin-Settings
    if load_admin_setting_func is None:
        def load_admin_setting_func(key, default=None):
            return st.session_state.get(f"admin_setting_{key}", default)

    if save_admin_setting_func is None:
        def save_admin_setting_func(key, value):
            st.session_state[f"admin_setting_{key}"] = value
            return True

    # Aktuelle Einstellungen laden
    current_payment_terms = load_admin_setting_func(
        'comprehensive_payment_terms',
        get_comprehensive_default_payment_terms())

    # Sicherstellen, dass die Struktur korrekt ist
    if not isinstance(current_payment_terms, dict):
        current_payment_terms = get_comprehensive_default_payment_terms()

    # Import-Funktion prüfen
    imported_config = render_import_export_tools(widget_key_suffix)
    if imported_config:
        current_payment_terms = imported_config
        st.success("✅ Importierte Konfiguration wurde geladen!")
        st.rerun()

    # Hauptnavigation
    main_tabs = st.tabs([
        "💳 Zahlungsoptionen",
        "⚖️ Geschäftsbedingungen",
        "🎯 Rabatte & Boni",
        "📋 Rechtliche Texte",
        "🧮 Berechnungen",
        "🎨 Darstellung",
        "👁️ Vorschau"
    ])

    # Tab 1: Zahlungsoptionen
    with main_tabs[0]:
        payment_options = current_payment_terms.get('payment_options', [])
        updated_payment_options = render_payment_options_management(
            payment_options, widget_key_suffix)
        current_payment_terms['payment_options'] = updated_payment_options

    # Tab 2: Allgemeine Geschäftsbedingungen
    with main_tabs[1]:
        general_terms = current_payment_terms.get('general_terms', {})
        updated_general_terms = render_general_terms_management(
            general_terms, widget_key_suffix)
        current_payment_terms['general_terms'] = updated_general_terms

    # Tab 3: Rabatte und Boni
    with main_tabs[2]:
        discount_rules = current_payment_terms.get('discount_rules', {})
        updated_discount_rules = render_discount_rules_management(
            discount_rules, widget_key_suffix)
        current_payment_terms['discount_rules'] = updated_discount_rules

    # Tab 4: Rechtliche Texte
    with main_tabs[3]:
        legal_texts = current_payment_terms.get('legal_texts', {})
        updated_legal_texts = render_legal_texts_management(
            legal_texts, widget_key_suffix)
        current_payment_terms['legal_texts'] = updated_legal_texts

    # Tab 5: Berechnungseinstellungen
    with main_tabs[4]:
        calc_settings = current_payment_terms.get('calculation_settings', {})
        updated_calc_settings = render_calculation_settings(
            calc_settings, widget_key_suffix)
        current_payment_terms['calculation_settings'] = updated_calc_settings

    # Tab 6: Darstellungseinstellungen
    with main_tabs[5]:
        display_settings = current_payment_terms.get('display_settings', {})
        updated_display_settings = render_display_settings(
            display_settings, widget_key_suffix)
        current_payment_terms['display_settings'] = updated_display_settings

    # Tab 7: Vorschau
    with main_tabs[6]:
        render_payment_preview_detailed(current_payment_terms)

    # Speicher- und Reset-Buttons
    st.markdown("---")
    col_save1, col_save2, col_save3, col_save4 = st.columns([2, 2, 2, 1])

    with col_save1:
        if st.button(
            "💾 Alle Einstellungen speichern",
            key=f"save_all_payment_terms{widget_key_suffix}",
                type="primary"):
            try:
                # Validierung vor dem Speichern
                validation_errors = validate_payment_terms_config(
                    current_payment_terms)

                if validation_errors:
                    st.error("❌ Validierungsfehler gefunden:")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    # Legacy-Format für Rückwärtskompatibilität auch speichern
                    legacy_config = convert_to_legacy_format(
                        current_payment_terms)

                    # Beide Formate speichern
                    success1 = save_admin_setting_func(
                        'comprehensive_payment_terms', current_payment_terms)
                    success2 = save_admin_setting_func(
                        'payment_terms', legacy_config) if PAYMENT_TERMS_AVAILABLE else True

                    if success1 and success2:
                        st.success(
                            "✅ Zahlungsmodalitäten erfolgreich gespeichert!")

                    else:
                        st.error(
                            "❌ Fehler beim Speichern der Zahlungsmodalitäten.")

            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {str(e)}")

    with col_save2:
        if st.button("🔄 Auf Standard zurücksetzen",
                     key=f"reset_payment_terms{widget_key_suffix}"):
            if st.session_state.get(
                    f"confirm_reset{widget_key_suffix}", False):
                default_config = get_comprehensive_default_payment_terms()
                if save_admin_setting_func(
                        'comprehensive_payment_terms', default_config):
                    st.success("✅ Auf Standardwerte zurückgesetzt!")
                    st.session_state[f"confirm_reset{widget_key_suffix}"] = False
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Zurücksetzen.")
            else:
                st.session_state[f"confirm_reset{widget_key_suffix}"] = True
                st.warning("⚠️ Klicken Sie erneut zum Bestätigen.")


def render_dynamic_payment_variants_ui(
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    widget_key_suffix: str = ""
):
    """
    Erweiterte UI für die Konfiguration der 4 spezifischen Zahlungsvarianten
    mit konfigurierbaren Prozentsätzen, optionalen festen Beträgen und Textbausteinen.
    """

    st.title("💳 Dynamische Zahlungsmodalitäten konfigurieren")
    st.markdown("---")
    st.markdown("""
    **Konfigurieren Sie bis zu 5 verschiedene Zahlungsvarianten mit:**
    - ✅ Konfigurierbaren Prozentsätzen und optionalen festen Beträgen
    - ✅ Anpassbaren Textbausteinen mit Platzhaltern ({p1}, {p2}, {p3}, {b1}, {b2}, {b3})
    - ✅ Automatischer Validierung (Summe muss 100% ergeben)
    - ✅ Vorschau mit Beispielbeträgen
    """)

    # Lade aktuelle Konfiguration und ergänze fehlende Varianten mit Defaults
    default_variants = get_default_payment_variants()
    current_variants = load_admin_setting_func(
        'dynamic_payment_variants', default_variants)
    if not isinstance(current_variants, dict):
        current_variants = default_variants
    else:
        for key, value in default_variants.items():
            current_variants.setdefault(key, value)

    # Globale Einstellungen
    st.subheader("🔧 Globale Einstellungen")
    col_global1, col_global2 = st.columns(2)

    with col_global1:
        example_total = st.number_input(
            "Beispiel-Gesamtbetrag für Vorschau (€):",
            min_value=1000.0,
            max_value=100000.0,
            value=15000.0,
            step=1000.0,
            key=f"example_total{widget_key_suffix}"
        )

    with col_global2:
        show_amounts_in_text = st.checkbox(
            "Beträge in Zahlungstext anzeigen",
            value=True,
            help="Wenn aktiviert, werden neben Prozenten auch die berechneten Beträge angezeigt",
            key=f"show_amounts{widget_key_suffix}")

    st.markdown("---")

    # Tab-Layout für die Varianten
    variant_tabs = st.tabs([
        "🚫 Variante 0 (Keine Vorkasse)",
        "🎯 Variante 1 (Anzahlung)",
        "💯 Variante 2 (100% Fertigstellung)",
        "📊 Variante 3 (2 Raten)",
        "⚙️ Variante 4 (Individuell)"
    ])

    variant_keys = [
        "variant_0",
        "variant_1",
        "variant_2",
        "variant_3",
        "variant_4"]
    updated_variants = current_variants.copy()

    for tab_idx, (tab, variant_key) in enumerate(
            zip(variant_tabs, variant_keys, strict=False)):
        with tab:
            variant_data = current_variants.get(
                variant_key, get_default_payment_variants()[variant_key])

            st.subheader(f"📝 {variant_data['name']}")
            st.caption(variant_data['description'])

            # Grundeinstellungen
            col_basic1, col_basic2 = st.columns([2, 1])

            with col_basic1:
                variant_name = st.text_input(
                    "Bezeichnung der Variante:",
                    value=variant_data.get('name', ''),
                    key=f"variant_{variant_key}_name{widget_key_suffix}"
                )

                variant_description = st.text_input(
                    "Beschreibung:",
                    value=variant_data.get('description', ''),
                    key=f"variant_{variant_key}_desc{widget_key_suffix}"
                )

            with col_basic2:
                variant_enabled = st.checkbox(
                    "Variante aktiviert",
                    value=variant_data.get('enabled', True),
                    key=f"variant_{variant_key}_enabled{widget_key_suffix}"
                )

            # Prozentsätze konfigurieren
            st.markdown("**💯 Prozentuale Aufteilung:**")

            is_static = variant_data.get('is_static', False)
            is_fully_customizable = variant_data.get(
                'is_fully_customizable', False)

            percents = variant_data.get('percents', [0.0, 0.0, 0.0])
            percent_labels = variant_data.get(
                'percent_labels', [
                    'Rate 1 (%)', 'Rate 2 (%)', 'Rate 3 (%)'])

            new_percents = []
            custom_labels = variant_data.get(
                'custom_labels', ['Rate 1', 'Rate 2', 'Rate 3'])
            new_custom_labels = []

            # Spezielle Behandlung für Variante 4 (vollständig anpassbar)
            if is_fully_customizable:
                st.info(
                    "💡 Diese Variante ist vollständig anpassbar - Sie können sowohl Bezeichnungen als auch Prozentsätze frei konfigurieren.")

                for i in range(3):
                    col_label, col_percent = st.columns([1, 1])

                    with col_label:
                        custom_label = st.text_input(
                            f"Bezeichnung Rate {
                                i + 1}:",
                            value=custom_labels[i] if i < len(custom_labels) else f"Rate {
                                i + 1}",
                            key=f"variant_{variant_key}_label_{i}{widget_key_suffix}")
                        new_custom_labels.append(custom_label)

                    with col_percent:
                        percent_val = st.number_input(
                            f"{custom_label} (%):",
                            min_value=0.0,
                            max_value=100.0,
                            value=percents[i] if i < len(percents) else 0.0,
                            step=0.1,
                            key=f"variant_{variant_key}_percent_{i}{widget_key_suffix}")
                        new_percents.append(percent_val)

            elif is_static:
                st.info(
                    "💡 Diese Variante hat feste Prozentsätze und kann nicht geändert werden.")
                new_percents = [percents[i] if i < len(
                    percents) else 0.0 for i in range(3)]
                static_cols = st.columns(3)
                for idx in range(3):
                    label = percent_labels[idx] if idx < len(
                        percent_labels) else f"Rate {idx + 1} (%)"
                    with static_cols[idx]:
                        st.metric(label, format_percent_de(new_percents[idx]))

            else:
                # Standard-Prozentsatz-Eingabe
                cols = st.columns(3)
                for i in range(3):
                    if percent_labels[i]:  # Nur wenn Label vorhanden
                        with cols[i]:
                            percent_val = st.number_input(
                                percent_labels[i],
                                min_value=0.0,
                                max_value=100.0,
                                value=percents[i] if i < len(percents) else 0.0,
                                step=0.1,
                                key=f"variant_{variant_key}_percent_{i}{widget_key_suffix}"
                            )
                            new_percents.append(percent_val)
                    else:
                        new_percents.append(0.0)

            # Validierung anzeigen
            variant_data_temp = variant_data.copy()
            variant_data_temp['percents'] = new_percents
            is_valid, validation_msg = validate_payment_variant_percentages(
                variant_data_temp)

            if is_valid:
                st.success(f"✅ {validation_msg}")
            else:
                st.error(f"❌ {validation_msg}")

            # Optionale feste Beträge
            with st.expander("💰 Feste Beträge (optional)", expanded=False):
                st.caption(
                    "Lassen Sie die Felder bei 0, um automatisch aus Prozentsätzen zu berechnen.")

                amounts = variant_data.get('amounts', [0.0, 0.0, 0.0])
                amount_labels = variant_data.get(
                    'amount_labels', [
                        'Betrag 1 (€)', 'Betrag 2 (€)', 'Betrag 3 (€)'])
                new_amounts = []

                cols_amounts = st.columns(3)
                for i in range(3):
                    if amount_labels[i]:  # Nur wenn Label vorhanden
                        with cols_amounts[i]:
                            amount_val = st.number_input(
                                amount_labels[i],
                                min_value=0.0,
                                max_value=100000.0,
                                value=amounts[i] if i < len(amounts) else 0.0,
                                step=50.0,
                                key=f"variant_{variant_key}_amount_{i}{widget_key_suffix}"
                            )
                            new_amounts.append(amount_val)
                    else:
                        new_amounts.append(0.0)

            # Textbaustein konfigurieren
            st.markdown("**📝 Textbaustein für PDF:**")
            st.caption(
                "Verfügbare Platzhalter: {p1}, {p2}, {p3} (Prozente), {b1}, {b2}, {b3} (Beträge)")
            if is_fully_customizable:
                st.caption(
                    "Zusätzlich: {label1}, {label2}, {label3} (Ihre benutzerdefinierten Bezeichnungen)")

            text_template = st.text_area(
                "Textvorlage:",
                value=variant_data.get(
                    'text_template',
                    ''),
                height=100,
                help="Verwenden Sie Platzhalter wie {p1} für Prozente und {b1} für Beträge",
                key=f"variant_{variant_key}_text{widget_key_suffix}")

            # Vorschau generieren
            st.markdown("**👁️ Vorschau:**")
            try:
                preview_text = format_payment_text_with_placeholders(
                    text_template,
                    new_percents,
                    new_amounts,
                    example_total,
                    new_custom_labels if is_fully_customizable else None
                )

                if show_amounts_in_text:
                    st.info(f"📄 **Vorschau-Text:** {preview_text}")
                else:
                    # Text ohne Beträge anzeigen
                    preview_no_amounts = format_payment_text_with_placeholders(
                        text_template.replace(
                            '({b1} €)',
                            '').replace(
                            '({b2} €)',
                            '').replace(
                            '({b3} €)',
                            ''),
                        new_percents,
                        [0.0, 0.0, 0.0],  # Keine Beträge
                        example_total,
                        new_custom_labels if is_fully_customizable else None
                    )
                    st.info(f"📄 **Vorschau-Text:** {preview_no_amounts}")

            except Exception as e:
                st.error(f"❌ Fehler in Textvorlage: {str(e)}")

            # Aktualisierte Variante speichern
            updated_variant = variant_data.copy()
            updated_variant.update({
                'name': variant_name,
                'description': variant_description,
                'enabled': variant_enabled,
                'percents': new_percents,
                'amounts': new_amounts,
                'text_template': text_template
            })

            if is_fully_customizable:
                updated_variant['custom_labels'] = new_custom_labels

            updated_variants[variant_key] = updated_variant

    # Speichern und Aktionen
    st.markdown("---")
    st.subheader("💾 Aktionen")

    col_save1, col_save2, col_save3 = st.columns(3)

    with col_save1:
        if st.button(
            "💾 Zahlungsvarianten speichern",
            key=f"save_variants{widget_key_suffix}",
                type="primary"):
            try:
                # Validierung aller Varianten
                all_valid = True
                validation_errors = []

                for variant_key, variant_data in updated_variants.items():
                    if variant_data.get('enabled', False):
                        is_valid, validation_msg = validate_payment_variant_percentages(
                            variant_data)
                        if not is_valid:
                            all_valid = False
                            validation_errors.append(
                                f"{variant_data['name']}: {validation_msg}")

                if not all_valid:
                    st.error("❌ Validierungsfehler gefunden:")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    if save_admin_setting_func(
                            'dynamic_payment_variants', updated_variants):
                        st.success(
                            "✅ Zahlungsvarianten erfolgreich gespeichert!")
                        st.balloons()
                    else:
                        st.error(
                            "❌ Fehler beim Speichern der Zahlungsvarianten.")

            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {str(e)}")

    with col_save2:
        if st.button(
            "🔄 Auf Standard zurücksetzen",
                key=f"reset_variants{widget_key_suffix}"):
            if st.session_state.get(
                    f"confirm_reset_variants{widget_key_suffix}", False):
                default_variants = get_default_payment_variants()
                if save_admin_setting_func(
                        'dynamic_payment_variants', default_variants):
                    st.success("✅ Auf Standardwerte zurückgesetzt!")
                    st.session_state[f"confirm_reset_variants{widget_key_suffix}"] = False
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Zurücksetzen.")
            else:
                st.session_state[f"confirm_reset_variants{widget_key_suffix}"] = True
                st.warning("⚠️ Klicken Sie erneut zum Bestätigen.")

    with col_save3:
        if st.button("📊 Alle Varianten testen",
                     key=f"test_variants{widget_key_suffix}"):
            st.markdown("### 🧪 Test aller Zahlungsvarianten")
            for variant_key, variant_data in updated_variants.items():
                if variant_data.get('enabled', False):
                    st.markdown(f"**{variant_data['name']}:**")
                    try:
                        test_text = format_payment_text_with_placeholders(
                            variant_data.get('text_template', ''),
                            variant_data.get('percents', []),
                            variant_data.get('amounts', []),
                            example_total,
                            variant_data.get('custom_labels')
                        )
                        st.success(f"✅ {test_text}")
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")
                else:
                    st.info(f"ℹ️ {variant_data['name']}: Deaktiviert")


# Hauptfunktion, die beide Systeme kombiniert
def render_comprehensive_admin_payment_terms_ui_with_variants(
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    widget_key_suffix: str = ""
):
    """
    Kombinierte UI für sowohl das umfassende Zahlungsmodalitäten-System
    als auch die neuen dynamischen Zahlungsvarianten.
    """

    st.title("💳 Erweiterte Zahlungsmodalitäten-Verwaltung")

    # Haupttabs
    main_tab1, main_tab2 = st.tabs([
        "💼 Umfassende Zahlungsoptionen",
        "🎯 Dynamische Zahlungsvarianten"
    ])

    with main_tab1:
        render_comprehensive_admin_payment_terms_ui(
            load_admin_setting_func,
            save_admin_setting_func,
            widget_key_suffix
        )

    with main_tab2:
        render_dynamic_payment_variants_ui(
            load_admin_setting_func,
            save_admin_setting_func,
            widget_key_suffix
        )


# ==========================================
# BENUTZER-AUSWAHL-KOMPONENTE FÜR PDF-ERSTELLUNG
# ==========================================

def render_payment_variant_selector_for_pdf(
    load_admin_setting_func: Callable[[str, Any], Any],
    widget_key_suffix: str = "",
    example_total: float = 15000.0
) -> dict[str, Any] | None:
    """
    Benutzer-Auswahl-Komponente für Zahlungsvarianten im PDF-Erstellungsbereich.

    Args:
        load_admin_setting_func: Funktion zum Laden der Admin-Einstellungen
        widget_key_suffix: Suffix für eindeutige Widget-Keys
        example_total: Beispielbetrag für die Vorschau

    Returns:
        Dict mit ausgewählter Zahlungsvariante oder None wenn keine ausgewählt
    """

    # Lade konfigurierte Zahlungsvarianten
    default_variants = get_default_payment_variants()
    configured_variants = load_admin_setting_func(
        'dynamic_payment_variants', default_variants)
    if not isinstance(configured_variants, dict):
        configured_variants = default_variants
    else:
        for key, value in default_variants.items():
            configured_variants.setdefault(key, value)

    # Nur aktivierte Varianten anzeigen
    active_variants = {
        key: variant for key, variant in configured_variants.items()
        if variant.get('enabled', True)
    }

    if not active_variants:
        st.warning(
            "⚠️ Keine Zahlungsvarianten konfiguriert. Bitte konfigurieren Sie zuerst die Zahlungsmodalitäten im Admin-Bereich.")
        return None

    st.markdown("### 💳 Zahlungsmodalitäten für PDF")
    st.caption("Wählen Sie die gewünschte Zahlungsvariante für dieses Angebot:")

    # Varianten als Liste für Selectbox vorbereiten
    variant_options = []
    variant_mapping = {}

    for key, variant in active_variants.items():
        display_name = f"{variant['name']} - {variant['description'][:50]}..."
        variant_options.append(display_name)
        variant_mapping[display_name] = (key, variant)

    # Auswahl-Widget
    col_select, col_preview = st.columns([2, 1])

    with col_select:
        selected_display = st.selectbox(
            "Zahlungsvariante auswählen:",
            options=variant_options,
            index=0,
            key=f"payment_variant_selector{widget_key_suffix}",
            help="Diese Zahlungsmodalität wird auf Seite 7 des PDFs angezeigt"
        )

        selected_key, selected_variant = variant_mapping[selected_display]

        # Zusätzliche Optionen
        show_detailed_breakdown = st.checkbox(
            "📊 Detaillierte Aufschlüsselung im PDF anzeigen",
            value=True,
            key=f"payment_detailed_breakdown{widget_key_suffix}",
            help="Zeigt eine tabellarische Aufschlüsselung der Zahlungsraten"
        )

        include_amounts_in_text = st.checkbox(
            "💰 Beträge im Zahlungstext anzeigen",
            value=True,
            key=f"payment_include_amounts{widget_key_suffix}",
            help="Fügt die berechneten Euro-Beträge neben den Prozentsätzen hinzu")

    with col_preview:
        st.markdown("**👁️ Vorschau:**")

        # Vorschau-Text generieren
        try:
            preview_text = format_payment_text_with_placeholders(
                selected_variant.get('text_template', ''),
                selected_variant.get('percents', []),
                selected_variant.get('amounts', []),
                example_total,
                selected_variant.get('custom_labels')
            )

            if not include_amounts_in_text:
                # Beträge aus Vorschau entfernen
                preview_text = format_payment_text_with_placeholders(
                    selected_variant.get('text_template', '')
                    .replace('({b1_with_sign})', '')
                    .replace('({b2_with_sign})', '')
                    .replace('({b3_with_sign})', '')
                    .replace('({b1} €)', '')
                    .replace('({b2} €)', '')
                    .replace('({b3} €)', ''),
                    selected_variant.get('percents', []),
                    [0.0, 0.0, 0.0],
                    example_total,
                    selected_variant.get('custom_labels')
                )

            st.info(f"📝 {preview_text}")

        except Exception as e:
            st.error(f"❌ Fehler in Vorschau: {str(e)}")

        # Prozentuale Aufschlüsselung anzeigen
        percents = selected_variant.get('percents', [])
        amounts = selected_variant.get('amounts', [])
        custom_labels = selected_variant.get(
            'custom_labels', ['Rate 1', 'Rate 2', 'Rate 3'])

        st.markdown("**📊 Aufschlüsselung:**")
        for i, percent in enumerate(percents):
            if percent > 0:
                if amounts and len(amounts) > i and amounts[i] > 0:
                    calculated_amount = float(amounts[i])
                else:
                    calculated_amount = (example_total * percent) / 100

                label = custom_labels[i] if i < len(
                    custom_labels) else f"Rate {i + 1}"
                st.metric(
                    label=label,
                    value=format_percent_de(percent),
                    delta=format_currency_de(calculated_amount)
                )

    # Rückgabe-Daten zusammenstellen
    return {
        'variant_key': selected_key,
        'variant_data': selected_variant,
        'display_name': selected_variant['name'],
        'show_detailed_breakdown': show_detailed_breakdown,
        'include_amounts_in_text': include_amounts_in_text,
        'preview_text': preview_text if 'preview_text' in locals() else '',
        'example_total': example_total
    }


def render_payment_variant_compact_selector(
    load_admin_setting_func: Callable[[str, Any], Any],
    widget_key_suffix: str = "",
    show_preview: bool = True,
    project_total: float | None = None
) -> str | None:
    """
    Kompakte Zahlungsvarianten-Auswahl für Integration in bestehende UI-Bereiche.

    Args:
        load_admin_setting_func: Funktion zum Laden der Admin-Einstellungen
        widget_key_suffix: Suffix für eindeutige Widget-Keys
        show_preview: Ob eine Vorschau angezeigt werden soll

    Returns:
        Key der ausgewählten Zahlungsvariante oder None
    """

    # Lade konfigurierte Zahlungsvarianten
    default_variants = get_default_payment_variants()
    configured_variants = load_admin_setting_func(
        'dynamic_payment_variants', default_variants)
    if not isinstance(configured_variants, dict):
        configured_variants = default_variants
    else:
        for key, value in default_variants.items():
            configured_variants.setdefault(key, value)

    # Nur aktivierte Varianten anzeigen
    active_variants = {
        key: variant for key, variant in configured_variants.items()
        if variant.get('enabled', True)
    }

    if not active_variants:
        st.info("ℹ️ Keine Zahlungsvarianten konfiguriert.")
        return None

    # Varianten als Liste für Selectbox vorbereiten
    variant_options: list[str] = []
    variant_mapping: dict[str, str | None] = {}

    # Ordnung nach Variantenschlüssel sicherstellen
    for key in sorted(active_variants.keys()):
        variant = active_variants[key]
        display_name = variant['name']
        variant_options.append(display_name)
        variant_mapping[display_name] = key

    if not variant_options:
        return None

    effective_total = project_total if isinstance(
        project_total, (int, float)) and project_total > 0 else 15000.0

    # Kompakte Auswahl
    selected_display = st.selectbox(
        "💳 Zahlungsmodalitäten:",
        options=variant_options,
        index=0,
        key=f"payment_variant_compact{widget_key_suffix}",
        help="Zahlungsmodalitäten für PDF (wird auf Seite 7 eingefügt)"
    )

    selected_key = variant_mapping[selected_display]
    selected_variant_raw = active_variants.get(
        selected_key) if selected_key else None

    if selected_variant_raw:
        st.session_state['selected_payment_variant_config'] = copy.deepcopy(
            selected_variant_raw)
    else:
        st.session_state.pop('selected_payment_variant_config', None)

    # Optionale Vorschau
    if show_preview and selected_key and selected_variant_raw:
        preview_variant = copy.deepcopy(selected_variant_raw)

        if selected_key == 'variant_4':
            custom_percent_values = st.session_state.get(
                'custom_variant_4_percents')
            if isinstance(custom_percent_values, (list, tuple)
                          ) and len(custom_percent_values) == 3:
                try:
                    preview_variant['percents'] = [
                        float(val) for val in custom_percent_values]
                except Exception:
                    pass

        with st.expander("👁️ Vorschau der Zahlungsmodalitäten", expanded=False):
            try:
                preview_text = format_payment_text_with_placeholders(
                    preview_variant.get('text_template', ''),
                    preview_variant.get('percents', []),
                    preview_variant.get('amounts', []),
                    effective_total,
                    preview_variant.get('custom_labels')
                )

                st.info(f"📝 **Beispiel-Text:** {preview_text}")

                # Kurze Übersicht der Raten
                percents = preview_variant.get('percents', [])
                if any(p > 0 for p in percents):
                    rate_info = []
                    custom_labels = preview_variant.get(
                        'custom_labels', ['Rate 1', 'Rate 2', 'Rate 3'])

                    for i, percent in enumerate(percents):
                        if percent > 0:
                            label = custom_labels[i] if i < len(
                                custom_labels) else f"Rate {i + 1}"
                            rate_info.append(
                                f"{label}: {
                                    format_percent_de(percent)}")

                    st.caption(f"💡 Aufteilung: {' | '.join(rate_info)}")

            except Exception as e:
                st.error(f"❌ Fehler in Vorschau: {str(e)}")

    return selected_key


def get_payment_variant_for_pdf_generation(
    selected_variant_key: str | None,
    load_admin_setting_func: Callable[[str, Any], Any],
    project_total: float,
    include_amounts: bool = True
) -> dict[str, Any] | None:
    """
    Bereitet die ausgewählte Zahlungsvariante für die PDF-Generierung vor.

    Args:
        selected_variant_key: Key der ausgewählten Zahlungsvariante
        load_admin_setting_func: Funktion zum Laden der Admin-Einstellungen
        project_total: Gesamtbetrag des Projekts
        include_amounts: Ob Beträge in den Text einbezogen werden sollen

    Returns:
        Dictionary mit formatierten Zahlungsdaten für PDF oder None
    """

    if not selected_variant_key:
        return None

    # Lade Zahlungsvarianten
    configured_variants = load_admin_setting_func(
        'dynamic_payment_variants', get_default_payment_variants())
    if not isinstance(configured_variants, dict):
        return None

    variant_data_raw = configured_variants.get(selected_variant_key)
    if not variant_data_raw or not variant_data_raw.get('enabled', True):
        return None

    variant_data = copy.deepcopy(variant_data_raw)
    custom_percentages_applied = False

    if selected_variant_key == 'variant_4':
        custom_percents = st.session_state.get('custom_variant_4_percents')
        if isinstance(custom_percents, (list, tuple)
                      ) and len(custom_percents) == 3:
            try:
                normalized_percents = [
                    float(max(0.0, min(100.0, value))) for value in custom_percents]
            except Exception:
                normalized_percents = None

            if normalized_percents:
                percent_sum = sum(normalized_percents)
                if abs(percent_sum - 100.0) > 0.01:
                    return {
                        'variant_name': variant_data.get(
                            'name',
                            'Individuell'),
                        'variant_description': variant_data.get(
                            'description',
                            ''),
                        'variant_key': selected_variant_key,
                        'validation_passed': False,
                        'error': f"Die Summe der individuellen Prozentwerte beträgt {
                            percent_sum:.2f}% und muss 100% ergeben."}
                variant_data['percents'] = normalized_percents
                custom_percentages_applied = True
        elif st.session_state.get('custom_variant_4_valid') is False:
            return {
                'variant_name': variant_data.get(
                    'name',
                    'Individuell'),
                'variant_description': variant_data.get(
                    'description',
                    ''),
                'variant_key': selected_variant_key,
                'validation_passed': False,
                'error': "Keine gültigen Prozentwerte für Variante 4 hinterlegt."}

    try:
        # Formatiere Text mit aktuellen Beträgen
        formatted_text = format_payment_text_with_placeholders(
            variant_data.get('text_template', ''),
            variant_data.get('percents', []),
            variant_data.get('amounts', []) if include_amounts else [0.0, 0.0, 0.0],
            project_total,
            variant_data.get('custom_labels')
        )

        # Berechne tatsächliche Beträge für jede Rate
        percents = variant_data.get('percents', [])
        amounts = variant_data.get('amounts', [])
        custom_labels = variant_data.get(
            'custom_labels', [
                'Rate 1', 'Rate 2', 'Rate 3'])

        safe_percents = [percents[i] if i < len(
            percents) else 0.0 for i in range(3)]
        amount_triplet: list[float] = []
        payment_breakdown = []

        for i, percent in enumerate(safe_percents):
            if amounts and len(amounts) > i and amounts[i] > 0:
                amount = float(amounts[i])
            else:
                amount = (project_total * percent) / 100
            amount = round(amount, 2)
            amount_triplet.append(amount)

            label = custom_labels[i] if i < len(
                custom_labels) else f"Rate {i + 1}"

            payment_breakdown.append({
                'label': label,
                'percentage': percent,
                'formatted_percentage': format_percent_de(percent),
                'amount': amount,
                'formatted_amount': format_currency_de(amount)
            })

        placeholder_values = {
            'anzahlung_percent': format_percent_de(safe_percents[0]),
            'anzahlung_percent_plain': _format_decimal_de(safe_percents[0], 2),
            'anzahlung_amount': format_currency_de(amount_triplet[0]),
            'anzahlung_amount_plain': _format_decimal_de(amount_triplet[0], 2),
            'nach_dc_percent': format_percent_de(safe_percents[1]),
            'nach_dc_percent_plain': _format_decimal_de(safe_percents[1], 2),
            'nach_dc_amount': format_currency_de(amount_triplet[1]),
            'nach_dc_amount_plain': _format_decimal_de(amount_triplet[1], 2),
            'nach_betrieb_percent': format_percent_de(safe_percents[2]),
            'nach_betrieb_percent_plain': _format_decimal_de(safe_percents[2], 2),
            'nach_betrieb_amount': format_currency_de(amount_triplet[2]),
            'nach_betrieb_amount_plain': _format_decimal_de(amount_triplet[2], 2),
        }

        return {
            'variant_name': variant_data['name'],
            'variant_description': variant_data['description'],
            'formatted_text': formatted_text,
            'payment_breakdown': payment_breakdown,
            'total_amount': project_total,
            'validation_passed': True,
            'percentages': safe_percents,
            'amounts': amount_triplet,
            'placeholder_values': placeholder_values,
            'variant_key': selected_variant_key,
            'custom_percentages_applied': custom_percentages_applied
        }

    except Exception as e:
        return {
            'variant_name': variant_data.get('name', 'Unbekannt'),
            'error': str(e),
            'validation_passed': False
        }


def validate_payment_terms_config(config: dict[str, Any]) -> list[str]:
    """Validiert die Zahlungsmodalitäten-Konfiguration."""
    errors = []

    # Zahlungsoptionen validieren
    payment_options = config.get('payment_options', [])
    if not payment_options:
        errors.append("Keine Zahlungsoptionen konfiguriert")

    active_options = [
        opt for opt in payment_options if opt.get(
            'enabled', True)]
    if not active_options:
        errors.append("Keine aktiven Zahlungsoptionen verfügbar")

    for i, option in enumerate(payment_options):
        option_id = option.get('id', f'option_{i}')

        if not option.get('name'):
            errors.append(f"Zahlungsoption {option_id}: Name fehlt")

        if option.get('payment_type') == 'installments':
            schedule = option.get('installment_schedule', [])
            if schedule:
                total_percentage = sum(inst.get('percentage', 0)
                                       for inst in schedule)
                if abs(total_percentage - 100.0) > 0.01:
                    errors.append(
                        f"Zahlungsoption {option_id}: Ratensumme ist {total_percentage}% (sollte 100% sein)")

    # Allgemeine Bedingungen validieren
    general_terms = config.get('general_terms', {})
    if general_terms.get('deposit_required', True):
        deposit_pct = general_terms.get('deposit_percentage', 0)
        if deposit_pct <= 0 or deposit_pct > 100:
            errors.append(
                "Anzahlungsprozentsatz muss zwischen 0 und 100% liegen")

    return errors


def convert_to_legacy_format(
        comprehensive_config: dict[str, Any]) -> dict[str, Any]:
    """Konvertiert das umfassende Format ins Legacy-Format für Rückwärtskompatibilität."""
    legacy_variants = []

    for option in comprehensive_config.get('payment_options', []):
        if not option.get('enabled', True):
            continue

        payment_type = option.get('payment_type', 'immediate')

        if payment_type == 'installments':
            schedule = option.get('installment_schedule', [])
            segments = []

            for i, installment in enumerate(schedule):
                segments.append({
                    "key": f"rate_{i + 1}",
                    "label": installment.get('label', f"Rate {i + 1}"),
                    "percent": installment.get('percentage', 0),
                    "amount": None
                })

            legacy_variants.append({
                "id": option.get('id', ''),
                "name": option.get('name', ''),
                "segments": segments,
                "text_template": f"Zahlung in {len(segments)} Raten"
            })

    return {"variants": legacy_variants}


# Hauptfunktion für Integration in Admin-Panel
def render_admin_payment_terms_ui(
    load_admin_setting_func: Callable,
    save_admin_setting_func: Callable,
    widget_key_suffix: str = "_payment_terms_admin"
) -> None:
    """Hauptfunktion für die Integration in das Admin-Panel."""
    render_comprehensive_admin_payment_terms_ui(
        load_admin_setting_func,
        save_admin_setting_func,
        widget_key_suffix
    )


if __name__ == "__main__":
    # Ermöglicht das eigenständige Starten dieses Moduls
    render_comprehensive_admin_payment_terms_ui()


# Export aller wichtigen Funktionen
__all__ = [
    'render_admin_payment_terms_ui',
    'render_comprehensive_admin_payment_terms_ui',
    'render_admin_payment_terms_settings',
    'get_comprehensive_default_payment_terms',
    'validate_payment_terms_config',
    'convert_to_legacy_format'
]
