# multi_offer_generator.py
"""
Multi-Firmen-Angebotsgenerator
Erstellt mehrere Angebote für verschiedene Firmen mit einem Klick
VERSION 3.0 - KORRIGIERT: Verwendet Kundendaten aus Projekt und Bedarfsanalyse
"""
import io
import logging
import os
import zipfile
from copy import deepcopy
from datetime import datetime
from typing import Any

import streamlit as st

try:
    from tqdm import tqdm
except ImportError:
    # Fallback, falls tqdm nicht installiert ist
    print("Hinweis: Für eine Fortschrittsanzeige installieren Sie 'tqdm' via 'pip install tqdm'.")
    tqdm = lambda x, **kwargs: x

# Import der bestehenden Module
try:
    from calculations import calculate_offer_details, perform_calculations
    from database import (
        get_company,
        get_db_connection,
        list_companies,
        list_company_documents,
        load_admin_setting,
        save_admin_setting,
    )
    from pdf_generator import create_offer_pdf, merge_pdfs
    from pdf_generator import (
        generate_offer_pdf_with_main_templates as generate_offer_pdf,
    )
    from product_db import get_product_by_id, list_products

    # PDF Output Directory - lokale Definition statt Import
    PDF_OUTPUT_DIRECTORY = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "data", "pdf_output")
except ImportError as e:
    st.error(f"Import-Fehler im Multi-Angebots-Generator: {e}")
    # Fallback für PDF_OUTPUT_DIRECTORY
    PDF_OUTPUT_DIRECTORY = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "data", "pdf_output")


def get_text_mog(key: str, fallback: str) -> str:
    """Hilfsfunktion für Texte"""
    return st.session_state.get("TEXTS", {}).get(key, fallback)


