"""
payment_terms.py
------------------

Erweiterte Zahlungsmodalitäten-Verwaltung für das Angebotssystem.
Dieses Modul wurde erheblich erweitert um umfassende Funktionalität
für verschiedene Zahlungsarten, Rabattsysteme und PDF-Integration.

Das Modul kapselt die Verwaltung der Zahlungsmodalitäten und stellt
Hilfsfunktionen zur Verfügung, um konfigurierbare Zahlungsvarianten
zu speichern, zu laden und auf Basis eines Gesamtbetrags einen
detaillierten Zahlungsplan zu berechnen.

Neue Features:
- Vollständige Zahlungsarten (Bar, Raten, Finanzierung, Leasing)
- Automatische Rabattberechnung (Mengen-, Saison-, Zahlungsrabatte)
- Umfassende PDF-Textgenerierung
- Validierung und Fehlerbehandlung
- Rückwärtskompatibilität zu bestehenden Systemen

Die Einstellungen werden in der bestehenden `admin_settings`-Tabelle
gespeichert. Standardwerte werden beim ersten Laden angelegt, falls
noch keine benutzerdefinierten Einstellungen vorhanden sind.

Varianten-Definition (Legacy-Format für Kompatibilität):
--------------------------------------------------------

Eine Variante besteht aus:

```
{
    "id": "variant1",
    "name": "Mit Anzahlung, nach DC‑Montage und Inbetriebnahme",
    "segments": [
        {
            "key": "deposit",
            "label": "Anzahlung",
            "percent": 30,
            "amount": null
        },
        {
            "key": "dc_montage",
            "label": "Nach DC‑Montage",
            "percent": 40,
            "amount": null
        },
        {
            "key": "commissioning",
            "label": "Nach Inbetriebnahme",
            "percent": 30,
            "amount": null
        }
    ],
    "text_template": "Die Zahlung erfolgt mit {deposit} Anzahlung, {dc_montage} nach DC‑Montage und {commissioning} nach Inbetriebnahme."
}
```

Neues umfassendes Format:
-------------------------

Das neue Format unterstützt erweiterte Zahlungsmodalitäten:

```
{
    "payment_options": [
        {
            "id": "cash_full",
            "name": "Vollzahlung",
            "payment_type": "immediate",
            "discount_percent": 3.0,
            "enabled": True
        },
        {
            "id": "installments_3",
            "name": "3 Raten",
            "payment_type": "installments",
            "installment_schedule": [...]
        },
        {
            "id": "financing",
            "name": "Finanzierung",
            "payment_type": "financing",
            "financing_options": [...]
        }
    ],
    "discount_rules": {...},
    "general_terms": {...}
}
```

`percent` und `amount` definieren den Anteil des Endbetrags. Sind
beide Werte definiert, hat der absolute Betrag Vorrang. Fehlt
`percent`, wird der Restbetrag zugewiesen. Bei der Berechnung des
Zahlungsplans wird darauf geachtet, dass die Summe aller Beträge dem
Gesamtbetrag entspricht (Rest wird dem letzten Segment zugeschlagen).

Hinweis: Die in `text_template` verwendeten Platzhalter müssen den
Schlüsseln aus den Segmenten entsprechen. Die Werte werden je nach
Vorhandensein als Prozentzahl mit `%` oder als fester Eurobetrag
formatiert.

"""

from __future__ import annotations

import json
from typing import Any

from database import load_admin_setting, save_admin_setting

# Schlüssel unter dem die Zahlungsvarianten in admin_settings gespeichert
# werden
PAYMENT_TERMS_KEY = "payment_terms_config"

# Neuer Schlüssel für erweiterte Zahlungsmodalitäten
COMPREHENSIVE_PAYMENT_KEY = "comprehensive_payment_config"


