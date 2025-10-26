"""
placeholders.py
Definiert die Zuordnung zwischen Beispieltexten in den coords/seiteX.yml-Dateien
und logischen Platzhalter-Schlüsseln sowie eine Hilfsfunktion, um aus den
App-Daten (project_data, analysis_results, company_info) die dynamischen Werte
für die PDF-Overlays zu erzeugen.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

try:
    from ..calculations import perform_calculations
except Exception:
    # Fall B: Skript wird direkt ausgeführt -> Parent-Verzeichnis in sys.path
    # schieben
    import os
    import sys
    _THIS_DIR = os.path.dirname(__file__)
    _PARENT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
    if _PARENT not in sys.path:
        sys.path.insert(0, _PARENT)
    from calculations import perform_calculations  # noqa: E402


def USE_PERFORM_CALCULATIONS(context: dict[str, Any]) -> dict[str, Any]:
    """
    DEF Block:
    Nutzt calculations.perform_calculations(context) und liefert die berechneten Werte
    zurück. Side-effect-frei; passt sich an bestehende Struktur an.
    """
    return perform_calculations(context)
# --- /import shim ---
# === Neuer Einspeisetarif-Block (integriert aus feed_in_tariffs.py) ===
# Original-Funktion oben wurde ersetzt; alter Code entfernt und durch
# robustere Variante ersetzt.


# 0) Fallback-Daten
_DEFAULT_FEED_IN_TARIFFS_FALLBACK = {
    "parts": [
        {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 7.86},
        {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 6.80},
        {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 5.56},
    ],
    "full": [
        {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.47},
        {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 10.45},
        {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 10.45},
    ],
}

# Spezifische Jahreserträge nach Ausrichtung und Neigung (aus admin_panel.py)
_DEFAULT_SPECIFIC_YIELDS_BY_ORIENTATION_TILT = {
    "Süd_0": 1050.0,
    "Süd_15": 1080.0,
    "Süd_30": 1100.0,
    "Süd_45": 1080.0,
    "Süd_60": 1050.0,
    "Südost_0": 980.0,
    "Südost_15": 1030.0,
    "Südost_30": 1070.0,
    "Südost_45": 1030.0,
    "Südost_60": 980.0,
    "Südwest_0": 980.0,
    "Südwest_15": 1030.0,
    "Südwest_30": 1070.0,
    "Südwest_45": 1030.0,
    "Südwest_60": 980.0,
    "Ost_0": 950.0,
    "Ost_15": 980.0,
    "Ost_30": 1000.0,
    "Ost_45": 980.0,
    "Ost_60": 950.0,
    "West_0": 950.0,
    "West_15": 980.0,
    "West_30": 1000.0,
    "West_45": 980.0,
    "West_60": 950.0,
    "Nord_0": 800.0,
    "Nord_15": 820.0,
    "Nord_30": 850.0,
    "Nord_45": 820.0,
    "Nord_60": 850.0,
    "Nordost_0": 850.0,
    "Nordost_15": 870.0,
    "Nordost_30": 890.0,
    "Nordost_45": 870.0,
    "Nordost_60": 850.0,
    "Nordwest_0": 850.0,
    "Nordwest_15": 870.0,
    "Nordwest_30": 890.0,
    "Nordwest_45": 870.0,
    "Nordwest_60": 850.0,
    "Flachdach_0": 950.0,
    "Flachdach_15": 1000.0,
    "Sonstige_0": 1000.0,
    "Sonstige_15": 1050.0,
    "Sonstige_30": 1080.0,
    "Sonstige_45": 1050.0,
    "Sonstige_60": 1000.0}

DEFAULT_FEED_IN_TARIFFS_FALLBACK = _DEFAULT_FEED_IN_TARIFFS_FALLBACK
DEFAULT_SPECIFIC_YIELDS_BY_ORIENTATION_TILT = _DEFAULT_SPECIFIC_YIELDS_BY_ORIENTATION_TILT


def _fit_to_float(x: Any) -> float:
    try:
        return float(str(x).replace(',', '.'))
    except Exception:
        return 0.0


def _normalize_tariff_to_eur_per_kwh(val: Any) -> float | None:
    if val in (None, ""):
        return None
    v = _fit_to_float(val)
    if v == 0.0:
        return 0.0
    return v / 100.0 if v > 1.0 else v


@lru_cache(maxsize=128)
def resolve_feed_in_tariff_eur_per_kwh(
    anlage_kwp: float,
    mode: str,
    load_admin_setting_func,
    analysis_results_snapshot: tuple | None = None,
    project_data_snapshot: tuple | None = None,
    default_parts_under_10_eur_per_kwh: float = 0.0786,
) -> float:
    """Neue robuste Einspeisetarif-Ermittlung (€/kWh). Nutzt Admin-Settings, sonst analysis_results, sonst Default."""
    try:
        mode_l = (mode or "parts").strip().lower()
        if mode_l not in ("parts", "full"):
            mode_l = "parts"
        tariffs_data = {}
        try:
            tariffs_data = load_admin_setting_func("feed_in_tariffs", {}) or {}
        except Exception:
            tariffs_data = {}
        tariffs_list = tariffs_data.get(
            mode_l, []) if isinstance(tariffs_data, dict) else []
        chosen = None
        for trf in tariffs_list or []:
            try:
                if _fit_to_float(
                    trf.get(
                        "kwp_min",
                        0)) <= anlage_kwp <= _fit_to_float(
                    trf.get(
                        "kwp_max",
                        999)):
                    chosen = _normalize_tariff_to_eur_per_kwh(
                        trf.get("ct_per_kwh"))
                    break
            except Exception:
                continue
        if chosen is None and analysis_results_snapshot:
            # Snapshot tuple: (einspeiseverguetung_eur_per_kwh, ... ) – wir
            # übergeben hier nur einen Wert bei Bedarf
            try:
                ar_val = analysis_results_snapshot[0]
                norm = _normalize_tariff_to_eur_per_kwh(ar_val)
                if norm is not None and norm > 0:
                    chosen = norm
            except Exception:
                pass
        if chosen is None or chosen <= 0:
            chosen = default_parts_under_10_eur_per_kwh
        return float(chosen)
    except Exception:
        return default_parts_under_10_eur_per_kwh

# (Alter Funktionsname für rückwärtskompatible Aufrufe innerhalb dieses Moduls)


def get_feed_in_tariff_eur_per_kwh(anlage_kwp: float, mode: str, load_admin_setting_func) -> float:  # noqa: D401
    return resolve_feed_in_tariff_eur_per_kwh(
        anlage_kwp, mode, load_admin_setting_func)


# Abbildung von Beispieltexten (so wie sie in den YML-Dateien stehen) auf
# logische Platzhalter-Keys. Diese Keys werden später mit echten Werten
# befüllt.
PLACEHOLDER_MAPPING: dict[str, str] = {
    # Kundendaten (Beispiele aus seite1.yml)
    # Platzhalter für Namen (wird aus Anrede/Titel/Vor-/Nachname gebaut)
    "qwe qe": "customer_name",
    "22359 Hamburg": "customer_city_zip",
    "Tel: 0155555555": "customer_phone",
    "oemertimur@gmail.com": "customer_email",

    # KPIs / Kennzahlen (Beispiele) – an echte Keys der App angepasst
    "36.958,00 EUR*": "anlage_kwp",
    "29.150,00 EUR*": "amortization_time",
    # Beispielwerte aus der Vorlage
    "8,4 kWp": "anlage_kwp",
    # Rechts neben "Batterie": statischer Text (ersetzt die Beispielzahl 6,1
    # kWh)
    "6,1 kWh": "storage_capacity_kwh",
    "8.251,92 kWh/Jahr": "annual_pv_production_kwh",
    "54%": "self_supply_rate_percent",
    "42%": "self_consumption_percent",
}

# Ergänzungen: Exakte YAML-Beispiele und Firmendaten-Mapping
PLACEHOLDER_MAPPING.update({
    # Exakte Adresse aus coords/seite1.yml (Schreibweise exakt wie in YML)
    "Auf den Wöörden 23": "customer_street",

    # Firmendaten (rechte Seite)
    "TommaTech GmbH": "company_name",
    "Zeppelinstraße 14": "company_street",
    "85748 Garching b. München": "company_city_zip",
    "Tel: +49 89 1250 36 860": "company_phone",
    "mail@tommatech.de": "company_email",
})

# Seite 1: spezielle Ersetzungen der linken Label durch dynamische Werte
PLACEHOLDER_MAPPING.update({
    # "Heizung" soll zur reinen Modulanzahl werden (
    "Heizung": "pv_modules_count_with_unit",
    # "Warmwasser" soll die Wechselrichter-Gesamtleistung (W mit Tausendertrennzeichen) anzeigen
    "Warmwasser": "inverter_total_power_w",
    # "Verbrauch" soll die Speicherkapazität (kWh) anzeigen
    "Verbrauch": "storage_capacity_kwh",
    # Neue Anforderungen Seite 1:
    # Wert neben „Dachneigung“ (Beispiel „30°“) zeigt jetzt die jährliche Einspeisevergütung in Euro
    "Dachneigung": "annual_feed_in_revenue_eur",
    # "Solaranlage" zeigt jetzt den MwSt.-Betrag (19% vom Netto-Endbetrag)
    "Solaranlage": "vat_amount_eur",
    # "Batterie" und "Jahresertrag" werden als statischer Text "inklusive" angezeigt
    "Batterie": "static_inklusive",
    "Jahresertrag": "static_inklusive",
    # Rechte Spalte Texte an den geänderten Positionen
    "DC Dachmontage": "static_dc_dachmontage",
    # Unterstütze beide Schreibweisen im Template für den rechten Wert neben "Jahresertrag"
    "AC Installation und Inbetriebnahme": "static_ac_installation",
    "AC Installation | Inbetriebnahme": "static_ac_installation",
})

# Footer: dynamische Firma/Datum (ersetzt feste Dummy-Werte in allen
# seiteX.yml)
PLACEHOLDER_MAPPING.update({
    "tom-90": "footer_company",
    "29.11.2024": "footer_date",
})

# Seite 2: Energieflüsse und Quoten
PLACEHOLDER_MAPPING.update({
    "8.251 kWh": "pv_prod_kwh_short",
    "1.945 kWh": "direct_self_consumption_kwh",
    "1.562 kWh": "battery_charge_kwh",
    "1.313 kWh": "battery_discharge_for_sc_kwh",
    # Variante im Template vorkommend
    "1.321 kWh": "battery_discharge_for_sc_kwh",
    "4.745 kWh": "grid_feed_in_kwh",
    "2.742 kWh": "grid_bezug_kwh",
    "6.000 kWh": "annual_consumption_kwh",
    # Kreisdiagramm-Beschriftungen (Produktion)
    "19%": "battery_use_quote_prod_percent",
    "58%": "direct_consumption_quote_prod_percent",
    # Zahlen-only Token neben separatem "%" auf dem Template
    "24": "feed_in_quote_prod_percent_number",
    # Kreisdiagramm-Beschriftungen (Verbrauch)
    "22%": "battery_cover_consumption_percent",
    "46%": "grid_consumption_rate_percent",
    "32": "direct_cover_consumption_percent_number",
})

# Seite 2: Hinweistext für Batterie-Heuristik (Token anpassbar in
# coords/seite2.yml)
PLACEHOLDER_MAPPING.update({
    "Hinweis Batteriespeicher": "battery_note_text",
})

# Seite 2: KWh-Anteile für "Woher kommt mein Strom?" (optional – Token in
# coords/seite2.yml platzieren)
PLACEHOLDER_MAPPING.update({
    "Direkter Verbrauch (kWh)": "consumption_direct_kwh",
    "Batteriespeicher (kWh)": "consumption_battery_kwh",
    "Netzbezug (kWh)": "consumption_grid_kwh",
})

# Seite 3: Wirtschaftlichkeit
PLACEHOLDER_MAPPING.update({
    # Ertrag über 20 Jahre (Zahl ohne Einheit, da "EUR" separat gelayoutet ist)
    # In der Vorlage stehen hier zwei Zahlen (links/rechts). Wir verwenden sie jetzt für
    # die Stromkosten-Projektion über 10 Jahre: links OHNE Erhöhung, rechts MIT Erhöhung.
    # Alte Template-Zahlen (Kompatibilität älterer seite3.yml Versionen)
    # (entfernt) "36.958": "cost_10y_with_increase_number",
    # (entfernt) "29.150": "cost_10y_no_increase_number",
    # Neue Template-Zahlen (aktuelles Layout) – Werte werden dynamisch ersetzt
    # ohne jährliche Stromtariferhöhung (reaktiviert)
    "46.296,00 €": "cost_10y_no_increase_number",
    # mit jährlicher Stromtariferhöhung (reaktiviert)
    "58.230,61 €": "cost_10y_with_increase_number",
    # 20-Jahres Simulation (rechter Chart) – Template-Werte
    # (entfernt) "92.592,00 €": "cost_20y_no_increase_number",
    # (entfernt) "153.082,14 €": "cost_20y_with_increase_number",
    # Einzel-Einsparungen Seite 3 (nur diese 4 dynamisch laut Vorgabe)

    # RENDITE: Prozentwerte werden durch dynamische Euro-Beträge ersetzt
    # Batteriespeicher-Werte: 123% und 321% durch dynamische Euro-Beträge ersetzen
    # Aktuelles Template (keine Prozentwerte mehr, sondern Text-Spaltenüberschriften rechts) –
    # wir mappen die blauen Kurz-Begriffe auf die dynamischen Geldwerte:
    "Direkt": "self_consumption_without_battery_eur",
    "Einspeisung": "annual_feed_in_revenue_eur",
    "platz1": "tax_benefits_eur",  # Steuerliche Vorteile
    "Gesamt": "total_annual_savings_eur",
    # KWh-Werte für Batterieberechnungen auf Seite 3
    "Speicherladung (kWh)": "calc_battery_charge_kwh_page3",
    "Speichernutzung (kWh)": "calc_battery_discharge_kwh_page3",
    "Verbrauch 32 Cent": "basis_tariff_text",
    # Seite 3: Berechnungsgrundlagen - Dynamische Werte für statische Beispieltexte
    "NOSW": "orientation_text",                   # Ausrichtung aus calculations.py
    "Deckung": "roof_covering_type",              # Dachdeckung aus data_input.py
    "Kredit": "financing_needed_text",            # Finanzierung Ja/Nein
    "Neigung": "roof_inclination_text",           # Dachneigung aus data_input.py
    "Art": "roof_type",                           # Dachart aus data_input.py
    "EEG": "feed_in_tariff_text",                 # EEG-Vergütung formatiert

    # Neue Platzhalter für die 4 Berechnungen im "Mit Batteriespeichersystem" Bereich
    # Diese werden unter der Hauptüberschrift angezeigt

    # Produktionskosten (ct/kWh) – basierend auf LCOE
    # Gesamtwert-Zeile (fehlte zuvor im Mapping)
    # Label "Einsparungen pro Jahr (gesamt)" soll statisch bleiben (kein Ersatz durch Zahl)
    # Gesamtbetrag stattdessen auf Satz "Kapitalkosten sowie Investition und Unterhalt." legen
    "Kapitalkosten sowie Investition und Unterhalt.": "annual_total_savings_year1_label",
})

# Seite 3: RENDITE – Erklärblock ersetzen durch dynamische Zeilen
PLACEHOLDER_MAPPING.update({
    " Der interne Zinsfuß entspricht der mittleren, jährlichen": "total_annual_savings_eur",
    "Rendite Ihres Kapitals über die gesamte Laufzeit.": "rendite_line_2",
    # Zusätzliche Platzhalter für die Beschriftungen/Labels

    "tom-90": "footer_company",
    "29.11.2024": "footer_date",
    # Seitenzahl dynamisch formatieren (Seite X von Y)
    "3": "page_number_with_total",
})

# Seite 3: Y-Achsen-Beschriftung des linken Diagramms (dynamisch skalieren)
# Ältere Vorlage: 25.000 ... 0 ; Aktuelle Vorlage: 100.000 ... 0
PLACEHOLDER_MAPPING.update({
    # Altwerte
    "25.000": "axis_tick_1_top",
    "20.000": "axis_tick_2",
    "15.000": "axis_tick_3",
    "10.000": "axis_tick_4",
    "5.000": "axis_tick_5",
    "0": "axis_tick_6_bottom",
    # Neue Werte (aktuelles Template seite3.yml)
    "100.000": "axis_tick_1_top",
    "80.000": "axis_tick_2",
    "60.000": "axis_tick_3",
    "40.000": "axis_tick_4",
    "20.000": "axis_tick_5",
})

# Seite 3: Rechter 20-Jahres-Chart – Achsenticks (werden aktuell maskiert,
# aber Mapping für Vollständigkeit)
PLACEHOLDER_MAPPING.update({
    "154.000,00": "axis20_tick_1_top",
    "123.200,00": "axis20_tick_2",
    "92.400,00": "axis20_tick_3",
    "61.600,00": "axis20_tick_4",
    "30.800,00": "axis20_tick_5",
    "0,00": "axis20_tick_6_bottom",
})

# Seite 4: Komponenten (Module / WR / Speicher)
# WICHTIG: Die folgenden Beispieltexte müssen 1:1 mit den Textfeldern in coords/seite4.yml übereinstimmen
# (ohne führende Leerzeichen). Diese sind absichtlich eindeutig, damit Module/WR/Speicher getrennt befüllt werden können.
PLACEHOLDER_MAPPING.update({
    # Modul
    "Modul-Hersteller": "module_manufacturer",
    "Modul-Modell": "module_model",
    "Modul-Leistung": "module_power_wp",
    "Modul-Garantie": "module_warranty_years",
    "Modul-Leistungsgarantie": "module_performance_warranty",
    # Wechselrichter
    "WR-Hersteller": "inverter_manufacturer",
    "WR-Wirkungsgrad": "inverter_max_efficiency_percent",
    "WR-Garantie": "inverter_warranty_years",
    # Wert neben der Überschrift WECHSELRICHTER (kW-Gesamtleistung)
    "WR-Leistung (Titel)": "inverter_total_power_kw",
    # Erweiterte Wechselrichter-Felder (Wert-Zeilen; Labels bleiben statisch
    # im YAML)
    "WR-Modell | Typ": "inverter_model",
    "WR-Leistung": "inverter_power_watt",
    "WR-Typ": "inverter_type",
    "WR-Phasen": "inverter_phases",
    "WR-Schattenmanagement": "inverter_shading_management",
    "WR-Notstrom": "inverter_backup_capable",
    "WR-Smart-Home": "inverter_smart_home_integration",
    "WR-Garantie-Text": "inverter_guarantee_text",
    # Speicher
    "Speicher-Hersteller": "storage_manufacturer",
    "Speicher-Modell | Typ": "storage_model",
    # Alte Felder bleiben gemappt, falls Templates sie noch nutzen
    "Speicher-Kapazität": "storage_capacity_kwh",
    "Speicher-Leistung": "storage_power_kw",
    "Speicher-Entladetiefe": "storage_dod_percent",
    "Speicher-Zyklen": "storage_cycles",
    # Neue, gewünschte Felder
    "Speicherzellentechnologie": "storage_cell_technology",
    "Größe des Batteriespeichers": "storage_size_battery_kwh_star",
    "Erweiterungsmodul Größe": "storage_extension_module_size_kwh",
    "Speichergröße maximum": "storage_max_size_kwh",
    "Reserve bzw. Notstrom": "storage_backup_text",
    "Outdoorfähig": "storage_outdoor_capability",
    "Speicher-Garantie-Text": "storage_warranty_text",
    # Wert neben der Überschrift BATTERIESPEICHER (ausgewählte Kapazität)
    "Speicherkapazität (Titel)": "storage_capacity_kwh",
})

# Seite 4: Überschrift Module mit Stückzahl und erweiterte Modul-Felder
PLACEHOLDER_MAPPING.update({
    # Überschriften (wir unterstützen beide Varianten im Template)
    "SOLARMODULE": "module_section_title",
    "PHOTOVOLTAIK MODULE": "module_section_title",
    "WECHSELRICHTER": "inverter_section_title",
    "BATTERIESPEICHER": "storage_section_title",
    # Neue/angepasste Werte-Felder rechte Spalte (Labels sind statisch in YAML)
    "Leistung pro PV-Modul": "module_power_per_panel_watt",
    # Fehlende direkte Mappings aus seite4.yml (Wertfelder):
    # In der YAML steht für Hersteller / Modell aktuell "Modul-Hersteller" und "Modul-Modell" als Platzhaltertexte
    # Diese waren bisher NICHT gemappt und erschienen deshalb statisch.
    "Modul-Hersteller": "module_manufacturer",
    "Modul-Modell": "module_model",
    "PV-Zellentechnologie1": "module_cell_technology",
    "Modulaufbau1": "module_structure",
    "Solarzellen1": "module_cell_type",
    "Version1": "module_version",
    "Modul-Garantie1": "module_guarantee_combined",
    # In der Vorlage steht neben "Garantie:" beim Modul oft der Text "siehe Produktdatenblatt" –
    # mappe diesen explizit auf den kombinierten Garantietext, damit echte Werte aus der DB erscheinen.
    "siehe Produktdatenblatt": "module_guarantee_combined",
    # Variante mit Zusatz "anbei" aus coords/seite4.yml
    "siehe Produktdatenblatt anbei": "module_guarantee_combined",

})

# Seite 5 – Nachhaltigkeit / CO2 Kennzahlen (Template Beispielwerte ersetzen)
# ACHTUNG: Kurze numerische Tokens wie "244" können theoretisch woanders vorkommen;
# falls Kollisionen auftreten, bitte spezifischere Platzhalter im YAML
# definieren.
PLACEHOLDER_MAPPING.update({
    "3.053,21 kg...": "sustainability_annual_co2_savings_kg_ellipsis",
    "15.266,22 Kilometer": "sustainability_car_km_equivalent_long",
    "15.266,22 km": "sustainability_car_km_equivalent_short",
    "38,00 %": "sustainability_co2_reduction_percent",
    "38,01 % .": "sustainability_co2_reduction_percent",
    "244 Bäume": "sustainability_tree_equivalent_with_label",
    "244": "sustainability_tree_equivalent_number",
    # zweite Variante (geändertes Template)
    "38,01 % .": "sustainability_co2_reduction_percent",
})

# (Entfernt) Seite 6 frühere KPI-Zusammenfassung wurde durch Produkt & Dienstleistungen ersetzt

# Seite 6 – Dienstleistungsplatzhalter (Standard & optional)
PLACEHOLDER_MAPPING.update({
    # Produkte (werden auf Seite 6 erneut gelistet)
    "X_PROD_MODULE": "summary_product_module_line",
    "X_PROD_INVERTER": "summary_product_inverter_line",
    "X_PROD_STORAGE": "summary_product_storage_line",

    # Separate Keys für Stückzahl und Kapazität
    "X_PROD_MODULE_COUNT": "pv_modules_count_key",
    "X_PROD_STORAGE_CAPACITY": "storage_capacity_key",

    # Neue formatierte Produktwerte für Seite 6
    "X_MODULE_COUNT_FORMATTED": "module_count_formatted",
    "X_INVERTER_POWER_FORMATTED": "inverter_power_w_formatted",
    "X_STORAGE_CAPACITY_FORMATTED": "storage_capacity_formatted",

    # Speicher-Relationen Platzhalter
    "relation_tagverbrauch_prozent": "storage_consumption_ratio_percent",
    "relation_pvproduktion_prozent": "storage_production_ratio_percent",

    # Standard-Dienstleistungen (immer standardmäßig aktiv)
    "X_SRV_BERATUNG": "service_consulting",
    "X_SRV_PLANUNG": "service_planning",
    "X_SRV_PROJEKTIERUNG": "service_project_management",
    "X_SRV_OPTIMIERUNG": "service_optimization",
    "X_SRV_EVU_GENEHMIGUNG": "service_grid_application",
    "X_SRV_DC_MONTAGE": "service_dc_installation",
    "X_SRV_AC_INSTALLATION": "service_ac_installation",
    "X_SRV_SPEICHER_INSTALLATION": "service_storage_installation",
    "X_SRV_INBETRIEBNAHME": "service_commissioning_training",
    "X_SRV_FERTIGMELDUNG_EVU": "service_grid_completion",

    # Optionale Dienstleistungen
    "X_SRV_WEITERE": "service_additional_tasks",
    "X_SRV_WALLBOX_LEITUNG": "service_wallbox_cabling",
    "X_SRV_NOTSTROM_AKTIVIERUNG": "service_backup_power_activation",
    "X_SRV_ENERGIEMANAGEMENT": "service_energy_management_system",
    "X_SRV_DYNAMISCHER_TARIF": "service_dynamic_tariff_activation",
    "X_SRV_SONSTIGES": "service_custom_entries_joined",
    # Dynamische Labels (werden geleert wenn Service deaktiviert)
    "X_LBL_BERATUNG": "label_service_consulting",
    "X_LBL_PLANUNG": "label_service_planning",
    "X_LBL_PROJEKTIERUNG": "label_service_project_management",
    "X_LBL_OPTIMIERUNG": "label_service_optimization",
    "X_LBL_EVU_GENEHMIGUNG": "label_service_grid_application",
    "X_LBL_DC_MONTAGE": "label_service_dc_installation",
    "X_LBL_AC_INSTALLATION": "label_service_ac_installation",
    "X_LBL_SPEICHER_INSTALLATION": "label_service_storage_installation",
    "X_LBL_INBETRIEBNAHME": "label_service_commissioning_training",
    "X_LBL_FERTIGMELDUNG_EVU": "label_service_grid_completion",
    "X_LBL_WEITERE": "label_service_additional_tasks",
    "X_LBL_WALLBOX_LEITUNG": "label_service_wallbox_cabling",
    "X_LBL_NOTSTROM_AKTIVIERUNG": "label_service_backup_power_activation",
    "X_LBL_ENERGIEMANAGEMENT": "label_service_energy_management_system",
    "X_LBL_DYNAMISCHER_TARIF": "label_service_dynamic_tariff_activation",
    "X_LBL_SONSTIGES": "label_service_custom_entries",
    "X_SRV_SUMMARY": "service_summary_line",
})


def fmt_number(
        value: Any,
        decimal_places: int = 2,
        suffix: str = "",
        force_german: bool = True) -> str:
    """Formatiert Zahlen im deutschen Format mit Punkt als Tausendertrennzeichen und Komma als Dezimaltrennzeichen."""
    try:
        if value is None or value == "":
            return "0,00" + (" " + suffix if suffix else "")

        # String bereinigen falls nötig
        if isinstance(value, str):
            # Entferne Einheiten und unerwünschte Zeichen
            clean_val = re.sub(r'[^\d,.-]', '', value)
            clean_val = clean_val.replace(',', '.')
        else:
            clean_val = str(value)

        num = float(clean_val)

        if force_german:
            # Deutsche Formatierung: Tausendertrennzeichen = Punkt,
            # Dezimaltrennzeichen = Komma
            if decimal_places == 0:
                formatted = f"{num:,.0f}".replace(
                    ',', '#').replace('.', ',').replace('#', '.')
            else:
                formatted = f"{num:,.{decimal_places}f}".replace(
                    ',', '#').replace('.', ',').replace('#', '.')
        else:
            # Fallback: Standard-Formatierung
            formatted = f"{num:.{decimal_places}f}"

        return formatted + (" " + suffix if suffix else "")

    except (ValueError, TypeError):
        return "0" + (",00" if decimal_places > 0 else "") + \
            (" " + suffix if suffix else "")


def build_dynamic_data(project_data: dict[str,
                                          Any] | None,
                       analysis_results: dict[str,
                                              Any] | None,
                       company_info: dict[str,
                       Any] | None = None) -> dict[str,
                                                   str]:
    """Erzeugt ein Dictionary mit dynamischen Werten für die Overlays."""
    import re  # Import re at the beginning of the function
    # Dies ist dein vollständiger Originalcode. Die einzige Änderung ist der
    # Block ganz am Ende.
    project_data = project_data or {}
    analysis_results = analysis_results or {}
    company_info = company_info or {}

    customer = project_data.get("customer_data", {}) if isinstance(
        project_data, dict) else {}
    project_details = project_data.get(
        "project_details", {}) if isinstance(project_data, dict) else {}

    def as_str(v: Any) -> str:
        return "" if v is None else str(v)

    def parse_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip()
            s = re.sub(r"[^0-9,\.\-]", "", s).replace(",", ".")
            return float(s) if s not in {"", "-", "."} else None
        except Exception:
            return None

    first = as_str(customer.get("first_name") or "").strip()
    last = as_str(customer.get("last_name") or "").strip()
    full_name = f"{first} {last}".strip()

    result: dict[str, str] = {
        "customer_name": full_name,
        "customer_street": f"{as_str(customer.get('address'))} {as_str(customer.get('house_number'))}".strip(),
        "customer_city_zip": f"{as_str(customer.get('zip_code'))} {as_str(customer.get('city'))}".strip(),
        "customer_phone": as_str(customer.get("phone_mobile") or customer.get("phone_landline")),
        "customer_email": as_str(customer.get("email")),
        "company_name": as_str(company_info.get("name")),
        "company_street": as_str(company_info.get("street")),
        "company_city_zip": f"{as_str(company_info.get('zip_code'))} {as_str(company_info.get('city'))}".strip(),
        "company_phone": as_str(company_info.get("phone")),
        "company_email": as_str(company_info.get("email")),
        "company_logo_b64": as_str(company_info.get("logo_base64")),
    }

    # Tolerante Zahl-zu-Float Konvertierung: akzeptiert "10,0", "10.0", "10
    # kWh", "10,00 kWh"
    def parse_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip()
            # Einheiten entfernen
            s = re.sub(r"[^0-9,\.\-]", "", s)
            # Komma in Punkt wandeln
            s = s.replace(",", ".")
            return float(s) if s not in {"", "-", "."} else None
        except Exception:
            return None

    # Kundendaten korrekt aus den echten Keys aufbauen
    first = as_str(customer.get("first_name") or "").strip()
    last = as_str(customer.get("last_name") or "").strip()
    salutation = as_str(customer.get("salutation") or "").strip()
    title = as_str(customer.get("title") or "").strip()
    if title.lower() in {"", "(kein)", "keine", "none", "null"}:
        title = ""
    name_parts = [p for p in [salutation, title, first, last] if p]
    full_name = " ".join(name_parts)

    street = as_str(customer.get("address") or "").strip()
    house_no = as_str(customer.get("house_number") or "").strip()
    street_full = (street + (" " + house_no if house_no else "")).strip()
    zip_code = as_str(customer.get("zip_code") or "").strip()
    city = as_str(customer.get("city") or "").strip()
    city_zip = (f"{zip_code} {city}").strip()
    phone = as_str(customer.get("phone_mobile")
                   or customer.get("phone_landline") or "").strip()
    email = as_str(customer.get("email") or "").strip()

    result: dict[str, str] = {
        "customer_name": full_name,
        "customer_street": street_full,
        "customer_city_zip": city_zip,
        "customer_phone": phone,
        "customer_email": email,

        # Firma (für Platzhalter rechts)
        "company_name": as_str(company_info.get("name") or ""),
        "company_street": as_str(company_info.get("street") or ""),
        "company_city_zip": as_str((f"{company_info.get('zip_code', '')} {company_info.get('city', '')}").strip()),
        "company_phone": as_str(company_info.get("phone") or ""),
        "company_email": as_str(company_info.get("email") or ""),
        "company_website": as_str(company_info.get("website") or ""),

        # Firmenlogo (Base64) für Overlay-Header auf Seiten 1-6
        "company_logo_b64": as_str(company_info.get("logo_base64") or ""),

        # Seite 4 – Defaults, damit keine Platzhaltertexte stehen bleiben
        "module_manufacturer": "",
        "module_model": "",
        "module_power_wp": "",
        "module_warranty_years": "siehe Produktdatenblatt",
        "module_performance_warranty": "",
        "inverter_manufacturer": "",
        "inverter_max_efficiency_percent": "",
        "inverter_warranty_years": "siehe Produktdatenblatt",
        # Neue WR-Felder (Seite 4 erweitert)
        "inverter_model": "",
        "inverter_power_watt": "",
        "inverter_type": "",
        "inverter_phases": "",
        "inverter_shading_management": "",
        "inverter_backup_capable": "",
        "inverter_smart_home_integration": "",
        "inverter_guarantee_text": "",
        "storage_manufacturer": "",
        "storage_model": "",
        "storage_capacity_kwh": "",
        "storage_power_kw": "",
        "storage_dod_percent": "",
        "storage_cycles": "",
        # Neue Speicher-Felder (Seite 4)
        "storage_cell_technology": "",
        "storage_size_battery_kwh_star": "",
        "storage_extension_module_size_kwh": "",
        "storage_max_size_kwh": "",
        "storage_backup_text": "",
        "storage_outdoor_capability": "",
        "storage_warranty_text": "siehe Produktdatenblatt",
        # Bilder für Seite 4 (aus Produkt-DB, Base64 – werden separat
        # gezeichnet)
        "module_image_b64": "",
        "inverter_image_b64": "",
        "storage_image_b64": "",
    }

    # Footer-Infos: Links unten jetzt Kundenname; Mitte: aktuelles Datum
    # (dd.mm.YYYY)
    try:
        from datetime import datetime
        date_str = datetime.now().strftime("%d.%m.%Y")
    except Exception:
        date_str = ""
    # Links unten: Kundenname (wie auf allen Seiten gewünscht)
    result["footer_company"] = full_name
    # Mitte unten: "Angebot, <Datum>"
    result["footer_date"] = f"Angebot, {date_str}" if date_str else "Angebot"

    # Anlagengröße (kWp): bevorzugt aus analysis_results, sonst aus
    # project_details berechnen
    anlage_kwp = analysis_results.get("anlage_kwp")
    if anlage_kwp is None:
        # Berechnung: Anzahl Module × Leistung pro Modul (Wp) / 1000
        try:
            mod_qty = float(project_details.get("module_quantity") or 0)
            mod_wp = float(project_details.get(
                "selected_module_capacity_w") or 0)
            anlage_kwp_calc = (
                mod_qty * mod_wp) / 1000.0 if mod_qty > 0 and mod_wp > 0 else project_details.get("anlage_kwp")
            anlage_kwp = anlage_kwp_calc
        except Exception:
            anlage_kwp = project_details.get("anlage_kwp")
    if anlage_kwp is not None:
        # Seite 1: immer 2 Dezimalstellen anzeigen
        result["anlage_kwp"] = fmt_number(anlage_kwp, 2, "kWp")
        # Kompatibilität: fülle optional alten Key mit (ebenfalls 2
        # Dezimalstellen)
        result["pv_power_kWp"] = fmt_number(anlage_kwp, 2, "kWp")

    # Anzahl der PV-Module (nur Zahl)
    try:
        mods_qty = project_details.get("module_quantity")
        if mods_qty is None:
            mods_qty = analysis_results.get("module_quantity")
        if mods_qty is not None:
            # Nur die Zahl ohne Einheit
            result["pv_modules_count_number"] = fmt_number(
                float(mods_qty), 0, "")
            # Neu: Darstellung mit Suffix "Stück" für Seite 1
            result["pv_modules_count_with_unit"] = f"{
                result['pv_modules_count_number']} Stück"
    except Exception:
        pass

    # Batteriegröße (kWh): Spiegel die UI-Logik aus dem Solar Calculator
    # Priorität:
    # 1) Vom Nutzer gesetzte Kapazität in der Technik-Auswahl: project_details['selected_storage_storage_power_kw'] (App-Konvention: kWh)
    # 2) Kapazität aus Produkt-DB zum gewählten Modell – bevorzugt 'storage_power_kw' (in der App häufig als kWh gepflegt),
    #    danach echte Kapazitätsfelder ('capacity_kwh', 'usable_capacity_kwh', 'nominal_capacity_kwh')
    # 3) Weitere Fallbacks: analysis_results['battery_capacity_kwh'],
    # project_details explizit, alternative Felder
    bat_kwh = None
    # 1) Modellkapazität aus DB (wie im Solar Calculator angezeigt) – BEVOR UI-Wert,
    #    damit direkt beim Modellwechsel die richtige Kapazität angezeigt wird.
    if bat_kwh in (None, 0.0):
        try:
            from product_db import get_product_by_model_name as _get_prod_model_cap
        except Exception:
            _get_prod_model_cap = None  # type: ignore
        storage_model_name_pref = as_str(
            project_details.get("selected_storage_name") or "").strip()
        if _get_prod_model_cap and storage_model_name_pref:
            try:
                std_pref = _get_prod_model_cap(storage_model_name_pref) or {}
                # Bevorzugt exakt wie im Solar Calculator: storage_power_kw als kWh interpretieren,
                # danach echte Kapazitätsfelder als Fallback
                cand_db = [
                    std_pref.get("storage_power_kw"),
                    std_pref.get("capacity_kwh"),
                    std_pref.get("usable_capacity_kwh"),
                    std_pref.get("nominal_capacity_kwh"),
                ]
                for cand in cand_db:
                    val = parse_float(cand)
                    if val and 0.0 < val <= 200.0:
                        bat_kwh = val
                        break
            except Exception:
                pass

    # 2) Nutzerwert aus UI (falls DB nichts lieferte)
    if bat_kwh in (None, 0.0):
        ui_kwh = parse_float(project_details.get(
            "selected_storage_storage_power_kw"))
        if ui_kwh and ui_kwh > 0:
            bat_kwh = ui_kwh

    # 3) Fallbacks auf Analyse/weitere Projektfelder
    if bat_kwh in (None, 0.0):
        fallbacks = [
            analysis_results.get("battery_capacity_kwh"),
            project_details.get("selected_storage_capacity_kwh"),
            project_details.get("battery_capacity_kwh"),
            analysis_results.get("selected_storage_storage_power_kw"),
        ]
        for f in fallbacks:
            val = parse_float(f)
            if val and val > 0:
                bat_kwh = val
                break

    if bat_kwh is not None and bat_kwh > 0:
        result["battery_capacity_kwh"] = fmt_number(float(bat_kwh), 2, "kWh")
        # Für Seite 1 und allgemeine Anzeige: gleicher Wert unter dem
        # generischen Key verwenden
        result["storage_capacity_kwh"] = fmt_number(float(bat_kwh), 2, "kWh")
        # Seite 4: Titel "BATTERIESPEICHER – <kWh>"
        result["storage_section_title"] = f"BATTERIESPEICHER – {
            fmt_number(
                float(bat_kwh), 2, 'kWh')}"
        # Seite 2: erwartete jährliche Batteriemenge (Daumenregel): Kapazität ×
        # 300 Tage
        try:
            battery_expected_annual_kwh = float(bat_kwh) * 300.0
        except Exception:
            battery_expected_annual_kwh = None
    else:
        battery_expected_annual_kwh = None
        # Kein Wert: Titel ohne kWh anzeigen
        result["storage_section_title"] = "BATTERIESPEICHER"

    # Jahresproduktion (kWh/Jahr)
    annual_prod = (
        analysis_results.get("annual_pv_production_kwh")
        or analysis_results.get("annual_yield_kwh")
        or analysis_results.get("sim_annual_yield_kwh")
    )
    if annual_prod is not None:
        # Seite 1: immer 2 Dezimalstellen anzeigen
        result["annual_pv_production_kwh"] = fmt_number(annual_prod, 2, "kWh")
        # Kurzform (z. B. Seite 2) bleibt grob gerundet
        result["pv_prod_kwh_short"] = fmt_number(annual_prod, 0, "kWh")

    # Wechselrichter Gesamtleistung (kW) – für Seite 1 "Warmwasser"-Platz
    # Quellen: project_details['selected_inverter_power_kw'] oder ['inverter_power_kw']
    # Fallback: single * quantity
    try:
        inv_total_kw = (
            project_details.get("selected_inverter_power_kw")
            or project_details.get("inverter_power_kw")
        )
        if inv_total_kw is None:
            inv_single = project_details.get(
                "selected_inverter_power_kw_single")
            inv_qty = project_details.get("selected_inverter_quantity", 1)
            if inv_single is not None and inv_qty:
                inv_total_kw = float(inv_single) * float(inv_qty)
        if inv_total_kw is not None:
            # Plausibilitätsprüfung: Wechselrichter sollten zwischen 1 kW und 100 kW haben
            # Falls der Wert unrealistisch hoch ist, vermutlich bereits in Watt
            # statt kW angegeben
            if float(inv_total_kw) > 100:
                # Wahrscheinlich bereits in Watt - konvertiere zu kW
                inv_total_kw = float(inv_total_kw) / 1000
                print(
                    f"WARNUNG: Wechselrichter-Leistung war wahrscheinlich in Watt angegeben. Korrigiert zu {inv_total_kw} kW")

            # Neu: ohne Dezimalstellen anzeigen (kW für Seite 4)
            result["inverter_total_power_kw"] = fmt_number(
                float(inv_total_kw), 0, "kW")

            # Neu: Wechselrichterleistung in Watt für Seite 1 "Warmwasser"
            # Platz
            inv_watt = int(float(inv_total_kw) * 1000)
            result["inverter_total_power_w"] = fmt_number(inv_watt, 0, "W")

            # Wechselrichter-Überschrift für Seite 4 mit Leistung
            # Konvertiere kW zu Watt für die Anzeige (z.B. "WECHSELRICHTER -
            # 10.000 W")
            watt_formatted = f"{inv_watt:,}".replace(",", ".")
            result["inverter_section_title"] = (
                f"WECHSELRICHTER – {watt_formatted} W"
            )
        else:
            result["inverter_section_title"] = "WECHSELRICHTER"
    except Exception:
        result["inverter_section_title"] = "WECHSELRICHTER"

    # Autarkie und Eigenverbrauch (%)
    self_supply = (
        analysis_results.get("self_supply_rate_percent")
        or analysis_results.get("self_sufficiency_percent")
        or analysis_results.get("autarky_percent")
    )
    if self_supply is not None:
        result["self_supply_rate_percent"] = fmt_number(self_supply, 0, "%")

    self_cons = analysis_results.get("self_consumption_percent")
    if self_cons is not None:
        result["self_consumption_percent"] = fmt_number(self_cons, 0, "%")

    # Amortisationszeit (Jahre) für Seite 1
    amort_years = (
        analysis_results.get("amortization_time_years")
        or analysis_results.get("amortisationszeit_jahre")
    )
    if amort_years is not None:
        # Immer 2 Dezimalstellen für die Amortisationszeit im PDF (Seite 1)
        result["amortization_time"] = fmt_number(amort_years, 2, "Jahre")

    # Seite 2: Energieflüsse (Jahr 1)
    monthly_direct_sc = analysis_results.get(
        "monthly_direct_self_consumption_kwh", []) or []
    monthly_storage_charge = analysis_results.get(
        "monthly_storage_charge_kwh", []) or []
    monthly_storage_discharge_sc = analysis_results.get(
        "monthly_storage_discharge_for_sc_kwh", []) or []
    feed_in_kwh = analysis_results.get("netzeinspeisung_kwh")
    grid_bezug_kwh = analysis_results.get(
        "grid_bezug_kwh") or analysis_results.get("grid_purchase_kwh")
    # Jahresverbrauch aus möglichst vielen Quellen robust ermitteln (9500 kWh
    # sicher übernehmen)
    annual_consumption = (
        # Primär: Analysis-Ergebnisse
        analysis_results.get("annual_consumption_kwh")
        or analysis_results.get("annual_consumption_kwh_yr")
        or analysis_results.get("total_consumption_kwh_yr")
        or analysis_results.get("annual_consumption")
        # Projekt-Details (Eingabemaske)
        or project_details.get("annual_consumption_kwh_yr")
        or project_details.get("annual_consumption_kwh")
        # Gesamtdaten (z. B. CRM/Quick-Calc/Importe)
        or project_data.get("annual_consumption_kwh")
        or project_data.get("annual_consumption")
        or (project_data.get("consumption_data", {}) or {}).get("annual_consumption")
    )
    # Falls nur Teilwerte vorhanden sind: Haushalt + Heizung aufaddieren
    if annual_consumption in (None, 0, 0.0):
        try:
            haushalt = float(project_details.get(
                "annual_consumption_kwh") or 0.0)
            heizung = float(project_details.get(
                "consumption_heating_kwh_yr") or 0.0)
            combo = haushalt + heizung
            annual_consumption = combo if combo > 0 else annual_consumption
        except Exception:
            pass
    # Jahresproduktion (für Konsistenzprüfung auf Seite 2)
    annual_prod_float = None
    try:
        if annual_prod is not None:
            annual_prod_float = float(annual_prod)
    except Exception:
        annual_prod_float = None

    try:
        direct_sc_sum = sum(float(v or 0) for v in monthly_direct_sc)
        charge_sum = sum(float(v or 0) for v in monthly_storage_charge)
        discharge_sc_sum = sum(float(v or 0)
                               for v in monthly_storage_discharge_sc)
    except Exception:
        direct_sc_sum, charge_sum, discharge_sc_sum = 0.0, 0.0, 0.0

    # Falls Speicherkapazität bekannt: Batteriesummen überschreiben
    # (heuristisch) mit Kapazität × 300
    if battery_expected_annual_kwh and battery_expected_annual_kwh > 0:
        charge_sum = float(battery_expected_annual_kwh)
        discharge_sc_sum = float(battery_expected_annual_kwh)

    # Konsistenz- und Realismus-Korrekturen für Seite 2
    def to_float_or_none(x: Any) -> float | None:
        try:
            return float(x)
        except Exception:
            return None

    cons_total = to_float_or_none(annual_consumption)
    grid_bezug_val = to_float_or_none(grid_bezug_kwh)
    feed_in_val = to_float_or_none(feed_in_kwh)

    # 1) Direktverbrauch darf weder Jahresproduktion noch Jahresverbrauch
    # überschreiten
    if annual_prod_float is not None:
        direct_sc_sum = min(direct_sc_sum, max(0.0, annual_prod_float))
    if cons_total is not None:
        direct_sc_sum = min(direct_sc_sum, max(0.0, cons_total))

    # 2) Speicher-Ladung kann nicht größer sein als Restproduktion nach
    # Direktverbrauch
    if annual_prod_float is not None:
        charge_sum = min(charge_sum, max(
            0.0, annual_prod_float - direct_sc_sum))
    # 3) Speicher-Entladung für Direktverbrauch kann nicht größer sein als
    # geladen UND Rest-Verbrauch
    if cons_total is not None:
        discharge_sc_sum = min(discharge_sc_sum, max(
            0.0, cons_total - direct_sc_sum))
    discharge_sc_sum = min(discharge_sc_sum, charge_sum)

    # 4) Einspeisung = Produktion - (Direkt + Speicher-Ladung) [>=0]
    if annual_prod_float is not None:
        feed_in_calc = max(0.0, annual_prod_float - direct_sc_sum - charge_sum)
        feed_in_val = feed_in_calc

    # 5) Netzbezug = Verbrauch - (Direkt + Speicher-Entladung) [>=0]
    if cons_total is not None:
        grid_bezug_calc = max(
            0.0, cons_total - direct_sc_sum - discharge_sc_sum)
        grid_bezug_val = grid_bezug_calc

    # Formatiert in Ergebnisfelder schreiben
    if direct_sc_sum:
        result["direct_self_consumption_kwh"] = fmt_number(
            direct_sc_sum, 0, "kWh")
    if charge_sum:
        result["battery_charge_kwh"] = fmt_number(charge_sum, 0, "kWh")
    if discharge_sc_sum:
        result["battery_discharge_for_sc_kwh"] = fmt_number(
            discharge_sc_sum, 0, "kWh")
    if feed_in_val is not None:
        result["grid_feed_in_kwh"] = fmt_number(feed_in_val, 0, "kWh")
    if grid_bezug_val is not None:
        result["grid_bezug_kwh"] = fmt_number(grid_bezug_val, 0, "kWh")
    if cons_total is not None:
        result["annual_consumption_kwh"] = fmt_number(cons_total, 0, "kWh")

    # Unteres Diagramm ("Woher kommt mein Strom?") als kWh ausgeben
    if cons_total is not None:
        # Direkter Verbrauch (aus PV)
        result["consumption_direct_kwh"] = fmt_number(
            max(0.0, min(direct_sc_sum, cons_total)), 0, "kWh")
        # Batteriespeicher deckt Verbrauch mittels Entladung
        result["consumption_battery_kwh"] = fmt_number(
            max(0.0, min(discharge_sc_sum, cons_total)), 0, "kWh")
        # Rest aus dem Netz
        res_grid = cons_total - \
            max(0.0, min(direct_sc_sum, cons_total)) - \
            max(0.0, min(discharge_sc_sum, cons_total))
        result["consumption_grid_kwh"] = fmt_number(
            max(0.0, res_grid), 0, "kWh")

    # Seite 2: Hinweistext zur Heuristik (300 Tage statt 365)
    if battery_expected_annual_kwh and battery_expected_annual_kwh > 0:
        result["battery_note_text"] = (
            "Hinweis: Batteriespeicher-Jahreswert überschlägig mit Speicherkapazität × 300 Tage kalkuliert (statt 365)."
        )

    # Falls self_consumption_percent fehlt, robust ableiten:
    # 1) aus Produktionsanteilen: direkt + Speicher (in %)
    # 2) aus kWh-Summen: (Direkt + Speicher-Entladung für Direktverbrauch) /
    # Jahresproduktion
    if not result.get("self_consumption_percent"):
        _direct_q = analysis_results.get(
            "direktverbrauch_anteil_pv_produktion_pct")
        _batt_q = analysis_results.get(
            "speichernutzung_anteil_pv_produktion_pct")
        if isinstance(
                _direct_q, (int, float)) and isinstance(
                _batt_q, (int, float)):
            try:
                val = max(0.0, min(100.0, float(_direct_q) + float(_batt_q)))
                result["self_consumption_percent"] = fmt_number(val, 0, "%")
            except Exception:
                pass
        elif (annual_prod is not None) and (direct_sc_sum or discharge_sc_sum):
            try:
                prod = float(annual_prod)
                if prod > 0:
                    val = max(0.0, min(
                        100.0, 100.0 * (float(direct_sc_sum) + float(discharge_sc_sum)) / prod))
                    result["self_consumption_percent"] = fmt_number(
                        val, 0, "%")
            except Exception:
                pass

    # Seite 2: Quoten / Prozente – Produktion strikt als Partition (Direkt,
    # Batterie-Ladung, Einspeisung)
    if annual_prod_float and annual_prod_float > 0:
        try:
            # Rohanteile 0..1
            direct_raw = max(
                0.0, min(direct_sc_sum, annual_prod_float)) / annual_prod_float
            # Batterieanteil an Produktion basiert auf Ladung aus Produktion,
            # begrenzt durch Rest nach Direktverbrauch
            battery_raw = max(0.0, min(charge_sum, max(
                0.0, annual_prod_float - direct_sc_sum))) / annual_prod_float
            feed_raw = max(0.0, 1.0 - direct_raw - battery_raw)

            # Integer-Normalisierung: Summe exakt 100
            direct_int = int(round(direct_raw * 100.0))
            battery_int = int(round(battery_raw * 100.0))
            # Falls Rundung > 100, zuerst Batterie reduzieren, dann Direkt
            if direct_int + battery_int > 100:
                over = direct_int + battery_int - 100
                reduce_batt = min(over, battery_int)
                battery_int -= reduce_batt
                over -= reduce_batt
                if over > 0:
                    direct_int = max(0, direct_int - over)
            feed_int = max(0, 100 - direct_int - battery_int)

            # Diese drei betreffen die Pfeile oben; Positionen von Direktverbrauch und Einspeisung tauschen
            # Direktverbrauchs-Prozent im Template soll den Einspeisungswert
            # anzeigen
            result["direct_consumption_quote_prod_percent"] = fmt_number(
                feed_int, 0, "%")
            result["battery_use_quote_prod_percent"] = fmt_number(
                battery_int, 0, "%")
            # Einspeisungs-Token (Zahl ohne %) soll den Direktverbrauchswert
            # anzeigen
            result["feed_in_quote_prod_percent_number"] = str(direct_int)
        except Exception:
            pass

    if cons_total and cons_total > 0:
        try:
            battery_cover_pct = 100.0 * \
                max(0.0, min(discharge_sc_sum, cons_total)) / cons_total
            grid_rate_pct = 100.0 * \
                max(0.0, min(grid_bezug_val or 0.0, cons_total)) / cons_total
            direct_cover_pct = 100.0 * \
                max(0.0, min(direct_sc_sum, cons_total)) / cons_total
            # Diese drei betreffen die Pfeile unten; immer setzen
            result["battery_cover_consumption_percent"] = fmt_number(
                battery_cover_pct, 0, "%")
            result["grid_consumption_rate_percent"] = fmt_number(
                grid_rate_pct, 0, "%")
            try:
                from calculations import format_kpi_value as _fmt
                result["direct_cover_consumption_percent_number"] = _fmt(
                    direct_cover_pct, unit="", precision=0)
            except Exception:
                result["direct_cover_consumption_percent_number"] = str(
                    int(round(direct_cover_pct)))
        except Exception:
            pass

    # NEUE BERECHNUNGSLOGIK (User-Vorgabe) für Seite 2 & Seite 1 Kennzahlen
    # "Meine Eigenverbrauchsquote" = Speicherladung Quote (oben) + direkter Stromverbrauch Quote (oben)
    # Alternativ: 100% - Netzeinspeisung Quote (oben)
    # "Mein erzielter Autarkiegrad" = Speichernutzung Quote (unten) + direkter Stromverbrauch Quote (unten)
    # Alternativ: 100% - Stromnetz Quote (unten)
    try:
        def _parse_pct_str(val: Any) -> float:
            if val is None:
                return 0.0
            try:
                s = str(val).strip().replace('%', '').replace(
                    ',', '.').replace(' ', '')
                return float(s) if s not in ('', '-', '.') else 0.0
            except Exception:
                return 0.0

        # OBERES DIAGRAMM (Produktion)
        battery_charge_pct = _parse_pct_str(result.get(
            "battery_use_quote_prod_percent"))  # z.B. "41%"
        # Direkter Verbrauch Prozent steht im Template als Zahl mit % Zeichen (im Beispiel 25%),
        # durch vorheriges Mapping kann 'direct_consumption_quote_prod_percent' aktuell FEED zeigen.
        # Der echte Direktverbrauchs-Prozentwert steckt (nach der
        # Swapping-Logik) in 'feed_in_quote_prod_percent_number'.
        direct_consumption_pct = _parse_pct_str(result.get(
            "feed_in_quote_prod_percent_number"))  # Zahl ohne % -> direkt
        feed_pct_swapped = _parse_pct_str(result.get(
            "direct_consumption_quote_prod_percent"))  # tatsächliche Netzeinspeisung
        # Primär-Definition: Speicher + Direkt
        upper_self_consumption = battery_charge_pct + direct_consumption_pct
        if upper_self_consumption <= 0.0 and feed_pct_swapped > 0.0:
            # Fallback: 100 - Netzeinspeisung
            upper_self_consumption = 100.0 - feed_pct_swapped
        upper_self_consumption = max(0.0, min(100.0, upper_self_consumption))

        # UNTERES DIAGRAMM (Verbrauch)
        battery_cover_pct = _parse_pct_str(result.get(
            "battery_cover_consumption_percent"))  # z.B. "Speichernutzung quote"
        direct_cover_pct = _parse_pct_str(result.get(
            "direct_cover_consumption_percent_number"))  # Zahl ohne %
        grid_pct = _parse_pct_str(result.get(
            "grid_consumption_rate_percent"))  # Stromnetz Quote
        lower_autarky = battery_cover_pct + direct_cover_pct
        if lower_autarky <= 0.0 and grid_pct > 0.0:
            lower_autarky = 100.0 - grid_pct
        lower_autarky = max(0.0, min(100.0, lower_autarky))

        # Override der bestehenden Keys für Seite 2 Anzeige & Seite 1 Donuts
        # self_consumption_percent -> "Meine Eigenverbrauchsquote"
        # self_supply_rate_percent -> "Mein erzielter Autarkiegrad"
        try:
            from calculations import format_kpi_value as _fmt
            result["self_consumption_percent"] = _fmt(
                upper_self_consumption, unit="%", precision=0)
            result["self_supply_rate_percent"] = _fmt(
                lower_autarky, unit="%", precision=0)
        except Exception:
            # Fallback einfache Formatierung
            result["self_consumption_percent"] = f"{
                int(
                    round(upper_self_consumption))}%"
            result["self_supply_rate_percent"] = f"{
                int(
                    round(lower_autarky))}%"
    except Exception:
        pass

    # Seite 3: LCOE als Cent/kWh, IRR
    lcoe_eur_kwh = analysis_results.get("lcoe_euro_per_kwh")
    if isinstance(lcoe_eur_kwh, (int, float)):
        result["lcoe_cent_per_kwh"] = fmt_number(
            lcoe_eur_kwh * 100.0, 1, "Cent")
    irr = analysis_results.get("irr_percent")
    if irr is not None:
        result["irr_percent"] = fmt_number(irr, 1, "%")

    # Seite 3 – Stromkosten-Projektion für 10 Jahre (Bars links/rechts) und dynamische Y-Achse
    # Datenquelle laut Anforderung: Bedarfsanalyse – monatliche Stromkosten
    # Haushalt + Heizung
    def _get_monthly_cost_eur() -> float:
        # 1) Primär: Top-Level project_data (wie in analysis.py verwendet)
        try:
            hh = parse_float(project_data.get(
                "stromkosten_haushalt_euro_monat")) or 0.0
            hz = parse_float(project_data.get(
                "stromkosten_heizung_euro_monat")) or 0.0
            if (hh + hz) > 0:
                return float(hh + hz)
        except Exception:
            pass
        # 2) Alternativ: project_details
        try:
            hh = parse_float(project_details.get(
                "stromkosten_haushalt_euro_monat")) or 0.0
            hz = parse_float(project_details.get(
                "stromkosten_heizung_euro_monat")) or 0.0
            if (hh + hz) > 0:
                return float(hh + hz)
        except Exception:
            pass
        # 3) Fallback: Aus Jahresverbrauch × aktuellem Strompreis (falls
        # verfügbar)
        try:
            cons_kwh = parse_float(analysis_results.get(
                "jahresstromverbrauch_fuer_hochrechnung_kwh"))
            price_eur_kwh = parse_float(analysis_results.get(
                "aktueller_strompreis_fuer_hochrechnung_euro_kwh"))
            if (cons_kwh and price_eur_kwh) and cons_kwh > 0 and price_eur_kwh > 0:
                return float(cons_kwh * price_eur_kwh / 12.0)
        except Exception:
            pass
        return 0.0

    def _get_price_increase_percent_pa() -> float:
        # Reihenfolge: analysis_results -> project_data/project_details ->
        # Admin-Setting -> 0
        cands = [
            analysis_results.get("electricity_price_increase_annual_percent"),
            analysis_results.get("electricity_price_increase"),
            project_data.get("electricity_price_increase_annual_percent"),
            project_details.get("electricity_price_increase_annual_percent"),
        ]
        for v in cands:
            val = parse_float(v)
            if val is not None and val >= 0:
                return float(val)
        # Admin-Fallback (falls gepflegt)
        try:
            from database import load_admin_setting as _load
            val = _load("electricity_price_increase_annual_percent", 5.0)
            valf = parse_float(val)
            if valf is not None and valf >= 0:
                return float(valf)
        except Exception:
            pass
        return 0.0

    try:
        monthly_cost = max(0.0, _get_monthly_cost_eur())
        annual_cost = monthly_cost * 12.0
        inc_pct = _get_price_increase_percent_pa()  # z. B. 5.0 für 5% p.a.
        inc_rate = max(0.0, float(inc_pct)) / 100.0
        # 10 Jahre ohne Erhöhung: linear 10x
        cost10_no_inc = annual_cost * 10.0
        # 10 Jahre mit Erhöhung: jährlich steigend (Zinseszins)
        cost10_with_inc = 0.0
        base = annual_cost
        for year in range(10):
            cost10_with_inc += base * ((1.0 + inc_rate) ** year)
        # Optional: 20 Jahre als Vorbereitung für spätere Darstellungen
        cost20_no_inc = annual_cost * 20.0
        cost20_with_inc = 0.0
        for year in range(20):
            cost20_with_inc += base * ((1.0 + inc_rate) ** year)
        # Werte in die Felder mit 2 Dezimalstellen und Euro-Suffix
        if cost10_no_inc > 0:
            result["cost_10y_no_increase_number"] = fmt_number(
                cost10_no_inc, 2, "€")
        if cost10_with_inc > 0:
            result["cost_10y_with_increase_number"] = fmt_number(
                cost10_with_inc, 2, "€")
        # 20-Jahre Felder bereitstellen (derzeit nicht ins Template gemappt) –
        # gleich formatiert
        if cost20_no_inc > 0:
            result["cost_20y_no_increase_number"] = fmt_number(
                cost20_no_inc, 2, "€")
        if cost20_with_inc > 0:
            result["cost_20y_with_increase_number"] = fmt_number(
                cost20_with_inc, 2, "€")
        # Dynamische Y-Achse (6 Ticks: Top .. 0) basierend auf Max-Wert
        max_val = max(cost10_no_inc, cost10_with_inc)
        if max_val <= 0:
            # Fallback: belasse Vorlage
            pass
        else:
            # "schöne" Schrittweite bestimmen (5 Intervalle bis 0)
            def nice_step(target: float) -> float:
                # Runde auf 1, 2, 5 x 10^n
                import math
                raw = max(1.0, target)
                exp = math.floor(math.log10(raw))
                for m in [1, 2, 5, 10]:
                    step = m * (10 ** exp)
                    if step * 5 >= raw:
                        return step
                # Fallback: nächsthöhere Zehnerpotenz
                return 10 ** (exp + 1)
            step = nice_step(max_val / 5.0)
            # Obergrenze auf Vielfaches von step*5 anheben
            import math
            top = math.ceil(max_val / step / 5.0) * step * 5.0
            # 5 gleichmäßige Abstände
            vals = [top * i / 5.0 for i in range(5, 0, -1)] + [0.0]
            keys = [
                "axis_tick_1_top",
                "axis_tick_2",
                "axis_tick_3",
                "axis_tick_4",
                "axis_tick_5",
                "axis_tick_6_bottom",
            ]
            for k, v in zip(keys, vals, strict=False):
                result[k] = fmt_number(v, 0, "").replace(" €", "")
    except Exception:
        pass

    # Seite 3 – NEUE BERECHNUNG (bereinigt, nur echte calculations.py Keys + neue dynamische Speicher-Keys)
        # 1. Einspeisetarif bestimmen (gestaffelt; Admin-Override möglich)
        # 1. Einspeisetarif bestimmen – PRIO: analysis_results > Admin > Default
# --- Seite 3 – Kernberechnung für die 5 Werte (einzige Quelle) ---

    # 1) Tarif (€/kWh) – vereinheitlicht über
    # resolve_feed_in_tariff_eur_per_kwh
    try:
        from database import load_admin_setting as _load_admin_setting_feed
    except Exception:
        _load_admin_setting_feed = None
    anlage_kwp_numeric = parse_float(analysis_results.get(
        "anlage_kwp")) or parse_float(project_data.get("anlage_kwp")) or 0.0
    einspeise_mode = (project_data.get("einspeise_art") or "parts")
    if _load_admin_setting_feed:
        eeg_eur_per_kwh = resolve_feed_in_tariff_eur_per_kwh(
            float(anlage_kwp_numeric),
            einspeise_mode,
            _load_admin_setting_feed,
            analysis_results_snapshot=(analysis_results.get(
                "einspeiseverguetung_eur_per_kwh"),)
        )
    else:
        eeg_eur_per_kwh = parse_float(analysis_results.get(
            "einspeiseverguetung_eur_per_kwh")) or 0.0786
        if eeg_eur_per_kwh > 1:  # falls ct geliefert
            eeg_eur_per_kwh /= 100.0

    # 2) Strompreis (€/kWh)
    price_eur_per_kwh = (
        parse_float(analysis_results.get(
            "aktueller_strompreis_fuer_hochrechnung_euro_kwh"))
        or parse_float(project_data.get("electricity_price_eur_per_kwh"))
        or parse_float(analysis_results.get("electricity_price_eur_per_kwh"))
        or parse_float(project_data.get("electricity_price_kwh"))
        or parse_float(project_data.get("electricity_price_per_kwh"))
        or 0.30
    )
    if price_eur_per_kwh > 5:  # Falls fälschlich ct/kWh
        price_eur_per_kwh /= 100.0

    # 3) Jahressummen / KWh-Quellen (aus calculations.py Ergebnissen/Listen)
    monthly_direct_sc = analysis_results.get(
        "monthly_direct_self_consumption_kwh") or []
    monthly_storage_charge = analysis_results.get(
        "monthly_storage_charge_kwh") or []
    monthly_storage_discharge = analysis_results.get(
        "monthly_storage_discharge_for_sc_kwh") or []
    monthly_feed_in_list = analysis_results.get("monthly_feed_in_kwh") or []

    direct_kwh = sum(float(x or 0)
                     for x in monthly_direct_sc) if monthly_direct_sc else 0.0

    # Primäre Quelle für Seite 3: exakt der auf Seite 2 berechnete Wert feed_in_val (ungekürzt) falls vorhanden
    # feed_in_val stammt aus Abschnitt Seite 2 weiter oben und wurde dort ggf.
    # plausibilisiert.
    feedin_kwh = None
    try:
        if 'feed_in_val' in locals() and feed_in_val is not None:
            feedin_kwh = float(feed_in_val)
    except Exception:
        feedin_kwh = None

    # Fallback 1: expliziter grid_feed_in_kwh Wert aus analysis_results (kann
    # Liste / String / Zahl sein)
    if (feedin_kwh is None or feedin_kwh == 0) and analysis_results.get(
            "grid_feed_in_kwh") is not None:
        raw_gfi = analysis_results.get("grid_feed_in_kwh")
        try:
            if isinstance(raw_gfi, list):
                feedin_kwh = sum(float(x or 0) for x in raw_gfi)
            elif isinstance(raw_gfi, (int, float)):
                feedin_kwh = float(raw_gfi)
            else:  # String
                import re as _re
                cleaned = _re.sub(r"[^0-9,\.]", "",
                                  str(raw_gfi)).replace(',', '.')
                feedin_kwh = float(cleaned) if cleaned else 0.0
        except Exception:
            feedin_kwh = None

    # Fallback 2: netzeinspeisung_kwh (Gesamtsumme aus Simulation)
    if (feedin_kwh is None or feedin_kwh == 0) and analysis_results.get(
            "netzeinspeisung_kwh") is not None:
        try:
            feedin_kwh = float(analysis_results.get(
                "netzeinspeisung_kwh") or 0)
        except Exception:
            pass

    # Fallback 3: Summe der monatlichen Feed-In Liste
    if (feedin_kwh is None or feedin_kwh == 0) and monthly_feed_in_list:
        try:
            feedin_kwh = sum(float(x or 0) for x in monthly_feed_in_list)
        except Exception:
            pass

    # Letzter Fallback: Wenn weiter nichts → 0 (KEIN hartkodierter 312er-Wert
    # mehr, Fehler sichtbar machen)
    if feedin_kwh is None:
        feedin_kwh = 0.0

    # Anomalie-Erkennung: Wenn Simulation (netzeinspeisung_kwh) extrem größer
    # als Seite 2 Wert war
    try:
        sim_val = parse_float(analysis_results.get(
            "netzeinspeisung_kwh")) or 0.0
        if 'feed_in_val' in locals() and feed_in_val not in (
                None, 0) and sim_val > 0 and feedin_kwh == sim_val:
            # Wenn Simulation > 3x Seite2-Wert -> verwende konservativ
            # Seite2-Wert
            if sim_val > 3 * float(feed_in_val):
                print(
                    f"WARN: Anomalie erkannt – simulierte Netzeinspeisung {
                        sim_val:.2f} kWh >> Seite2 {
                        feed_in_val:.2f} kWh. Verwende Seite2-Wert.")
                feedin_kwh = float(feed_in_val)
    except Exception:
        pass

    # Alias für konsistenten Zugriff (kann später im Result verwendet /
    # getestet werden)
    result.setdefault("annual_feed_in_kwh", fmt_number(feedin_kwh, 0, "kWh"))

    speicher_ladung_kwh = sum(
        float(
            x or 0) for x in monthly_storage_charge) if monthly_storage_charge else 0.0
    speicher_nutzung_kwh = sum(float(
        x or 0) for x in monthly_storage_discharge) if monthly_storage_discharge else 0.0

    # Fallbacks, wenn Monatslisten fehlen
    if not speicher_ladung_kwh:
        v = parse_float(analysis_results.get("annual_storage_charge_kwh"))
        if v:
            speicher_ladung_kwh = v
    if not speicher_nutzung_kwh:
        v = parse_float(analysis_results.get("annual_storage_discharge_kwh"))
        if v:
            speicher_nutzung_kwh = v

    speicher_ueberschuss_kwh = max(
        0.0, (speicher_ladung_kwh or 0.0) - (speicher_nutzung_kwh or 0.0))

    # 4) Geldwerte (die 5 Kacheln)
    val_direct_money = (direct_kwh or 0.0) * float(price_eur_per_kwh)
    val_feedin_money = (feedin_kwh or 0.0) * float(eeg_eur_per_kwh)
    val_speicher_nutzung_money = (
        speicher_nutzung_kwh or 0.0) * float(price_eur_per_kwh)
    val_speicher_ueberschuss_money = (
        speicher_ueberschuss_kwh or 0.0) * float(eeg_eur_per_kwh)

    # 5) Neue Berechnung: Steuerliche Vorteile
    # Einspeisevergütung unterliegt der Einkommensteuer, daher ist die
    # Steuerersparnis ein Vorteil
    einkommensteuer_satz = parse_float(project_data.get("income_tax_rate") or project_details.get(
        # Fallback: 42% (Standard in Deutschland)
        "income_tax_rate") or analysis_results.get("income_tax_rate")) or 0.42
    val_steuerliche_vorteile = val_feedin_money * \
        (einkommensteuer_satz /
         100.0) if einkommensteuer_satz > 1 else val_feedin_money * einkommensteuer_satz

    # Neue Gesamtberechnung: NUR Direkt + Einspeisung + Steuerliche Vorteile
    # (OHNE Speicher)
    total_savings = val_direct_money + val_feedin_money + val_steuerliche_vorteile

    # 5) Ergebnisfelder (NUR HIER setzen)
    result["self_consumption_without_battery_eur"] = fmt_number(
        val_direct_money, 2, "€")
    result["direct_grid_feed_in_eur"] = fmt_number(val_feedin_money, 2, "€")
    result["annual_feed_in_revenue_eur"] = fmt_number(
        val_feedin_money, 2, "€")  # Alias für Einspeisung
    result["tax_benefits_eur"] = fmt_number(
        val_steuerliche_vorteile, 2, "€")  # Neue steuerliche Vorteile
    result["battery_usage_savings_eur"] = fmt_number(
        val_speicher_nutzung_money, 2, "€")
    result["battery_surplus_feed_in_eur"] = fmt_number(
        val_speicher_ueberschuss_money, 2, "€")
    result["total_annual_savings_eur"] = fmt_number(total_savings, 2, "€")

    # (Optional) KWh-Infos für Debug / Anzeige
    result["calc_grid_feed_in_kwh_page3"] = fmt_number(feedin_kwh, 0, "kWh")
    result["calc_battery_discharge_kwh_page3"] = fmt_number(
        speicher_nutzung_kwh, 0, "kWh")
    result["calc_battery_charge_kwh_page3"] = fmt_number(
        speicher_ladung_kwh, 0, "kWh")
    result["calc_battery_surplus_kwh_page3"] = fmt_number(
        speicher_ueberschuss_kwh, 0, "kWh")

    # Debug-Ausgabe wie im Test
    print("DEBUG PAGE3 -> Preise & Tarife:")
    print(
        f"  Strompreis (€ / kWh): {price_eur_per_kwh:.2f} | EEG (€ / kWh): {eeg_eur_per_kwh:.2f}")
    print("DEBUG PAGE3 -> kWh-Datenquellen ANALYSE:")
    print(
        f"  grid_feed_in_kwh (Seite 2, raw): {
            analysis_results.get('grid_feed_in_kwh')}")
    print(
        f"  netzeinspeisung_kwh (Simulation): {
            analysis_results.get('netzeinspeisung_kwh')}")
    print(
        f"  monthly_feed_in_kwh (Liste): {
            analysis_results.get('monthly_feed_in_kwh')}")
    try:
        print(
            f"  Summe monthly_feed_in_kwh: {
                sum(
                    float(
                        x or 0) for x in (
                        analysis_results.get('monthly_feed_in_kwh') or [])):.2f} kWh")
    except Exception:
        print("  Summe monthly_feed_in_kwh: n/a")
    print(f"  FINAL verwendeter Feed-In Wert (kWh): {feedin_kwh:.2f}")
    if result.get('annual_feed_in_kwh'):
        print(
            f"  annual_feed_in_kwh (alias): {
                result.get('annual_feed_in_kwh')}")
    print(
        f"  Direkt: {
            direct_kwh:.2f} | Einspeisung: {
            feedin_kwh:.2f} | Speicher Ladung: {
                speicher_ladung_kwh:.2f} | Nutzung: {
                    speicher_nutzung_kwh:.2f} | Überschuss: {
                        speicher_ueberschuss_kwh:.2f}")
    print("DEBUG PAGE3 -> Berechnete Geldwerte:")
    print(
        f"  Direkt: {
            val_direct_money:.2f} € | Einspeisung: {
            val_feedin_money:.2f} € | Steuervorteile: {
                val_steuerliche_vorteile:.2f} €")
    print(
        f"  FORMEL Einspeisung: {
            feedin_kwh:.2f} kWh × {
            eeg_eur_per_kwh:.4f} €/kWh = {
                val_feedin_money:.2f} €")
    print(
        f"  Speichernutzung: {
            val_speicher_nutzung_money:.2f} | Speicherüberschuss: {
            val_speicher_ueberschuss_money:.2f}")
    print(f"  GESAMT (ohne Speicher): {total_savings:.2f}")
    print(
        f"  Einkommensteuersatz: {
            einkommensteuer_satz * 100 if einkommensteuer_satz <= 1 else einkommensteuer_satz:.1f}%")
    # --- Ende Kernblock ---

    # Seite 4: Produktdetails für Modul / WR / Speicher
    # Wir versuchen, Produktdetails aus der lokalen DB zu laden (optional),
    # basierend auf den ausgewählten Modellnamen.
    get_product_by_model_name = None
    try:
        from product_db import get_product_by_model_name as _get_prod
        get_product_by_model_name = _get_prod  # type: ignore
    except Exception:
        get_product_by_model_name = None

    # Kleine Normalisierungshilfen (für Fuzzy-Matching und Schlüsselvergleiche)
    def _norm_key(s: Any) -> str:
        try:
            st = str(s).strip().lower()
            # vereinheitliche Leer-/Sonderzeichen
            st = re.sub(r"\s+", " ", st)
            return st
        except Exception:
            return ""

    def _norm_flat(s: Any) -> str:
        try:
            st = str(s).strip().lower()
            # entferne alles außer a-z0-9
            return re.sub(r"[^a-z0-9]", "", st)
        except Exception:
            return ""

    def fetch_details(model_name: str) -> dict[str, Any]:
        if not model_name or not isinstance(model_name, str):
            return {}
        if get_product_by_model_name is None:
            return {}
        try:
            data = get_product_by_model_name(model_name)
            return data or {}
        except Exception:
            return {}

    # Modul
    module_name = as_str(project_details.get(
        "selected_module_name") or "").strip()
    module_id = project_details.get("selected_module_id")
    module_details = {}
    if module_id not in (None, ""):
        # Bevorzugt per ID (robust gegen Namensabweichungen)
        try:
            from product_db import get_product_by_id as _get_prod_by_id
            md = _get_prod_by_id(int(module_id))
            if isinstance(md, dict):
                module_details = md
                module_name = as_str(md.get("model_name") or module_name)
        except Exception:
            pass
    if not module_details and module_name:
        module_details = fetch_details(module_name) or {}
    # Alternativ: explizites Projektfeld 'module_model' als Modellname
    # versuchen
    if not module_details:
        alt_model = as_str(project_details.get("module_model") or "").strip()
        if alt_model:
            module_details = fetch_details(alt_model) or {}

    # Falls weiterhin keine Details/ID gefunden: Fuzzy-Matching über
    # Produktliste (Kategorie Modul)
    if not module_details and (
            module_name or project_details.get("module_model")):
        try:
            from product_db import get_product_by_id as _get_prod_by_id
            from product_db import list_products as _list_products
        except Exception:
            _list_products = None  # type: ignore
            _get_prod_by_id = None  # type: ignore
        if _list_products and _get_prod_by_id:
            try:
                cands = []
                if module_name:
                    cands.append(str(module_name))
                mm_pd = as_str(project_details.get(
                    "module_model") or "").strip()
                if mm_pd:
                    cands.append(mm_pd)
                # ggf. vorhandene DB-Infos
                if module_details.get("model_name"):
                    cands.append(as_str(module_details.get("model_name")))
                if module_details.get(
                        "brand") and module_details.get("model_name"):
                    cands.append(
                        f"{module_details.get('brand')} {module_details.get('model_name')}")
                cands_norm = {_norm_flat(c): c for c in cands if c}
                prods = _list_products(
                    category="Modul") or _list_products() or []
                best_id = None
                for p in prods:
                    mn = as_str(p.get("model_name") or "")
                    br = as_str(p.get("brand") or "")
                    alts = [mn, f"{br} {mn}".strip()]
                    alts_norm = [_norm_flat(x) for x in alts if x]
                    if any(an in cands_norm for an in alts_norm):
                        best_id = int(p.get("id"))
                        break
                # wenn nichts exakt passt: enthalte/substring-Test
                if not best_id and prods and cands_norm:
                    cand_keys = list(cands_norm.keys())
                    for p in prods:
                        mn = as_str(p.get("model_name") or "")
                        br = as_str(p.get("brand") or "")
                        alt = _norm_flat(f"{br} {mn}".strip())
                        if any(k and k in alt for k in cand_keys):
                            best_id = int(p.get("id"))
                            break
                if best_id:
                    try:
                        md = _get_prod_by_id(int(best_id)) or {}
                        if md:
                            module_details = md
                            module_name = as_str(
                                md.get("model_name") or module_name)
                    except Exception:
                        pass
            except Exception:
                pass
    # Überschrift: "PHOTOVOLTAIK MODULE – <Anzahl> Stück" (immer anzeigen)
    try:
        mod_qty = int(float(project_details.get("module_quantity") or 0))
    except Exception:
        mod_qty = 0

    if mod_qty > 0:
        result["module_section_title"] = f"PHOTOVOLTAIK MODULE – {mod_qty} Stück"
    else:
        result["module_section_title"] = "PHOTOVOLTAIK MODULE"

    # Weitere Modul-Details nur wenn verfügbar
    if module_details or module_name:
        mod_brand = as_str(module_details.get("brand")
                           or module_details.get("manufacturer") or "")
        if mod_brand:
            result["module_manufacturer"] = mod_brand
        mod_model = as_str(module_details.get("model_name") or module_name)
        if mod_model:
            # Verwende model_name direkt (Filter entfernt)
            result["module_model"] = mod_model
        # Direkte Overrides aus project_details (falls DB nicht gepflegt ist)
        ov_brand = as_str(project_details.get(
            "module_manufacturer") or "").strip()
        if ov_brand:
            result["module_manufacturer"] = ov_brand
        ov_model = as_str(project_details.get("module_model") or "").strip()
        if ov_model:
            result["module_model"] = ov_model

        # FALLBACK: Hersteller-Name aus Produktnamen extrahieren wenn
        # module_details leer
        if not result.get("module_manufacturer") and module_name:
            # Extrahiere ersten Teil des Produktnamens als Hersteller
            first_word = module_name.split()[0] if module_name.split() else ""
            if first_word:
                result["module_manufacturer"] = first_word
        mod_wp = module_details.get("capacity_w") or project_details.get(
            "selected_module_capacity_w")
        if mod_wp is not None:
            try:
                result["module_power_wp"] = fmt_number(float(mod_wp), 0, "Wp")
                # Neue Detailzeile: Leistung pro PV-Modul als "xxx Watt"
                result["module_power_per_panel_watt"] = fmt_number(
                    float(mod_wp), 0, "Watt")
            except Exception:
                result["module_power_wp"] = as_str(mod_wp)
        mod_warranty_years = module_details.get("warranty_years")
        if mod_warranty_years is not None:
            try:
                result["module_warranty_years"] = fmt_number(
                    float(mod_warranty_years), 0, "Jahre")
            except Exception:
                result["module_warranty_years"] = as_str(mod_warranty_years)
        # Leistungsgarantie (z. B. "30 Jahre / 87%") – falls Felder existieren
        perf_years = module_details.get("performance_warranty_years")
        perf_pct = module_details.get(
            "performance_warranty_percent") or module_details.get("efficiency_percent_end")
        if perf_years is not None and perf_pct is not None:
            try:
                years_str = fmt_number(float(perf_years), 0, "Jahre")
            except Exception:
                years_str = as_str(perf_years)
            try:
                pct_str = fmt_number(float(perf_pct), 0, "%")
            except Exception:
                pct_str = as_str(perf_pct)
            result["module_performance_warranty"] = f"{years_str} / {pct_str}"
            # Kombinierter Garantietext falls Produktgarantie bekannt
            prod_warranty_years = module_details.get("warranty_years")
            try:
                prod_txt = fmt_number(
                    float(prod_warranty_years),
                    0,
                    "Jahre Produktgarantie") if prod_warranty_years is not None else ""
            except Exception:
                prod_txt = f"{
                    as_str(prod_warranty_years)} Jahre Produktgarantie" if prod_warranty_years is not None else ""
            if prod_txt:
                result["module_guarantee_combined"] = f"{prod_txt} | {years_str} Leistungsgarantie"
        # Zusätzliche Modul-Detailfelder: STRICT MODE – nur exakte DB-Spalten verwenden
        # PV-Zellentechnologie / Modulaufbau / Solarzellen / Version (keine
        # Synonyme, kein Raten)
        for out_key, src_key in [
            ("module_cell_technology", "cell_technology"),
            ("module_structure", "module_structure"),
            ("module_cell_type", "cell_type"),
            ("module_version", "version"),
        ]:
            val = module_details.get(src_key)
            if val not in (None, ""):
                result[out_key] = as_str(val)
                print(
                    f"DEBUG: Set {out_key} = {val} from module_details.{src_key}")
            else:
                print(
                    f"DEBUG: {out_key} not found in module_details.{src_key} (val={val})")

        # DEBUG: Zeige verfügbare Felder für alle Hersteller (nicht nur
        # Solarfabrik)
        if module_details:
            print(
                f"DEBUG: module_details keys for {module_name}: {
                    list(
                        module_details.keys())}")
            non_empty_fields = {
                k: v for k, v in module_details.items() if v not in (None, "")}
            if non_empty_fields:
                print(f"DEBUG: Non-empty fields: {non_empty_fields}")
            else:
                print("DEBUG: No non-empty fields found in module_details")
        else:
            print(f"DEBUG: No module_details found for {module_name}")

        # Erweiterung: behutsame Synonym-Suche in den direkten DB-Feldern (ohne
        # Fuzzy, nur gängige Aliase)
        synonyms_map_db: dict[str,
                              list] = {"module_cell_technology": ["technology",
                                                                  "celltech",
                                                                  "pv_cell_technology",
                                                                  "pvcelltechnology",
                                                                  "zelltechnologie",
                                                                  "pv-zellentechnologie",
                                                                  "pv zellentechnologie",
                                                                  "PV-Zellentechnologie",
                                                                  "PV Zellentechnologie",
                                                                  "n-type",
                                                                  "p-type",
                                                                  ],
                                       "module_structure": ["structure",
                                                            "module_build",
                                                            "aufbau",
                                                            "modulaufbau",
                                                            "Modulaufbau",
                                                            "glas_typ",
                                                            "glasstruktur",
                                                            "frame",
                                                            "bauweise",
                                                            "glas-glas",
                                                            "glas folie",
                                                            ],
                                       "module_cell_type": ["solar_cells",
                                                            "cells",
                                                            "solar_cell_type",
                                                            "zelltyp",
                                                            "Solarzellen",
                                                            "cellcount",
                                                            "cell_count",
                                                            "mono",
                                                            "monokristallin",
                                                            "polykristallin",
                                                            "halfcut",
                                                            ],
                                       "module_version": ["module_version",
                                                          "variant",
                                                          "ausfuehrung",
                                                          "ausführung",
                                                          "modulversion",
                                                          "Version",
                                                          "version_label",
                                                          "black",
                                                          "fullblack",
                                                          "allblack",
                                                          ],
                                       }
        for out_k, alt_keys in synonyms_map_db.items():
            if not result.get(out_k):
                for ak in alt_keys:
                    v = module_details.get(ak)
                    if v not in (None, ""):
                        result[out_k] = as_str(v)
                        break

        # Optionaler Zusatz: falls obige Felder leer sind, nutze flexible
        # Attribute-Tabelle mit robustem Key-Matching
        try:
            if not all(
                result.get(k) for k in (
                    "module_cell_technology",
                    "module_structure",
                    "module_cell_type",
                    "module_version")):
                from database import (
                    load_admin_setting as _load_admin_setting,  # optional
                )
                from product_attributes import get_attribute_value as _get_attr
                from product_attributes import list_attributes as _list_attrs
                from product_db import get_product_id_by_model_name as _get_pid
                pid = None
                # Nutze bevorzugt die ausgewählte ID
                if module_id not in (None, ""):
                    try:
                        pid = int(module_id)
                    except Exception:
                        pid = None
                # Fallback: ID über Modellnamen ermitteln
                if not pid:
                    if 'mod_model' in locals() and mod_model:
                        pid = _get_pid(mod_model)
                    if not pid and module_name:
                        pid = _get_pid(module_name)
                    # Zusätzlich: explizites Projektfeld 'module_model'
                    # berücksichtigen
                    if not pid:
                        mm_pd = as_str(project_details.get(
                            "module_model") or "").strip()
                        if mm_pd:
                            pid = _get_pid(mm_pd)
                # Wenn noch keine ID: versuche Fuzzy wie oben
                if not pid and module_details.get("id"):
                    try:
                        pid = int(module_details.get("id"))
                    except Exception:
                        pid = None
                if pid:
                    # Admin-Alias-Map laden und reverse (kanonisch ->
                    # Aliasliste) normalisiert aufbauen
                    alias_map = None
                    try:
                        alias_map = _load_admin_setting(
                            "module_pdf_alias_map", {}) or {}
                    except Exception:
                        alias_map = None
                    rev: dict[str, list] = {}
                    if alias_map:
                        for src_key, dst_key in alias_map.items():
                            if not src_key or not dst_key:
                                continue
                            can = _norm_key(dst_key)
                            rev.setdefault(can, []).append(
                                str(src_key).strip())
                    # Alle Attribute einmalig listen für normalisierte Suche
                    attrs = []
                    try:
                        attrs = _list_attrs(int(pid)) or []
                    except Exception:
                        attrs = []
                    attrs_norm_map: dict[str, Any] = {}
                    for a in attrs:
                        k = _norm_key(a.get("attribute_key"))
                        if k and k not in attrs_norm_map:
                            attrs_norm_map[k] = a.get("attribute_value")

                    def _resolve_attr(canonical: str, syns: list[str]) -> str:
                        # 1) exakt über get_attribute_value
                        val = _get_attr(int(pid), canonical)
                        if val not in (None, ""):
                            return str(val)
                        # 2) Synonyme direkt
                        for s in syns:
                            val2 = _get_attr(int(pid), s)
                            if val2 not in (None, ""):
                                return str(val2)
                        # 3) Admin-Aliase (reverse)
                        can_n = _norm_key(canonical)
                        for alias_key in rev.get(can_n, []) or []:
                            val3 = _get_attr(int(pid), alias_key)
                            if val3 not in (None, ""):
                                return str(val3)
                        # 4) Normalisierte Suche in allen Attributen
                        cand_keys = [_norm_key(canonical)] + \
                            [_norm_key(x) for x in syns]
                        # Admin-Aliase auch normalisiert ergänzen
                        for alias_key in rev.get(can_n, []) or []:
                            cand_keys.append(_norm_key(alias_key))
                        for ck in cand_keys:
                            if ck in attrs_norm_map and attrs_norm_map[ck] not in (
                                    None, ""):
                                return str(attrs_norm_map[ck])
                        return ""

                    # Synonyme je Ausgabefeld
                    synonyms_map_attr: dict[str,
                                            list] = {"module_cell_technology": ["technology",
                                                                                "pv_cell_technology",
                                                                                "zelltechnologie",
                                                                                "pv zellentechnologie",
                                                                                "pv-zellentechnologie",
                                                                                "n-type",
                                                                                "p-type",
                                                                                "topcon",
                                                                                "heterojunction",
                                                                                "perc"],
                                                     "module_structure": ["structure",
                                                                          "module_build",
                                                                          "aufbau",
                                                                          "modulaufbau",
                                                                          "modulaufbau",
                                                                          "glas-glas",
                                                                          "glas folie",
                                                                          "frame"],
                                                     "module_cell_type": ["solar_cells",
                                                                          "cells",
                                                                          "solar_cell_type",
                                                                          "zelltyp",
                                                                          "solarzellen",
                                                                          "cellcount",
                                                                          "cell_count",
                                                                          "mono",
                                                                          "monokristallin",
                                                                          "polykristallin",
                                                                          "halfcut"],
                                                     "module_version": ["module_version",
                                                                        "variant",
                                                                        "ausfuehrung",
                                                                        "ausführung",
                                                                        "modulversion",
                                                                        "version",
                                                                        "version_label",
                                                                        "black",
                                                                        "fullblack",
                                                                        "allblack"],
                                                     "module_guarantee_combined": ["garantie",
                                                                                   "garantietext",
                                                                                   "module_warranty_text",
                                                                                   "garantie_text",
                                                                                   "warranty_text"],
                                                     }
                    canon_map = {
                        "module_cell_technology": "cell_technology",
                        "module_structure": "module_structure",
                        "module_cell_type": "cell_type",
                        "module_version": "version",
                        "module_guarantee_combined": "module_warranty_text",
                    }
                    for out_k, can_k in canon_map.items():
                        if result.get(out_k):
                            continue
                        val = _resolve_attr(
                            can_k, synonyms_map_attr.get(out_k, []))
                        if val:
                            result[out_k] = val
        except Exception:
            pass

        # Fallback/Overrides: Erlaube, diese Felder direkt über project_details
        # zu setzen
        for out_key in [
            "module_cell_technology",
            "module_structure",
            "module_cell_type",
            "module_version",
        ]:
            ov = project_details.get(out_key)
            if ov not in (None, "") and not result.get(out_key):
                result[out_key] = as_str(ov)

        # Keine Synonym-/Heuristik-Ratespielchen: nur explizite Felder
        # verwenden

        # Garantie-Text explizit überschreibbar (z. B. "30 Jahre
        # Produktgarantie")
        ov_combined = project_details.get("module_guarantee_combined")
        if ov_combined not in (None, ""):
            result["module_guarantee_combined"] = as_str(ov_combined)
        else:
            # Alternativ nur Produktgarantie-Jahre aus project_details
            ov_years = project_details.get("module_product_warranty_years")
            try:
                if ov_years not in (None, "") and float(ov_years) >= 0:
                    result["module_guarantee_combined"] = fmt_number(
                        float(ov_years), 0, "Jahre Produktgarantie")
            except Exception:
                pass
        # Falls DB einen kombinierten Garantietext anbietet (exakte Spalte)
        if not result.get("module_guarantee_combined"):
            db_gw = module_details.get("module_warranty_text")
            if db_gw not in (None, ""):
                result["module_guarantee_combined"] = as_str(db_gw)
        # Garantietext: ausschließlich 'module_guarantee_combined' aus
        # project_details oder DB-Produktgarantie

        # Produktbild (Base64), falls in DB vorhanden
        img_b64 = as_str(module_details.get("image_base64") or "").strip()
        if img_b64:
            result["module_image_b64"] = img_b64
        # Overrides aus project_details
        if project_details.get("module_image_b64"):
            result["module_image_b64"] = as_str(
                project_details.get("module_image_b64"))

    # Unbedingte PV-Overrides (auch wenn kein selected_module_name gesetzt ist)
    ov_mod_brand = as_str(project_details.get(
        "module_manufacturer") or "").strip()
    if ov_mod_brand:
        result["module_manufacturer"] = ov_mod_brand
    ov_mod_model = as_str(project_details.get("module_model") or "").strip()
    if ov_mod_model:
        result["module_model"] = ov_mod_model
    # Leistung pro PV-Modul aus selected_module_capacity_w ableiten
    if not result.get("module_power_per_panel_watt"):
        cap_w = project_details.get("selected_module_capacity_w")
        pf = parse_float(cap_w)
        if pf and pf > 0:
            result["module_power_per_panel_watt"] = fmt_number(pf, 0, "Watt")
    # Weitere Felder direkt aus project_details übernehmen (override) –
    # neutrale Tokens schützen DB-Werte
    neutral_tokens = {"siehe produktdatenblatt",
                      "-", "n/a", "na", "keine angabe"}
    for k in (
        "module_cell_technology",
        "module_structure",
        "module_cell_type",
        "module_version",
            "module_guarantee_combined"):
        v = project_details.get(k)
        if v in (None, ""):
            continue
        v_str = as_str(v).strip()
        if k == "module_guarantee_combined":
            result[k] = v_str
        else:
            if (not result.get(k)) or (v_str.lower() not in neutral_tokens):
                result[k] = v_str

    # Garantiefallback nur, wenn leer
    if not result.get("module_guarantee_combined"):
        result["module_guarantee_combined"] = "siehe Produktdatenblatt"

    # Letzte Fallback Defaults für Anzeige (verhindert 'None')
    fallback_display = {
        "module_cell_technology": "k.A.",
        "module_structure": "k.A.",
        "module_cell_type": "k.A.",
        "module_version": "k.A.",
    }
    for fk, fv in fallback_display.items():
        if not result.get(fk):
            result[fk] = fv
            print(
                f"DEBUG: Applied fallback {fk} = {fv} (original value was {
                    result.get(fk)!r})")

    # DEBUG: Modul-Seite4 Attribute (temporär, zur Validierung der neuen
    # Mappings)
    try:
        debug_keys = [
            "module_manufacturer",
            "module_model",
            "module_power_per_panel_watt",
            "module_cell_technology",
            "module_structure",
            "module_cell_type",
            "module_version",
            "module_guarantee_combined"]
        print("DEBUG SEITE4 MODULE ATTRIBUTES:")
        print(
            f"  selected_module_name = {
                project_details.get('selected_module_name')!r}")
        print(
            f"  module_details keys = {
                list(
                    module_details.keys()) if module_details else 'None'}")
        for dk in debug_keys:
            print(f"  {dk} = {result.get(dk)!r}")

        # Spezielle Debug-Ausgabe für Solarfabrik
        if 'solarfabrik' in str(
            project_details.get(
                'selected_module_name',
                '')).lower():
            print("  *** SOLARFABRIK DETECTED - EXTENDED DEBUG ***")
            print(f"  module_details = {module_details}")
            print(
                f"  module_details.cell_technology = {
                    module_details.get('cell_technology')}")
            print(
                f"  module_details.module_structure = {
                    module_details.get('module_structure')}")
            print(
                f"  module_details.cell_type = {
                    module_details.get('cell_type')}")
            print(
                f"  module_details.version = {module_details.get('version')}")
    except Exception:
        pass

    # Wechselrichter
    inverter_name = as_str(project_details.get(
        "selected_inverter_name") or "").strip()
    inverter_details = fetch_details(inverter_name) if inverter_name else {}
    if inverter_details or inverter_name:
        inv_brand = as_str(inverter_details.get("brand")
                           or inverter_details.get("manufacturer") or "")
        if inv_brand:
            result["inverter_manufacturer"] = inv_brand

        # FALLBACK: Hersteller-Name aus Produktnamen extrahieren wenn
        # inverter_details leer
        if not result.get("inverter_manufacturer") and inverter_name:
            # Extrahiere ersten Teil des Produktnamens als Hersteller
            first_word = inverter_name.split(
            )[0] if inverter_name.split() else ""
            if first_word:
                result["inverter_manufacturer"] = first_word
        # Modell | Typ (mit Menge, falls >1)
        try:
            inv_qty = int(project_details.get(
                "selected_inverter_quantity", 1) or 1)
        except Exception:
            inv_qty = 1
        # Verwende inverter_name direkt (Filter entfernt)
        result["inverter_model"] = (f"{inv_qty}x {inverter_name}" if inv_qty >
                                    1 and inverter_name else inverter_name)
        inv_eff = inverter_details.get("efficiency_percent")
        if inv_eff is not None:
            try:
                result["inverter_max_efficiency_percent"] = fmt_number(
                    float(inv_eff), 0, "%")
            except Exception:
                result["inverter_max_efficiency_percent"] = as_str(inv_eff)
        inv_warranty_years = inverter_details.get("warranty_years")
        if inv_warranty_years is not None:
            try:
                result["inverter_warranty_years"] = fmt_number(
                    float(inv_warranty_years), 0, "Jahre")
            except Exception:
                result["inverter_warranty_years"] = as_str(inv_warranty_years)

        # Leistung in W
        try:
            # Unterstütze sowohl kW- als auch W-Quellen und verhindere
            # Doppel-Multiplikation
            cand = [
                ("w", inverter_details.get("power_watt") or inverter_details.get(
                    "rated_power_w") or inverter_details.get("power_w")),
                ("kw", inverter_details.get("power_kw")),
                ("w", project_details.get("selected_inverter_power_w")
                 or project_details.get("inverter_power_w")),
                ("kw", project_details.get("selected_inverter_power_kw")
                 or project_details.get("inverter_power_kw")),
            ]
            watt_val = None
            for unit, v in cand:
                pf = parse_float(v)
                if pf and pf > 0:
                    if unit == "kw":
                        # Plausibilitätsprüfung: Wechselrichter sollten zwischen 1 kW und 100 kW haben
                        # Werte > 100 sind wahrscheinlich bereits in Watt
                        # angegeben
                        if pf > 100:
                            watt_val = pf  # Bereits in Watt
                        else:
                            watt_val = pf * 1000.0  # kW zu Watt konvertieren
                    else:
                        watt_val = pf
                    break
            # Fallback-Heuristik, falls Quelle unklar: Werte > 1000 als W
            # interpretieren, sonst kW
            if watt_val is None:
                v = inverter_details.get(
                    "power") or project_details.get("inverter_power")
                pf = parse_float(v)
                if pf and pf > 0:
                    watt_val = pf if pf >= 1000 else pf * 1000.0
            # Zusätzliche Plausibilisierung: Falls immer noch unrealistisch groß und eine kW-Gesamtleistung existiert,
            # bevorzuge diese.
            try:
                if watt_val is not None and watt_val > 1000:  # >100 kW ist unrealistisch für einzelne WR
                    # Versuche aus der Gesamtleistung zu korrigieren
                    inv_total_kw = (
                        project_details.get("selected_inverter_power_kw")
                        or project_details.get("inverter_power_kw")
                        or project_details.get("selected_inverter_power_kw_single")
                    )
                    total_pf = parse_float(inv_total_kw)
                    if total_pf and total_pf > 0 and total_pf <= 1000:
                        watt_val = total_pf * 1000.0
            except Exception:
                pass
            if watt_val is not None:
                # Format: Tausendertrennzeichen (deutsch), keine
                # Nachkommastellen: z.B. 6.000 W
                try:
                    watt_int = int(round(watt_val))
                except Exception:
                    watt_int = watt_val
                try:
                    result["inverter_power_watt"] = f"{watt_int:,.0f}".replace(
                        ",", ".") + " W"
                except Exception:
                    # Fallback auf vorhandenes Formatierungs-Hilfsmittel
                    result["inverter_power_watt"] = fmt_number(
                        watt_val, 0, "W")
        except Exception:
            pass

        # Typ Wechselrichter (Heuristik)
        name_l = inverter_name.lower()
        if "hybrid" in name_l:
            result["inverter_type"] = "Hybrid-Wechselrichter"
        elif "string" in name_l:
            result["inverter_type"] = "String-Wechselrichter"
        else:
            try:
                has_storage = bool(project_details.get("selected_storage_name") or project_details.get(
                    "battery_capacity_kwh") or analysis_results.get("battery_capacity_kwh"))
            except Exception:
                has_storage = False
            result["inverter_type"] = "Hybrid-Wechselrichter" if has_storage else "String-Wechselrichter"

        # Anzahl Phasen (Heuristik über Leistung)
        try:
            pkw = None
            if isinstance(inverter_details.get("power_kw"), (int, float)):
                pkw = float(inverter_details.get("power_kw"))
            elif project_details.get("selected_inverter_power_kw") not in (None, ""):
                pkw = float(project_details.get("selected_inverter_power_kw"))
            if pkw is not None:
                result["inverter_phases"] = "Dreiphasig" if pkw >= 4.6 else "Einphasig"
        except Exception:
            pass

        # Feature-Defaults, falls nicht aus DB vorhanden
        if not result.get("inverter_shading_management"):
            result["inverter_shading_management"] = "ja, vorhanden"
        if not result.get("inverter_backup_capable"):
            result["inverter_backup_capable"] = "ja, wenn Hauselektrik kompatibel"
        if not result.get("inverter_smart_home_integration"):
            result["inverter_smart_home_integration"] = "ja"
        if not result.get("inverter_guarantee_text"):
            result["inverter_guarantee_text"] = "siehe Produktdatenblatt"

        # Zusätzliche Werte aus der flexiblen Attribute-Tabelle lesen und
        # Defaults überschreiben
        try:
            from product_attributes import get_attribute_value as _get_attr
            from product_db import get_product_id_by_model_name as _get_pid_inv
        except Exception:
            _get_pid_inv = None  # type: ignore
            _get_attr = None  # type: ignore

        def _norm_yes_no(val: Any) -> str:
            if val is None:
                return ""
            s = str(val).strip()
            l = s.lower()
            if l in {"true", "wahr", "ja", "yes", "y", "1"}:
                return "ja"
            if l in {"false", "falsch", "nein", "no", "n", "0"}:
                return "nein"
            return s

        def _get_attr_any(pid: Any, keys: list[str]) -> str:
            if not _get_attr or not pid:
                return ""
            for k in keys:
                try:
                    v = _get_attr(int(pid), k)
                    if v not in (None, ""):
                        return str(v)
                except Exception:
                    continue
            return ""

        inv_id = project_details.get("selected_inverter_id")
        if not inv_id and _get_pid_inv and inverter_name:
            try:
                inv_id = _get_pid_inv(inverter_name)
            except Exception:
                inv_id = None

        if inv_id:
            # Typ (falls im Attribut gepflegt)
            aval = _get_attr_any(
                inv_id, [
                    "inverter_type", "wr_typ", "typ wechselrichter", "typ", "inverter_typ"])
            if aval:
                result["inverter_type"] = aval
            # Phasen
            aval = _get_attr_any(
                inv_id, ["inverter_phases", "phasen", "phases", "wr_phasen"])
            if aval:
                al = aval.lower()
                if any(t in al for t in ["3", "drei", "dreiphas"]):
                    result["inverter_phases"] = "Dreiphasig"
                elif any(t in al for t in ["1", "einphas"]):
                    result["inverter_phases"] = "Einphasig"
                else:
                    result["inverter_phases"] = aval
            # Schattenmanagement
            aval = _get_attr_any(inv_id,
                                 ["inverter_shading_management",
                                  "shade_management",
                                  "shading_management",
                                  "schattenmanagement"])
            if aval:
                result["inverter_shading_management"] = _norm_yes_no(aval)
                # Falls hier fälschlich Phasenangabe geliefert wurde, umhängen
                al = str(aval).lower()
                if any(
                    t in al for t in [
                        "dreiphas",
                        "drei",
                        "einphas",
                        "1phas",
                        "3phas"]):
                    # Setze Phasen entsprechend
                    if any(t in al for t in ["dreiphas", "drei", "3"]):
                        result["inverter_phases"] = "Dreiphasig"
                    elif any(t in al for t in ["einphas", "1"]):
                        result["inverter_phases"] = "Einphasig"
                    # und normalisiere Schattenmanagement zurück auf 'ja,
                    # vorhanden'
                    result["inverter_shading_management"] = "ja, vorhanden"
            # Notstrom/Backup
            aval = _get_attr_any(inv_id,
                                 ["inverter_backup_capable",
                                  "backup",
                                  "notstrom",
                                  "notstromfaehig",
                                  "ersatzstrom"])
            if aval:
                result["inverter_backup_capable"] = _norm_yes_no(aval)
            # Smart Home
            aval = _get_attr_any(
                inv_id, [
                    "inverter_smart_home_integration", "smart_home", "smarthome", "smart home"])
            if aval:
                result["inverter_smart_home_integration"] = _norm_yes_no(aval)
            # Garantie-Text
            aval = _get_attr_any(
                inv_id, [
                    "inverter_guarantee_text", "garantie", "garantie_text", "warranty_text"])
            if aval:
                result["inverter_guarantee_text"] = aval

        # Produktbild (Base64)
        img_b64 = as_str(inverter_details.get("image_base64") or "").strip()
        if img_b64:
            result["inverter_image_b64"] = img_b64
        # Overrides
        if project_details.get("inverter_image_b64"):
            result["inverter_image_b64"] = as_str(
                project_details.get("inverter_image_b64"))

    # Speicher
    storage_name = as_str(project_details.get(
        "selected_storage_name") or "").strip()
    storage_details = fetch_details(storage_name) if storage_name else {}
    if storage_details or storage_name or project_details.get(
            "include_storage"):
        sto_brand = as_str(storage_details.get("brand")
                           or storage_details.get("manufacturer") or "")
        if sto_brand:
            result["storage_manufacturer"] = sto_brand

        # FALLBACK: Hersteller-Name aus Produktnamen extrahieren wenn
        # storage_details leer
        if not result.get("storage_manufacturer") and storage_name:
            # Extrahiere ersten Teil des Produktnamens als Hersteller
            first_word = storage_name.split(
            )[0] if storage_name.split() else ""
            if first_word:
                result["storage_manufacturer"] = first_word
        sto_model = as_str(storage_details.get("model_name") or storage_name)
        if sto_model:
            # Verwende storage model_name direkt (Filter entfernt)
            result["storage_model"] = sto_model
        # Kapazität (kWh): wie in der Technik-Auswahl zuerst den UI-Wert nehmen,
        # dann DB (bevorzugt storage_power_kw als kWh), dann weitere Felder
        # Wie oben: erst DB-Kapazität anzeigen, dann UI-Wert
        cand_sto = [
            # App-Konvention: häufig als kWh gepflegt
            storage_details.get("storage_power_kw"),
            storage_details.get("capacity_kwh"),
            storage_details.get("usable_capacity_kwh"),
            storage_details.get("nominal_capacity_kwh"),
            project_details.get("selected_storage_storage_power_kw"),
            project_details.get("selected_storage_capacity_kwh"),
            project_details.get("battery_capacity_kwh"),
        ]
        sto_kwh = None
        for c in cand_sto:
            v = parse_float(c)
            if v and v > 0:
                sto_kwh = v
                break
        if sto_kwh is not None:
            try:
                val = float(sto_kwh)
                # Nur setzen, wenn noch nicht vorbelegt
                if not result.get("storage_capacity_kwh"):
                    # 2 Nachkommastellen (z. B. 15,00 kWh) – ohne Sternchen
                    result["storage_capacity_kwh"] = fmt_number(val, 2, "kWh")
                # battery_capacity_kwh parallel konsistent halten, falls noch
                # leer
                if not result.get("battery_capacity_kwh"):
                    result["battery_capacity_kwh"] = fmt_number(val, 2, "kWh")
                # Größe des Batteriespeichers ohne Sternchen anzeigen
                result["storage_size_battery_kwh_star"] = fmt_number(
                    val, 2, "kWh")
                # Erweiterungsmodul und maximale Größe aus DB/Projekt/Analyse,
                # ohne Schätz-Fallbacks
                ext_mod = parse_float(
                    storage_details.get("extension_module_kwh")
                    or storage_details.get("module_size_kwh")
                    or project_details.get("extension_module_kwh")
                    or project_details.get("storage_extension_module_size_kwh")
                    or analysis_results.get("storage_extension_module_kwh")
                )
                max_size = parse_float(
                    storage_details.get("max_capacity_kwh")
                    or storage_details.get("max_size_kwh")
                    or project_details.get("max_capacity_kwh")
                    or project_details.get("storage_max_size_kwh")
                    or analysis_results.get("storage_max_capacity_kwh")
                )
                if ext_mod and ext_mod > 0:
                    result["storage_extension_module_size_kwh"] = fmt_number(
                        ext_mod, 2, "kWh")
                # Wenn kein valider DB/Projekt/Analyse-Wert vorhanden ist, leer
                # lassen (kein falscher Fallback)
                if max_size and max_size > 0:
                    result["storage_max_size_kwh"] = fmt_number(
                        max_size, 2, "kWh")
            except Exception:
                if not result.get("storage_capacity_kwh"):
                    result["storage_capacity_kwh"] = as_str(sto_kwh)
        # Leistung (kW)
        sto_kw = storage_details.get("power_kw") or storage_details.get(
            "storage_power_kw") or project_details.get("selected_storage_power_kw")
        if sto_kw is not None:
            try:
                # 1 Nachkommastelle wie Beispiel (15,0 kW)
                result["storage_power_kw"] = fmt_number(float(sto_kw), 1, "kW")
            except Exception:
                result["storage_power_kw"] = as_str(sto_kw)
        # Entladetiefe (DoD %)
        dod_pct = storage_details.get(
            "dod_percent") or analysis_results.get("storage_dod_percent")
        if dod_pct is not None:
            try:
                result["storage_dod_percent"] = fmt_number(
                    float(dod_pct), 0, "%")
            except Exception:
                result["storage_dod_percent"] = as_str(dod_pct)
        # Zyklen (beibehalten für Alt-Layouts)
        cycles = storage_details.get(
            "max_cycles") or analysis_results.get("storage_cycles")
        if cycles is not None:
            try:
                result["storage_cycles"] = f"{int(float(cycles))} cycles"
            except Exception:
                result["storage_cycles"] = f"{as_str(cycles)} cycles"

        # Neue Speicher-Felder füllen (generisch)
        if not result.get("storage_cell_technology"):
            # Versuch aus DB-Feldern, sonst Standardtext gemäß Kundenwunsch
            for k in (
                "cell_technology",
                "battery_cell_technology",
                "chemistry",
                    "cell_type"):
                val = storage_details.get(k)
                if val:
                    chem = as_str(val)
                    # Korrigiere häufige Tippfehler-Varianten auf LiFePO4
                    chem = chem.replace("LiFePO5", "LiFePO4").replace(
                        "Lifepo5", "LiFePO4").replace("LiFePo5", "LiFePO4")
                    result["storage_cell_technology"] = chem
                    break
            if not result["storage_cell_technology"]:
                result["storage_cell_technology"] = "Lithium-Eisenphosphat (LiFePO4)"

        # Reserve/Notstrom und Outdoor-Fähigkeit – Defaults, falls nicht aus DB
        # bekannt
        if not result.get("storage_backup_text"):
            result["storage_backup_text"] = "ja, dreiphasig"
        if not result.get("storage_outdoor_capability"):
            result["storage_outdoor_capability"] = "Outdoorfähig"
        if not result.get("storage_warranty_text"):
            result["storage_warranty_text"] = "siehe Produktdatenblatt"

        # Produktbild (Base64)
        img_b64 = as_str(storage_details.get("image_base64") or "").strip()
        if img_b64:
            result["storage_image_b64"] = img_b64
        # Overrides
        if project_details.get("storage_image_b64"):
            result["storage_image_b64"] = as_str(
                project_details.get("storage_image_b64"))

        # Speicher: erweiterte Felder aus Attribute-Tabelle (Erweiterungsmodul,
        # max. Größe, Outdoor, Notstrom, Garantie)
        try:
            from product_attributes import get_attribute_value as _get_attr
            from product_db import get_product_id_by_model_name as _get_pid_sto
        except Exception:
            _get_pid_sto = None  # type: ignore
            _get_attr = None  # type: ignore

        def _get_attr_any_sto(pid: Any, keys: list[str]) -> str:
            if not _get_attr or not pid:
                return ""
            for k in keys:
                try:
                    v = _get_attr(int(pid), k)
                    if v not in (None, ""):
                        return str(v)
                except Exception:
                    continue
            return ""

        sto_id = project_details.get("selected_storage_id")
        if not sto_id and _get_pid_sto and storage_name:
            try:
                sto_id = _get_pid_sto(storage_name)
            except Exception:
                sto_id = None

        if sto_id:
            # Erweiterungsmodul-Größe
            aval = _get_attr_any_sto(sto_id,
                                     ["storage_extension_module_size_kwh",
                                      "extension_module_kwh",
                                      "expansion_module",
                                      "erweiterungsmodul",
                                      "erweiterungsmodul_kwh"])
            pf = parse_float(aval)
            if pf and pf > 0:
                result["storage_extension_module_size_kwh"] = fmt_number(
                    pf, 2, "kWh")
            # Maximale Größe
            aval = _get_attr_any_sto(sto_id,
                                     ["storage_max_size_kwh",
                                      "max_capacity_kwh",
                                      "max_size_kwh",
                                      "max_speichergroesse",
                                      "max_speichergröße",
                                      "max_storage_size",
                                      "max. speichergröße"])
            pf = parse_float(aval)
            if pf and pf > 0:
                result["storage_max_size_kwh"] = fmt_number(pf, 2, "kWh")
            # Notstrom/Reserve
            aval = _get_attr_any_sto(
                sto_id, [
                    "storage_backup_text", "backup", "notstrom", "ersatzstrom", "reserve"])
            if aval:
                result["storage_backup_text"] = str(aval)
            # Outdoorfähigkeit
            aval = _get_attr_any_sto(
                sto_id, [
                    "storage_outdoor_capability", "outdoor", "outdoorfaehig", "outdoor_fähig"])
            if aval:
                result["storage_outdoor_capability"] = str(aval)
            # Garantie-Text
            aval = _get_attr_any_sto(
                sto_id, [
                    "storage_warranty_text", "garantie_text", "warranty_text", "garantie"])
            if aval:
                result["storage_warranty_text"] = str(aval)
            # DoD Prozent (falls als Attribut gepflegt)
            if not result.get("storage_dod_percent"):
                aval = _get_attr_any_sto(
                    sto_id, ["dod_percent", "dod", "entladetiefe"])
                pf = parse_float(aval)
                if pf and pf > 0:
                    result["storage_dod_percent"] = fmt_number(pf, 0, "%")
            # Zyklen (Attribut)
            if not result.get("storage_cycles"):
                aval = _get_attr_any_sto(
                    sto_id, ["max_cycles", "zyklen", "cycle_count"])
                try:
                    if aval:
                        result["storage_cycles"] = f"{int(float(parse_float(aval) or 0))} cycles" if parse_float(
                            aval) else str(aval)
                except Exception:
                    pass

        # Wenn Speicher ausgewählt ist, aber Erweiterungsmodul/Max-Größe leer,
        # zeige neutralen Hinweis statt leer
        try:
            if (project_details.get("include_storage") or storage_name) and not result.get(
                    "storage_extension_module_size_kwh"):
                result["storage_extension_module_size_kwh"] = "siehe Produktdatenblatt"
            if (project_details.get("include_storage")
                    or storage_name) and not result.get("storage_max_size_kwh"):
                result["storage_max_size_kwh"] = "siehe Produktdatenblatt"
        except Exception:
            pass

        # Spezifische Belegung für Huawei LUNA2000-7-S1 (exakte Wunschwerte)
        name_l = (storage_name or "").lower()
        brand_l = (sto_brand or "").lower()
        if ("huawei" in brand_l) or ("luna2000" in name_l):
            result["storage_manufacturer"] = "Huawei"
            result["storage_model"] = "LUNA2000-7-S1-7kWh Stromspeicher"
            result["storage_cell_technology"] = "Lithium-Eisenphosphat (LiFePO4)"
            # Fixwerte gemäß Vorgabe (ohne Sternchen)
            result["storage_size_battery_kwh_star"] = fmt_number(7.0, 2, "kWh")
            result["storage_extension_module_size_kwh"] = fmt_number(
                7.0, 2, "kWh")
            result["storage_max_size_kwh"] = fmt_number(21.0, 2, "kWh")
            result["storage_backup_text"] = "ja, dreiphasig"
            result["storage_outdoor_capability"] = "Outdoorfähig"
            result["storage_warranty_text"] = "siehe Produktdatenblatt"

    # Unbedingte Overrides aus project_details (Bilder/Logos), unabhängig von
    # DB-Ladung
    for k in (
        "module_image_b64",
        "inverter_image_b64",
        "storage_image_b64",
        "module_brand_logo_b64",
        "inverter_brand_logo_b64",
        "storage_brand_logo_b64",
    ):
        v = project_details.get(k)
        if v not in (None, ""):
            result[k] = as_str(v)

    # =============================================================
    # Hersteller-Namen NORMALISIERUNG (nur Anzeige, Logo-Lookup nutzt Raw)
    # =============================================================
    def _normalize_brand_display(name: str) -> str:
        """Bereinigt Herstellernamen nur für die Anzeige.
        Entfernt funktionale Suffixe, egal ob angehängt (EcoFlowWR) oder getrennt (EcoFlow WR / EcoFlow Speicher).
        """
        try:
            if not name:
                return name
            import re
            original = name.strip()
            # 1. Separator-Varianten vereinheitlichen
            cleaned = original.replace("_", " ").replace("-", " ")
            suffix_tokens = {
                "pv",
                "wr",
                "wechselrichter",
                "speicher",
                "batterie",
                "akku",
                "ess",
                "stromspeicher"}

            # 2. Token-basiertes Entfernen am Ende
            parts = [p for p in cleaned.split() if p]
            changed = False
            while parts and parts[-1].lower().strip("()[]{}.,") in suffix_tokens:
                parts.pop()
                changed = True

            candidate = " ".join(parts).strip() if parts else original

            # 3. Direkt angehängte Suffixe mehrfach entfernen (EcoFlowWRSpeicher -> EcoFlow)
            # Pattern wiederholt anwenden bis nichts mehr entfernt wird.
            attached_pattern = re.compile(
                r"^(.*?)(pv|wr|speicher|batterie|akku|ess|stromspeicher)$",
                re.IGNORECASE)
            prev = None
            while candidate and candidate != prev:
                prev = candidate
                m = attached_pattern.match(candidate)
                if m and m.group(1).strip():
                    candidate = m.group(1).strip()
                    changed = True
                else:
                    break

            # 4. Mindestlängen-/Rest-Heuristik: Verhindere zu starke Kürzung
            if changed:
                # Wenn extrem kurz oder nur generisches Fragment, fallback auf
                # original
                if len(candidate) < 3:
                    return original
                # Verhindere dass nur generische Wörter alleine bleiben
                generic_alone = {"solar", "energy", "power"}
                if candidate.lower() in generic_alone:
                    return original
            # 5. Mehrfache Spaces entfernen
            candidate = re.sub(r"\s+", " ", candidate).strip()
            return candidate or original
        except Exception:
            return name

    # Roh-Werte sichern bevor wir bereinigen (für Logo-Lookup wichtig)
    for comp_key in ("module", "inverter", "storage"):
        man_key = f"{comp_key}_manufacturer"
        if man_key in result and result.get(man_key):
            raw_key = f"{man_key}_raw"
            if raw_key not in result:  # nur einmal setzen
                result[raw_key] = result.get(man_key)
            # Anzeige bereinigen
            result[man_key] = _normalize_brand_display(
                str(result.get(man_key)))

    # =============================================================
    # Garantie-Texte GLOBAL vereinheitlichen (Kundenwunsch)
    # =============================================================
    for gk in (
        "module_guarantee_combined",
        "inverter_guarantee_text",
            "storage_warranty_text"):
        # Immer überschreiben unabhängig vom bisherigen Inhalt
        result[gk] = "siehe Produktdatenblatt"

    # DEBUG: Garantie-Override & Hersteller Raw/Display prüfen
    try:
        print("DEBUG GUARANTEE OVERRIDE:")
        print("  module_guarantee_combined=",
              result.get("module_guarantee_combined"))
        print("  inverter_guarantee_text=",
              result.get("inverter_guarantee_text"))
        print("  storage_warranty_text=", result.get("storage_warranty_text"))
        for comp_key in ("module", "inverter", "storage"):
            print(
                f"  {comp_key}_manufacturer_raw=", result.get(
                    f"{comp_key}_manufacturer_raw"), "display=", result.get(
                    f"{comp_key}_manufacturer"))
    except Exception:
        pass

    # Seite 1 – neue dynamische Felder und statische Texte nach Kundenwunsch
    # 1) Jährliche Einspeisevergütung in Euro (für Platz "Dachneigung")
    # KOMPLETT DEAKTIVIERT: Diese ganze Sektion überschreibt die korrekte
    # Seite 3 Berechnung
    r"""
    DEAKTIVIERTE SEKTION - ÜBERSCHREIBT KORREKTE BERECHNUNG
    if False and "annual_feed_in_revenue_eur" not in result:
        try:
            # Primär vorhandene Berechnung nehmen
            annual_feed_rev = (
                analysis_results.get("annual_feedin_revenue_euro")
                or analysis_results.get("annual_feed_in_revenue_year1")
            )
            # Falls nicht vorhanden oder offensichtlich inkonsistent, neu berechnen
            # Hole Netzeinspeisung (Seite 2 Wert) und ermittele EEG-Tarif erneut wie oben verwendet
            grid_feedin_raw = analysis_results.get("grid_feed_in_kwh") or result.get("grid_feed_in_kwh")
            feed_in_kwh_val = None
            if grid_feedin_raw:
                try:
                    feed_in_kwh_val = float(str(grid_feedin_raw).split()[0].replace('.', '').replace(',', '.')) if ' ' in str(grid_feedin_raw) else float(str(grid_feedin_raw).replace('.', '').replace(',', '.'))
                except Exception:
                    try:
                        feed_in_kwh_val = float(re.sub(r"[^0-9,\.]", "", str(grid_feedin_raw)).replace(',', '.'))
                    except Exception:
                        feed_in_kwh_val = None
            # EEG Tarif erneut bestimmen (gleiche Logik wie Seite3 oben)
            try:
                anlage_kwp_local = parse_float(analysis_results.get("anlage_kwp")) or 0.0
                from database import load_admin_setting as _load_tar
                fit_loc = _load_tar("feed_in_tariffs", {})
                mode_loc = project_data.get("einspeise_art", "parts")
                local_tariff = None
                for trf in fit_loc.get(mode_loc, []):
                    if trf.get("kwp_min", 0) <= anlage_kwp_local <= trf.get("kwp_max", 999):
                        local_tariff = (trf.get("ct_per_kwh", 7.86) or 7.86) / 100.0
                        break
                if local_tariff is None:
                    local_tariff = 0.068  # Fallback 6,8 ct
            except Exception:
                local_tariff = 0.068
            # Neuberechnung wenn nötig
            if feed_in_kwh_val is not None:
                calc_rev = feed_in_kwh_val * local_tariff
                if (annual_feed_rev is None) or (abs(calc_rev - float(annual_feed_rev)) > max(5.0, 0.2 * calc_rev)):
                    annual_feed_rev = calc_rev
                if annual_feed_rev is not None:
                    result["annual_feed_in_revenue_eur"] = fmt_number(float(annual_feed_rev), 2, "€")
        except Exception:
            pass
    """

    # 2) MwSt.-Betrag (19% vom finalen Angebotspreis) für Platz "Solaranlage"
    # Verwende die gleiche Logik wie für Amortisationszeit - finale Preise aus
    # Solar Calculator
    try:
        vat_amount = None

        # NEUE LOGIK: Prüfe finale Preise aus Solar Calculator zuerst
        if project_details:
            # Priorität: Preisänderungen > Provision > Basis
            if project_details.get('formatted_final_modified_vat_amount'):
                # MwSt aus Preisänderungen (bereits formatiert)
                result["vat_amount_eur"] = project_details['formatted_final_modified_vat_amount']
                print(
                    f"DEBUG: MwSt verwendet formatted_final_modified_vat_amount: {
                        result['vat_amount_eur']}")
                vat_amount = "found"  # Skip weitere Berechnung
            elif project_details.get('final_modified_price_net'):
                # Berechne MwSt aus modifiziertem Netto-Preis
                net_price = float(project_details['final_modified_price_net'])
                vat_amount = net_price * 0.19
                print(
                    f"DEBUG: MwSt berechnet aus final_modified_price_net: {net_price} * 0.19 = {vat_amount}")
            elif project_details.get('final_price_with_provision'):
                # Berechne MwSt aus Preis mit Provision
                net_price = float(
                    project_details['final_price_with_provision'])
                vat_amount = net_price * 0.19
                print(
                    f"DEBUG: MwSt berechnet aus final_price_with_provision: {net_price} * 0.19 = {vat_amount}")
            elif project_details.get('final_offer_price_net'):
                # Berechne MwSt aus finalem Angebotspreis
                net_price = float(project_details['final_offer_price_net'])
                vat_amount = net_price * 0.19
                print(
                    f"DEBUG: MwSt berechnet aus final_offer_price_net: {net_price} * 0.19 = {vat_amount}")

        # FALLBACK: Nur wenn keine finalen Preise gefunden wurden

        # Prüfe ob finale MwSt aus Solar Calculator verfügbar ist
        try:
            import streamlit as st
            if hasattr(
                    st,
                    'session_state') and 'project_data' in st.session_state:
                project_details = st.session_state.project_data.get(
                    'project_details', {})

                # Priorität: Preisänderungen > Provision > Basis
                if project_details.get('formatted_final_modified_vat_amount'):
                    # MwSt aus Preisänderungen (bereits formatiert)
                    vat_amount_formatted = project_details.get(
                        'formatted_final_modified_vat_amount', '')
                    result["vat_amount_eur"] = vat_amount_formatted
                    vat_amount = "found"  # Markiere als gefunden
                elif project_details.get('final_modified_price_net'):
                    # Berechne MwSt aus modifiziertem Netto-Preis
                    net_price = float(
                        project_details['final_modified_price_net'])
                    vat_amount = net_price * 0.19
                elif project_details.get('final_price_with_provision'):
                    # Berechne MwSt aus Preis mit Provision
                    net_price = float(
                        project_details['final_price_with_provision'])
                    vat_amount = net_price * 0.19
                elif project_details.get('final_offer_price_net'):
                    # Berechne MwSt aus finalem Angebotspreis
                    net_price = float(project_details['final_offer_price_net'])
                    vat_amount = net_price * 0.19
        except Exception:
            pass

        # Fallback: Verwende analysis_results
        if vat_amount is None:
            base_net = (
                analysis_results.get("total_investment_netto")
                or analysis_results.get("final_price")
                or analysis_results.get("subtotal_netto")
            )
            if isinstance(base_net, (int, float)):
                vat_amount = float(base_net) * 0.19
            else:
                # Falls nur Brutto/Netto-Kombi verfügbar, Differenz nutzen
                netto = analysis_results.get("total_investment_netto")
                brutto = analysis_results.get("total_investment_brutto")
                if isinstance(
                        netto, (int, float)) and isinstance(
                        brutto, (int, float)):
                    vat_amount = max(0.0, float(brutto) - float(netto))

        # Formatiere MwSt falls noch nicht formatiert
        if isinstance(vat_amount, (int, float)) and vat_amount is not None:
            result["vat_amount_eur"] = fmt_number(float(vat_amount), 2, "€")

    except Exception:
        pass

    # 3) Statische Texte
    #    a) „inklusive“ für die Label-Plätze "Batterie" und "Jahresertrag"
    result["static_inklusive"] = "inklusive"
    #    b) Rechts neben Batterie: „DC Dachmontage“
    result["static_dc_dachmontage"] = "DC Dachmontage"
    #    c) Rechts neben Jahresertrag: „AC Installation | Inbetriebnahme“
    result["static_ac_installation"] = "AC Installation | Inbetriebnahme"

    # Seite 3: Basis-Parameter dynamisch füllen
    try:
        # Energieversorger Name (falls vorhanden)
        provider = project_data.get("energy_supplier") or project_data.get(
            "stromanbieter") or analysis_results.get("energy_supplier")
        if provider:
            result["basis_energy_supplier_name"] = str(provider)
        # Wartung Prozent (z.B. 1 % Invest p.a.)
        maint_pct = analysis_results.get("maintenance_costs_percent") or analysis_results.get(
            "maintenance_percent_invest_pa")
        if isinstance(maint_pct, (int, float)):
            result["basis_maintenance_percent_invest"] = f"{
                maint_pct:.2f} % Invest. p.a."
        # Verbrauchstarif Text (exakte €/kWh Anzeige mit 4 Nachkommastellen
        # statt "Verbrauch 32 Cent")
        price_eur_kwh = (
            analysis_results.get(
                "aktueller_strompreis_fuer_hochrechnung_euro_kwh")
            or analysis_results.get("electricity_price_eur_per_kwh")
            or analysis_results.get("electricity_price_kwh")
            or analysis_results.get("electricity_price_per_kwh")
        )
        if isinstance(price_eur_kwh, (int, float)) and price_eur_kwh > 0:
            result["basis_tariff_text"] = f"{price_eur_kwh:.2f} € / kWh"
        # PV Lebensdauer
        lifetime = analysis_results.get(
            "simulation_period_years") or project_data.get("simulation_period_years")
        if isinstance(lifetime, (int, float)) and lifetime > 0:
            result["basis_pv_lifetime_years"] = f"{int(lifetime)} Jahre"
        # Strompreissteigerung
        inc_pct = analysis_results.get("electricity_price_increase_annual_percent") or project_data.get(
            "electricity_price_increase_annual_percent")
        if isinstance(inc_pct, (int, float)):
            result["basis_price_increase_percent_text"] = f"{
                inc_pct:.2f} % jährlich"
        # Eigenkapitalkosten
        cost_cap = analysis_results.get("cost_of_capital_percent") or project_data.get(
            "cost_of_capital_percent") or analysis_results.get("alternative_investment_interest_rate_percent")
        if isinstance(cost_cap, (int, float)):
            result["basis_cost_of_capital_percent"] = f"{cost_cap:.2f} %"
    except Exception:
        pass

    # Seite 3: Einsparungs-/Ertragszeilen neu & exakt nach Nutzerformeln
    # berechnen
    try:
        def _pf(v):
            try:
                if isinstance(v, (int, float)):
                    return float(v)
                return float(str(v).replace(',', '.'))
            except Exception:
                return None
        curr_price = _pf(price_eur_kwh) or _pf(analysis_results.get(
            "aktueller_strompreis_fuer_hochrechnung_euro_kwh")) or 0.0
        direct_kwh = _pf(analysis_results.get("direct_self_consumption_kwh")) or _pf(
            analysis_results.get("annual_direct_self_consumption_kwh"))
        if direct_kwh is None:
            try:
                eigenv_total = _pf(analysis_results.get(
                    "annual_self_consumption_kwh"))
                batt_dis_tmp = _pf(analysis_results.get(
                    "battery_discharge_for_sc_kwh")) or 0.0
                if eigenv_total is not None:
                    direct_kwh = max(0.0, eigenv_total - batt_dis_tmp)
            except Exception:
                pass
        if direct_kwh is not None and curr_price > 0:
            result["annual_electricity_cost_savings_self_consumption_year1"] = fmt_number(
                direct_kwh * curr_price, 2, "€")
        feed_kwh = _pf(analysis_results.get("netzeinspeisung_kwh"))
        feed_tariff = _pf(
            analysis_results.get("einspeiseverguetung_eur_per_kwh")) or _pf(
            analysis_results.get("feed_in_tariff_eur_per_kwh")) or _pf(
            analysis_results.get("feed_in_tariff_year1_eur_per_kwh"))
        # DEAKTIVIERT: Diese Zeile überschreibt die korrekte Seite 3 Berechnung mit falschen Daten
        # if feed_kwh is not None and feed_tariff is not None:
        #     result["annual_feed_in_revenue_year1"] = fmt_number(feed_kwh*feed_tariff,2,"€")
        batt_dis = _pf(analysis_results.get("battery_discharge_for_sc_kwh"))
        if batt_dis is not None and curr_price > 0:
            result["annual_battery_discharge_value_year1"] = fmt_number(
                batt_dis * curr_price, 2, "€")
        batt_charge = _pf(analysis_results.get("battery_charge_kwh"))
        if batt_charge is not None and batt_dis is not None and feed_tariff is not None:
            surplus = max(0.0, batt_charge - batt_dis)
            result["annual_battery_surplus_feed_in_value_year1"] = fmt_number(
                surplus * feed_tariff, 2, "€")
        parts = []
        for k in [
            "annual_electricity_cost_savings_self_consumption_year1",
            "annual_feed_in_revenue_year1",
            "annual_battery_discharge_value_year1",
                "annual_battery_surplus_feed_in_value_year1"]:
            val_s = result.get(k)
            if val_s:
                try:
                    parts.append(float(str(val_s).replace('.', '').replace(
                        '€', '').replace(' ', '').replace(',', '.')))
                except Exception:
                    pass
        if parts:
            result["annual_total_savings_year1_label"] = fmt_number(
                sum(parts), 2, "€")
    except Exception:
        pass

    # === FAIL-SAFE: Seite 3 Werte final absichern (falls weiter oben nichts gesetzt wurde) ===
    def _to_float(x):
        try:
            # Kommas tolerieren
            return float(str(x).replace(",", "."))
        except Exception:
            return 0.0

    def _eur(x):
        return fmt_number(x, 2, "€")

    # Einspeisetarif in €/kWh sichern (aus results oder Default <10 kWp
    # Teileinspeisung)
    eeg = _to_float(analysis_results.get(
        "einspeiseverguetung_eur_per_kwh") or 0.0786)
    if eeg > 1:  # Schutz falls ct/kWh geliefert
        eeg /= 100.0

    # Strompreis in €/kWh sichern
    price_eur_kwh = (
        _to_float(analysis_results.get(
            "aktueller_strompreis_fuer_hochrechnung_euro_kwh"))
        or _to_float(analysis_results.get("electricity_price_eur_per_kwh"))
        or _to_float(project_data.get("electricity_price_kwh"))
        or _to_float(project_data.get("electricity_price_per_kwh"))
        or 0.30
    )
    if price_eur_kwh > 1:  # Schutz falls ct/kWh geliefert
        price_eur_kwh /= 100.0

    # Jahreswerte als Fallback, falls Monatslisten fehlten
    feedin_kwh = _to_float(analysis_results.get("netzeinspeisung_kwh"))
    charge_kwh = _to_float(analysis_results.get("annual_storage_charge_kwh"))
    discharge_kwh = _to_float(
        analysis_results.get("annual_storage_discharge_kwh"))
    surplus_kwh = max(0.0, charge_kwh - discharge_kwh)

    # Falls die Seite-3 Felder noch leer/nicht vorhanden sind → jetzt befüllen
   # if not result.get("direct_grid_feed_in_eur"):
    #   result["direct_grid_feed_in_eur"] = _eur(feedin_kwh * eeg)

   # if not result.get("battery_usage_savings_eur"):
    #  result["battery_usage_savings_eur"] = _eur(discharge_kwh * price_eur_kwh)

   # if not result.get("battery_surplus_feed_in_eur"):
   #     result["battery_surplus_feed_in_eur"] = _eur(surplus_kwh * eeg)

    # Zusatz: kWh-Hilfsfelder für Seite 3, wenn noch leer
    if not result.get("calc_grid_feed_in_kwh_page3"):
        result["calc_grid_feed_in_kwh_page3"] = fmt_number(
            feedin_kwh, 0, "kWh")
    if not result.get("calc_battery_discharge_kwh_page3"):
        result["calc_battery_discharge_kwh_page3"] = fmt_number(
            discharge_kwh, 0, "kWh")
    if not result.get("calc_battery_surplus_kwh_page3"):
        result["calc_battery_surplus_kwh_page3"] = fmt_number(
            surplus_kwh, 0, "kWh")

    # Gesamtwert (total_annual_savings_eur) zwingend berechnen, falls noch
    # nicht gesetzt (inkl. Direktverbrauch)
    if not result.get("total_annual_savings_eur"):
        # Direktverbrauchs-Ersparnis nachladen falls fehlend
        if not result.get("self_consumption_without_battery_eur"):
            direct_kwh_fs = (
                _to_float(
                    analysis_results.get("annual_self_consumption_kwh")) or sum(
                    _to_float(x) for x in (
                        analysis_results.get("monthly_direct_self_consumption_kwh") or [])) or 0.0)
            result["self_consumption_without_battery_eur"] = _eur(
                direct_kwh_fs * price_eur_kwh)

        # Steuerliche Vorteile hinzufügen, falls noch nicht berechnet
        if not result.get("tax_benefits_eur"):
            # Einspeisevergütung für Steuerberechnung verwenden
            feedin_value = _to_float((result.get("annual_feed_in_revenue_eur") or result.get(
                "direct_grid_feed_in_eur") or "0").replace("€", "").replace(".", "").replace(",", "."))
            einkommensteuer_satz = _to_float(project_data.get("income_tax_rate") or project_details.get(
                "income_tax_rate") or analysis_results.get("income_tax_rate")) or 0.42
            tax_benefits = feedin_value * \
                (einkommensteuer_satz / 100.0 if einkommensteuer_satz >
                 1 else einkommensteuer_satz)
            result["tax_benefits_eur"] = _eur(tax_benefits)

        # Summe über die DREI Hauptbestandteile bilden (OHNE Speicherwerte wie
        # gewünscht)
        keys_sum = (
            "self_consumption_without_battery_eur",
            "direct_grid_feed_in_eur",
            "tax_benefits_eur",  # Steuerliche Vorteile
        )
        total = sum(
            _to_float((result.get(k) or "0").replace(
                "€", "").replace(".", "").replace(",", "."))
            for k in keys_sum
        )
        result["total_annual_savings_eur"] = _eur(total)

    # === Seite 3: Berechnungsgrundlagen - Dynamische Werte ===

    # Ausrichtung (orientation_text) aus calculations.py mit erweiterten
    # Fallbacks
    orientation = (
        analysis_results.get("orientation_text")
        or analysis_results.get("orientation")
        or analysis_results.get("ausrichtung")
        or project_data.get("orientation")
        or project_details.get("orientation")
        or project_data.get("ausrichtung")
        or project_details.get("ausrichtung")
        or project_data.get("roof_orientation")
        or project_details.get("roof_orientation")
        # Häufigster Schlüssel aus data_input.py Bedarfsanalyse
        or (project_data.get("project_details", {}) or {}).get("roof_orientation")
    )
    print(
        f"DEBUG ORIENTATION: raw_value='{orientation}', from analysis_results: '{
            analysis_results.get('orientation_text')}', from project_data: '{
            project_data.get('orientation')}', from project_details.roof_orientation: '{
                project_details.get('roof_orientation')}'")

    # Erweiterte Ausrichtungs-Logik - einfache Anzeige ohne Ertragswerte
    if orientation and str(orientation).strip() not in (
            "", "None", "null", "Bitte wählen", "Please select"):
        orientation_str = str(orientation).strip()
        result["orientation_text"] = orientation_str
        print(f"DEBUG ORIENTATION: using value '{orientation_str}'")
    else:
        # Fallback für fehlende Ausrichtung
        result["orientation_text"] = "Süd"
        print("DEBUG ORIENTATION: using fallback 'Süd'")

    print(
        f"DEBUG ORIENTATION: final result='{result.get('orientation_text')}'")

    # Seitennummerierung für Seite 3
    try:
        total_pages = project_data.get("total_pages", 7)
        result["page_number_with_total"] = f"Seite 3 von {total_pages}"
        print(f"DEBUG PAGE_NUMBER: formatted as 'Seite 3 von {total_pages}'")
    except Exception:
        result["page_number_with_total"] = "3"
        print("DEBUG PAGE_NUMBER: fallback to '3'")

    # Dachdeckung aus data_input.py (project_data oder project_details)
    roof_covering = (
        project_data.get("roof_covering_type")
        or project_details.get("roof_covering_type")
        or project_data.get("roof_covering")
        or project_details.get("roof_covering")
    )
    if roof_covering:
        result["roof_covering_type"] = str(roof_covering)

    # Dachneigung aus data_input.py
    roof_inclination = (
        project_data.get("roof_inclination_deg")
        or project_details.get("roof_inclination_deg")
        or project_data.get("roof_inclination")
        or project_details.get("roof_inclination")
        # Häufigster Schlüssel aus data_input.py Bedarfsanalyse
        or (project_data.get("project_details", {}) or {}).get("roof_inclination_deg")
    )
    print(
        f"DEBUG ROOF_INCLINATION: raw_value='{roof_inclination}', from project_details: '{
            project_details.get('roof_inclination_deg')}', from nested: '{
            (
                project_data.get(
                    'project_details',
                    {}) or {}).get('roof_inclination_deg')}'")

    if roof_inclination is not None:
        try:
            incl_val = float(roof_inclination)
            result["roof_inclination_text"] = f"{incl_val:.0f}°"
            print(
                f"DEBUG ROOF_INCLINATION: formatted as '{
                    result['roof_inclination_text']}'")
        except Exception:
            result["roof_inclination_text"] = str(roof_inclination)
            print(
                f"DEBUG ROOF_INCLINATION: used as string '{
                    result['roof_inclination_text']}'")
    else:
        result["roof_inclination_text"] = "30°"
        print("DEBUG ROOF_INCLINATION: using fallback '30°'")

    # Dachart aus data_input.py
    roof_type = (
        project_data.get("roof_type")
        or project_details.get("roof_type")
        or project_data.get("roof_structure")
        or project_details.get("roof_structure")
    )
    # Debug-Print und Filter für "Bitte wählen"-Werte
    print(
        f"DEBUG ROOF_TYPE: raw_value='{roof_type}', from project_data: '{
            project_data.get('roof_type')}', from project_details: '{
            project_details.get('roof_type')}'")

    if roof_type and str(roof_type).strip() not in (
            "", "Bitte wählen", "Please select", "None", "null"):
        result["roof_type"] = str(roof_type).strip()
    else:
        # Fallback: Versuche andere mögliche Schlüssel
        fallback_keys = ["dach_art", "dachtyp", "roof_material", "dach_typ"]
        for key in fallback_keys:
            val = project_data.get(key) or project_details.get(key)
            if val and str(val).strip() not in (
                    "", "Bitte wählen", "Please select", "None", "null"):
                result["roof_type"] = str(val).strip()
                print(
                    f"DEBUG ROOF_TYPE: used fallback key '{key}' with value '{val}'")
                break
        else:
            result["roof_type"] = "Standard"  # Letzter Fallback
            print("DEBUG ROOF_TYPE: using fallback 'Standard'")

    print(f"DEBUG ROOF_TYPE: final result='{result.get('roof_type')}'")

    # Finanzierung/Leasing gewünscht - zeigt die gewählte Finanzierungsart
    # oder "Nein"
    financing_requested = (
        project_data.get("financing_requested")
        or project_data.get("financing_needed")
        or project_data.get("financing_leasing_required")
        or project_data.get("finanzierung_leasing_gewuenscht")
        or project_details.get("financing_needed")
        or project_details.get("financing_leasing_required")
        or (project_data.get("customer_data") or {}).get("financing_requested")
        or (project_details.get("customer_data") or {}).get("financing_requested")
    )

    # Finanzierungsart ermitteln
    financing_type = (
        project_data.get("financing_type")
        or project_details.get("financing_type")
        or (project_data.get("customer_data") or {}).get("financing_type")
        or (project_details.get("customer_data") or {}).get("financing_type")
    )

    # Debug-Output für Finanzierung
    print(
        f"DEBUG FINANCING: financing_requested='{financing_requested}', financing_type='{financing_type}'")
    print(
        f"DEBUG FINANCING: project_data.customer_data={
            project_data.get(
                'customer_data',
                {})}")

    if financing_requested:
        # Wenn Finanzierung gewünscht ist, zeige die gewählte Art
        if isinstance(financing_requested, bool) and financing_requested:
            if financing_type and isinstance(financing_type, str):
                result["financing_needed_text"] = financing_type
            else:
                result["financing_needed_text"] = "Ja"
        elif isinstance(financing_requested, str):
            financing_str = financing_requested.lower().strip()
            if financing_str in {"true", "ja", "yes", "1", "wahr"}:
                if financing_type and isinstance(financing_type, str):
                    result["financing_needed_text"] = financing_type
                else:
                    result["financing_needed_text"] = "Ja"
            else:
                result["financing_needed_text"] = "Nein"
        else:
            result["financing_needed_text"] = "Nein"
    else:
        result["financing_needed_text"] = "Nein"

    print(
        f"DEBUG FINANCING: final result financing_needed_text='{
            result.get('financing_needed_text')}')")

    # EEG-Vergütung formatiert (ct/kWh)
    try:
        anlage_kwp_val = parse_float(analysis_results.get(
            "anlage_kwp") or project_data.get("anlage_kwp")) or 0.0
        mode_val = project_data.get("einspeise_art", "parts")

        # Nutze die neue resolve_feed_in_tariff_eur_per_kwh Funktion
        try:
            from database import load_admin_setting as _load_admin_func
        except Exception:
            _load_admin_func = None

        if _load_admin_func:
            eeg_eur_per_kwh = resolve_feed_in_tariff_eur_per_kwh(
                anlage_kwp_val,
                mode_val,
                _load_admin_func,
                analysis_results_snapshot=(analysis_results.get(
                    "einspeiseverguetung_eur_per_kwh"),)
            )
            # Zurück in ct/kWh umrechnen für Anzeige
            eeg_ct_per_kwh = eeg_eur_per_kwh * 100.0
            result["feed_in_tariff_text"] = f"{eeg_ct_per_kwh:.2f} Cent / kWh"
        else:
            # Fallback ohne Admin-Settings
            result["feed_in_tariff_text"] = " Cent / kWh"
    except Exception:
        result["feed_in_tariff_text"] = " Cent / kWh"

    # === NEUE LOGO-INTEGRATION FÜR SEITE 4 ===
    # Logo-Platzhalter für Hersteller basierend auf ausgewählten Produkten
    try:
        # Import der Logo-Funktionen
        from brand_logo_db import get_logos_for_brands

        # Hersteller aus Projektdaten extrahieren (lokale Implementierung)
        def extract_brands_from_project_data(
                project_data_local: dict[str, Any]) -> dict[str, str]:
            """Extrahiert Hersteller-Roh-Namen (für Logo-Lookup). Nutzen Reihenfolge:
            1. project_details explizit
            2. *_manufacturer_raw (vor Normalisierung gesichert)
            3. bereinigte *_manufacturer (Leerzeichen entfernt)
            """
            brands: dict[str, str] = {}
            project_details_local = project_data_local.get(
                "project_details", {}) or {}

            def pick(raw_key: str, disp_key: str, proj_key: str) -> str:
                # Priorität: project_details -> raw -> display -> ""
                val = as_str(project_details_local.get(proj_key) or "").strip()
                if not val:
                    val = as_str(result.get(raw_key) or "").strip()
                if not val:
                    val = as_str(result.get(disp_key) or "").strip()
                return val.replace(" ", "")

            module_brand = pick("module_manufacturer_raw",
                                "module_manufacturer", "module_manufacturer")
            if module_brand:
                brands["modul"] = module_brand

            inverter_brand = pick(
                "inverter_manufacturer_raw",
                "inverter_manufacturer",
                "inverter_manufacturer")
            if inverter_brand:
                brands["wechselrichter"] = inverter_brand

            storage_brand = pick(
                "storage_manufacturer_raw",
                "storage_manufacturer",
                "storage_manufacturer")
            if storage_brand:
                brands["batteriespeicher"] = storage_brand

            return brands

        # Hersteller aus Projektdaten extrahieren (Roh)
        brands_by_category = extract_brands_from_project_data(project_data)

        # Fallback-Varianten ohne funktionale Suffixe für besseren DB-Match
        # vorbereiten
        def _brand_logo_key_variants(b: str) -> list[str]:
            import re
            if not b:
                return []
            variants = []
            base = b
            attached = re.compile(
                r"^(.*?)(pv|wr|speicher|batterie|akku|ess|stromspeicher)$",
                re.IGNORECASE)
            prev = None
            while base and base != prev:
                prev = base
                m = attached.match(base)
                if m and m.group(1).strip():
                    base = m.group(1).strip()
                    variants.append(base)
                else:
                    break
            variants_norm = list(
                {v for v in variants if v and v.lower() != b.lower()})
            return variants_norm

    # (Frühere Dummy-Placeholder "logo_*_placeholder" entfernt – direkte Nutzung der echten Keys)

        # Logos aus Datenbank holen
        if brands_by_category:
            brand_names_raw = list(brands_by_category.values())
            extended = []
            for b in brand_names_raw:
                extended.append(b)
                for v in _brand_logo_key_variants(b):
                    if v not in extended:
                        extended.append(v)
            unique_brands = list(set(extended))

            logos_data = get_logos_for_brands(unique_brands)

            logo_mapping = {
                'modul': 'module_brand_logo_b64',
                'wechselrichter': 'inverter_brand_logo_b64',
                'batteriespeicher': 'storage_brand_logo_b64'
            }

            for category, brand_name in brands_by_category.items():
                logo_key = logo_mapping.get(category)
                if not logo_key:
                    continue
                chosen = None
                if brand_name in logos_data:
                    chosen = logos_data[brand_name]
                else:
                    for v in _brand_logo_key_variants(brand_name):
                        if v in logos_data:
                            chosen = logos_data[v]
                            break
                if chosen:
                    result[logo_key] = chosen.get('logo_base64', '')
                    result[f"{logo_key}_format"] = chosen.get(
                        'logo_format', 'PNG')
                    print(
                        f"Logo für {category} ({brand_name}) -> Match gespeichert (DB-Key: {
                            chosen.get('brand_name')})")
                else:
                    print(
                        f"Kein Logo-Match für {category} ({brand_name}) inkl. Varianten")

    except Exception as e:
        print(f"Fehler bei der Logo-Integration: {e}")
        # Keine Dummy-Keys mehr – stiller Fallback (einfach keine Logos)

    # --- Erweiterung 2025-08: Wärmepumpen-Angebotsplatzhalter integrieren ---
    try:
        # Falls bereits ein fertiges Offer im project_data steckt (z.B. aus
        # UI), verwende dieses
        hp_offer = None
        if isinstance(project_data, dict):
            hp_offer = project_data.get("heatpump_offer")
        if not hp_offer:
            # Versuche on-the-fly zu berechnen (Standard ohne Rabatte)
            try:
                from heatpump_pricing import (
                    build_full_heatpump_offer,
                    extract_placeholders_from_offer,
                )
                hp_offer = build_full_heatpump_offer()
                hp_ph = extract_placeholders_from_offer(hp_offer)
            except Exception:
                hp_ph = {}
        else:
            from heatpump_pricing import extract_placeholders_from_offer  # type: ignore
            hp_ph = extract_placeholders_from_offer(hp_offer)

        # HP-Placeholders in das Haupt-Result-Dictionary einfügen
        if hp_ph and isinstance(hp_ph, dict):
            for key, value in hp_ph.items():
                if key.startswith('HP_'):
                    result[key] = value
                else:
                    result[f'HP_{key.upper()}'] = value

        # Zusätzliche HP-Felder erstellen (vereinfacht, aus hp_offer direkt)
        if hp_offer and isinstance(hp_offer, dict):
            # Grundlegende HP-Informationen
            result['hp_title'] = 'Wärmepumpen-Angebot'
            result['hp_summary_line1'] = 'Energieeffiziente Heizlösung für Ihr Zuhause'
            result['hp_summary_line2'] = 'Nachhaltig • Effizient • Zukunftssicher'

            # BEG-Förderung
            beg_data = hp_offer.get('beg_subsidy', {})
            if beg_data:
                subsidy_rate = beg_data.get('subsidy_rate_percent', 0)
                subsidy_amount = beg_data.get('beg_subsidy_amount_eur', 0)
                result['hp_subsidy_rate'] = f"{subsidy_rate}%" if subsidy_rate else "0%"
                result['hp_subsidy_amount'] = fmt_number(
                    subsidy_amount, 0, '€') if subsidy_amount else "0 €"

            # Finanzierung
            financing = hp_offer.get('financing', {})
            if financing:
                monthly_rate = financing.get('monthly_payment_eur', 0)
                result['hp_financing_monthly'] = fmt_number(
                    monthly_rate, 2, '€') if monthly_rate else "0,00 €"
        # Werte formatieren (Euro / Prozent)

        def _fmt_eur(v):
            try:
                return fmt_number(float(v), 0, "€")
            except Exception:
                return ""

        def _fmt_pct(v):
            try:
                return fmt_number(float(v), 0, "%")
            except Exception:
                return ""
        mapping_fmt = {}
        for k, v in hp_ph.items():
            if k.endswith("_PCT"):
                mapping_fmt[k] = _fmt_pct(v)
            elif k.endswith("_AMOUNT") or k.endswith("_NET") or k.endswith("_PRICE_NET") or k in {"HP_MONTHLY_RATE", "HP_TOTAL_INTEREST"}:
                mapping_fmt[k] = _fmt_eur(v)
            else:
                mapping_fmt[k] = str(v)
        result.update(mapping_fmt)
        # Kombinations-Angebot: falls PV + WP beide vorhanden
        try:
            if analysis_results and isinstance(analysis_results, dict):
                hp_after = hp_ph.get('HP_AFTER_SUBSIDY_NET')
                pv_total = analysis_results.get('total_investment_netto')
                combined = None
                if hp_after is not None and pv_total is not None:
                    try:
                        combined = float(hp_after) + float(pv_total)
                    except Exception:
                        combined = None
                if combined is not None:
                    result['COMBINED_TOTAL_NET'] = fmt_number(combined, 0, '€')
                    result['PV_TOTAL_NET'] = fmt_number(
                        pv_total, 0, '€') if pv_total is not None else ''
                    result['HP_TOTAL_NET'] = fmt_number(
                        hp_after, 0, '€') if hp_after is not None else ''
        except Exception:
            pass
    except Exception as _hp_err:
        print(f"Hinweis: Wärmepumpen-Platzhalter nicht erzeugt: {_hp_err}")

    # =============================
    # Seite 5: Nachhaltigkeits-KPIs
    # =============================
    try:
        # 1) Jahres-CO2-Ersparnis (kg)
        annual_co2_keys = [
            'co2_savings_kg_per_year',
            'co2_einsparung_jahr_kg',
            'annual_co2_savings_kg',
            'environmental_co2_savings_kg_year',
            'co2_annual_savings_kg']
        annual_co2_kg = 0.0
        for k in annual_co2_keys:
            v = analysis_results.get(k)
            if isinstance(v, (int, float)) and v > 0:
                annual_co2_kg = float(v)
                break
        if annual_co2_kg <= 0:  # Fallback aus Produktion * Emissionsfaktor
            prod_kwh = None
            for pk in [
                'annual_pv_production_kwh',
                'annual_yield_kwh',
                    'sim_annual_yield_kwh']:
                pv = analysis_results.get(pk)
                if isinstance(pv, (int, float)) and pv > 0:
                    prod_kwh = float(pv)
                    break
            emission_factor = analysis_results.get(
                'co2_emission_factor_kg_per_kwh')
            if not isinstance(emission_factor, (int, float)
                              ) or emission_factor <= 0:
                emission_factor = 0.474  # Standard DE Strommix kg/kWh
            if prod_kwh:
                annual_co2_kg = prod_kwh * float(emission_factor)

        # 2) Baumäquivalent
        tree_factor = analysis_results.get('co2_per_tree_kg_pa')
        if not isinstance(tree_factor, (int, float)) or tree_factor <= 0:
            tree_factor = 12.5  # konservativer Mittelwert
        trees_equiv = annual_co2_kg / tree_factor if tree_factor > 0 else 0.0

        # 3) Auto-Kilometer Äquivalent
        car_factor = analysis_results.get('co2_per_car_km_kg')
        if not isinstance(car_factor, (int, float)) or car_factor <= 0:
            car_factor = 0.12  # ~120 g CO2 pro km
        car_km_equiv = annual_co2_kg / car_factor if car_factor > 0 else 0.0

        # 4) Prozentuale Reduktion (Anteil am durchschnittlichen dt. Pro-Kopf
        # Fußabdruck ~7,69 t)
        baseline_tons = analysis_results.get('co2_baseline_per_capita_tons')
        if not isinstance(baseline_tons, (int, float)) or baseline_tons <= 0:
            baseline_tons = 7.69
        co2_reduction_pct = 0.0
        if baseline_tons > 0:
            co2_reduction_pct = (annual_co2_kg / 1000.0) / \
                baseline_tons * 100.0
        # Bereits berechnete Werte ggf. bevorzugen
        for rk in ['co2_reduction_percent', 'co2_footprint_reduction_percent']:
            rv = analysis_results.get(rk)
            if isinstance(rv, (int, float)) and rv > 0:
                co2_reduction_pct = float(rv)
                break

        # Formatierungen (deutsches Zahlenformat via fmt_number)
        result['sustainability_annual_co2_savings_kg_ellipsis'] = f"{
            fmt_number(
                annual_co2_kg,
                2)} kg..."
        result['sustainability_car_km_equivalent_long'] = f"{
            fmt_number(
                car_km_equiv,
                2)} Kilometer"
        result['sustainability_car_km_equivalent_short'] = f"{
            fmt_number(
                car_km_equiv, 2)} km"
        result['sustainability_co2_reduction_percent'] = f"{
            fmt_number(
                co2_reduction_pct, 2)} %"
        # Bäume: gerundete ganze Zahl
        result['sustainability_tree_equivalent_with_label'] = f"{
            fmt_number(
                round(trees_equiv),
                0)} Bäume"
        result['sustainability_tree_equivalent_number'] = fmt_number(
            round(trees_equiv), 0)

        print("DEBUG SEITE5 SUSTAINABILITY:")
        print(
            f"  annual_co2_kg={
                annual_co2_kg:.2f} | trees_equiv={
                trees_equiv:.2f} | car_km_equiv={
                car_km_equiv:.2f} | co2_reduction_pct={
                    co2_reduction_pct:.2f}")
    except Exception as e:
        print(f"WARN Seite5 Nachhaltigkeit Block Fehler: {e}")

    # =============================
    # Seite 6: Zusammenfassung
    # =============================
    try:
        # Saubere CO2 Zahl ohne Ellipse bereitstellen
        if 'sustainability_annual_co2_savings_kg_ellipsis' in result:
            # Entferne ' kg...' -> Zahl extrahieren
            raw = result['sustainability_annual_co2_savings_kg_ellipsis']
            m = re.search(r"([0-9\.,]+)", raw)
            if m:
                result['sustainability_annual_co2_savings_kg_clean'] = f"{
                    m.group(1)} kg"
            else:
                result['sustainability_annual_co2_savings_kg_clean'] = raw.replace(
                    "...", " ").strip()
        # Systemkonfiguration zusammensetzen (nur vorhandene Werte, ohne
        # doppelte Einheiten)
        parts = []
        for key in [
            "anlage_kwp",
            "pv_modules_count_with_unit",
            "storage_capacity_kwh",
                "inverter_total_power_kw"]:
            val = result.get(key)
            if val and isinstance(val, str) and val.strip():
                parts.append(val.strip())
        if parts:
            result['summary_system_configuration'] = " | ".join(parts)
        else:
            result['summary_system_configuration'] = ""

        # Produkt-Zeilen für Seite 6 (Module, WR, Speicher) – neue Formatierung
        # ohne "|" und Einheiten
        def _clean(v: str) -> str:
            return (v or '').replace('\n', ' ').strip()

        # Module: Hersteller + Modell (ohne Leistung und Stückzahl)
        # Priorität: analysis_results > result (aus DB/project_details)
        mod_manufacturer = (analysis_results.get('module_manufacturer') or
                            result.get('module_manufacturer') or '').strip()
        mod_model = (analysis_results.get('module_model') or
                     result.get('module_model') or '').strip()

        mod_line_parts = []
        if mod_manufacturer:
            mod_line_parts.append(_clean(mod_manufacturer))
        if mod_model:
            mod_line_parts.append(_clean(mod_model))
        result['summary_product_module_line'] = ' '.join(mod_line_parts)

        # Separate Keys für PV Module Stückzahl
        result['pv_modules_count_key'] = result.get(
            'pv_modules_count_with_unit', '')

        # Wechselrichter: Hersteller + Modell (ohne Leistung)
        # Priorität: analysis_results > result (aus DB/project_details)
        inv_manufacturer = (analysis_results.get('inverter_manufacturer') or
                            result.get('inverter_manufacturer') or '').strip()
        inv_model = (analysis_results.get('inverter_model') or
                     result.get('inverter_model') or '').strip()

        inv_line_parts = []
        if inv_manufacturer:
            inv_line_parts.append(_clean(inv_manufacturer))
        if inv_model:
            inv_line_parts.append(_clean(inv_model))
        result['summary_product_inverter_line'] = ' '.join(inv_line_parts)

        # Speicher: Hersteller + Modell (ohne Kapazität)
        # Priorität: analysis_results > result (aus DB/project_details)
        stor_manufacturer = (analysis_results.get('storage_manufacturer') or
                             result.get('storage_manufacturer') or '').strip()
        stor_model = (analysis_results.get('storage_model') or
                      result.get('storage_model') or '').strip()

        stor_line_parts = []
        if stor_manufacturer:
            stor_line_parts.append(_clean(stor_manufacturer))
        if stor_model:
            stor_line_parts.append(_clean(stor_model))
        result['summary_product_storage_line'] = ' '.join(stor_line_parts)

        # Separate Keys für Batteriespeicher Kapazität
        # Priorität: analysis_results > result
        storage_capacity = (analysis_results.get('storage_capacity_kwh') or
                            result.get('storage_capacity_kwh') or '').strip()
        result['storage_capacity_key'] = storage_capacity

    except Exception as e:
        print(f"WARN Seite6 Produktzeilen Fehler: {e}")

    # === SEITE 6 DIENSTLEISTUNGEN ===
    # Dienstleistungen – Standard & Optional
    # Standard-Services können jetzt per Flag (true/false) deaktiviert werden.
    standard_services = {
        'service_consulting': 'Beratung',
        'service_planning': 'Planung',
        'service_project_management': 'Projektierung',
        'service_optimization': 'Optimierung',
        'service_grid_application': 'Anmeldung / Genehmigung EVU',
        'service_dc_installation': 'DC Montagearbeiten',
        'service_ac_installation': 'AC Elektroinstallationsarbeiten',
        'service_storage_installation': 'Installation Batteriespeicher',
        'service_commissioning_training': 'Inbetriebnahme & Einweihung',
        'service_grid_completion': 'Fertigmeldung & Abnahme von EVU',
    }
    optional_services = {
        'service_additional_tasks': 'Weitere Tätigkeiten',
        'service_wallbox_cabling': 'Leitungsverlegung Wallbox',
        'service_backup_power_activation': 'Aktivierung Notstromversorgung',
        'service_energy_management_system': 'Installation Energiemanagementsystem',
        'service_dynamic_tariff_activation': 'Aktivierung dynamischer Stromtarif',
    }

    # Nutzer-Auswahl aus project_data -> erwartet Struktur
    # project_data['pdf_services'] = {key: bool, 'custom': '...'}
    pdf_services_cfg = project_data.get(
        'pdf_services') if isinstance(project_data, dict) else None
    if not isinstance(pdf_services_cfg, dict):
        pdf_services_cfg = {}

    # Checkbox-Modus 'extras_enabled' (setzt optionalen Block frei)
    extras_enabled = bool(pdf_services_cfg.get('extras_enabled', False))

    # Standard-Services: aktiv wenn Flag fehlt oder True; gesetzt auf '' wenn
    # False
    design_cfg = (project_data.get('pdf_design_config')
                  or analysis_results.get('pdf_design_config')
                  or project_data.get('inclusion_options', {}).get('pdf_design_config')
                  or {})

    # Merge mit aktueller Session-State Konfiguration (falls UI Änderungen noch
    # nicht in project_data übernommen wurden). Session-Werte überschreiben.
    try:  # defensiv – funktioniert auch außerhalb Streamlit-Kontext
        import streamlit as st  # type: ignore
        if 'pdf_design_config' in st.session_state:
            session_cfg = st.session_state.get('pdf_design_config') or {}
            if isinstance(session_cfg, dict) and session_cfg:
                # Session überschreibt vorhandene Keys (nur nicht-None Werte)
                merged = dict(design_cfg)
                for _k, _v in session_cfg.items():
                    merged[_k] = _v
                design_cfg = merged
    except Exception:
        pass
    checkmarks_on = bool(design_cfg.get(
        'service_checkmarks_enabled', True))
    # check|checkbox|dot|none (Default geändert auf 'none')
    symbol_style = design_cfg.get('service_symbol_style', 'none')
    hide_value_col = bool(design_cfg.get(
        'service_value_column_hidden', False))
    symbol_color = design_cfg.get('service_symbol_color')  # Hex
    label_color = design_cfg.get('service_label_color')

    # Map Symbolstil
    def _symbol(active: bool) -> str:
        if not active or not checkmarks_on or symbol_style == 'none' or hide_value_col:
            return ''
        if symbol_style == 'checkbox':
            return '☑'
            if symbol_style == 'dot':
                return '•'
            # default 'check'
            return '✓'

        for k, label in standard_services.items():
            enabled = pdf_services_cfg.get(k, True)
            # Service-Werte zeigen jetzt echte Inhalte statt nur Symbole
            if enabled:
                result[k] = label  # Zeige den Service-Namen als Wert
            else:
                result[k] = ''  # Leer wenn deaktiviert
            # Dynamische Label-Ausgabe (gleiche Logik)
            label_key = 'label_' + k
            result[label_key] = label if enabled else ''

        # Kombinierte Labels mit "/" für bestimmte Services
        beratung_enabled = pdf_services_cfg.get('service_consulting', True)
        planung_enabled = pdf_services_cfg.get('service_planning', True)
        projektierung_enabled = pdf_services_cfg.get(
            'service_project_management', True)
        optimierung_enabled = pdf_services_cfg.get(
            'service_optimization', True)

        # Beratung / Planung auf gleicher Zeile
        if beratung_enabled and planung_enabled:
            result['label_service_consulting'] = 'Beratung / Planung'
            result['label_service_planning'] = ''  # Leer, da kombiniert
        elif beratung_enabled:
            result['label_service_consulting'] = 'Beratung'
        elif planung_enabled:
            result['label_service_planning'] = 'Planung'

        # Projektierung / Optimierung auf gleicher Zeile
        if projektierung_enabled and optimierung_enabled:
            result['label_service_project_management'] = 'Projektierung / Optimierung'
            result['label_service_optimization'] = ''  # Leer, da kombiniert
        elif projektierung_enabled:
            result['label_service_project_management'] = 'Projektierung'
        elif optimierung_enabled:
            result['label_service_optimization'] = 'Optimierung'

        # Optionale Services nur wenn extras_enabled und Flag aktiv
        for k, label in optional_services.items():
            enabled = extras_enabled and pdf_services_cfg.get(k, False)
            # Service-Werte zeigen jetzt echte Inhalte statt nur Symbole
            if enabled:
                result[k] = label  # Zeige den Service-Namen als Wert
            else:
                result[k] = ''  # Leer wenn deaktiviert
            label_key = 'label_' + k
            result[label_key] = label if enabled else ''

        # Farbinformationen für Overlay-Engine (falls dort unterstützt)
        if symbol_color:
            result['service_symbol_color'] = symbol_color
        if label_color:
            result['service_label_color'] = label_color
        result['service_value_column_hidden'] = '1' if hide_value_col else ''

        # Custom Entries Label nur wenn Inhalte vorhanden
        custom_entries_raw = pdf_services_cfg.get('custom_entries', '')
        if isinstance(custom_entries_raw, str) and custom_entries_raw.strip():
            result['label_service_custom_entries'] = 'Sonstiges / Individuelle Eintragung'
        else:
            result['label_service_custom_entries'] = ''

        # Zusammenfassungszeile: Anzahl aktiver Dienstleistungen (Standard +
        # optional + custom block)
        active_service_keys = []
        for k in list(standard_services.keys()) + \
                list(optional_services.keys()):
            if result.get(k):
                active_service_keys.append(k)
        if result.get('service_custom_entries_joined'):
            active_service_keys.append('service_custom_entries_joined')
        count_active = len(active_service_keys)
        # Zusammenfassungszeile deaktiviert (Anforderung: Menge nicht anzeigen)
        result['service_summary_line'] = ''

        # Custom / Sonstiges Einträge (Textarea, Zeilenumbrüche oder Semikolon
        # trennen)
        custom_raw = pdf_services_cfg.get('custom_entries') or ''
        custom_entries = []
        if isinstance(custom_raw, str) and custom_raw.strip():
            for part in re.split(r'[\n;]+', custom_raw):
                p = part.strip()
                if p:
                    custom_entries.append(p)
        result['service_custom_entries_joined'] = ' | '.join(custom_entries)

    # === NEUE FORMATIERTE PRODUKTWERTE FÜR SEITE 6 ===
    try:
        # 1. Module Anzahl Format "28 x"
        pv_count_raw = analysis_results.get(
            'pv_modules_count_with_unit') if analysis_results else None
        if not pv_count_raw and project_data and 'project_details' in project_data:
            pv_count_raw = project_data['project_details'].get(
                'module_quantity')

        if pv_count_raw:
            match = re.search(r'(\d+)', str(pv_count_raw))
            if match:
                result['module_count_formatted'] = f"{match.group(1)} x"
            else:
                result['module_count_formatted'] = str(pv_count_raw)
        else:
            result['module_count_formatted'] = ''

        # 2. Wechselrichter Leistung in W Format "10.000 W"
        inverter_power = (analysis_results.get('inverter_total_power_kw')
                          if analysis_results else None) or result.get('inverter_total_power_kw')

        # Fallback: Versuche andere mögliche Keys
        if not inverter_power and project_data and 'project_details' in project_data:
            project_details = project_data['project_details']
            inverter_power = (project_details.get('selected_inverter_power_kw') or
                              project_details.get('inverter_power_kw'))

        if inverter_power:
            try:
                power_val = float(
                    str(inverter_power).replace(
                        ',',
                        '.').replace(
                        ' kW',
                        '').replace(
                        'kW',
                        ''))
                # Konvertiere kW zu W
                power_w = power_val * 1000
                result['inverter_power_w_formatted'] = f"{
                    power_w:,.0f} W".replace(
                    ',', '.')
            except Exception as e:
                print(f"DEBUG: Inverter power conversion error: {e}")
                result['inverter_power_w_formatted'] = str(inverter_power)
        else:
            print(
                "DEBUG: No inverter power found in analysis_results, result, or project_details")
            result['inverter_power_w_formatted'] = ''

        # 3. Speicher Kapazität Format "12,09 kWh"
        storage_capacity = (analysis_results.get('storage_capacity_kwh')
                            if analysis_results else None) or result.get('storage_capacity_kwh')

        # Fallback: Versuche andere mögliche Keys
        if not storage_capacity and project_data and 'project_details' in project_data:
            project_details = project_data['project_details']
            storage_capacity = (project_details.get('selected_storage_capacity_kwh') or
                                project_details.get('storage_capacity_kwh') or
                                project_details.get('battery_capacity_kwh'))

        if storage_capacity:
            try:
                capacity_val = float(
                    str(storage_capacity).replace(
                        ',',
                        '.').replace(
                        ' kWh',
                        '').replace(
                        'kWh',
                        ''))
                result['storage_capacity_formatted'] = f"{
                    capacity_val:,.2f} kWh".replace(
                    '.', ',')
            except Exception as e:
                print(f"DEBUG: Storage capacity conversion error: {e}")
                result['storage_capacity_formatted'] = str(storage_capacity)
        else:
            print(
                "DEBUG: No storage capacity found in analysis_results, result, or project_details")
            result['storage_capacity_formatted'] = ''

        # === SPEICHER-RELATIONEN BERECHNUNGEN ===
        try:
            from calculations import (
                calculate_storage_to_consumption_ratio,
                calculate_storage_to_production_ratio,
            )

            # Speicherkapazität extrahieren (in kWh)
            storage_kwh = 0
            if storage_capacity:
                try:
                    storage_kwh = float(
                        str(storage_capacity).replace(
                            ',',
                            '.').replace(
                            ' kWh',
                            '').replace(
                            'kWh',
                            ''))
                except BaseException:
                    pass

            # Tagesverbrauch berechnen (Jahresverbrauch / 365)
            daily_consumption = 0
            if project_data and 'project_details' in project_data:
                annual_consumption = project_data['project_details'].get(
                    'annual_consumption_kwh', 0)
                if annual_consumption:
                    try:
                        annual_consumption_val = float(
                            str(annual_consumption).replace(',', '.'))
                        daily_consumption = annual_consumption_val / 365
                    except BaseException:
                        pass

            # PV-Tagesproduktion berechnen (Jahresertrag / 365)
            daily_production = 0
            if analysis_results:
                annual_yield = analysis_results.get('annual_yield_kwh', 0)
                if annual_yield:
                    try:
                        annual_yield_val = float(
                            str(annual_yield).replace(',', '.'))
                        daily_production = annual_yield_val / 365
                    except BaseException:
                        pass

            # Fallback: Versuche aus result
            if daily_production == 0 and result.get(
                    'annual_pv_production_kwh'):
                try:
                    annual_prod_val = float(str(result['annual_pv_production_kwh']).replace(
                        ',', '.').replace(' kWh', '').replace('kWh', ''))
                    daily_production = annual_prod_val / 365
                except BaseException:
                    pass

            # Berechnung 1: Speicher zu Tagesverbrauch Relation
            if storage_kwh > 0 and daily_consumption > 0:
                consumption_ratio = calculate_storage_to_consumption_ratio(
                    storage_kwh, daily_consumption)
                result['storage_consumption_ratio_percent'] = f"{
                    consumption_ratio:.0f}"
                print(
                    f"DEBUG: Storage consumption ratio: {
                        consumption_ratio:.0f}% (Storage: {storage_kwh} kWh, Daily consumption: {
                        daily_consumption:.2f} kWh)")
            else:
                result['storage_consumption_ratio_percent'] = "0"
                print(
                    f"DEBUG: Cannot calculate consumption ratio - Storage: {storage_kwh} kWh, Daily consumption: {daily_consumption} kWh")

            # Berechnung 2: Speicher zu PV-Tagesproduktion Relation
            if storage_kwh > 0 and daily_production > 0:
                production_ratio = calculate_storage_to_production_ratio(
                    storage_kwh, daily_production)
                result['storage_production_ratio_percent'] = f"{
                    production_ratio:.0f}"
                print(
                    f"DEBUG: Storage production ratio: {
                        production_ratio:.0f}% (Storage: {storage_kwh} kWh, Daily production: {
                        daily_production:.2f} kWh)")
            else:
                result['storage_production_ratio_percent'] = "0"
                print(
                    f"DEBUG: Cannot calculate production ratio - Storage: {storage_kwh} kWh, Daily production: {daily_production} kWh")

        except Exception as e:
            print(f"WARN Speicher-Relationen Berechnung Fehler: {e}")
            result['storage_consumption_ratio_percent'] = "0"
            result['storage_production_ratio_percent'] = "0"

    except Exception as e:
        print(f"WARN Formatierte Produktwerte Fehler: {e}")
        result['module_count_formatted'] = ''
        result['inverter_power_w_formatted'] = ''
        result['storage_capacity_formatted'] = ''
        result['storage_consumption_ratio_percent'] = "0"
        result['storage_production_ratio_percent'] = "0"

    return result
