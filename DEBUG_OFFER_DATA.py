#!/usr/bin/env python3
"""
Debug-Script zur Überprüfung der Multi-Offer Datenstruktur
"""
from pdf_template_engine.placeholders import _alias_value, fmt_number
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Prüfe, ob die rotier Produkt-IDs in den final_end_preis_formatted
# Platzhaltern verwendet werden

# Simuliere analysis_results mit UNTERSCHIEDLICHEN Preisen
analysis_results_company1 = {
    'total_investment_brutto': 9260,  # Firma 1
    'total_investment_netto': 7789
}

analysis_results_company2 = {
    'total_investment_brutto': 9800,  # Firma 2 (UNTERSCHIEDLICH!)
    'total_investment_netto': 8235
}

# Test: Was liefert _alias_value wenn analysis_results vorhanden?
print("\n=== TEST 1: _alias_value mit analysis_results ===")

result1 = _alias_value(
    fmt_number(
        analysis_results_company1.get('total_investment_brutto'),
        2,
        "€") if analysis_results_company1.get('total_investment_brutto') else None,
    fmt_number(
        analysis_results_company1.get('total_investment_netto'),
        2,
        "€") if analysis_results_company1.get('total_investment_netto') else None,
    None,  # Fallbacks
)
print(f"Firma 1 (analysis_results): {result1}")

result2 = _alias_value(
    fmt_number(
        analysis_results_company2.get('total_investment_brutto'),
        2,
        "€") if analysis_results_company2.get('total_investment_brutto') else None,
    fmt_number(
        analysis_results_company2.get('total_investment_netto'),
        2,
        "€") if analysis_results_company2.get('total_investment_netto') else None,
    None,  # Fallbacks
)
print(f"Firma 2 (analysis_results): {result2}")

print("\n=== ERGEBNIS ===")
print("✅ Wenn analysis_results UNTERSCHIEDLICH sind → Preise UNTERSCHIEDLICH")
print("❌ Wenn analysis_results GLEICH sind → Preise GLEICH")

# Das bedeutet: Das Problem ist wahrscheinlich NICHT in placeholders.py
# sondern in der Neuberechnung oder Datenübergabe!

print("\n=== HYPOTHESE ===")
print("Die analysis_results werden bei ALLEN Firmen mit den GLEICHEN Werten gefüllt!")
print("Das bedeutet, die Neuberechnung (perform_calculations) wird nicht mit unterschiedlichen Produkten aufgerufen.")