class PaymentTermsManager:
    """
    Erweiterte Zahlungsmodalitäten-Manager-Klasse.

    Diese Klasse verwaltet sowohl das Legacy-Varianten-System als auch
    das neue umfassende Zahlungssystem mit verschiedenen Zahlungsarten,
    Rabatten und Finanzierungsoptionen.
    """

    def __init__(self):
        self.legacy_config = None
        self.comprehensive_config = None
        self._load_configs()

    def _load_configs(self):
        """Lädt beide Konfigurationen (Legacy und Umfassend)."""
        self.legacy_config = get_payment_terms_config()
        self.comprehensive_config = self.get_comprehensive_payment_config()

    def get_comprehensive_payment_config(self) -> dict[str, Any]:
        """Lädt die umfassende Zahlungsmodalitätskonfiguration."""
        config = load_admin_setting(COMPREHENSIVE_PAYMENT_KEY, None)
        if not config:
            # Erstelle Standard-Konfiguration
            default_config = self._get_default_comprehensive_config()
            save_admin_setting(COMPREHENSIVE_PAYMENT_KEY, default_config)
            return default_config

        if isinstance(config, str):
            try:
                return json.loads(config)
            except BaseException:
                return self._get_default_comprehensive_config()
        return config

    def _get_default_comprehensive_config(self) -> dict[str, Any]:
        """Standardkonfiguration für umfassende Zahlungsmodalitäten."""
        return {
            "payment_options": [
                {
                    "id": "cash_full",
                    "name": "Sofortzahlung (Vollzahlung)",
                    "payment_type": "immediate",
                    "discount_percent": 3.0,
                    "enabled": True,
                    "description": "Komplette Zahlung bei Vertragsabschluss mit Skonto"
                },
                {
                    "id": "cash_delivery",
                    "name": "Zahlung bei Lieferung",
                    "payment_type": "immediate",
                    "discount_percent": 2.0,
                    "enabled": True,
                    "description": "Vollzahlung bei Lieferung der Anlage"
                },
                {
                    "id": "installments_3",
                    "name": "3 Raten",
                    "payment_type": "installments",
                    "installment_schedule": [
                        {"percentage": 30, "due_days": 0, "description": "Anzahlung"},
                        {"percentage": 40, "due_days": 30, "description": "Nach DC-Montage"},
                        {"percentage": 30, "due_days": 60, "description": "Nach Inbetriebnahme"}
                    ],
                    "enabled": True
                },
                {
                    "id": "installments_6",
                    "name": "6 Raten",
                    "payment_type": "installments",
                    "installment_schedule": [
                        {"percentage": 20, "due_days": 0, "description": "Anzahlung"},
                        {"percentage": 16, "due_days": 30, "description": "2. Rate"},
                        {"percentage": 16, "due_days": 60, "description": "3. Rate"},
                        {"percentage": 16, "due_days": 90, "description": "4. Rate"},
                        {"percentage": 16, "due_days": 120, "description": "5. Rate"},
                        {"percentage": 16, "due_days": 150, "description": "6. Rate"}
                    ],
                    "enabled": True
                },
                {
                    "id": "financing_bank",
                    "name": "Bankfinanzierung",
                    "payment_type": "financing",
                    "financing_options": [
                        {"duration_years": 5, "interest_rate": 3.5, "description": "5 Jahre Laufzeit"},
                        {"duration_years": 10, "interest_rate": 4.2, "description": "10 Jahre Laufzeit"},
                        {"duration_years": 15, "interest_rate": 4.8, "description": "15 Jahre Laufzeit"}
                    ],
                    "enabled": True
                },
                {
                    "id": "leasing",
                    "name": "Leasing",
                    "payment_type": "leasing",
                    "leasing_options": [
                        {"duration_years": 10, "monthly_rate_factor": 0.012, "description": "Gewerbeleasing 10 Jahre"},
                        {"duration_years": 15, "monthly_rate_factor": 0.009, "description": "Privatleasing 15 Jahre"}
                    ],
                    "enabled": True
                }
            ],
            "discount_rules": {
                "quantity_discounts": [
                    {"min_amount": 50000, "discount_percent": 2.0, "description": "Ab 50.000€ Auftragswert"},
                    {"min_amount": 100000, "discount_percent": 4.0, "description": "Ab 100.000€ Auftragswert"},
                    {"min_amount": 200000, "discount_percent": 6.0, "description": "Ab 200.000€ Auftragswert"}
                ],
                "seasonal_discounts": [
                    {"months": [11, 12, 1, 2], "discount_percent": 3.0, "description": "Winterrabatt"},
                    {"months": [6, 7, 8], "discount_percent": 1.5, "description": "Sommerrabatt"}
                ],
                "early_payment_discount": {
                    "enabled": True,
                    "days": 14,
                    "discount_percent": 2.0,
                    "description": "Bei Zahlung innerhalb von 14 Tagen"
                }
            },
            "general_terms": {
                "default_payment_days": 30,
                "late_payment_interest": 8.0,
                "currency": "EUR",
                "tax_rate": 19.0,
                "payment_methods": ["Überweisung", "SEPA-Lastschrift", "PayPal", "Kreditkarte"]
            },
            "legal_texts": {
                "general_terms": "Es gelten unsere Allgemeinen Geschäftsbedingungen. Alle Preise verstehen sich inklusive der gesetzlichen Mehrwertsteuer.",
                "payment_conditions": "Zahlung erfolgt gemäß den vereinbarten Zahlungsmodalitäten. Bei Verzug werden Verzugszinsen in Höhe von 8% p.a. berechnet.",
                "warranty_terms": "Wir gewähren gesetzliche Gewährleistung. Zusätzliche Garantiebedingungen nach Vereinbarung.",
                "installation_terms": "Die Installation erfolgt durch zertifizierte Fachkräfte nach geltenden Normen und Vorschriften."
            }
        }

    def calculate_payment_with_discounts(self,
                                         amount: float,
                                         payment_option_id: str,
                                         quantity_amount: float = None,
                                         month: int = None) -> dict[str,
                                                                    Any]:
        """
        Berechnet Zahlungsbetrag unter Berücksichtigung aller Rabatte.

        Args:
            amount: Grundbetrag
            payment_option_id: ID der gewählten Zahlungsoption
            quantity_amount: Auftragswert für Mengenrabatt
            month: Monat für Saisonrabatt (1-12)

        Returns:
            Dict mit Berechnungsdetails
        """
        config = self.comprehensive_config
        payment_option = self._get_payment_option(payment_option_id)

        if not payment_option:
            return {"error": "Unbekannte Zahlungsoption"}

        result = {
            "original_amount": amount,
            "payment_option": payment_option,
            "discounts_applied": [],
            "total_discount_percent": 0.0,
            "final_amount": amount
        }

        # Zahlungsrabatt
        if payment_option.get("discount_percent", 0) > 0:
            discount = payment_option["discount_percent"]
            result["discounts_applied"].append({
                "type": "payment_discount",
                "description": f"Zahlungsrabatt ({payment_option['name']})",
                "percent": discount
            })
            result["total_discount_percent"] += discount

        # Mengenrabatt
        if quantity_amount:
            quantity_discount = self._calculate_quantity_discount(
                quantity_amount)
            if quantity_discount > 0:
                result["discounts_applied"].append({
                    "type": "quantity_discount",
                    "description": f"Mengenrabatt ab {quantity_amount:.2f}€",
                    "percent": quantity_discount
                })
                result["total_discount_percent"] += quantity_discount

        # Saisonrabatt
        if month:
            seasonal_discount = self._calculate_seasonal_discount(month)
            if seasonal_discount > 0:
                result["discounts_applied"].append({
                    "type": "seasonal_discount",
                    "description": f"Saisonrabatt für Monat {month}",
                    "percent": seasonal_discount
                })
                result["total_discount_percent"] += seasonal_discount

        # Endpreis berechnen
        discount_factor = 1.0 - (result["total_discount_percent"] / 100.0)
        result["final_amount"] = round(amount * discount_factor, 2)
        result["total_discount_amount"] = round(
            amount - result["final_amount"], 2)

        return result

    def _get_payment_option(self, option_id: str) -> dict[str, Any] | None:
        """Ermittelt Zahlungsoption anhand der ID."""
        for option in self.comprehensive_config.get("payment_options", []):
            if option.get("id") == option_id:
                return option
        return None

    def _calculate_quantity_discount(self, amount: float) -> float:
        """Berechnet Mengenrabatt basierend auf Auftragswert."""
        discount_rules = self.comprehensive_config.get(
            "discount_rules", {}).get(
            "quantity_discounts", [])
        applicable_discount = 0.0

        for rule in sorted(
                discount_rules,
                key=lambda x: x.get(
                    "min_amount",
                    0),
                reverse=True):
            if amount >= rule.get("min_amount", 0):
                applicable_discount = rule.get("discount_percent", 0)
                break

        return applicable_discount

    def _calculate_seasonal_discount(self, month: int) -> float:
        """Berechnet Saisonrabatt basierend auf Monat."""
        discount_rules = self.comprehensive_config.get(
            "discount_rules", {}).get(
            "seasonal_discounts", [])

        for rule in discount_rules:
            if month in rule.get("months", []):
                return rule.get("discount_percent", 0)

        return 0.0

    def generate_payment_schedule_text(
            self,
            payment_option_id: str,
            amount: float) -> str:
        """Generiert Beschreibungstext für Zahlungsplan."""
        payment_option = self._get_payment_option(payment_option_id)
        if not payment_option:
            return "Unbekannte Zahlungsoption"

        payment_type = payment_option.get("payment_type", "")
        name = payment_option.get("name", "")

        if payment_type == "immediate":
            return f"Zahlung: {name} über {amount:.2f}€"

        if payment_type == "installments":
            schedule = payment_option.get("installment_schedule", [])
            parts = []
            for item in schedule:
                item_amount = round(amount * item["percentage"] / 100, 2)
                parts.append(f"{item_amount:.2f}€ {item['description']}")
            return f"Ratenzahlung ({name}): " + ", ".join(parts)

        if payment_type == "financing":
            options = payment_option.get("financing_options", [])
            if options:
                option = options[0]  # Erste Option als Standard
                years = option.get("duration_years", 0)
                rate = option.get("interest_rate", 0)
                return f"Finanzierung über {years} Jahre zu {rate}% Zinsen"

        elif payment_type == "leasing":
            options = payment_option.get("leasing_options", [])
            if options:
                option = options[0]  # Erste Option als Standard
                years = option.get("duration_years", 0)
                monthly = round(
                    amount *
                    option.get(
                        "monthly_rate_factor",
                        0),
                    2)
                return f"Leasing über {years} Jahre, ca. {monthly:.2f}€/Monat"

        return f"Zahlung gemäß {name}"

    def save_comprehensive_config(self, config: dict[str, Any]) -> bool:
        """Speichert die umfassende Zahlungskonfiguration."""
        success = save_admin_setting(COMPREHENSIVE_PAYMENT_KEY, config)
        if success:
            self.comprehensive_config = config
        return success


