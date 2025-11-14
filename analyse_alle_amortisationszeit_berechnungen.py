"""
VOLLSTÄNDIGE ANALYSE: AMORTISATIONSZEIT-BERECHNUNGEN
Zeigt ALLE Stellen wo Amortisationszeit berechnet wird
"""

print("=" * 120)
print("ANALYSE: WO WIRD AMORTISATIONSZEIT BERECHNET?")
print("=" * 120)

print("\n📍 HAUPTBERECHNUNG 1: calculations.py (Zeile 3640-3698)")
print("-" * 120)
print("""
FUNKTION: perform_calculations()
ORT: calculations.py, Zeile 3692-3698
FORMEL: final_investment_amount / annual_financial_benefit_year1

PREIS-LOGIK (Priorität):
1. [OK] FINAL_END_PREIS aus st.session_state['final_pricing_data']
2. [OK] final_end_preis aus st.session_state['project_data']['project_details']
3. [ERROR] final_modified_price_net (ALT!)
4. [ERROR] final_price_with_provision (ALT!)
5. [ERROR] final_offer_price_net (ALT!)
6. [ERROR] total_investment_netto (Fallback)

GESPEICHERT ALS:
- results["amortization_time_years"]

ZUSÄTZLICH:
- Admin Cheat kann Wert überschreiben (Zeile 3699-3732)
- Wird in results["amortization_time_years"] gespeichert
""")

print("\n📍 BERECHNUNG 2: analysis.py (Zeile 403)")
print("-" * 120)
print("""
FUNKTION: _calculate_amortization_time()
ORT: analysis.py, Zeile 403
PROBLEM: [ERROR] FUNKTION EXISTIERT NICHT!

CODE:
    amortisation_years = _calculate_amortization_time(final_price, annual_savings)

FEHLER:
- Die Funktion wird aufgerufen, aber ist nirgendwo definiert!
- Vermutlich sollte sie importiert werden aus calculations.py
- Das könnte zu einem Runtime-Error führen!
""")

print("\n📍 PDF-SEITE 1: placeholders.py (Zeile 892-899)")
print("-" * 120)
print("""
FUNKTION: generate_placeholders()
ORT: pdf_template_engine/placeholders.py, Zeile 892-899

CODE:
    amort_years = (
        analysis_results.get("amortization_time_years")
        or analysis_results.get("amortisationszeit_jahre")
    )
    if amort_years is not None:
        result["amortization_time"] = fmt_number(amort_years, 2, "Jahre")

VERWENDET:
- Liest aus analysis_results["amortization_time_years"] (von calculations.py)
- Fallback: analysis_results["amortisationszeit_jahre"]
- Formatiert mit 2 Dezimalstellen
- Speichert in result["amortization_time"] für PDF

PDF-PLACEHOLDER:
- "29.150,00 EUR*": "amortization_time"  (Zeile 152)
""")

print("\n📍 WEITERE BERECHNUNGEN:")
print("-" * 120)

berechnungen = [
    {
        "nr": 4,
        "name": "calculations_extended.py",
        "zeile": "104-109",
        "funktion": "calculate_payback_period()",
        "formel": "investment_costs / annual_savings",
        "typ": "Statische Amortisation"
    },
    {
        "nr": 5,
        "name": "calculations_extended.py",
        "zeile": "36-56",
        "funktion": "calculate_dynamic_payback_period()",
        "formel": "Mit jährlicher Preissteigerung",
        "typ": "Dynamische Amortisation"
    },
    {
        "nr": 6,
        "name": "calculations_heatpump.py",
        "zeile": "116-120",
        "funktion": "calculate_heatpump_economics()",
        "formel": "investment_cost / annual_savings",
        "typ": "Wärmepumpen-Amortisation"
    },
    {
        "nr": 7,
        "name": "live_calculation_engine.py",
        "zeile": "77-87",
        "funktion": "calculate_live_results()",
        "formel": "final_price / annual_income",
        "typ": "Live-Berechnung"
    },
    {
        "nr": 8,
        "name": "analysis.py",
        "zeile": "9313",
        "funktion": "Szenario-Berechnung",
        "formel": "investment / savings_scenario",
        "typ": "Szenario-Analyse"
    },
]

for b in berechnungen:
    print(f"\n{b['nr']}. {b['name']} (Zeile {b['zeile']})")
    print(f"   Funktion: {b['funktion']}")
    print(f"   Formel: {b['formel']}")
    print(f"   Typ: {b['typ']}")

print("\n" + "=" * 120)
print("CO2-AMORTISATION (Separate Berechnung)")
print("=" * 120)

