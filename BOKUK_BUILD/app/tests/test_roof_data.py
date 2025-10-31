#!/usr/bin/env python3
"""
Test für Dachneigung und Dachausrichtung aus Bedarfsanalyse
"""

from pdf_template_engine.placeholders import build_dynamic_data
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_roof_data_from_analysis():
    """Teste, ob Dachneigung und Ausrichtung aus Bedarfsanalyse korrekt gelesen werden"""

    print("=== Test 1: Daten direkt in project_details ===")
    project_data = {
        "project_details": {
            "roof_orientation": "Südwest",
            "roof_inclination_deg": 45
        }
    }
    analysis_results = {}
    company_info = {}

    result = build_dynamic_data(project_data, analysis_results, company_info)

    print(f"orientation_text: '{result.get('orientation_text')}'")
    print(f"roof_inclination_text: '{result.get('roof_inclination_text')}'")

    print("\n=== Test 2: Daten in project_details nested ===")
    project_data = {
        "project_details": {
            "roof_orientation": "Ost",
            "roof_inclination_deg": 30
        }
    }

    result = build_dynamic_data(project_data, analysis_results, company_info)

    print(f"orientation_text: '{result.get('orientation_text')}'")
    print(f"roof_inclination_text: '{result.get('roof_inclination_text')}'")

    print("\n=== Test 3: Fallback-Verhalten ===")
    project_data = {}

    result = build_dynamic_data(project_data, analysis_results, company_info)

    print(f"orientation_text: '{result.get('orientation_text')}'")
    print(f"roof_inclination_text: '{result.get('roof_inclination_text')}'")


if __name__ == "__main__":
    test_roof_data_from_analysis()
