# === AUTO-GENERATED INSERT PATCH ===
# target_module: multi_offer_generator_new.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import logging
import os
import tempfile
from datetime import datetime
import streamlit as st
import zipfile
import io
import re
from typing import Dict, List, Any
import traceback

# --- DEF BLOCK START: func render_multi_offer_generator ---


def render_multi_offer_generator(
    texts,
    project_data_doc=None,
     calc_results_doc=None):
    """
    Hauptfunktion für den Multi-Firmen-Angebotsgenerator
    Wird vom GUI-Modul aufgerufen
    """
    st.header(" Multi-Firmen-Angebotsgenerator")
    st.markdown(
        "Erstellen Sie Angebote für mehrere Firmen basierend auf Ihren Projektdaten.")

    # Generator initialisieren
    if "mog_generator" not in st.session_state:
        st.session_state.mog_generator = MultiCompanyOfferGenerator()

    generator = st.session_state.mog_generator
    generator.initialize_session_state()

    # Texte für das System setzen
    st.session_state["TEXTS"] = texts

    # Projektdaten übernehmen falls vorhanden
    if project_data_doc and "customer_data" in project_data_doc:
        if not st.session_state.multi_offer_customer_data.get("last_name"):
            st.session_state.multi_offer_customer_data = project_data_doc["customer_data"]
            st.session_state.multi_offer_project_data = project_data_doc

    # Berechungsergebnisse übernehmen falls vorhanden
    if calc_results_doc:
        st.session_state.multi_offer_calc_results = calc_results_doc

    # UI rendern
    try:
        # Schritt 1: Kundendaten
        customer_data_ready = generator.render_customer_input()

        if customer_data_ready:
            st.markdown("---")
            # Schritt 2: Firmenauswahl
            companies_selected = generator.render_company_selection()

            if companies_selected:
                st.markdown("---")                # Schritt 3: Konfiguration
                config_ready = generator.render_offer_configuration()

                if config_ready:
                    st.markdown("---")
                    # Schritt 4: PDF-Generierung
                    generator.generate_multi_offers()

    except Exception as e:
        st.error(f"Fehler im Multi-Angebotsgenerator: {str(e)}")
        logging.error(f"Fehler in render_multi_offer_generator: {e}")
        logging.error(f"Exception Typ: {type(e).__name__}")
        logging.error(f"Exception Details: {repr(e)}")
        # Zusätzliche Debug-Info für company_name Fehler
        if "company_name" in str(
            e) and "not associated with a value" in str(e):
            logging.error(
                "COMPANY_NAME DEBUG: Dies ist der spezifische company_name Fehler")
            logging.error(f"Traceback Details verfügbar in den Logs")
        st.info("Bitte versuchen Sie es erneut oder wenden Sie sich an den Support.")
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: method MultiCompanyOfferGenerator.get_rotated_products_for_company ---
   def get_rotated_products_for_company(self, company_index: int, base_settings: Dict) -> Dict:
        """
        Vollständig flexible Produktrotation für verschiedene Firmen
        company_index: 0 = erste Firma, 1 = zweite Firma, etc.
        Unterstützt: Lineare Rotation, Zufällige Auswahl, Kategorie-spezifische Schritte
        """
        rotated_settings = base_settings.copy()

        if not base_settings.get("enable_product_rotation", False):
            return rotated_settings

        try:
            rotation_mode = base_settings.get("rotation_mode", "linear")

            # Kategorien mit individuellen Rotation-Schritten
            categories = ["module", "inverter", "storage"]

            for category in categories:
                base_id_key = f"selected_{category}_id"
                base_id = base_settings.get(base_id_key)

                if not base_id or category not in self.products:
                    continue

                available_products = self.products[category]
                if len(available_products) <= 1:
                    # Nur ein Produkt verfügbar - behalte das Original
                    logging.info(f"Produktrotation {category}: Nur 1 Produkt verfügbar, behalte Original")
                    continue

                # Finde Index des Basisprodukts
                base_index = -1
                for i, product in enumerate(available_products):
                    if product.get("id") == base_id:
                        base_index = i
                        break

                if base_index == -1:
                    logging.warning(f"Produktrotation {category}: Basisprodukt nicht gefunden")
                    continue

                # Bestimme Rotation-Schritt basierend auf Modus
                if rotation_mode == "kategorie-spezifisch":
                    rotation_step = base_settings.get(f"{category}_rotation_step", 1)
                elif rotation_mode == "zufällig":
                    import random
                    rotation_step = random.randint(1, len(available_products) - 1)
                else:  # linear
                    rotation_step = base_settings.get("product_rotation_step", 1)

                # Berechne neuen Index mit flexiblem Schritt
                new_index = (base_index + (company_index * rotation_step)) % len(available_products)
                rotated_product = available_products[new_index]
                rotated_settings[base_id_key] = rotated_product.get("id")

                logging.info(f"Produktrotation {category}: Firma {company_index +1} -> {rotated_product.get('model_name', 'Unknown')} (Schritt: {rotation_step}, Verfügbare: {len(available_products)})")

        except Exception as e:
            logging.warning(f"Fehler bei Produktrotation: {e}")

        return rotated_settings
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: method MultiCompanyOfferGenerator.apply_price_scaling ---
   def apply_price_scaling(self, company_index: int, base_settings: Dict, calc_results: Dict) -> Dict:
        """
        Vollständig flexible Preisstaffelung für verschiedene Firmen
        Unterstützt: Linear, Exponentiell, Custom-Faktoren
        company_index: 0 = erste Firma, 1 = zweite Firma, etc.
        """
        if company_index == 0:
            return calc_results  # Erste Firma behält Originalpreis

        price_increment = base_settings.get("price_increment_percent", 0)
        if price_increment == 0:
            return calc_results  # Keine Preissteigerung

        scaled_results = calc_results.copy()

        try:
            # Bestimme Preisfaktor basierend auf Berechnungsmodus
            calc_mode = base_settings.get("price_calculation_mode", "linear")

            if calc_mode == "linear":
                price_factor = 1.0 + (company_index * price_increment / 100.0)
            elif calc_mode == "exponentiell":
                exponent = base_settings.get("price_exponent", 1.03)
                price_factor = exponent ** company_index
            elif calc_mode == "custom":
                try:
                    import json
                    custom_factors = json.loads(base_settings.get("custom_price_factors", "[1.0]"))
                    price_factor = custom_factors[company_index] if company_index < len(custom_factors) else custom_factors[-1]
                except BaseException:
                    # Fallback auf linear
                    price_factor = 1.0 + (company_index * price_increment / 100.0)
            else:
                price_factor = 1.0

            logging.info(f"Preisstaffelung: Firma {company_index +1}, Modus: {calc_mode}, Faktor: {price_factor:.3f}")

            # Preisbezogene Felder skalieren
            price_fields = [
                'total_investment_netto',
                'total_investment_brutto',
                'module_cost_total',
                'inverter_cost_total',
                'storage_cost_total',
                'additional_costs',
                'installation_cost',
                'total_cost_euro',
                'wallbox_cost',
                'ems_cost',
                'optimizer_cost',
                'carport_cost',
                'notstrom_cost',
                'tierabwehr_cost'
            ]

            for field in price_fields:
                if field in scaled_results and isinstance(scaled_results[field], (int, float)):
                    original_value = scaled_results[field]
                    scaled_results[field] = original_value * price_factor

            # Wirtschaftlichkeitsberechnungen intelligent anpassen
            if 'amortization_time_years' in scaled_results and isinstance(scaled_results['amortization_time_years'], (int, float)):
                # Längere Amortisationszeit durch höhere Kosten (aber begrenzt)
                amort_factor = min(price_factor, 1.5)  # Maximal 50% längere Amortisation
                scaled_results['amortization_time_years'] = scaled_results['amortization_time_years'] * amort_factor

            # ROI anpassen (niedriger durch höhere Investition)
            roi_fields = ['roi_percent_year1', 'roi_percent_year10', 'roi_percent_year20']
            for roi_field in roi_fields:
                if roi_field in scaled_results and isinstance(scaled_results[roi_field], (int, float)):
                    scaled_results[roi_field] = scaled_results[roi_field] / price_factor
              # Jährliche Ersparnisse bleiben gleich (da gleiche Anlage, nur teurer)
            # annual_savings bleibt unverändert

        except Exception as e:
            logging.warning(f"Fehler bei Preisstaffelung für Firma {company_index +1}: {e}")

        return scaled_results
# --- DEF BLOCK END ---
