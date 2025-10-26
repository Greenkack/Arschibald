# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_wirtschaftlichkeit.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from pdf_template_engine.placeholders import build_dynamic_data


# --- DEF BLOCK START: func run_test ---
def run_test():
    """
    Simuliert den Aufruf der build_dynamic_data Funktion mit realistischen
    Testdaten, um die Berechnungslogik für Seite 3 zu überprüfen.
    """
    print("\n--- Starte Test für die Wirtschaftlichkeitsberechnung (Seite 3) ---")

    # ========================================================================
    # DIES SIND SIMULIERTE DATEN, WIE SIE VON `calculations.py` KOMMEN SOLLTEN.
    # Wir benutzen die Werte aus deinem PDF-Beispiel, um die Logik zu prüfen.
    # ========================================================================
    mock_analysis_results = {
        # Strompreis aus deinem PDF-Beispiel
        "aktueller_strompreis_fuer_hochrechnung_euro_kwh": 0.4328,

        # Einspeisevergütung (7,86 ct/kWh)
        "einspeiseverguetung_eur_per_kwh": 0.0786,

        # Jährliche kWh-Werte aus deinem PDF-Beispiel.
        # Wir simulieren hier die monatlichen Listen, die `calculations.py`
        # erzeugt.
        "netzeinspeisung_kwh": 1482.0,
        "monthly_storage_charge_kwh": [410.0] * 12,      # Summe: 4920 kWh
        "monthly_storage_discharge_for_sc_kwh": [64.5] * 12,  # Summe: 774 kWh

        # Annahme für den Direktverbrauch, da dieser Wert nicht direkt im PDF
        # stand.
        # Annahme: 2500 kWh / Jahr
        "monthly_direct_self_consumption_kwh": [208.33] * 12
    }

    # Leere Dictionaries für die anderen Argumente, da wir sie hier nicht
    # brauchen.
    mock_project_data = {
        "customer_data": {
            "first_name": "Test",
            "last_name": "Kunde"}}
    mock_company_info = {}

    # ========================================================================
    # Wir rufen die eigentliche Funktion auf, die in placeholders.py steht.
    # ========================================================================
    dynamic_data = build_dynamic_data(
        mock_project_data,
        mock_analysis_results,
        mock_company_info
    )

    # ========================================================================
    # Wir prüfen die Ergebnisse, die für die Seite 3 relevant sind.
    # ========================================================================
    print("\n--- ERGEBNISSE DER BERECHNUNG ---")

    keys_to_show = [
        "self_consumption_savings_eur",  # Sollte "Direkt" ersetzen
        "grid_feed_in_revenue_eur",       # Sollte "Einspeisung" ersetzen
        "battery_usage_savings_eur",      # Sollte "Speichernutzung" ersetzen
        "battery_surplus_feed_in_eur",    # Sollte "Überschuss" ersetzen
        "total_annual_savings_eur"        # Sollte "Gesamt" ersetzen
    ]

    all_keys_found = True
    for key in keys_to_show:
        if key in dynamic_data:
            print(f"  - Platzhalter '{key}': '{dynamic_data[key]}'")
        else:
            print(f"  - PLATZHALTER '{key}': !!! FEHLT IM ERGEBNIS !!!")
            all_keys_found = False

    if all_keys_found:
        print("\n[SUCCESS] Alle erwarteten Platzhalter für Seite 3 wurden berechnet.")
    else:
        print(
            "\n[FEHLER] Nicht alle Platzhalter wurden im Ergebnis gefunden. Bitte `placeholders.py` prüfen.")

    print("--- Test beendet ---")
# --- DEF BLOCK END ---
