"""Schneller Smoke-Test: Einzel-PDF mit echten Produktpreisen aus DB generieren.
"""
import io
import os
import json
from datetime import datetime

from product_db import list_products
from calculations import perform_calculations
from pdf_generator import generate_offer_pdf_with_main_templates


def pick_products():
    modules, inverters, storages = [], [], []
    for p in list_products() or []:
        cat = str(p.get("category", "")).lower()
        if "modul" in cat:
            modules.append(p)
        elif "wechselrichter" in cat:
            inverters.append(p)
        elif "speicher" in cat or "batterie" in cat or "battery" in cat:
            storages.append(p)
    if not modules:
        raise RuntimeError("Keine Module in der Produktdatenbank gefunden")
    if not inverters:
        raise RuntimeError(
            "Keine Wechselrichter in der Produktdatenbank gefunden")
    # Speicher optional
    storage = storages[0] if storages else None
    return modules[0], inverters[0], storage


def main():
    module, inverter, storage = pick_products()
    project_data = {
        "customer_data": {
            "salutation": "Herr",
            "first_name": "Max",
            "last_name": "Mustermann",
            "address": "Musterstraße 1",
            "zip_code": "12345",
            "city": "Musterstadt",
            "email": "max@example.com",
        },
        "project_details": {
            "module_quantity": 20,
            "selected_module_id": module.get("id"),
            "selected_inverter_id": inverter.get("id"),
            "selected_storage_id": storage.get("id") if storage else None,
            "include_storage": bool(storage),
            "include_additional_components": True,
        },
    }

    # Rechnen
    errors: list[str] = []
    analysis_results = perform_calculations(project_data, {}, errors)
    if errors:
        print("Berechnungswarnungen:")
        for e in errors[:10]:
            print("  -", e)

    print("WICHTIG: Ergebnissummen aus Berechnung:")
    print("  total_investment_netto:",
          analysis_results.get("total_investment_netto"))
    print("  total_investment_brutto:",
          analysis_results.get("total_investment_brutto"))
    print("  base_matrix_price_netto:",
          analysis_results.get("base_matrix_price_netto"))

    company_info = {"id": 1, "name": "Testfirma GmbH"}
    texts = {}
    inclusion_options = {"selected_sections": [
        "ProjectOverview", "TechnicalComponents", "CostDetails", "Economics",
        "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"
    ], "append_additional_pages_after_main8": False}

    pdf_bytes = generate_offer_pdf_with_main_templates(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        company_logo_base64=None,
        selected_title_image_b64=None,
        selected_offer_title_text="Ihr individuelles Solaranlagen-Angebot",
        selected_cover_letter_text="",
        sections_to_include=inclusion_options["selected_sections"],
        inclusion_options=inclusion_options,
        load_admin_setting_func=lambda k,
        d=None: d,
        save_admin_setting_func=lambda k,
        v: None,
        list_products_func=list_products,
        get_product_by_id_func=lambda pid: next(
            (p for p in list_products() if p.get("id") == pid),
            None),
        db_list_company_documents_func=lambda cid,
        dtype=None: [],
        active_company_id=1,
        texts=texts,
    )

    if pdf_bytes:
        out = os.path.join(
            os.path.dirname(__file__), f"single_pdf_test_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        with open(out, "wb") as f:
            f.write(pdf_bytes)
        print("PDF erzeugt:", out, "Größe:", len(pdf_bytes), "Bytes")
    else:
        print("Keine PDF-Bytes erzeugt!")


if __name__ == "__main__":
    main()