# Legacy-Funktionen für Rückwärtskompatibilität

# Standardkonfiguration, die beim ersten Laden verwendet wird.
# Administratoren können diese im UI anpassen und speichern.
DEFAULT_PAYMENT_TERMS_CONFIG: dict[str, Any] = {
    "variants": [
        {
            "id": "variant1",
            "name": "Anzahlung / DC‑Montage / Inbetriebnahme",
            "segments": [
                {"key": "deposit", "label": "Anzahlung", "percent": 30, "amount": None},
                {"key": "dc_montage", "label": "Nach DC‑Montage", "percent": 40, "amount": None},
                {"key": "commissioning", "label": "Nach Inbetriebnahme", "percent": 30, "amount": None},
            ],
            "text_template": (
                "Die Zahlung erfolgt in drei Schritten: {deposit} bei Vertragsabschluss, "
                "{dc_montage} nach der DC‑Montage und {commissioning} nach Inbetriebnahme."
            ),
        },
        {
            "id": "variant2",
            "name": "100 % nach Lieferung / Montage / Inbetriebnahme",
            "segments": [
                {"key": "full_payment", "label": "Nach Lieferung / Montage / Inbetriebnahme", "percent": 100, "amount": None},
            ],
            "text_template": (
                "Die Zahlung erfolgt in einer Rate: {full_payment} nach Lieferung, Montage und Inbetriebnahme."
            ),
        },
        {
            "id": "variant3",
            "name": "Nach DC‑Montage / Nach Inbetriebnahme",
            "segments": [
                {"key": "dc_delivery", "label": "Nach DC‑Montage und Lieferung", "percent": 50, "amount": None},
                {"key": "commissioning", "label": "Nach Inbetriebnahme", "percent": 50, "amount": None},
            ],
            "text_template": (
                "Die Zahlung erfolgt in zwei Schritten: {dc_delivery} nach DC‑Montage und Lieferung, "
                "{commissioning} nach Inbetriebnahme."
            ),
        },
        {
            "id": "variant4",
            "name": "Individuell (benutzerdefiniert)",
            "segments": [
                {"key": "custom1", "label": "Rate 1", "percent": 50, "amount": None},
                {"key": "custom2", "label": "Rate 2", "percent": 50, "amount": None},
            ],
            "text_template": (
                "Die Zahlung erfolgt in mehreren individuell definierten Raten: {custom1}, {custom2} usw."
            ),
        },
    ]
}