class MultiCompanyOfferGenerator:
    """Generator für Multi-Firmen-Angebote - übernimmt Kundendaten aus Projekt"""

    def __init__(self):
        self.customer_data = {}
        self.selected_companies = []
        self.offer_settings = {}
        self.products = self.load_all_products()

    def initialize_session_state(self):
        """Initialisiert Session State"""
        if "multi_offer_customer_data" not in st.session_state:
            st.session_state.multi_offer_customer_data = {}
        if "multi_offer_selected_companies" not in st.session_state:
            st.session_state.multi_offer_selected_companies = []
        if "multi_offer_settings" not in st.session_state:
            st.session_state.multi_offer_settings = {
                "module_quantity": 20,
                "include_storage": True,
            }
        # Erweiterte PDF-Ausgabe Flags (pro Firma) + Master-Schalter
        if "multi_offer_company_extended" not in st.session_state:
            st.session_state.multi_offer_company_extended = {}
        if "multi_offer_extend_all" not in st.session_state:
            st.session_state.multi_offer_extend_all = False

    def load_all_products(self) -> dict[str, list[dict[str, Any]]]:
        """Lädt alle Produkte und kategorisiert sie."""
        try:
            all_products = list_products() if callable(list_products) else []
            categorized = {"module": [], "inverter": [], "storage": []}
            for p in all_products:
                cat = p.get("category", "Sonstiges").lower()
                if "modul" in cat:
                    categorized["module"].append(p)
                elif "wechselrichter" in cat:
                    categorized["inverter"].append(p)
                elif "speicher" in cat or "battery" in cat:
                    categorized["storage"].append(p)
            return categorized
        except Exception as e:
            st.warning(f"Konnte Produkte nicht laden: {e}")
            return {"module": [], "inverter": [], "storage": []}

    def get_available_companies(self) -> list[dict[str, Any]]:
        """Lädt verfügbare Firmen"""
        try:
            return list_companies() if callable(list_companies) else []
        except Exception as e:
            st.warning(f"Konnte Firmen nicht laden: {e}")
            return []

    def render_customer_input(self):
        """Übernimmt Kundendaten aus der Projekt-/Bedarfsanalyse"""
        st.subheader("Schritt 1: Kundendaten aus Projekt übernehmen")

        # Versuche Kundendaten aus project_data zu übernehmen
        project_data = st.session_state.get("project_data", {})
        customer_data = project_data.get("customer_data", {})

        if customer_data:
            # Daten gefunden - anzeigen und übernehmen
            st.success(" Kundendaten aus Projekt-/Bedarfsanalyse gefunden!")

            cols = st.columns(2)
            with cols[0]:
                st.write("**Kundendaten:**")
                st.write(
                    f"Name: {
                        customer_data.get(
                            'first_name',
                            '')} {
                        customer_data.get(
                            'last_name',
                            '')}")
                st.write(
                    f"E-Mail: {customer_data.get('email', 'Nicht angegeben')}")
                st.write(
                    f"Telefon: {
                        customer_data.get(
                            'phone',
                            'Nicht angegeben')}")

            with cols[1]:
                st.write("**Adresse:**")
                st.write(
                    f"Straße: {
                        customer_data.get(
                            'address',
                            'Nicht angegeben')}")
                st.write(
                    f"PLZ/Ort: {customer_data.get('zip_code', '')} {customer_data.get('city', '')}")

            # Kundendaten in multi_offer_customer_data übernehmen
            st.session_state.multi_offer_customer_data = customer_data.copy()

            # Projektdaten anzeigen falls verfügbar
            if project_data.get("consumption_data"):
                st.write("**Verbrauchsdaten:**")
                consumption = project_data["consumption_data"]
                st.write(
                    f"Jahresverbrauch: {
                        consumption.get(
                            'annual_consumption',
                            'N/A')} kWh")
                st.write(
                    f"Strompreis: {
                        consumption.get(
                            'electricity_price',
                            'N/A')} €/kWh")
              # Projektdaten auch in session state speichern für
              # PDF-Generierung
            st.session_state.multi_offer_project_data = project_data.copy()

        else:
            # Fallback: Manuelle Eingabe wenn keine Projektdaten vorhanden
            st.warning(
                " Keine Kundendaten aus Projekt gefunden. Bitte zuerst die Projekt-/Bedarfsanalyse durchführen oder Daten manuell eingeben.")

            with st.form("customer_data_form_multi"):
                cols = st.columns(2)
                data = st.session_state.multi_offer_customer_data

                data["salutation"] = cols[0].selectbox(
                    "Anrede", [
                        "Herr", "Frau", "Divers"], index=[
                        "Herr", "Frau", "Divers"].index(
                        data.get(
                            "salutation", "Herr")), )
                data["first_name"] = cols[0].text_input(
                    "Vorname", value=data.get("first_name", "")
                )
                data["last_name"] = cols[1].text_input(
                    "Nachname", value=data.get("last_name", "")
                )
                data["address"] = st.text_input(
                    "Straße & Hausnummer", value=data.get("address", "")
                )
                data["zip_code"] = cols[0].text_input(
                    "PLZ", value=data.get("zip_code", ""))
                data["city"] = cols[1].text_input(
                    "Ort", value=data.get("city", ""))
                data["email"] = st.text_input(
                    "E-Mail", value=data.get("email", ""))
                data["phone"] = st.text_input(
                    "Telefon", value=data.get("phone", ""))

                if st.form_submit_button("Kundendaten speichern"):
                    st.success("Kundendaten gespeichert.")

        return bool(
            st.session_state.multi_offer_customer_data.get("first_name"))

    def render_company_selection(self):
        """Schritt 2: Firmenauswahl - Vollständig flexibel für 2-20+ Firmen"""
        st.subheader("Schritt 2: Firmen für Angebote auswählen")

        all_companies = self.get_available_companies()
        if not all_companies:
            st.warning(
                "Keine Firmen in der Datenbank gefunden. Bitte im Admin-Panel anlegen.")
            return False

        # Erweiterte Firmenauswahl-UI
        cols = st.columns([3, 1])

        with cols[0]:
            company_options = {c["name"]: c["id"] for c in all_companies}
            selected_company_names = st.multiselect(
                f"Wählen Sie 2-{len(all_companies)} Firmen aus (unbegrenzt):",
                options=list(company_options.keys()),
                default=[
                    name
                    for name, cid in company_options.items()
                    if cid in st.session_state.multi_offer_selected_companies
                ],
                help=f"Verfügbare Firmen: {len(all_companies)} | Keine Begrenzung auf 5 Firmen!"
            )

        with cols[1]:
            # Schnellauswahl-Buttons
            if st.button(" Alle auswählen"):
                st.session_state.multi_offer_selected_companies = list(
                    company_options.values())
                st.rerun()
            if st.button(" Alle abwählen"):
                st.session_state.multi_offer_selected_companies = []
                st.rerun()

        st.session_state.multi_offer_selected_companies = [
            company_options[name] for name in selected_company_names
        ]

        # Pflege der per-Firma Extended-Flags entsprechend aktueller Auswahl
        # Entferne nicht mehr ausgewählte Firmen aus dem Flag-Dict
        current_ids = set(st.session_state.multi_offer_selected_companies)
        st.session_state.multi_offer_company_extended = {
            cid: val for cid,
            val in st.session_state.multi_offer_company_extended.items() if cid in current_ids}
        # Füge neu ausgewählte Firmen mit Default False hinzu
        for cid in current_ids:
            st.session_state.multi_offer_company_extended.setdefault(
                cid, False)

        # Erweiterte Firmen-Übersicht
        if st.session_state.multi_offer_selected_companies:
            num_companies = len(
                st.session_state.multi_offer_selected_companies)

            # Status-Übersicht
            if num_companies == 1:
                st.info(
                    "ℹ **1 Firma ausgewählt** - Für echte Multi-Angebote mindestens 2 Firmen empfohlen.")
            elif num_companies <= 5:
                st.success(
                    f" **{num_companies} Firmen ausgewählt** - Optimale Anzahl für Vergleichsangebote!")
            elif num_companies <= 10:
                st.success(
                    f" **{num_companies} Firmen ausgewählt** - Umfassende Marktabdeckung!")
            else:
                st.success(
                    f" **{num_companies} Firmen ausgewählt** - Maximale Auswahl für Kunden!")

            # Firmen-Vorschau in expandierbarer Sektion
            with st.expander(f" Gewählte Firmen anzeigen ({num_companies})", expanded=num_companies <= 8):
                preview_cols = st.columns(min(4, num_companies))
                for i, company_id in enumerate(
                        st.session_state.multi_offer_selected_companies[:12]):  # Max 12 in Vorschau
                    col_index = i % 4
                    try:
                        company = get_company(company_id) if callable(get_company) else {
                            "name": f"Firma {company_id}", "id": company_id}
                        with preview_cols[col_index]:
                            st.markdown(
                                f"**{i + 1}. {company.get('name', 'Unbekannt')}**")
                            st.caption(f"ID: {company_id}")
                    except BaseException:
                        with preview_cols[col_index]:
                            st.markdown(f"**{i + 1}. Firma {company_id}**")
                            st.caption(f"ID: {company_id}")

                if num_companies > 12:
                    st.caption(f"... und {num_companies - 12} weitere Firmen")

            # Erweiterte PDF-Ausgabe je Firma + Master-Schalter
            with st.expander(" Erweiterte PDF-Ausgabe (ab Seite 7) je Firma", expanded=False):
                c1, c2 = st.columns([1, 3])
                with c1:
                    master = st.checkbox(
                        "Alle erweitern",
                        value=st.session_state.get(
                            "multi_offer_extend_all",
                            False),
                        help="Aktiviert für alle ausgewählten Firmen die erweiterte PDF-Ausgabe (Zusatzseiten).",
                    )
                    if master != st.session_state.get(
                            "multi_offer_extend_all", False):
                        st.session_state.multi_offer_extend_all = master
                        # Wenn Master aktiv, setze alle auf True; sonst keine
                        # Massenänderung der Einzelwerte
                        if master:
                            for cid in current_ids:
                                st.session_state.multi_offer_company_extended[cid] = True
                with c2:
                    for cid in st.session_state.multi_offer_selected_companies:
                        try:
                            cinfo = get_company(cid) if callable(get_company) else {
                                "name": f"Firma {cid}", "id": cid}
                            label = f"{cinfo.get('name', f'Firma {cid}')}"
                        except Exception:
                            label = f"Firma {cid}"
                        st.session_state.multi_offer_company_extended[cid] = st.checkbox(
                            f"{label} – Erweiterte Ausgabe",
                            value=st.session_state.multi_offer_company_extended.get(cid, False),
                            key=f"extended_flag_{cid}"
                        )

            return True
        st.warning(
            " Bitte mindestens eine Firma auswählen. Für Multi-Angebote sind 2+ Firmen empfohlen.")
        return False

    def render_offer_configuration(self):
        """Schritt 3: Angebotskonfiguration"""
        st.subheader("Schritt 3: Globale Angebotskonfiguration")

        settings = st.session_state.multi_offer_settings

        # Basis-Einstellungen
        cols = st.columns(3)

        settings["module_quantity"] = cols[0].slider(
            "Anzahl der Module", 5, 100, settings.get("module_quantity", 20)
        )
        settings["include_storage"] = cols[1].checkbox(
            "Batteriespeicher ins Angebot aufnehmen?",
            value=settings.get("include_storage", True),
        )
        # NEUE FEATURE: Automatische Preisstaffelung
        st.markdown("###  Automatische Produktrotation & Preisstaffelung")
        auto_cols = st.columns(3)

        settings["enable_product_rotation"] = auto_cols[0].checkbox(
            " Automatische Produktrotation aktivieren",
            value=settings.get(
                "enable_product_rotation",
                True),
            help="Jede Firma bekommt ein anderes Produkt aus der gleichen Kategorie")

        if settings["enable_product_rotation"]:
            settings["product_rotation_step"] = auto_cols[1].slider(
                " Produktrotation-Schritt",
                1, 5,
                settings.get("product_rotation_step", 1),
                help="Wie viele Produkte überspringen? 1=nächstes, 2=übernächstes, etc."
            )
        else:
            settings["product_rotation_step"] = 1

        settings["price_increment_percent"] = auto_cols[2].slider(
            " Preisstaffelung pro Firma (%)",
            0.0, 20.0,
            settings.get("price_increment_percent", 3.0),
            step=0.1,
            help="Vollständig anpassbar: 0% = keine Steigerung, bis 20% möglich"
        )

        # Erweiterte Einstellungen in Expander
        with st.expander(" Erweiterte Rotation & Preiseinstellungen"):
            adv_cols = st.columns(2)

            with adv_cols[0]:
                settings["rotation_mode"] = st.selectbox(
                    "Rotationsmodus",
                    ["linear", "zufällig", "kategorie-spezifisch"],
                    index=["linear", "zufällig", "kategorie-spezifisch"].index(settings.get("rotation_mode", "linear")),
                    help="Linear: der Reihe nach, Zufällig: per Zufall, Kategorie-spezifisch: unterschiedliche Schritte pro Kategorie"
                )

                if settings["rotation_mode"] == "kategorie-spezifisch":
                    st.write("**Kategorie-spezifische Rotation:**")
                    settings["module_rotation_step"] = st.slider(
                        "Module-Rotation", 1, 10, settings.get("module_rotation_step", 1))
                    settings["inverter_rotation_step"] = st.slider(
                        "Wechselrichter-Rotation", 1, 10, settings.get("inverter_rotation_step", 1))
                    settings["storage_rotation_step"] = st.slider(
                        "Speicher-Rotation", 1, 10, settings.get("storage_rotation_step", 1))

            with adv_cols[1]:
                settings["price_calculation_mode"] = st.selectbox(
                    "Preisberechnungsmodus",
                    ["linear", "exponentiell", "custom"],
                    index=["linear", "exponentiell", "custom"].index(settings.get("price_calculation_mode", "linear")),
                    help="Linear: +X% pro Firma, Exponentiell: X%^Firma, Custom: individuelle Faktoren"
                )

                if settings["price_calculation_mode"] == "exponentiell":
                    settings["price_exponent"] = st.slider(
                        "Exponentieller Faktor",
                        1.01, 1.20,
                        settings.get("price_exponent", 1.03),
                        step=0.01,
                        help="Firma 1: 100%, Firma 2: 103%, Firma 3: 106.09%, etc."
                    )
                elif settings["price_calculation_mode"] == "custom":
                    st.text_area(
                        "Custom Preisfaktoren (JSON)",
                        value=settings.get(
                            "custom_price_factors",
                            "[1.0, 1.03, 1.07, 1.12, 1.18]"),
                        help="JSON-Array mit Preisfaktoren für jede Firma, z.B. [1.0, 1.05, 1.15, 1.25]")

        # Dynamische Vorschau basierend auf ausgewählten Firmen
        if st.session_state.multi_offer_selected_companies:
            num_companies = len(
                st.session_state.multi_offer_selected_companies)
            st.markdown(f"###  Vorschau für {num_companies} Firmen")

            preview_cols = st.columns(min(4, num_companies))
            for i in range(
                    min(4, num_companies)):  # Zeige max 4 Firmen-Previews
                with preview_cols[i]:
                    if settings["enable_product_rotation"]:
                        st.info(f"**Firma {i +
                                           1}**\n Produkt-Offset: {i *
                                                                   settings.get('product_rotation_step', 1)}")
                    else:
                        st.info(f"**Firma {i + 1}**\n Gleiches Produkt")

                    if settings["price_increment_percent"] > 0:
                        if settings["price_calculation_mode"] == "linear":
                            price_factor = 1.0 + \
                                (i * settings["price_increment_percent"] / 100.0)
                        elif settings["price_calculation_mode"] == "exponentiell":
                            price_factor = settings.get(
                                "price_exponent", 1.03) ** i
                        else:  # custom
                            try:
                                import json
                                factors = json.loads(settings.get(
                                    "custom_price_factors", "[1.0]"))
                                price_factor = factors[i] if i < len(
                                    factors) else factors[-1]
                            except BaseException:
                                price_factor = 1.0 + (i * 0.03)

                        st.success(
                            f" Preisfaktor: {price_factor:.3f} ({(price_factor - 1) * 100:.1f}%)")
                    else:
                        st.success(" Originalpreis")

            if num_companies > 4:
                st.caption(
                    f"... und {
                        num_companies -
                        4} weitere Firmen mit entsprechender Rotation/Preisstaffelung")

        if settings["enable_product_rotation"]:
            st.info("ℹ **Produktrotation aktiv:** Jede Firma erhält automatisch andere Produkte derselben Kategorie (sofern verfügbar).")

        if settings["price_increment_percent"] > 0:
            st.info(
                "ℹ **Preisstaffelung aktiv:** Vollständig anpassbare Preisgestaltung für alle Firmen.")

        st.markdown("---")
        products = self.products

        # Produktauswahl
        st.markdown("###  Basisprodukte auswählen")
        prod_cols = st.columns(3)

        # Photovoltaik-Modul auswählen
        with prod_cols[0]:
            if products.get("module"):
                module_options = {p["model_name"]: p["id"]
                                  for p in products["module"]}
                default_module = settings.get("selected_module_id")
                default_module_index = (
                    list(module_options.values()).index(default_module)
                    if default_module in module_options.values()
                    else 0
                )
                selected_module_name = st.selectbox(
                    " Photovoltaik-Modul (Basis)",
                    options=list(module_options.keys()),
                    index=default_module_index,
                    help="Erste Firma erhält dieses Modul, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_module_id"] = module_options.get(
                    selected_module_name)
            else:
                st.warning(
                    "Keine Photovoltaik-Module in der Produktdatenbank gefunden.")
                settings["selected_module_id"] = None

        # Wechselrichter auswählen
        with prod_cols[1]:
            if products.get("inverter"):
                inverter_options = {p["model_name"]: p["id"]
                                    for p in products["inverter"]}
                default_inverter = settings.get("selected_inverter_id")
                default_inverter_index = (
                    list(inverter_options.values()).index(default_inverter)
                    if default_inverter in inverter_options.values()
                    else 0
                )
                selected_inverter_name = st.selectbox(
                    " Wechselrichter (Basis)",
                    options=list(inverter_options.keys()),
                    index=default_inverter_index,
                    help="Erste Firma erhält diesen Wechselrichter, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_inverter_id"] = inverter_options.get(
                    selected_inverter_name)
            else:
                st.warning(
                    "Keine Wechselrichter in der Produktdatenbank gefunden.")
                settings["selected_inverter_id"] = None

        # Batteriespeicher auswählen (wenn aktiviert)
        with prod_cols[2]:
            if settings["include_storage"] and products.get("storage"):
                storage_options = {p["model_name"]: p["id"]
                                   for p in products["storage"]}
                default_storage = settings.get("selected_storage_id")
                default_storage_index = (
                    list(storage_options.values()).index(default_storage)
                    if default_storage in storage_options.values()
                    else 0
                )
                selected_storage_name = st.selectbox(
                    " Batteriespeicher (Basis)",
                    options=list(storage_options.keys()),
                    index=default_storage_index,
                    help="Erste Firma erhält diesen Speicher, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_storage_id"] = storage_options.get(
                    selected_storage_name)
            elif settings["include_storage"]:
                st.warning("Keine Batteriespeicher gefunden.")
                settings["selected_storage_id"] = None
            else:
                settings["selected_storage_id"] = None
                st.info("Batteriespeicher nicht im Angebot enthalten.")

        st.markdown("---")

        # NEUE FEATURE: Erweiterte PDF-Optionen wie bei Einzel-PDF
        st.markdown("###  PDF-Darstellungsoptionen")

        # PDF-Optionen initialisieren falls nicht vorhanden
        if "pdf_options" not in settings:
            settings["pdf_options"] = {
                "include_company_logo": True,
                "include_product_images": True,
                "include_charts": True,
                "include_visualizations": True,
                "include_all_documents": False,
                "include_optional_component_details": True,
                "selected_sections": [
                    "ProjectOverview", "TechnicalComponents", "CostDetails",
                    "Economics", "SimulationDetails", "CO2Savings",
                    "Visualizations", "FutureAspects"
                ]
            }

        pdf_options = settings["pdf_options"]

        # PDF-Optionen in 3 Spalten
        pdf_cols = st.columns(3)

        with pdf_cols[0]:
            st.markdown("** Branding & Layout**")
            pdf_options["include_company_logo"] = st.checkbox(
                "Firmenlogo anzeigen",
                value=pdf_options.get("include_company_logo", True),
                help="Logo der jeweiligen Firma im PDF anzeigen"
            )
            pdf_options["include_product_images"] = st.checkbox(
                "Produktbilder anzeigen",
                value=pdf_options.get("include_product_images", True),
                help="Bilder der Produkte im PDF anzeigen"
            )
            pdf_options["include_all_documents"] = st.checkbox(
                "Produktdatenblätter anhängen",
                value=pdf_options.get("include_all_documents", False),
                help="Produktdatenblätter und Firmendokumente als Anhang"
            )

        with pdf_cols[1]:
            st.markdown("** Diagramme & Visualisierungen**")
            pdf_options["include_charts"] = st.checkbox(
                "Wirtschaftlichkeits-Diagramme",
                value=pdf_options.get("include_charts", True),
                help="Kostenprojektionen, ROI-Diagramme etc."
            )
            pdf_options["include_visualizations"] = st.checkbox(
                "Technische Visualisierungen",
                value=pdf_options.get("include_visualizations", True),
                help="Produktionsdiagramme, Verbrauchsanalysen etc."
            )
            pdf_options["include_optional_component_details"] = st.checkbox(
                "Details zu Zusatzkomponenten",
                value=pdf_options.get(
                    "include_optional_component_details",
                    True),
                help="Wallbox, EMS, Optimierer etc.")

        with pdf_cols[2]:
            st.markdown("** Inhalts-Sektionen**")
            available_sections = {
                "ProjectOverview": "1. Projektübersicht",
                "TechnicalComponents": "2. Systemkomponenten",
                "CostDetails": "3. Kostenaufstellung",
                "Economics": "4. Wirtschaftlichkeit",
                "SimulationDetails": "5. Simulation",
                "CO2Savings": "6. CO₂-Einsparung",
                "Visualizations": "7. Grafiken",
                "FutureAspects": "8. Zukunftsaspekte"
            }

            # Multi-Select für Sektionen
            selected_sections = st.multiselect(
                "Sektionen auswählen", options=list(
                    available_sections.keys()), default=pdf_options.get(
                    "selected_sections", list(
                        available_sections.keys())), format_func=lambda x: available_sections[x])
            pdf_options["selected_sections"] = selected_sections

            if len(selected_sections) == 0:
                st.warning(" Mindestens eine Sektion muss ausgewählt sein!")
            else:
                st.success(f" {len(selected_sections)} Sektionen ausgewählt")

        return True

    def generate_multi_offers(self):
        """Generiert PDFs für alle ausgewählten Firmen"""
        st.subheader("Schritt 4: PDF-Angebote generieren")

        customer_data = st.session_state.multi_offer_customer_data
        selected_companies = st.session_state.multi_offer_selected_companies
        settings = st.session_state.multi_offer_settings
        project_data = st.session_state.get("multi_offer_project_data", {})

        if not customer_data or not selected_companies:
            st.error("Kundendaten oder Firmenauswahl fehlt!")
            return

        if st.button(" Angebote für alle Firmen erstellen", type="primary"):

            try:
                # Produkte frisch laden, damit Rotationen aktuelle Daten
                # verwenden
                self.products = self.load_all_products()

                # Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()

                generated_pdfs = []
                total_companies = len(selected_companies)

                for i, company_id in enumerate(selected_companies):
                    # Fallback-Name sofort setzen
                    company_name = f"Firma_{company_id}"
                    try:
                        # Company-Daten laden
                        company = get_company(company_id) if callable(
                            get_company) else {}
                        company_name = company.get(
                            "name", f"Firma_{company_id}")  # Überschreibe mit echtem Namen

                        status_text.text(
                            f"Erstelle Angebot für {company_name} (Firma {
                                i + 1}/{total_companies})...")

                        # NEUE FEATURE: Produktrotation für diese Firma
                        company_settings = self.get_rotated_products_for_company(
                            i, settings, project_data)
                        # PDF-Generierung vorbereiten mit firmenspezifischen
                        # Produkten
                        offer_data = self._prepare_offer_data(
                            customer_data, company, company_settings, project_data, i)

                        # PDF generieren mit company_index für Preisstaffelung
                        pdf_content = self._generate_company_pdf(
                            offer_data, company, i)

                        if pdf_content:
                            generated_pdfs.append({
                                "company_name": company_name,
                                "pdf_content": pdf_content,
                                "filename": f"Angebot_{company_name}_{customer_data.get('last_name', 'Kunde')}.pdf"
                            })
                            st.success(f" PDF für {company_name} erstellt")
                        else:
                            # Fortschritt aktualisieren
                            st.error(
                                f" PDF für {company_name} konnte nicht erstellt werden")
                        progress_bar.progress((i + 1) / total_companies)

                    except Exception as e:
                        # Sichere Verwendung von company_name - falls nicht
                        # definiert, Fallback verwenden
                        safe_company_name = locals().get(
                            'company_name', f"Firma_{company_id}")
                        st.error(f"Fehler bei {safe_company_name}: {str(e)}")
                        logging.error(
                            f"Fehler bei PDF-Generierung für {safe_company_name}: {e}")
                        logging.error(f"Exception Typ: {type(e).__name__}")
                        logging.error(
                            f"Verfügbare lokale Variablen: {
                                list(
                                    locals().keys())}")
                        # Ausführlichere Fehlerbehandlung für company_name
                        # Probleme
                        if "company_name" in str(e):
                            logging.error(
                                f"COMPANY_NAME DEBUG: company_id={company_id}, locals company_name: {
                                    locals().get(
                                        'company_name', 'NOT_FOUND')}")
                        continue  # Weiter mit der nächsten Firma

                # ZIP-Download erstellen
                if generated_pdfs:
                    zip_content = self._create_zip_download(generated_pdfs)

                    st.success(
                        f" {len(generated_pdfs)} Angebote erfolgreich erstellt!")
                    st.download_button(
                        label=" Alle Angebote als ZIP herunterladen",
                        data=zip_content,
                        file_name=f"Multi_Angebote_{
                            customer_data.get(
                                'last_name',
                                'Kunde')}_{
                            datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip")

                    # CRM: Kunde speichern & alle PDFs in Kundenakte ablegen
                    with st.expander(" CRM: Kunde speichern & Angebote in Kundenakte ablegen", expanded=False):
                        try:
                            import sqlite3

                            from crm import (
                                create_tables_crm,
                                save_customer,
                                save_project,
                            )
                            from database import (
                                add_customer_document,
                                get_db_connection,
                            )

                            conn = get_db_connection()
                            if conn is None:
                                st.error("Keine DB-Verbindung für CRM.")
                            else:
                                conn.row_factory = sqlite3.Row
                                create_tables_crm(conn)
                                # Kunde erstellen/finden
                                first_name = customer_data.get(
                                    'first_name', '')
                                last_name = customer_data.get('last_name', '')
                                email_val = customer_data.get('email', '')
                                cur = conn.cursor()
                                cur.execute(
                                    "SELECT id FROM customers WHERE first_name=? AND last_name=? AND (email = ? OR ? = '') LIMIT 1",
                                    (first_name,
                                     last_name,
                                     email_val,
                                     email_val))
                                row = cur.fetchone()
                                if row:
                                    crm_customer_id = int(row[0])
                                else:
                                    cust_payload = {
                                        'salutation': customer_data.get('salutation'),
                                        'title': customer_data.get('title'),
                                        'first_name': first_name or 'Interessent',
                                        'last_name': last_name or 'Unbekannt',
                                        'company_name': customer_data.get('company_name'),
                                        'address': customer_data.get('address'),
                                        'house_number': customer_data.get('house_number'),
                                        'zip_code': customer_data.get('zip_code'),
                                        'city': customer_data.get('city'),
                                        'state': customer_data.get('state'),
                                        'region': customer_data.get('region'),
                                        'email': email_val,
                                        'phone_landline': customer_data.get('phone_landline') or customer_data.get('phone'),
                                        'phone_mobile': customer_data.get('phone_mobile'),
                                        'income_tax_rate_percent': float(
                                            customer_data.get('income_tax_rate_percent') or 0.0),
                                        'creation_date': datetime.now().isoformat(),
                                    }
                                    crm_customer_id = save_customer(
                                        conn, cust_payload)

                                # Projekt anlegen (ein generisches
                                # Multi-Angebotsprojekt)
                                crm_project_id = None
                                if crm_customer_id:
                                    proj = st.session_state.get(
                                        'multi_offer_project_data', {})
                                    proj_details = proj.get(
                                        'project_details', {}) if isinstance(
                                        proj, dict) else {}
                                    proj_payload = {
                                        'customer_id': crm_customer_id,
                                        'project_name': proj_details.get('project_name') or f"Multi-Angebot {datetime.now().strftime('%Y-%m-%d')}",
                                        'project_status': 'Angebot',
                                        'module_quantity': proj_details.get('module_quantity'),
                                        'selected_module_id': proj_details.get('selected_module_id'),
                                        'selected_inverter_id': proj_details.get('selected_inverter_id'),
                                        'include_storage': int(bool(proj_details.get('include_storage'))),
                                        'selected_storage_id': proj_details.get('selected_storage_id'),
                                        'selected_storage_storage_power_kw': proj_details.get('selected_storage_storage_power_kw'),
                                        'visualize_roof_in_pdf': int(bool(proj_details.get('visualize_roof_in_pdf'))),
                                        'latitude': proj_details.get('latitude'),
                                        'longitude': proj_details.get('longitude'),
                                        'creation_date': datetime.now().isoformat(),
                                    }
                                    crm_project_id = save_project(
                                        conn, proj_payload)

                                # Alle erzeugten PDFs in Kundenakte ablegen
                                if crm_customer_id:
                                    saved_docs = 0
                                    for item in generated_pdfs:
                                        try:
                                            pdf_bytes = item.get(
                                                'pdf_content') or item.get('bytes')
                                            filename = item.get('filename') or f"Angebot_{
                                                datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                            if isinstance(
                                                    pdf_bytes, (bytes, bytearray)):
                                                add_customer_document(
                                                    crm_customer_id,
                                                    pdf_bytes,
                                                    display_name=filename,
                                                    doc_type="offer_pdf",
                                                    project_id=crm_project_id,
                                                    suggested_filename=filename)
                                                saved_docs += 1
                                        except Exception as e_item:
                                            st.warning(
                                                f"Konnte ein PDF nicht speichern: {e_item}")
                                    st.success(
                                        f"Kunde gespeichert. {saved_docs} PDF(s) in Kundenakte abgelegt.")

                                # Navigation zur CRM-Ansicht
                                if st.button(
                                    " Zur CRM Kundenverwaltung",
                                        key="go_crm_after_multi"):
                                    st.session_state['selected_page_key_sui'] = 'crm'
                                    if crm_customer_id:
                                        st.session_state['selected_customer_id'] = crm_customer_id
                                        st.session_state['crm_view_mode'] = 'view_customer'
                                    st.rerun()
                        except Exception as e:
                            st.error(f"CRM-Speichern fehlgeschlagen: {e}")
                else:
                    st.error("Keine PDFs konnten erstellt werden!")

                status_text.text("Fertig!")

            except Exception as e:
                st.error(f"Fehler bei der PDF-Generierung: {str(e)}")
                logging.error(f"Fehler in generate_multi_offers: {e}")

    def get_rotated_products_for_company(
            self,
            company_index: int,
            base_settings: dict,
            project_data: dict | None = None) -> dict:
        """
        Vollständig flexible Produktrotation für verschiedene Firmen
        company_index: 0 = erste Firma, 1 = zweite Firma, etc.
        Unterstützt: Lineare Rotation, Zufällige Auswahl, Kategorie-spezifische Schritte
        """
        rotated_settings = base_settings.copy()

        if not base_settings.get("enable_product_rotation", False):
            return rotated_settings

        try:
            project_details = {}
            if project_data and isinstance(project_data, dict):
                project_details = project_data.get("project_details", {}) or {}

            rotation_mode = base_settings.get("rotation_mode", "linear")

            # Kategorien mit individuellen Rotation-Schritten
            categories = ["module", "inverter", "storage"]

            for category in categories:
                base_id_key = f"selected_{category}_id"
                base_id = base_settings.get(base_id_key)

                if not base_id and project_details:
                    base_id = project_details.get(base_id_key)
                    if base_id:
                        rotated_settings[base_id_key] = base_id

                if not base_id or category not in self.products:
                    continue

                available_products = self.products[category]
                if len(available_products) <= 1:
                    # Nur ein Produkt verfügbar - behalte das Original
                    logging.info(
                        f"Produktrotation {category}: Nur 1 Produkt verfügbar, behalte Original")
                    continue

                # Finde Index des Basisprodukts
                base_index = -1
                for i, product in enumerate(available_products):
                    if product.get("id") == base_id:
                        base_index = i
                        break

                if base_index == -1:
                    logging.warning(
                        f"Produktrotation {category}: Basisprodukt nicht gefunden")
                    if available_products:
                        rotated_settings[base_id_key] = available_products[0].get(
                            "id")
                    continue

                # Bestimme Rotation-Schritt basierend auf Modus
                if rotation_mode == "kategorie-spezifisch":
                    rotation_step = base_settings.get(
                        f"{category}_rotation_step", 1)
                elif rotation_mode == "zufällig":
                    import random
                    rotation_step = random.randint(
                        1, len(available_products) - 1)
                else:  # linear
                    rotation_step = base_settings.get(
                        "product_rotation_step", 1)

                # Berechne neuen Index mit flexiblem Schritt
                new_index = (base_index + (company_index *
                             rotation_step)) % len(available_products)
                rotated_product = available_products[new_index]
                rotated_settings[base_id_key] = rotated_product.get("id")

                # Sicherstellen, dass ein Basisprodukt gesetzt ist, falls
                # vorher leer
                if rotated_settings.get(
                        base_id_key) is None and available_products:
                    rotated_settings[base_id_key] = available_products[0].get(
                        "id")

                logging.info(
                    f"Produktrotation {category}: Firma {
                        company_index + 1} -> {
                        rotated_product.get(
                            'model_name',
                            'Unknown')} (Schritt: {rotation_step}, Verfügbare: {
                        len(available_products)})")

        except Exception as e:
            logging.warning(f"Fehler bei Produktrotation: {e}")

        return rotated_settings

    def apply_price_scaling(
            self,
            company_index: int,
            base_settings: dict,
            calc_results: dict) -> dict:
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
                    custom_factors = json.loads(
                        base_settings.get(
                            "custom_price_factors", "[1.0]"))
                    price_factor = custom_factors[company_index] if company_index < len(
                        custom_factors) else custom_factors[-1]
                except BaseException:
                    # Fallback auf linear
                    price_factor = 1.0 + \
                        (company_index * price_increment / 100.0)
            else:
                price_factor = 1.0

            logging.info(
                f"Preisstaffelung: Firma {
                    company_index +
                    1}, Modus: {calc_mode}, Faktor: {
                    price_factor:.3f}")

            # Preisbezogene Felder skalieren
            price_fields = [
                'total_investment_netto',
                'total_investment_brutto',
                'pricing_result_total_netto',
                'pricing_result_total_brutto',
                'pricing_result_total_gross',
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
                'tierabwehr_cost',
                'final_price',
                'final_price_net',
                'final_price_netto',
                'final_price_brutto',
                'final_price_gross',
                'final_price_with_provision',
                'final_offer_price_net',
                'final_end_preis'
            ]

            for field in price_fields:
                if field in scaled_results and isinstance(
                        scaled_results[field], (int, float)):
                    original_value = scaled_results[field]
                    scaled_results[field] = original_value * price_factor

            pricing_details = scaled_results.get('pricing_details')
            if isinstance(pricing_details, dict):
                pd_fields = [
                    'total_final_price_net',
                    'total_final_price_brutto',
                    'total_final_price_gross',
                    'final_price_net',
                    'final_price_brutto',
                    'final_price_gross',
                    'subtotal_netto',
                    'subtotal_after_bonus',
                    'net_total',
                    'gross_total',
                ]
                for pd_field in pd_fields:
                    if pd_field in pricing_details and isinstance(
                            pricing_details[pd_field], (int, float)):
                        pricing_details[pd_field] = pricing_details[pd_field] * \
                            price_factor

            # Wirtschaftlichkeitsberechnungen intelligent anpassen
            if 'amortization_time_years' in scaled_results and isinstance(
                    scaled_results['amortization_time_years'], (int, float)):
                # Längere Amortisationszeit durch höhere Kosten (aber begrenzt)
                # Maximal 50% längere Amortisation
                amort_factor = min(price_factor, 1.5)
                scaled_results['amortization_time_years'] = scaled_results['amortization_time_years'] * amort_factor

            # ROI anpassen (niedriger durch höhere Investition)
            roi_fields = [
                'roi_percent_year1',
                'roi_percent_year10',
                'roi_percent_year20']
            for roi_field in roi_fields:
                if roi_field in scaled_results and isinstance(
                        scaled_results[roi_field], (int, float)):
                    scaled_results[roi_field] = scaled_results[roi_field] / \
                        price_factor
              # Jährliche Ersparnisse bleiben gleich (da gleiche Anlage, nur teurer)
            # annual_savings bleibt unverändert

        except Exception as e:
            logging.warning(
                f"Fehler bei Preisstaffelung für Firma {
                    company_index + 1}: {e}")

        return scaled_results

    @staticmethod
    def _extract_first_numeric(source: dict,
                               candidate_keys: list[str]) -> float | None:
        """Liefert den ersten numerischen Wert aus source passend zu candidate_keys."""
        if not isinstance(source, dict):
            return None

        for key in candidate_keys:
            value = source.get(key)
            if isinstance(value, (int, float)):
                return float(value)
        return None

    def _prepare_offer_data(
            self,
            customer_data: dict,
            company: dict,
            settings: dict,
            project_data: dict,
            company_index: int = 0) -> dict:
        """Bereitet die Angebotsdaten für PDF-Generierung vor"""
        # Basis-Angebotsdaten
        offer_data = {
            "customer_data": customer_data,
            "company_data": company,
            "offer_date": datetime.now().strftime("%d.%m.%Y"),
            "module_quantity": settings.get("module_quantity", 20),
            "include_storage": settings.get("include_storage", True),
        }

        # Projektdaten hinzufügen
        if project_data:
            offer_data["project_data"] = project_data

            # Verbrauchsdaten
            if project_data.get("consumption_data"):
                offer_data["consumption_data"] = project_data["consumption_data"]

            # Berechnungen
            if project_data.get("calculation_results"):
                # KRITISCH: Produktdetails für PDF-Generierung vorbereiten
                offer_data["calculation_results"] = project_data["calculation_results"]
        # Die PDF-Generierung erwartet diese Daten in "project_details"
        project_details = {
            "module_quantity": settings.get("module_quantity", 20),
            "include_storage": settings.get("include_storage", True),
            "include_additional_components": True,  # Zusatzkomponenten aktivieren
        }

        # Fallback: Verwende Produktauswahl aus project_data falls verfügbar
        existing_project_details = project_data.get(
            "project_details", {}) if project_data else {}

        # Produktdaten hinzufügen
        try:
            # Modul
            module_id = settings.get(
                "selected_module_id") or existing_project_details.get("selected_module_id")
            if module_id:
                offer_data["selected_module"] = get_product_by_id(module_id)
                project_details["selected_module_id"] = module_id
                if offer_data.get("selected_module"):
                    project_details["selected_module"] = deepcopy(
                        offer_data["selected_module"])
                    project_details["selected_module_name"] = offer_data["selected_module"].get(
                        "model_name")

            # Wechselrichter
            inverter_id = settings.get(
                "selected_inverter_id") or existing_project_details.get("selected_inverter_id")
            if inverter_id:
                offer_data["selected_inverter"] = get_product_by_id(
                    inverter_id)
                project_details["selected_inverter_id"] = inverter_id
                if offer_data.get("selected_inverter"):
                    project_details["selected_inverter"] = deepcopy(
                        offer_data["selected_inverter"])
                    project_details["selected_inverter_name"] = offer_data["selected_inverter"].get(
                        "model_name")

            # Speicher
            storage_id = settings.get(
                "selected_storage_id") or existing_project_details.get("selected_storage_id")
            if storage_id:
                offer_data["selected_storage"] = get_product_by_id(storage_id)
                project_details["selected_storage_id"] = storage_id
                # Speicher-spezifische Details
                storage_product = get_product_by_id(storage_id)
                if storage_product:
                    project_details["selected_storage_storage_power_kw"] = storage_product.get(
                        "storage_power_kw", 0)
                    project_details["selected_storage"] = deepcopy(
                        storage_product)
                    project_details["selected_storage_name"] = storage_product.get(
                        "model_name")

            # Zusatzkomponenten (Wallbox, EMS, etc.) aus Projektdaten
            # übertragen
            additional_components = [
                'selected_wallbox_id',
                'selected_ems_id',
                'selected_optimizer_id',
                'selected_carport_id',
                'selected_notstrom_id',
                'selected_tierabwehr_id'
            ]

            for comp_key in additional_components:
                comp_id = existing_project_details.get(comp_key)
                if comp_id:
                    project_details[comp_key] = comp_id
                    # Produktdaten auch zu offer_data hinzufügen für
                    # Vollständigkeit
                    comp_product = get_product_by_id(comp_id)
                    if comp_product:
                        offer_data[comp_key.replace('_id', '')] = comp_product

            # Weitere wichtige Felder aus existing_project_details übernehmen
            if existing_project_details:
                # Übernehme Modulanzahl falls nicht in settings
                if "module_quantity" not in settings and "module_quantity" in existing_project_details:
                    project_details["module_quantity"] = existing_project_details["module_quantity"]
                    offer_data["module_quantity"] = existing_project_details["module_quantity"]

                # Übernehme Speicher-Einstellung falls nicht in settings
                if "include_storage" not in settings and "include_storage" in existing_project_details:
                    project_details["include_storage"] = existing_project_details["include_storage"]
                    offer_data["include_storage"] = existing_project_details["include_storage"]

                # Übernehme zusätzliche Komponenten-Einstellungen
                for field in [
                    "include_additional_components",
                    "visualize_roof_in_pdf_satellite",
                        "satellite_image_base64_data"]:
                    if field in existing_project_details:
                        project_details[field] = existing_project_details[field]
        except Exception as e:
            logging.warning(f"Produktdaten konnten nicht geladen werden: {e}")

        # Project_details zu offer_data hinzufügen (KRITISCH für
        # PDF-Generierung)
        offer_data["project_details"] = project_details

        return offer_data

    def _build_calculation_input(self, offer_data: dict) -> dict:
        """Stellt Eingabedaten für perform_calculations mit firmenspezifischer Produktauswahl zusammen."""
        base_project_data = offer_data.get("project_data") if isinstance(
            offer_data.get("project_data"), dict) else {}
        calc_input = deepcopy(base_project_data) if base_project_data else {}

        if not isinstance(calc_input, dict):
            calc_input = {}

        project_details = deepcopy(calc_input.get("project_details", {}))
        if offer_data.get("project_details"):
            project_details.update(deepcopy(offer_data["project_details"]))
        calc_input["project_details"] = project_details

        if offer_data.get("customer_data"):
            calc_input["customer_data"] = deepcopy(offer_data["customer_data"])
        else:
            calc_input.setdefault("customer_data", {})

        for key in (
            "consumption_data",
            "roof_data",
            "location_data",
            "technical_specs",
                "pricing_settings"):
            if offer_data.get(key) is not None and key not in calc_input:
                calc_input[key] = deepcopy(offer_data[key])

        return calc_input

    def _generate_company_pdf(
            self,
            offer_data: dict,
            company: dict,
            company_index: int = 0) -> bytes:
        """Generiert PDF für eine spezifische Firma mit firmenspezifischen Produkten und Preisen"""
        try:
            # PDF-Generierung über generate_offer_pdf mit allen 16
            # erforderlichen Parametern
            if callable(generate_offer_pdf):
                calc_results: dict[str, Any] = {}
                calc_input = self._build_calculation_input(offer_data)

                if callable(perform_calculations):
                    calc_errors: list[str] = []
                    try:
                        calc_results = perform_calculations(
                            calc_input, {}, calc_errors) or {}
                    except Exception as calc_ex:
                        logging.error(
                            f"Berechnung für Firma {
                                company.get(
                                    'name',
                                    'Unbekannt')} fehlgeschlagen: {calc_ex}")
                        calc_results = {}

                    if calc_errors:
                        logging.warning(
                            f"Berechnungswarnungen ({company.get('name', 'Unbekannt')}): {calc_errors[:3]}")
                else:
                    logging.warning(
                        "perform_calculations nicht verfügbar – verwende Session-State Werte")

                if not calc_results:
                    calc_results = st.session_state.get(
                        'calculation_results', {}) or {}
                    if not calc_results:
                        calc_results = st.session_state.get(
                            'multi_offer_calc_results', {}) or {}

                if not calc_results:
                    logging.warning(
                        "Keine echten Berechnungsergebnisse verfügbar - verwende Mock-Daten")
                    module_qty = calc_input.get("project_details", {}).get(
                        "module_quantity") or offer_data.get('module_quantity', 20)
                    estimated_kwp = module_qty * 0.4
                    base_net = module_qty * 750
                    calc_results = {
                        'anlage_kwp': estimated_kwp,
                        'annual_pv_production_kwh': module_qty * 400,
                        'total_investment_netto': base_net,
                        'total_investment_brutto': base_net * 1.19,
                        'amortization_time_years': 12.5,
                        'self_supply_rate_percent': 65.0,
                        'annual_financial_benefit_year1': 1200.0,
                        'final_price': base_net,
                        'final_price_net': base_net,
                        'final_price_netto': base_net,
                        'final_price_brutto': base_net * 1.19,
                        'final_price_with_provision': base_net,
                        'final_end_preis': base_net,
                    }
                else:
                    logging.info(
                        f"Verwende echte Berechnungsergebnisse mit {
                            len(calc_results)} Feldern")

                base_settings = st.session_state.get(
                    "multi_offer_settings", {})
                calc_results = self.apply_price_scaling(
                    company_index, base_settings, calc_results)

                # KRITISCH: total_investment_netto ZUERST - das ist das
                # skalierte Feld!
                net_price = self._extract_first_numeric(
                    calc_results,
                    [
                        'total_investment_netto',  # SKALIERT - MUSS ZUERST KOMMEN!
                        'final_price_net',
                        'final_price_netto',
                        'final_price_with_provision',
                        'final_price',
                        'pricing_result_total_netto',
                    ],
                )
                gross_price = self._extract_first_numeric(
                    calc_results,
                    [
                        'total_investment_brutto',  # SKALIERT - ZUERST!
                        'final_price_brutto',
                        'final_price_gross',
                        'pricing_result_total_brutto',
                    ],
                )

                if net_price is not None:
                    calc_results.setdefault(
                        'final_price_with_provision', net_price)
                    calc_results.setdefault('final_price_net', net_price)
                    calc_results.setdefault('final_price', net_price)
                    calc_results.setdefault('final_end_preis', net_price)
                    calc_results.setdefault('final_price_netto', net_price)
                if gross_price is not None:
                    calc_results.setdefault('final_price_brutto', gross_price)
                    calc_results.setdefault('final_price_gross', gross_price)

                pricing_details = calc_results.setdefault(
                    'pricing_details', {}) if isinstance(
                    calc_results, dict) else {}
                if isinstance(pricing_details, dict):
                    if net_price is not None:
                        pricing_details['total_final_price_net'] = net_price
                        pricing_details['final_price_net'] = net_price
                    if gross_price is not None:
                        pricing_details['total_final_price_brutto'] = gross_price
                        pricing_details['total_final_price_gross'] = gross_price

                project_details = calc_input.get("project_details", {})
                if net_price is not None:
                    project_details["final_offer_price_net"] = net_price
                    project_details["final_price_with_provision"] = net_price
                    project_details["final_price_netto"] = net_price
                    project_details["final_end_preis"] = net_price
                if gross_price is not None:
                    project_details["final_price_brutto"] = gross_price

                if isinstance(pricing_details, dict):
                    project_details["pricing_details"] = deepcopy(
                        pricing_details)

                offer_data["project_details"] = project_details
                offer_data["calculation_results"] = calc_results

                logging.info(
                    f"PDF-Generierung für Firma {
                        company_index +
                        1}: Netto={
                        net_price or 'n/a'} | Brutto={
                        gross_price or 'n/a'}")

                pdf_project_data = {
                    "customer_data": offer_data.get("customer_data", {}),
                    "project_details": project_details,
                    "consumption_data": offer_data.get("consumption_data", {}),
                    "calculation_results": calc_results
                }

                if "project_data" in offer_data and offer_data["project_data"]:
                    original_project_data = offer_data["project_data"]
                    for key in [
                        "address",
                        "roof_data",
                        "location_data",
                            "technical_specs"]:
                        if key in original_project_data and key not in pdf_project_data:
                            pdf_project_data[key] = original_project_data[key]

                logging.info("Multi-Offer PDF Datenstruktur:")
                logging.info(
                    f"  project_details keys: {
                        list(
                            pdf_project_data.get(
                                'project_details',
                                {}).keys())}")
                logging.info(
                    f"  selected_module_id: {
                        pdf_project_data.get(
                            'project_details',
                            {}).get(
                            'selected_module_id',
                            'NICHT GESETZT')}")
                logging.info(
                    f"  selected_inverter_id: {
                        pdf_project_data.get(
                            'project_details',
                            {}).get(
                            'selected_inverter_id',
                            'NICHT GESETZT')}")
                logging.info(
                    f"  selected_storage_id: {
                        pdf_project_data.get(
                            'project_details',
                            {}).get(
                            'selected_storage_id',
                            'NICHT GESETZT')}")
                available_charts = []
                if calc_results and isinstance(calc_results, dict):
                    # Chart-Keys aus analysis_results finden
                    chart_keys = [k for k in calc_results.keys() if k.endswith(
                        '_chart_bytes') and calc_results[k] is not None]
                    available_charts = chart_keys
                    logging.info(
                        f"Multi-Offer PDF: {len(available_charts)} Charts gefunden: {chart_keys}")

                # PDF-Templates aus Admin-Einstellungen laden
                try:
                    # Templates laden (falls verfügbar)
                    title_image_templates = load_admin_setting(
                        "pdf_title_image_templates", []) if callable(load_admin_setting) else []
                    offer_title_templates = load_admin_setting(
                        "pdf_offer_title_templates", []) if callable(load_admin_setting) else []
                    cover_letter_templates = load_admin_setting(
                        "pdf_cover_letter_templates", []) if callable(load_admin_setting) else []

                    # Erstes verfügbares Template verwenden
                    selected_title_image = title_image_templates[0] if title_image_templates else None
                    selected_offer_title = offer_title_templates[0] if offer_title_templates else None
                    selected_cover_letter = cover_letter_templates[0] if cover_letter_templates else None

                    logging.info(
                        f"Templates geladen: Titelbild={
                            bool(selected_title_image)}, Titel={
                            bool(selected_offer_title)}, Anschreiben={
                            bool(selected_cover_letter)}")
                except Exception as e:
                    logging.warning(f"Fehler beim Laden der Templates: {e}")
                    selected_title_image = selected_offer_title = selected_cover_letter = None
                  # NEUE FEATURE: Benutzerdefinierten PDF-Optionen aus
                  # Einstellungen verwenden
                base_settings = st.session_state.get(
                    "multi_offer_settings", {})
                pdf_options = base_settings.get("pdf_options", {})

                # Sektionen aus Benutzereinstellungen
                selected_sections = pdf_options.get("selected_sections", [
                    "ProjectOverview", "TechnicalComponents", "CostDetails",
                    "Economics", "SimulationDetails", "CO2Savings",
                    "Visualizations", "FutureAspects"
                ])

                # Charts basierend auf Benutzereinstellungen filtern
                charts_to_include = available_charts if pdf_options.get(
                    "include_charts", True) else []
                if not pdf_options.get("include_visualizations", True):
                    # Technische Visualisierungen entfernen
                    charts_to_include = [
                        c for c in charts_to_include if not any(
                            vis_key in c for vis_key in [
                                'daily_production',
                                'weekly_production',
                                'yearly_production'])]

                # Wichtig: Logo/Firmendaten müssen pro Firma gesetzt werden – kein Global-Fallback der Hauptfirma
                # Extended-Flag pro Firma bestimmen (oder Master "Alle
                # erweitern")
                is_extended = bool(
                    st.session_state.get(
                        "multi_offer_extend_all",
                        False) or st.session_state.get(
                        "multi_offer_company_extended",
                        {}).get(
                        company.get(
                            "id",
                            0),
                        False))

                # Company-Dokumente IDs ermitteln, wenn erweitert und Anhänge
                # gewünscht
                base_settings = st.session_state.get(
                    "multi_offer_settings", {})
                pdf_options = base_settings.get("pdf_options", {})
                include_all_docs = bool(
                    pdf_options.get(
                        "include_all_documents", False))
                company_doc_ids: list[int] = []
                if is_extended and include_all_docs and callable(
                        list_company_documents):
                    try:
                        docs = list_company_documents(
                            company.get("id", 0), None) or []
                        company_doc_ids = [
                            d.get("id") for d in docs if isinstance(
                                d, dict) and d.get("id") is not None]
                    except Exception as _e_docs:
                        logging.warning(
                            f"Konnte Firmendokumente nicht laden: {_e_docs}")

                # Drag&Drop-Reihenfolge und erweiterte Konfigurationen
                # (Finanzierung, Design, Custom Content) aus globalem State
                custom_section_order = st.session_state.get(
                    'pdf_section_order', [])
                inclusion_extras = {
                    'financing_config': st.session_state.get(
                        'financing_config', {}), 'chart_config': st.session_state.get(
                        'chart_config', {}), 'custom_content_items': st.session_state.get(
                        'custom_content_items', []), 'pdf_editor_config': st.session_state.get(
                        'pdf_editor_config', {}), 'pdf_design_config': st.session_state.get(
                        'pdf_design_config', {}), 'custom_section_order': custom_section_order if isinstance(
                            custom_section_order, list) else []}
                pdf_content = generate_offer_pdf(
                    project_data=pdf_project_data,  # Korrekt strukturierte Daten
                    analysis_results=calc_results,
                    company_info=company,
                    # wird im Generator in project_data.company_information
                    # injiziert
                    company_logo_base64=company.get(
                        "logo_base64"),  # pro Firma
                    selected_title_image_b64=None,
                    selected_offer_title_text=f"Ihr individuelles Solaranlagen-Angebot von {
                        company.get(
                            'name', 'Unser Unternehmen')}",
                    selected_cover_letter_text="Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse an nachhaltiger Solarenergie.",
                    sections_to_include=selected_sections,  # Benutzerdef. Sektionen
                    inclusion_options={
                        "include_company_logo": pdf_options.get("include_company_logo", True),
                        "include_product_images": pdf_options.get("include_product_images", True),
                        "include_all_documents": include_all_docs,
                        "company_document_ids_to_include": company_doc_ids,
                        "selected_charts_for_pdf": charts_to_include if is_extended else [],
                        "include_optional_component_details": pdf_options.get("include_optional_component_details", True),
                        # Erweiterte Ausgabe ab Seite 7
                        "append_additional_pages_after_main6": is_extended,
                        # Templates hinzufügen
                        "selected_title_image_template": selected_title_image,
                        "selected_offer_title_template": selected_offer_title,
                        "selected_cover_letter_template": selected_cover_letter,
                        "use_templates": True,
                        # DnD & Advanced Configs
                        **inclusion_extras
                    },
                    texts=st.session_state.get("TEXTS", {}),
                    list_products_func=list_products if callable(
                        list_products) else list,
                    get_product_by_id_func=get_product_by_id if callable(
                        get_product_by_id) else lambda x: {},
                    load_admin_setting_func=load_admin_setting if callable(
                        load_admin_setting) else lambda k, d=None: d,
                    save_admin_setting_func=save_admin_setting if callable(
                        save_admin_setting) else lambda k, v: None,
                    db_list_company_documents_func=list_company_documents if callable(
                        list_company_documents) else lambda cid, dtype=None: [],
                    active_company_id=company.get("id", 1)
                )
                return pdf_content
            st.error("PDF-Generator nicht verfügbar")
            return None

        except Exception as e:
            logging.error(f"Fehler bei PDF-Generierung: {e}")
            st.error(f"PDF-Generierung fehlgeschlagen: {str(e)}")
            return None

    def _create_zip_download(self, generated_pdfs: list[dict]) -> bytes:
        """Erstellt ZIP-Datei mit allen PDFs"""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf_info in generated_pdfs:
                zip_file.writestr(
                    pdf_info["filename"],
                    pdf_info["pdf_content"]
                )

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def render_ui(self):
        """Hauptfunktion für die UI-Darstellung"""
        st.title(" Multi-Firmen-Angebotsgenerator")
        st.markdown(
            "Erstellen Sie Angebote für mehrere Firmen basierend auf Ihren Projektdaten.")

        self.initialize_session_state()

        # Schritt 1: Kundendaten
        customer_data_ready = self.render_customer_input()

        if customer_data_ready:
            # Schritt 2: Firmenauswahl
            companies_selected = self.render_company_selection()

            if companies_selected:
                # Schritt 3: Konfiguration
                config_ready = self.render_offer_configuration()

                if config_ready:
                    # Schritt 4: PDF-Generierung
                    self.generate_multi_offers()


# Hauptfunktion für Streamlit
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
            logging.error("Traceback Details verfügbar in den Logs")
        st.info("Bitte versuchen Sie es erneut oder wenden Sie sich an den Support.")


def main():
    """Hauptfunktion für den Multi-Angebotsgenerator"""
    generator = MultiCompanyOfferGenerator()
    generator.render_ui()


if __name__ == "__main__":
    main()
