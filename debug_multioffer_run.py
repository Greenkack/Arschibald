"""Kleines Debug-Skript: startet die Multi-Offer-Pipeline und loggt calc_input/Ergebnisse für 5 Firmen.
Nur für lokale Debug-Zwecke: importiert die vorhandenen Module und ruft _prepare_offer_data + _generate_company_pdf auf.
"""
import logging

from multi_offer_generator import MultiCompanyOfferGenerator

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    gen = MultiCompanyOfferGenerator()
    # Erstelle minimale Testdaten: customer_data, project_data, 5
    # company_settings
    customer_data = {"name": "Testkunde"}
    project_data = {
        "project_details": {
            "module_quantity": 20
        }
    }
    companies = []
    # Simuliere 5 Firmen mit rotierten selected_module_id/inverter/storage
    for i in range(5):
        comp = {
            "id": f"C{i + 1}",
            "name": f"Firma {i + 1}",
        }
        # company_settings: unterschiedliche module/inverter/storage ids (nur
        # als Demo-IDs)
        settings = {
            "selected_module_id": 11 + i,  # 11,12,13,14,15
            "selected_inverter_id": 322 + i,
            "selected_storage_id": 187 + i,
            "module_quantity": 20
        }
        companies.append((comp, settings))

    for idx, (company, settings) in enumerate(companies):
        logging.info(f"--- RUN für Firma {idx + 1} ---")
        offer_data = gen._prepare_offer_data(
            customer_data, company, settings, project_data, idx)
        # _generate_company_pdf gibt bytes zurück; wir rufen es, damit die
        # Debug-Logs in multi_offer_generator auftreten
        try:
            pdf_bytes = gen._generate_company_pdf(offer_data, company, idx)
            logging.info(
                f"PDF generiert, bytes length: {
                    len(pdf_bytes) if pdf_bytes else 'None'}")
        except Exception:
            logging.exception("Fehler beim Generieren der PDF (Debug run)")