def get_payment_terms_config() -> dict[str, Any]:
    """Lädt die Zahlungsmodalitätskonfiguration aus der Datenbank.

    Falls noch keine Konfiguration vorhanden ist, wird die
    Standardkonfiguration gespeichert und zurückgegeben.

    Returns:
        Dict[str, Any]: Konfiguration mit Variantenliste.
    """
    config = load_admin_setting(PAYMENT_TERMS_KEY, None)
    if not config:
        # Noch nichts gespeichert – Standardwert persistieren
        save_admin_setting(PAYMENT_TERMS_KEY, DEFAULT_PAYMENT_TERMS_CONFIG)
        return json.loads(json.dumps(DEFAULT_PAYMENT_TERMS_CONFIG))
    # Gewährleistet, dass ein dict zurückgegeben wird
    if isinstance(config, str):
        try:
            config_dict = json.loads(config)
        except Exception:
            config_dict = DEFAULT_PAYMENT_TERMS_CONFIG
        return config_dict
    return config


def save_payment_terms_config(config: dict[str, Any]) -> bool:
    """Speichert die Zahlungsmodalitätskonfiguration.

    Args:
        config: Neue Konfiguration.

    Returns:
        bool: True bei Erfolg, False sonst.
    """
    return save_admin_setting(PAYMENT_TERMS_KEY, config)


