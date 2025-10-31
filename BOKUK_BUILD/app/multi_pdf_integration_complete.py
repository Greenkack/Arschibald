# multi_pdf_integration_complete.py
"""
Multi-PDF & Wärmepumpen Integration Module - VOLLSTÄNDIG
Extrahiert aus repair_pdf/multi_offer_generator.py mit kompletter Pipeline
VERSION: 2.0 - Mit PDF-Generierung & Produktrotation
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import os
import io
import zipfile
from datetime import datetime
import logging

# ===================================================================
# TEIL 1: MULTI-PDF KERNLOGIK
# ===================================================================

def init_multi_pdf_session_state():
    """Initialisiert Session State für Multi-PDF"""
    if "multi_offer_customer_data" not in st.session_state:
        st.session_state.multi_offer_customer_data = {}
    if "multi_offer_selected_companies" not in st.session_state:
        st.session_state.multi_offer_selected_companies = []
    if "multi_offer_settings" not in st.session_state:
        st.session_state.multi_offer_settings = {
            "enable_product_rotation": True,
            "product_rotation_step": 1,
            "price_increment_percent": 3.0,
            "rotation_mode": "linear",
            "module_quantity": 20,
            "include_storage": True,
            "module_rotation_step": 1,
            "inverter_rotation_step": 1,
            "storage_rotation_step": 1,
        }
    if "multi_offer_company_extended" not in st.session_state:
        st.session_state.multi_offer_company_extended = {}
    if "multi_offer_extend_all" not in st.session_state:
        st.session_state.multi_offer_extend_all = False
    if "multi_offer_project_data" not in st.session_state:
        st.session_state.multi_offer_project_data = {}


def load_customer_data_from_project() -> Dict[str, Any]:
    """
    Lädt Kundendaten automatisch aus Projekt/Bedarfsanalyse
    
    Rückgabewert:
        Dict mit Kundendaten oder leeres Dict
    """
    project_data = st.session_state.get("project_data", {})
    customer_data = project_data.get("customer_data", {})
    
    if customer_data:
        return {
            "first_name": customer_data.get("first_name", ""),
            "last_name": customer_data.get("last_name", ""),
            "street": customer_data.get("street", ""),
            "zip_code": customer_data.get("zip_code", ""),
            "city": customer_data.get("city", ""),
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
        }
    
    # Fallback: Versuche aus Bedarfsanalyse zu laden
    demand_data = st.session_state.get("demand_analysis_data", {})
    if demand_data:
        name_parts = demand_data.get("customer_name", "").split(" ", 1)
        return {
            "first_name": name_parts[0] if name_parts else "",
            "last_name": name_parts[1] if len(name_parts) > 1 else "",
            "street": demand_data.get("customer_street", ""),
            "zip_code": demand_data.get("customer_zip", ""),
            "city": demand_data.get("customer_city", ""),
            "email": demand_data.get("customer_email", ""),
            "phone": demand_data.get("customer_phone", ""),
        }
    
    return {}


def render_multi_pdf_customer_input() -> bool:
    """
    Rendert Kundendaten-Eingabe für Multi-PDF
    
    Rückgabewert:
        True wenn Daten vollständig, sonst False
    """
    st.subheader("📋 Schritt 1: Kundendaten")
    
    # Versuche automatische Übernahme
    auto_customer_data = load_customer_data_from_project()
    
    if auto_customer_data and any(auto_customer_data.values()):
        st.success("✅ Kundendaten aus Projekt/Bedarfsanalyse übernommen!")
        st.session_state.multi_offer_customer_data = auto_customer_data
        
        # Zeige übernommene Daten an
        col1, col2 = st.columns(2)
        with col1:
            full_name = f"{auto_customer_data.get('first_name', '')} {auto_customer_data.get('last_name', '')}"
            st.text_input("Kunde", value=full_name, disabled=True)
            st.text_input("Straße", value=auto_customer_data.get("street", ""), disabled=True)
        with col2:
            st.text_input("PLZ", value=auto_customer_data.get("zip_code", ""), disabled=True)
            st.text_input("Ort", value=auto_customer_data.get("city", ""), disabled=True)
        
        if st.button("🔄 Kundendaten manuell ändern"):
            st.session_state.multi_offer_customer_data = {}
            st.rerun()
        
        return True
    
    # Manuelle Eingabe
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("Vorname*")
        street = st.text_input("Straße*")
        email = st.text_input("E-Mail")
    
    with col2:
        last_name = st.text_input("Nachname*")
        col_zip, col_city = st.columns([1, 2])
        with col_zip:
            zip_code = st.text_input("PLZ*")
        with col_city:
            city = st.text_input("Ort*")
        phone = st.text_input("Telefon")
    
    if all([first_name, last_name, street, zip_code, city]):
        st.session_state.multi_offer_customer_data = {
            "first_name": first_name,
            "last_name": last_name,
            "street": street,
            "zip_code": zip_code,
            "city": city,
            "email": email,
            "phone": phone,
        }
        return True
    
    return False


def render_multi_pdf_company_selection(companies: List[Dict]) -> List[int]:
    """
    Rendert Firmenauswahl mit Extended-PDF-Toggles
    
    Parameter:
        companies: Liste von Firmen-Dicts
    
    Rückgabewert:
        Liste der ausgewählten Firmen-IDs
    """
    st.subheader("🏢 Schritt 2: Firmenauswahl (2-20+ Firmen)")
    
    if not companies:
        st.error("Keine Firmen in Datenbank gefunden!")
        return []
    
    company_options = {company["name"]: company["id"] for company in companies}
    
    col_select, col_buttons = st.columns([3, 1])
    
    with col_select:
        selected_names = st.multiselect(
            "Firmen auswählen",
            options=list(company_options.keys()),
            default=[companies[i]["name"] for i in range(min(5, len(companies)))],
        )
    
    with col_buttons:
        if st.button("✅ Alle wählen"):
            st.session_state.multi_offer_selected_companies = list(company_options.values())
            st.rerun()
        if st.button("❌ Alle abwählen"):
            st.session_state.multi_offer_selected_companies = []
            st.rerun()
    
    selected_ids = [company_options[name] for name in selected_names]
    st.session_state.multi_offer_selected_companies = selected_ids
    
    # Pflege der Extended-Flags
    current_ids = set(selected_ids)
    st.session_state.multi_offer_company_extended = {
        cid: val for cid, val in st.session_state.multi_offer_company_extended.items() if cid in current_ids
    }
    for cid in current_ids:
        st.session_state.multi_offer_company_extended.setdefault(cid, False)
    
    # Erweiterte PDF-Einstellungen
    if selected_ids:
        num = len(selected_ids)
        st.success(f"✅ **{num} Firma(en) ausgewählt**")
        
        with st.expander("📄 Erweiterte PDF-Ausgabe (Seite 7+) je Firma"):
            col_master, col_individual = st.columns([1, 3])
            
            with col_master:
                master = st.checkbox(
                    "🎛️ Alle erweitern",
                    value=st.session_state.get("multi_offer_extend_all", False),
                    help="Aktiviert erweiterte PDF-Ausgabe für ALLE Firmen"
                )
                if master != st.session_state.get("multi_offer_extend_all", False):
                    st.session_state.multi_offer_extend_all = master
                    if master:
                        for cid in current_ids:
                            st.session_state.multi_offer_company_extended[cid] = True
            
            with col_individual:
                for cid in selected_ids:
                    company_name = next((c["name"] for c in companies if c["id"] == cid), f"Firma {cid}")
                    st.session_state.multi_offer_company_extended[cid] = st.checkbox(
                        f"📄 {company_name}",
                        value=st.session_state.multi_offer_company_extended.get(cid, False),
                        key=f"ext_{cid}"
                    )
    
    return selected_ids


def render_multi_pdf_settings():
    """Rendert Einstellungen für Multi-PDF"""
    st.subheader("⚙️ Schritt 3: Angebotskonfiguration")
    
    settings = st.session_state.multi_offer_settings
    
    # Produktrotation & Preisstaffelung
    st.markdown("### 🔄 Automatische Produktrotation & Preisstaffelung")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        settings["enable_product_rotation"] = st.checkbox(
            "🔄 Produktrotation aktivieren",
            value=settings.get("enable_product_rotation", True),
            help="Jede Firma bekommt andere Produkte aus der gleichen Kategorie"
        )
    
    with col2:
        if settings["enable_product_rotation"]:
            settings["product_rotation_step"] = st.slider(
                "Rotationsschritt",
                1, 5,
                settings.get("product_rotation_step", 1),
                help="Wie viele Produkte überspringen?"
            )
    
    with col3:
        settings["price_increment_percent"] = st.slider(
            "💰 Preisstaffelung (%)",
            0.0, 20.0,
            settings.get("price_increment_percent", 3.0),
            step=0.5,
            help="Preissteigerung pro Firma"
        )
    
    # Erweiterte Einstellungen
    with st.expander("🔧 Erweiterte Rotation & Preiseinstellungen"):
        col_mode, col_steps = st.columns(2)
        
        with col_mode:
            settings["rotation_mode"] = st.selectbox(
                "Rotationsmodus",
                ["linear", "zufällig", "kategorie-spezifisch"],
                index=["linear", "zufällig", "kategorie-spezifisch"].index(settings.get("rotation_mode", "linear"))
            )
            
            if settings["rotation_mode"] == "kategorie-spezifisch":
                st.write("**Kategorie-spezifische Schritte:**")
                settings["module_rotation_step"] = st.slider("Module", 1, 10, settings.get("module_rotation_step", 1))
                settings["inverter_rotation_step"] = st.slider("Wechselrichter", 1, 10, settings.get("inverter_rotation_step", 1))
                settings["storage_rotation_step"] = st.slider("Speicher", 1, 10, settings.get("storage_rotation_step", 1))


# ===================================================================
# TEIL 2: WÄRMEPUMPEN-INTEGRATION
# ===================================================================

def init_heatpump_session_state():
    """Initialisiert Session State für Wärmepumpen"""
    if "multi_offer_heatpump_enabled" not in st.session_state:
        st.session_state.multi_offer_heatpump_enabled = False
    if "heatpump_calculation_data" not in st.session_state:
        st.session_state.heatpump_calculation_data = {}


def render_heatpump_integration_toggle() -> bool:
    """
    Rendert Wärmepumpen-Integrations-Toggle
    
    Rückgabewert:
        True wenn Wärmepumpe aktiviert, sonst False
    """
    st.subheader("🔥 Wärmepumpen-Integration (optional)")
    
    enabled = st.checkbox(
        "Wärmepumpe in Angebote integrieren",
        value=st.session_state.multi_offer_heatpump_enabled,
        help="Kombiniert PV-Anlage mit Wärmepumpe für ganzheitliche Energielösung"
    )
    
    st.session_state.multi_offer_heatpump_enabled = enabled
    
    if enabled:
        # Prüfe ob Wärmepumpen-Daten verfügbar sind
        if st.session_state.get("heatpump_calculation_data"):
            st.success("✅ Wärmepumpen-Daten aus Bedarfsanalyse übernommen")
        else:
            st.info("ℹ️ Keine Wärmepumpen-Daten verfügbar. Bitte erst Bedarfsanalyse durchführen.")
            return False
    
    return enabled


# ===================================================================
# TEIL 3: PRODUKTROTATION & PDF-GENERIERUNG
# ===================================================================

def calculate_rotation_products(company_index: int, base_settings: dict) -> dict:
    """
    Vollständig flexible Produktrotation für verschiedene Firmen
    company_index: 0 = erste Firma, 1 = zweite Firma, etc.
    Unterstützt: Lineare Rotation, Zufällige Auswahl, Kategorie-spezifische Schritte
    """
    from product_db import list_products
    
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
            
            if not base_id:
                continue
            
            # Lade verfügbare Produkte für diese Kategorie
            try:
                available_products = list_products(category)
            except Exception as e:
                logging.warning(f"Produktrotation {category}: Fehler beim Laden: {e}")
                continue
            
            if not available_products or len(available_products) <= 1:
                # Nur ein Produkt verfügbar - behalte das Original
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
            
            logging.info(f"Produktrotation {category}: Firma {company_index+1} -> {rotated_product.get('model_name', 'Unknown')} (Schritt: {rotation_step})")
    
    except Exception as e:
        logging.error(f"Fehler bei Produktrotation: {e}")
    
    return rotated_settings


def prepare_offer_data(customer_data: dict, company: dict, settings: dict, project_data: dict, company_index: int) -> dict:
    """
    Bereitet Angebotsdaten für PDF-Generierung vor
    
    Parameter:
        customer_data: Kundendaten
        company: Firmendaten
        settings: Angebotseinstellungen mit rotierten Produkten
        project_data: Projektdaten aus Session State
        company_index: Index der Firma für Preisstaffelung
    
    Rückgabewert:
        Dict mit aufbereiteten Angebotsdaten
    """
    # Rotierte Produkte für diese Firma
    rotated_settings = calculate_rotation_products(company_index, settings)
    
    # Preisstaffelung anwenden
    base_price = project_data.get("total_price", 0)
    increment = settings.get("price_increment_percent", 0)
    final_price = apply_price_increment(base_price, company_index, increment)
    
    return {
        "customer_data": customer_data,
        "company": company,
        "settings": rotated_settings,
        "total_price": final_price,
        "module_quantity": rotated_settings.get("module_quantity", 20),
        "selected_module_id": rotated_settings.get("selected_module_id"),
        "selected_inverter_id": rotated_settings.get("selected_inverter_id"),
        "selected_storage_id": rotated_settings.get("selected_storage_id"),
        "include_storage": rotated_settings.get("include_storage", True),
        "extended_output": st.session_state.multi_offer_company_extended.get(company["id"], False),
        "heatpump_enabled": st.session_state.multi_offer_heatpump_enabled,
        "heatpump_data": st.session_state.get("heatpump_calculation_data", {}),
    }


def generate_company_pdf(offer_data: dict) -> Optional[bytes]:
    """
    Generiert PDF für eine Firma
    
    Parameter:
        offer_data: Aufbereitete Angebotsdaten
    
    Rückgabewert:
        PDF als Bytes oder None bei Fehler
    """
    try:
        # Import der PDF-Generierungs-Funktion
        from pdf_generator import generate_pdf
        
        # PDF generieren
        pdf_bytes = generate_pdf(offer_data)
        
        return pdf_bytes
    
    except Exception as e:
        logging.error(f"Fehler bei PDF-Generierung: {e}")
        return None


def create_multi_pdf_zip(generated_pdfs: List[Dict]) -> bytes:
    """
    Erstellt ZIP-Archiv mit allen generierten PDFs
    
    Parameter:
        generated_pdfs: Liste von Dicts mit filename und pdf_content
    
    Rückgabewert:
        ZIP-Datei als Bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_info in generated_pdfs:
            zip_file.writestr(pdf_info["filename"], pdf_info["pdf_content"])
    
    return zip_buffer.getvalue()