co2_berechnungen = [
    {
        "name": "calculations.py",
        "zeile": "1296-1307",
        "funktion": "calculate_co2_impact()",
        "formel": "manufacturing_co2 / net_annual_saving",
        "key": "co2_payback_years"
    },
    {
        "name": "calculations.py",
        "zeile": "2313-2338",
        "funktion": "Weitere CO2-Berechnung",
        "formel": "carbon_payback_time",
        "key": "carbon_payback_time"
    },
    {
        "name": "calculations_extended.py",
        "zeile": "371-378",
        "funktion": "calculate_co2_payback_time()",
        "formel": "Spezifisch für CO2",
        "key": "co2_payback_time"
    },
]

for co2 in co2_berechnungen:
    print(f"\n• {co2['name']} (Zeile {co2['zeile']})")
    print(f"  Funktion: {co2['funktion']}")
    print(f"  Formel: {co2['formel']}")
    print(f"  Key: {co2['key']}")

print("\n" + "=" * 120)
print("ALLE VERWENDETEN KEYS")
print("=" * 120)

keys = [
    ("amortization_time_years", "calculations.py → analysis_results", "[OK] HAUPTKEY für PDF Seite 1"),
    ("amortisationszeit_jahre", "Fallback in placeholders.py", "[ERROR] Fallback (alt)"),
    ("amortization_time", "PDF Placeholder", "[OK] Für PDF-Template"),
    ("payback_time", "Verschiedene Module", "[WARNING] Mehrfachverwendung"),
    ("payback_period", "Alte Berechnungen", "[ERROR] Veraltet"),
    ("payback_period_years", "calculations_heatpump.py", "[WARNING] Nur für Wärmepumpe"),
    ("co2_payback_years", "CO2-Amortisation", "[WARNING] Nur für CO2"),
    ("carbon_payback_time", "CO2-Amortisation", "[WARNING] Nur für CO2"),
    ("amortisation_years", "analysis.py (lokal)", "[ERROR] Lokal, nicht gespeichert"),
]

for key, quelle, status in keys:
    print(f"\n{key:30} | {quelle:45} | {status}")

print("\n" + "=" * 120)
print("🔥 KRITISCHE PROBLEME")
print("=" * 120)

probleme = [{"problem": "analysis.py ruft _calculate_amortization_time() auf",
             "zeile": "403",
             "fehler": "[ERROR] FUNKTION EXISTIERT NICHT!",
             "auswirkung": "RuntimeError wenn analysis.py diese Zeile erreicht"},
            {"problem": "Alte Preis-Keys haben Fallback-Priorität",
             "zeile": "calculations.py 3671-3683",
             "fehler": "[WARNING] final_modified_price_net, final_price_with_provision",
             "auswirkung": "Könnte falschen Preis verwenden wenn neue Keys fehlen"},
            {"problem": "Mehrere verschiedene Keys für gleiche Sache",
             "zeile": "Überall",
             "fehler": "[WARNING] amortization_time_years vs payback_time vs payback_period",
             "auswirkung": "Verwirrung, Inkonsistenz"},
            {"problem": "PDF könnte alten Key verwenden",
             "zeile": "placeholders.py 892-899",
             "fehler": "[WARNING] Fallback auf amortisationszeit_jahre",
             "auswirkung": "Wenn FINAL_END_PREIS nicht verwendet wird → falsche Amortisation"},
            ]

for i, p in enumerate(probleme, 1):
    print(f"\n{i}. {p['problem']}")
    print(f"   Zeile: {p['zeile']}")
    print(f"   Fehler: {p['fehler']}")
    print(f"   Auswirkung: {p['auswirkung']}")

print("\n" + "=" * 120)
print("[IDEA] EMPFEHLUNG")
print("=" * 120)

print("""
1. SOFORT FIXEN:
   [ERROR] analysis.py Zeile 403: _calculate_amortization_time() entfernen oder implementieren

2. PREIS FÜR AMORTISATION PRÜFEN:
   [OK] Sicherstellen dass calculations.py FINAL_END_PREIS verwendet
   [ERROR] Alte Keys (final_modified_price_net, etc.) auskommentieren oder entfernen

3. KEYS VEREINHEITLICHEN:
   → Nur noch "amortization_time_years" verwenden
   → Alle anderen Keys (payback_time, payback_period) eliminieren

4. PDF-PLACEHOLDER PRÜFEN:
   → Sicherstellen dass "amortization_time" den richtigen Wert aus
     "amortization_time_years" bekommt
   → Fallback auf "amortisationszeit_jahre" entfernen

5. DEBUG AKTIVIEREN:
   → In calculations.py DEBUG-Prints sind schon drin (Zeile 3657-3689)
   → Log anschauen welchen Preis die Amortisation verwendet
""")

print("\n" + "=" * 120)
print("ANALYSE ABGESCHLOSSEN")
print("=" * 120)