def compute_payment_schedule(
        variant_id: str, total_amount: float) -> list[dict[str, Any]]:
    """Berechnet für eine Variante den Zahlungsplan.

    Es wird geprüft, ob feste Beträge hinterlegt sind. Diese werden
    direkt übernommen und vom Gesamtbetrag subtrahiert. Für
    Prozentangaben wird der entsprechende Anteil berechnet. Bleibt am
    Ende ein Restbetrag übrig (z.B. durch Rundung oder weil Summen
    kleiner als 100 % sind), wird dieser dem letzten Segment
    zugeschlagen.

    Args:
        variant_id: Die ID der gewählten Variante.
        total_amount: Gesamtbetrag (inkl. MwSt.), der verteilt werden soll.

    Returns:
        List[Dict[str, Any]]: Liste von Segmenten mit berechneten Beträgen.
    """
    config = get_payment_terms_config()
    variants: list[dict[str, Any]] = config.get("variants", [])
    variant = next((v for v in variants if v.get("id") == variant_id), None)
    if not variant:
        return []
    schedule: list[dict[str, Any]] = []
    remaining = float(total_amount)
    # Zuerst feste Beträge verarbeiten
    for seg in variant.get("segments", []):
        seg_key = seg.get("key")
        amount = seg.get("amount")
        percent = seg.get("percent")
        entry: dict[str, Any] = {
            "key": seg_key,
            "label": seg.get("label", seg_key),
            "percent": None,
            "amount": None,
        }
        if amount is not None:
            try:
                amount_val = float(amount)
            except Exception:
                amount_val = 0.0
            entry["amount"] = round(amount_val, 2)
            remaining -= amount_val
        elif percent is not None:
            # Prozentsatz wird später berechnet
            entry["percent"] = float(percent)
        schedule.append(entry)
    # Jetzt Prozentwerte berechnen (zweiter Durchlauf, um feste Beträge
    # abgezogen zu haben)
    for entry in schedule:
        if entry["percent"] is not None:
            portion = (entry["percent"] / 100.0) * total_amount
            portion = round(portion, 2)
            entry["amount"] = portion
            remaining -= portion
    # Falls nach Rundung ein Rest übrig ist, dem letzten Segment hinzufügen
    if schedule and abs(remaining) > 0.01:
        schedule[-1]["amount"] = round(schedule[-1]["amount"] + remaining,
                                       2) if schedule[-1]["amount"] else round(remaining, 2)
    # Prozent neu berechnen basierend auf den endgültigen Beträgen
    for entry in schedule:
        amount_val = entry.get("amount", 0.0)
        entry["percent"] = round(
            (amount_val / total_amount) * 100.0,
            2) if total_amount else 0.0
    return schedule