def apply_price_increment(base_price: float, company_index: int, increment_percent: float) -> float:
    """
    Wendet Preisstaffelung an
    
    Parameter:
        base_price: Basispreis
        company_index: Index der Firma (0 = erste, 1 = zweite, etc.)
        increment_percent: Preissteigerung in Prozent
    
    Rückgabewert:
        Angepasster Preis
    """
    price_factor = 1.0 + (company_index * increment_percent / 100.0)
    return base_price * price_factor


# ===================================================================
# TEIL 4: HAUPT-PDF-GENERIERUNGS-PIPELINE
# ===================================================================

def batch_generate_offers():
    """
    Generiert PDFs für alle ausgewählten Firmen mit vollständiger Pipeline
    """
    st.subheader("🚀 Schritt 4: PDF-Angebote generieren")
    
    customer_data = st.session_state.multi_offer_customer_data
    selected_companies = st.session_state.multi_offer_selected_companies
    settings = st.session_state.multi_offer_settings
    project_data = st.session_state.get("multi_offer_project_data", {})
    
    if not customer_data or not selected_companies:
        st.error("❌ Kundendaten oder Firmenauswahl fehlt!")
        return
    
    if st.button("🎯 Angebote für alle Firmen erstellen", type="primary", use_container_width=True):
        
        try:
            from database import get_company
            from tqdm import tqdm
            
            # Fortschrittsanzeige
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            generated_pdfs = []
            total_companies = len(selected_companies)
            
            for i, company_id in enumerate(selected_companies):
                company_name = f"Firma_{company_id}"  # Fallback
                
                try:
                    # Company-Daten laden
                    company = get_company(company_id) if callable(get_company) else {"id": company_id, "name": company_name}
                    company_name = company.get("name", company_name)
                    
                    status_text.text(f"🔄 Erstelle Angebot für {company_name} ({i+1}/{total_companies})...")
                    
                    # Angebotsdaten vorbereiten mit Rotation & Preisstaffelung
                    offer_data = prepare_offer_data(customer_data, company, settings, project_data, i)
                    
                    # PDF generieren
                    pdf_content = generate_company_pdf(offer_data)
                    
                    if pdf_content:
                        filename = f"Angebot_{company_name}_{customer_data.get('last_name', 'Kunde')}.pdf"
                        generated_pdfs.append({
                            "company_name": company_name,
                            "pdf_content": pdf_content,
                            "filename": filename,
                            "bytes": pdf_content,  # Für CRM-Speicherung
                        })
                        st.success(f"✅ PDF für {company_name} erstellt")
                    else:
                        st.error(f"❌ PDF für {company_name} konnte nicht erstellt werden")
                    
                    # Fortschritt aktualisieren
                    progress_bar.progress((i + 1) / total_companies)
                    
                except Exception as e:
                    st.error(f"❌ Fehler bei {company_name}: {str(e)}")
                    logging.error(f"Fehler bei PDF-Generierung für {company_name}: {e}")
                    continue
            
            # ZIP-Download erstellen
            if generated_pdfs:
                zip_content = create_multi_pdf_zip(generated_pdfs)
                
                st.success(f"🎉 **{len(generated_pdfs)} Angebote erfolgreich erstellt!**")
                
                # Download-Button
                st.download_button(
                    label="📦 Alle Angebote als ZIP herunterladen",
                    data=zip_content,
                    file_name=f"Multi_Angebote_{customer_data.get('last_name', 'Kunde')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                # CRM-Integration (optional)
                render_crm_integration(customer_data, generated_pdfs, project_data)
            
            else:
                st.error("❌ Keine PDFs konnten erstellt werden!")
            
            status_text.text("✅ Fertig!")
            
        except Exception as e:
            st.error(f"❌ Fehler bei der PDF-Generierung: {str(e)}")
            logging.error(f"Fehler in batch_generate_offers: {e}")


def render_crm_integration(customer_data: dict, generated_pdfs: List[Dict], project_data: dict):
    """
    Rendert CRM-Integration für Kundenspeicherung
    """
    with st.expander("💼 CRM: Kunde speichern & Angebote in Kundenakte ablegen"):
        try:
            import sqlite3
            from database import get_db_connection, add_customer_document
            from crm import save_customer, save_project, create_tables_crm
            
            conn = get_db_connection()
            if conn is None:
                st.error("❌ Keine DB-Verbindung für CRM")
                return
            
            conn.row_factory = sqlite3.Row
            create_tables_crm(conn)
            
            # Kunde erstellen/finden
            first_name = customer_data.get('first_name', '')
            last_name = customer_data.get('last_name', '')
            email_val = customer_data.get('email', '')
            
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM customers WHERE first_name=? AND last_name=? AND (email=? OR ?='') LIMIT 1",
                (first_name, last_name, email_val, email_val)
            )
            row = cur.fetchone()
            
            if row:
                crm_customer_id = int(row[0])
                st.info(f"ℹ️ Kunde bereits vorhanden (ID: {crm_customer_id})")
            else:
                cust_payload = {
                    'first_name': first_name or 'Interessent',
                    'last_name': last_name or 'Unbekannt',
                    'address': customer_data.get('street'),
                    'zip_code': customer_data.get('zip_code'),
                    'city': customer_data.get('city'),
                    'email': email_val,
                    'phone_landline': customer_data.get('phone'),
                    'creation_date': datetime.now().isoformat(),
                }
                crm_customer_id = save_customer(conn, cust_payload)
                st.success(f"✅ Neuer Kunde erstellt (ID: {crm_customer_id})")
            
            # Projekt anlegen
            if crm_customer_id:
                proj_payload = {
                    'customer_id': crm_customer_id,
                    'project_name': f"Multi-Angebot {datetime.now().strftime('%Y-%m-%d')}",
                    'project_status': 'Angebot',
                    'creation_date': datetime.now().isoformat(),
                }
                crm_project_id = save_project(conn, proj_payload)
                
                # PDFs in Kundenakte ablegen
                saved_docs = 0
                for item in generated_pdfs:
                    try:
                        pdf_bytes = item.get('bytes')
                        filename = item.get('filename')
                        if isinstance(pdf_bytes, (bytes, bytearray)):
                            add_customer_document(
                                crm_customer_id,
                                pdf_bytes,
                                display_name=filename,
                                doc_type="offer_pdf",
                                project_id=crm_project_id,
                                suggested_filename=filename
                            )
                            saved_docs += 1
                    except Exception as e_item:
                        st.warning(f"⚠️ Konnte PDF nicht speichern: {e_item}")
                
                st.success(f"✅ {saved_docs} PDF(s) in Kundenakte abgelegt!")
                
                # Navigation zu CRM
                if st.button("👤 Zur CRM Kundenverwaltung"):
                    st.session_state['selected_page_key_sui'] = 'crm'
                    st.session_state['selected_customer_id'] = crm_customer_id
                    st.session_state['crm_view_mode'] = 'view_customer'
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ CRM-Speichern fehlgeschlagen: {e}")
            logging.error(f"CRM-Integration Fehler: {e}")


