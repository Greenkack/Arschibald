#!/usr/bin/env python3
"""
Erstelle ein Test-PDF mit Logos
"""

from pdf_generator import generate_offer_pdf_with_main_templates
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_test_pdf_with_logos():
    """Erstelle Test-PDF mit Logos"""
    print("🔧 ERSTELLE TEST-PDF MIT LOGOS")
    print("=" * 50)

    # Test-Daten mit bekannten Logo-Herstellern
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann",
            "address": "Musterstraße 1",
            "zip_code": "12345",
            "city": "Musterstadt",
            "email": "max@beispiel.de"
        },
        "project_details": {
            "roof_area": 50,
            "roof_orientation": "Süd"
        },
        "selected_products": {
            "module": {
                "product_id": 1,
                "brand_name": "Huawei",
                "product_name": "SUN2000-8KTL-M1"
            },
            "inverter": {
                "product_id": 2,
                "brand_name": "GoodWe",
                "product_name": "GW8K-ET"
            },
            "storage": {
                "product_id": 3,
                "brand_name": "BYD",
                "product_name": "Battery-Box Premium HVM"
            }
        }
    }

    analysis_results = {
        "total_investment_netto": 15000,
        "total_investment_brutto": 17850,
        "anlage_kwp": 8.5,
        "annual_pv_production_kwh": 8500,
        "final_price": 15000
    }

    company_info = {
        "name": "Solar GmbH",
        "street": "Solarweg 123",
        "zip_code": "54321",
        "city": "Sonnenstein",
        "phone": "0123-456789",
        "email": "info@solar-gmbh.de"
    }

    try:
        # Temporäre Datei für PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            temp_pdf_path = tmp_file.name

        print(f"📄 Erstelle PDF: {temp_pdf_path}")

        # PDF generieren (nur Template-Version)
        pdf_bytes = generate_offer_pdf_with_main_templates(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            template_type="6seiten"
        )

        if pdf_bytes:
            # PDF-Bytes in Datei schreiben
            with open(temp_pdf_path, 'wb') as f:
                f.write(pdf_bytes)

            file_size = len(pdf_bytes)
            print("✅ PDF erfolgreich erstellt!")
            print(f"   Datei: {temp_pdf_path}")
            print(f"   Größe: {file_size:,} Bytes")
            print("\n💡 Öffne die PDF-Datei und prüfe Seite 4 auf die Logos!")
            return temp_pdf_path
        print("❌ PDF-Generierung fehlgeschlagen")
        return None

    except Exception as e:
        print(f"❌ Fehler bei PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    pdf_path = create_test_pdf_with_logos()
    if pdf_path:
        print(f"\n🎯 PDF erstellt: {pdf_path}")
        print("   Bitte öffne die Datei und prüfe Seite 4 auf die Hersteller-Logos!")
        print("   Die Logos sollten bei den Positionen 'Logomodul', 'Logoricht', 'Logoakkus' erscheinen.")
    else:
        print("\n❌ PDF-Test fehlgeschlagen")