def get_payment_terms_text(
        variant_id: str, schedule: list[dict[str, Any]]) -> str:
    """Erzeugt einen erläuternden Text für die gewählte Zahlungsvariante.

    Die im Konfigurationsobjekt hinterlegte Vorlage (`text_template`) wird
    mit Werten aus dem berechneten Zahlungsplan gefüllt. Für jeden
    Platzhalter wird entweder der Prozentwert (mit `%`) oder – wenn
    vorhanden – der Eurobetrag (mit `€`) eingesetzt.

    Args:
        variant_id: Gewählte Varianten-ID.
        schedule: Berechnete Zahlungsplanliste.

    Returns:
        str: Formattierter Text. Falls keine Vorlage existiert, wird
        eine einfache Aufzählung der Teilbeträge zurückgegeben.
    """
    config = get_payment_terms_config()
    variants: list[dict[str, Any]] = config.get("variants", [])
    variant = next((v for v in variants if v.get("id") == variant_id), None)
    if not variant:
        return ""
    template = variant.get("text_template", "") or ""
    # Mapping aus schedule zusammensetzen
    fmt_map: dict[str, str] = {}
    for seg in schedule:
        key = seg.get("key")
        amount = seg.get("amount") or 0.0
        percent = seg.get("percent") or 0.0
        # Eurobetrag hat Vorrang vor Prozent, wenn explizit gesetzt
        original_seg = next(
            (s for s in variant.get(
                "segments",
                []) if s.get("key") == key),
            None)
        if original_seg and original_seg.get("amount") is not None:
            fmt_map[key] = f"{
                amount:,.2f} €".replace(
                ",", ".")  # deutsches Format
        else:
            fmt_map[key] = f"{percent:.0f} %"
    try:
        if template:
            return template.format(**fmt_map)
    except Exception:
        pass
    # Fallback: eigene Auflistung
    segments_text = []
    for seg in schedule:
        label = seg.get("label", seg.get("key"))
        amount = seg.get("amount", 0.0)
        segments_text.append(f"{label}: {amount:,.2f} €".replace(",", "."))
    return "; ".join(segments_text)


# Neue Convenience-Funktionen für die erweiterte Zahlungsmodalitäten-Verwaltung

def get_payment_manager() -> PaymentTermsManager:
    """Factory-Funktion für PaymentTermsManager-Instanz."""
    return PaymentTermsManager()


def calculate_comprehensive_payment(amount: float,
                                    payment_option_id: str,
                                    quantity_amount: float = None,
                                    month: int = None) -> dict[str,
                                                               Any]:
    """
    Wrapper-Funktion für umfassende Zahlungsberechnungen.

    Args:
        amount: Grundbetrag
        payment_option_id: ID der Zahlungsoption
        quantity_amount: Optional - Auftragswert für Mengenrabatt
        month: Optional - Monat für Saisonrabatt (1-12)

    Returns:
        Dict mit Berechnungsdetails und angewandten Rabatten
    """
    manager = get_payment_manager()
    return manager.calculate_payment_with_discounts(
        amount, payment_option_id, quantity_amount, month)