# ===================================================================
# TEIL 5: HAUPTFUNKTION
# ===================================================================

def render_multi_pdf_generator():
    """
    Haupt-UI für Multi-PDF-Generator
    Vollständige Integration mit PDF-Generierungs-Pipeline
    """
    st.title("📊 Multi-Firmen-Angebotsgenerator")
    st.caption("Erstellen Sie mehrere individualisierte Angebote mit einem Klick")
    
    # Initialisierung
    init_multi_pdf_session_state()
    init_heatpump_session_state()
    
    # Import der notwendigen Funktionen
    try:
        from database import list_companies
    except ImportError:
        st.error("❌ Datenbankfunktionen nicht verfügbar")
        return
    
    # Schritt 1: Kundendaten
    customer_data_complete = render_multi_pdf_customer_input()
    
    if not customer_data_complete:
        st.info("👆 Bitte erst Kundendaten eingeben")
        return
    
    st.markdown("---")
    
    # Schritt 2: Firmenauswahl
    available_companies = list_companies()
    selected_company_ids = render_multi_pdf_company_selection(available_companies)
    
    if not selected_company_ids or len(selected_company_ids) < 2:
        st.info("👆 Bitte mindestens 2 Firmen auswählen")
        return
    
    st.markdown("---")
    
    # Schritt 3: Einstellungen
    render_multi_pdf_settings()
    
    st.markdown("---")
    
    # Schritt 4: Wärmepumpen-Integration (optional)
    heatpump_enabled = render_heatpump_integration_toggle()
    
    st.markdown("---")
    
    # Schritt 5: Zusammenfassung & Generierung
    st.info(f"""
    📊 **Zusammenfassung:**
    - 👥 {len(selected_company_ids)} Firma(en) ausgewählt
    - 🧑 Kunde: {st.session_state.multi_offer_customer_data.get('first_name')} {st.session_state.multi_offer_customer_data.get('last_name')}
    - 🔄 Produktrotation: {'✅ Aktiv' if st.session_state.multi_offer_settings.get('enable_product_rotation') else '❌ Deaktiviert'}
    - 💰 Preisstaffelung: {st.session_state.multi_offer_settings.get('price_increment_percent', 0)}%
    - 🔥 Wärmepumpe: {'✅ Ja' if heatpump_enabled else '❌ Nein'}
    """)
    
    # PDF-Generierung
    batch_generate_offers()


# ===================================================================
# MAIN ENTRY POINT
# ===================================================================

if __name__ == "__main__":
    render_multi_pdf_generator()
