#!/usr/bin/env python3
"""
Test für die rechtsbündige Ausrichtung der Seite 1 Werte
"""

from pdf_template_engine.placeholders import build_dynamic_data
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_page1_right_aligned_values():
    """Teste die 3 dynamischen Werte auf Seite 1 für rechtsbündige Ausrichtung"""

    project_data = {}
    analysis_results = {
        "anlage_kwp": 8.4,
        "annual_pv_production_kwh": 8251.92,
        "amortization_time_years": 12.5,
    }

    result = build_dynamic_data(project_data, analysis_results, {})

    print("=== Seite 1: Werte die jetzt rechtsbündig ausgerichtet werden ===")
    print(f"Anlagengröße (anlage_kwp): '{result.get('anlage_kwp')}'")
    print(
        f"Stromproduktion (annual_pv_production_kwh): '{
            result.get('annual_pv_production_kwh')}'")
    print(
        f"Amortisationszeit (amortization_time): '{
            result.get('amortization_time')}'")

    print("\n=== Seite 3: Beibehaltene rechtsbündige Werte ===")
    print(f"Ausrichtung: '{result.get('orientation_text')}'")
    print(f"Dachneigung: '{result.get('roof_inclination_text')}'")


if __name__ == "__main__":
    test_page1_right_aligned_values()