def get_comprehensive_payment_options() -> list[dict[str, Any]]:
    """Gibt alle verfügbaren umfassenden Zahlungsoptionen zurück."""
    manager = get_payment_manager()
    return manager.comprehensive_config.get("payment_options", [])


def get_payment_schedule_description(
        payment_option_id: str,
        amount: float) -> str:
    """Generiert Beschreibungstext für eine Zahlungsoption."""
    manager = get_payment_manager()
    return manager.generate_payment_schedule_text(payment_option_id, amount)


def update_comprehensive_payment_config(config: dict[str, Any]) -> bool:
    """Aktualisiert die umfassende Zahlungskonfiguration."""
    manager = get_payment_manager()
    return manager.save_comprehensive_config(config)


def get_discount_summary(amount: float,
                         quantity_amount: float = None,
                         month: int = None) -> dict[str,
                                                    Any]:
    """
    Gibt eine Übersicht über alle verfügbaren Rabatte für einen Betrag.

    Args:
        amount: Grundbetrag
        quantity_amount: Optional - Auftragswert für Mengenrabatt
        month: Optional - Monat für Saisonrabatt

    Returns:
        Dict mit Rabattinformationen
    """
    manager = get_payment_manager()

    # Alle Payment-Optionen durchgehen und beste Kombination finden
    best_option = None
    best_savings = 0.0

    for option in manager.comprehensive_config.get("payment_options", []):
        if not option.get("enabled", True):
            continue

        result = manager.calculate_payment_with_discounts(
            amount, option["id"], quantity_amount, month
        )

        if "error" not in result:
            savings = result.get("total_discount_amount", 0)
            if savings > best_savings:
                best_savings = savings
                best_option = result

    return {
        "original_amount": amount,
        "best_option": best_option,
        "maximum_savings": best_savings,
        "savings_percent": round(
            (best_savings / amount) * 100,
            2) if amount > 0 else 0}


# Migration und Kompatibilitätsfunktionen

def migrate_legacy_to_comprehensive():
    """
    Migriert bestehende Legacy-Konfiguration zu umfassendem System.
    Behält Legacy-System bei, erweitert es aber um neue Features.
    """
    legacy_config = get_payment_terms_config()
    manager = get_payment_manager()

    # Prüfe ob umfassende Konfiguration bereits existiert
    comprehensive_config = manager.comprehensive_config

    # Füge Legacy-Varianten als Ratenzahlungsoptionen hinzu falls nicht
    # vorhanden
    existing_ids = [
        opt.get(
            "id",
            "") for opt in comprehensive_config.get(
            "payment_options",
            [])]

    for variant in legacy_config.get("variants", []):
        variant_id = f"legacy_{variant.get('id', '')}"

        if variant_id not in existing_ids:
            # Konvertiere Legacy-Variante zu neuer Payment-Option
            new_option = {
                "id": variant_id,
                "name": f"Legacy: {variant.get('name', '')}",
                "payment_type": "installments",
                "enabled": True,
                "description": f"Migriert von Legacy-Variante {variant.get('id', '')}",
                "installment_schedule": []
            }

            # Konvertiere Segmente zu Installment-Schedule
            for segment in variant.get("segments", []):
                new_option["installment_schedule"].append({
                    "percentage": segment.get("percent", 0),
                    "due_days": 0,  # Standard - kann angepasst werden
                    "description": segment.get("label", segment.get("key", ""))
                })

            comprehensive_config["payment_options"].append(new_option)

    # Speichere aktualisierte Konfiguration
    return manager.save_comprehensive_config(comprehensive_config)


def ensure_comprehensive_config_exists():
    """Stellt sicher, dass umfassende Konfiguration existiert."""
    manager = get_payment_manager()
    if not manager.comprehensive_config.get("payment_options"):
        # Initialisiere mit Standard-Konfiguration
        default_config = manager._get_default_comprehensive_config()
        return manager.save_comprehensive_config(default_config)
    return True
