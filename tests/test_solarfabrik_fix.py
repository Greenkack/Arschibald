#!/usr/bin/env python3
"""
Test ob Solarfabrik die korrekten Werte aus der Datenbank bekommt
"""

from product_db import get_product_by_model_name
from pdf_template_engine.placeholders import build_dynamic_data
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_solarfabrik_values():
    """Testet ob Solarfabrik die korrekten Werte bekommt"""

    print("🔧 Test Solarfabrik Werte")
    print("=" * 40)

    # Test verschiedene Solarfabrik Module
    solarfabrik_models = [
        "Solarfabrik Mono S4 Halfcut 410W",
        "Mono S4 Trendline 440W",
        "Mono S4 Trendline 445W"
    ]

    for model in solarfabrik_models:
        print(f"\n📦 Test Modell: {model}")

        # Direkt aus Datenbank abrufen
        db_product = get_product_by_model_name(model)
        if db_product:
            print("   DB-Werte:")
            print(
                f"     Zellentechnologie: {
                    db_product.get(
                        'cell_technology',
                        'N/A')}")
            print(
                f"     Modulaufbau: {
                    db_product.get(
                        'module_structure',
                        'N/A')}")
            print(f"     Zellentyp: {db_product.get('cell_type', 'N/A')}")
            print(f"     Version: {db_product.get('version', 'N/A')}")
        else:
            print("   ❌ Nicht in Datenbank gefunden")

        # Test mit PDF-Platzhalter-System
        project_data = {
            "project_details": {
                "selected_module_name": model
            }
        }

        dynamic_data = build_dynamic_data(project_data, {}, {})

        print("   PDF-Werte:")
        print(
            f"     Zellentechnologie: {
                dynamic_data.get(
                    'module_cell_technology',
                    'N/A')}")
        print(
            f"     Modulaufbau: {
                dynamic_data.get(
                    'module_structure',
                    'N/A')}")
        print(f"     Zellentyp: {dynamic_data.get('module_cell_type', 'N/A')}")
        print(f"     Version: {dynamic_data.get('module_version', 'N/A')}")

        # Vergleich
        if db_product:
            db_tech = db_product.get('cell_technology', '')
            pdf_tech = dynamic_data.get('module_cell_technology', '')

            if db_tech and pdf_tech == db_tech:
                print("   ✅ Werte stimmen überein")
            elif pdf_tech == "k.A.":
                print(f"   ❌ PDF zeigt k.A. statt DB-Wert: {db_tech}")
            else:
                print(
                    f"   ⚠️  Unterschiedliche Werte - DB: {db_tech}, PDF: {pdf_tech}")


def test_comparison_with_other_brands():
    """Vergleicht Solarfabrik mit anderen Marken"""

    print("\n🔍 Vergleich mit anderen Marken")
    print("=" * 40)

    test_models = [
        ("Solarfabrik", "Mono S4 Trendline 440W"),
        ("TrinaSolar", "Vertex S+ TSM-440"),
        ("Viessmann", "Vitovolt 300-DG M440HC")
    ]

    for brand, model in test_models:
        print(f"\n📦 {brand} - {model}")

        project_data = {
            "project_details": {
                "selected_module_name": f"{brand}PV - {model}" if brand != "Solarfabrik" else f"{brand}PV - {model}"
            }
        }

        dynamic_data = build_dynamic_data(project_data, {}, {})

        print(
            f"   Zellentechnologie: {
                dynamic_data.get(
                    'module_cell_technology',
                    'N/A')}")
        print(f"   Modulaufbau: {dynamic_data.get('module_structure', 'N/A')}")
        print(f"   Zellentyp: {dynamic_data.get('module_cell_type', 'N/A')}")
        print(f"   Version: {dynamic_data.get('module_version', 'N/A')}")


if __name__ == "__main__":
    test_solarfabrik_values()
    test_comparison_with_other_brands()

    print("\n🎯 Erwartung:")
    print("   Solarfabrik sollte die gleichen Werte wie TrinaSolar/Viessmann haben")
    print("   NICHT 'k.A.' anzeigen")
